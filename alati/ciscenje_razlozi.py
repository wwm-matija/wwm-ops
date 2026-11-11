# -*- coding: utf-8 -*-
"""Zašto neposlana vinarija s vlastitom domenom nije dobila mail, adresu po adresu.

Spaja popis skupine C iz lova (naš mail piše na webu vinarije) s datotekama
čišćenja od 4.10.2026. (CISCENJE_<CC>.csv, stupci ime_razlog, adr_razlog,
web_prov, web_razlog, salje_se) i s poznatim rezultatima Snov provjere.
Ništa ne šalje i ništa ne mijenja; piše CSV i sažetak u out/lov/.

  py -I alati/ciscenje_razlozi.py
  py -I alati/ciscenje_razlozi.py --c out/lov/c_nas_mail_na_webu.json --ciscenje <mapa wwm_b2b_svijet>

Skupine:
  PALO_4_10          bila u čišćenju 4.10., salje_se = 0
  PROSLO_NEPOSLANO   bila u čišćenju 4.10., salje_se = 1, a adresa nije kontaktirana
  NIJE_CISCENO       nije bila među kandidatima 4.10.

Stupac `zasto` kaže razlog: za PALO iz datoteke čišćenja; za PROSLO iz plana kruga 1
(KRUG1_PLAN.csv) i boje u Snovu (kand_boje_2710.json: 1 zelena, 2 žuta); za NIJE_CISCENO
iz popisa kandidata 4.10. (jedna adresa po domeni, samo obični MX ili Google) i MX zapisa
domene (out/lov/mx_nije_cisceno_<datum>.json, {domena: "mx1,mx2" | "nema MX" | "NXDOMAIN"}).
"""
import argparse, collections, csv, datetime, glob, io, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out")
ISKLJUCENE = {"DE", "AT", "CH", "LI", "HR", "SI", "RS", "BA", "ME", "MK", "XK"}
CISCENJE = r"C:\Users\world\stari_laptop_2026-11-11\Downloads\wwm_b2b_svijet"
SNOV = [
    r"C:\Users\world\Documents\WWM_REVIZIJA_2026-10-17\DANAS_1710\skripte_I\verifikacija_s_rezultat_2710.json",
    r"C:\Users\world\Documents\WWM_REVIZIJA_2026-10-17\DANAS_1710\skripte_I\verifikacija_grbrcy_rezultat_0911.json",
    os.path.join(OUT, "snov_provjera_lov1011_rezultat.json"),
]


def mali(s):
    return (s or "").strip().lower()


def skup_adresa(put, stupac=None, razdjelnik=","):
    s = set()
    if not os.path.isfile(put):
        return s
    with io.open(put, encoding="utf-8-sig", newline="") as f:
        if stupac is None:
            return set(mali(x) for x in f if x.strip())
        for r in csv.DictReader(f, delimiter=razdjelnik):
            for a in (r.get(stupac) or "").replace(",", ";").split(";"):
                if a.strip():
                    s.add(mali(a))
    return s


def snov_stanje(putovi):
    st = {}
    for p in putovi:
        if not os.path.isfile(p):
            continue
        d = json.load(io.open(p, encoding="utf-8"))
        for m, v in (d.get("rezultat") or {}).items():
            if not isinstance(v, dict) or v.get("status") != "complete":
                continue
            if v.get("smtp") == "valid" and not v.get("catchall"):
                x = "zelena"
            elif v.get("smtp") == "not_valid":
                x = "nevaljana"
            elif v.get("catchall"):
                x = "catch-all"
            else:
                x = "nepoznato"
            st[mali(m)] = x
    return st


def u_nacrtima(snov_putovi):
    """Adrese koje već čekaju u nacrtu: Mailjet liste r3 i zelene GR/CY/BR (Snov nacrti 9.11.)."""
    s = {}
    for p in glob.glob(os.path.join(OUT, "lista_*_r3*.csv")):
        for m in skup_adresa(p, "email"):
            s[m] = "Mailjet nacrt r3"
    for p in snov_putovi:
        if "grbrcy" not in os.path.basename(p) or not os.path.isfile(p):
            continue
        for m, v in (json.load(io.open(p, encoding="utf-8")).get("rezultat") or {}).items():
            if isinstance(v, dict) and v.get("smtp") == "valid" and not v.get("catchall") and v.get("cc") in ("GR", "CY", "BR"):
                s[mali(m)] = "Snov nacrt GR/CY/BR"
    return s


