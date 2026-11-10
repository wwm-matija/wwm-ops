# -*- coding: utf-8 -*-
"""Čišćenje liste za slanje prije Mailjeta ili Snova. SAMO ČITA ulaz, piše očišćeni CSV i izvještaj. Ništa ne šalje.

python alati/lista_ciscenje.py --ulaz out/lov/NOVI_MAILOVI_2026-11-10.csv --izlaz out/lista_IT_r3.csv --cc IT [--filtar za_slanje=da ...]
        [--sve-zemlje] [--vise-po-domeni] [--bez-kontaktirano] [--body2-jezik it]
python alati/lista_ciscenje.py --osvjezi          povuče s Hetznera out/MAIL_VAN.csv i out/KONTAKTIRANO_ADRESE.txt (ssh hetzner)

Što izbacuje (i broji u izvještaju):
  bez adrese ili neispravna; PEC/legalmail; adresa ili domena na out/NE_KONTAKTIRATI.csv; (wid, adresa) u out/MAIL_VAN.csv;
  adresa u out/KONTAKTIRANO_ADRESE.txt (već poslano ili u nacrtu); isključene zemlje DE AT CH LI HR SI RS BA ME MK XK (osim --sve-zemlje);
  dvostruka adresa; druga vinarija na istoj vlastitoj domeni (osim --vise-po-domeni; besplatne domene se ne broje).
Izlaz: stupci email, company_name, body2, wwm_id, cc (+ ostali iz ulaza). body2 = pozdravni oblik imena po jeziku
(--body2-jezik: it »di <ime>«, fr »du/de <ime>«, es/pt »de <ime>«, en/cs/sk = ime), kao u rundi 2; za ručni pregled imena vidi odluke.
Ulaz: CSV zarez ili točka-zarez, stupac mail/email, ime/company_name, wwm_id, cc.
"""
import argparse, collections, csv, io, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out")
NK = os.path.join(OUT, "NE_KONTAKTIRATI.csv"); MV = os.path.join(OUT, "MAIL_VAN.csv"); KONT = os.path.join(OUT, "KONTAKTIRANO_ADRESE.txt")
ISKLJUCENE = {"DE", "AT", "CH", "LI", "HR", "SI", "RS", "BA", "ME", "MK", "XK"}
PEC = re.compile(r"(^|[.\-@])(pec|legalmail|postecert|postacert|arubapec|pecimprese|sicurezzapostale|mypec|registerpec|gigapec|casellapec|lamiapec|pecditta|cert)([.\-]|$)", re.I)
BESPL = re.compile(r"^(gmail|googlemail|yahoo|ymail|hotmail|outlook|live|icloud|aol|msn|libero|virgilio|alice|tiscali|tin|fastwebnet|inwind|email|orange|wanadoo|free|laposte|sfr|neuf|bbox|gmx|web|t-online|freenet|seznam|centrum|volny|sapo|terra|uol|bol|telefonica|me|mac|mail|protonmail|proton|pm|yandex|bluewin|comcast|att|sbcglobal|verizon|bigpond|btinternet|shaw|telus|xtra|iinet|optusnet|skynet|telenet|hetnet|ziggo|kpn|planet|online|arcor|aon|chello|interia|wp|onet|o2|citromail|freemail|abv|163|126|qq|naver|hanmail|daum)\.", re.I)
MAIL = re.compile(r"^[a-z0-9][a-z0-9._%+\-]{0,63}@[a-z0-9][a-z0-9.\-]{1,60}\.[a-z]{2,12}$")


def citaj(put):
    t = io.open(put, encoding="utf-8-sig", newline="").read()
    prvi = t.splitlines()[0] if t else ""
    delim = ";" if prvi.count(";") > prvi.count(",") else ","
    return list(csv.DictReader(io.StringIO(t), delimiter=delim))


PRAVNI = re.compile(r"(?i)(?:^|[\s,.-])(?:s\.?r\.?l\.?s?|s\.?s\.?a?\.?|s\.?n\.?c\.?|s\.?a\.?s\.?|s\.?p\.?a\.?|s\.?c\.?a\.?r\.?l\.?|s\.?c\.?|s\.?l\.?u?\.?|s\.?a\.?u?\.?|s\.?a\.?t\.?|soc(?:\.|ieta'?|ietà)?\s+(?:semplice|agricola|agr\.|coop(?:erativa)?)(?:\s+agricola)?|"
                    r"soc\.?\s*agr\.?|societa'?\s*agricola\s*semplice|coop\.?(?:erativa)?|scea|scev|earl|gaec|sarl|sas|sca|sci|gfa|lda|ltda|l\.?t\.?d\.?a?\.?|pty\.?\s*ltd\.?|llc|l\.?l\.?c\.?|inc\.?|co\.?|corp\.?|gmbh(?:\s*&\s*co\.?\s*kg)?|"
                    r"kg|ohg|e\.?u\.?|gbr|ag|kft\.?|bt\.?|zrt\.?|s\.?r\.?o\.?|a\.?s\.?|d\.?o\.?o\.?|d\.?d\.?|eood|ood|sp\.?\s*z\s*o\.?o\.?|srl|srls|sagl|di\s+[A-Za-zÀ-ÿ' ]+\s*&\s*c\.?|&\s*c\.?|e\s+c\.?)(?=[\s,.]|$)")
