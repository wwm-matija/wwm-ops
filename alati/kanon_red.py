#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kanon_red.py: upiše JEDAN novi red (radni paket) u veliki kanon SUSTAV_RADA.md, bez da agent otvara datoteku.

Pravila koja alat sam drži:
  - broj paketa = najveći postojeći + 1
  - red ide IZNAD dosadašnjeg najnovijeg reda (tablica je najnoviji-gore)
  - biljeg <!-- BILJEG --> mora biti jedinstven; ako već postoji, STOP (red je već upisan)
  - kopija kanona u kopije/<datum>/SUSTAV_RADA.md.prije-kanon-tNNN-<vrijeme> PRIJE pisanja
  - bez --pisi samo pokazuje što bi upisao (proba)
  - poslije upisa obnovi KANON_KRATKI.md (alati/kanon_kratki.py), osim uz --bez-kratkog

Upotreba (iz /root/wwm_ops na Hetzneru):
    python3 alati/kanon_red.py --iz red.json            # proba
    python3 alati/kanon_red.py --iz red.json --pisi     # upis

red.json (UTF-8):
    {
      "naslov":   "MAILOVI 8.11.: 3 ODGOVORA VINARIMA, 1 MICANJE S KARTE",
      "datum":    "8.11.2026.",                 # ako nema, danas
      "citat":    "šalji 1 i 2",                # Matijina riječ (neobavezno)
      "biljeg":   "MAILOVI-2026-11-08",         # ako nema, gradi se iz datuma i naslova
      "tijelo":   "što je napravljeno, s putanjama i brojkama",
      "pouke":    "što smo naučili",
      "otvoreno": "što čeka Matiju ili sljedeći korak",
      "status":   "bez objave"                  # npr. objavljeno #115 / bez objave
    }
Polja se mogu dati i kao argumenti (--naslov, --tijelo, ...); argument pobjeđuje JSON.
Znak | u tekstu zamjenjuje se s /, prijelomi redaka razmakom (red kanona je jedna linija).
"""
import argparse, io, json, os, re, shutil, subprocess, sys, time

KANON_ZADANO = "/root/vino_world/SUSTAV_RADA.md"
OVDJE = os.path.dirname(os.path.abspath(__file__))
RED_RE = re.compile(r"^\| (\d+) \| \*\*")


def ocisti(s):
    s = (s or "").replace("\r", " ").replace("\n", " ").replace("|", "/")
    return re.sub(r"\s+", " ", s).strip()


def slug(s):
    s = s.upper()
    s = s.replace("Č", "C").replace("Ć", "C").replace("Š", "S").replace("Ž", "Z").replace("Đ", "D")
    s = re.sub(r"[^A-Z0-9]+", "-", s).strip("-")
    return s[:40].rstrip("-")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--iz", help="JSON datoteka s poljima reda")
    for k in ("naslov", "datum", "citat", "biljeg", "tijelo", "pouke", "otvoreno", "status"):
        ap.add_argument("--" + k)
    ap.add_argument("--kanon", default=KANON_ZADANO)
    ap.add_argument("--pisi", action="store_true", help="stvarno upiši (bez toga je proba)")
    ap.add_argument("--bez-kratkog", action="store_true", help="ne obnavljaj KANON_KRATKI.md poslije upisa")
    a = ap.parse_args()

    polja = {}
    if a.iz:
        polja = json.load(io.open(a.iz, encoding="utf-8"))
    for k in ("naslov", "datum", "citat", "biljeg", "tijelo", "pouke", "otvoreno", "status"):
        v = getattr(a, k)
        if v is not None:
            polja[k] = v
    for k in ("naslov", "tijelo", "pouke", "otvoreno"):
        if not ocisti(polja.get(k)):
            sys.exit("STOP: polje '%s' je prazno; red bez toga ne ide u kanon" % k)
    datum = ocisti(polja.get("datum")) or time.strftime("%-d.%-m.%Y.")
    status = ocisti(polja.get("status")) or "bez objave"
    biljeg = ocisti(polja.get("biljeg")) or "%s-%s" % (slug(polja["naslov"])[:24], time.strftime("%Y-%m-%d"))
    citat = ocisti(polja.get("citat"))

    if not os.path.exists(a.kanon):
        sys.exit("STOP: nema kanona na %s" % a.kanon)
    s = io.open(a.kanon, encoding="utf-8").read()
    if "<!-- %s -->" % biljeg in s:
        sys.exit("STOP: biljeg %s već postoji u kanonu; red je već upisan" % biljeg)

    linije = s.split("\n")
    najveci, idx = -1, -1
    for i, l in enumerate(linije):
        m = RED_RE.match(l)
        if m:
            n = int(m.group(1))
            if n > najveci:
                najveci, idx = n, i
    if idx < 0:
        sys.exit("STOP: nisam našao nijedan red paketa u kanonu")
    novi_n = najveci + 1

    glava = "**%s** (%s%s) <!-- %s -->" % (ocisti(polja["naslov"]), datum,
                                            ("; vlasnik: »%s«" % citat) if citat else "", biljeg)
    pouke_otv = "POUKE: %s OTVORENO: %s" % (ocisti(polja["pouke"]), ocisti(polja["otvoreno"]))
    red = "| %d | %s | %s | %s | %s | %s |" % (novi_n, glava, ocisti(polja["tijelo"]), pouke_otv, datum, status)

    print("kanon: %s (%d znakova, %d redaka)" % (a.kanon, len(s), len(linije)))
    print("najnoviji postojeći: t.%d (linija %d); novi red: t.%d, %d znakova, biljeg %s"
          % (najveci, idx + 1, novi_n, len(red), biljeg))
    print("--- red:")
    print(red[:600] + (" …" if len(red) > 600 else ""))
    if not a.pisi:
        print("(proba, ništa nije upisano; dodaj --pisi)")
        return

    kop_dir = os.path.join(os.path.dirname(a.kanon), "kopije", time.strftime("%Y-%m-%d"))
    os.makedirs(kop_dir, exist_ok=True)
    kop = os.path.join(kop_dir, "SUSTAV_RADA.md.prije-kanon-t%d-%s" % (novi_n, time.strftime("%Y%m%d%H%M%S")))
    shutil.copy2(a.kanon, kop)
    if os.path.getsize(kop) != len(s.encode("utf-8")):
        sys.exit("STOP: kopija nije iste veličine kao izvor, ne pišem")

    linije.insert(idx, red)
    novo = "\n".join(linije)
    assert len(novo) == len(s) + len(red) + 1, "duljina ne odgovara, ne pišem"
    io.open(a.kanon, "w", encoding="utf-8", newline="\n").write(novo)

    provjera = io.open(a.kanon, encoding="utf-8").read()
    if provjera.count("<!-- %s -->" % biljeg) != 1 or not provjera.startswith(s[:200]):
        sys.exit("STOP: provjera nakon pisanja nije prošla; vrati kopiju %s" % kop)
    print("upisano t.%d; kopija %s" % (novi_n, kop))

    if not a.bez_kratkog:
        kratki = os.path.join(OVDJE, "kanon_kratki.py")
        r = subprocess.run([sys.executable, kratki, "--kanon", a.kanon], capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())


if __name__ == "__main__":
    main()
