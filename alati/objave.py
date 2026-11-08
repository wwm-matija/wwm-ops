#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
objave.py: pretraga medijskih objava naših PR tekstova TOČNIM frazama kroz DataForSEO (samo standard queue),
provjera stranica i vođenje popisa objava. Objedinjuje ranije skripte plan/dfs/kandidati/zapisi (21.10., 28.10., 3.11.2026.).

Radi na laptopu (ključ DataForSEO je u `C:/Users/world/wwm/.env.bevanda`, varijabla DATAFORSEO_B64) ili na stroju
gdje postoji datoteka iz env var DFS_ENV. Ključ se nikad ne ispisuje. Podaci žive u `out/objave/`; popis objava
`out/OBJAVE_SVE.json` ide u git.

Koraci (svaki je zasebna naredba; sve osim `posalji` je besplatno):
  python alati/objave.py fraze --izvor press-popis PUTANJA/PRESS_POPIS.json --val nise
        naslovi press stranica -> out/objave/fraze_nise.json (kw, cc, lang, tip, val)
  python alati/objave.py fraze --izvor csv PUTANJA.csv --val lokvin --kolona naslov --cc-kolona cc --lang-kolona lang
  python alati/objave.py plan --val nise [--od 2026-10-30 --do 2026-11-08] [--bez-news]
        fraze -> upiti (organic + news, depth 50, datumski raspon), ispis BROJKI i procjene troška; NIŠTA se ne šalje
  python alati/objave.py posalji --val nise --strop 3.00
        task_post u paketima <=100, ID-jevi odmah u out/objave/taskovi.jsonl; tvrdi strop u USD; traži Matijinu riječ
  python alati/objave.py kupi [--minute 60]
        task_get po ID-ju za sve postane a nepokupljene; rezultati u out/objave/rezultati.json (smije se ponavljati)
  python alati/objave.py kandidati [--maks 300]
        iz rezultata izdvoji URL-ove koji NISU u out/OBJAVE_SVE.json i imaju signal (ime karte, Gavrilović, 4,3 mil., fraza),
        otvori stranice (Chrome UA, 1 s po domeni), utvrdi spomen, link na kartu, datum, naslov -> out/objave/kandidati.json
        + čitljiv pregled out/objave/KANDIDATI.md za Matiju
  python alati/objave.py zapisi --iz out/objave/potvrdjeno.json
        potvrđene (Matija ili agent po pregledu) dopiši u out/OBJAVE_SVE.json (+ .csv); dedupe po URL-u

