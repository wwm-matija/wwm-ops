#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
proba_povrata.py: dokaz da se iz kopija stvarno može vratiti. Vraća kopije na PROBNO mjesto na volumenu,
uspoređuje ih sa živim stanjem i mjeri trajanje. Živo se samo ČITA (baza se otvara mode=ro).

Radi na Hetzneru (python3, modul sqlite3). Piše isključivo u probnu mapu i u izvještaj.

    python3 alati/proba_povrata.py                 # sve tri kopije: dnevna lokalna, off-site Namecheap, tjedna Storage Box
    python3 alati/proba_povrata.py --bez-boxa      # bez skidanja 0,6 GB s Boxa
    python3 alati/proba_povrata.py --ostavi        # ne briši vraćene datoteke na kraju (zadano: briše velike, izvještaj ostaje)

Što provjerava:
  1. dnevna radna baza (kopije/wwm-radno-<dan>.db.gz): raspakira, integrity_check, broj redaka po tablici prema živoj bazi
  2. dnevne fotografije (kopije/wwm-slike-<dan>.tar.gz): raspakira, broj i veličina datoteka prema živom uploads/, md5 uzorka
  3. off-site Namecheap (~/wwm-kopije): današnje dvije datoteke postoje i md5 im je isti kao lokalnima
  4. Storage Box, tjedna cijela baza (wwm/db/wwm_<datum>.db.gz): skida, raspakira, quick_check, broj redaka ključnih tablica prema živoj
  5. Storage Box, izvor sustava (wwm/pipeline/wwm_izvor_<datum>.tar.gz): skida, otvara, broj datoteka, kanon unutra i čitljiv