BOJE = "C:/Users/world/Documents/WWM_REVIZIJA_2026-10-17/DANAS_1710/skripte_I/kand_boje_2710.json"
FILTRI = ("mailspamprotection", "ppe-hosted", "pphosted", "barracuda", "hornetsecurity", "mimecast", "spamexperts",
          "sophos", "trendmicro", "vadesecure")


def mx_vrsta(v):
    if v is None:
        return ""
    if v in ("NXDOMAIN", "nema MX", "prazno") or v.startswith("greska"):
        return "bez MX"
    if "outlook.com" in v or "microsoft" in v:
        return "Microsoft 365"
    if "google" in v:
        return "Google"
    if any(f in v for f in FILTRI):
        return "filtar poste"
    return "drugi MX"


def zasto(sk, x, cc, mail, plan, boje, kdom, mx):
    if sk == "PALO_4_10":
        d = []
        if x.get("adr_razlog"): d.append("adresa: " + x["adr_razlog"])
        if x.get("ime_razlog"): d.append("ime: " + x["ime_razlog"])
        if x.get("web_prov") != "POTVRDJENO": d.append("web: " + (x.get("web_razlog") or x.get("web_prov", "")))
        return "palo 4.10. | " + " | ".join(d)
    if sk == "PROSLO_NEPOSLANO":
        if mail not in plan:
            return "nije u planu kruga 1: za zemlju nije bilo teksta"
        b = (boje.get(mail) or [None, None])[1]
        if b == 2:
            return "u planu kruga 1, u Snovu zuta (slane samo zelene)"
        if b == 1:
            return "u planu kruga 1, u Snovu zelena, nije poslano"
        if cc in ("GR", "CY", "BR"):
            return "u planu kruga 1, zemlja zaustavljena (GR/CY/BR)"
        return "u planu kruga 1, bez zapisa boje u Snovu"
    d = mail.split("@")[-1]
    if d in kdom:
        return "nije kandidat 4.10.: ista domena vec kod druge vinarije"
    return "nije kandidat 4.10.: MX domene nije obican ni Google (danas: %s)" % (mx_vrsta(mx.get(d)) or "nije provjereno")