Pravila (iz kanona i memorije): nikad live endpoint; samo točne fraze pod navodnicima; po jeziku jedna lokacija;
bez qdr:m, raspon datuma od dana slanja PR-a; depth 50; news samo za državne tekstove (ne za regionalne);
dedupe prema OBJAVE_SVE; svaku novu stranicu otvoriti i zapisati link na kartu. Već poslane press brojke se ne mijenjaju.
"""
import argparse, collections, csv, glob, html, io, json, os, re, sys, time, threading, unicodedata
from urllib.parse import urlparse, parse_qs, unquote
import concurrent.futures as cf

try:
    import requests, urllib3
    urllib3.disable_warnings()
except ImportError:
    requests = None

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OVDJE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(OVDJE)
OUT = os.path.join(REPO, "out", "objave")
LEDGER_JSON = os.path.join(REPO, "out", "OBJAVE_SVE.json")
LEDGER_CSV = os.path.join(REPO, "out", "OBJAVE_SVE.csv")
TASKOVI = os.path.join(OUT, "taskovi.jsonl")
REZ = os.path.join(OUT, "rezultati.json")
KAND = os.path.join(OUT, "kandidati.json")
API = "https://api.dataforseo.com/v3/"
CIJENA_PROC = 0.003  # USD po tasku, depth 50, standard queue (nominalno; prava cijena iz 'cost')
ENV_KANDIDATI = [os.environ.get("DFS_ENV", ""), "C:/Users/world/wwm/.env.bevanda", os.path.expanduser("~/.env.dataforseo"), "/root/.env.dataforseo"]

PRESS = ["worldwinerymap", "winerymap", "pr-voice", "031news", "051news", "021news", "01news", "1brand", "brand365", "brand77", "nobilistrade",
         "nobilis777", "365promo", "communiquepresse", "mediaeco", "elaltavoz", "altifalante", "altofalante", "reflectormedia", "omnialuxe", "top365",
         "antilalos", "ohlas.eu", "medienecho", "visszhang", "otzvuk", "rozglos", "prvoice", "365pr", "cityranking", "osjecki", "rijecki", "splitski", "zagrebacki"]
OWN = PRESS + ["einpresswire", "einnews", "prnewswire", "facebook", "instagram", "linkedin", "tiktok", "youtube", "x.com", "twitter", "pinterest", "reddit",
               "threads", "crunchbase", "google.", "bing.", "shutterstock", "dreamstime", "stock.adobe", "alamy", "istockphoto", "gettyimages", "depositphotos",
               "vectorstock", "etsy", "ebay", "amazon", "abebooks", "wikipedia", "msn.com", "news.google", "flipboard", "whatsapp", "t.me", "telegram", "vk.com", "ok.ru", "scribd"]
TWO = {"co.za", "com.ar", "com.br", "co.uk", "com.mx", "co.nz", "com.au", "co.il", "com.pl", "org.uk", "com.tr", "co.jp", "com.cy", "com.uy", "com.pe", "org.il",
       "com.ua", "org.ua", "co.in", "gov.uk", "ac.uk", "or.jp", "ne.jp", "org.br", "gov.br", "org.ar", "gob.ar", "gob.mx", "gob.es", "net.au", "org.au", "com.ge",
       "com.gr", "org.mk", "com.mk", "co.rs", "org.rs", "in.rs", "co.me", "com.hr", "com.ba", "com.ro", "com.bg", "com.md", "net.br", "com.co", "com.ec", "com.ve",
       "co.ma", "press.ma", "co.at", "or.at", "com.cn", "com.tw", "co.kr", "com.sg", "com.my", "co.id", "net.mk", "edu.mk", "gov.mk", "gov.rs", "gov.ba", "gov.si"}
SIG = re.compile(r"world\s?winery\s?map|worldwinerymap|gavrilovi|гавриловиќ|гавриловић|umag|умаг|m\.\s?g\.\s?solutions|4[.,]3\s?(mil|мил|mln|εκατ|מיליון|million)")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
      "Accept-Language": "en,hr;q=0.8,*;q=0.5", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
LANGMAP = {"zh-cn": "zh-CN", "zh-tw": "zh-TW", "pt-br": "pt", "pt-pt": "pt"}


# ---------------- pomoćno ----------------
def hdr():
    for p in ENV_KANDIDATI:
        if p and os.path.exists(p):
            for l in io.open(p, encoding="utf-8"):
                if l.startswith("DATAFORSEO_B64"):
                    return {"Authorization": "Basic " + l.split("=", 1)[1].strip().strip('"'), "Content-Type": "application/json"}
    sys.exit("STOP: nema DATAFORSEO_B64 ni u jednoj od: %s (postavi DFS_ENV na putanju .env datoteke)" % ", ".join(p for p in ENV_KANDIDATI if p))


def ucitaj_json(p, zadano):
    return json.load(io.open(p, encoding="utf-8")) if os.path.exists(p) else zadano


def spremi_json(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(d, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)


def reg(d):
    p = (d or "").lower().replace("www.", "").split(".")
    return ".".join(p[-3:]) if len(p) >= 3 and ".".join(p[-2:]) in TWO else ".".join(p[-2:])


def own(d):
    return any(o in (d or "").lower() for o in OWN)


def norm(u):
    u = re.sub(r"#.*$", "", (u or "").strip())
    u = re.sub(r"[?&](utm_[^&]+|fbclid=[^&]+|amp=?[^&]*)", "", u)
    return u.rstrip("/").replace("http://", "https://").replace("https://www.", "https://").replace("/amp/", "/").replace("/mobile/", "/")


def bez(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return re.sub(r"\s+", " ", "".join(c for c in s if not unicodedata.combining(c)))


def kratko(s, n=90):
    s = re.sub(r"\s+", " ", s or "").strip().strip("*")
    if s[:40].count(" ") < 2:  # jezici bez razmaka (zh, ja, th): do prvog interpunkcijskog znaka
        return re.split(r"[，、。,：:]", s)[0][:28]
    if len(s) <= n:
        return s
    c = s[:n]
    if " " in c[20:]:
        c = c.rsplit(" ", 1)[0]
    return c.rstrip(" ,;:،，、")


def lokacije():
    """cc -> location_name iz DFS popisa (besplatan endpoint), keširano u out/objave/dfs_locations.json."""
    p = os.path.join(OUT, "dfs_locations.json")
    if not os.path.exists(p):
        r = requests.get(API + "serp/google/locations", headers=hdr(), timeout=120).json()
        L = [x for t in r.get("tasks") or [] for x in (t.get("result") or []) if x.get("location_type") == "Country"]
        spremi_json(p, L)
    L = ucitaj_json(p, [])
    m = {x["country_iso_code"]: x["location_name"] for x in L}
    m.setdefault("TW", "Taiwan"); m.setdefault("HK", "Hong Kong")
    return m


def jezici():
    p = os.path.join(OUT, "dfs_languages.json")
    if not os.path.exists(p):
        r = requests.get(API + "serp/google/languages", headers=hdr(), timeout=120).json()
        spremi_json(p, [x for t in r.get("tasks") or [] for x in (t.get("result") or [])])
    return {x["language_code"] for x in ucitaj_json(p, [])}


def ledger():
    return ucitaj_json(LEDGER_JSON, [])


# ---------------- fraze ----------------
def cmd_fraze(a):
    F = []
    if a.izvor == "press-popis":
        # ključ je npr. AE_ar, AE_ar_bf (varijanta teksta), R-ES-DOP-012_es (regionalni tekst), R-FINGER-LAKES_en (US regija)
        for x in ucitaj_json(a.putanja, []):
            k = x.get("kljuc", "")
            dijelovi = k.split("_")
            kod = dijelovi[0]; lang = dijelovi[1].lower() if len(dijelovi) > 1 else ""
            lang = LANGMAP.get(lang, lang)
            tip = "naslov"
            if kod.startswith("R-"):
                tip = "naslov-regija"
                p0 = kod[2:].split("-")[0]
                cc = p0 if len(p0) == 2 and p0.isalpha() else "US"
            else:
                cc = kod[:2]
            if x.get("naslov"):
                F.append(dict(kw=kratko(x["naslov"], 110), cc=cc.upper(), lang=lang, tip=tip, val=a.val, izvor=k))
    elif a.izvor == "csv":
        with io.open(a.putanja, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                kw = (row.get(a.kolona) or "").strip()
                if kw:
                    F.append(dict(kw=kratko(kw, 110), cc=(row.get(a.cc_kolona) or "").upper(), lang=LANGMAP.get((row.get(a.lang_kolona) or "").lower(), (row.get(a.lang_kolona) or "").lower()),
                                  tip=a.tip, val=a.val, izvor=os.path.basename(a.putanja)))
    else:
        sys.exit("STOP: --izvor press-popis ili csv")
    seen = set(); U = []
    for f in F:
        k = (f["kw"], f["cc"], f["lang"])
        if k in seen or len(f["kw"]) < 8:
            continue
        seen.add(k); U.append(f)
    p = os.path.join(OUT, "fraze_%s.json" % a.val)
    spremi_json(p, U)
    print("fraze: %d (iz %d redaka) -> %s" % (len(U), len(F), p))
    print("po jeziku:", dict(collections.Counter(f["lang"] for f in U).most_common(12)))
    print("bez jezika:", sum(1 for f in U if not f["lang"]), "| bez zemlje:", sum(1 for f in U if not f["cc"]))


# ---------------- plan ----------------
def cmd_plan(a):
    F = ucitaj_json(os.path.join(OUT, "fraze_%s.json" % a.val), None)
    if F is None:
        sys.exit("STOP: nema out/objave/fraze_%s.json; prvo `fraze`" % a.val)
    LOC = lokacije(); JEZ = jezici()
    tbs = "tbs=cdr:1,cd_min:%s,cd_max:%s" % (us_datum(a.od), us_datum(a.do_)) if a.od else ""
    P = []; bez_loc = collections.Counter(); bez_jez = collections.Counter()
    for f in F:
        lang = f["lang"]
        if lang not in JEZ:
            bez_jez[lang or "?"] += 1; continue
        loc = LOC.get(f["cc"])
        if not loc:
            bez_loc[f["cc"] or "?"] += 1; loc = "United States"
        kw = '"%s"' % f["kw"].strip().strip('"„“«»').strip()
        # news samo za državne tekstove; regionalni tekstovi idu samo organic (pravilo iz memorije 21.10.)
        vrste = ["organic"] if (a.bez_news or f["tip"].endswith("regija")) else ["organic", "news"]
        for v in vrste:
            P.append(dict(vrsta=v, keyword=kw, location_name=loc, language_code=lang, tip=f["tip"], val=a.val, tbs=tbs, izvor=f.get("izvor", "")))
    u = {}
    for t in P:
        u.setdefault((t["vrsta"], t["keyword"], t["location_name"], t["language_code"]), t)
    P = list(u.values())
    p = os.path.join(OUT, "plan_%s.json" % a.val)
    spremi_json(p, P)
    print("PLAN %s: %d upita (%s) iz %d fraza; %d različitih fraza; %d parova jezik×lokacija; %d jezika"
          % (a.val, len(P), ", ".join("%s %d" % kv for kv in collections.Counter(t["vrsta"] for t in P).items()), len(F),
             len({t["keyword"] for t in P}), len({(t["language_code"], t["location_name"]) for t in P}), len({t["language_code"] for t in P})))
    print("raspon datuma:", tbs or "BEZ (cijela povijest)", "| procjena troška: %.2f USD (%d × %.3f)" % (len(P) * CIJENA_PROC, len(P), CIJENA_PROC))
    if bez_jez: print("preskočeno, jezik nije u DFS:", dict(bez_jez))
    if bez_loc: print("zemlja nije u DFS (ide na United States):", dict(bez_loc))
    print("-> %s ; ništa nije poslano. Slanje: `posalji --val %s --strop <USD>` tek na Matijinu riječ." % (p, a.val))


def us_datum(s):
    y, m, d = s.split("-")
    return "%d/%d/%s" % (int(m), int(d), y)


# ---------------- posalji ----------------
def postano():
    if not os.path.exists(TASKOVI):
        return [], 0.0
    L = [json.loads(l) for l in io.open(TASKOVI, encoding="utf-8") if l.strip()]
    return L, sum((x.get("cost") or 0) for x in L)


def cmd_posalji(a):
    P = ucitaj_json(os.path.join(OUT, "plan_%s.json" % a.val), None)
    if P is None:
        sys.exit("STOP: nema plana; prvo `plan --val %s`" % a.val)
    H = hdr()
    L, trosak = postano()
    vec = {(x["vrsta"], x["kw"], x["loc"], x["lang"], x.get("tbs", "")) for x in L if x.get("status") == 20100}
    lista = [t for t in P if (t["vrsta"], t["keyword"], t["location_name"], t["language_code"], t.get("tbs", "")) not in vec]
    if a.samo_proba:
        lista = lista[:2]
    print("za slanje %d od %d (već postano %d, potrošeno dosad %.4f USD), strop %.2f USD" % (len(lista), len(P), len(P) - len(lista), trosak, a.strop))
    if trosak + len(lista) * CIJENA_PROC > a.strop:
        print("UPOZORENJE: procjena %.2f USD prelazi strop; šaljem dok strop ne stane." % (trosak + len(lista) * CIJENA_PROC))
    os.makedirs(OUT, exist_ok=True)
    for v in ("organic", "news"):
        Q = [t for t in lista if t["vrsta"] == v]
        for i in range(0, len(Q), 100):
            dio = Q[i:i + 100]
            if trosak + len(dio) * CIJENA_PROC > a.strop:
                print("STROP: stajem, postano %.4f USD" % trosak); return
            payload = []
            for t in dio:
                p = {"keyword": t["keyword"], "location_name": t["location_name"], "language_code": t["language_code"], "depth": 50,
                     "tag": "%s|%s|%s|%s|%s" % (t["val"], v, t["language_code"], t["location_name"], t["tip"])}
                if t.get("tbs"):
                    p["search_param"] = t["tbs"]
                payload.append(p)
            r = requests.post(API + "serp/google/%s/task_post" % v, headers=H, json=payload, timeout=120).json()
            with io.open(TASKOVI, "a", encoding="utf-8") as f:
                for tk, t in zip(r.get("tasks") or [], dio):
                    d = tk.get("data") or {}
                    f.write(json.dumps({"id": tk.get("id"), "vrsta": v, "kw": d.get("keyword"), "loc": d.get("location_name"), "lang": d.get("language_code"),
                                        "tag": d.get("tag"), "tbs": t.get("tbs", ""), "status": tk.get("status_code"), "poruka": tk.get("status_message"),
                                        "cost": tk.get("cost"), "val": t["val"], "vrijeme": time.strftime("%Y-%m-%d %H:%M:%S")}, ensure_ascii=False) + "\n")
                    trosak += tk.get("cost") or 0
                    if tk.get("status_code") != 20100:
                        print("  GREŠKA", tk.get("status_code"), tk.get("status_message"), d.get("keyword"), d.get("location_name"))
            print(v, i, len(dio), r.get("status_message"), "cijena paketa", r.get("cost"), "ukupno postano %.4f" % trosak, flush=True)
    print("GOTOVO posalji: ukupno potrošeno %.4f USD; sad `kupi`" % trosak)


# ---------------- kupi ----------------
K_POLJA = ("type", "rank_absolute", "url", "domain", "title", "description", "snippet", "timestamp", "time_published", "source")


def _kupi_jedan(t, H):
    try:
        g = requests.get(API + "serp/google/%s/task_get/advanced/%s" % (t["vrsta"], t["id"]), headers=H, timeout=60).json()
    except Exception:
        return None
    tk = (g.get("tasks") or [{}])[0]; sc = tk.get("status_code")
    if sc == 20000:
        items = []
        for res in tk.get("result") or []:
            for it in (res or {}).get("items") or []:
                if isinstance(it, dict):
                    items.append({k: it.get(k) for k in K_POLJA})
                    for s in (it.get("items") or []):
                        if isinstance(s, dict) and s.get("url"):
                            items.append({k: s.get(k) for k in K_POLJA})
        return dict(id=t["id"], vrsta=t["vrsta"], kw=t["kw"], loc=t["loc"], lang=t["lang"], tag=t.get("tag"), val=t.get("val"), cost=tk.get("cost"), items=items)
    if sc not in (40601, 40602, 20100, None):
        return dict(id=t["id"], vrsta=t["vrsta"], kw=t["kw"], loc=t["loc"], lang=t["lang"], tag=t.get("tag"), val=t.get("val"), greska="%s %s" % (sc, tk.get("status_message")), items=[])
    return None


def cmd_kupi(a):
    H = hdr()
    L, _ = postano(); T = [t for t in L if t.get("status") == 20100]
    rez = {r["id"]: r for r in ucitaj_json(REZ, [])}
    t0 = time.time()
    while time.time() - t0 < a.minute * 60:
        ost = [t for t in T if t["id"] not in rez]
        if not ost:
            break
        with cf.ThreadPoolExecutor(12) as ex:
            for r in ex.map(lambda t: _kupi_jedan(t, H), ost):
                if r:
                    rez[r["id"]] = r
        spremi_json(REZ, list(rez.values()))
        print(time.strftime("%H:%M:%S"), "pokupljeno %d / %d" % (len(rez), len(T)), flush=True)
        if len(rez) < len(T):
            time.sleep(120)
    print("KRAJ kupi: %d / %d, s greškom %d, stavki ukupno %d -> %s" % (len(rez), len(T), sum(1 for r in rez.values() if r.get("greska")),
                                                                         sum(len(r.get("items") or []) for r in rez.values()), REZ))


# ---------------- kandidati ----------------
LOCK = threading.Lock(); ZADNJE = {}


def pauza(dom):
    while True:
        with LOCK:
            if time.time() - ZADNJE.get(dom, 0) >= 1.0:
                ZADNJE[dom] = time.time(); return
        time.sleep(0.3)


def get_stranica(u, dom):
    pauza(dom)
    t0 = time.time(); buf = b""
    try:
        with requests.get(u, headers=UA, timeout=30, verify=False, allow_redirects=True, stream=True) as r:
            for ch in r.iter_content(65536):
                buf += ch
                if len(buf) > 3000000 or time.time() - t0 > 40:
                    break
            enc = r.encoding if r.encoding and r.encoding.lower() != "iso-8859-1" else None
            txt = buf.decode(enc or "utf-8", errors="ignore")
            if not enc:
                m = re.search(rb'charset=["\']?([\w-]+)', buf[:5000])
                if m and m.group(1).lower() not in (b"utf-8", b"utf8"):
                    try: txt = buf.decode(m.group(1).decode(), errors="ignore")
                    except Exception: pass
            return r.status_code, r.url, txt
    except Exception as e:
        return 0, u, "ERR " + str(e)[:120]


def nasa(h):
    h = html.unescape(h); p = urlparse(h)
    if any(x in p.netloc.lower() for x in PRESS):
        return h
    q = parse_qs(p.query)
    for k in ("u", "url", "q"):
        if k in q:
            v = unquote(q[k][0])
            if any(x in urlparse(v).netloc.lower() for x in PRESS):
                return v
    return None


DATE_RX = [r'article:published_time["\']?\s+content=["\']([^"\']+)', r'content=["\']([^"\']+)["\']\s+(?:property|name)=["\']article:published_time',
           r'"datePublished"\s*:\s*"([^"]+)"', r'(?:property|name|itemprop)=["\'](?:og:published_time|pubdate|publishdate|date|dc\.date|datePublished)["\']\s+content=["\']([^"\']+)',
           r'<time[^>]+datetime=["\']([^"\']+)']


def datum_str(h, u):
    for rx in DATE_RX:
        m = re.search(rx, h, re.I)
        if m and re.match(r"20\d\d-\d\d-\d\d", m.group(1)):
            return m.group(1)[:10], "meta"
    m = re.search(r"/(20\d\d)[/-](\d\d)[/-](\d\d)/", u)
    return ("%s-%s-%s" % m.groups(), "url") if m else ("", "")


def fraza_ok(kw, txt):
    f = [w for w in re.findall(r"\w+", bez(kw.replace("site:", " "))) if len(w) > 2]
    if not f:
        return False
    t = bez(txt)
    return sum(1 for w in f if w in t) / len(f) >= 0.75


def provjeri_stranicu(c):
    st, fu, h = get_stranica(c["url"], c["reg"])
    tekst = re.sub(r"(?s)<(script|style|noscript)\b.*?</\1>", " ", h); tekst = html.unescape(re.sub(r"<[^>]+>", " ", tekst))
    tl = re.sub(r"\s+", " ", tekst.lower()); low = h.lower()
    n_ime = len(re.findall(r"world\s?winery\s?map", tl)); n_dom = len(re.findall(r"worldwinerymap", tl)); n_raw = len(re.findall(r"worldwinerymap|world\s?winery\s?map", low))
    n_ost = len(re.findall(r"gavrilovi|гавриловиќ|гавриловић|m\.\s?g\.\s?solutions", tl))
    tags = re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>', h, re.I); full = re.findall(r'<a\b[^>]*href=["\'][^"\']+["\'][^>]*>', h, re.I)
    L = []; nof = 0
    for t, f in zip(tags, full):
        n = nasa(t)
        if n:
            L.append(n); nof += bool(re.search(r'rel=["\'][^"\']*(nofollow|sponsored|ugc)', f, re.I))
    m = re.search(r"<title[^>]*>(.*?)</title>", h, re.I | re.S); naslov = re.sub(r"\s+", " ", html.unescape(m.group(1))).strip()[:250] if m else ""
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)', h, re.I); og = html.unescape(m.group(1)).strip()[:250] if m else ""
    m = re.search(r'<html[^>]*\blang=["\']([A-Za-z-]+)', h, re.I); lang = m.group(1).lower()[:5] if m else ""
    dt, dt_izv = datum_str(h, fu)
    m = re.search(r".{0,160}(world\s?winery\s?map|worldwinerymap|gavrilovi|гавриловиќ|гавриловић).{0,160}", tl); isj = m.group(0) if m else ""
    if st != 200: kl = "nije otvoreno (%s), potvrđeno isječkom" % st if st in (401, 403, 429, 503) else "ne otvara se (%s)" % st
    elif L and nof < len(L): kl = "LINK dofollow"
    elif L: kl = "LINK nofollow"
    elif n_dom: kl = "adresa napisana, bez linka"
    elif n_ime: kl = "samo ime, bez adrese"
    elif n_ost: kl = "samo Gavrilović/M.G. Solutions, bez imena karte"
    else: kl = "nema spomena u HTML-u"
    c.update(status=st, final=fu, n_ime=n_ime, n_dom=n_dom, n_ost=n_ost, linkovi=sorted(set(L))[:6], n_link=len(L), n_nofollow=nof, link_klasa=kl,
             naslov=og or naslov, html_lang=lang, datum=dt, datum_izvor=dt_izv, isjecak=isj[:340], potvrdjeno=bool(n_ime or n_dom or n_raw))
    return c


def cmd_kandidati(a):
    R = ucitaj_json(REZ, None)
    if R is None:
        sys.exit("STOP: nema out/objave/rezultati.json; prvo `kupi`")
    POZ = ledger()
    POZ_URL = {norm(p["url"]) for p in POZ if p.get("url")}
    POZ_REG = {reg(urlparse(p["url"]).netloc) for p in POZ if p.get("url")} | {reg(p.get("medij", "")) for p in POZ}

    def poznat(n):
        return n in POZ_URL or any(len(p) > 40 and (n.startswith(p) or p.startswith(n)) for p in POZ_URL)

    C = collections.OrderedDict()
    for r in R:
        for it in r.get("items") or []:
            u = it.get("url"); d = (it.get("domain") or urlparse(u or "").netloc or "").lower()
            if not u or not d or own(d):
                continue
            n = norm(u); txt = "%s %s" % (it.get("title") or "", it.get("description") or it.get("snippet") or "")
            c = C.setdefault(n, dict(url=u, norm=n, domena=d.replace("www.", ""), reg=reg(d), serp_naslov=it.get("title") or "",
                                     serp_opis=(it.get("description") or it.get("snippet") or "")[:400], serp_vrijeme=it.get("timestamp") or it.get("time_published") or "",
                                     pogoci=[], poznat_url=poznat(n), poznata_domena=reg(d) in POZ_REG, signal=False, val=r.get("val", "")))
            c["pogoci"].append("%s|%s|%s|%s" % (r["kw"], r["lang"], r["loc"], r["vrsta"]))
            if SIG.search(txt.lower()) or fraza_ok(r["kw"], txt):
                c["signal"] = True
    SVI = list(C.values())
    NOVI = sorted([c for c in SVI if not c["poznat_url"] and c["signal"]], key=lambda c: -len(c["pogoci"]))
    print("URL-ova u SERP-u (bez naših i društvenih) %d | poznatih %d | novih sa signalom %d | novih bez signala %d"
          % (len(SVI), sum(c["poznat_url"] for c in SVI), len(NOVI), sum(1 for c in SVI if not c["poznat_url"] and not c["signal"])))
    STARO = {c["norm"]: c for c in ucitaj_json(KAND, {}).get("otvoreni", []) if "status" in c}
    OTV = NOVI[:a.maks]

    def jedan(c):
        s = STARO.get(c["norm"])
        if s:
            s["pogoci"] = c["pogoci"]; return s
        return provjeri_stranicu(c)

    t0 = time.time()
    with cf.ThreadPoolExecutor(12) as ex:
        Lr = list(ex.map(jedan, OTV))
    spremi_json(KAND, {"svi": SVI, "otvoreni": Lr, "vrijeme": time.strftime("%Y-%m-%d %H:%M")})
    print("otvoreno %d (%d s) | potvrđeno %d | ne otvara se %d" % (len(Lr), round(time.time() - t0), sum(c["potvrdjeno"] for c in Lr), sum(1 for c in Lr if c["status"] != 200)))
    print(dict(collections.Counter(c["link_klasa"] for c in Lr)))
    # čitljiv pregled za Matiju
    M = ["# KANDIDATI OBJAVA, %s" % time.strftime("%d.%m.%Y. %H:%M"), "",
         "Novih URL-ova sa signalom: %d, otvoreno: %d, potvrđeno spomenom na stranici: %d. Poznate (već u OBJAVE_SVE): %d."
         % (len(NOVI), len(Lr), sum(c["potvrdjeno"] for c in Lr), sum(c["poznat_url"] for c in SVI)), "",
         "## Potvrđene (spomen karte na stranici)", ""]
    for c in sorted([c for c in Lr if c["potvrdjeno"]], key=lambda c: c.get("datum") or "", reverse=True):
        M.append("- **%s** · %s · %s · %s · [%s]\n  %s\n  pogodaka %d: %s" % (c["domena"], c.get("datum") or "bez datuma", c.get("html_lang") or "?", c["link_klasa"], c["url"],
                                                                      (c.get("naslov") or c["serp_naslov"])[:160], len(c["pogoci"]), c["pogoci"][0][:100]))
    M += ["", "## Nisu potvrđene na stranici (samo SERP signal) ili se ne otvaraju", ""]
    for c in [c for c in Lr if not c["potvrdjeno"]]:
        M.append("- %s · %s · %s · [%s] %s" % (c["domena"], c["link_klasa"], c.get("datum") or "", c["url"], (c.get("naslov") or c["serp_naslov"])[:120]))
    io.open(os.path.join(OUT, "KANDIDATI.md"), "w", encoding="utf-8", newline="\n").write("\n".join(M) + "\n")
    print("-> %s i %s" % (KAND, os.path.join(OUT, "KANDIDATI.md")))


# ---------------- zapisi ----------------
LEDGER_POLJA = ["cc", "medij", "naslov", "url", "datum", "vrsta", "jezik", "status", "link_karta"]


def cmd_zapisi(a):
    N = ucitaj_json(a.iz, None)
    if N is None:
        sys.exit("STOP: nema %s" % a.iz)
    SVE = ledger(); vec = {norm(p.get("url", "")) for p in SVE}
    K = {c["norm"]: c for c in ucitaj_json(KAND, {}).get("otvoreni", [])}
    dod = []
    for x in N:
        n = norm(x["url"])
        if n in vec:
            continue
        c = K.get(n, {})
        red = dict(cc=x.get("cc", ""), medij=urlparse(x["url"]).netloc.replace("www.", ""), naslov=(x.get("naslov") or c.get("naslov") or c.get("serp_naslov") or "")[:200],
                   url=x["url"], datum=x.get("datum") or c.get("datum") or "", vrsta=x.get("vrsta", "članak"), jezik=x.get("jezik", c.get("html_lang", "")),
                   status=x.get("status") or "nađeno %s" % time.strftime("%d.%m."), link_karta=x.get("link_karta") or c.get("link_klasa") or "nije otvoreno")
        SVE.append(red); dod.append(red); vec.add(n)
    spremi_json(LEDGER_JSON, SVE)
    with io.open(LEDGER_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_POLJA, extrasaction="ignore"); w.writeheader()
        for r in SVE:
            w.writerow({k: r.get(k, "") for k in LEDGER_POLJA})
    print("dopisano %d, ukupno objava %d -> %s (+ .csv)" % (len(dod), len(SVE), LEDGER_JSON))
    for r in dod:
        print(" ", r["cc"], r["medij"], r["datum"], r["link_karta"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("fraze"); p.add_argument("--izvor", required=True, choices=["press-popis", "csv"]); p.add_argument("putanja"); p.add_argument("--val", required=True)
    p.add_argument("--kolona", default="naslov"); p.add_argument("--cc-kolona", default="cc"); p.add_argument("--lang-kolona", default="lang"); p.add_argument("--tip", default="naslov")
    p = sp.add_parser("plan"); p.add_argument("--val", required=True); p.add_argument("--od"); p.add_argument("--do", dest="do_", default=time.strftime("%Y-%m-%d")); p.add_argument("--bez-news", action="store_true")
    p = sp.add_parser("posalji"); p.add_argument("--val", required=True); p.add_argument("--strop", type=float, required=True, help="tvrdi strop u USD"); p.add_argument("--samo-proba", action="store_true", help="samo 2 upita")
    p = sp.add_parser("kupi"); p.add_argument("--minute", type=int, default=60)
    p = sp.add_parser("kandidati"); p.add_argument("--maks", type=int, default=300)
    p = sp.add_parser("zapisi"); p.add_argument("--iz", required=True)
    a = ap.parse_args()
    if requests is None:
        sys.exit("STOP: treba `pip install requests`")
    os.makedirs(OUT, exist_ok=True)
    {"fraze": cmd_fraze, "plan": cmd_plan, "posalji": cmd_posalji, "kupi": cmd_kupi, "kandidati": cmd_kandidati, "zapisi": cmd_zapisi}[a.cmd](a)


if __name__ == "__main__":
    main()
