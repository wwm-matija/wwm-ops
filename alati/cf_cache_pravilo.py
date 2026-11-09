#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cf_cache_pravilo.py: postavi (ili pokaže) Cloudflare Cache Rule koje kešira /data/* na worldwinerymap.com.

Zašto: Cloudflare JSON ne kešira sam (cf-cache-status: DYNAMIC), pa svaki posjetitelj vuče ~10 datoteka karte
s origina u SAD-u (1,0 do 1,5 s po datoteci). Datoteke su versionirane (?v=SHV), origin već šalje max-age=604800.

Radi na Hetzneru. Token čita iz /root/.env.cf_pravila (CF_PRAVILA_TOKEN: Zone Cache Rules Edit + Zone Read),
zonu iz /root/.env.cloudflare (CF_ZONE_ID). Ništa od tajni ne ispisuje.

    python3 alati/cf_cache_pravilo.py            # pokaži postojeća cache pravila zone
    python3 alati/cf_cache_pravilo.py --pisi     # dodaj pravilo ako ga nema (idempotentno, po opisu WWM-DATA-CACHE)
"""
import json, sys, urllib.request, urllib.error

OPIS = "WWM-DATA-CACHE: /data/* (bez shards) s nase stranice, bez robota, u rubni kes (2026-11-09)"
# Kes smije samo ono sto bi i origin pustio: zahtjev s nase stranice (Referer) i bez robotskog agenta.
# Sve ostalo NIJE podobno za kes pa ide na origin, gdje .htaccess brave rade kao i prije (403).
# /data/shards/ (tocke vinarija) se nikad ne kesira: origin za njih trazi Referer i to mora ostati na originu.
ROBOTI = ["curl", "wget", "python", "scrapy", "httrack", "libwww", "lwp-", "java/", "go-http-client", "okhttp", "axios", "node-fetch", "aiohttp", "Python", "Java/", "Go-http-client"]
IZRAZ = ('(http.host eq "worldwinerymap.com" and starts_with(http.request.uri.path, "/data/")'
         ' and not starts_with(http.request.uri.path, "/data/shards/")'
         ' and http.referer contains "worldwinerymap.com" and http.user_agent ne ""'
         + "".join(' and not http.user_agent contains "%s"' % r for r in ROBOTI) + ')')
PRAVILO = {"description": OPIS, "expression": IZRAZ, "action": "set_cache_settings", "enabled": True,
           "action_parameters": {"cache": True, "edge_ttl": {"mode": "respect_origin"}, "browser_ttl": {"mode": "respect_origin"}}}


def env(p, var):
    for l in open(p, encoding="utf-8"):
        if l.startswith(var + "="):
            return l.split("=", 1)[1].strip().strip('"')
    sys.exit("STOP: nema %s u %s" % (var, p))


def api(metoda, put, tok, tijelo=None):
    req = urllib.request.Request("https://api.cloudflare.com/client/v4" + put, method=metoda,
                                 data=json.dumps(tijelo).encode("utf-8") if tijelo is not None else None,
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json", "User-Agent": "wwm-ops/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"success": False, "errors": [str(e)]}


def main():
    pisi = "--pisi" in sys.argv
    tok = env("/root/.env.cf_pravila", "CF_PRAVILA_TOKEN"); zona = env("/root/.env.cloudflare", "CF_ZONE_ID")
    baza = "/zones/%s/rulesets/phases/http_request_cache_settings/entrypoint" % zona
    st, r = api("GET", baza, tok)
    pravila = []
    if st == 200 and r.get("success"):
        pravila = r["result"].get("rules") or []
        print("postojeći skup cache pravila: %d pravila" % len(pravila))
        for p in pravila:
            print("  - [%s] %s | %s | %s" % ("uklj" if p.get("enabled") else "ISKLJ", p.get("description", "")[:70], p.get("action"), p.get("expression", "")[:90]))
    elif st == 404:
        print("skup cache pravila još ne postoji (nijedno pravilo)")
    else:
        sys.exit("STOP: čitanje pravila nije uspjelo (%s): %s" % (st, json.dumps(r.get("errors"))[:300]))
    postoji = [p for p in pravila if (p.get("description") or "").startswith("WWM-DATA-CACHE")]
    if postoji and postoji[0].get("expression") == IZRAZ:
        print("pravilo WWM-DATA-CACHE vec postoji s istim izrazom; nista ne mijenjam"); return
    if not pisi:
        print("(proba: pravilo bi bilo %s; pokreni s --pisi)" % ("azurirano" if postoji else "dodano")); return
    cista = [{k: v for k, v in p.items() if k in ("description", "expression", "action", "action_parameters", "enabled")}
             for p in pravila if not (p.get("description") or "").startswith("WWM-DATA-CACHE")]
    st, r = api("PUT", baza, tok, {"rules": cista + [PRAVILO]})
    if st == 200 and r.get("success"):
        print("UPISANO: skup sada ima %d pravila; novo: %s" % (len(r["result"].get("rules") or []), OPIS))
    else:
        sys.exit("STOP: upis nije uspio (%s): %s" % (st, json.dumps(r.get("errors"))[:400]))


if __name__ == "__main__":
    main()
