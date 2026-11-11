# -*- coding: utf-8 -*-
"""Temeljna baza slanja WWM-a: jedna SQLite baza u kojoj je sve što je poslano, kome, i što se dogodilo.

  py -I alati/temeljna_baza.py mailjet-povuci     Mailjet kampanje i status po poruci -> izvori/mailjet_poruke.json (samo čita)
  py -I alati/temeljna_baza.py snov-odgovori      tko je odgovorio po Snov kampanji -> izvori/snov_odgovori.json (samo čita, 1,1 s po pozivu)
  py -I alati/temeljna_baza.py gradi              složi out/temeljna/slanja.db iznova iz izvora
  py -I alati/temeljna_baza.py stanje             brojke po temi, valu, vrsti kontakta i ishodu
  py -I alati/temeljna_baza.py adresa <mail>      sve o jednoj adresi (ili domeni: adresa @domena.com)

Baza se uvijek gradi IZNOVA iz izvora (ništa se ručno ne upisuje u nju), pa je sigurno pokrenuti `gradi` kad god.
Ništa ne šalje, ne mijenja Snov ni Mailjet, ne čita sandučiće. Ključevi iz .env datoteka, nikad se ne ispisuju.

Tablice:
  kampanja   jedna kampanja u Snovu ili Mailjetu: kanal, naziv, tema, val, jezik, domena pošiljatelja, od, do, poruka
  slanje     jedan red = jedna adresa u jednoj kampanji
  ishod      što se dogodilo s adresom: odgovor, bounce, blokirano, odjava, spam, zabrana, registracija, pro, otvoreno, klik
  kontakt    svaka adresa koju znamo: vrsta (vinarija / medij / institucija / nepoznato), zemlja, naziv, wwm_id
  baza       popis baza i lista (izvor, broj redaka, broj adresa); baza_clan = koja adresa je u kojoj bazi
  objava     članci medija o karti (iz alati/objave.py)
  nas_odgovor  pojedinačni mailovi koje smo MI poslali iz sandučića (mapa Sent): sandučić, kome, kada, predmet
  ceka       adrese u nacrtima koji čekaju Matijinu riječ (Mailjet runda 3, niše, Snov GR/CY/BR)
Pošta (odgovori, automatski odgovori, bounce) dolazi iz alati/posta_popis.py, koji radi na mail poslužiteljima i ne sprema tekst.
Odgovor s druge adrese iste domene pripisuje se adresi kojoj smo pisali (izvor kaže »po domeni«); besplatne domene se ne pripisuju.
Ishod »možda micanje (ključna riječ)« NIJE zahtjev za micanje dok se poruka ne pročita: 11.11. je svih 6 provjerenih bilo lažno
(pitanja kako se prijaviti, cijena, pravne napomene u potpisu). Pravi zahtjevi idu kroz alati/sken.py i NE_KONTAKTIRATI.
  izvan_wwm  kampanje klijenata i stare probe: samo naziv i broj poruka, adrese se NE učitavaju
Teme (po nazivu kampanje): B2B (vinarije), PR (mediji), WINE_NEWS (poziv medijima na suradnju), INSTITUCIJE (WWM regije 17.9.), TEST.
Kampanja može imati dvije teme: val niša (WWM NISE 30.10. i Mailjet NISE) nosi u istom mailu poziv za Wine News i press priču,
pa je i PR i WINE_NEWS (tablica kampanja_tema). Samo poziv: WWM VINSKI 1.10., WWM AGRO / TURIZAM / POSLOVNI 2.10.
"""
import argparse, collections, csv, datetime, glob, io, json, os, re, sqlite3, sys, time

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out")
T = os.path.join(OUT, "temeljna")
IZV = os.path.join(T, "izvori")
DB = os.path.join(T, "slanja.db")
STARI = "C:/Users/world/stari_laptop_2026-11-11"
GTWT = "C:/Users/world/GTWT_baze"
MAIL = re.compile(r"^[a-z0-9][a-z0-9._%+\-]{0,63}@[a-z0-9][a-z0-9.\-]{1,60}\.[a-z]{2,12}$")
KLIJENT = re.compile(r"(?i)^(mc |bevanda|hr test bevanda|strano bevanda|sylvie|elite digital)")
STARO = re.compile(r"^(bra|Rumunjska|FIN|cz|Albania|FRA|den|esT|arme)\b")
WN = ("WWM VINSKI", "WWM TURIZAM", "WWM AGRO", "WWM POSLOVNI")
RANG = {"vinarija": 3, "institucija": 2, "medij": 1, "nepoznato": 0}
BESPL = re.compile(r"^(gmail|googlemail|yahoo|ymail|hotmail|outlook|live|icloud|aol|msn|libero|virgilio|alice|tiscali|tin|fastwebnet|inwind|"
                   r"email|orange|wanadoo|free|laposte|sfr|gmx|web|t-online|seznam|centrum|sapo|terra|uol|me|mac|mail|protonmail|proton|"
                   r"yandex|bluewin|comcast|att|bigpond|btinternet|interia|wp|onet|o2|abv|163|qq)\.", re.I)

