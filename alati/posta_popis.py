#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
posta_popis.py: popis SVE pošte u WWM/PR sandučićima od zadanog dana, za temeljnu bazu slanja.

RADI NA POSLUŽITELJU (namecheap-portal: Python 3.6; hostarmada: Python 3.9). Samo čita poštu.
Ne dira stanje posla »mailovi« (vidjeni.json, sken_zadnji.txt). Piše jednu datoteku: ~/wwm_ops_podaci/posta_popis_<host>.json.
Tekst poruke se NE sprema: samo tko, kome (sandučić), kada, predmet, vrsta i, kod bouncea, adresa koja je odbijena.

    scp alati/posta_popis.py alati/sken.py alati/sken_iskljuci.txt namecheap-portal:~/wwm_ops_podaci/
    ssh namecheap-portal 'PYTHONIOENCODING=utf-8 python3 ~/wwm_ops_podaci/posta_popis.py --od 2026-09-15'
    scp namecheap-portal:~/wwm_ops_podaci/posta_popis_*.json out/temeljna/izvori/
    isto za hostarmada.

Vrste: odgovor (u nit), auto (automatski odgovor), bounce, ostalo (nova poruka, nije odgovor), izvjestaj (DMARC), warmup_spam,
       poslano (poruka iz mape Sent prema vanjskoj adresi: naš pojedinačni odgovor).
