#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
odjave_iz_poste.py: prođe SVU poštu na mail poslužitelju (sve mape sandučića osim poslane i warmupa, bez vremenske granice)
i izdvoji poruke vanjskih pošiljatelja koje su odjava, odbijanje ili zahtjev da im se više ne piše.
Samo čita. Ispisuje JSON na stdout (popis kandidata) i sažetak na stderr. Radi na poslužitelju uz sken.py u istoj mapi.

    ssh namecheap-portal 'PYTHONIOENCODING=utf-8 python3 ~/wwm_ops_podaci/odjave_iz_poste.py' > out/odjave_namecheap.json

Razredi:
  sigurno   : izričita odjava ili zabrana (STOP, unsubscribe, remove me, ne pišite više, ...) u dijelu koji je napisao pošiljatelj
  vjerojatno: odbijanje bez izričite zabrane (not interested, nismo zainteresirani, ...)
Citirani dio našeg maila se ne gleda (naš tekst sam sadrži riječ »unsubscribe«).
Kandidate razreda sigurno agent smije upisati u out/NE_KONTAKTIRATI.csv; vjerojatne pregledava Matija.
"""
import os, re, sys, json, email, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sken  # body_of, split_quote, hdr, ucitaj_iskljucene
from email.utils import getaddresses, parsedate_to_datetime

ROOT = os.path.expanduser("~/mail")
SIGURNO = re.compile(
    r"\b(unsubscribe( me)?|remove (me|us|my|our)|take (me|us) off|stop (emailing|sending|contacting|writing)|do not (contact|email|write)|don'?t (contact|email|write)|"
    r"no (more|further) (emails?|messages?|contact)|opt[- ]?out|delete (my|our) (data|address|e-?mail)|gdpr|"
    r"cancell?a(temi|teci|re il mio)|rimuov(ete|i|ere)|non (scrivete|contattate|inviate)|togliete|disiscri|"
    r"d[ée]sabonn|d[ée]sinscri|ne (plus|pas) (nous |me )?(contacter|[ée]crire|envoyer)|retirez|supprim(ez|er) (mon|notre)|"
    r"dar(me|nos)? de baja|no (nos |me )?(env[ií]en?|escriban?|contacten?)|elimin(en|ar) (mi|nuestro)|borr(en|ar) (mi|nuestro)|"
    r"abmelden|austragen|keine (weiteren )?(e-?mails?|nachrichten|werbung)|nicht mehr (kontaktieren|schreiben|anschreiben)|l[öo]schen sie|"
    r"uitschrijven|afmelden|geen (verdere )?(e-?mails?|berichten)|niet meer (mailen|contacteren)|"
    r"odhl[áa]sit|neps[áa]t|nepi[šs]te|nezas[íi]lejte|vymazat|"
    r"odjav(a|ite|iti)|ne (pi[šs]ite|[šs]aljite|kontaktirajte)|izbri[šs]ite|uklonite|"
    r"descadastr|remov(a|am|er) (o meu|o nosso)|n[ãa]o (enviem|contactem|escrevam)|cancelar (a )?subscri|"
    r"leiratkoz|ne k[üu]ldj|wypisa[ćc]|nie (pisz|wysy[łl]a)|avregistrer|afmeld|avsluta|poista)\w*", re.I)
STOP_SAM = re.compile(r"^\s*(stop|unsubscribe|remove|no|nein|non|basta|baja|odjava)\s*[.!]*\s*$", re.I | re.M)
VJEROJATNO = re.compile(
    r"\b(not interested|no interest|no thank|not (a )?(good )?fit|we (are|'re) not|"
    r"non (siamo|sono) interessat|non (ci )?interessa|pas int[ée]ress[ée]|ne sommes pas|no (estamos|estoy) interesad|no nos interesa|"
    r"kein interesse|nicht interessiert|geen interesse|niet ge[ïi]nteresseerd|nem[áa]me z[áa]jem|nemamo interes|nismo zainteresiran|"
    r"n[ãa]o (temos|tenho) interesse|nie jeste[śs]my zainteresowan|ikke interessert|inte intresserad|spam)\w*", re.I)


def main():
    isk = sken.ucitaj_iskljucene(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sken_iskljuci.txt"))
    domene = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)) and "." in d and not d.startswith(".") and not d.startswith("dovecot"))
    nase = set(domene); out = []; n = 0; t0 = time.time()
    for dom in domene:
        if dom in isk:
            continue
        dp = os.path.join(ROOT, dom)
        for user in sorted(os.listdir(dp)):
            up = os.path.join(dp, user)
            if not os.path.isdir(up) or user.startswith(".") or user in ("new", "cur", "tmp") or user.lower() == "dmarc":
                continue
            mape = [up] + [os.path.join(up, m) for m in os.listdir(up) if m.startswith(".") and os.path.isdir(os.path.join(up, m))
                           and m.lower() not in (".sent", ".snovio", ".drafts", ".trash", ".spam", ".junk")]
            for mp in mape:
                for sub in ("new", "cur"):
                    dd = os.path.join(mp, sub)
                    if not os.path.isdir(dd):
                        continue
                    for fn in os.listdir(dd):
                        n += 1
                        try:
                            with open(os.path.join(dd, fn), "rb") as fh:
                                m = email.message_from_binary_file(fh)
                        except Exception:
                            continue
                        frm = sken.hdr(m, "From"); adr = (getaddresses([frm]) or [("", "")])[0]
                        fa = adr[1].lower()
                        if not fa or fa.split("@")[-1] in nase or re.search(r"mailer-daemon|postmaster|no-?reply|dmarc", fa):
                            continue
                        subj = re.sub(r"\s+", " ", sken.hdr(m, "Subject")).strip()
                        if subj.startswith("[WRM]") or subj.startswith("***SPAM***"):
                            continue
                        iznad, ispod = sken.split_quote(sken.body_of(m))
                        njihovo = (iznad + "\n" + ispod)[:3000]
                        razred = None; fraza = ""
                        ms = SIGURNO.search(njihovo) or STOP_SAM.search(njihovo[:200]) or (SIGURNO.search(subj) if not re.match(r"\s*(re|aw|r|rif|sv|odp)\s*:", subj, re.I) else None)
                        if ms:
                            razred = "sigurno"; fraza = ms.group(0)
                        else:
                            mv = VJEROJATNO.search(njihovo)
                            if mv:
                                razred = "vjerojatno"; fraza = mv.group(0)
                        if not razred:
                            continue
                        try:
                            kad = parsedate_to_datetime(m.get("Date")).strftime("%Y-%m-%d")
                        except Exception:
                            kad = ""
                        out.append(dict(email=fa, ime=adr[0], kad=kad, box="%s/%s" % (dom, user), mapa=os.path.basename(mp) if mp != up else "INBOX",
                                        predmet=subj[:140], razred=razred, fraza=fraza[:60], tekst=re.sub(r"\s+", " ", njihovo)[:500]))
    # jedna adresa jednom: sigurno pobjeđuje, pa najstariji datum
    naj = {}
    for r in sorted(out, key=lambda r: (r["razred"] != "sigurno", r["kad"])):
        naj.setdefault(r["email"], r)
    L = sorted(naj.values(), key=lambda r: (r["razred"], r["kad"]))
    json.dump(L, sys.stdout, ensure_ascii=False, indent=1)
    sys.stderr.write("pregledano poruka %d u %.0f s; kandidata %d (adresa %d): sigurno %d, vjerojatno %d\n"
                     % (n, time.time() - t0, len(out), len(L), sum(1 for r in L if r["razred"] == "sigurno"), sum(1 for r in L if r["razred"] == "vjerojatno")))


if __name__ == "__main__":
    main()