# naziv, vrsta kontakta (ili "tabla" = čitaj iz stupca tabla), put, stupci s mailom, stupac zemlje, stupac naziva, stupac wwm_id
BAZE = [
    ("vinarije na karti (wwm.db)", "vinarija", IZV + "/vinarije.csv", ["mail"], "cc", "ime", "wwm_id"),
    ("mediji i institucije BAZA_MASTER_v6", "tabla", STARI + "/Downloads/BAZA_MASTER_v6.csv", ["email", "email2"], "iso", "domain", ""),
    ("institucije INSTITUCIJE_MASTER_v6", "institucija", STARI + "/Downloads/INSTITUCIJE_MASTER_v6.csv", ["email", "email2"], "iso", "domain", ""),
    ("institucije INSTITUCIJE_SEND_v3 (lista za slanje)", "institucija", STARI + "/Downloads/INSTITUCIJE_SEND_v3.csv", ["email"], "drzava", "domain", ""),
    ("GTWT _FINAL_v4 (mediji + institucije, 8/2026)", "tabla", GTWT + "/_FINAL_v4.csv", ["email", "email2"], "drzava", "domain", ""),
    ("GTWT sektori (institucije, 8/2026)", "institucija", GTWT + "/_SEKTORI_MASTER.csv", ["email", "email2"], "COUNTRY", "name", ""),
    ("GTWT vinski mediji (8/2026)", "medij", GTWT + "/_WINE_MASTER.csv", ["email", "email2"], "COUNTRY", "name", ""),
]
# rasporedi valova: (uzorak puta, vrsta kontakta)
RASPOREDI = [
    (STARI + "/Downloads/wwm_b2b_it_val2/RASPORED_B2B_IT_VAL2.csv", "vinarija"),
    (STARI + "/Downloads/wwm_b2b_svijet/KRUG1_RASPORED.csv", "vinarija"),
    (STARI + "/Downloads/wwm_il_kampanje/RASPORED_*.csv", "medij"),
    (STARI + "/Downloads/wwm_nove_zemlje/RASPORED_NOVE_289.csv", "medij"),
    (STARI + "/Downloads/wwm_val14/RASPORED_VAL14C2.csv", "medij"),
    (STARI + "/Downloads/wwm_vinski/RASPORED_VINSKI_0110.csv", "medij"),
    (STARI + "/Downloads/wwm_sektori/RASPORED_SEKTORI_0210.csv", "medij"),
    (STARI + "/Documents/WWM_PR_LOKVIN_2026-10-27/RASPORED_LOKVIN.csv", "medij"),
    (STARI + "/Documents/WWM_PR_NISE_2026-10-29/RASPORED_NISE.csv", "medij"),
]


def mali(s):
    return (s or "").strip().lower()


def adrese(s):
    return [a for a in (mali(x) for x in re.split(r"[;,\s]+", s or "")) if MAIL.match(a)]


def citaj_csv(put):
    with io.open(put, encoding="utf-8-sig", newline="") as f:
        prvi = f.readline(); f.seek(0)
        if prvi.startswith("\ufeff"):
            f.read(1)
        d = ";" if prvi.count(";") > prvi.count(",") else ","
        for r in csv.DictReader(f, delimiter=d):
            yield r


def tema_snov(ime):
    u = ime.upper()
    if u.startswith("TEST"):
        return "TEST"
    if KLIJENT.match(ime) or "bevanda" in ime.lower():
        return "KLIJENT"
    if STARO.match(ime):
        return "STARO"
    if u.startswith("B2B ") or u.startswith("WWM B2B"):
        return "B2B"
    if u.startswith(WN):
        return "WINE_NEWS"
    if u.startswith("WWM REGIJE"):      # val 17.9.2026.: vinske udruge, konzorciji, vinske ceste (128 od 149 adresa je iz baze institucija)
        return "INSTITUCIJE"
    if u.startswith("WWM "):
        return "PR"
    return "STARO"


def teme_snov(ime):
    """Sve teme kampanje; prva je glavna."""
    t = tema_snov(ime)
    if t == "PR" and ime.upper().startswith("WWM NISE"):
        return ["PR", "WINE_NEWS"]
    return [t]


def val_snov(ime):
    t = ime.split()
    v = " ".join(t[:2])
    return re.sub(r"\s*\d{1,2}\.\d{1,2}\.?$", "", v)


def jezik_iz(ime):
    for t in ime.replace("|", " ").split()[2:]:
        if re.fullmatch(r"[A-Za-z]{2}(-[A-Za-z]{2,4})?", t) and t.upper() not in ("EU", "AM", "AS", "AF", "OC", "V2"):
            return t.upper()
    return ""


