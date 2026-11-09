#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cf_token_upis.py: iz sirove datoteke koju je Matija spremio (token zalijepljen u Notepad, smije biti i ostali tekst sa
stranice tokena) izvuče Cloudflare API token, provjeri ga kod Cloudflarea i upiše u env datoteku 0600.
Vrijednost tokena se NIKAD ne ispisuje. Sirova datoteka se briše tek nakon potvrđenog upisa.

Radi na Hetzneru:
    python3 alati/cf_token_upis.py --sirovo /root/.cf_sirovo.txt --env /root/.env.cf_pravila --var CF_PRAVILA_TOKEN
"""
import argparse, json, os, re, sys, urllib.request


def provjeri(tok):
    req = urllib.request.Request("https://api.cloudflare.com/client/v4/user/tokens/verify",
                                 headers={"Authorization": "Bearer " + tok, "User-Agent": "wwm-ops/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"success": False, "errors": [str(e)[:200]]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sirovo", required=True); ap.add_argument("--env", required=True); ap.add_argument("--var", required=True)
    a = ap.parse_args()
    txt = open(a.sirovo, encoding="utf-8", errors="replace").read()
    # kandidati: dugi nizovi bez razmaka (token ima 40+ znakova); izbaci URL-ove i riječi iz curl primjera
    kand = []
    for m in re.finditer(r"[A-Za-z0-9_\-]{37,}", txt):
        s = m.group(0)
        if s.lower().startswith(("http", "application", "authorization")):
            continue
        if s not in kand:
            kand.append(s)
    print("kandidata za token u datoteci: %d (duljine: %s)" % (len(kand), ", ".join(str(len(k)) for k in kand)))
    dobar = None
    for k in kand:
        r = provjeri(k)
        if r.get("success") and (r.get("result") or {}).get("status") == "active":
            dobar = k
            print("token potvrđen: status active, id %s, istječe %s" % ((r["result"].get("id") or "")[:8] + "…", r["result"].get("expires_on") or "BEZ ROKA"))
            break
    if not dobar:
        sys.exit("STOP: nijedan kandidat nije prošao provjeru kod Cloudflarea; ništa nije upisano, sirova datoteka ostaje")
    stari = ""
    if os.path.exists(a.env):
        stari = "".join(l for l in open(a.env, encoding="utf-8") if not l.startswith(a.var + "="))
    fd = os.open(a.env, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(stari + "%s=%s\n" % (a.var, dobar))
    os.chmod(a.env, 0o600)
    # potvrda upisa pa brisanje sirove datoteke
    ok = any(l.strip() == "%s=%s" % (a.var, dobar) for l in open(a.env, encoding="utf-8"))
    if not ok:
        sys.exit("STOP: upis nije potvrđen, sirova datoteka ostaje")
    os.remove(a.sirovo)
    print("upisano u %s kao %s (prava %s); sirova datoteka obrisana" % (a.env, a.var, oct(os.stat(a.env).st_mode & 0o777)))


if __name__ == "__main__":
    main()
