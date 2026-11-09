#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
posalji.py: šalje ODOBRENE odgovore iz plana, iz sandučića u koji je primatelj pisao, kao odgovor u istu nit.
Jedan alat za oba mail poslužitelja (namecheap-portal, hostarmada). Šalje se NA POSLUŽITELJU kroz lokalni
sendmail (DKIM domene), kopija u Maildir .Sent, trag u ledgeru. Nikakve lozinke: pristup je ssh ključem.

Dva načina rada:
  LOKALNO (laptop ili Hetzner, iz klona wwm-ops):
      python3 alati/posalji.py --plan out/plan_2026-11-08.json --host namecheap --proba
      python3 alati/posalji.py --plan out/plan_2026-11-08.json --host namecheap --posalji
    Kopira skriptu i plan na poslužitelj (scp), tamo pokreće provjeru ili slanje (ssh, u prednjem planu),
    vraća serverski ledger i dopisuje nove retke u out/POSLANO.csv.
  NA POSLUŽITELJU (poziva ga lokalni dio): python3 posalji.py --na-serveru --plan plan.json --proba|--posalji

Plan (JSON, popis stavki); gradi ga agent iz sken JSON-a + odobrenja Matije:
  {
    "id": "7284bf3687",                  # id iz skena (ili bilo koji jedinstven)
    "host": "namecheap",                 # namecheap | hostarmada
    "sanducic": "contact@worldwinerymap.com",
    "from_name": "Matija Gavrilovic",    # ime kojim je ta nit dosad potpisivana
    "to": "scott.osborn@foxrunvineyards.com",
    "subject": "Re: word",
    "in_reply_to": "<...>",              # Message-ID njihove poruke (iz skena: mid)
    "references": "<...> <...>",         # iz skena: references + ' ' + mid
    "body": "cijeli tekst odgovora, na jeziku primatelja",
    "vrsta": "vinarija",                 # vinarija | medij | ostalo
    "predlozak": "vinarije/kako-preuzeti-profil",
    "odobrio": "Matija: »šalji 1«",      # OBAVEZNO: njegova riječ za baš ovaj mail, doslovno
    "cc": [],                            # neobavezno
    "dopusti_novije": false,             # ako je od njih stigla novija poruka, bez ovoga se preskače
    "dopusti_nas_poslije": false         # ako smo im već odgovorili poslije te poruke, bez ovoga se preskače
  }

Brave (svaka zaustavlja stavku, --proba ih sve ispiše):
  - prazno polje odobrio -> ne šalje se nikad
  - sandučić ne postoji na poslužitelju / njihova poruka (in_reply_to) nije nađena u Maildiru
  - stigla je novija poruka od njih ili već postoji naš odgovor poslije njihove (osim uz dopusti_*)
  - duga ili srednja crtica u tijelu (AGENTS.md §8)
  - id već u ledgeru (bilo koji status) -> preskače se, idempotentno
