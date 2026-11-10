# -*- coding: utf-8 -*-
"""Unos novih mailova vinarija iz lova (9.11.2026.) u BAZU i na LISTU ZA SLANJE. Vrti se NA HETZNERU.
Odluka vlasnika 10.11.2026.: »ulaze u oboje, da budu za stalno tu za dalje«.

python3 alati/mail_unos.py --plan     suhi prolaz: kandidati, provjere, lista; ništa se ne piše u bazu ni u ledger
python3 alati/mail_unos.py --pisi     kopije, dopis u out/DOM_ISPRAVAK.csv, UPDATE wwm.db, provjera natrag

ZAŠTO LEDGER, NE SAMO UPDATE: stupce dom i mail u wwm.db pri svakoj gradnji ispočetka upisuje searchdb.py
(master + treći ulaz + ledger out/DOM_ISPRAVAK.csv). Ručni UPDATE nestaje prvom gradnjom; ledger je trajna istina
(SUSTAV_RADA t.329, dom_ispravak.py). Zato svaki upis = redak u ledgeru + isti UPDATE u živoj bazi, nikad samo UPDATE.
Mail u bazi je i podloga auto-claima (app.py: adresa iz stupca mail potvrđuje claim bez ruke), pa u bazu ide samo
adresa koja je NEDVOSMISLENO te vinarije: jedna adresa na više vinarija (zadruga, grupa, agencija) ide samo na listu.

ULAZ (lov 9.11.): web_rezultat_*.jsonl (prolaz webova, lov_web.py) i ai/AI_MAILOVI.csv (Google AI način, lov_ai.py ocjena)
PRAVILO PRIHVATA: web = skupina A (bez maila) ili P (samo PEC), adresa na domeni weba (ista_domena/domena_kraja),
  ime vinarije na stranici ili u domeni; AI = ocjena »POTVRĐEN + mjesto« (adresa, ime i mjesto pišu na izvoru).
NE ULAZI U BAZU (ide na listu s oznakom ili ispada):
  PEC/uprava (pec., cert., legalmail, gov, gouv, comune, regione, provincia), naša lista ne kontaktirati (adresa ili domena),
  MAIL_VAN za taj wid, adresa koju već nosi druga vinarija u bazi, adresa na više vinarija u lovu, vinarija s vlasnikom
  profila (ima tko održava), vinarija koja već ima običan mail (netko upisao u međuvremenu), wid već u DOM_ISPRAVAK s mailom,
  wid koji nije u masteru ni u vinarije_nove (searchdb.py bi stao), vinarija koja nije na karti.
Samo PEC u bazi: novi mail se DODAJE (»pec;novi«), PEC ostaje (službena adresa, claim).
Isključene zemlje za slanje (DE AT CH LI HR SI RS BA ME MK XK): u bazu DA, na listi oznaka iskljucena_zemlja=da.

IZLAZ: <LOV>/NOVI_MAILOVI_<datum>.csv (lista za slanje; stupci wwm_id;cc;ime;mjesto;mail;vrsta;izvor;dokaz;stari_mail;
  iskljucena_zemlja;u_bazu;napomena) + <LOV>/mail_unos_<datum>.json (brojke) + kopije prije pisanja:
  /root/vino_world/arhiva/<datum>/DOM_ISPRAVAK.csv.prije-mail-unos-<ts> i <LOV>/wwm_mail_prije_<ts>.csv (wwm_id;mail zahvaćenih).
Idempotentno: wid koji je već u DOM_ISPRAVAK preskače se, pa se --pisi smije ponoviti.
"""
import argparse, collections, csv, datetime, glob, io, json, os, re, shutil, sqlite3, sys, time

sys.stdout.reconfigure(encoding="utf-8")
LOV = os.environ.get("WWM_LOV", "/mnt/HC_Volume_106719381/lov_mailova_2026-11-09")
VW = "/root/vino_world"
DOM_ISPR = VW + "/out/DOM_ISPRAVAK.csv"
MAIL_VAN = VW + "/out/MAIL_VAN.csv"
FINAL = "/mnt/wwm/predaja_vinarija_2026-08-31/KARTA_FINAL_2026-08-31.csv"
DB = "/root/wwm_api/wwm.db"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NE_KONT = os.path.join(REPO, "out", "NE_KONTAKTIRATI.csv")
ISKLJUCENE = {"DE", "AT", "CH", "LI", "HR", "SI", "RS", "BA", "ME", "MK", "XK"}
UPRAVA = re.compile(r"(^|[.@-])(pec|cert|legalmail|postacert|pecimprese|gov|gouv|comune|regione|provincia|municipio|ayuntamiento|mairie|ville|gemeinde|camcom)([.@-]|$)", re.I)
BESPL = re.compile(r"^(gmail|googlemail|yahoo|hotmail|outlook|live|icloud|aol|msn|libero|virgilio|alice|tiscali|orange|wanadoo|free|laposte|sfr|gmx|web|t-online|seznam|centrum|sapo|me|mail|protonmail|proton|yandex|bluewin|tin|inwind|email|arcor|freenet|ymail|terra|telefonica|hispavia|neuf|club-internet|bbox|numericable|iol|fastwebnet|pec)\.", re.I)
PREDNOST = ["info", "contact", "contacto", "contatti", "kontakt", "office", "mail", "hello", "hola", "ciao", "bonjour", "wine", "vino", "vin", "wein", "cantina", "weingut", "domaine", "bodega", "winery", "vendite", "sales", "shop", "ordini", "commerciale", "export"]
DANAS = datetime.date.today().isoformat()
TS = time.strftime("%Y%m%d%H%M")


