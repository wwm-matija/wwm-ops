#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lov_priprema.py: složi ulaz za lov na mailove vinarija. Radi na Hetzneru, bazu samo čita.

    python3 lov_priprema.py MAPA [--inv /tmp/wwm_inv]

Ulaz (iz --inv, ono što je složio inventar 9.11.): snov_poslano.json, preklop.json, nk.csv.
Izlaz u MAPA:
  ulaz_web.jsonl      jedan redak po domeni: {dom, vinarije:[{wwm_id, cc, ime, skupina, mail}]}   -> za lov_web.py
  ulaz_bez_weba.jsonl jedan redak po vinariji bez weba (bez maila, ili samo PEC): {wwm_id, cc, ime, lat, lng, gr, ad[, skupina, mail]}  -> za lov_pretraga.py
  priprema.json       brojke

Skupine (vinarija na karti, nije kontaktirana, ne čeka u nacrtu, nije na listi ne kontaktirati, nema profil):
  A  bez maila, ima web
  P  mail je PEC (ne šalje se nikad; traži se drugi mail)
  B  samo besplatni mail (gmail, libero ...), ima web
  C  mail na vlastitoj domeni, zemlja nije isključena (ispalo na čišćenju, žuta, vjerojatno): provjera je li web pravi
Isključene zemlje (DACH, ex-YU) se u skupini C preskaču: mail imaju, ne šaljemo im.
"""
import csv, io, json, os, re, sqlite3, sys, collections

BESPL = re.compile(r"^(gmail|googlemail|yahoo|ymail|hotmail|outlook|live|icloud|aol|msn|libero|virgilio|alice|tiscali|tin|fastwebnet|inwind|email|orange|wanadoo|free|laposte|sfr|neuf|bbox|gmx|web|t-online|freenet|seznam|centrum|volny|sapo|terra|uol|bol|telefonica|me|mac|mail|protonmail|proton|pm|yandex|rambler|bluewin|comcast|att|sbcglobal|verizon|bigpond|btinternet|shaw|telus|xtra|iinet|optusnet|skynet|telenet|hetnet|ziggo|kpn|planet|online|arcor|aon|chello|interia|wp|onet|o2|citromail|freemail|abv|163|126|qq|naver|hanmail|daum)\.", re.I)
PEC = re.compile(r"(^|[.\-])pec([.\-]|$)|legalmail|postecert|arubapec|pecimprese|sicurezzapostale|mypec|registerpec|gigapec|postacert|actaliscertymail|ticertifica|casellapec|lamiapec|pecditta", re.I)
DRUSTVENE = re.compile(r"(^|\.)(facebook|fb|instagram|linktr|google|goo|tripadvisor|wixsite|wordpress|blogspot|business|youtube|youtu|twitter|x|yelp|booking|vivino|untappd|linkedin|tiktok|bit|sites\.google|paginegialle|pagesjaunes|airbnb|wine-searcher|winetourism|squarespace|weebly|jimdo|jimdofree|webnode|godaddysites|ueniweb|site123|strikingly|canva|carrd|shopify|myshopify)\.[a-z.]{2,8}$", re.I)
ISKLJUCENE = set("DE AT CH LI HR SI RS BA ME MK XK".split())


def cista_domena(d):
    d = re.sub(r"^https?://", "", (d or "").strip().lower()).split("/")[0].split("?")[0]
    d = re.sub(r"^www\.", "", d).strip(". ")
    return d if re.fullmatch(r"[a-z0-9\-]+(\.[a-z0-9\-]+)+", d) else ""


def main():
    mapa = sys.argv[1]; inv = sys.argv[sys.argv.index("--inv") + 1] if "--inv" in sys.argv else "/tmp/wwm_inv"
    os.makedirs(mapa, exist_ok=True)
    sn = json.load(io.open(inv + "/snov_poslano.json", encoding="utf-8"))
    pk = json.load(io.open(inv + "/preklop.json", encoding="utf-8"))
    nk = list(csv.DictReader(io.open(inv + "/nk.csv", encoding="utf-8", newline="")))
    poslano = {a.lower().strip() for k in sn.values() for a in (k.get("adrese") or [])}
    ceka = set()
    for ime, L in pk["mailjet"].items():
        (poslano if " r1" in ime else ceka).update(x.lower().strip() for x in L)
    for L in pk["snov"].values(): ceka.update(x.lower().strip() for x in L)
    nk_mail = {r["email"].lower() for r in nk if r.get("email")}
    nk_dom = {r["domena"].lower() for r in nk if r.get("domena") and not r.get("email")} - {"pec.it"}
    c = sqlite3.connect("file:/root/wwm_api/wwm.db?mode=ro", uri=True)
    profil = {str(w) for (w,) in c.execute("SELECT wwm_id FROM claims WHERE status='verified' AND wwm_id IS NOT NULL")}
    po_dom = collections.defaultdict(list); bez = []; B = collections.Counter()
    for w, cc, ime, lat, lng, d, m in c.execute("SELECT wwm_id, upper(coalesce(cc,'')), ime, lat, lng, coalesce(dom,''), lower(coalesce(mail,'')) FROM vinarije WHERE na_karti=1"):
        adrese = [e for e in re.split(r"[;, ]+", m) if "@" in e]
        dd = cista_domena(d)
        if str(w) in profil: B["preskočeno: ima profil"] += 1; continue
        if any(a in poslano for a in adrese): B["preskočeno: kontaktirano"] += 1; continue
        if any(a in ceka for a in adrese): B["preskočeno: čeka u nacrtu"] += 1; continue
        if any(a in nk_mail or a.split("@")[-1] in nk_dom for a in adrese): B["preskočeno: ne kontaktirati"] += 1; continue
        if not adrese:
            if not dd:
                bez.append(dict(wwm_id=w, cc=cc, ime=ime, lat=lat, lng=lng)); B["bez maila i bez weba"] += 1; continue
            sk = "A"
        else:
            md = adrese[0].split("@")[-1]
            if PEC.search(md): sk = "P"
            elif BESPL.match(md): sk = "B"
            elif cc in ISKLJUCENE: B["preskočeno: isključena zemlja s mailom"] += 1; continue
            else:
                sk = "C"
                if not dd: dd = cista_domena(md)      # web nije upisan: probaj domenu maila
            if not dd:
                B["%s bez weba (ne ide u lov kroz web)" % sk] += 1
                if sk == "P": bez.append(dict(wwm_id=w, cc=cc, ime=ime, lat=lat, lng=lng, skupina="P", mail=adrese[0]))
                continue
        if DRUSTVENE.search(dd): B["%s: web je društvena mreža ili graditelj stranica" % sk] += 1; continue
        po_dom[dd].append(dict(wwm_id=w, cc=cc, ime=ime, skupina=sk, mail=adrese[0] if adrese else ""))
        B["%s u lov kroz web" % sk] += 1
    with io.open(mapa + "/ulaz_web.jsonl", "w", encoding="utf-8") as f:
        for d in sorted(po_dom): f.write(json.dumps(dict(dom=d, vinarije=po_dom[d]), ensure_ascii=False) + "\n")
    try:
        t = sqlite3.connect("file:/root/vino_world/tiles/wineries.db?mode=ro", uri=True)
        GA = {x: (g or "", ad or "") for x, g, ad in t.execute("select wwm_id, gr, ad from w")}
    except Exception:
        GA = {}
    for r in bez: r["gr"], r["ad"] = GA.get(r["wwm_id"], ("", ""))
    with io.open(mapa + "/ulaz_bez_weba.jsonl", "w", encoding="utf-8") as f:
        for r in bez: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    B["domena za lov"] = len(po_dom)
    B["domena koje dijeli više od 3 vinarije"] = sum(1 for v in po_dom.values() if len(v) > 3)
    json.dump(dict(B), io.open(mapa + "/priprema.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k in sorted(B): print("  %-58s %7d" % (k, B[k]))


if __name__ == "__main__":
    main()