def domena_iz(ime):
    m = re.search(r"@([\w.-]+\.[a-z]{2,})", ime)
    if m:
        return m.group(1).lower()
    m = re.search(r"\b([\w-]+)[. ](info|eu|site|space|store|online|lat|shop|org|com|click)\b", ime)
    return (m.group(1) + "." + m.group(2)).lower() if m else ""


# ---------- povlačenje (samo čitanje) ----------
def mailjet_povuci(a):
    sys.path.insert(0, os.path.join(REPO, "alati"))
    import slanje_stanje as ss
    auth = (ss.env(ss.ENV_MJ, "MAILJET_API_KEY"), ss.env(ss.ENV_MJ, "MAILJET_SECRET_KEY"))
    kamp = ss.mj(auth, "campaign", FromTS=a.od + "T00:00:00Z", Limit=500)
    rez = {}
    for k in kamp:
        naslov = ""
        if k.get("NewsLetterID"):
            d = ss.mj(auth, "campaigndraft/%s" % k["NewsLetterID"])
            naslov = (d[0].get("Title") if d else "") or ""
        por = []; off = 0
        while True:
            m = ss.mj(auth, "message", Campaign=k["ID"], ShowContactAlt="true", Limit=1000, Offset=off)
            por += [[mali(x.get("ContactAlt")), x.get("Status"), x.get("ArrivedAt")] for x in m]
            if len(m) < 1000:
                break
            off += 1000
        rez[str(k["ID"])] = dict(naslov=naslov, predmet=k.get("Subject"), od=k.get("FromEmail"), pocetak=k.get("SendStartAt"),
                                 nacrt=k.get("NewsLetterID"), poruke=por)
        print("%-10s %-44s %5d poruka  %s" % (k["ID"], naslov[:44], len(por), dict(collections.Counter(p[1] for p in por))))
    os.makedirs(IZV, exist_ok=True)
    json.dump(dict(vrijeme_utc=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"), kampanje=rez),
              io.open(IZV + "/mailjet_poruke.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("kampanja", len(rez), "poruka", sum(len(v["poruke"]) for v in rez.values()))


def snov_kampanje():
    k = {}
    p = OUT + "/snov_poslano_sve_0911.json"
    if os.path.isfile(p):
        for cid, v in json.load(io.open(p, encoding="utf-8")).items():
            k[str(cid)] = dict(ime=v.get("ime") or "", status=v.get("status"), od=v.get("od"), do=v.get("do"),
                               adrese=[mali(x) for x in v.get("adrese") or []])
    for p in sorted(glob.glob(OUT + "/slanje_stanje_*.json")):
        for v in json.load(io.open(p, encoding="utf-8")).get("snov") or []:
            if v.get("poslano_adrese") is None:
                continue
            k[str(v["kampanja"])] = dict(ime=v.get("naziv") or "", status=v.get("status"), od=v.get("od"), do=v.get("do"),
                                         adrese=[mali(x) for x in v["poslano_adrese"]])
    return k


def snov_odgovori(a):
    sys.path.insert(0, os.path.join(REPO, "alati"))
    import slanje_stanje as ss
    put = IZV + "/snov_odgovori.json"
    stanje = json.load(io.open(put, encoding="utf-8")) if os.path.isfile(put) else dict(kampanje={})
    s = ss.Snov(); kamp = snov_kampanje(); n = 0
    for cid, v in sorted(kamp.items()):
        if cid in stanje["kampanje"] or not v["adrese"] or tema_snov(v["ime"]) in ("KLIJENT", "STARO", "TEST"):
            continue
        st, r = s.get("/v1/get-emails-replies", campaignId=cid)
        if st != 200:
            print("  Snov %s: http %s, preskačem (ponovi naredbu kasnije)" % (cid, st)); continue
        lst = r if isinstance(r, list) else []
        # samo tko i kada; tekst odgovora se ne sprema
        stanje["kampanje"][cid] = [dict(email=mali(x.get("prospectEmail") or x.get("email") or x.get("userEmail") or ""),
                                       ime=x.get("prospectName") or "", datum=x.get("visitedAt") or x.get("replyDate") or "")
                                  for x in lst if isinstance(x, dict)]
        n += 1
        if n % 25 == 0:
            stanje["vrijeme_utc"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            json.dump(stanje, io.open(put, "w", encoding="utf-8"), ensure_ascii=False)
            print(n, "kampanja, odgovora dosad", sum(len(x) for x in stanje["kampanje"].values()), flush=True)
        if a.najvise and n >= a.najvise:
            break
    stanje["vrijeme_utc"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    json.dump(stanje, io.open(put, "w", encoding="utf-8"), ensure_ascii=False)
    print("gotovo: kampanja", len(stanje["kampanje"]), "odgovora", sum(len(x) for x in stanje["kampanje"].values()))


# ---------- gradnja ----------
SHEMA = """
create table kampanja(kljuc text primary key, kanal text, vanjski_id text, naziv text, tema text, val text, jezik text,
                      domena_posiljatelja text, od text, do text, poruka integer, status text);
create table kampanja_tema(kampanja text, tema text, primary key(kampanja, tema));
create table slanje(kampanja text, email text, datum text, primary key(kampanja, email));
create table ishod(email text, vrsta text, datum text, izvor text, kampanja text, napomena text);
create table kontakt(email text primary key, domena text, vrsta text, cc text, naziv text, wwm_id text);
create table baza(id integer primary key, naziv text, vrsta text, put text, redaka integer, adresa integer, mijenjano text);
create table baza_clan(baza integer, email text, primary key(baza, email));
create table objava(domena text, cc text, medij text, naslov text, url text, datum text, vrsta text);
create table izvan_wwm(kanal text, naziv text, razlog text, poruka integer, od text, do text);
create table nas_odgovor(host text, sanducic text, prema text, datum text, predmet text, u_nit integer);
create table ceka(kanal text, naziv text, tema text, email text);
create index i_ceka_email on ceka(email);
create index i_nas_prema on nas_odgovor(prema);
create table meta(kljuc text primary key, vrijednost text);
create index i_slanje_email on slanje(email);
create index i_ishod_email on ishod(email);
create index i_kontakt_dom on kontakt(domena);
create index i_kontakt_wwm on kontakt(wwm_id);
create view v_adresa as
  select k.email, k.vrsta, k.cc, k.naziv, k.wwm_id,
         (select count(*) from slanje s where s.email = k.email) as slanja,
         (select min(datum) from slanje s where s.email = k.email) as prvo,
         (select max(datum) from slanje s where s.email = k.email) as zadnje,
         (select group_concat(distinct s.tema) from v_slanje s where s.email = k.email) as teme,
         (select group_concat(distinct i.vrsta) from ishod i where i.email = k.email) as ishodi
  from kontakt k;
create view v_slanje as
  select s.email, s.datum, s.kampanja, t.tema, c.val, c.kanal, c.naziv, c.od, c.do
  from slanje s join kampanja c on c.kljuc = s.kampanja join kampanja_tema t on t.kampanja = s.kampanja;
create view v_val as
  select tema, val, kanal, count(distinct kampanja) as kampanja, count(*) as poruka, count(distinct email) as adresa,
         min(od) as od, max(do) as do
  from v_slanje group by tema, val, kanal;
"""


def gradi(a):
    os.makedirs(T, exist_ok=True)
    tmp = DB + ".novo"
    if os.path.exists(tmp):
        os.remove(tmp)
    c = sqlite3.connect(tmp); c.executescript(SHEMA)
    kont = {}

    def kontakt(email, vrsta, cc="", naziv="", wwm=""):
        x = kont.get(email)
        if x is None:
            kont[email] = [vrsta, cc or "", naziv or "", wwm or ""]
        else:
            if RANG[vrsta] > RANG[x[0]]:
                x[0] = vrsta
                if cc: x[1] = cc
                if naziv: x[2] = naziv
            x[1] = x[1] or cc or ""; x[2] = x[2] or naziv or ""; x[3] = x[3] or wwm or ""

    # baze i liste
    bid = 0
    popis = [(n, v, p, st, cc, nz, w) for (n, v, p, st, cc, nz, w) in BAZE]
    for uz, v in RASPOREDI:
        for p in sorted(glob.glob(uz)):
            if "prije" in os.path.basename(p):
                continue
            popis.append(("raspored " + os.path.basename(p)[:-4], v, p, ["email"], "", "", ""))
    for naziv, vrsta, put, stupci, s_cc, s_naz, s_w in popis:
        if not os.path.isfile(put):
            print("NEMA IZVORA:", put); continue
        bid += 1; red = 0; clan = set()
        for r in citaj_csv(put):
            red += 1
            if vrsta == "vinarija" and "na_karti" in r and str(r["na_karti"]) != "1":
                continue
            vr = vrsta if vrsta != "tabla" else ("institucija" if mali(r.get("tabla")) == "institucije" else "medij")
            cc = r.get(s_cc) or r.get("_cc") or r.get("iso") or r.get("cc") or r.get("iso_konacno") or ""
            for st in stupci:
                for m in adrese(r.get(st)):
                    clan.add(m); kontakt(m, vr, cc.strip(), (r.get(s_naz) or "").strip(), (r.get(s_w) or r.get("wwm_id") or r.get("wid") or "").strip())
        c.execute("insert into baza values(?,?,?,?,?,?,?)", (bid, naziv, vrsta, put, red, len(clan),
                  datetime.datetime.fromtimestamp(os.path.getmtime(put)).strftime("%Y-%m-%d")))
        c.executemany("insert or ignore into baza_clan values(?,?)", [(bid, m) for m in clan])

    # Snov
    for cid, v in snov_kampanje().items():
        tt = teme_snov(v["ime"]); tema = tt[0]
        if tema in ("KLIJENT", "STARO"):
            c.execute("insert into izvan_wwm values(?,?,?,?,?,?)", ("snov", v["ime"], "klijent" if tema == "KLIJENT" else "stare probe (7/2026)",
                      len(v["adrese"]), v["od"], v["do"]))
            continue
        kl = "snov:" + cid
        c.execute("insert into kampanja values(?,?,?,?,?,?,?,?,?,?,?,?)", (kl, "snov", cid, v["ime"], "+".join(tt), val_snov(v["ime"]), jezik_iz(v["ime"]),
                  domena_iz(v["ime"]), v["od"], v["do"], len(v["adrese"]), v["status"]))
        c.executemany("insert or ignore into slanje values(?,?,?)", [(kl, m, v["od"]) for m in set(v["adrese"]) if MAIL.match(m)])
        c.executemany("insert into kampanja_tema values(?,?)", [(kl, x) for x in tt])

    # Mailjet
    p = IZV + "/mailjet_poruke.json"
    mj_st = {"bounce": "bounce", "hardbounced": "bounce", "softbounced": "meki bounce", "blocked": "blokirano", "spam": "spam",
             "unsub": "odjava", "opened": "otvoreno", "clicked": "klik"}
    if os.path.isfile(p):
        for cid, v in json.load(io.open(p, encoding="utf-8"))["kampanje"].items():
            naziv = v.get("naslov") or v.get("predmet") or ""
            if not v["poruke"]:
                continue
            tt = ["PR", "WINE_NEWS"] if naziv.upper().startswith("NISE") else ["B2B"]; tema = "+".join(tt)
            kl = "mailjet:" + cid; dan = (v.get("pocetak") or "")[:10]
            c.executemany("insert into kampanja_tema values(?,?)", [(kl, x) for x in tt])
            m = re.match(r"(?:WWM|NISE)\s+(\S+)\s+(r\d)", naziv)
            c.execute("insert into kampanja values(?,?,?,?,?,?,?,?,?,?,?,?)", (kl, "mailjet", cid, naziv, tema, "Mailjet " + (m.group(2) if m else "r?"),
                      (m.group(1) if m else ""), mali(v.get("od")).split("@")[-1], dan, dan, len(v["poruke"]), "sent"))
            for em, st, kad in v["poruke"]:
                if not MAIL.match(em or ""):
                    continue
                c.execute("insert or ignore into slanje values(?,?,?)", (kl, em, (kad or dan)[:10]))
                if st in mj_st:
                    c.execute("insert into ishod values(?,?,?,?,?,?)", (em, mj_st[st], (kad or dan)[:10], "Mailjet status poruke", kl, st))
    else:
        print("NEMA IZVORA: mailjet_poruke.json (pokreni mailjet-povuci)")

    # ishodi
    p = OUT + "/NE_KONTAKTIRATI.csv"
    nk = {"rucno": "zabrana", "bounce": "bounce", "odbijanje": "odbijanje", "odjava": "odjava", "micanje": "micanje s karte"}
    if os.path.isfile(p):
        for r in citaj_csv(p):
            for m in adrese(r.get("email")):
                c.execute("insert into ishod values(?,?,?,?,?,?)", (m, nk.get(r.get("razlog"), r.get("razlog") or "zabrana"), r.get("datum") or "",
                          "NE_KONTAKTIRATI: " + (r.get("izvor") or ""), None, r.get("napomena") or ""))
    p = IZV + "/claims.csv"
    if os.path.isfile(p):
        for r in citaj_csv(p):
            if r["status"] != "verified":
                continue
            d = datetime.datetime.utcfromtimestamp(int(r["created"])).strftime("%Y-%m-%d") if (r["created"] or "").isdigit() else ""
            for m in adrese(r["email"]):
                c.execute("insert into ishod values(?,?,?,?,?,?)", (m, "registracija", d, "wwm.db claims (%s)" % r["metoda"], None, r["wwm_id"]))
                kontakt(m, "vinarija", "", r["ime"], r["wwm_id"])
    p = IZV + "/profiles.csv"
    if os.path.isfile(p):
        for r in citaj_csv(p):
            if r["tier"] == "pro":
                for m in adrese(r["owner"]):
                    c.execute("insert into ishod values(?,?,?,?,?,?)", (m, "pro", (r.get("updated") or "")[:10], "wwm.db profiles", None, r["wwm_id"]))
    p = IZV + "/snov_odgovori.json"
    if os.path.isfile(p):
        for cid, lst in json.load(io.open(p, encoding="utf-8"))["kampanje"].items():
            for x in lst:
                if MAIL.match(x.get("email") or ""):
                    c.execute("insert into ishod values(?,?,?,?,?,?)", (x["email"], "odgovor (Snov)", (x.get("datum") or "")[:10], "Snov get-emails-replies",
                              "snov:" + cid, ""))
    # pošta: odgovori, automatski odgovori, bounce, naši pojedinačni odgovori
    poslano_na = set(r[0] for r in c.execute("select distinct email from slanje"))
    po_dom = collections.defaultdict(list)
    for m in sorted(poslano_na):
        po_dom[m.split("@")[-1]].append(m)
    vr = {"odgovor": "odgovor", "auto": "auto-odgovor", "ostalo": "poruka (nije u nit)"}
    for p in sorted(glob.glob(IZV + "/posta_popis_*.json")):
        d = json.load(io.open(p, encoding="utf-8"))
        for r in d["poruke"]:
            dan = (r.get("kad") or "")[:10]; izv = "pošta %s" % r["box"]
            if r["kat"] == "poslano":
                c.execute("insert into nas_odgovor values(?,?,?,?,?,?)", (r["host"], r["box"], mali(r["prema"]), dan, r["predmet"], r.get("irt") or 0))
            elif r["kat"] == "bounce":
                if MAIL.match(r.get("odbijena") or ""):
                    c.execute("insert into ishod values(?,?,?,?,?,?)", (r["odbijena"], "bounce (pošta)", dan, izv, None, ""))
            elif r["kat"] in vr:
                m = mali(r["od"])
                if not MAIL.match(m):
                    continue
                cilj = m; dom = m.split("@")[-1]
                if m not in poslano_na and not BESPL.match(dom) and po_dom.get(dom):
                    cilj = po_dom[dom][0]; izv += " (po domeni, pisao %s)" % m
                c.execute("insert into ishod values(?,?,?,?,?,?)", (cilj, vr[r["kat"]], dan, izv, None, r["predmet"]))
                if r.get("micanje"):
                    c.execute("insert into ishod values(?,?,?,?,?,?)", (cilj, "možda micanje (ključna riječ)", dan, izv, None, r["predmet"]))
    # ponude i uplate (bez podataka o kupcu)
    w_mail = collections.defaultdict(list)
    for m, x in kont.items():
        if x[3]:
            w_mail[x[3]].append(m)
    p = IZV + "/ponude.csv"
    if os.path.isfile(p):
        for r in citaj_csv(p):
            dan = datetime.datetime.utcfromtimestamp(int(r["created"])).strftime("%Y-%m-%d") if (r["created"] or "").isdigit() else (r["created"] or "")[:10]
            for m in (adrese(r.get("racun")) or w_mail.get(r["wwm_id"], [])[:1]):
                c.execute("insert into ishod values(?,?,?,?,?,?)", (m, "ponuda Pro" if r["status"] != "paid" else "plaćeno Pro (ponuda)", dan,
                          "wwm.db ponude", None, "%s %s %s, %s" % (r["broj"], r["proizvod"], r["status"], r["wwm_id"])))
    p = IZV + "/pretplate.csv"
    if os.path.isfile(p):
        for r in citaj_csv(p):
            for m in adrese(r.get("email")):
                c.execute("insert into ishod values(?,?,?,?,?,?)", (m, "plaćeno Pro (%s)" % (r["provider"] or "pretplata"), (r.get("pocetak") or "")[:10],
                          "wwm.db pretplate", None, "%s %s, %s" % (r["tier"], r["status"], r["wwm_id"])))
    # nacrti koji čekaju
    for p in sorted(glob.glob(OUT + "/lista_*_r3*.csv")):
        if "proba" in p:
            continue
        naz = "WWM " + os.path.basename(p)[6:-4].replace("_r3", " r3").replace("_besplatni", " besplatni")
        c.executemany("insert into ceka values(?,?,?,?)", [("mailjet", naz, "B2B", m) for r in citaj_csv(p) for m in adrese(r.get("email"))])
    for p in sorted(glob.glob(OUT + "/nise_r2/liste/*.csv")):
        naz = "NISE %s r2" % os.path.basename(p)[:-4]
        c.executemany("insert into ceka values(?,?,?,?)", [("mailjet", naz, "PR+WINE_NEWS", m) for r in citaj_csv(p) for m in adrese(r.get("email"))])
    p = "C:/Users/world/Documents/WWM_REVIZIJA_2026-10-17/DANAS_1710/skripte_I/verifikacija_grbrcy_rezultat_0911.json"
    if os.path.isfile(p):
        for m, v in (json.load(io.open(p, encoding="utf-8")).get("rezultat") or {}).items():
            if isinstance(v, dict) and v.get("smtp") == "valid" and not v.get("catchall") and v.get("cc") in ("GR", "CY", "BR") and MAIL.match(mali(m)):
                c.execute("insert into ceka values(?,?,?,?)", ("snov", "B2B nacrt %s" % ("GR/CY" if v["cc"] != "BR" else "BR"), "B2B", mali(m)))

    p = OUT + "/OBJAVE_SVE.json"
    if os.path.isfile(p):
        for o in json.load(io.open(p, encoding="utf-8")):
            dom = re.sub(r"^www\.", "", re.sub(r"^https?://", "", o.get("url") or "").split("/")[0].lower())
            c.execute("insert into objava values(?,?,?,?,?,?,?)", (dom, o.get("cc"), o.get("medij"), o.get("naslov"), o.get("url"), o.get("datum"), o.get("vrsta")))

    # kontakti: sve adrese iz slanja i ishoda koje nisu ni u jednoj bazi
    for (m,) in c.execute("select distinct email from slanje union select distinct email from ishod"):
        if m and m not in kont:
            kontakt(m, "nepoznato")
    c.executemany("insert into kontakt values(?,?,?,?,?,?)", [(m, m.split("@")[-1], x[0], x[1], x[2], x[3]) for m, x in kont.items()])
    c.execute("insert into meta values('slozeno_utc', ?)", (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"),))
    c.commit(); c.execute("analyze"); c.commit(); c.close()
    if os.path.exists(DB):
        os.replace(DB, DB + ".prije")
    os.replace(tmp, DB)
    print("slozeno:", DB, "%.1f MB" % (os.path.getsize(DB) / 1e6))
    stanje(a)


def stanje(a):
    c = sqlite3.connect("file:%s?mode=ro" % DB.replace("\\", "/"), uri=True)
    q = lambda s, *p: c.execute(s, p).fetchall()
    print("\nSloženo (UTC):", q("select vrijednost from meta where kljuc='slozeno_utc'")[0][0])
    print("\n== POSLANO PO TEMI")
    print("%-12s %9s %8s %8s %8s  %s" % ("tema", "kampanja", "poruka", "adresa", "domena", "razdoblje"))
    for r in q("""select s.tema, count(distinct s.kampanja), count(*), count(distinct s.email), count(distinct k.domena), min(s.od), max(s.do)
                  from v_slanje s join kontakt k on k.email=s.email group by s.tema order by 3 desc"""):
        print("%-12s %9d %8d %8d %8d  %s do %s" % r)
    print("\n== PO VALU")
    for r in q("select tema, val, kanal, kampanja, poruka, adresa, od, do from v_val order by tema, od"):
        print("%-10s %-18s %-8s %4d kamp %6d por %6d adr  %s do %s" % r)
    print("\n== KOME (vrsta kontakta po temi, jedinstvene adrese)")
    for r in q("""select s.tema, k.vrsta, count(distinct s.email) from v_slanje s join kontakt k on k.email=s.email
                  group by s.tema, k.vrsta order by 1, 3 desc"""):
        print("%-12s %-12s %7d" % r)
    print("\n== ISHODI (jedinstvene adrese kojima je poslano u toj temi)")
    for r in q("""select s.tema, i.vrsta, count(distinct i.email) from ishod i join v_slanje s on s.email=i.email
                  group by s.tema, i.vrsta order by 1, 3 desc"""):
        print("%-12s %-18s %7d" % r)
    r = q("""select count(distinct k.wwm_id) from v_slanje s join kontakt k on k.email=s.email
             where s.tema='B2B' and k.wwm_id<>''""")[0][0]
    reg = q("""with prvo as (select k.wwm_id w, min(s.datum) d from v_slanje s join kontakt k on k.email=s.email
                             where s.tema='B2B' and k.wwm_id<>'' group by k.wwm_id)
               select count(distinct i.napomena), count(distinct case when i.datum >= p.d then i.napomena end) from ishod i join prvo p on p.w = i.napomena where i.vrsta='registracija'""")[0]
    print("\nB2B: vinarija kojima je poslano %d; od toga registriranih %s (nakon prvog maila %s)" % (r, reg[0], reg[1]))
    r = q("""select count(distinct o.domena) from objava o where o.domena in
             (select k.domena from v_slanje s join kontakt k on k.email=s.email where s.tema='PR')""")[0][0]
    print("PR: objava u popisu %d, na %d domena; od toga domena kojima smo slali PR: %d" % (q("select count(*) from objava")[0][0],
          q("select count(distinct domena) from objava")[0][0], r))
    print("\n== WINE NEWS: kome je išao poziv")
    for r in q("select val, kanal, count(distinct kampanja), count(distinct email), min(od), max(do) from v_slanje where tema='WINE_NEWS' group by val, kanal order by 5"):
        print("%-18s %-8s %4d kamp %6d adr  %s do %s" % r)
    print("ukupno različitih adresa:", q("select count(distinct email) from v_slanje where tema='WINE_NEWS'")[0][0],
          "| različitih domena:", q("select count(distinct k.domena) from v_slanje s join kontakt k on k.email=s.email where s.tema='WINE_NEWS'")[0][0])
    print("\n== ODGOVORI IZ POŠTE PO TEMI (adrese kojima smo pisali)")
    for r in q("""select s.tema, i.vrsta, count(distinct i.email), count(*) from ishod i join (select distinct email, tema from v_slanje) s on s.email=i.email
                  where i.izvor like 'pošta%' group by s.tema, i.vrsta order by 1, 3 desc"""):
        print("%-12s %-20s %6d adresa %6d poruka" % r)
    r = q("select count(*), count(distinct email) from ishod where izvor like 'pošta%' and vrsta in ('odgovor','poruka (nije u nit)') and email not in (select email from slanje)")[0]
    print("pošta od adresa kojima nismo pisali (ni po domeni): %d poruka, %d adresa" % r)
    r = q("select count(*), count(distinct prema), sum(prema in (select email from slanje)) from nas_odgovor")[0]
    print("naši pojedinačni mailovi iz sandučića: %d poruka na %d adresa (od toga na adrese iz kampanja: %s)" % r)
    print("\n== ODGOVORI BEZ NAŠEG ODGOVORA (u mapama Sent nema maila prema toj adresi ni domeni)")
    for r in q("""select s.tema, count(distinct i.email) from ishod i join (select distinct email, tema from v_slanje) s on s.email=i.email
                  where i.vrsta='odgovor' and i.izvor like 'pošta%'
                    and substr(i.email, instr(i.email,'@')+1) not in (select substr(prema, instr(prema,'@')+1) from nas_odgovor)
                  group by 1 order by 2 desc"""):
        print("%-12s %6d adresa" % r)
    print("\n== ČEKA U NACRTIMA (nije poslano)")
    for r in q("select kanal, tema, count(distinct naziv), count(distinct email), sum(email in (select email from slanje)) from ceka group by 1, 2"):
        print("%-8s %-14s %4d nacrta %6d adresa (već dobilo neki mail: %s)" % r)
    print("\n== BAZE I LISTE")
    for r in q("select naziv, vrsta, redaka, adresa, mijenjano, (select count(distinct s.email) from baza_clan b join slanje s on s.email=b.email where b.baza=baza.id) from baza order by id"):
        print("%-52s %-11s %7d red %7d adr  %s  poslano na %6d" % r)
    print("\nkontakata ukupno:", ", ".join("%s %d" % x for x in q("select vrsta, count(*) from kontakt group by vrsta order by 2 desc")))
    print("\n== IZVAN WWM-a (adrese nisu učitane)")
    for r in q("select razlog, count(*), sum(poruka), min(od), max(do) from izvan_wwm group by razlog"):
        print("%-22s %4d kampanja %6d poruka  %s do %s" % r)


def adresa(a):
    c = sqlite3.connect("file:%s?mode=ro" % DB.replace("\\", "/"), uri=True)
    x = mali(a.mail)
    uv = "k.domena = ?" if x.startswith("@") else "k.email = ?"; x = x.lstrip("@")
    for k in c.execute("select email, vrsta, cc, naziv, wwm_id from kontakt k where " + uv, (x,)).fetchall():
        print("\n%s | %s | %s | %s | %s" % k)
        for r in c.execute("select b.naziv from baza_clan bc join baza b on b.id=bc.baza where bc.email=?", (k[0],)):
            print("   u bazi:", r[0])
        for r in c.execute("select s.datum, c.tema, c.kanal, c.naziv from slanje s join kampanja c on c.kljuc=s.kampanja where s.email=? order by 1", (k[0],)):
            print("   poslano %s  %-9s %-7s %s" % r)
        for r in c.execute("select datum, vrsta, izvor, napomena from ishod where email=? order by 1", (k[0],)):
            print("   ishod   %s  %-14s %s %s" % r)
        for r in c.execute("select datum, sanducic, predmet from nas_odgovor where prema=? order by 1", (k[0],)):
            print("   mi smo pisali %s  iz %s  %s" % r)
        for r in c.execute("select kanal, naziv from ceka where email=?", (k[0],)):
            print("   čeka u nacrtu: %s %s" % r)


def main():
    p = argparse.ArgumentParser(); s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("mailjet-povuci"); x.add_argument("--od", default="2026-09-01")
    x = s.add_parser("snov-odgovori"); x.add_argument("--najvise", type=int, default=0)
    s.add_parser("gradi"); s.add_parser("stanje")
    x = s.add_parser("adresa"); x.add_argument("mail")
    a = p.parse_args()
    {"mailjet-povuci": mailjet_povuci, "snov-odgovori": snov_odgovori, "gradi": gradi, "stanje": stanje, "adresa": adresa}[a.cmd](a)


if __name__ == "__main__":
    main()