MALE = {"di", "de", "del", "della", "dei", "degli", "da", "dal", "dalla", "du", "des", "le", "la", "les", "lo", "l'", "y", "e", "i", "and", "of", "the", "von", "van", "zu", "el", "al", "en", "sur", "et", "a", "au", "aux", "d'", "dell'"}
VINSKA = re.compile(r"(?i)\b(wine|wines|winery|vineyard|vineyards|cellar|cellars|estate|vino|vini|cantina|cantine|azienda|tenuta|tenute|fattoria|podere|masseria|vigna|vigne|vigneti|vignoble|domaine|ch[aâ]teau|clos|mas|cave|caves|bodega|bodegas|vi[nñ]a|vi[nñ]edo|celler|quinta|adega|weingut|winzer|weinbau|weinhof|vinarija|vinograd|pince|pinc[eé]szet|winnica|vina[řr]stv[ií]|cooperativa|coop|cantina|vignerons?|viticult\w*|vitivinic\w*)\b")


def ime_cisto(ime):
    """Ime za pozdrav: makne pravni oblik, ALL CAPS pretvori u naslovna slova, vrati (ime, treba_pregled, razlog)."""
    s = re.sub(r"\s+", " ", (ime or "").strip().strip(",;."))
    s = re.sub(r"(?i)^az\.?\s*agr\.?\s+", "Azienda Agricola ", s)
    s = re.sub(r"(?i)^soc\.?\s*agr\.?\s+", "Società Agricola ", s)
    s = re.sub(r"(?i)^(?:az\.?\s*vitivinicola|az\.?\s*vinicola)\s+", "Azienda Vitivinicola ", s)
    prije = None
    while prije != s:
        prije = s
        s = PRAVNI.sub("", s).strip(" ,.-")
        s = re.sub(r"\s*\(\s*\)\s*", " ", s).strip()
    razlog = []
    slova = [c for c in s if c.isalpha()]
    if slova and sum(c.isupper() for c in slova) / len(slova) > 0.8 and len(slova) > 3:
        rijeci = []
        for i, w in enumerate(s.split(" ")):
            wl = w.lower()
            if i and wl in MALE:
                rijeci.append(wl)
            elif re.fullmatch(r"[A-Z]{1,3}\.?", w) and i:
                rijeci.append(w)
            else:
                rijeci.append("-".join(p[:1].upper() + p[1:].lower() for p in w.split("-")))
                rijeci[-1] = "'".join(p[:1].upper() + p[1:] if k else p for k, p in enumerate(rijeci[-1].split("'"))) if "'" in rijeci[-1] else rijeci[-1]
        s = " ".join(rijeci)
        if not VINSKA.search(s) and 1 <= len(s.split()) <= 3:
            razlog.append("velika slova, možda osobno ime")
    if len(s) > 40 or len(s.split()) > 6:
        razlog.append("dugo ime")
    if not s:
        razlog.append("prazno nakon čišćenja"); s = (ime or "").strip()
    return s, bool(razlog), "; ".join(razlog)


def body2(ime, jezik):
    ime = ime.strip()
    if jezik == "it":
        return "di " + ime
    if jezik == "fr":
        n = ime.lower()
        if n.startswith(("domaine", "château", "chateau", "clos", "mas ", "vignoble")):
            return "du " + ime
        return "de " + ime
    if jezik in ("es", "pt"):
        return "de " + ime
    return ime


