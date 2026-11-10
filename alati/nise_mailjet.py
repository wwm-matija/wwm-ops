# -*- coding: utf-8 -*-
"""Niše (mediji, val 29.10.): novi krug kroz Mailjet za adrese kojima mail iz Snova nije otišao (čekale, žute, preskočene).
Odluka Matije 10.11.2026.: »novi tekst, ostavi stari za ovu rundu; žute može kroz Mailjet«. NIŠTA SE NE ŠALJE ovim alatom;
slanje ide kroz `alati/mailjet_runda.py salji --naslov ... --odobrio ...` po nacrtu, na Matijinu riječ.

python alati/nise_mailjet.py plan     [--runda r2]      liste i tekstovi po ključu teksta (zemlja_jezik) u out/nise_<runda>/, izvještaj
python alati/nise_mailjet.py mailjet  [--runda r2] [--samo US_en,DE_de]   liste i nacrti u Mailjetu (status 0), bez slanja
python alati/nise_mailjet.py probni   --kljuc US_en --na desk@worldwinerymap.org

Ulaz (mapa vala, WWM_NISE ili C:/Users/world/Documents/WWM_PR_NISE_2026-10-29): RASPORED_NISE.csv (5.440 adresa: email, tekst, _lang,
_hook, _grupa), PRESS_POPIS.json (predmet, pitch, naslov, folder), izlaz/<ključ>.md kroz gen_press_nise.ucitaj (priča: pod, odlomci),
potpisi_labele_nise.json. Pošiljatelj contact@prvoiceglobal.com »PR Voice Global«; potpis sig_b s brendom PR Voice Global;
kuka = ista press stranica na pr-voice.info (provjera 200; ako je nema, ostaje izvorna kuka iz rasporeda).
Tko ne ide: kome je Snov stvarno poslao (out/snov_poslano_sve_0911.json), tko je odgovorio (ODGOVORI_3010.json, _odgovori_scan_*.json),
naša lista ne kontaktirati, dvostruke adrese. Isti tekst kao u Snovu (i »WorldWineryMap.com« kao tekst, Matija 10.11.: crne liste čiste, smije),
uz podnožje s odjavom na engleskom (Mailjet traži [[UNSUB_LINK_XX]]). LINK na worldwinerymap.com i dalje ne smije (Spamhaus 19.9.).
"""
import argparse, collections, csv, html, io, json, os, re, sys, time, types

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out")
D = os.environ.get("WWM_NISE", "C:/Users/world/Documents/WWM_PR_NISE_2026-10-29")
SNOV_POSLANO = os.path.join(OUT, "snov_poslano_sve_0911.json")
NK = os.path.join(OUT, "NE_KONTAKTIRATI.csv")
PRESS_DOM = "pr-voice.info"
BREND = "PR Voice Global"
RTL = {"ar", "he", "fa", "ur"}
LOCALE = {"en": "en_US", "es": "es_ES", "it": "it_IT", "fr": "fr_FR", "de": "de_DE", "pt": "pt_PT", "nl": "nl_NL", "pl": "pl_PL", "tr": "tr_TR", "hu": "hu_HU", "ja": "ja_JP",
          "ro": "ro_RO", "cs": "cs_CZ", "bg": "bg_BG", "sv": "sv_SE", "uk": "uk_UA", "ko": "ko_KR", "ar": "ar_AR", "no": "nb_NO", "el": "el_GR", "sk": "sk_SK", "fi": "fi_FI",
          "id": "id_ID", "da": "da_DK", "vi": "vi_VN", "he": "he_IL", "zh-cn": "zh_CN", "th": "th_TH", "ru": "ru_RU", "hr": "hr_HR", "sl": "sl_SI", "sr": "sr_RS", "lt": "lt_LT", "lv": "lv_LV", "et": "et_EE"}
PODNOZJE = ("PR Voice Global is a division of M.G. Solutions d.o.o., Ulica Labinske republike 6B, 52470 Umag, Croatia. "
            "You are receiving this email because your publication covers wine, food, travel or business. To stop further messages: unsubscribe [[UNSUB_LINK_EN]]")
MAILRE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._%+\-]{0,63}@[A-Za-z0-9][A-Za-z0-9.\-]{1,60}\.[A-Za-z]{2,12}")


def ucitaj_gp():
    stub = types.ModuleType("gen_press_il"); stub.esc = lambda s: html.escape(s, quote=False); stub.CSS = ""; stub.docx_story = lambda *a, **k: None
    sys.modules["gen_press_il"] = stub
    sys.path.insert(0, D)
    cwd = os.getcwd(); os.chdir(D)
    import gen_press_nise as GP
    os.chdir(cwd)
    return GP


