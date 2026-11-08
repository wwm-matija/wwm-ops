#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kanon_kratki.py: iz velikog kanona (SUSTAV_RADA.md, 1,2 MB) izvuče zadnjih N radnih paketa
u kratku datoteku KANON_KRATKI.md koju agent s malim kontekstom može pročitati na početku posla.

Samo čita kanon. Piše isključivo KANON_KRATKI.md (u korijenu wwm-ops).

Upotreba (na Hetzneru, iz /root/wwm_ops):
    python3 alati/kanon_kratki.py                 # zadnjih 30 paketa -> KANON_KRATKI.md
    python3 alati/kanon_kratki.py --n 50
    python3 alati/kanon_kratki.py --kanon /putanja/SUSTAV_RADA.md --izlaz /putanja/KANON_KRATKI.md

Oblik reda paketa u kanonu (6 stupaca, najnoviji red je najviše u tablici):
    | 402 | **NASLOV** (datum; vlasnik: »citat«) <!-- BILJEG --> | tijelo | POUKE: ... OTVORENO: ... | 5.11.2026. | status |
"""
import argparse, io, os, re, sys, time

KANON_ZADANO = "/root/vino_world/SUSTAV_RADA.md"
OVDJE = os.path.dirname(os.path.abspath(__file__))
IZLAZ_ZADANO = os.path.join(os.path.dirname(OVDJE), "KANON_KRATKI.md")

RED_RE = re.compile(r"^\| (\d+) \| \*\*")
DATUM_RE = re.compile(r"^\d{1,2}\.\s?\d{1,2}\.\s?\d{4}\.?")
NASLOV_RE = re.compile(r"^\*\*(.+?)\*\*(.*)$", re.S)


def paketi(tekst):
    """Vrati popis rječnika za svaki red paketa: `| N | **NASLOV** ... |`.

    Stupci se dijele na ' | ', ali tekst paketa zna sadržavati okomite crte (npr. `python | cut`),
    pa se datum i status traže s desne strane: zadnja ćelija koja izgleda kao datum je datum,
    sve iza nje je status, ćelija prije je pouke/otvoreno, sve između naslova i toga je tijelo.
    Stariji redovi s manje stupaca prolaze s praznim datumom/statusom.
    """
    out = []
    for br, linija in enumerate(tekst.splitlines(), 1):
        if not RED_RE.match(linija):
            continue
        celije = [c.strip() for c in linija.strip().strip("|").split(" | ")]
        if len(celije) < 2:
            continue
        n = int(celije[0])
        m = NASLOV_RE.match(celije[1])
        if not m:
            continue
        naslov, ostatak_naslova = m.group(1), m.group(2)
        ostatak_celije = celije[2:]
        datum, status = "", ""
        i_dat = -1
        for i in range(len(ostatak_celije) - 1, -1, -1):
            if DATUM_RE.match(ostatak_celije[i]):
                i_dat = i
                break
        if i_dat >= 0:
            # novi oblik (od t.388): ... | pouke+otvoreno | datum | status |
            datum = ostatak_celije[i_dat]
            status = " | ".join(ostatak_celije[i_dat + 1:])
            ostalo = " | ".join(ostatak_celije[:i_dat])
        else:
            # stariji oblik: datum je u zagradi uz naslov, nema zasebnih stupaca
            ostalo = " | ".join(ostatak_celije)
            md = re.search(r"\(?\s*(\d{1,2}\.\s?\d{1,2}\.\s?\d{4}\.?)", ostatak_naslova)
            if md:
                datum = md.group(1)
        # tijelo / pouke / otvoreno po biljezima u tekstu, ne po stupcima (tekst zna imati |)
        tijelo, pouke, otv = ostalo, "", ""
        if "POUKE:" in ostalo:
            tijelo, pouke = ostalo.split("POUKE:", 1)
        elif "OTVORENO:" in ostalo:
            tijelo, otv = ostalo.split("OTVORENO:", 1)
        if "OTVORENO:" in pouke:
            pouke, otv = pouke.split("OTVORENO:", 1)
        tijelo = tijelo.strip(" |")
        pouke = pouke.strip(" |*")
        otv = otv.strip(" |*")
        biljezi = re.findall(r"<!--\s*(.*?)\s*-->", ostatak_naslova)
        ostatak = re.sub(r"<!--.*?-->", "", ostatak_naslova).strip()
        out.append(dict(n=n, linija=br, naslov=naslov.strip(), uz_naslov=ostatak,
                        biljezi=biljezi, tijelo=tijelo.strip(), pouke=pouke, otvoreno=otv.strip(),
                        datum=datum.strip(), status=status.strip()))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kanon", default=KANON_ZADANO)
    ap.add_argument("--izlaz", default=IZLAZ_ZADANO)
    ap.add_argument("--n", type=int, default=30, help="koliko zadnjih paketa (zadano 30)")
    ap.add_argument("--s-tijelom", action="store_true", help="uključi i puno tijelo paketa (dulje)")
    a = ap.parse_args()

    if not os.path.exists(a.kanon):
        sys.exit("STOP: nema kanona na %s" % a.kanon)
    tekst = io.open(a.kanon, encoding="utf-8").read()
    svi = paketi(tekst)
    if not svi:
        sys.exit("STOP: u kanonu nisam našao nijedan red paketa (oblik se promijenio?)")
    svi.sort(key=lambda p: p["n"], reverse=True)
    zadnji = svi[: a.n]

    L = []
    L.append("# KANON KRATKI")
    L.append("")
    L.append("Sažetak zadnjih %d radnih paketa iz `%s` (ukupno paketa: %d, najnoviji t.%d). "
             "Napravio `alati/kanon_kratki.py` %s. Ovo je izvod, ne izvor: kod neslaganja vrijedi veliki kanon."
             % (len(zadnji), a.kanon, len(svi), svi[0]["n"], time.strftime("%d.%m.%Y. %H:%M UTC", time.gmtime())))
    L.append("")
    L.append("Čitaj odozgo: najnoviji paket je prvi. Za svaki: što je napravljeno (naslov), pouke, što je ostalo otvoreno.")
    L.append("")
    for p in zadnji:
        L.append("## t.%d · %s · %s" % (p["n"], p["datum"], p["status"] or "bez statusa"))
        L.append("")
        L.append("**%s**" % p["naslov"])
        if p["uz_naslov"]:
            L.append("")
            L.append(p["uz_naslov"])
        if p["biljezi"]:
            L.append("")
            L.append("Biljezi: " + ", ".join("`%s`" % b for b in p["biljezi"]))
        if a.s_tijelom and p["tijelo"]:
            L.append("")
            L.append("Što: " + p["tijelo"])
        if p["pouke"]:
            L.append("")
            L.append("Pouke: " + p["pouke"])
        if p["otvoreno"]:
            L.append("")
            L.append("Otvoreno: " + p["otvoreno"])
        L.append("")
    izlaz = "\n".join(L) + "\n"
    io.open(a.izlaz, "w", encoding="utf-8", newline="\n").write(izlaz)
    print("KANON_KRATKI.md: %d paketa (t.%d do t.%d), %d znakova -> %s"
          % (len(zadnji), zadnji[-1]["n"], zadnji[0]["n"], len(izlaz), a.izlaz))


if __name__ == "__main__":
    main()