Izvještaj: <probna mapa>/PROBA_POVRATA_<datum>.md (i ispis).
"""
import argparse, gzip, hashlib, os, random, shutil, sqlite3, subprocess, sys, tarfile, time

A = "/root/wwm_api"
ZIVA = A + "/wwm.db"
KOPIJE = A + "/kopije"
UPLOADS = A + "/uploads"
PROBA_KORIJEN = "/mnt/HC_Volume_106719381/proba_povrata"
BOX_SSH = ["ssh", "-p", "23", "-i", "/root/.ssh/id_ed25519_backupbox", "-o", "BatchMode=yes"]
BOX = "u658155@u658155.your-storagebox.de"
IZV = []


def zapis(s=""):
    print(s, flush=True); IZV.append(s)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def tablice(con):
    return [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]


def broj(con, t):
    try:
        return con.execute('SELECT COUNT(*) FROM "%s"' % t).fetchone()[0]
    except Exception as e:
        return "greška: %s" % str(e)[:60]


def ro(p):
    return sqlite3.connect("file:%s?mode=ro" % p, uri=True, timeout=60)


def raspakiraj_gz(src, dst):
    with gzip.open(src, "rb") as f, open(dst, "wb") as g:
        shutil.copyfileobj(f, g, 1 << 22)


def korak_dnevna_baza(D, dan):
    zapis("## 1. Dnevna radna baza (lokalna kopija)")
    src = "%s/wwm-radno-%s.db.gz" % (KOPIJE, dan)
    if not os.path.exists(src):
        zapis("- **PAD**: nema %s" % src); return False
    t0 = time.time(); dst = D + "/wwm-radno.db"; raspakiraj_gz(src, dst)
    k = sqlite3.connect(dst); ic = k.execute("PRAGMA integrity_check").fetchone()[0]
    z = ro(ZIVA); tz = set(tablice(z)); ok = (ic == "ok"); red = []
    for t in tablice(k):
        nk = broj(k, t); nz = broj(z, t) if t in tz else "nema u živoj"
        razl = (nz - nk) if isinstance(nk, int) and isinstance(nz, int) else "?"
        red.append((t, nk, nz, razl))
        if isinstance(razl, int) and razl < 0 and abs(razl) > max(5, nk * 0.02):
            ok = False   # kopija ima znatno VIŠE redaka od žive: nešto je obrisano ili je kopija kriva
    k.close(); z.close()
    zapis("- datoteka %s (%d B), raspakirano %d B, integrity_check: **%s**, trajanje %.1f s" % (os.path.basename(src), os.path.getsize(src), os.path.getsize(dst), ic, time.time() - t0))
    zapis("- tablica u kopiji: %d; redaka ukupno u kopiji %d" % (len(red), sum(r[1] for r in red if isinstance(r[1], int))))
    zapis(""); zapis("| tablica | kopija 03:40 | živo sada | razlika |"); zapis("|---|---|---|---|")
    for t, nk, nz, razl in red:
        zapis("| %s | %s | %s | %s |" % (t, nk, nz, razl))
    zapis(""); return ok


def korak_slike(D, dan):
    zapis("## 2. Fotografije (lokalna kopija)")
    src = "%s/wwm-slike-%s.tar.gz" % (KOPIJE, dan)
    if not os.path.exists(src):
        zapis("- **PAD**: nema %s" % src); return False
    t0 = time.time(); dst = D + "/slike"; os.makedirs(dst, exist_ok=True)
    with tarfile.open(src) as t:
        t.extractall(dst)
    vr = []
    for kor, _, dat in os.walk(dst):
        for d in dat:
            vr.append(os.path.join(kor, d))
    zi = []
    for kor, _, dat in os.walk(UPLOADS):
        for d in dat:
            zi.append(os.path.join(kor, d))
    vel_v = sum(os.path.getsize(p) for p in vr); vel_z = sum(os.path.getsize(p) for p in zi)
    # md5 uzorka: iste relativne putanje
    def rel(p, baza):
        r = os.path.relpath(p, baza)
        return r[len("uploads/"):] if r.startswith("uploads/") else r
    mapa_z = {rel(p, UPLOADS): p for p in zi}; mapa_v = {rel(p, dst): p for p in vr}
    zajednicke = sorted(set(mapa_z) & set(mapa_v)); random.seed(1); uz = random.sample(zajednicke, min(40, len(zajednicke)))
    isti = sum(1 for r in uz if md5(mapa_z[r]) == md5(mapa_v[r]))
    zapis("- datoteka %s (%d B), vraćeno %d datoteka (%d B); živo uploads: %d datoteka (%d B); trajanje %.1f s" % (os.path.basename(src), os.path.getsize(src), len(vr), vel_v, len(zi), vel_z, time.time() - t0))
    zapis("- zajedničkih putanja %d; u živom a ne u kopiji %d (dodano poslije 03:40 ili nije u kopiji); u kopiji a ne u živom %d" % (len(zajednicke), len(set(mapa_z) - set(mapa_v)), len(set(mapa_v) - set(mapa_z))))
    zapis("- md5 uzorka: %d od %d isto" % (isti, len(uz))); zapis("")
    return len(vr) > 0 and isti == len(uz)


def korak_namecheap(dan):
    zapis("## 3. Off-site kopija na Namecheapu")
    imena = ["wwm-radno-%s.db.gz" % dan, "wwm-slike-%s.tar.gz" % dan]
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=30", "namecheap-portal",
                        "cd ~/wwm-kopije && md5sum " + " ".join(imena)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    dalj = {l.split()[1]: l.split()[0] for l in r.stdout.splitlines() if len(l.split()) == 2}
    ok = True
    for i in imena:
        lok = md5(KOPIJE + "/" + i) if os.path.exists(KOPIJE + "/" + i) else None
        isto = lok is not None and dalj.get(i) == lok
        ok = ok and isto
        zapis("- %s: %s" % (i, "isti md5 na Namecheapu" if isto else "**PAD** (lokalno %s, daljinski %s)" % ("ima" if lok else "nema", "ima drugačiji" if i in dalj else "nema")))
    zapis(""); return ok


def box_ls(put):
    r = subprocess.run(BOX_SSH + [BOX, "ls " + put], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return sorted(l.strip() for l in r.stdout.splitlines() if l.strip())


def box_skini(put, dst):
    r = subprocess.run(["rsync", "-e", " ".join(BOX_SSH), "%s:%s" % (BOX, put), dst], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return r.returncode == 0, r.stderr.strip()[:200]


def korak_box_baza(D):
    zapis("## 4. Storage Box: tjedna cijela baza")
    L = [x for x in box_ls("wwm/db") if x.startswith("wwm_") and x.endswith(".db.gz")]
    if not L:
        zapis("- **PAD**: na Boxu nema wwm/db/wwm_*.db.gz"); return False
    ime = L[-1]; t0 = time.time(); gz = D + "/" + ime
    ok, por = box_skini("wwm/db/" + ime, gz)
    if not ok:
        zapis("- **PAD**: skidanje %s nije uspjelo: %s" % (ime, por)); return False
    t1 = time.time(); db = D + "/wwm_box.db"; raspakiraj_gz(gz, db); t2 = time.time()
    k = sqlite3.connect(db); qc = k.execute("PRAGMA quick_check").fetchone()[0]; t3 = time.time()
    z = ro(ZIVA); tk = tablice(k); tz = set(tablice(z))
    zapis("- %s: skinuto %d B za %.0f s, raspakirano %d B za %.0f s, quick_check: **%s** (%.0f s); kopija na Boxu ukupno %d komada" % (ime, os.path.getsize(gz), t1 - t0, os.path.getsize(db), t2 - t1, qc, t3 - t2, len(L)))
    zapis("- tablica: kopija %d, živo %d; u živoj a ne u kopiji: %s" % (len(tk), len(tz), ", ".join(sorted(tz - set(tk))) or "nema"))
    zapis(""); zapis("| tablica | kopija (%s) | živo sada | razlika |" % ime[4:14]); zapis("|---|---|---|---|")
    dobro = (qc == "ok")
    for t in tk:
        nk = broj(k, t); nz = broj(z, t) if t in tz else "nema u živoj"
        razl = (nz - nk) if isinstance(nk, int) and isinstance(nz, int) else "?"
        if isinstance(nk, int) and nk >= 1000 or isinstance(razl, int) and razl != 0:
            zapis("| %s | %s | %s | %s |" % (t, nk, nz, razl))
    zapis("(prikazane tablice s 1.000+ redaka ili s razlikom)"); zapis("")
    k.close(); z.close()
    return dobro


def korak_box_izvor(D):
    zapis("## 5. Storage Box: izvor sustava (kod, kanon, ledgeri, konfiguracija)")
    L = [x for x in box_ls("wwm/pipeline") if x.startswith("wwm_izvor_")]
    if not L:
        zapis("- **PAD**: na Boxu nema wwm/pipeline/wwm_izvor_*"); return False
    ime = L[-1]; t0 = time.time(); tar = D + "/" + ime
    ok, por = box_skini("wwm/pipeline/" + ime, tar)
    if not ok:
        zapis("- **PAD**: skidanje %s nije uspjelo: %s" % (ime, por)); return False
    with tarfile.open(tar) as t:
        imena = t.getnames()
        kanon = "root/vino_world/SUSTAV_RADA.md"
        ima_kanon = kanon in imena; vel_k = 0
        if ima_kanon:
            t.extract(kanon, D + "/izvor"); vel_k = os.path.getsize(D + "/izvor/" + kanon)
    kljucne = ["root/wwm_api/app.py", "root/vino_world/peci.sh", "etc/nginx/sites-available/wwm_api", "meta/crontab.txt", "root/backup_box.sh"]
    fale = [k for k in kljucne if k not in imena]
    zapis("- %s: %d B, %d datoteka u arhivi, trajanje %.0f s; arhiva na Boxu ukupno %d komada" % (ime, os.path.getsize(tar), len(imena), time.time() - t0, len(L)))
    zapis("- kanon u arhivi: %s (%d B; živi sada %d B)" % ("da" if ima_kanon else "**NE**", vel_k, os.path.getsize("/root/vino_world/SUSTAV_RADA.md")))
    zapis("- ključne datoteke: %s" % ("sve prisutne (%s)" % ", ".join(kljucne) if not fale else "**FALE** " + ", ".join(fale)))
    zapis("- napomena: tajne (.env) NISU ni u jednoj kopiji; drže se ručno izvan servera"); zapis("")
    return ima_kanon and not fale


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bez-boxa", action="store_true"); ap.add_argument("--ostavi", action="store_true")
    a = ap.parse_args()
    dan = time.strftime("%Y-%m-%d"); D = "%s/%s" % (PROBA_KORIJEN, dan); os.makedirs(D, exist_ok=True)
    t0 = time.time()
    zapis("# PROBA POVRATA %s" % dan); zapis("")
    zapis("Probna mapa: `%s`. Živo se samo čita. Pokrenuto %s UTC." % (D, time.strftime("%H:%M", time.gmtime()))); zapis("")
    rez = {}
    rez["1 dnevna baza"] = korak_dnevna_baza(D, dan)
    rez["2 fotografije"] = korak_slike(D, dan)
    rez["3 off-site Namecheap"] = korak_namecheap(dan)
    if not a.bez_boxa:
        rez["4 Box cijela baza"] = korak_box_baza(D)
        rez["5 Box izvor"] = korak_box_izvor(D)
    zapis("## Sažetak"); zapis("")
    for k, v in rez.items():
        zapis("- %s: %s" % (k, "PROŠLO" if v else "**PAD**"))
    zapis("- ukupno trajanje: %.0f s" % (time.time() - t0))
    if not a.ostavi:
        for f in os.listdir(D):
            p = os.path.join(D, f)
            if os.path.isdir(p):
                shutil.rmtree(p)
            elif not f.endswith(".md"):
                os.remove(p)
        zapis("- vraćene datoteke obrisane iz probne mape (ostaje samo izvještaj)")
    izv = "%s/PROBA_POVRATA_%s.md" % (D, dan)
    with open(izv, "w", encoding="utf-8") as f:
        f.write("\n".join(IZV) + "\n")
    print("izvještaj:", izv)
    sys.exit(0 if all(rez.values()) else 1)


if __name__ == "__main__":
    main()
