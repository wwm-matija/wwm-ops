#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sken.py: jedan sken svih WWM/PR sandučića na mail poslužitelju (cPanel Maildir), za posao »mailovi«.

RADI NA POSLUŽITELJU (namecheap-portal: Python 3.6; hostarmada: Python 3.9). Samo čita poštu.
Piše isključivo u ~/wwm_ops_podaci/ (popis viđenih poruka, izlazni JSON, vrijeme zadnjeg skena).

Kako ga agent pokreće (iz klona wwm-ops na laptopu ili Hetzneru):
    scp alati/sken.py alati/sken_iskljuci.txt namecheap-portal:~/wwm_ops_podaci/
    ssh namecheap-portal 'PYTHONIOENCODING=utf-8 python3 ~/wwm_ops_podaci/sken.py'
    isto za hostarmada.

Što radi:
  1. prolazi ~/mail/<domena>/<sandučić>/{new,cur}; domene iz sken_iskljuci.txt preskače (klijenti, privatno)
  2. uzima poruke novije od zadnjeg skena (ili --od), koje nisu od naših domena i koje još nisu u popisu viđenih
  3. razvrstava: bounce / auto (automatski odgovor) / odgovor (u nit) / ostalo (nova poruka, nije odgovor)
  4. tekst dijeli na dio IZNAD citata i dio ISPOD citata (bottom-posting), oba se gledaju
  5. označava zahtjeve za MICANJE S KARTE (ključne riječi) i stavlja ih na vrh izvještaja
  6. ispisuje izvještaj (Markdown) i sprema JSON sa svim poljima koja trebaju za odgovor
     (box, Message-ID, In-Reply-To, References, predmet, tekst)

Opcije:
  --od 2026-11-06T00:00   ili  --od 48h      od kada gledati (zadano: zadnji sken, inače 48 h)
  --sve                   zanemari popis viđenih (ponovno prikaži sve u rasponu)
  --bez-upisa             ništa ne upisuj (ni viđene ni vrijeme skena); za probu
  --iskljuci PUTANJA      druga datoteka s isključenim domenama (zadano: sken_iskljuci.txt pored skripte)
  --izlaz PUTANJA         JSON izlaz (zadano ~/wwm_ops_podaci/sken_<host>_<vrijeme>.json)
  --puni-tekst            u izvještaju puni tekst (zadano prvih 2500 znakova iznad i 800 ispod citata)
