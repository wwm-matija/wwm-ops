#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cf_access_admin.py: stavi stranicu https://api.worldwinerymap.com/admin iza Cloudflare Accessa (prijava kodom na mail),
dopušteno samo navedenim adresama. Odluka vlasnika 9.11.2026. (odluke/2026-11-08-revizija-1, stavka 1.2).

Opseg: SAMO stranica /admin. Admin API (/api/admin/*) ostaje iza ključa X-Admin-Key kao dosad; cron ide na 127.0.0.1
i Access ga ne dira. Preduvjet koji API ne može: Zero Trust (Access) mora biti jednom uključen u Cloudflare sučelju.

Radi na Hetzneru. Token iz /root/.env.cf_pravila (CF_PRAVILA_TOKEN, ovlast Zone: Access: Apps and Policies Edit),
zona iz /root/.env.cloudflare (CF_ZONE_ID).

    python3 alati/cf_access_admin.py                                  # pokaži postojeće Access aplikacije zone
    python3 alati/cf_access_admin.py --pisi --mail ime@gmail.com      # napravi aplikaciju i pravilo (idempotentno)
"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cf_cache_pravilo import env, api

IME = "WWM admin"
DOMENA = "api.worldwinerymap.com/admin"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pisi", action="store_true"); ap.add_argument("--mail", action="append", default=[])
    a = ap.parse_args()
    tok = env("/root/.env.cf_pravila", "CF_PRAVILA_TOKEN"); zona = env("/root/.env.cloudflare", "CF_ZONE_ID")
    baza = "/zones/%s/access/apps" % zona
    st, r = api("GET", baza, tok)
    if not r.get("success"):
        poruka = json.dumps(r.get("errors"))
        if "not_enabled" in poruka:
            sys.exit("STOP: Access nije uključen na računu. Matija: Cloudflare, početna stranica računa, Zero Trust, odabrati ime tima i Free plan. Zatim ponovi.")
        sys.exit("STOP: čitanje aplikacija nije uspjelo (%s): %s" % (st, poruka[:300]))
    apps = r.get("result") or []
    print("Access aplikacija u zoni: %d" % len(apps))
    for x in apps:
        print("  - %s | %s | sesija %s" % (x.get("name"), x.get("domain"), x.get("session_duration")))
    postoji = [x for x in apps if x.get("domain") == DOMENA]
    if not a.pisi:
        print("(proba; aplikacija za %s %s)" % (DOMENA, "postoji" if postoji else "ne postoji")); return
    if not a.mail:
        sys.exit("STOP: treba --mail adresa kojoj je ulaz dopušten")
    if postoji:
        app = postoji[0]; print("aplikacija već postoji: %s" % app.get("id", "")[:8])
    else:
        st, r = api("POST", baza, tok, {"name": IME, "domain": DOMENA, "type": "self_hosted", "session_duration": "24h",
                                         "app_launcher_visible": False, "auto_redirect_to_identity": False})
        if not r.get("success"):
            sys.exit("STOP: aplikacija nije napravljena (%s): %s" % (st, json.dumps(r.get("errors"))[:400]))
        app = r["result"]; print("aplikacija napravljena: %s za %s" % (app.get("id", "")[:8], DOMENA))
    st, r = api("GET", baza + "/%s/policies" % app["id"], tok)
    pravila = r.get("result") or []
    if any(p.get("name") == "samo vlasnik" for p in pravila):
        print("pravilo »samo vlasnik« već postoji (%d pravila)" % len(pravila)); return
    st, r = api("POST", baza + "/%s/policies" % app["id"], tok,
                {"name": "samo vlasnik", "decision": "allow", "include": [{"email": {"email": m.strip().lower()}} for m in a.mail]})
    if not r.get("success"):
        sys.exit("STOP: pravilo nije upisano (%s): %s; aplikacija BEZ pravila odbija sve, provjeri odmah" % (st, json.dumps(r.get("errors"))[:400]))
    print("pravilo upisano: dopušteno %d adresa; sve ostalo odbijeno" % len(a.mail))


if __name__ == "__main__":
    main()