def dom(a):
    return a.split("@")[-1].lower()


def osnova(d):
    d = d.lower().strip(".")
    return d[4:] if d.startswith("www.") else d


def je_pec(a):
    return bool(UPRAVA.search(dom(a))) or dom(a).startswith("pec")


def izbor(adrese):
    """Jedna adresa od više na istoj domeni: po prednosti local-parta, pa najkraća."""
    def kljuc(a):
        lp = a.split("@")[0].lower()
        for i, p in enumerate(PREDNOST):
            if lp == p or lp.startswith(p):
                return (0, i, len(a))
        return (1, 0, len(a))
    return sorted(adrese, key=kljuc)[0]


def web_kandidati():
    out = {}
    for f in sorted(glob.glob(LOV + "/web_rezultat_*.jsonl")):
        for l in io.open(f, encoding="utf-8"):
            r = json.loads(l)
            if r.get("stanje") != "ok":
                continue
            na_dom = [m for m in r.get("mailovi", []) if m["vrsta"] in ("ista_domena", "domena_kraja")]
            if not na_dom:
                continue
            for v in r["vinarije"]:
                if v["skupina"] not in ("A", "P") or not (v.get("ime_na_webu") or v.get("ime_u_domeni")):
                    continue
                adrese = sorted({m["e"].lower() for m in na_dom})
                a = izbor(adrese)
                gdje = next((m["gdje"] for m in na_dom if m["e"].lower() == a), "")
                out[v["wwm_id"]] = dict(wwm_id=v["wwm_id"], cc=v["cc"], ime=v["ime"], mjesto="", mail=a, izvor="web", dokaz=gdje,
                                        stari_mail=v.get("mail") or "", ostale=";".join(x for x in adrese if x != a))
    return out


def ai_kandidati():
    out = {}
    for r in csv.DictReader(io.open(LOV + "/ai/AI_MAILOVI.csv", encoding="utf-8-sig", newline=""), delimiter=";"):
        if r["ocjena"] != "POTVRĐEN + mjesto" or not r["mail"]:
            continue
        out[r["wwm_id"]] = dict(wwm_id=r["wwm_id"], cc=r["cc"], ime=r["ime"], mjesto=r.get("mjesto", ""), mail=r["mail"].lower().strip(),
                                izvor="ai", dokaz=r.get("gdje piše", ""), stari_mail=r.get("stari mail (PEC)", ""), ostale="")
    return out