Polje micanje = 1 kad odgovor traži micanje s karte (iste ključne riječi kao sken.py).
"""
import os, re, sys, json, time, email, socket, argparse, calendar
from email.utils import parsedate_to_datetime, getaddresses

OVDJE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OVDJE)
import sken  # hdr, body_of, split_quote, AUTO, MICANJE, ucitaj_iskljucene

ROOT = os.path.expanduser("~/mail")
PODACI = os.path.expanduser("~/wwm_ops_podaci")
HOST = socket.gethostname().split(".")[0]
ADR = re.compile(r"[A-Za-z0-9][A-Za-z0-9._%+\-]{0,63}@[A-Za-z0-9][A-Za-z0-9.\-]{1,60}\.[A-Za-z]{2,12}")
SENT = (".Sent", ".Sent Messages", ".Sent Items", ".INBOX.Sent")


def odbijena(m, nase):
    """Adresa koja je odbijena u bounce poruci."""
    x = (m.get("X-Failed-Recipients") or "").strip()
    if x:
        return x.split(",")[0].strip().lower()
    for p in m.walk():
        ct = p.get_content_type()
        if ct in ("message/delivery-status", "text/plain", "text/rfc822-headers"):
            try:
                t = p.get_payload(decode=True)
                t = t.decode("utf-8", "replace") if isinstance(t, bytes) else str(p.get_payload())
            except Exception:
                t = str(p.get_payload())
            r = re.search(r"(?:Final|Original)-Recipient:\s*rfc822;\s*<?([^\s<>]+@[^\s<>]+)", t, re.I)
            if r:
                return r.group(1).strip().lower()
            if ct == "text/plain":
                for a in ADR.findall(t[:4000]):
                    a = a.lower()
                    if a.split("@")[-1] not in nase and not re.search(r"mailer-daemon|postmaster", a):
                        return a
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--od", default="2026-09-15")
    ap.add_argument("--iskljuci", default=os.path.join(OVDJE, "sken_iskljuci.txt"))
    a = ap.parse_args()
    od = calendar.timegm(time.strptime(a.od[:10], "%Y-%m-%d"))
    if not os.path.isdir(ROOT):
        sys.exit("STOP: nema %s; skripta ide na mail poslužitelj" % ROOT)
    iskljucene = sken.ucitaj_iskljucene(a.iskljuci)
    domene = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)) and "." in d and not d.startswith(".")
                    and not d.startswith("dovecot") and d not in ("new", "cur", "tmp"))
    nase = set(domene)
    rows = []; n = 0; kutija = 0
    for dom in domene:
        if dom in iskljucene:
            continue
        dp = os.path.join(ROOT, dom)
        for user in sorted(os.listdir(dp)):
            up = os.path.join(dp, user)
            if not os.path.isdir(up) or user in ("new", "cur", "tmp") or user.startswith("."):
                continue
            kutija += 1
            mape = [("", "new"), ("", "cur")] + [(s, c) for s in SENT for c in ("cur", "new")]
            for pod, sub in mape:
                dd = os.path.join(up, pod, sub) if pod else os.path.join(up, sub)
                if not os.path.isdir(dd):
                    continue
                for fn in os.listdir(dd):
                    fp = os.path.join(dd, fn)
                    try:
                        if os.path.getmtime(fp) < od - 86400:
                            continue
                        with open(fp, "rb") as fh:
                            m = email.message_from_binary_file(fh)
                    except Exception:
                        continue
                    n += 1
                    try:
                        dt = parsedate_to_datetime(m.get("Date")); ts = dt.timestamp(); kad = time.strftime("%Y-%m-%d %H:%M", time.gmtime(ts))
                    except Exception:
                        ts = os.path.getmtime(fp); kad = time.strftime("%Y-%m-%d %H:%M", time.gmtime(ts))
                    if ts < od:
                        continue
                    subj = re.sub(r"\s+", " ", sken.hdr(m, "Subject")).strip()
                    fa = (getaddresses([sken.hdr(m, "From")]) or [("", "")])[0][1].lower(); fd = fa.split("@")[-1]
                    box = "%s/%s" % (dom, user)
                    if pod:      # mapa Sent: naša poruka prema van
                        prim = [x[1].lower() for x in getaddresses([sken.hdr(m, "To"), sken.hdr(m, "Cc")]) if x[1]]
                        prim = [x for x in prim if x.split("@")[-1] not in nase]
                        for x in prim[:5]:
                            rows.append(dict(host=HOST, box=box, kat="poslano", od=box.split("/")[1] + "@" + dom, prema=x, kad=kad,
                                             predmet=subj[:200], micanje=0, odbijena="", irt=1 if m.get("In-Reply-To") else 0))
                        continue
                    if fd in nase:
                        continue
                    kat = "odgovor"
                    if user.lower() == "dmarc" or re.search(r"dmarc", fa) or re.search(r"Report Domain:|DMARC (Aggregate )?Report", subj, re.I):
                        kat = "izvjestaj"
                    elif subj.startswith("[WRM]") or subj.startswith("***SPAM***"):
                        kat = "warmup_spam"
                    elif re.search(r"mailer-daemon|postmaster", fa) or re.search(r"Undeliver|Delivery Status|Mail delivery|failure notice|Returned mail", subj, re.I):
                        kat = "bounce"
                    elif (m.get("Auto-Submitted", "no").lower() != "no") or m.get("X-Autoreply") or m.get("X-Autorespond") or sken.AUTO.search(subj):
                        kat = "auto"
                    elif not (m.get("In-Reply-To") or m.get("References") or re.match(r"\s*(re|aw|sv|vs|odp|rif|r|ris|res|antw)\s*:", subj, re.I)):
                        kat = "ostalo"
                    mic = 0; odb = ""
                    if kat == "bounce":
                        odb = odbijena(m, nase)
                    elif kat in ("odgovor", "ostalo"):
                        try:
                            above, below = sken.split_quote(sken.body_of(m))
                        except Exception:
                            above, below = "", ""
                        if kat == "odgovor" and sken.AUTO.search(above[:300]):
                            kat = "auto"
                        if (kat == "odgovor" or user.lower() in ("contact", "info", "hello", "support")) and sken.MICANJE.search((above + "\n" + below)[:6000]):
                            mic = 1
                    rows.append(dict(host=HOST, box=box, kat=kat, od=fa, prema="", kad=kad, predmet=subj[:200], micanje=mic, odbijena=odb,
                                     irt=1 if (m.get("In-Reply-To") or m.get("References")) else 0))
    os.makedirs(PODACI, exist_ok=True)
    izlaz = os.path.join(PODACI, "posta_popis_%s.json" % HOST)
    with open(izlaz, "w", encoding="utf-8") as f:
        json.dump(dict(host=HOST, od=a.od, slozeno_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), sanducica=kutija, poruke=rows), f, ensure_ascii=False)
    from collections import Counter
    c = Counter(r["kat"] for r in rows)
    print("%s: sandučića %d, datoteka otvoreno %d, u popisu %d (%s) -> %s" % (HOST, kutija, n, len(rows),
          ", ".join("%s %d" % kv for kv in sorted(c.items())), izlaz))


if __name__ == "__main__":
    main()