def tekst_kljuca(GP, P, SIG, k, hook):
    """Vrati (predmet, čisti tekst, html) za ključ teksta i kuku."""
    p = P[k]; t = GP.ucitaj(k.replace("_st", "").replace("_bf", "") if (k.endswith("_st") or k.endswith("_bf")) else k)
    lang = k.split("_", 1)[1].replace("_st", "").replace("_bf", "")
    naslov = p["naslov"]; pod = t["pod"]; odl = list(t["odl"])
    if k.endswith("_st"):
        st = t.get("startup") or ""
        if st:
            odl.insert(1, st)
    pitch = p["pitch"]
    sig = [x.replace("{BREND}", BREND) for x in SIG[lang]["sig_b"]]
    pitch = pitch.replace("{NASLOV}", naslov).replace("{HOOK}", hook).replace("{POTPIS}", "\n".join(sig))
    sep = SIG[lang].get("sep", "-" * 87)
    # 10.11. Matija: .com kao tekst (ne link) išao je u 534 niše i val lok. vinarija 27.10. bez posljedica, crne liste čiste; tekst ostaje kakav je u Snovu
    if "https://worldwinerymap.com" in (pitch + naslov + pod + " ".join(odl)).lower() or "http://worldwinerymap.com" in (pitch + " ".join(odl)).lower():
        raise SystemExit("LINK na worldwinerymap.com u tekstu %s (Spamhaus 19.9.): tekst ne ide" % k)
    txt = pitch.strip() + "\n\n" + sep + "\n\n" + naslov + "\n\n" + pod + "\n\n" + "\n\n".join(odl) + "\n\n" + PODNOZJE
    e = lambda s: html.escape(s, quote=False)
    rtl = ' dir="rtl" style="text-align:right"' if lang in RTL else ""
    ps = 'style="font-family:Georgia,serif;font-size:15px;line-height:1.5;color:#1F1B24"'
    hp = []
    for par in [x.strip() for x in pitch.split("\n\n") if x.strip()]:
        h = "<br>".join(e(l) for l in par.split("\n"))
        h = re.sub(r"(https://[^\s<]+?)([.,;:!?)]*)(?=\s|<|$)", r'<a href="\1" style="color:#1a4a8a">\1</a>\2', h)
        hp.append("<p %s>%s</p>" % (ps, h))
    hp.append('<p style="color:#9a9a9a;font-size:12px">%s</p>' % e(sep))
    hp.append("<p %s><b>%s</b></p>" % (ps, e(naslov)))
    hp.append("<p %s><em>%s</em></p>" % (ps, e(pod)))
    hp += ["<p %s>%s</p>" % (ps, e(o)) for o in odl]
    hp.append('<p style="font-family:Georgia,serif;font-size:12px;line-height:1.5;color:#6B6B6B">%s</p>' % e(PODNOZJE).replace(
        "unsubscribe [[UNSUB_LINK_EN]]", '<a href="[[UNSUB_LINK_EN]]" style="color:#6B6B6B">unsubscribe</a>'))
    htm = '<html><head><meta charset="utf-8"></head><body%s style="background:#ffffff;padding:16px;max-width:640px">' % rtl + "\n".join(hp) + "</body></html>"
    for z in ("https://worldwinerymap.com", "http://worldwinerymap.com", "\u2014", "\u2013"):
        if z in htm.lower():
            raise SystemExit("ZABRANA u tekstu %s: %r" % (k, z))
    return p["predmet"], txt, htm


def hook_za(r, cache):
    """Ista press stranica na pr-voice.info; provjera 200 (keš); inače izvorna kuka."""
    import requests
    izv = r["_hook"]; put = "/" + izv.split("/", 3)[3]
    url = "https://%s%s" % (PRESS_DOM, put)
    if url not in cache:
        try:
            rr = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"}); cache[url] = rr.status_code
        except requests.RequestException:
            cache[url] = 0
        time.sleep(0.3)
    return url if cache[url] == 200 else izv