def preporuka(sk, c, r, snov, zapreka):
    if zapreka.startswith("ceka"):
        return "CEKA: " + zapreka[5:]
    if zapreka:
        return "NE: " + zapreka
    if snov == "nevaljana":
        return "NE: Snov nevaljana"
    ime_r = (c or {}).get("ime_razlog", ""); adr_r = (c or {}).get("adr_razlog", "")
    if adr_r:
        return "RUCNO: adresa (%s)" % adr_r.split(" (")[0]
    if "nije vinarija" in ime_r:
        return "RUCNO: po imenu nije vinarija"
    if sk == "PROSLO_NEPOSLANO":
        return "VRATITI: proslo ciscenje"
    if sk == "PALO_4_10":
        if ime_r:
            return "VRATITI, IME PREGLEDATI"
        return "VRATITI: web razlog otpao"
    if r[5]:
        return "VRATITI: ime na webu"
    if r[6]:
        return "VRATITI: ime u domeni"
    return "RUCNO: ime nije potvrdjeno"


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--c", default=os.path.join(OUT, "lov", "c_nas_mail_na_webu.json"))
    a.add_argument("--ciscenje", default=CISCENJE)
    a.add_argument("--snov", nargs="*", default=SNOV)
    a.add_argument("--datum", default=datetime.date.today().isoformat())
    a = a.parse_args()

    c = json.load(io.open(a.c, encoding="utf-8"))
    cis = {}
    dat = sorted(glob.glob(os.path.join(a.ciscenje, "CISCENJE_*.csv")))
    if not dat:
        sys.exit("STOP: nema CISCENJE_*.csv u " + a.ciscenje)
    for p in dat:
        with io.open(p, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                cis[(r["wwm_id"], mali(r["email"]))] = r
    kont = skup_adresa(os.path.join(OUT, "KONTAKTIRANO_ADRESE.txt"))
    nk = skup_adresa(os.path.join(OUT, "NE_KONTAKTIRATI.csv"), "email")
    mv = skup_adresa(os.path.join(OUT, "MAIL_VAN.csv"), "mail_stari", ";")
    snov = snov_stanje(a.snov)
    nacrt = u_nacrtima(a.snov)
    plan = skup_adresa(os.path.join(a.ciscenje, "KRUG1_PLAN.csv"), "email")
    boje = {mali(k): v for k, v in json.load(io.open(BOJE, encoding="utf-8")).items()} if os.path.isfile(BOJE) else {}
    kdom = set()
    with io.open(os.path.join(a.ciscenje, "B2B_SVIJET_KANDIDATI_2026-10-04.csv"), encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            kdom.add(mali(r["email"]).split("@")[-1])
    mx = {}
    for p in sorted(glob.glob(os.path.join(OUT, "lov", "mx_nije_cisceno_*.json"))):
        mx.update(json.load(io.open(p, encoding="utf-8")))

    red = []; B = collections.OrderedDict()
    def broji(k, cc):
        B.setdefault(k, collections.Counter())[cc] += 1
    for r in c:
        w, cc, ime, mail, izvor = r[0], r[1], r[2], mali(r[3]), r[4]
        x = cis.get((w, mail))
        sk = "NIJE_CISCENO" if x is None else ("PROSLO_NEPOSLANO" if x["salje_se"] == "1" else "PALO_4_10")
        zap = ("kontaktirano" if mail in kont else "ne kontaktirati" if mail in nk else
               "MAIL_VAN" if mail in mv else "iskljucena zemlja" if cc in ISKLJUCENE else
               "ceka " + nacrt[mail] if mail in nacrt else "")
        s = snov.get(mail, "")
        pr = preporuka(sk, x, r, s, zap)
        x = x or {}
        zs = zasto(sk, x, cc, mail, plan, boje, kdom, mx)
        if pr.startswith("VRATITI") and sk == "NIJE_CISCENO" and mx_vrsta(mx.get(mail.split("@")[-1])) == "bez MX":
            pr = "NE: domena bez MX"
        broji("zasto: " + (zs.split(" | ")[0] if sk == "PALO_4_10" else zs), cc)
        red.append([w, cc, ime, mail, izvor, int(bool(r[5])), int(bool(r[6])), sk, x.get("web_prov", ""),
                    x.get("web_razlog", ""), x.get("ime_razlog", ""), x.get("adr_razlog", ""),
                    x.get("ime_novo", ""), s, zs, pr])
        broji("skupina: " + sk, cc); broji("preporuka: " + pr.split(" (")[0], cc)
        if sk == "PALO_4_10":
            raz = []
            if x.get("adr_razlog"): raz.append("adresa")
            if x.get("ime_razlog"): raz.append("ime")
            if x.get("web_prov") != "POTVRDJENO": raz.append("web " + x.get("web_prov", ""))
            broji("palo zbog: " + " + ".join(raz), cc)
        if s:
            broji("snov poznat: " + s, cc)

    mapa = os.path.join(OUT, "lov"); os.makedirs(mapa, exist_ok=True)
    izl = os.path.join(mapa, "C_RAZLOZI_%s.csv" % a.datum)
    with io.open(izl, "w", encoding="utf-8-sig", newline="") as f:
        wri = csv.writer(f, delimiter=";")
        wri.writerow(["wwm_id", "cc", "ime", "mail", "izvor", "ime_na_webu", "ime_u_domeni", "skupina", "web_prov",
                      "web_razlog", "ime_razlog", "adr_razlog", "ime_novo", "snov", "zasto", "preporuka"])
        wri.writerows(red)
    saz = dict(datum=a.datum, ukupno=len(red), ciscenje_datoteka=len(dat), ciscenje_redaka=len(cis),
               brojke={k: dict(ukupno=sum(v.values()), po_zemlji=dict(v.most_common(12))) for k, v in B.items()})
    with io.open(izl[:-4] + ".json", "w", encoding="utf-8") as f:
        json.dump(saz, f, ensure_ascii=False, indent=1)
    print("ukupno", len(red), "->", izl)
    for k in sorted(B, key=lambda k: (k.split(":")[0], -sum(B[k].values()))):
        print("%6d  %-46s %s" % (sum(B[k].values()), k, ", ".join("%s %d" % t for t in B[k].most_common(6))))


if __name__ == "__main__":
    main()
