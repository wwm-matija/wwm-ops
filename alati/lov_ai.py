#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lov_ai.py: za vinarije bez weba pitaj Google AI način za mail (DataForSEO, red). Jedan upit po vinariji.
Prije rada pročitaj upute/dataforseo.md. Radi na laptopu (ključ u C:/Users/world/wwm/.env.bevanda). U bazu ne piše ništa.

    python alati/lov_ai.py plan                    # broj upita, jezici, trošak; ništa se ne šalje
    python alati/lov_ai.py posalji --strop 32      # task_post po 100, ID-jevi odmah u out/lov/ai_taskovi.jsonl
    python alati/lov_ai.py kupi --minuta 240       # task_get po ID-ju, u krugovima, dok sve ne stigne ili istekne vrijeme
    python alati/lov_ai.py ocjena                  # otvori izvore: piše li mail na stranici uz ime i mjesto vinarije

Ulaz:  out/lov/ulaz_bez_weba.jsonl (lov_priprema.py na Hetzneru: bez maila i weba, ili samo PEC)
Izlaz: out/lov/ai_taskovi.jsonl, ai_rezultati.jsonl, ai_ocjena.jsonl, AI_MAILOVI.csv

Odluka Matije 9.11.2026. (»može, kreni«) nakon testa na 200: AI način 93 potvrđena maila, pretraga s AI odgovorom 76,
obična pretraga 32 weba. Upit: »ime mjesto email«, lokalni jezik, lokacija = država.
- AI način (serp/google/ai_mode) 0,0012 USD po upitu. Ne prima portugalski: PT i BR idu kao obična pretraga
  s load_async_ai_overview (ista cijena). Ako jezik bude odbijen (40501), upit se ponavlja na engleskom.