"""
import os, re, sys, json, time, html, email, hashlib, socket, argparse
from email.utils import parsedate_to_datetime, getaddresses
from email.header import decode_header, make_header

ROOT = os.path.expanduser("~/mail")
PODACI = os.path.expanduser("~/wwm_ops_podaci")
OVDJE = os.path.dirname(os.path.abspath(__file__))
HOST = socket.gethostname().split(".")[0]

QUOTE = re.compile(r"^(On .{5,120}wrote:|Il .{5,120}ha scritto:|Le .{5,120}a écrit|El .{5,120}escribió:|Em .{5,120}escreveu:|"
                   r"Am .{5,120}schrieb|Op .{5,120}schreef|Dne .{5,120}napsal|.{0,40}időpontban .{0,80}írta:|W dniu .{5,120}napisał|"
                   r"Den .{5,120}skrev|-----\s*(Original Message|Ursprüngliche Nachricht|Message d.origine|Messaggio originale|Mensaje original)|"
                   r"From:\s|Da:\s|De:\s|Von:\s|Od:\s|Feladó:\s|Från:\s|Fra:\s|Van:\s)", re.I | re.M)
AUTO = re.compile(r"auto(matic)?[ -]?repl|out of (the )?office|abwesen|autosvar|risposta automatica|réponse automatique|"
                  r"respuesta automática|afwezig|fuori sede|away from|thank you for (your|contacting)|we have received your|"
                  r"vacation|hors du bureau|automatyczna|automatische|nieobecn|nepřítomn|відпуст|отпуск", re.I)
MICANJE = re.compile(r"\b(remove|removal|delete|take (it|us) (down|off)|unlist|not a winery|no longer|closed down|"
                     r"rimuov|cancell|elimin|togli|supprim|retir|enlev|löschen|entfern|streichen|verwijder|"
                     r"usu[nń]|odstra[nň]|smaza|izbri[sš]|ukloni|makni|удал|убер|törl|eltávol|fjern|ta bort|poista)\w*", re.I)

def hdr(m, k):
    v = m.get(k, "") or ""
    try:
        return str(make_header(decode_header(v)))
    except Exception:
        return v

def body_of(m):
    plain = None; htmlb = None
    for p in m.walk():
        ct = p.get_content_type()
        if ct not in ("text/plain", "text/html"):
            continue
        try:
            t = p.get_payload(decode=True).decode(p.get_content_charset() or "utf-8", "replace")
        except Exception:
            continue
        if ct == "text/plain" and plain is None: plain = t
        if ct == "text/html" and htmlb is None: htmlb = t
    if plain and plain.strip():
        return plain
    if htmlb:
        t = re.sub(r"<(br|/p|/div|/tr|/li)[^>]*>", "\n", htmlb)
        t = re.sub(r"<style.*?</style>|<script.*?</script>", "", t, flags=re.S)
        t = re.sub(r"<[^>]+>", "", t)
        return html.unescape(t)
    return ""

def split_quote(body):
    lines = body.splitlines(); qi = None
    for i, l in enumerate(lines):
        if l.startswith(">") or QUOTE.match(l.strip()):
            qi = i; break
    if qi is None:
        return body.strip(), ""
    above = "\n".join(lines[:qi]).strip()
    qs = [i for i, l in enumerate(lines) if l.startswith(">")]
    last = max(qs) if qs else len(lines) - 1
    below = "\n".join(l for l in lines[last + 1:] if not l.startswith(">")).strip()
    # potpis ispod citata nije odgovor: makni ako je samo kratak potpis
    if below and len(below) < 25:
        below = ""
    return above, below

def ucitaj_iskljucene(putanja):
    s = set()
    if os.path.exists(putanja):
        for l in open(putanja, encoding="utf-8"):
            l = l.split("#", 1)[0].strip().lower()
            if l: s.add(l)
    return s

def od_kada(arg):
    """--od je uvijek UTC (poslužitelji imaju razne lokalne zone; 8.11. je 00:48 postalo 05:48 UTC)."""
    if not arg:
        return None
    m = re.match(r"^(\d+)\s*h$", arg.strip())
    if m:
        return time.time() - int(m.group(1)) * 3600
    import calendar
    try:
        return calendar.timegm(time.strptime(arg.strip()[:16], "%Y-%m-%dT%H:%M"))
    except ValueError:
        try:
            return calendar.timegm(time.strptime(arg.strip()[:10], "%Y-%m-%d"))
        except ValueError:
            sys.exit("STOP: --od ne razumijem: %r (očekujem 2026-11-06T00:00 UTC, 2026-11-06 ili 48h)" % arg)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--od")
    ap.add_argument("--sve", action="store_true")
    ap.add_argument("--bez-upisa", action="store_true")
    ap.add_argument("--iskljuci", default=os.path.join(OVDJE, "sken_iskljuci.txt"))
    ap.add_argument("--izlaz")
    ap.add_argument("--puni-tekst", action="store_true")
    a = ap.parse_args()

    if not os.path.isdir(ROOT):
        sys.exit("STOP: nema %s; skripta ide na mail poslužitelj, ne na laptop" % ROOT)
    os.makedirs(PODACI, exist_ok=True)
    stamp_p = os.path.join(PODACI, "sken_zadnji.txt")
    vidjeni_p = os.path.join(PODACI, "vidjeni.json")
    vidjeni = set()
    if os.path.exists(vidjeni_p) and not a.sve:
        try:
            vidjeni = set(tuple(x) for x in json.load(open(vidjeni_p, encoding="utf-8")))
        except Exception:
            vidjeni = set()
    od = od_kada(a.od)
    if od is None:
        if os.path.exists(stamp_p):
            try:
                od = float(open(stamp_p).read().strip())
            except Exception:
                od = time.time() - 48 * 3600
        else:
            od = time.time() - 48 * 3600
    pocetak = time.time()
    iskljucene = ucitaj_iskljucene(a.iskljuci)

    # mape domena: bez skrivenih (.ime@domena = IMAP podmape koje cPanel drži na vrhu) i bez dovecot/maildir datoteka
    domene = sorted(d for d in os.listdir(ROOT)
                    if os.path.isdir(os.path.join(ROOT, d)) and "." in d and not d.startswith(".")
                    and not d.startswith("dovecot") and d not in ("new", "cur", "tmp"))
    nase = set(domene)
    skenirane = [d for d in domene if d not in iskljucene]
    preskocene = [d for d in domene if d in iskljucene]

    rows = []; n_pregledano = 0; n_vec = 0
    for dom in skenirane:
        dp = os.path.join(ROOT, dom)
        for user in sorted(os.listdir(dp)):
            up = os.path.join(dp, user)
            # samo pravi sandučići: podmape (.Sent, .spam, .snovio, .Junk) i tehničke mape se preskaču
            if not os.path.isdir(up) or user in ("new", "cur", "tmp") or user.startswith("."):
                continue
            for sub in ("new", "cur"):
                dd = os.path.join(up, sub)
                if not os.path.isdir(dd):
                    continue
                for fn in os.listdir(dd):
                    fp = os.path.join(dd, fn)
                    try:
                        if os.path.getmtime(fp) < od:
                            continue
                    except OSError:
                        continue
                    n_pregledano += 1
                    try:
                        with open(fp, "rb") as fh:
                            m = email.message_from_binary_file(fh)
                    except Exception:
                        continue
                    frm = hdr(m, "From"); subj = re.sub(r"\s+", " ", hdr(m, "Subject")).strip()
                    adrese = getaddresses([frm]) or [("", "")]
                    fa = adrese[0][1].lower(); fd = fa.split("@")[-1]
                    if fd in nase:
                        continue  # naša vlastita poruka (kopija, test)
                    mid = (m.get("Message-ID") or "").strip() or ("bez-mid:" + fn)
                    box = "%s/%s" % (dom, user)
                    if (box, mid) in vidjeni and not a.sve:
                        n_vec += 1
                        continue
                    kat = "odgovor"
                    if user.lower() == "dmarc" or re.search(r"dmarc", fa) or re.search(r"Report Domain:|DMARC (Aggregate )?Report", subj, re.I):
                        kat = "izvjestaj"      # DMARC i slični strojni izvještaji: samo broj
                    elif subj.startswith("[WRM]") or subj.startswith("***SPAM***") or "/.snovio" in fp:
                        kat = "warmup_spam"    # Snov warmup i označeni spam: samo broj
                    elif re.search(r"mailer-daemon|postmaster", fa) or re.search(r"Undeliver|Delivery Status|Mail delivery|failure notice|Returned mail", subj, re.I):
                        kat = "bounce"
                    elif (m.get("Auto-Submitted", "no").lower() != "no") or m.get("X-Autoreply") or m.get("X-Autorespond") or AUTO.search(subj):
                        kat = "auto"
                    elif not (m.get("In-Reply-To") or m.get("References") or re.match(r"\s*(re|aw|sv|vs|odp|rif|r|ris|res|antw)\s*:", subj, re.I)):
                        kat = "ostalo"
                    if kat in ("izvjestaj", "warmup_spam"):
                        above, below = "", ""
                    else:
                        b = body_of(m); above, below = split_quote(b)
                    if kat == "odgovor" and AUTO.search(above[:300]):
                        kat = "auto?"
                    # micanje s karte: samo odgovori u nit i poruke na contact@ (tamo vinari pišu sami)
                    tekst_za_kljucne = (above + "\n" + below)[:6000]
                    micanje = bool((kat == "odgovor" or (kat == "ostalo" and user.lower() in ("contact", "info", "hello", "support")))
                                   and MICANJE.search(tekst_za_kljucne))
                    try:
                        kad_utc = parsedate_to_datetime(m.get("Date")).strftime("%Y-%m-%d %H:%M UTC") if m.get("Date") else ""
                    except Exception:
                        kad_utc = hdr(m, "Date")[:31]
                    rid = hashlib.sha1((box + "|" + mid).encode("utf-8")).hexdigest()[:10]
                    rows.append(dict(id=rid, host=HOST, box=box, mapa=sub, od_ime=adrese[0][0], od=fa, kad=kad_utc,
                                     predmet=subj, kat=kat, micanje=micanje, iznad=above[:8000], ispod=below[:3000],
                                     mid=mid, irt=(m.get("In-Reply-To") or "").strip(),
                                     references=re.sub(r"\s+", " ", (m.get("References") or "")).strip(),
                                     datoteka=fp.replace(os.path.expanduser("~"), "~")))
    rows.sort(key=lambda r: r["kad"])

    izlaz = a.izlaz or os.path.join(PODACI, "sken_%s_%s.json" % (HOST, time.strftime("%Y%m%d_%H%M")))
    if not a.bez_upisa:
        with open(izlaz, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        for r in rows:
            vidjeni.add((r["box"], r["mid"]))
        with open(vidjeni_p, "w", encoding="utf-8") as f:
            json.dump(sorted(vidjeni), f, ensure_ascii=False)
        with open(stamp_p, "w") as f:
            f.write("%f\n" % pocetak)

    # ---- izvještaj (Markdown) ----
    from collections import Counter
    c = Counter(r["kat"] for r in rows)
    L = []
    L.append("# SKEN %s, %s UTC" % (HOST, time.strftime("%Y-%m-%d %H:%M", time.gmtime())))
    L.append("od: %s UTC · pregledano datoteka: %d · već viđeno (preskočeno): %d · novo: %d (%s)"
             % (time.strftime("%Y-%m-%d %H:%M", time.gmtime(od)), n_pregledano, n_vec, len(rows),
                ", ".join("%s %d" % (k, v) for k, v in sorted(c.items())) or "ništa"))
    L.append("domena skenirano: %d · isključeno: %d (%s)" % (len(skenirane), len(preskocene), ", ".join(preskocene)))
    L.append("izlaz: %s%s" % (izlaz, "  [BEZ UPISA, proba]" if a.bez_upisa else ""))
    N1 = None if a.puni_tekst else 2500; N2 = None if a.puni_tekst else 800
    mic = [r for r in rows if r["micanje"]]
    L.append(""); L.append("## 1. MICANJE S KARTE (%d) — uvijek prvo" % len(mic))
    for r in mic:
        L.append(""); L.append("### [%s] %s | %s | %s <%s> | %s" % (r["id"], r["kad"], r["box"], r["od_ime"], r["od"], r["predmet"]))
        L.append(r["iznad"][:N1])
        if r["ispod"]: L.append("--- ISPOD CITATA: " + r["ispod"][:N2])
    L.append(""); L.append("## 2. ODGOVORI I NOVE PORUKE")
    for r in rows:
        if r["kat"] in ("odgovor", "ostalo", "auto?") and not r["micanje"]:
            L.append(""); L.append("### [%s] %s | %s | %s | %s <%s> | %s" % (r["id"], r["kat"].upper(), r["kad"], r["box"], r["od_ime"], r["od"], r["predmet"]))
            L.append(r["iznad"][:N1] if r["iznad"] else "(prazno iznad citata)")
            if r["ispod"]: L.append("--- ISPOD CITATA: " + r["ispod"][:N2])
    L.append(""); L.append("## 3. BOUNCE I AUTOMATSKI (sažeto)")
    for r in rows:
        if r["kat"] in ("bounce", "auto"):
            L.append("- %s | %s | %s | %s | %s" % (r["kat"], r["kad"][:16], r["box"], r["od"][:50], r["predmet"][:70]))
    n_izv = sum(1 for r in rows if r["kat"] == "izvjestaj"); n_ws = sum(1 for r in rows if r["kat"] == "warmup_spam")
    L.append(""); L.append("## 4. SAMO BROJ: DMARC izvještaji %d · Snov warmup / označeni spam %d (u JSON-u su, u izvještaju ne)" % (n_izv, n_ws))
    print("\n".join(L))

if __name__ == "__main__":
    main()
