# -*- coding: utf-8 -*-
"""Mailjet runda (vinarije ili mediji): lista, nacrt, probni, stanje, slanje. Vrti se na laptopu (ključevi u .env.mailjet).
NIŠTA SE NE ŠALJE bez naredbe `salji` s `--odobrio "<Matijina riječ doslovno>"`.

python alati/mailjet_runda.py stanje                                   nacrti (status 0 = nacrt, 2 = poslano) i liste s brojem kontakata
python alati/mailjet_runda.py lista  --ime "WWM IT r3" --csv out/lista_IT_r3.csv
        CSV (zarez ili točka-zarez): stupac email (ili mail), company_name, body2 [i druga svojstva]. Prije uvoza: adrese s
        out/NE_KONTAKTIRATI.csv (adresa ili domena) i iz --kontaktirano (zadano out/KONTAKTIRANO_ADRESE.txt) se IZBACUJU i broje;
        dvostruke adrese jednom. Uvoz addforce, čeka se job, ispiše broj na listi.
python alati/mailjet_runda.py nacrt  --ime "WWM IT r3" --naslov "WWM IT r3 (PR Voice Global)" --locale it_IT \
        --predmet tekstovi/mailjet/predmet_IT.txt --tijelo tekstovi/mailjet/tijelo_IT.txt
        Tijelo = čisti tekst s [[data:company_name:""]], [[data:body2:""]] i [[UNSUB_LINK_XX]]; HTML se složi sam (isti izgled kao r2).
        Brave: u tekstu nema worldwinerymap.com, dugih crtica ni »100,000«; varijable samo one koje lista nosi.
python alati/mailjet_runda.py probni --naslov "WWM IT r3 (PR Voice Global)" --na desk@worldwinerymap.org
        Probni mail s poljima prvog stvarnog kontakta liste (campaigndraft/{id}/test). Kampanja se NE šalje.
python alati/mailjet_runda.py salji  --naslov "WWM IT r3 (PR Voice Global)" --odobrio "Matija 10.11.: šalji IT r3"
        Provjere (nacrt status 0, lista nije prazna, sadržaj ima tekst), pa campaigndraft/{id}/send; zapis u out/MAILJET_POSLANO.csv.
python alati/mailjet_runda.py makni  --ime "WWM IT r3" --adrese out/makni.txt      skida adrese (jedna po retku) s liste

Stanje (lista_id, nacrt_id po naslovu): out/mailjet_runda_stanje.json. Ključevi se nikad ne ispisuju.
Pošiljatelj zadano contact@prvoiceglobal.com »PR Voice Global« (--posiljatelj, --ime-posiljatelja za drugo).
"""
import argparse, csv, datetime, io, json, os, re, sys, time
import requests

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out")
ENV_MJ = os.environ.get("WWM_ENV_MAILJET", "C:/Users/world/wwm/.env.mailjet")
API = "https://api.mailjet.com/v3/REST/"
STANJE = os.path.join(OUT, "mailjet_runda_stanje.json")
NK = os.path.join(OUT, "NE_KONTAKTIRATI.csv")
KONT = os.path.join(OUT, "KONTAKTIRANO_ADRESE.txt")
POSLANO = os.path.join(OUT, "MAILJET_POSLANO.csv")
ZABRANE = ("worldwinerymap.com", "\u2014", "\u2013", "100,000", "100.000")


def env(var):
    for l in io.open(ENV_MJ, encoding="utf-8"):
        if l.startswith(var + "="):
            return l.split("=", 1)[1].strip().strip('"')
    raise SystemExit("nema %s u %s" % (var, ENV_MJ))


AUTH = None


def api(m, put, **k):
    global AUTH
    if AUTH is None:
        AUTH = (env("MAILJET_API_KEY"), env("MAILJET_SECRET_KEY"))
    for pok in range(3):
        try:
            r = requests.request(m, API + put, auth=AUTH, timeout=120, **k)
            try:
                j = r.json()
            except ValueError:
                j = {"_text": r.text[:300]}
            return r.status_code, j
        except requests.RequestException as e:
            if m != "GET" and pok:
                raise
            time.sleep(5)
    return 0, {}