- U bazu smije samo mail s ocjenom POTVRĐEN + mjesto; bez PEC-a i bez domena uprave. Ostalo je za ručni pregled.
"""
import argparse, collections, csv, io, json, os, re, sys, threading, time
import concurrent.futures as cf
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import objave
import lov_web as LW
from lov_pretraga import JEZIK

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "lov")
API = "https://api.dataforseo.com/v3/"
CIJENA = 0.0012
BEZ_AI_NACINA = {"pt"}                       # jezici koje AI način odbija -> pretraga s AI odgovorom
MAIL = re.compile(r"[A-Za-z0-9][A-Za-z0-9._%+\-]{0,48}@[A-Za-z0-9][A-Za-z0-9.\-]{1,60}\.[A-Za-z]{2,12}")
UPRAVA = re.compile(r"\.gov(\.|$)|\.gv\.at$|\.gouv\.|\.gob\.|comune\.|\.comune\.|mairie|ayuntamiento|ayto\.|gemeinde|polgarmester|onkormanyzat|hivatal|\.edu(\.|$)|camcom|cciaa", re.I)
IMENIK = re.compile(r"facebook|instagram|tripadvisor|paginegialle|pagesjaunes|yelp|google\.|linkedin|youtube|wikipedia", re.I)
TP, RP, OP = (os.path.join(OUT, x) for x in ("ai_taskovi.jsonl", "ai_rezultati.jsonl", "ai_ocjena.jsonl"))


def ucitaj(p):
    out = []
    if os.path.exists(p):
        for l in io.open(p, encoding="utf-8"):
            try: out.append(json.loads(l))
            except Exception: pass
    return out


def upit(v):
    gdje = (v.get("gr") or "").strip() or (v.get("ad") or "").strip()[:80]
    return re.sub(r"\s+", " ", "%s %s email" % (v["ime"], gdje)).strip()[:180]


def slozi():
    loc = objave.lokacije(); P = []
    for v in ucitaj(os.path.join(OUT, "ulaz_bez_weba.jsonl")):
        lang = JEZIK.get(v["cc"], "en")
        P.append(dict(wwm_id=v["wwm_id"], cc=v["cc"], kw=upit(v), lang=lang, loc=loc.get(v["cc"], "United States"), metoda="aio" if lang in BEZ_AI_NACINA else "aim"))
    return P


def plan(a):
    P = slozi(); vec = {t["wwm_id"] for t in ucitaj(TP)}
    print("vinarija: %d | već poslano: %d | za slanje: %d" % (len(P), len(vec), sum(1 for p in P if p["wwm_id"] not in vec)))
    print("metoda:", dict(collections.Counter(p["metoda"] for p in P)), "| jezika %d | lokacija %d" % (len({p["lang"] for p in P}), len({p["loc"] for p in P})))
    print("jezici:", dict(collections.Counter(p["lang"] for p in P).most_common()))
    print("trošak: %d × %.4f = %.2f USD" % (len(P), CIJENA, len(P) * CIJENA))
    for p in P[:6]: print("  ", p["cc"], p["lang"], p["metoda"], "|", p["kw"])


def _post(H, metoda, pak):
    put = "serp/google/ai_mode/task_post" if metoda == "aim" else "serp/google/organic/task_post"
    tijelo = [dict(keyword=p["kw"], location_name=p["loc"], language_code=p["lang"], tag=p["wwm_id"], **({} if metoda == "aim" else dict(depth=10, load_async_ai_overview=True))) for p in pak]
    for i in range(4):
        try:
            return requests.post(API + put, headers=H, json=tijelo, timeout=120).json()
        except requests.exceptions.RequestException:
            time.sleep(10 * (i + 1))
    return {}


def posalji(a):
    P = slozi(); vec = {t["wwm_id"] for t in ucitaj(TP)}
    L = [p for p in P if p["wwm_id"] not in vec]
    if len(L) * CIJENA > a.strop: sys.exit("STOP: %d upita = %.2f USD je iznad stropa %.2f" % (len(L), len(L) * CIJENA, a.strop))
    H = objave.hdr(); po = {p["wwm_id"]: p for p in L}; n = 0; tr = 0.0; ponovi = []; greske = collections.Counter(); t0 = time.time()
    with io.open(TP, "a", encoding="utf-8") as f:
        def upisi(r, metoda):
            nonlocal n, tr
            for t in r.get("tasks") or []:
                d = t.get("data") or {}; p = po.get(d.get("tag"))
                if t.get("id") and t.get("status_code") == 20100:
                    f.write(json.dumps(dict(id=t["id"], wwm_id=d.get("tag"), metoda=metoda, kw=d.get("keyword"), lang=d.get("language_code"), cost=t.get("cost")), ensure_ascii=False) + "\n")
                    n += 1; tr += t.get("cost") or 0
                elif p and t.get("status_code") == 40501 and "language" in (t.get("status_message") or "") and p["lang"] != "en":
                    ponovi.append(dict(p, lang="en"))
                else:
                    greske["%s %s" % (t.get("status_code"), (t.get("status_message") or "")[:50])] += 1
            f.flush()
        for metoda in ("aim", "aio"):
            S = [p for p in L if p["metoda"] == metoda]
            for i in range(0, len(S), 100):
                upisi(_post(H, metoda, S[i:i + 100]), metoda)
                if (i // 100) % 20 == 0: print("%s  %s poslano %d / %d" % (time.strftime("%H:%M:%S"), metoda, n, len(L)), flush=True)
                time.sleep(0.5)
        if ponovi:
            print("ponavljam na engleskom: %d" % len(ponovi), flush=True)
            for i in range(0, len(ponovi), 100): upisi(_post(H, "aim", ponovi[i:i + 100]), "aim"); time.sleep(0.5)
    print("POSLANO: %d upita | trošak po odgovoru %.2f USD | greške: %s | %.0f s" % (n, tr, dict(greske), time.time() - t0), flush=True)


def _tekst_ai(x):
    if x.get("markdown"): return x["markdown"]
    return "\n".join(it[k] for it in (x.get("items") or []) for k in ("markdown", "text", "title") if isinstance(it.get(k), str))


def _kupi_jedan(H, t):
    put = "serp/google/ai_mode/task_get/advanced/" if t["metoda"] == "aim" else "serp/google/organic/task_get/advanced/"
    try:
        tk = (requests.get(API + put + t["id"], headers=H, timeout=60).json().get("tasks") or [{}])[0]
    except Exception:
        return None
    sc = tk.get("status_code")
    if sc != 20000:
        return None if sc in (20100, 40601, 40602, None) else dict(id=t["id"], wwm_id=t["wwm_id"], greska="%s %s" % (sc, tk.get("status_message")))
    tekst = ""; refs = []; org = []
    for res in tk.get("result") or []:
        for x in res.get("items") or []:
            if x.get("type") == "ai_overview":
                tekst += _tekst_ai(x) + "\n"
                for r in x.get("references") or []: refs.append(dict(dom=(r.get("domain") or "").lower().replace("www.", ""), url=r.get("url")))
            elif x.get("type") == "organic" and len(org) < 10:
                org.append(dict(dom=x.get("domain"), url=x.get("url"), naslov=x.get("title"), opis=x.get("description")))
    return dict(id=t["id"], wwm_id=t["wwm_id"], metoda=t["metoda"], kw=t["kw"], tekst=tekst[:3500], mailovi=sorted({e.lower().strip(".") for e in MAIL.findall(tekst)})[:8],
                linkovi=sorted(set(re.findall(r"https?://[^\s\)\]\"']+", tekst)))[:8], refs=refs[:8], org=org)


def kupi(a):
    H = objave.hdr(); t0 = time.time(); brava = threading.Lock()
    while True:
        T = ucitaj(TP); got = {r["id"] for r in ucitaj(RP)}; L = [t for t in T if t["id"] not in got]
        if not L: print("SVE POKUPLJENO: %d" % len(T), flush=True); return
        novo = 0
        with io.open(RP, "a", encoding="utf-8") as f, cf.ThreadPoolExecutor(8) as ex:
            for r in ex.map(lambda t: _kupi_jedan(H, t), L):
                if r:
                    with brava: f.write(json.dumps(r, ensure_ascii=False) + "\n"); novo += 1
        print("%s  pokupljeno novih %d | čeka %d | ukupno %d od %d" % (time.strftime("%H:%M:%S"), novo, len(L) - novo, len(got) + novo, len(T)), flush=True)
        if len(L) - novo == 0: continue
        if time.time() - t0 > a.minuta * 60: print("vrijeme isteklo, ostalo %d; pokreni kupi ponovno" % (len(L) - novo), flush=True); return
        time.sleep(60 if novo < 200 else 5)


def _provjeri(arg):
    r, v = arg
    out = dict(wwm_id=r["wwm_id"], cc=v["cc"], ime=v["ime"], gr=v.get("gr") or "", stari_mail=v.get("mail") or "", mailovi=[], refs=[x["dom"] for x in r.get("refs") or []][:4])
    mails = [e for e in r.get("mailovi") or [] if not LW.SMECE.search(e)]
    if r.get("greska"): out["ocjena"] = "greška upita"; return out
    if not mails: out["ocjena"] = "bez maila u odgovoru"; return out
    s = requests.Session(); s.headers.update({"User-Agent": LW.UA}); ciljevi = [x["url"] for x in (r.get("refs") or [])[:5] if x.get("url")]
    for e in mails:
        d = e.split("@")[-1]
        if not LW.BESPL.match(d) and not LW.PEC.search(d): ciljevi += ["https://" + d + "/", "https://" + d + "/contact", "https://" + d + "/contatti", "https://" + d + "/kontakt"]
    ciljevi += (r.get("linkovi") or [])[:4]
    vid = set(); nad = {}; tekst = ""; t0 = time.time()
    for u in ciljevi[:12]:
        if u in vid or time.time() - t0 > 60: continue
        vid.add(u); st, ku, t = LW.dohvati(s, u, rok=10)
        if not t or t.startswith("!"): continue
        tekst += " " + LW.tekst_stranice(t)[:80000]
        for e in LW.mailovi_iz(t): nad.setdefault(e, ku)
    ime = LW.ime_na(tekst, v["ime"]); g = LW.bez_naglasaka(v.get("gr") or "").strip(); mj = len(g) >= 3 and g in tekst
    for e in mails:
        d = e.split("@")[-1]
        out["mailovi"].append(dict(e=e, vrsta="pec" if LW.PEC.search(d) else "uprava" if UPRAVA.search(d) else "besplatni" if LW.BESPL.match(d) else "vlastita", na_stranici=e in nad, gdje=(nad.get(e) or "")[:120]))
    dobri = [m for m in out["mailovi"] if m["vrsta"] in ("vlastita", "besplatni")]
    kratko = len(LW.rijeci_imena(v["ime"])) == 1 and len(LW.rijeci_imena(v["ime"])[0]) <= 4
    if not dobri: out["ocjena"] = "samo PEC ili uprava"
    elif not tekst: out["ocjena"] = "izvor se ne otvara"
    elif any(m["na_stranici"] for m in dobri) and ime and mj and not kratko: out["ocjena"] = "POTVRĐEN + mjesto"
    elif any(m["na_stranici"] for m in dobri) and ime: out["ocjena"] = "potvrđen bez mjesta"
    elif any(m["na_stranici"] for m in dobri): out["ocjena"] = "mail na izvoru, ime nije"
    elif ime: out["ocjena"] = "ime na izvoru, mail nije"
    else: out["ocjena"] = "ni mail ni ime na izvoru"
    out["mail"] = next((m["e"] for m in dobri if m["na_stranici"]), dobri[0]["e"] if dobri else "")
    return out


def ocjena(a):
    V = {v["wwm_id"]: v for v in ucitaj(os.path.join(OUT, "ulaz_bez_weba.jsonl"))}
    got = {o["wwm_id"] for o in ucitaj(OP)}; L = [(r, V[r["wwm_id"]]) for r in ucitaj(RP) if r["wwm_id"] in V and r["wwm_id"] not in got]
    print("za provjeru: %d (već ocijenjeno %d)" % (len(L), len(got)), flush=True); n = 0; t0 = time.time()
    with io.open(OP, "a", encoding="utf-8") as f, cf.ThreadPoolExecutor(a.niti) as ex:
        for o in ex.map(_provjeri, L):
            f.write(json.dumps(o, ensure_ascii=False) + "\n"); n += 1
            if n % 500 == 0: f.flush(); print("%s  %d / %d (%.1f/s)" % (time.strftime("%H:%M:%S"), n, len(L), n / (time.time() - t0)), flush=True)
    A = ucitaj(OP); C = collections.Counter(o["ocjena"] for o in A)
    print("ocijenjeno: %d" % len(A))
    for k, v in C.most_common(): print("  %-34s %6d" % (k, v))
    pc = collections.Counter(o["cc"] for o in A if o["ocjena"] == "POTVRĐEN + mjesto"); print("  POTVRĐEN + mjesto po zemlji:", dict(pc.most_common(20)))
    with io.open(os.path.join(OUT, "AI_MAILOVI.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["wwm_id", "cc", "ime", "mjesto", "ocjena", "mail", "vrsta", "gdje piše", "stari mail (PEC)", "izvori"])
        for o in sorted(A, key=lambda o: (o["ocjena"] != "POTVRĐEN + mjesto", o["ocjena"], o["cc"], o["ime"])):
            if not o.get("mail"): continue
            m = next((x for x in o["mailovi"] if x["e"] == o["mail"]), {})
            w.writerow([o["wwm_id"], o["cc"], o["ime"], o["gr"], o["ocjena"], o["mail"], m.get("vrsta", ""), m.get("gdje", ""), o.get("stari_mail", ""), ", ".join(o["refs"])])
    print("popis: out/lov/AI_MAILOVI.csv")


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("plan")
    p = sp.add_parser("posalji"); p.add_argument("--strop", type=float, required=True)
    p = sp.add_parser("kupi"); p.add_argument("--minuta", type=int, default=240)
    p = sp.add_parser("ocjena"); p.add_argument("--niti", type=int, default=24)
    a = ap.parse_args(); os.makedirs(OUT, exist_ok=True)
    {"plan": plan, "posalji": posalji, "kupi": kupi, "ocjena": ocjena}[a.cmd](a)


if __name__ == "__main__":
    main()
