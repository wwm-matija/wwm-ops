#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lov_pretraga.py: za vinarije BEZ weba nađi njihov web kroz Google pretragu (DataForSEO, uvijek red, nikad live).
Radi na laptopu (ključ DATAFORSEO_B64 u C:/Users/world/wwm/.env.bevanda). Ništa ne piše u bazu.

    python alati/lov_pretraga.py plan --n 200         # uzorak + upiti + trošak; ništa se ne šalje
    python alati/lov_pretraga.py posalji --strop 1.0  # task_post, ID-jevi odmah u out/lov/pretraga_taskovi.jsonl
    python alati/lov_pretraga.py kupi                 # task_get za sve nepokupljene (smije se ponavljati)
    python alati/lov_pretraga.py ocjena               # što koja varijanta upita daje; out/lov/PRETRAGA_UZORAK.md

Ulaz: out/lov/ulaz_bez_weba.jsonl (wwm_id, cc, ime, lat, lng, gr, ad), složen na Hetzneru (lov_priprema.py).
Varijante upita (test 9.11.2026., Matija: »na više jezika, uzorak što daje, treba li dodati riječi ili adresu«):
  V1 "ime" mjesto                       lokalni jezik
  V2 ime mjesto + riječ za vinariju     lokalni jezik
  V3 ime mjesto + riječ za kontakt      lokalni jezik
  V4 ime + adresa (+ mjesto)            lokalni jezik (samo gdje adresa postoji)
  V5 ime mjesto winery                  engleski (samo zemlje gdje lokalni jezik nije engleski)
