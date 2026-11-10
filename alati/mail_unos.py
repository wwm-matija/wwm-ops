# -*- coding: utf-8 -*-
"""Unos novih mailova vinarija iz lova (9.11.2026.) u BAZU i na LISTU ZA SLANJE. Vrti se NA HETZNERU.
Odluka vlasnika 10.11.2026.: »ulaze u oboje, da budu za stalno tu za dalje«.

python3 alati/mail_unos.py --kontekst [--niti 40]   otvori izvor svakog kandidata: vinske riječi na stranici, mail na stranici
                                      (keš <LOV>/kontekst_izvora.jsonl, nastavljiv; bez njega kandidat čeka)
python3 alati/mail_unos.py --plan     suhi prolaz: kandidati, provjere, lista; ništa se ne piše u bazu ni u ledger
python3 alati/mail_unos.py --pisi     kopije, dopis u out/DOM_ISPRAVAK.csv, UPDATE wwm.db, provjera natrag

POUKA 10.11.: »POTVRĐEN + mjesto« iz AI načina nije dovoljan za bazu. Vinarije s osobnim imenom (SCHIAVONE ANTONIO,
BARONI ALESSANDRO) pogađaju bilo koju stranicu s tim imenom u tom mjestu (sveučilište, agencija za nekretnine, bolnica).
Zato svaki izvor mora imati vinski kontekst (bar 2 vinske riječi na stranici) i mail mora pisati na njemu; adrese
ustanova (općina, sveučilište, bolnica, nekretnine, odvjetnici, crkva) ispadaju po adresi; domena imenika ili portala
(DOM_VAN ledger, ili domena koju na karti nosi 3+ vinarija) ne ide u bazu.

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
UPRAVA = re.compile(r"(^|[.@-])(pec|cert|legalmail|postacert|postecert|arubapec|pecimprese|sicurezzapostale|gov|gouv|comune|regione|provincia|municipio|ayuntamiento|mairie|ville|gemeinde|camcom)([.@-]|$)", re.I)
VINARIJE_NOVE = VW + "/out/VINARIJE_NOVE.csv"   # treći ulaz (searchdb.py ga čita umjesto tablice vinarije_nove)
DOM_VAN = VW + "/out/DOM_VAN.csv"                # ledger domena portala/platformi/agregatora maknutih s vinarija
KONTEKST = LOV + "/kontekst_izvora.jsonl"        # keš provjere izvora (--kontekst)
INSTITUCIJA = re.compile(r"(^|[.@_-])(mairie|comune|comuni|municipio|ayuntamiento|ajuntament|gemeinde|stadt|ville|ufficio|protocollo|urp|sindaco|segreteria|rathaus|prefettura|questura|"
                         r"uni|univ|unibo|unipi|unimi|unito|unifi|unina|edu|ac|scuola|school|ecole|liceo|istituto|iis|itis|ospedale|hospital|clinic|clinica|asl|ausl|ulss|sanita|sanidad|salud|"
                         r"immobiliare|immobilier|inmobiliaria|realestate|remax|bank|banca|banque|assicura|allianz|generali|avvocat|abogado|notai|notaire|commercialist|studio|"
                         r"lebenshilfe|caritas|diocesi|parrocchia|chiesa|church|kirche|pfarre|farmacia|pharmacie|apotheke|dentist|medic|dott|dr)([.@_-]|$)", re.I)
VINO = re.compile(r"\b(wine|wines|winery|wineries|winemaker\w*|vineyard|vineyards|vintner\w*|cellar|cellars|vino|vini|vinos|vinho|vinhos|vin|vins|vigna|vigne|vigneto|vigneti|vigneron\w*|vignoble\w*|"
                  r"viticol\w*|vitivinic\w*|viticult\w*|cantina|cantine|azienda agricola|enolog\w*|oenolog\w*|domaine|chateau|cave|caves|wein|weine|weingut|weingueter|weinbau|winzer\w*|"
                  r"buschenschank|heurige\w*|bodega|bodegas|vinedo|vinedos|quinta|adega|vinarija|vinograd\w*|boraszat|pince|pinceszet|szolo|winnica|wino|wina|vinarstvo|vinarstvi|vinice|"
                  r"vinohrad\w*|sarap\w*|oinopoi\w*|krasi|ampelon\w*|wijn|wijngaard|wijnhuis|grape|grapes|uva|uve|raisin|traube\w*|sekt|spumante|prosecco|champagne|cava|cru|appellation|"
                  r"doc|docg|igt|aoc|aop|igp|tenuta|tenute|fattoria|podere|masseria|clos|mas|celler|cellers|vinya|vinyes|weinkellerei|kellerei|sommelier|degustaz\w*|degustation|tasting)\b")
KONTAKTIRANO = LOV + "/slanje_0911/KONTAKTIRANO_ADRESE.txt"   # adrese kojima je već poslano ili čekaju u nacrtu (jedna po retku)
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


def kandidati():
    web, ai = web_kandidati(), ai_kandidati()
    print("kandidata: web %d, AI %d, preklop %d" % (len(web), len(ai), len(set(web) & set(ai))))
    kand = dict(ai); kand.update(web)  # web (vlastita stranica) ima prednost nad AI
    return kand


def ucitaj_kontekst():
    K = {}
    if os.path.exists(KONTEKST):
        for l in io.open(KONTEKST, encoding="utf-8"):
            try:
                z = json.loads(l); K[z["wwm_id"]] = z
            except ValueError:
                pass
    return K


def kontekst(kand, niti):
    """Otvori izvor (dokaz) svakog kandidata: http, broj vinskih riječi, je li mail na stranici (i u cf zaštiti), je li ime na njoj."""
    import concurrent.futures as cf, threading
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import requests, urllib3
    urllib3.disable_warnings()
    from lov_web import dohvati, tekst_stranice, bez_naglasaka, cf_dekod, ime_na, UA
    K = ucitaj_kontekst()
    red = [k for w, k in sorted(kand.items()) if w not in K]
    print("kontekst: u kešu %d, za otvoriti %d, niti %d" % (len(K), len(red), niti))
    brava = threading.Lock(); f = io.open(KONTEKST, "a", encoding="utf-8"); t0 = time.time(); n = [0]
    lok = threading.local()

    def ses():
        if not hasattr(lok, "s"):
            lok.s = requests.Session(); lok.s.headers.update({"User-Agent": UA, "Accept": "text/html,*/*;q=0.8", "Accept-Language": "en,it;q=0.8,fr;q=0.7,es;q=0.6,de;q=0.5"})
        return lok.s

    def jedan(k):
        url = k["dokaz"] if k["dokaz"].startswith("http") else "http://" + k["dokaz"]
        http, kraj, t = dohvati(ses(), url, rok=15)
        z = dict(wwm_id=k["wwm_id"], url=url, http=http, vino=0, mail_na=False, ime_na=False, kraj=kraj[:160])
        if http and 200 <= http < 400 and t and not t.startswith("!"):
            sirovo = t.lower()
            cfm = {cf_dekod(h).lower() for h in re.findall(r'data-cfemail="([0-9a-f]+)"', t)}
            m = k["mail"].lower()
            z["mail_na"] = (m in sirovo) or (m in cfm) or (m.replace("@", "%40") in sirovo) or (m.split("@")[0] in sirovo and m.split("@")[1] in sirovo)
            txt = tekst_stranice(t)
            z["vino"] = len(VINO.findall(txt))
            z["ime_na"] = bool(ime_na(txt, k["ime"]))
        with brava:
            f.write(json.dumps(z, ensure_ascii=False) + "\n"); n[0] += 1
            if n[0] % 200 == 0:
                f.flush(); print("  %d / %d, %.1f/s" % (n[0], len(red), n[0] / (time.time() - t0)), flush=True)
        return z

    with cf.ThreadPoolExecutor(niti) as ex:
        list(ex.map(jedan, red))
    f.close()
    K = ucitaj_kontekst()
    c = collections.Counter(("otvoren" if 200 <= (z["http"] or 0) < 400 else "ne otvara", "vino>=2" if z["vino"] >= 2 else "bez vina", "mail na" if z["mail_na"] else "mail nije") for z in K.values())
    for k, v in sorted(c.items()): print(" ", k, v)
    print("kontekst GOTOVO: %d zapisa, %.0f s" % (len(K), time.time() - t0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--pisi", action="store_true")
    ap.add_argument("--kontekst", action="store_true")
    ap.add_argument("--niti", type=int, default=40)
    a = ap.parse_args()
    if not (a.plan or a.pisi or a.kontekst):
        ap.error("zadaj --kontekst, --plan ili --pisi")
    kand = kandidati()
    if a.kontekst:
        kontekst(kand, a.niti); return
    sys.path.insert(0, VW)
    from dom_ispravak import ucitaj_dom, POLJA  # isti čitač kao searchdb.py
    KON = ucitaj_kontekst()
    web = {w for w, k in kand.items() if k["izvor"] == "web"}; ai = {w for w, k in kand.items() if k["izvor"] == "ai"}
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
    broj_dom = collections.Counter(osnova(re.sub(r"^[a-z+.\-]+://", "", (d or "").strip().lower()).split("/")[0].split(":")[0])
                                   for (d,) in con.execute("SELECT dom FROM vinarije WHERE na_karti=1 AND dom IS NOT NULL AND dom!=''"))
    dom_van = set()
    if os.path.exists(DOM_VAN):
        for r in csv.DictReader(io.open(DOM_VAN, encoding="utf-8-sig", newline=""), delimiter=";"):
            dv = (r.get("dom_stari") or r.get("dom") or r.get("dom_novi") or "").strip().lower()
            if dv:
                dom_van.add(osnova(re.sub(r"^[a-z+.\-]+://", "", dv).split("/")[0]))
    nove = {r["wid"].strip().lower() for r in csv.DictReader(io.open(VINARIJE_NOVE, encoding="utf-8-sig", newline=""), delimiter=";")
            if r.get("status") in ("approved", "pending")}
    vlasnik = {w for (w,) in con.execute("SELECT wwm_id FROM profiles WHERE owner IS NOT NULL AND owner!=''")}
    kontaktirano = set()
    if os.path.exists(KONTAKTIRANO):
        kontaktirano = {l.strip().lower() for l in io.open(KONTAKTIRANO, encoding="utf-8") if l.strip() and not l.startswith("#")}
    print("podloge: ledger %d widova, MAIL_VAN %d widova, ne kontaktirati %d adresa + %d domena, master %d, treći ulaz %d, vlasnika %d, kontaktirano %d adresa, DOM_VAN %d domena, domena s 3+ vinarija %d, kontekst %d"
          % (len(ledger), len(mv), len(nk_adr), len(nk_dom), len(master), len(nove), len(vlasnik), len(kontaktirano), len(dom_van), sum(1 for v in broj_dom.values() if v >= 3), len(KON)))
    adresa_u_bazi = collections.defaultdict(set)   # samo vinarije NA KARTI (rezani dvojnik ne brani upis)
    for w, (cc, m, nk) in ziva.items():
        if not nk:
            continue
        for x in m.split(";"):
            if x.strip():
                adresa_u_bazi[x.strip().lower()].add(w)
    broj_u_lovu = collections.Counter(k["mail"] for k in kand.values())
    # --- presuda po vinariji
    razlozi = collections.Counter(); lista = []; za_bazu = []
    for w, k in sorted(kand.items()):
        m = k["mail"]; d = dom(m); nap = []
        u_bazu = True; slanje_ok = True
        if je_pec(m):
            razlozi["ispada: PEC ili uprava"] += 1; continue
        if INSTITUCIJA.search(m):
            razlozi["ispada: adresa ustanove (općina, sveučilište, bolnica, nekretnine...)"] += 1; continue
        if osnova(d) in dom_van:
            razlozi["ispada: domena iz DOM_VAN (portal, platforma)"] += 1; continue
        if m in nk_adr or osnova(d) in nk_dom:
            razlozi["ispada: na našoj listi ne kontaktirati"] += 1; continue
        kz = KON.get(w)
        if not kz:
            u_bazu = False; slanje_ok = False; nap.append("čeka provjeru izvora (--kontekst)")
        elif not (200 <= (kz["http"] or 0) < 400):
            u_bazu = False; slanje_ok = False; nap.append("izvor se ne otvara (http %s)" % kz["http"])
        elif kz["vino"] < 2:
            u_bazu = False; slanje_ok = False; nap.append("izvor bez vinskog konteksta (%d vinskih riječi)" % kz["vino"])
        elif not kz["mail_na"]:
            u_bazu = False; slanje_ok = False; nap.append("mail ne piše na izvoru pri ponovnom otvaranju")
        if broj_dom.get(osnova(d), 0) >= 3:
            u_bazu = False; nap.append("domenu adrese nosi %d vinarija na karti (grupa ili imenik)" % broj_dom[osnova(d)])
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
        if adresa_u_bazi.get(m, set()) - {w}:
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
                   napomena="; ".join(nap), ostale=k["ostale"], _slanje_ok=slanje_ok)
        lista.append(red)
        razlozi["u bazu i na listu" if u_bazu else ("samo lista: " if slanje_ok else "ni baza ni slanje: ") + re.sub(r"\(.*\)|\d+", "N", nap[0] if nap else "")] += 1
        if u_bazu:
            za_bazu.append((w, k, mail_novi, stari))
    # --- lista za slanje: zajednička adresa samo jednom; već kontaktirana adresa ostaje na listi, ali ne ide
    videno = set(); lista_slanje = []
    for r in lista:
        if not r.pop("_slanje_ok"):
            r["za_slanje"] = "ne"
        elif r["mail"] in kontaktirano:
            r["napomena"] = (r["napomena"] + "; " if r["napomena"] else "") + "adresa već kontaktirana ili čeka u nacrtu"
            r["za_slanje"] = "ne"
        elif r["mail"] in videno:
            r["napomena"] = (r["napomena"] + "; " if r["napomena"] else "") + "adresa već na listi pod drugom vinarijom"
            r["u_bazu"] = "ne"; r["za_slanje"] = "ne"
        else:
            videno.add(r["mail"]); r["za_slanje"] = "da"
        lista_slanje.append(r)
    u_bazu_po_wid = {r["wwm_id"]: r["u_bazu"] for r in lista_slanje}
    za_bazu = [x for x in za_bazu if u_bazu_po_wid.get(x[0]) == "da"]
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
