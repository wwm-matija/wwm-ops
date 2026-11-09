#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lov_web.py: s web stranica vinarija izvadi mail adrese. Samo čita javne stranice; u bazu ne piše ništa.

    python3 lov_web.py MAPA [--uzorak 200] [--niti 40] [--dio 0/3]

--dio i/n: obradi samo i-ti od n dijelova ulaza (za više procesa odjednom); izlaz web_rezultat_i.jsonl.

Ulaz:  MAPA/ulaz_web.jsonl   (lov_priprema.py)
Izlaz: MAPA/web_rezultat.jsonl, jedan redak po domeni (nastavlja gdje je stao):
  dom, stanje (ok | greska | parkirano), kraj (domena na kojoj je završio), stranica (koliko ih je otvoreno),
  mailovi: [{e, vrsta, gdje}]   vrsta: ista_domena | domena_kraja | besplatni | pec | druga_domena
  vinarije: [{wwm_id, cc, ime, skupina, mail, ime_na_webu, ime_u_domeni}]
Po domeni najviše 7 stranica: naslovnica, do 4 poveznice kontakta/impressuma s naslovnice, inače do 3 uobičajene putanje.
Pravi web = ime vinarije piše na stranici (jedna razlikovna riječ ako ime ima jednu, inače bar dvije).
"""
import io, json, os, re, sys, time, html, random, threading, unicodedata, zlib
import concurrent.futures as cf
from urllib.parse import urljoin, urlparse, unquote
import requests, urllib3

urllib3.disable_warnings()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
MAIL = re.compile(r"[A-Za-z0-9][A-Za-z0-9._%+\-]{0,48}@[A-Za-z0-9][A-Za-z0-9.\-]{1,60}\.[A-Za-z]{2,12}")
AT = re.compile(r"\s*(?:\[|\(|\{)\s*(?:at|chiocciola|arroba|ät|et|kukac|zavináč)\s*(?:\]|\)|\})\s*|\s+(?:\[at\]|\(at\))\s+", re.I)
DOT = re.compile(r"\s*(?:\[|\(|\{)\s*(?:dot|punto|point|punkt|tecka|tečka)\s*(?:\]|\)|\})\s*", re.I)
CF = re.compile(r'data-cfemail="([0-9a-fA-F]{10,})"|/cdn-cgi/l/email-protection#([0-9a-fA-F]{10,})')
KONTAKT = re.compile(r"contact|kontakt|contatt|contacto|contato|impressum|imprint|mentions|legal|legali|aviso|about|chi-siamo|chisiamo|nous|qui-sommes|uber-uns|ueber-uns|quienes|sobre|azienda|dove|where|find-us|visit|visita|privacy|datenschutz|elerhetoseg|kapcsolat|o-nas|onas|epikoinonia|iletisim|yhteys|kontakty", re.I)
PUTANJE = ["contact", "contatti", "kontakt", "contacto", "contact-us", "contato", "impressum", "mentions-legales", "kapcsolat"]
SMECE = re.compile(r"\.(png|jpe?g|gif|webp|svg|css|js|woff2?|ico)$|sentry|wixpress|example\.|@domain\.|yourdomain|youremail|your-email|email@email|name@|nome@|user@|test@|^your@|^mail@gmail|^email@|^info@example|^tuo@|^votre@|^tu@|^ejemplo@|^esempio@|^exemple@|@email\.com$|@mail\.com$|@dominio\.|@domaine\.|@site\.|@website\.|@test\.|godaddy|@sentry|@2x|@3x|noreply|no-reply|donotreply|@schema\.|@w3\.|@u00|protected|@medium\.|privacy@(wix|google)", re.I)
PARK = re.compile(r"domain (is|may be) for sale|buy this domain|this domain is parked|parked free|sedoparking|hugedomains|dan\.com|domaine? (est )?à vendre|dominio (è )?in vendita|diese domain (steht|ist) zum verkauf|dominio en venta|afternic|bodis", re.I)
BESPL = re.compile(r"^(gmail|googlemail|yahoo|ymail|hotmail|outlook|live|icloud|aol|msn|libero|virgilio|alice|tiscali|tin|fastwebnet|inwind|email|orange|wanadoo|free|laposte|sfr|neuf|bbox|gmx|web|t-online|freenet|seznam|centrum|volny|sapo|terra|uol|bol|telefonica|me|mac|mail|protonmail|proton|pm|yandex|rambler|bluewin|comcast|att|sbcglobal|verizon|bigpond|btinternet|shaw|telus|xtra|iinet|optusnet|skynet|telenet|hetnet|ziggo|kpn|planet|online|arcor|aon|chello|interia|wp|onet|o2|citromail|freemail|abv|163|126|qq|naver|hanmail|daum)\.", re.I)
PEC = re.compile(r"(^|[.\-])pec([.\-]|$)|legalmail|postecert|arubapec|pecimprese|sicurezzapostale|mypec|registerpec|gigapec|postacert|actaliscertymail|ticertifica|casellapec|lamiapec|pecditta", re.I)
OPCE = set("""winery wineries wine wines vineyard vineyards cellar cellars estate estates cantina cantine azienda agricola agricole societa società
soc srl spa sas snc ss coop cooperativa vini vino vinicola vitivinicola tenuta tenute fattoria podere poderi casa domaine domaines chateau château
clos cave caves vignoble vignobles vins vin earl scea gaec sarl sca bodega bodegas vinos vinedos viñedos viña vina finca quinta adega adegas vinhos
herdade weingut weinbau winzer winzergenossenschaft vinarija vinarstvo vinarstvi vinařství vinarstvo pince pinceszet pincészet boraszat borászat
birtok winnica crama vinaria the and of di de del della delle dei degli des du la le les il lo el los las et e y und von van der den da do dos
das san santa saint sainte st family famille famiglia fratelli hermanos sons son figli farm farms ranch company inc llc ltd pty gmbh co kft doo""".split())


def bez_naglasaka(s):
    return "".join(ch for ch in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(ch)).lower()


def rijeci_imena(ime):
    r = [w for w in re.findall(r"[a-z0-9]+", bez_naglasaka(ime)) if len(w) >= 3 and w not in OPCE and not w.isdigit()]
    return list(dict.fromkeys(r))


def ime_na(tekst_norm, ime):
    r = rijeci_imena(ime)
    if not r:
        return None
    n = sum(1 for w in r if re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", tekst_norm))
    return n >= (1 if len(r) == 1 else 2)


def cf_dekod(h):
    try:
        k = int(h[:2], 16)
        return "".join(chr(int(h[i:i + 2], 16) ^ k) for i in range(2, len(h), 2))
    except Exception:
        return ""


def dohvati(s, url, rok=12):
    try:
        r = s.get(url, timeout=(7, rok), stream=True, allow_redirects=True, verify=False)
        ct = r.headers.get("Content-Type", "")
        if r.status_code >= 400 or (ct and "html" not in ct and "text" not in ct and "json" not in ct):
            r.close(); return r.status_code, r.url, ""
        buf = b""
        for ch in r.iter_content(65536):
            buf += ch
            if len(buf) > 700000: break
        r.close()
        m = re.search(rb"charset=[\"']?([A-Za-z0-9_\-]+)", buf[:3000])
        enc = (m.group(1).decode("ascii", "ignore") if m else None) or r.encoding or "utf-8"
        try:
            t = buf.decode(enc, "replace")
        except LookupError:
            t = buf.decode("utf-8", "replace")
        return r.status_code, r.url, t
    except Exception as e:
        return 0, url, "!" + type(e).__name__


def mailovi_iz(t):
    nadeno = set()
    for a, b in CF.findall(t):
        e = cf_dekod(a or b)
        if "@" in e: nadeno.add(e)
    u = html.unescape(unquote(t))
    u2 = DOT.sub(".", AT.sub("@", u))
    for src in (u, u2):
        for e in MAIL.findall(src): nadeno.add(e)
    cisto = set()
    for e in nadeno:
        e = re.sub(r"^(u003e|u003c|x3e|20|mailto:)+", "", e.strip(".-_ ").lower())
        if "@" not in e or SMECE.search(e) or ".." in e or len(e.split("@")[0]) > 40:
            continue
        cisto.add(e)
    return cisto


def tekst_stranice(t):
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", t)
    naslov = " ".join(re.findall(r"(?is)<title[^>]*>(.*?)</title>", t)[:1])
    meta = " ".join(re.findall(r'(?is)<meta[^>]+content="([^"]{3,300})"', t)[:12])
    return bez_naglasaka(html.unescape(naslov + " " + meta + " " + re.sub(r"(?s)<[^>]+>", " ", t)))


def osnova(dom_):
    p = dom_.lower().split(".")
    if len(p) >= 3 and p[-2] in ("co", "com", "org", "net", "gov", "ac", "edu") and len(p[-1]) == 2:
        return ".".join(p[-3:])
    return ".".join(p[-2:])


def obradi(z):
    dom_ = z["dom"]; t0 = time.time()
    s = requests.Session(); s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Language": "en,it;q=0.8,fr;q=0.7,es;q=0.6,de;q=0.5"})
    st, kraj_url, t = 0, "", ""
    for u in ("https://" + dom_ + "/", "https://www." + dom_ + "/", "http://" + dom_ + "/"):
        st, kraj_url, t = dohvati(s, u)
        if t and not t.startswith("!"): break
    out = dict(dom=dom_, stanje="greska", http=st, kraj="", stranica=0, mailovi=[], vinarije=[], s=0.0)
    if not t or t.startswith("!"):
        out["greska"] = t[1:] if t else "http %s" % st
        out["vinarije"] = [dict(v, ime_na_webu=None, ime_u_domeni=None) for v in z["vinarije"]]
        out["s"] = round(time.time() - t0, 1); return out
    kraj = re.sub(r"^www\.", "", urlparse(kraj_url).netloc.lower().split(":")[0])
    out.update(stanje="ok", kraj=kraj, stranica=1)
    gdje = {}
    for e in mailovi_iz(t): gdje.setdefault(e, kraj_url)
    sav = tekst_stranice(t)
    if PARK.search(t[:20000]) or (len(sav) < 400 and not gdje and re.search(r"domain|dominio|domaine", sav)):
        out["stanje"] = "parkirano"
    else:
        veze = []
        for href, txt in re.findall(r'(?is)<a\s[^>]*href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', t)[:600]:
            if href.lower().startswith(("mailto:", "tel:", "javascript:")): continue
            if KONTAKT.search(href) or KONTAKT.search(re.sub(r"<[^>]+>", " ", txt)[:60]):
                u = urljoin(kraj_url, href)
                if osnova(urlparse(u).netloc.lower().split(":")[0] or kraj) == osnova(kraj) and u not in veze and u.rstrip("/") != kraj_url.rstrip("/"):
                    veze.append(u)
        veze.sort(key=lambda u: (0 if re.search(r"contact|kontakt|contatt|contato|kapcsolat", u, re.I) else 1 if re.search(r"impressum|imprint|mentions|legal", u, re.I) else 2, len(u)))
        ciljevi = veze[:4] if veze else [urljoin(kraj_url, "/" + p) for p in PUTANJE[:3]]
        if veze and not gdje and len(veze) < 2: ciljevi += [urljoin(kraj_url, "/" + p) for p in PUTANJE[:2]]
        for u in ciljevi[:6]:
            if time.time() - t0 > 50: break
            st2, ku, t2 = dohvati(s, u, rok=10)
            if not t2 or t2.startswith("!"): continue
            out["stranica"] += 1
            for e in mailovi_iz(t2): gdje.setdefault(e, ku)
            sav += " " + tekst_stranice(t2)[:60000]
    for e, u in sorted(gdje.items()):
        md = e.split("@")[-1]
        vrsta = ("pec" if PEC.search(md) else "ista_domena" if osnova(md) == osnova(dom_) else "domena_kraja" if osnova(md) == osnova(kraj or dom_)
                 else "besplatni" if BESPL.match(md) else "druga_domena")
        out["mailovi"].append(dict(e=e, vrsta=vrsta, gdje=u[:160]))
    dn = re.sub(r"[^a-z0-9]", "", bez_naglasaka(osnova(kraj or dom_).split(".")[0]))
    for v in z["vinarije"]:
        r = rijeci_imena(v["ime"])
        out["vinarije"].append(dict(v, ime_na_webu=ime_na(sav, v["ime"]), ime_u_domeni=(any(w in dn for w in r if len(w) >= 4) if r else None)))
        if v.get("gr"):
            g = bez_naglasaka(v["gr"]).strip()
            out["vinarije"][-1]["mjesto_na_webu"] = bool(g) and len(g) >= 3 and g in sav
    out["s"] = round(time.time() - t0, 1)
    return out


def main():
    mapa = sys.argv[1]
    uzorak = int(sys.argv[sys.argv.index("--uzorak") + 1]) if "--uzorak" in sys.argv else 0
    niti = int(sys.argv[sys.argv.index("--niti") + 1]) if "--niti" in sys.argv else 40
    dio = sys.argv[sys.argv.index("--dio") + 1].split("/") if "--dio" in sys.argv else None
    izl = mapa + ("/web_uzorak.jsonl" if uzorak else "/web_rezultat_%s.jsonl" % dio[0] if dio else "/web_rezultat.jsonl")
    ulaz = [json.loads(l) for l in io.open(mapa + "/ulaz_web.jsonl", encoding="utf-8")]
    if dio:
        ulaz = [z for z in ulaz if zlib.crc32(z["dom"].encode()) % int(dio[1]) == int(dio[0])]
    gotovo = set()
    if os.path.exists(izl):
        for l in io.open(izl, encoding="utf-8"):
            try: gotovo.add(json.loads(l)["dom"])
            except Exception: pass
    if uzorak:
        random.seed(911); ulaz = random.sample(ulaz, min(uzorak, len(ulaz)))
    else:
        random.seed(912); random.shuffle(ulaz)          # da isti poslužitelj ne dobije niz zahtjeva zaredom
    posao = [z for z in ulaz if z["dom"] not in gotovo]
    print("domena u ulazu %d, već gotovo %d, radim %d, niti %d" % (len(ulaz), len(gotovo), len(posao), niti), flush=True)
    brava = threading.Lock(); t0 = time.time(); n = 0
    with io.open(izl, "a", encoding="utf-8") as f, cf.ThreadPoolExecutor(niti) as ex:
        for r in ex.map(obradi, posao):
            with brava:
                f.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
                if n % 500 == 0:
                    f.flush(); print("%s  %d / %d  (%.1f domena/s)" % (time.strftime("%H:%M:%S"), n, len(posao), n / (time.time() - t0)), flush=True)
    print("GOTOVO: %d domena u %.0f s (%.2f domena/s)" % (n, time.time() - t0, n / max(1, time.time() - t0)), flush=True)


if __name__ == "__main__":
    main()