Cijena: 0,0006 USD po upitu (red, 10 rezultata). Prava cijena se čita iz odgovora (cost).
"""
import argparse, collections, io, json, os, random, re, sys, time
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import objave  # hdr(), lokacije(), reg()
from lov_web import rijeci_imena, bez_naglasaka

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "lov")
API = "https://api.dataforseo.com/v3/"
CIJENA = 0.0006
JEZIK = {"IT": "it", "FR": "fr", "US": "en", "ES": "es", "HU": "hu", "AR": "es", "DE": "de", "AT": "de", "GE": "ka", "JP": "ja", "GR": "el", "PT": "pt",
         "BR": "pt", "AU": "en", "CH": "de", "HR": "hr", "CL": "es", "ZA": "en", "CZ": "cs", "PL": "pl", "RO": "ro", "BG": "bg", "SI": "sl", "RS": "sr",
         "GB": "en", "CA": "en", "NZ": "en", "MX": "es", "UY": "es", "SK": "sk", "TR": "tr", "NL": "nl", "BE": "fr", "MD": "ro", "UA": "uk", "CN": "zh-CN"}
VINARIJA = {"it": "cantina vini", "fr": "domaine vin", "en": "winery", "es": "bodega vinos", "hu": "pincészet borászat", "de": "weingut", "ka": "ღვინის მარანი",
            "ja": "ワイナリー", "el": "οινοποιείο", "pt": "adega vinhos", "hr": "vinarija", "cs": "vinařství", "pl": "winnica", "ro": "cramă vinuri", "bg": "винарна",
            "sl": "vinarstvo", "sr": "vinarija", "sk": "vinárstvo", "tr": "şarap evi", "nl": "wijngaard", "uk": "виноробня", "zh-CN": "酒庄"}
KONTAKT = {"it": "contatti email", "fr": "contact email", "en": "contact email", "es": "contacto email", "hu": "kapcsolat email", "de": "kontakt email",
           "ka": "კონტაქტი", "ja": "お問い合わせ", "el": "επικοινωνία email", "pt": "contacto email", "hr": "kontakt email", "cs": "kontakt email",
           "pl": "kontakt email", "ro": "contact email", "bg": "контакти", "sl": "kontakt email", "sr": "kontakt email", "sk": "kontakt email",
           "tr": "iletişim", "nl": "contact email", "uk": "контакти", "zh-CN": "联系方式"}
KVOTA = {"IT": 50, "FR": 35, "US": 20, "ES": 15, "HU": 10, "AR": 8, "DE": 8, "AT": 6, "GE": 8, "JP": 8, "GR": 6, "PT": 6, "BR": 5, "AU": 5, "CH": 3, "HR": 3, "CL": 2, "ZA": 2}
IMENIK = re.compile(r"facebook|instagram|tripadvisor|paginegialle|paginebianche|pagesjaunes|yelp|vivino|wine-searcher|google\.|europages|kompass|infobel|cylex|"
                    r"registroimprese|ufficiocamerale|societe\.com|pappers|verif\.com|informazione-aziende|reportaziende|icribis|dnb\.com|opencorporates|linkedin|youtube|"
                    r"wikipedia|mapquest|yellowpages|winetourism|vinatis|tannico|twitter|x\.com|tiktok|pinterest|booking\.|airbnb|untappd|cellartracker|foursquare|"
                    r"wanderlog|waze|maps\.|apple\.com|bing\.|amazon|ebay|trovaweb|misterimprese|virgilio|tuttocitta|italiaonline|aziende\.it|guidamonaci|atoka|"
                    r"companyreports|fatturatoitalia|societe\.ninja|manageo|infogreffe|annuaire|118000|mappy|hachette-vins|vin-vigne|vitisphere|idealwine|"
                    r"einforma|axesor|empresite|infocif|paginasamarillas|cronoshare|bizapedia|manta\.com|chamberofcommerce|zoominfo|buzzfile|opengovus|"
                    r"winemag|decanter|gamberorosso|slowfood|winesofargentina|ceginformacio|nemzeticegtar|cegtalalo|opten|bisnode|firmania|quattrocalici|"
                    r"cantine\.wine|italyheritage|winerist|thewinebuyingguide|wein\.plus|falstaff|visititaly|justdial|nicelocal|restaurantguru|top-rated|cybo\.com", re.I)


def ucitaj(p):
    return [json.loads(l) for l in io.open(p, encoding="utf-8")] if os.path.exists(p) else []


def upiti_za(v):
    lang = JEZIK.get(v["cc"], "en"); ime = re.sub(r"\s+", " ", v["ime"]).strip(); gr = (v.get("gr") or "").strip(); ad = (v.get("ad") or "").strip()
    U = [("V1", '"%s" %s' % (ime, gr), lang), ("V2", "%s %s %s" % (ime, gr, VINARIJA.get(lang, "winery")), lang),
         ("V3", "%s %s %s" % (ime, gr, KONTAKT.get(lang, "contact email")), lang)]
    if ad and len(ad) > 8: U.append(("V4", "%s %s %s" % (ime, ad[:110], "" if gr.lower() in ad.lower() else gr), lang))
    if lang != "en": U.append(("V5", "%s %s winery" % (ime, gr), "en"))
    return [(k, re.sub(r"\s+", " ", q).strip()[:180], l) for k, q, l in U]


def plan(a):
    V = ucitaj(os.path.join(OUT, "ulaz_bez_weba.jsonl"))
    po = collections.defaultdict(list)
    for v in V: po[v["cc"]].append(v)
    random.seed(911); uz = []
    for cc, n in KVOTA.items():
        k = int(round(n * a.n / 200.0)); uz += random.sample(po.get(cc, []), min(k, len(po.get(cc, []))))
    loc = objave.lokacije(); P = []
    for v in uz:
        for var, q, lang in upiti_za(v):
            P.append(dict(wwm_id=v["wwm_id"], cc=v["cc"], ime=v["ime"], gr=v.get("gr") or "", ad=v.get("ad") or "", var=var, keyword=q, language_code=lang, location_name=loc.get(v["cc"], "United States")))
    objave.spremi_json(os.path.join(OUT, "pretraga_plan.json"), P)
    c = collections.Counter(p["var"] for p in P)
    print("vinarija u uzorku: %d (od %d bez weba) | s mjestom %d, s adresom %d" % (len(uz), len(V), sum(1 for v in uz if v.get("gr")), sum(1 for v in uz if v.get("ad"))))
    print("upita: %d | po varijanti: %s | različitih fraza %d | jezika %d | lokacija %d" % (len(P), dict(sorted(c.items())), len({p["keyword"] for p in P}),
          len({p["language_code"] for p in P}), len({p["location_name"] for p in P})))
    print("trošak (red, 10 rezultata): %d × %.4f = %.2f USD" % (len(P), CIJENA, len(P) * CIJENA))
    for p in P[:12]: print("  ", p["cc"], p["var"], p["language_code"], "|", p["keyword"])


def posalji(a):
    P = objave.ucitaj_json(os.path.join(OUT, "pretraga_plan.json"), [])
    tp = os.path.join(OUT, "pretraga_taskovi.jsonl")
    vec = {(t["wwm_id"], t["var"]) for t in ucitaj(tp)}
    lista = [p for p in P if (p["wwm_id"], p["var"]) not in vec]
    if len(lista) * CIJENA > a.strop: sys.exit("STOP: %d upita = %.2f USD je iznad stropa %.2f" % (len(lista), len(lista) * CIJENA, a.strop))
    H = objave.hdr(); trosak = 0.0; n = 0
    with io.open(tp, "a", encoding="utf-8") as f:
        for i in range(0, len(lista), 100):
            pak = lista[i:i + 100]
            payload = [dict(keyword=p["keyword"], location_name=p["location_name"], language_code=p["language_code"], depth=10, tag="%s|%s" % (p["wwm_id"], p["var"])) for p in pak]
            r = requests.post(API + "serp/google/organic/task_post", headers=H, json=payload, timeout=120).json()
            for tk in r.get("tasks") or []:
                d = tk.get("data") or {}; wid, var = (d.get("tag") or "|").split("|")[:2]
                if tk.get("id") and tk.get("status_code") in (20100, 20000):
                    f.write(json.dumps(dict(id=tk["id"], wwm_id=wid, var=var, kw=d.get("keyword"), cost=tk.get("cost")), ensure_ascii=False) + "\n"); n += 1; trosak += tk.get("cost") or 0
                else:
                    print("  GREŠKA", tk.get("status_code"), tk.get("status_message"), d.get("keyword"))
            f.flush(); time.sleep(1)
    print("poslano upita: %d | trošak po odgovoru: %.4f USD" % (n, trosak))


def kupi(a):
    T = ucitaj(os.path.join(OUT, "pretraga_taskovi.jsonl")); rp = os.path.join(OUT, "pretraga_rezultati.json")
    R = objave.ucitaj_json(rp, {}); H = objave.hdr(); novo = 0; ceka = 0
    for t in T:
        if t["id"] in R: continue
        g = requests.get(API + "serp/google/organic/task_get/regular/%s" % t["id"], headers=H, timeout=60).json()
        tk = (g.get("tasks") or [{}])[0]
        if tk.get("status_code") == 20000:
            items = [dict(pos=x.get("rank_absolute"), dom=x.get("domain"), url=x.get("url"), naslov=x.get("title"), opis=x.get("description"))
                     for res in (tk.get("result") or []) for x in (res.get("items") or []) if x.get("type") == "organic"]
            R[t["id"]] = dict(wwm_id=t["wwm_id"], var=t["var"], kw=t["kw"], items=items); novo += 1
        else:
            ceka += 1
        if novo % 100 == 0 and novo: objave.spremi_json(rp, R)
    objave.spremi_json(rp, R)
    print("pokupljeno novih %d | još čeka %d | ukupno %d od %d" % (novo, ceka, len(R), len(T)))


def kandidat(v, items):
    """Vrati (domena, razlog, pozicija) prvog rezultata koji izgleda kao vlastiti web vinarije, ili None."""
    r = rijeci_imena(v["ime"])
    if not r: return None
    for x in items:
        d = (x.get("dom") or "").lower().replace("www.", "")
        if not d or IMENIK.search(d): continue
        dn = re.sub(r"[^a-z0-9]", "", bez_naglasaka(objave.reg(d).split(".")[0]))
        nas = bez_naglasaka((x.get("naslov") or ""))
        u_dom = [w for w in r if len(w) >= 4 and w in dn]
        u_nas = [w for w in r if re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", nas)]
        if u_dom and (len(r) == 1 or len(u_nas) >= 1 or len(u_dom) >= 2): return d, "ime u domeni", x.get("pos")
        if len(u_nas) >= (1 if len(r) == 1 else 2) and x.get("pos", 99) <= 3 and len(d.split(".")[0]) > 3 and not re.search(r"blog|news|giornale|journal|wiki|shop|store|market|guide|guida", d):
            return d, "ime u naslovu (vrh)", x.get("pos")
    return None


def ocjena(a):
    P = objave.ucitaj_json(os.path.join(OUT, "pretraga_plan.json"), []); R = objave.ucitaj_json(os.path.join(OUT, "pretraga_rezultati.json"), {})
    V = {}
    for p in P: V.setdefault(p["wwm_id"], p)
    po = collections.defaultdict(dict)
    for r in R.values(): po[r["wwm_id"]][r["var"]] = r
    MAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
    S = collections.defaultdict(collections.Counter); red = []; kand = {}
    for wid, vr in po.items():
        v = V[wid]; nadeno = {}; fb = False; mail_u_opisu = set()
        for var, r in sorted(vr.items()):
            S[var]["upita"] += 1
            k = kandidat(v, r["items"])
            if k: S[var]["kandidat za vlastiti web"] += 1; nadeno[var] = k
            if not r["items"]: S[var]["bez rezultata"] += 1
            if any(re.search(r"facebook|instagram", x.get("dom") or "") and any(w in bez_naglasaka(x.get("naslov") or "") for w in rijeci_imena(v["ime"])) for x in r["items"]):
                S[var]["Facebook/Instagram s imenom"] += 1; fb = True
            for x in r["items"]:
                for e in MAIL.findall((x.get("opis") or "")): mail_u_opisu.add(e.lower())
            if any(MAIL.search(x.get("opis") or "") for x in r["items"]): S[var]["mail u isječku"] += 1
        S["BILO KOJA"]["upita"] += 1
        if nadeno: S["BILO KOJA"]["kandidat za vlastiti web"] += 1; kand[wid] = collections.Counter(k[0] for k in nadeno.values()).most_common(1)[0][0]
        if fb: S["BILO KOJA"]["Facebook/Instagram s imenom"] += 1
        if mail_u_opisu: S["BILO KOJA"]["mail u isječku"] += 1
        if not nadeno and not fb: S["BILO KOJA"]["ništa (ni web ni mreža)"] += 1
        S["cc " + v["cc"]]["upita"] += 1
        if nadeno: S["cc " + v["cc"]]["kandidat za vlastiti web"] += 1
        red.append((v, nadeno, fb, sorted(mail_u_opisu)[:3], vr))
    print("vinarija s rezultatima: %d" % len(po))
    for k in ["V1", "V2", "V3", "V4", "V5", "BILO KOJA"]:
        s = S[k]; n = s["upita"] or 1
        print("  %-10s upita %4d | vlastiti web %4d (%2d %%) | FB/IG %4d | mail u isječku %4d | bez rezultata %3d | ništa %s" % (
            k, s["upita"], s["kandidat za vlastiti web"], 100 * s["kandidat za vlastiti web"] / n, s["Facebook/Instagram s imenom"], s["mail u isječku"], s["bez rezultata"], s.get("ništa (ni web ni mreža)", "")))
    print("  po zemlji (vinarija / s kandidatom):", ", ".join("%s %d/%d" % (k[3:], S[k]["kandidat za vlastiti web"], S[k]["upita"]) for k in sorted(S) if k.startswith("cc ")))
    # koja varijanta jedina nađe
    jed = collections.Counter()
    for v, nadeno, fb, m, vr in red:
        if len(nadeno) == 1: jed[list(nadeno)[0]] += 1
    print("  kandidat nađen SAMO jednom varijantom:", dict(jed))
    M = ["# Lov kroz pretragu: uzorak %d vinarija bez weba (9.11.2026.)\n" % len(red), "| zemlja | vinarija | mjesto | kandidat (varijanta, pozicija) | FB/IG | mail u isječku |", "|---|---|---|---|---|---|"]
    for v, nadeno, fb, m, vr in sorted(red, key=lambda x: (x[0]["cc"], x[0]["ime"])):
        M.append("| %s | %s | %s | %s | %s | %s |" % (v["cc"], v["ime"][:44].replace("|", "/"), (v["gr"] or "")[:24], "; ".join("%s (%s, %s)" % (k[0], var, k[2]) for var, k in sorted(nadeno.items())) or "", "da" if fb else "", ", ".join(m)))
    io.open(os.path.join(OUT, "PRETRAGA_UZORAK.md"), "w", encoding="utf-8", newline="\n").write("\n".join(M) + "\n")
    objave.spremi_json(os.path.join(OUT, "pretraga_kandidati.json"), [dict(dom=d, vinarije=[dict(wwm_id=w, cc=V[w]["cc"], ime=V[w]["ime"], skupina="S", mail="", gr=V[w]["gr"])]) for w, d in kand.items()])
    print("uzorak: out/lov/PRETRAGA_UZORAK.md | kandidata za provjeru kroz lov_web: %d" % len(kand))


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("plan"); p.add_argument("--n", type=int, default=200)
    p = sp.add_parser("posalji"); p.add_argument("--strop", type=float, default=1.0)
    sp.add_parser("kupi"); sp.add_parser("ocjena")
    a = ap.parse_args(); os.makedirs(OUT, exist_ok=True)
    {"plan": plan, "posalji": posalji, "kupi": kupi, "ocjena": ocjena}[a.cmd](a)


if __name__ == "__main__":
    main()