def cmd_plan(a):
    GP = ucitaj_gp()
    P = {p["kljuc"]: p for p in json.load(io.open(D + "/PRESS_POPIS.json", encoding="utf-8"))}
    SIG = json.load(io.open(D + "/potpisi_labele_nise.json", encoding="utf-8"))
    R = list(csv.DictReader(io.open(D + "/RASPORED_NISE.csv", encoding="utf-8-sig", newline="")))
    sn = json.load(io.open(SNOV_POSLANO, encoding="utf-8")); poslano = {e.lower() for v in sn.values() for e in v.get("adrese", [])}
    odg = set()
    for f in os.listdir(D):
        if f.startswith(("ODGOVORI_", "_odgovori_scan")) and f.endswith(".json"):
            odg |= {m.lower() for m in MAILRE.findall(io.open(os.path.join(D, f), encoding="utf-8", errors="replace").read())}
    nk_a, nk_d = set(), set()
    for r in csv.DictReader(io.open(NK, encoding="utf-8-sig", newline="")):
        if r.get("email"):
            nk_a.add(r["email"].strip().lower())
        elif r.get("domena"):
            nk_d.add(r["domena"].strip().lower())
    O = os.path.join(OUT, "nise_" + a.runda); os.makedirs(O + "/liste", exist_ok=True); os.makedirs(O + "/tekstovi", exist_ok=True)
    kes_p = O + "/hook_provjera.json"; kes = json.load(io.open(kes_p, encoding="utf-8")) if os.path.exists(kes_p) else {}
    izb = collections.Counter(); videno = set(); po_kljucu = collections.defaultdict(list)
    for r in R:
        e = r["email"].strip().lower()
        if e in poslano:
            izb["Snov već poslao"] += 1; continue
        if e in odg:
            izb["odgovorili"] += 1; continue
        if e in nk_a or e.split("@")[1] in nk_d:
            izb["ne kontaktirati"] += 1; continue
        if e in videno:
            izb["dvostruko"] += 1; continue
        if r["tekst"] not in P:
            izb["ključ bez teksta u PRESS_POPIS"] += 1; continue
        videno.add(e); po_kljucu[r["tekst"]].append(r)
    nacrti = {}; hook_pad = 0
    for k, rows in sorted(po_kljucu.items()):
        hook = hook_za(rows[0], kes)
        if PRESS_DOM not in hook:
            hook_pad += 1
        pred, txt, htm = tekst_kljuca(GP, P, SIG, k, hook)
        lang = k.split("_", 1)[1].replace("_st", "").replace("_bf", "")
        with io.open("%s/liste/%s.csv" % (O, k), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f); w.writerow(["email", "company_name", "body2", "jezik", "zemlja", "nisa"])
            for r in rows:
                w.writerow([r["email"].lower(), r["domain"], r["domain"], lang, r.get("iso_konacno", ""), r.get("nisa_konacno", "")])
        io.open("%s/tekstovi/%s_predmet.txt" % (O, k), "w", encoding="utf-8").write(pred)
        io.open("%s/tekstovi/%s_tijelo.txt" % (O, k), "w", encoding="utf-8").write(txt)
        io.open("%s/tekstovi/%s_tijelo.html" % (O, k), "w", encoding="utf-8").write(htm)
        nacrti[k] = {"adresa": len(rows), "jezik": lang, "locale": LOCALE.get(lang, "en_US"), "predmet": pred, "hook": hook, "lista": "NISE %s %s" % (k, a.runda),
                     "naslov": "NISE %s %s (PR Voice Global)" % (k, a.runda), "csv": "liste/%s.csv" % k, "tijelo": "tekstovi/%s_tijelo.txt" % k}
    json.dump(kes, io.open(kes_p, "w", encoding="utf-8"), indent=0)
    po_jez = collections.Counter();
    for k, v in nacrti.items():
        po_jez[v["jezik"]] += v["adresa"]
    rep = {"vrijeme": time.strftime("%Y-%m-%d %H:%M"), "raspored": len(R), "izbaceno": dict(izb), "za_slanje": sum(v["adresa"] for v in nacrti.values()),
           "kljuceva": len(nacrti), "kuka_nije_na_pr_voice": hook_pad, "po_jeziku": dict(po_jez.most_common()), "nacrti": nacrti}
    json.dump(rep, io.open(O + "/plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "nacrti"}, ensure_ascii=False, indent=1))
    print("PLAN:", O, "| nacrta", len(nacrti), "| ništa nije dirano u Mailjetu")


def cmd_mailjet(a):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mailjet_runda as MJ
    O = os.path.join(OUT, "nise_" + a.runda); plan = json.load(io.open(O + "/plan.json", encoding="utf-8"))
    samo = {x.strip() for x in a.samo.split(",") if x.strip()} if a.samo else None
    S = MJ.ucitaj_stanje(); N = S.setdefault("nacrti", {}); L = S.setdefault("liste", {})
    s, j = MJ.api("GET", "contactmetadata", params={"Limit": 200}); ima = {x["Name"] for x in MJ.data(j)}
    for p in ("company_name", "body2"):
        if p not in ima:
            MJ.api("POST", "contactmetadata", json={"Datatype": "str", "Name": p, "NameSpace": "static"})
    kont_sve = set()
    if os.path.exists(MJ.KONT):
        kont_sve = {l.strip().lower() for l in io.open(MJ.KONT, encoding="utf-8") if l.strip() and not l.startswith("#")}
    n_ok = 0
    for k, v in sorted(plan["nacrti"].items()):
        if samo and k not in samo:
            continue
        if N.get(v["naslov"], {}).get("id"):
            did = N[v["naslov"]]["id"]
            s, j = MJ.api("GET", "campaigndraft/%s" % did)
            if s == 200 and MJ.data(j)[0].get("Status") == 0:
                txt = io.open(os.path.join(O, v["tijelo"]), encoding="utf-8").read()
                htm = io.open(os.path.join(O, "tekstovi/%s_tijelo.html" % k), encoding="utf-8").read()
                s2, j2 = MJ.api("POST", "campaigndraft/%s/detailcontent" % did, json={"Html-part": htm, "Text-part": txt})
                print("nacrt postoji, sadržaj osvježen:", v["naslov"], s2); n_ok += 1; continue
            print("preskačem, nacrt postoji i nije u stanju 0:", v["naslov"]); n_ok += 1; continue
        R = MJ.citaj_csv(os.path.join(O, v["csv"]))
        kont = [{"Email": r["email"], "Name": r["company_name"][:255], "Properties": {"company_name": r["company_name"], "body2": r["body2"]}} for r in R if r["email"] not in kont_sve]
        lid, n = MJ.lista_id(v["lista"])
        if not lid:
            s, j = MJ.api("POST", "contactslist", json={"Name": v["lista"]}); lid = MJ.data(j)[0]["ID"]
        s, j = MJ.api("POST", "contactslist/%s/managemanycontacts" % lid, json={"Action": "addforce", "Contacts": kont}); job = MJ.data(j)[0]["JobID"] if s < 300 else None
        if not job:
            print("UVOZ NIJE PRIHVAĆEN", k, s, str(j)[:160]); continue
        for cek in range(60):
            time.sleep(4); s, j = MJ.api("GET", "contactslist/%s/managemanycontacts/%s" % (lid, job)); dd = MJ.data(j)
            if dd and dd[0].get("Status") in ("Completed", "Error"):
                break
            if not dd and cek % 5 == 4:
                print("  job %s: Mailjet vraća %s %s, čekam" % (job, s, str(j)[:80]))
        MJ.upisi("liste", v["lista"], {"id": lid, "kontakata": len(kont), "kad": time.strftime("%Y-%m-%d %H:%M")})
        pred = io.open(os.path.join(O, "tekstovi/%s_predmet.txt" % k), encoding="utf-8").read().strip()
        txt = io.open(os.path.join(O, v["tijelo"]), encoding="utf-8").read()
        htm = io.open(os.path.join(O, "tekstovi/%s_tijelo.html" % k), encoding="utf-8").read()
        s, j = MJ.api("POST", "campaigndraft", json={"Locale": v["locale"], "Sender": BREND, "SenderName": BREND, "SenderEmail": "contact@prvoiceglobal.com", "ReplyEmail": "contact@prvoiceglobal.com",
                                                    "Subject": pred, "ContactsListID": lid, "Title": v["naslov"], "EditMode": "html2"})
        if s >= 300 and v["locale"] != "en_US":
            s, j = MJ.api("POST", "campaigndraft", json={"Locale": "en_US", "Sender": BREND, "SenderName": BREND, "SenderEmail": "contact@prvoiceglobal.com", "ReplyEmail": "contact@prvoiceglobal.com",
                                                        "Subject": pred, "ContactsListID": lid, "Title": v["naslov"], "EditMode": "html2"})
        if s >= 300:
            print("NACRT NIJE STVOREN", k, s, str(j)[:160]); continue
        did = MJ.data(j)[0]["ID"]
        s2, j2 = MJ.api("POST", "campaigndraft/%s/detailcontent" % did, json={"Html-part": htm, "Text-part": txt})
        MJ.upisi("nacrti", v["naslov"], {"id": did, "lista": v["lista"], "lista_id": lid, "predmet": pred, "tijelo": v["tijelo"], "kad": time.strftime("%Y-%m-%d %H:%M"), "sadrzaj_http": s2})
        n_ok += 1
        print("%-28s lista %s (%d) nacrt %s sadržaj %s" % (k, lid, len(kont), did, s2))
    print("GOTOVO: nacrta spremno %d od %d | NIŠTA NIJE POSLANO" % (n_ok, len(plan["nacrti"]) if not samo else len(samo)))


def cmd_probni(a):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mailjet_runda as MJ
    naslov = "NISE %s %s (PR Voice Global)" % (a.kljuc, a.runda)
    ns = argparse.Namespace(naslov=naslov, na=a.na); MJ.cmd_probni(ns)


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan"); p.add_argument("--runda", default="r2")
    p = sub.add_parser("mailjet"); p.add_argument("--runda", default="r2"); p.add_argument("--samo", default="")
    p = sub.add_parser("probni"); p.add_argument("--runda", default="r2"); p.add_argument("--kljuc", required=True); p.add_argument("--na", required=True)
    a = ap.parse_args()
    {"plan": cmd_plan, "mailjet": cmd_mailjet, "probni": cmd_probni}[a.cmd](a)


if __name__ == "__main__":
    main()