def data(j):
    return (j or {}).get("Data") or []


def ucitaj_stanje():
    return json.load(io.open(STANJE, encoding="utf-8")) if os.path.exists(STANJE) else {}


def spremi_stanje(S):
    os.makedirs(OUT, exist_ok=True)
    json.dump(S, io.open(STANJE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def upisi(grupa, kljuc, vr):
    """Upis jednog ključa uz ponovno čitanje datoteke (dva alata smiju pisati naizmjence, nijedan ne smije pregaziti drugoga)."""
    S = ucitaj_stanje(); S.setdefault(grupa, {})[kljuc] = vr; spremi_stanje(S)


def citaj_csv(put):
    t = io.open(put, encoding="utf-8-sig", newline="").read()
    delim = ";" if t.splitlines()[0].count(";") > t.splitlines()[0].count(",") else ","
    R = list(csv.DictReader(io.StringIO(t), delimiter=delim))
    for r in R:
        if "email" not in r and "mail" in r:
            r["email"] = r["mail"]
    return R


def ne_kontaktirati():
    adr, dom = set(), set()
    if os.path.exists(NK):
        for r in csv.DictReader(io.open(NK, encoding="utf-8-sig", newline="")):
            if r.get("email"):
                adr.add(r["email"].strip().lower())
            elif r.get("domena"):
                dom.add(r["domena"].strip().lower())
    return adr, dom


def lista_id(ime):
    s, j = api("GET", "contactslist", params={"Limit": 500})
    for x in data(j):
        if x["Name"] == ime and not x.get("IsDeleted"):
            return x["ID"], x.get("SubscriberCount")
    return None, None


def cmd_stanje(a):
    s, j = api("GET", "campaigndraft", params={"Limit": 100})
    if s != 200:
        print("campaigndraft:", s, str(j)[:200])
    print("NACRTI (status 0 nacrt, 1 programiran, 2 poslano, -1 arhiviran):")
    for d in sorted(data(j), key=lambda x: x.get("CreatedAt", ""), reverse=True)[:40]:
        print("  %-10s st %2s  lista %-10s %s | %s" % (d["ID"], d.get("Status"), d.get("ContactsListID"), d.get("Title", "")[:40], d.get("CreatedAt", "")[:16]))
    s, j = api("GET", "contactslist", params={"Limit": 500})
    print("LISTE:")
    for x in sorted(data(j), key=lambda x: x.get("CreatedAt", ""), reverse=True)[:40]:
        if not x.get("IsDeleted"):
            print("  %-10s %-30s kontakata %s" % (x["ID"], x["Name"][:30], x.get("SubscriberCount")))


def cmd_lista(a):
    R = citaj_csv(a.csv)
    nk_a, nk_d = ne_kontaktirati()
    kont = set()
    if a.kontaktirano and os.path.exists(a.kontaktirano):
        kont = {l.strip().lower() for l in io.open(a.kontaktirano, encoding="utf-8") if l.strip() and not l.startswith("#")}
    videno, kontakti, izb = set(), [], {"ne kontaktirati": 0, "već kontaktirano": 0, "dvostruko": 0, "bez adrese": 0}
    svojstva = [k for k in R[0].keys() if k not in ("email", "mail") and k]
    for r in R:
        e = (r.get("email") or "").strip().lower()
        if not e or "@" not in e:
            izb["bez adrese"] += 1; continue
        if e in nk_a or e.split("@")[1] in nk_d:
            izb["ne kontaktirati"] += 1; continue
        if e in kont:
            izb["već kontaktirano"] += 1; continue
        if e in videno:
            izb["dvostruko"] += 1; continue
        videno.add(e)
        kontakti.append({"Email": e, "Name": (r.get("company_name") or "")[:255], "Properties": {k: (r.get(k) or "") for k in svojstva}})
    print("CSV %d redaka -> %d kontakata; izbačeno %s; svojstva %s" % (len(R), len(kontakti), izb, svojstva))
    if not kontakti:
        raise SystemExit("prazna lista, ništa nije stvoreno")
    s, j = api("GET", "contactmetadata", params={"Limit": 200}); ima = {x["Name"] for x in data(j)}
    for p in svojstva:
        if p not in ima:
            s, j = api("POST", "contactmetadata", json={"Datatype": "str", "Name": p, "NameSpace": "static"}); print("svojstvo", p, s)
    lid, n = lista_id(a.ime)
    if not lid:
        s, j = api("POST", "contactslist", json={"Name": a.ime}); lid = data(j)[0]["ID"]; print("lista stvorena", lid)
    else:
        print("lista postoji", lid, "kontakata", n)
    for i in range(0, len(kontakti), 1000):
        s, j = api("POST", "contactslist/%s/managemanycontacts" % lid, json={"Action": "addforce", "Contacts": kontakti[i:i + 1000]})
        job = data(j)[0]["JobID"] if s < 300 else None
        print("uvoz %d..%d: %s job %s" % (i, i + len(kontakti[i:i + 1000]), s, job))
        if not job:
            raise SystemExit("uvoz nije prihvaćen: %s" % str(j)[:200])
        for cek in range(90):
            time.sleep(6); s, j = api("GET", "contactslist/%s/managemanycontacts/%s" % (lid, job)); d = data(j)[0]
            if d.get("Status") in ("Completed", "Error"):
                print("  job", d["Status"], "count", d.get("Count"), "errors", d.get("ErrorCount")); break
    s, j = api("GET", "contactslist/%s" % lid); print("LISTA", a.ime, "ID", lid, "kontakata", data(j)[0]["SubscriberCount"])
    upisi("liste", a.ime, {"id": lid, "csv": a.csv, "kontakata": len(kontakti), "kad": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})


def html_iz(txt):
    txt = txt.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"').replace("\u00ab", '"').replace("\u00bb", '"')
    m = re.search(r"\[\[UNSUB_LINK_\w+\]\]", txt)
    if not m:
        raise SystemExit("u tijelu nema [[UNSUB_LINK_XX]]")
    unsub = m.group(0)
    hp = []
    for p in [p.strip() for p in txt.split("\n\n") if p.strip()]:
        p2 = re.sub(r"(https://[^\s<]+?)([.,;:!?)]*)(?=\s|<|$)", r'<a href="\1" style="color:#1a4a8a">\1</a>\2', p)
        if unsub in p2:
            rijec = p2.split(":")[-1].strip().replace(unsub, "").strip() or "unsubscribe"
            p2 = re.sub(r":\s*[^:]*" + re.escape(unsub) + r"\s*$", ': <a href="%s" style="color:#6B6B6B">%s</a>' % (unsub, rijec), p2)
        small = "font-size:12px;color:#6B6B6B;" if ("M.G. Solutions" in p or unsub in p2) else ""
        hp.append('<p style="font-family:Georgia,serif;font-size:15px;line-height:1.5;color:#1F1B24;%s">%s</p>' % (small, p2.replace("\n", "<br>")))
    html = '<html><head><meta charset="utf-8"></head><body style="background:#ffffff;padding:16px;max-width:640px">' + "\n".join(hp) + "</body></html>"
    for z in ZABRANE:
        if z in html:
            raise SystemExit("ZABRANA u tekstu: %r" % z)
    return html, txt, unsub


def cmd_nacrt(a):
    lid, n = lista_id(a.ime)
    if not lid:
        raise SystemExit("lista %r ne postoji; prvo `lista`" % a.ime)
    predmet = io.open(a.predmet, encoding="utf-8").read().strip()
    txt = io.open(a.tijelo, encoding="utf-8").read().strip()
    html, txt, unsub = html_iz(txt)
    s, j = api("GET", "contact", params={"ContactsList": lid, "Limit": 1}); c = data(j)[0]
    s, j = api("GET", "contactdata/%s" % c["ID"]); polja = {x["Name"] for x in data(j)[0]["Data"]}
    vars_ = set(re.findall(r"\[\[data:([^:\]]+)", html + predmet))
    if not vars_ <= polja:
        raise SystemExit("tekst traži polja %s, a kontakti liste nose %s" % (sorted(vars_), sorted(polja)))
    S = ucitaj_stanje(); N = S.setdefault("nacrti", {})
    did = (N.get(a.naslov) or {}).get("id")
    if did:
        s, j = api("GET", "campaigndraft/%s" % did)
        if s != 200 or data(j)[0].get("Status") != 0:
            did = None
    if not did:
        s, j = api("POST", "campaigndraft", json={"Locale": a.locale, "Sender": a.ime_posiljatelja, "SenderName": a.ime_posiljatelja, "SenderEmail": a.posiljatelj,
                                                 "ReplyEmail": a.posiljatelj, "Subject": predmet, "ContactsListID": lid, "Title": a.naslov, "EditMode": "html2"})
        if s >= 300:
            raise SystemExit("nacrt nije stvoren: %s %s" % (s, str(j)[:200]))
        did = data(j)[0]["ID"]; print("nacrt stvoren", did)
    s, j = api("POST", "campaigndraft/%s/detailcontent" % did, json={"Html-part": html, "Text-part": txt}); print("sadržaj", s)
    s, j = api("GET", "campaigndraft/%s" % did); d = data(j)[0]
    print("PROVJERA", {k: d.get(k) for k in ("ID", "Title", "Subject", "SenderName", "SenderEmail", "ContactsListID", "Status", "Locale")})
    upisi("nacrti", a.naslov, {"id": did, "lista": a.ime, "lista_id": lid, "predmet": predmet, "tijelo": a.tijelo, "kad": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
    print("GOTOVO nacrt %s | NIŠTA NIJE POSLANO" % a.naslov)


def nacrt_po_naslovu(naslov):
    S = ucitaj_stanje(); z = (S.get("nacrti") or {}).get(naslov)
    if z:
        return z["id"], z["lista_id"]
    for off in range(0, 2000, 100):
        s, j = api("GET", "campaigndraft", params={"Limit": 100, "Offset": off})
        D = data(j)
        for d in D:
            if d.get("Title") == naslov:
                return d["ID"], d.get("ContactsListID")
        if len(D) < 100:
            break
    raise SystemExit("nacrt %r ne postoji" % naslov)


def cmd_probni(a):
    did, lid = nacrt_po_naslovu(a.naslov)
    s, j = api("GET", "contact/" + a.na)
    if s == 404:
        s, j = api("POST", "contact", json={"Email": a.na, "Name": "WWM proba"}); print("probni kontakt stvoren", s)
    s, j = api("GET", "contact", params={"ContactsList": lid, "Limit": 1}); c = data(j)[0]
    s, j = api("GET", "contactdata/%s" % c["ID"]); polja = {x["Name"]: x["Value"] for x in data(j)[0]["Data"]}
    s, j = api("PUT", "contactdata/" + a.na, json={"Data": [{"Name": k, "Value": v} for k, v in polja.items()]}); print("polja probnog kontakta", s, polja)
    time.sleep(2)
    s, j = api("POST", "campaigndraft/%s/test" % did, json={"Recipients": [{"Email": a.na, "Name": "WWM proba"}]})
    print("PROBNI na %s: %s %s" % (a.na, s, str(j)[:150] if s >= 300 else "poslan"))
    s, j = api("GET", "campaigndraft/%s" % did); print("status nacrta poslije:", data(j)[0].get("Status"), "(0 = nacrt, nije poslano)")


def cmd_salji(a):
    if not a.odobrio or len(a.odobrio) < 8:
        raise SystemExit("--odobrio mora nositi Matijinu riječ doslovno (tko, datum, što)")
    did, lid = nacrt_po_naslovu(a.naslov)
    s, j = api("GET", "campaigndraft/%s" % did); d = data(j)[0]
    s, j = api("GET", "contactslist/%s" % lid); L = data(j)[0]
    s, j = api("GET", "campaigndraft/%s/detailcontent" % did); sadrzaj = data(j)[0] if data(j) else {}
    print("nacrt %s | status %s | predmet %s | od %s | lista %s (%s kontakata) | tekst %d znakova" % (
        did, d.get("Status"), d.get("Subject"), d.get("SenderEmail"), L.get("Name"), L.get("SubscriberCount"), len(sadrzaj.get("Text-part") or "")))
    if d.get("Status") != 0:
        raise SystemExit("STOP: nacrt nije u stanju 0 (nacrt), ne šaljem")
    if not L.get("SubscriberCount"):
        raise SystemExit("STOP: lista prazna")
    if len(sadrzaj.get("Text-part") or "") < 200:
        raise SystemExit("STOP: sadržaj nacrta prazan ili prekratak")
    s, j = api("POST", "campaigndraft/%s/send" % did)
    print("SEND", s, str(j)[:200])
    os.makedirs(OUT, exist_ok=True); novo = not os.path.exists(POSLANO)
    with io.open(POSLANO, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["kad_utc", "naslov", "nacrt", "lista", "lista_id", "kontakata", "posiljatelj", "predmet", "odobrio", "http", "odgovor"])
        w.writerow([datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), a.naslov, did, L.get("Name"), lid, L.get("SubscriberCount"),
                    d.get("SenderEmail"), d.get("Subject"), a.odobrio, s, json.dumps(j, ensure_ascii=False)[:200]])
    if s >= 300:
        raise SystemExit("slanje NIJE prihvaćeno")
    print("POSLANO: %s, %s kontakata; zapis %s" % (a.naslov, L.get("SubscriberCount"), POSLANO))


def cmd_makni(a):
    lid, n = lista_id(a.ime)
    if not lid:
        raise SystemExit("lista %r ne postoji" % a.ime)
    adrese = [l.strip().lower() for l in io.open(a.adrese, encoding="utf-8") if l.strip() and "@" in l]
    ok = 0
    for e in adrese:
        s, j = api("POST", "contactslist/%s/managecontact" % lid, json={"Email": e, "Action": "remove"})
        ok += s < 300; time.sleep(0.3)
    s, j = api("GET", "contactslist/%s" % lid)
    print("maknuto %d od %d; lista sad %s kontakata" % (ok, len(adrese), data(j)[0]["SubscriberCount"]))


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("stanje")
    p = sub.add_parser("lista"); p.add_argument("--ime", required=True); p.add_argument("--csv", required=True); p.add_argument("--kontaktirano", default=KONT)
    p = sub.add_parser("nacrt"); p.add_argument("--ime", required=True); p.add_argument("--naslov", required=True); p.add_argument("--locale", required=True)
    p.add_argument("--predmet", required=True); p.add_argument("--tijelo", required=True)
    p.add_argument("--posiljatelj", default="contact@prvoiceglobal.com"); p.add_argument("--ime-posiljatelja", default="PR Voice Global")
    p = sub.add_parser("probni"); p.add_argument("--naslov", required=True); p.add_argument("--na", required=True)
    p = sub.add_parser("salji"); p.add_argument("--naslov", required=True); p.add_argument("--odobrio", required=True)
    p = sub.add_parser("makni"); p.add_argument("--ime", required=True); p.add_argument("--adrese", required=True)
    a = ap.parse_args()
    {"stanje": cmd_stanje, "lista": cmd_lista, "nacrt": cmd_nacrt, "probni": cmd_probni, "salji": cmd_salji, "makni": cmd_makni}[a.cmd](a)


if __name__ == "__main__":
    main()