def ucitaj_ne_kontaktirati():
    adr, domene = set(), set()
    for r in csv.DictReader(io.open(NE_KONT, encoding="utf-8-sig", newline="")):
        if r.get("email"):
            adr.add(r["email"].strip().lower())
        elif r.get("domena"):
            domene.add(osnova(r["domena"]))
    return adr, domene


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--pisi", action="store_true")
    a = ap.parse_args()
    if not (a.plan or a.pisi):
        ap.error("zadaj --plan ili --pisi")
    sys.path.insert(0, VW)
    from dom_ispravak import ucitaj_dom, POLJA  # isti čitač kao searchdb.py

    web, ai = web_kandidati(), ai_kandidati()
    print("kandidata: web %d, AI %d, preklop %d" % (len(web), len(ai), len(set(web) & set(ai))))
    kand = dict(ai); kand.update(web)  # web (vlastita stranica) ima prednost nad AI
    # --- podloge
    ledger = ucitaj_dom(obavezan=True)
    u_ledgeru = {w for w, z in ledger.items() if z["mail"]}
    mv = collections.defaultdict(set)
    for r in csv.DictReader(io.open(MAIL_VAN, encoding="utf-8-sig", newline=""), delimiter=";"):
        mv[r["wid"].strip().lower()].add(r["mail_stari"].strip().lower())
    nk_adr, nk_dom = ucitaj_ne_kontaktirati()
    master = {r["wid"].strip().lower() for r in csv.DictReader(io.open(FINAL, encoding="utf-8-sig", newline=""))}
    con = sqlite3.connect(DB, timeout=60)
    con.execute("PRAGMA busy_timeout=60000")
    ziva = {w: (cc, m or "", nk) for w, cc, m, nk in con.execute("SELECT wwm_id, cc, mail, na_karti FROM vinarije")}
    nove = {w for (w,) in con.execute("SELECT wwm_id_novi FROM vinarije_nove WHERE status IN ('approved','pending') AND wwm_id_novi IS NOT NULL")}
    vlasnik = {w for (w,) in con.execute("SELECT wwm_id FROM profiles WHERE owner IS NOT NULL AND owner!=''")}
    adresa_u_bazi = collections.defaultdict(set)
    for w, (cc, m, nk) in ziva.items():
        for x in m.split(";"):
            if x.strip():
                adresa_u_bazi[x.strip().lower()].add(w)
    broj_u_lovu = collections.Counter(k["mail"] for k in kand.values())
    # --- presuda po vinariji
    razlozi = collections.Counter(); lista = []; za_bazu = []
    for w, k in sorted(kand.items()):
        m = k["mail"]; d = dom(m); nap = []
        u_bazu = True
        if je_pec(m):
            razlozi["ispada: PEC ili uprava"] += 1; continue
        if m in nk_adr or osnova(d) in nk_dom:
            razlozi["ispada: na našoj listi ne kontaktirati"] += 1; continue
        if m in mv.get(w, ()):
            razlozi["ispada: MAIL_VAN za taj wid"] += 1; continue
        z = ziva.get(w)
        if not z or not z[2]:
            razlozi["ispada: nije na karti"] += 1; continue
        if w not in master and w not in nove:
            razlozi["ispada: wid nije u masteru ni u vinarije_nove"] += 1; continue
        if m in {x.strip().lower() for x in z[1].split(";")}:
            razlozi["ispada: baza već nosi tu adresu"] += 1; continue
        if broj_u_lovu[m] > 1:
            u_bazu = False; nap.append("ista adresa na %d vinarije u lovu" % broj_u_lovu[m])
        if adresa_u_bazi.get(m) - {w}:
            u_bazu = False; nap.append("adresu već nosi druga vinarija u bazi")
        if w in vlasnik:
            u_bazu = False; nap.append("vinarija ima vlasnika profila")
        if w in u_ledgeru:
            u_bazu = False; nap.append("wid već u DOM_ISPRAVAK (ručni redak pobjeđuje)")
        stari = z[1].strip()
        obicni = [x.strip() for x in stari.split(";") if x.strip() and not je_pec(x.strip())]
        if obicni:
            u_bazu = False; nap.append("baza već ima običan mail (%s)" % obicni[0])
        pec_stari = [x.strip() for x in stari.split(";") if x.strip() and je_pec(x.strip())]
        mail_novi = ";".join(pec_stari + [m]) if pec_stari else m
        vrsta = "besplatni" if BESPL.match(d) else "vlastita"
        red = dict(wwm_id=w, cc=k["cc"], ime=k["ime"], mjesto=k["mjesto"], mail=m, vrsta=vrsta, izvor=k["izvor"], dokaz=k["dokaz"],
                   stari_mail=stari, iskljucena_zemlja="da" if k["cc"] in ISKLJUCENE else "", u_bazu="da" if u_bazu else "ne",
                   napomena="; ".join(nap), ostale=k["ostale"])
        lista.append(red)
        razlozi["u bazu i na listu" if u_bazu else "samo lista: " + (nap[0] if nap else "")] += 1
        if u_bazu:
            za_bazu.append((w, k, mail_novi, stari))
    # --- lista za slanje: zajednička adresa samo jednom
    videno = set(); lista_slanje = []
    for r in lista:
        if r["mail"] in videno:
            r["napomena"] = (r["napomena"] + "; " if r["napomena"] else "") + "adresa već na listi pod drugom vinarijom"
            r["u_bazu"] = "ne"; r["za_slanje"] = "ne"
        else:
            videno.add(r["mail"]); r["za_slanje"] = "da"
        lista_slanje.append(r)
    polja = ["wwm_id", "cc", "ime", "mjesto", "mail", "vrsta", "izvor", "dokaz", "stari_mail", "iskljucena_zemlja", "u_bazu", "za_slanje", "napomena", "ostale"]
    put_lista = LOV + "/NOVI_MAILOVI_%s.csv" % DANAS
    with io.open(put_lista, "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, polja, delimiter=";"); wr.writeheader(); wr.writerows(lista_slanje)
    po_cc = collections.Counter(r["cc"] for r in lista_slanje if r["za_slanje"] == "da")
    brojke = {"vrijeme": time.strftime("%Y-%m-%d %H:%M"), "kandidata": {"web": len(web), "ai": len(ai), "ukupno": len(kand)},
              "presuda": dict(razlozi), "lista": len(lista_slanje), "za_slanje": sum(1 for r in lista_slanje if r["za_slanje"] == "da"),
              "za_slanje_izvan_iskljucenih": sum(1 for r in lista_slanje if r["za_slanje"] == "da" and not r["iskljucena_zemlja"]),
              "vrsta": dict(collections.Counter(r["vrsta"] for r in lista_slanje if r["za_slanje"] == "da")),
              "u_bazu": len(za_bazu), "u_bazu_pec_dodan": sum(1 for _, _, mn, _ in za_bazu if ";" in mn),
              "po_cc_za_slanje": dict(po_cc.most_common()), "lista_put": put_lista, "nacin": "pisi" if a.pisi else "plan"}
    print(json.dumps({k: v for k, v in brojke.items() if k != "po_cc_za_slanje"}, ensure_ascii=False, indent=1))
    print("po zemlji (za slanje):", ", ".join("%s %d" % kv for kv in po_cc.most_common(25)))
    if not a.pisi:
        json.dump(brojke, io.open(LOV + "/mail_unos_%s_plan.json" % DANAS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("SUHI PROLAZ, ništa nije pisano. Lista:", put_lista)
        return
    # --- PISANJE 1: ledger (kopija, dopis, provjera čitačem searchdb-a; na grešku vraćam kopiju)
    arh = VW + "/arhiva/" + DANAS; os.makedirs(arh, exist_ok=True)
    kop = arh + "/DOM_ISPRAVAK.csv.prije-mail-unos-" + TS
    shutil.copy2(DOM_ISPR, kop)
    with io.open(DOM_ISPR, "a", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, delimiter=";", lineterminator="\r\n")
        for w, k, mail_novi, stari in za_bazu:
            razlog = ("lov mailova 9.11.2026. (web vinarije: adresa na domeni weba, ime na stranici)" if k["izvor"] == "web"
                      else "lov mailova 9.11.2026. (Google AI nacin: adresa, ime i mjesto pisu na izvoru)") + \
                     ", odluka vlasnika 10.11.2026. ulaze u bazu i na listu, alat wwm-ops/alati/mail_unos.py"
            wr.writerow([w, k["ime"], "", "", stari, mail_novi, razlog, k["dokaz"].replace(";", ","), DANAS])
    try:
        novi_ledger = ucitaj_dom(obavezan=True)
        fale = [w for w, _, mn, _ in za_bazu if novi_ledger.get(w, {}).get("mail") != mn]
        if fale:
            raise ValueError("%d redaka nije u ledgeru kako treba (npr. %s)" % (len(fale), fale[:3]))
    except Exception as e:
        shutil.copy2(kop, DOM_ISPR)
        print("STOP: ledger ne prolazi čitač (%s); vraćena kopija %s, baza NIJE dirana" % (e, kop)); sys.exit(1)
    print("ledger: dopisano %d redaka, čitač prolazi (%d widova s mailom); kopija %s" % (len(za_bazu), sum(1 for z in novi_ledger.values() if z["mail"]), kop))
    # --- PISANJE 2: živa baza (kopija zahvaćenih, jedna transakcija, provjera natrag)
    kop_db = LOV + "/wwm_mail_prije_%s.csv" % TS
    with io.open(kop_db, "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, delimiter=";"); wr.writerow(["wwm_id", "mail"])
        for w, _, _, stari in za_bazu:
            wr.writerow([w, stari])
    con.execute("CREATE TEMP TABLE nov(wid TEXT PRIMARY KEY, mail TEXT)")
    con.executemany("INSERT INTO nov VALUES (?,?)", [(w, mn) for w, _, mn, _ in za_bazu])
    with con:
        con.execute("UPDATE vinarije SET mail=(SELECT mail FROM nov WHERE nov.wid=vinarije.wwm_id) WHERE wwm_id IN (SELECT wid FROM nov)")
    natrag = dict(con.execute("SELECT wwm_id, mail FROM vinarije WHERE wwm_id IN (SELECT wid FROM nov)"))
    krivo = [w for w, _, mn, _ in za_bazu if natrag.get(w) != mn]
    print("baza: UPDATE %d redaka, provjera natrag %s; kopija prije %s" % (len(za_bazu), "0 razlika" if not krivo else "%d RAZLIKA %s" % (len(krivo), krivo[:3]), kop_db))
    brojke.update({"ledger_kopija": kop, "baza_kopija": kop_db, "baza_razlika": len(krivo)})
    json.dump(brojke, io.open(LOV + "/mail_unos_%s.json" % DANAS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("GOTOVO. Lista:", put_lista)


if __name__ == "__main__":
    main()
