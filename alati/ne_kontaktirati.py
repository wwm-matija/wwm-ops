#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ne_kontaktirati.py: JEDNA naša lista adresa i domena kojima se više ništa ne šalje, iz svih kanala
(Snov, Mailjet, odjave mailom, usmene odjave, zahtjevi za micanje, bounce). Odluka vlasnika 9.11.2026.

Lista: out/NE_KONTAKTIRATI.csv (ide u git). Stupci: email, domena, razlog, izvor, datum, napomena, upisao.
  - redak s emailom blokira tu adresu; redak s praznim emailom i upisanom domenom blokira CIJELU domenu
  - razlog: odjava | odbijanje | micanje | bounce | spam-prijava | rucno
  - ništa se iz liste ne briše; ispravak je novi redak s napomenom (povijest ostaje)

Naredbe:
  python alati/ne_kontaktirati.py stat
  python alati/ne_kontaktirati.py provjeri adresa@domena.com [jos@adresa ...]     # izlaz 1 ako je ijedna na listi
  python alati/ne_kontaktirati.py dodaj --email a@b.com --razlog odjava --izvor "mail 9.11." [--napomena "..."] [--upisao Codex]
  python alati/ne_kontaktirati.py dodaj --domena b.com --razlog rucno --izvor "Matija usmeno 9.11."
  python alati/ne_kontaktirati.py uvezi --json out/mailjet_odjavljeni_0911.json --razlog odjava --izvor "Mailjet odjava"
        (JSON: popis objekata s poljem email; neobavezno kad, lista)
  python alati/ne_kontaktirati.py uvezi --txt popis.txt --razlog odjava --izvor "Snov DNE 7.10."   (jedna adresa po retku)

Tko je čita: alati/posalji.py prije svakog slanja (adresa na listi = stavka se ne šalje, bez iznimke),
i svaki agent prije nego složi bilo koju listu primatelja za Snov ili Mailjet.
Listu u Snovu (DNE) i Mailjetu (unsub/exclusion) ovo NE mijenja; to je naša istina, a u alate se prenosi posebno.
"""
import argparse, csv, io, json, os, sys, time

OVDJE = os.path.dirname(os.path.abspath(__file__))
LISTA = os.path.join(os.path.dirname(OVDJE), "out", "NE_KONTAKTIRATI.csv")
STUPCI = ["email", "domena", "razlog", "izvor", "datum", "napomena", "upisao"]
RAZLOZI = ("odjava", "odbijanje", "micanje", "bounce", "spam-prijava", "rucno")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def ucitaj():
    if not os.path.exists(LISTA):
        return []
    with io.open(LISTA, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def spremi(R):
    os.makedirs(os.path.dirname(LISTA), exist_ok=True)
    with io.open(LISTA, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=STUPCI, extrasaction="ignore"); w.writeheader()
        for r in R:
            w.writerow({k: r.get(k, "") for k in STUPCI})


def skupovi(R=None):
    R = ucitaj() if R is None else R
    adrese = {r["email"].strip().lower() for r in R if r.get("email")}
    domene = {r["domena"].strip().lower() for r in R if r.get("domena") and not r.get("email")}
    return adrese, domene


def blokirana(adresa, adrese=None, domene=None):
    """Vrati razlog (tekst) ako je adresa ili njezina domena na listi, inače ''."""
    if adrese is None:
        adrese, domene = skupovi()
    a = (adresa or "").strip().lower()
    if a in adrese:
        return "adresa na listi"
    if a.split("@")[-1] in domene:
        return "domena na listi"
    return ""


def dodaj_red(R, email, domena, razlog, izvor, napomena, upisao, datum=None):
    email = (email or "").strip().lower(); domena = (domena or "").strip().lower() or (email.split("@")[-1] if email else "")
    if not email and not domena:
        return False
    if email and any(r.get("email", "").lower() == email for r in R):
        return False
    if not email and any(not r.get("email") and r.get("domena", "").lower() == domena for r in R):
        return False
    R.append(dict(email=email, domena=domena, razlog=razlog, izvor=izvor, datum=datum or time.strftime("%Y-%m-%d"), napomena=napomena or "", upisao=upisao or ""))
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("stat")
    p = sp.add_parser("provjeri"); p.add_argument("adrese", nargs="+")
    p = sp.add_parser("dodaj"); p.add_argument("--email"); p.add_argument("--domena"); p.add_argument("--razlog", required=True, choices=RAZLOZI)
    p.add_argument("--izvor", required=True); p.add_argument("--napomena", default=""); p.add_argument("--upisao", default="")
    p = sp.add_parser("uvezi"); p.add_argument("--json"); p.add_argument("--txt"); p.add_argument("--razlog", required=True, choices=RAZLOZI)
    p.add_argument("--izvor", required=True); p.add_argument("--upisao", default="")
    a = ap.parse_args()
    R = ucitaj()
    if a.cmd == "stat":
        import collections
        ad, do = skupovi(R)
        print("NE_KONTAKTIRATI: %d redaka, %d adresa, %d cijelih domena" % (len(R), len(ad), len(do)))
        print("po razlogu:", dict(collections.Counter(r["razlog"] for r in R)))
        print("po izvoru:", dict(collections.Counter(r["izvor"] for r in R).most_common(12)))
        return
    if a.cmd == "provjeri":
        ad, do = skupovi(R); lose = 0
        for x in a.adrese:
            b = blokirana(x, ad, do)
            print("%s: %s" % (x, ("NE SLATI (%s)" % b) if b else "nije na listi")); lose += bool(b)
        sys.exit(1 if lose else 0)
    if a.cmd == "dodaj":
        if not a.email and not a.domena:
            sys.exit("STOP: treba --email ili --domena")
        ok = dodaj_red(R, a.email, a.domena, a.razlog, a.izvor, a.napomena, a.upisao)
        if ok:
            spremi(R)
        print("dodano" if ok else "već na listi, ništa nije dodano"); return
    if a.cmd == "uvezi":
        n = 0
        if a.json:
            for x in json.load(io.open(a.json, encoding="utf-8")):
                e = x.get("email") if isinstance(x, dict) else x
                nap = " ".join(str(x.get(k)) for k in ("lista", "medij", "razlog") if isinstance(x, dict) and x.get(k))
                n += dodaj_red(R, e, "", a.razlog, a.izvor, nap, a.upisao, (x.get("kad") or x.get("upisano") or None) if isinstance(x, dict) else None)
        if a.txt:
            for l in io.open(a.txt, encoding="utf-8"):
                l = l.strip()
                if l and "@" in l:
                    n += dodaj_red(R, l, "", a.razlog, a.izvor, "", a.upisao)
        spremi(R)
        print("uvezeno novih: %d; lista sada ima %d redaka" % (n, len(R)))


if __name__ == "__main__":
    main()