def osvjezi():
    for src, dst in (("/root/vino_world/out/MAIL_VAN.csv", MV), ("/mnt/HC_Volume_106719381/lov_mailova_2026-11-09/slanje_0911/KONTAKTIRANO_ADRESE.txt", KONT)):
        r = subprocess.run(["scp", "-q", "hetzner:" + src, dst]); print("scp", src, "->", dst, "ok" if r.returncode == 0 else "GREŠKA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ulaz"); ap.add_argument("--izlaz"); ap.add_argument("--cc", default="", help="zarezom odvojene zemlje; prazno = sve")
    ap.add_argument("--filtar", action="append", default=[]); ap.add_argument("--sve-zemlje", action="store_true"); ap.add_argument("--vise-po-domeni", action="store_true")
    ap.add_argument("--bez-kontaktirano", action="store_true"); ap.add_argument("--body2-jezik", default="en"); ap.add_argument("--osvjezi", action="store_true")
    ap.add_argument("--imena", default="", help="JSON {email: {ime, van, bilo}} iz ručnog ili Opus pregleda imena; van != '' = redak ispada")
    a = ap.parse_args()
    if a.osvjezi:
        osvjezi()
        if not a.ulaz:
            return
    if not (a.ulaz and a.izlaz):
        ap.error("zadaj --ulaz i --izlaz")
    R = citaj(a.ulaz)
    for f in a.filtar:
        k, v = f.split("=", 1); R = [r for r in R if (r.get(k) or "") == v]
    cc_dop = {x.strip().upper() for x in a.cc.split(",") if x.strip()}
    nk_a, nk_d = set(), set()
    for r in csv.DictReader(io.open(NK, encoding="utf-8-sig", newline="")):
        if r.get("email"):
            nk_a.add(r["email"].strip().lower())
        elif r.get("domena"):
            nk_d.add(r["domena"].strip().lower())
    mv = set()
    if os.path.exists(MV):
        for r in csv.DictReader(io.open(MV, encoding="utf-8-sig", newline=""), delimiter=";"):
            mv.add((r["wid"].strip().lower(), r["mail_stari"].strip().lower()))
    kont = set()
    if not a.bez_kontaktirano and os.path.exists(KONT):
        kont = {l.strip().lower() for l in io.open(KONT, encoding="utf-8") if l.strip() and not l.startswith("#")}
    imena = json.load(io.open(a.imena, encoding="utf-8")) if a.imena else {}
    izb = collections.Counter(); videno, dom_videno, out = set(), set(), []
    for r in R:
        e = (r.get("email") or r.get("mail") or "").strip().lower()
        wid = (r.get("wwm_id") or r.get("wid") or "").strip().lower(); cc = (r.get("cc") or "").strip().upper()
        ime = (r.get("company_name") or r.get("ime") or r.get("naziv") or "").strip()
        if cc_dop and cc not in cc_dop:
            izb["druga zemlja"] += 1; continue
        if not MAIL.match(e):
            izb["bez adrese ili neispravna"] += 1; continue
        d = e.split("@")[1]
        if PEC.search(d):
            izb["PEC"] += 1; continue
        if e in nk_a or d in nk_d:
            izb["ne kontaktirati"] += 1; continue
        if (wid, e) in mv:
            izb["MAIL_VAN"] += 1; continue
        if e in kont:
            izb["već kontaktirano ili u nacrtu"] += 1; continue
        if cc in ISKLJUCENE and not a.sve_zemlje:
            izb["isključena zemlja"] += 1; continue
        if e in videno:
            izb["dvostruka adresa"] += 1; continue
        if not a.vise_po_domeni and not BESPL.match(d) and d in dom_videno:
            izb["druga vinarija na istoj domeni"] += 1; continue
        pr = imena.get(e)
        if pr and (pr.get("van") or "").strip():
            izb["pregled imena: nije vinarija (van)"] += 1; continue
        videno.add(e); dom_videno.add(d)
        ime_c, pregled, zasto = ime_cisto(ime)
        if pr and (pr.get("ime") or "").strip():
            ime_c, pregled, zasto = pr["ime"].strip(), False, ""
            izb["ime iz pregleda"] += 1
        izb["ime za pregled"] += bool(pregled)
        red = {"email": e, "company_name": ime_c, "body2": body2(ime_c, a.body2_jezik), "wwm_id": wid, "cc": cc, "ime_izvorno": ime, "ime_pregled": zasto}
        for k, v in r.items():
            if k and k not in red and k not in ("mail", "ime", "naziv", "wid"):
                red[k] = v
        out.append(red)
    OSN = ["email", "company_name", "body2", "wwm_id", "cc", "ime_izvorno", "ime_pregled"]
    polja = OSN + [k for k in (out[0].keys() if out else []) if k not in OSN]
    with io.open(a.izlaz, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, polja, extrasaction="ignore"); w.writeheader(); w.writerows(out)
    rep = {"ulaz": a.ulaz, "redaka": len(R), "izlaz": a.izlaz, "ostaje": len(out), "izbaceno": dict(izb), "po_cc": dict(collections.Counter(r["cc"] for r in out).most_common()),
           "podloge": {"ne_kontaktirati": len(nk_a) + len(nk_d), "mail_van": len(mv), "kontaktirano": len(kont)}}
    json.dump(rep, io.open(a.izlaz + ".izvjestaj.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "po_cc"}, ensure_ascii=False, indent=1))
    print("po zemlji:", ", ".join("%s %d" % kv for kv in list(rep["po_cc"].items())[:20]))


if __name__ == "__main__":
    main()
