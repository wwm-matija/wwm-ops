#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crne_liste.py: jesu li naše domene i IP-ovi slanja na crnim listama. Samo DNS upiti, ništa ne šalje i ne mijenja.
Preuzeto iz spam_nadzor_1710.py (17.10.2026.), prošireno 9.11.2026. domenama Mailjeta i novih pošiljatelja.

    python alati/crne_liste.py                 # jedna provjera, ispis; izlaz 1 ako je išta na listi
    python alati/crne_liste.py --petlja 30     # provjera svakih 30 minuta, do 72 h; svaki krug u out/crne_liste.log

Liste: domene na Spamhaus DBL, SURBL, URIBL; IP-ovi na Spamhaus ZEN, Barracuda, SpamCop, UCEPROTECT-1, PSBL, Mailspike.
»nepoznato« = lista je odbila upit (javni DNS poslužitelj); tada ponovi s drugog stroja (laptop i Hetzner).
Pravilo (Matija 9.11.2026.): prije svakog paketa slanja i tijekom slanja; na prvi nalaz slanje staje i javlja se Matiji.
"""
import io, os, socket, sys, time
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "crne_liste.log")
IPS = ["64.204.250.74", "66.29.141.138", "66.29.141.143"]          # HostArmada, Namecheap (dva)
IPBL = ["zen.spamhaus.org", "b.barracudacentral.org", "bl.spamcop.net", "dnsbl-1.uceprotect.net", "psbl.surriel.com", "bl.mailspike.net"]
DOMS = ["worldwinerymap.com", "prvoiceglobal.com",
        "021news.info", "031news.info", "051news.info", "1brand.site", "brand365.space", "pr-voice.info", "communiquepresse.eu", "mediaeco.eu",
        "elaltavoz.eu", "elaltavoz.lat", "omnialuxe.store", "ohlas.eu", "antilalos.eu",
        "worldwinerymap.site", "worldwinerymap.store", "worldwinerymap.shop", "worldwinerymap.space", "worldwinerymap.lat", "worldwinerymap.org",
        "worldwinerymap.eu", "worldwinerymap.click",
        "winerymap.site", "winerymapping.online", "winerymapping.site", "worldwinerymapping.online", "worldwinerymapping.site", "worldwinerymaps.online"]
DBL = ["dbl.spamhaus.org", "multi.surbl.org", "multi.uribl.com"]


def q(name):
    try: return socket.gethostbyname(name)
    except socket.gaierror: return None
    except Exception: return "ERR"


def provjera():
    """Vrati (nalazi, nepoznato, radi): nalazi = popis »X na listi=odgovor«."""
    radi = q("2.0.0.127.zen.spamhaus.org") is not None or q("2.0.0.127.bl.spamcop.net") is not None or q("test.multi.surbl.org") is not None
    nal = []; nep = []
    for ip in IPS:
        rev = ".".join(reversed(ip.split(".")))
        for bl in IPBL:
            a = q(rev + "." + bl)
            if a == "ERR" or (a and a.startswith("127.255.255")): nep.append(ip + "@" + bl)
            elif a: nal.append("%s na %s=%s" % (ip, bl, a))
    for d in DOMS:
        for bl in DBL:
            a = q(d + "." + bl)
            if a == "ERR" or (a and (a.startswith("127.255.255") or (a == "127.0.0.1" and "uribl" in bl))): nep.append(d + "@" + bl)
            elif a: nal.append("%s na %s=%s" % (d, bl, a))
    return nal, nep, radi


def krug():
    nal, nep, radi = provjera()
    liste_nep = sorted({x.split("@")[1] for x in nep})
    s = "%s | provjereno %d domena × %d + %d IP × %d | NALAZI: %s | nepoznato %d %s%s" % (
        time.strftime("%Y-%m-%d %H:%M:%S"), len(DOMS), len(DBL), len(IPS), len(IPBL), "; ".join(nal) if nal else "NIŠTA", len(nep), liste_nep if nep else "",
        "" if radi else " | UPOZORENJE: kontrolni upit ne prolazi, DNS možda ne radi")
    print(s, flush=True)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with io.open(LOG, "a", encoding="utf-8") as f: f.write(socket.gethostname() + " | " + s + "\n")
    return nal


if __name__ == "__main__":
    if "--petlja" in sys.argv:
        korak = int(sys.argv[sys.argv.index("--petlja") + 1]) * 60; t0 = time.time()
        while time.time() - t0 < 72 * 3600:
            if krug(): print("ALARM: nalaz na crnoj listi, slanje treba stati", flush=True)
            time.sleep(korak)
    else:
        sys.exit(1 if krug() else 0)