Prva greška slanja zaustavlja cijeli poziv. Pauza 20 do 40 s između mailova.
"""
import os, sys, io, json, re, time, random, socket, subprocess, glob, argparse, csv
from email import policy
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import formatdate, make_msgid, getaddresses, parsedate_to_datetime
from email.parser import BytesHeaderParser

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

POL = policy.SMTP.clone(max_line_length=900)
HP = BytesHeaderParser(policy=policy.default)
OVDJE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(OVDJE)
HOSTOVI = {"namecheap": "namecheap-portal", "hostarmada": "hostarmada"}
PODACI = "~/wwm_ops_podaci"                     # na poslužitelju
LEDGER_CSV = os.path.join(REPO, "out", "POSLANO.csv")
CSV_STUPCI = ["vrijeme_utc", "host", "sanducic", "to", "subject", "vrsta", "predlozak", "odobrio",
              "message_id", "in_reply_to", "status", "kopija", "greska", "id"]


def utc():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


def ucitaj_plan(p, host, samo):
    L = json.load(io.open(p, encoding="utf-8"))
    L = [e for e in L if e.get("host") == host]
    if samo:
        L = [e for e in L if e["id"] in samo]
    return L


# ---------------- na poslužitelju ----------------
def srv_ledger_p():
    return os.path.join(os.path.expanduser(PODACI), "POSLANO.jsonl")


def srv_ledger_ids():
    ids = {}
    p = srv_ledger_p()
    if os.path.exists(p):
        for l in io.open(p, encoding="utf-8"):
            if l.strip():
                r = json.loads(l); ids.setdefault(r["id"], []).append(r["status"])
    return ids


def srv_ledger_pisi(r):
    with io.open(srv_ledger_p(), "a", encoding="utf-8") as f:
        f.write(json.dumps(r, ensure_ascii=False) + "\n"); f.flush(); os.fsync(f.fileno())


def box_dir(e):
    user, dom = e["sanducic"].split("@")
    return os.path.join(os.path.expanduser("~/mail"), dom, user)


def sastavi(e):
    m = EmailMessage(policy=POL)
    user, dom = e["sanducic"].split("@")
    m["From"] = Address(display_name=e.get("from_name") or "", addr_spec=e["sanducic"])
    m["To"] = e["to"]
    if e.get("cc"):
        m["Cc"] = ", ".join(e["cc"])
    m["Reply-To"] = e["sanducic"]
    m["Subject"] = e["subject"]
    m["Date"] = formatdate(localtime=True)
    m["Message-ID"] = make_msgid(domain=dom)
    m["In-Reply-To"] = e["in_reply_to"]
    m["References"] = e.get("references") or e["in_reply_to"]
    m.set_content(e["body"])
    sirovo = m.as_bytes()
    odm = sirovo.replace(b"\r\n ", b" ").replace(b"\n ", b" ")
    assert b"In-Reply-To: " + e["in_reply_to"].encode() in odm, "zaglavlje niti kodirano"
    return m, sirovo, [e["to"]] + list(e.get("cc") or [])


def provjeri(e):
    """Samo čitanje Maildira: sandučić, njihova poruka, novije od njih, naš odgovor poslije."""
    r = {"id": e["id"], "problemi": []}
    if not (e.get("odobrio") or "").strip():
        r["problemi"].append("nema odobrenja (polje odobrio prazno)")
    if u"—" in e["body"] or u"–" in e["body"]:
        r["problemi"].append("duga ili srednja crtica u tijelu")
    if not e.get("in_reply_to"):
        r["problemi"].append("nema in_reply_to (odgovor mora ići u nit)")
    b = box_dir(e)
    if not os.path.isdir(b):
        r["problemi"].append("sandučić %s ne postoji na ovom poslužitelju" % e["sanducic"]); return r
    nj = e["to"].lower(); kad = None; nadjen = False; od_njih = []; nasi = []
    datoteke = glob.glob(b + "/cur/*") + glob.glob(b + "/new/*") + glob.glob(b + "/.*/cur/*") + glob.glob(b + "/.*/new/*")
    for p in datoteke:
        try:
            with open(p, "rb") as fh:
                h = HP.parse(fh)
            mid = str(h.get("Message-ID", "") or "").strip()
            fa = [a.lower() for _, a in getaddresses([str(h.get("From", "") or "")])]
            d0 = parsedate_to_datetime(str(h.get("Date", ""))).timestamp() if h.get("Date") else 0
            if mid == e.get("in_reply_to"):
                nadjen = True; kad = d0; r["mapa"] = p[len(b):].split("/")[1] or "INBOX"
            if fa and fa[0] == nj:
                od_njih.append(d0)
            if "/.Sent/" in p:
                to = [a.lower() for _, a in getaddresses([str(h.get("To", "") or ""), str(h.get("Cc", "") or "")])]
                if nj in to:
                    nasi.append(d0)
        except Exception:
            continue
    if not nadjen:
        r["problemi"].append("njihova poruka (in_reply_to) nije nađena u sandučiću")
    else:
        r["novija_od_njih"] = len([d for d in od_njih if d > kad + 1])
        r["nas_odgovor_poslije"] = len([d for d in nasi if d > kad])
        if r["novija_od_njih"] and not e.get("dopusti_novije"):
            r["problemi"].append("od njih je stigla novija poruka (%d); pročitaj je pa dopusti_novije" % r["novija_od_njih"])
        if r["nas_odgovor_poslije"] and not e.get("dopusti_nas_poslije"):
            r["problemi"].append("već postoji naš odgovor poslije njihove poruke (%d)" % r["nas_odgovor_poslije"])
    try:
        sastavi(e)
    except Exception as ex:
        r["problemi"].append("poruka se ne da složiti: %s" % ex)
    return r


def posalji_srv(e, sirovo, prim):
    p = subprocess.run(["/usr/sbin/sendmail", "-i", "-f", e["sanducic"]] + prim, input=sirovo,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError("sendmail izlaz %s: %s" % (p.returncode, p.stderr.decode("utf-8", "replace")[:300]))
    sent = os.path.join(box_dir(e), ".Sent")
    for d in ("cur", "new", "tmp"):
        os.makedirs(os.path.join(sent, d), exist_ok=True)
    ime = "%d.M%dP%d.%s:2,S" % (time.time(), int(time.time() * 1e6) % 1000000, os.getpid(), socket.gethostname())
    with open(os.path.join(sent, "cur", ime), "wb") as fh:
        fh.write(sirovo)
    return ".Sent/cur/" + ime


def na_serveru(a):
    host = a.host
    L = ucitaj_plan(a.plan, host, a.samo)
    led = srv_ledger_ids()
    print("%s UTC | %s | stavki u planu za ovaj poslužitelj: %d | ledger %s" % (utc(), socket.gethostname(), len(L), srv_ledger_p()))
    rez = []
    for e in L:
        r = provjeri(e)
        if e["id"] in led:
            r["problemi"].append("već u ledgeru: %s" % ",".join(led[e["id"]]))
        rez.append((e, r))
    for e, r in rez:
        print("\n[%s] %s -> %s | %s | odobrio: %s" % (e["id"], e["sanducic"], e["to"], e["subject"][:70], e.get("odobrio", "")))
        print("   provjera: %s" % json.dumps({k: v for k, v in r.items() if k not in ("id", "problemi")}, ensure_ascii=False))
        print("   %s" % ("SPREMNO" if not r["problemi"] else "NIJE SPREMNO: " + " | ".join(r["problemi"])))
    spremno = [(e, r) for e, r in rez if not r["problemi"]]
    print("\nspremno %d od %d" % (len(spremno), len(rez)))
    if not a.posalji:
        print("(proba, ništa nije poslano)"); return
    ok = 0
    for i, (e, r) in enumerate(spremno):
        m, sirovo, prim = sastavi(e)
        zapis = dict(id=e["id"], host=host, sanducic=e["sanducic"], to=e["to"], subject=e["subject"], vrsta=e.get("vrsta", ""),
                     predlozak=e.get("predlozak", ""), odobrio=e.get("odobrio", ""), message_id=str(m["Message-ID"]),
                     in_reply_to=e["in_reply_to"], vrijeme_utc=utc(), status="zapoceto")
        srv_ledger_pisi(dict(zapis))
        print("ŠALJEM %s %s -> %s" % (e["id"], e["sanducic"], e["to"]))
        try:
            kopija = posalji_srv(e, sirovo, prim)
        except Exception as ex:
            zapis.update(status="greska", greska=str(ex)[:400], vrijeme_utc=utc()); srv_ledger_pisi(zapis)
            print("GREŠKA %s: %s\nZAUSTAVLJENO. Poslano u ovom pozivu: %d." % (e["id"], ex, ok)); sys.exit(2)
        zapis.update(status="poslano", kopija=kopija, vrijeme_utc=utc()); srv_ledger_pisi(zapis)
        ok += 1; print("   poslano, %s, kopija %s" % (zapis["message_id"], kopija))
        if i < len(spremno) - 1:
            p = random.uniform(20, 40); print("   pauza %.0f s" % p); time.sleep(p)
    print("GOTOVO: poslano %d" % ok)


# ---------------- lokalno ----------------
def ssh(alias, cmd, prednji=False):
    for pok in range(4):
        if prednji:
            r = subprocess.run(["ssh", "-o", "ConnectTimeout=30", alias, cmd])
        else:
            r = subprocess.run(["ssh", "-o", "ConnectTimeout=30", alias, cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.returncode != 255:
            return r
        time.sleep(15)
    return r


def csv_natrag(alias, host):
    r = ssh(alias, "cat %s/POSLANO.jsonl 2>/dev/null" % PODACI)
    redovi = [json.loads(l) for l in r.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    os.makedirs(os.path.dirname(LEDGER_CSV), exist_ok=True)
    postoje = set()
    if os.path.exists(LEDGER_CSV):
        with io.open(LEDGER_CSV, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                postoje.add((row.get("id"), row.get("status"), row.get("vrijeme_utc")))
    novo = [x for x in redovi if (x.get("id"), x.get("status"), x.get("vrijeme_utc")) not in postoje]
    nova_dat = not os.path.exists(LEDGER_CSV)
    with io.open(LEDGER_CSV, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_STUPCI, extrasaction="ignore")
        if nova_dat:
            w.writeheader()
        for x in novo:
            w.writerow({k: x.get(k, "") for k in CSV_STUPCI})
    print("ledger: %d novih redaka s %s -> %s" % (len(novo), host, LEDGER_CSV))


def brava_ne_kontaktirati(a):
    """Prije svakog slanja: nijedan primatelj (ni cc) ne smije biti na out/NE_KONTAKTIRATI.csv. Bez iznimke."""
    sys.path.insert(0, OVDJE)
    import ne_kontaktirati as nk
    adrese, domene = nk.skupovi()
    lose = []
    for e in ucitaj_plan(a.plan, a.host, a.samo):
        for adr in [e.get("to", "")] + list(e.get("cc") or []):
            b = nk.blokirana(adr, adrese, domene)
            if b:
                lose.append("%s -> %s (%s)" % (e.get("id"), adr, b))
    if lose:
        sys.exit("STOP: primatelj je na listi NE KONTAKTIRATI, ništa nije poslano ni provjeravano:\n  " + "\n  ".join(lose)
                 + "\nMakni te stavke iz plana. Lista se ne zaobilazi.")
    print("lista ne kontaktirati: %d adresa i %d domena, nijedan primatelj iz plana nije na njoj" % (len(adrese), len(domene)))


def lokalno(a):
    brava_ne_kontaktirati(a)
    alias = HOSTOVI[a.host]
    r = ssh(alias, "mkdir -p %s" % PODACI)
    if r.returncode:
        sys.exit("ssh mkdir pao: %s" % r.stderr.decode("utf-8", "replace"))
    r = subprocess.run(["scp", "-q", os.path.abspath(__file__), os.path.abspath(a.plan), "%s:%s/" % (alias, PODACI)])
    if r.returncode:
        sys.exit("scp pao")
    plan_srv = "%s/%s" % (PODACI, os.path.basename(a.plan))
    samo = (" --samo " + ",".join(sorted(a.samo))) if a.samo else ""
    nacin = "--posalji" if a.posalji else "--proba"
    cmd = "cd %s && PYTHONIOENCODING=utf-8 python3 posalji.py --na-serveru --host %s --plan %s %s%s" % (PODACI, a.host, plan_srv, nacin, samo)
    r = ssh(alias, cmd, prednji=True)
    if a.posalji:
        csv_natrag(alias, a.host)
    if r.returncode:
        sys.exit(r.returncode)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--host", required=True, choices=sorted(HOSTOVI))
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--proba", action="store_true", help="samo provjera, ništa se ne šalje")
    g.add_argument("--posalji", action="store_true", help="stvarno pošalji spremne stavke")
    ap.add_argument("--samo", help="samo ovi id-evi, odvojeni zarezom")
    ap.add_argument("--na-serveru", action="store_true")
    a = ap.parse_args()
    a.samo = set(x for x in (a.samo or "").split(",") if x)
    if a.na_serveru:
        na_serveru(a)
    else:
        lokalno(a)


if __name__ == "__main__":
    main()
