# -*- coding: utf-8 -*-
"""Stanje slanja vinarijama: Mailjet kampanje i Snov kampanje. SAMO ČITA, ništa ne šalje i ne mijenja.

python alati/slanje_stanje.py                      Mailjet od 9.11.2026. + Snov kampanje iz out/snov_kampanje_u_tijeku.txt
python alati/slanje_stanje.py --od 2026-11-09      Mailjet kampanje poslane od tog dana
python alati/slanje_stanje.py --snov 3214757,3214758   Snov kampanje po ID-u (ili --snov-popis datoteka, prvi stupac = ID)
python alati/slanje_stanje.py --bez-snov | --bez-mailjet

Ispis: tablica po kampanji (poslano, bounce, blokirano, odjave, spam; Snov: poslano, odgovora koje Snov vidi).
Zapis: out/slanje_stanje_<datum>.json (ne ide u git).
Ključevi: MAILJET_API_KEY i MAILJET_SECRET_KEY iz .env.mailjet, SNOV_CLIENT_ID i SNOV_CLIENT_SECRET iz .env.bevanda
(putanje: WWM_ENV_MAILJET, WWM_ENV_SNOV ili zadano C:/Users/world/wwm/). Ključevi se nikad ne ispisuju.
Snov: pauza 1,1 s po pozivu, 429 = čekanje 310 s; nikad dvije Snov petlje paralelno.
Odgovori koje Snov broji nisu mjerodavni (promaši većinu); pravi pregled odgovora je čitanje sandučića (alati/posta_popis.py, alati/sken.py), bez pitanja.
"""
import argparse, datetime, io, json, os, sys, time
import requests

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out")
ENV_MJ = os.environ.get("WWM_ENV_MAILJET", "C:/Users/world/wwm/.env.mailjet")
ENV_SNOV = os.environ.get("WWM_ENV_SNOV", "C:/Users/world/wwm/.env.bevanda")
POPIS_SNOV = os.path.join(OUT, "snov_kampanje_u_tijeku.txt")


def env(put, var):
    for l in io.open(put, encoding="utf-8"):
        if l.startswith(var + "="):
            return l.split("=", 1)[1].strip().strip('"')
    raise SystemExit("nema %s u %s" % (var, put))


# ---------- Mailjet ----------
def mj(auth, put, **par):
    for pok in range(3):
        try:
            r = requests.get("https://api.mailjet.com/v3/REST/" + put, auth=auth, params=par, timeout=60)
            if r.status_code == 200:
                return r.json().get("Data", [])
            print("  Mailjet %s: %s %s" % (put, r.status_code, r.text[:150]))
            return []
        except requests.RequestException as e:
            time.sleep(5)
    return []


def mailjet(od):
    auth = (env(ENV_MJ, "MAILJET_API_KEY"), env(ENV_MJ, "MAILJET_SECRET_KEY"))
    kamp = mj(auth, "campaign", FromTS=od + "T00:00:00Z", Limit=200)
    rez = []
    for k in kamp:
        s = mj(auth, "statcounters", SourceId=k["ID"], CounterSource="Campaign", CounterTiming="Message", CounterResolution="Lifetime")
        s = s[0] if s else {}
        rez.append({
            "kampanja": k["ID"], "nacrt": k.get("NewsLetterID"), "predmet": k.get("Subject"), "od": k.get("FromEmail"),
            "pocetak": k.get("SendStartAt"), "status": k.get("Status"),
            "ukupno": s.get("Total"), "poslano": s.get("MessageSentCount"), "u_redu": s.get("MessageQueuedCount"),
            "odgodjeno": s.get("MessageDeferredCount"), "tvrdi_bounce": s.get("MessageHardBouncedCount"),
            "meki_bounce": s.get("MessageSoftBouncedCount"), "blokirano": s.get("MessageBlockedCount"),
            "spam": s.get("MessageSpamCount"), "odjave": s.get("MessageUnsubscribedCount"),
            "otvoreno": s.get("MessageOpenedCount"), "klik": s.get("MessageClickedCount"),
        })
    return rez


# ---------- Snov ----------
class Snov:
    B = "https://api.snov.io"

    def __init__(self):
        self.cid, self.sec = env(ENV_SNOV, "SNOV_CLIENT_ID"), env(ENV_SNOV, "SNOV_CLIENT_SECRET")
        self.tok, self.t = None, 0
        self.ses = requests.Session()

    def token(self):
        if not self.tok or time.time() - self.t > 2400:
            r = self.ses.post(self.B + "/v1/oauth/access_token", data={"grant_type": "client_credentials", "client_id": self.cid, "client_secret": self.sec}, timeout=30)
            self.tok, self.t = r.json()["access_token"], time.time()
            time.sleep(1.1)
        return self.tok

    def get(self, put, **par):
        return self._zovi("GET", put, params=par)

    def post(self, put, data=None, ponovi=True):
        """ponovi=False: kod mrežne greške NE ponavlja (POST koji je možda stigao do Snova ne smije se poslati dvaput)."""
        return self._zovi("POST", put, data=data, ponovi=ponovi)

    def _zovi(self, m, put, ponovi=True, **k):
        for pok in range(4):
            try:
                r = self.ses.request(m, self.B + put, headers={"Authorization": "Bearer " + self.token()}, timeout=90, **k)
            except requests.RequestException:
                if not ponovi:
                    return 0, {}
                time.sleep(10); continue
            time.sleep(1.1)
            if r.status_code == 429:
                print("  Snov 429, čekam 310 s"); time.sleep(310); continue
            try:
                return r.status_code, r.json()
            except ValueError:
                return r.status_code, {"tekst": r.text[:200]}
        return 0, {}


def snov_ids(args):
    if args.snov:
        return [int(x) for x in args.snov.split(",") if x.strip()]
    put = args.snov_popis or POPIS_SNOV
    if not os.path.exists(put):
        print("nema popisa Snov kampanja (%s); zadaj --snov ID,ID ili --snov-popis datoteka" % put)
        return []
    ids = []
    for l in io.open(put, encoding="utf-8"):
        l = l.strip()
        if l and not l.startswith("#") and l.split()[0].isdigit():
            ids.append(int(l.split()[0]))
    return ids


def snov(ids):
    s = Snov(); rez = []
    for cid in ids:
        # /v2/campaigns/{id} -> {"data": {"id", "status", "title", ...}}; /v1/emails-sent i get-emails-replies vraćaju POPIS
        st, k = s.get("/v2/campaigns/%d" % cid)
        k = (k or {}).get("data") or {} if isinstance(k, dict) else {}
        st, poslano = s.get("/v1/emails-sent", campaignId=cid)
        poslano = poslano if isinstance(poslano, list) else []
        st, odg = s.get("/v1/get-emails-replies", campaignId=cid)
        odg = odg if isinstance(odg, list) else []
        dani = sorted({(x.get("sentDate") or "")[:10] for x in poslano if isinstance(x, dict)})
        rez.append({"kampanja": cid, "naziv": k.get("title"), "status": k.get("status"),
                    "poslano": len(poslano), "od": dani[0] if dani else "", "do": dani[-1] if dani else "", "odgovora_snov": len(odg),
                    "poslano_adrese": sorted({(x.get("userEmail") or "").lower() for x in poslano if isinstance(x, dict) and x.get("userEmail")}),
                    "odgovorili_snov": sorted({(x.get("prospectName") or "") + " " + (x.get("visitedAt") or "")[:16] for x in odg if isinstance(x, dict)})})
        print("  Snov %d %-45s %-9s poslano %4d (%s do %s)  odgovora(Snov) %d" % (cid, (rez[-1]["naziv"] or "")[:45], rez[-1]["status"] or "?", len(poslano), rez[-1]["od"][5:], rez[-1]["do"][5:], len(odg)))
    return rez


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--od", default="2026-11-09")
    ap.add_argument("--snov", default="")
    ap.add_argument("--snov-popis", default="")
    ap.add_argument("--bez-snov", action="store_true")
    ap.add_argument("--bez-mailjet", action="store_true")
    a = ap.parse_args()
    sad = datetime.datetime.now(datetime.timezone.utc)
    izl = {"vrijeme_utc": sad.strftime("%Y-%m-%d %H:%M"), "mailjet": [], "snov": []}
    if not a.bez_mailjet:
        print("MAILJET kampanje od %s" % a.od)
        izl["mailjet"] = mailjet(a.od)
        print("%-10s %-40s %6s %6s %6s %6s %6s %5s %5s %6s" % ("kampanja", "predmet", "ukupno", "poslano", "tvrdiB", "mekiB", "blok", "spam", "odj", "otvor"))
        z = {}
        for r in izl["mailjet"]:
            print("%-10s %-40s %6s %6s %6s %6s %6s %5s %5s %6s" % (r["kampanja"], (r["predmet"] or "")[:40], r["ukupno"], r["poslano"], r["tvrdi_bounce"], r["meki_bounce"], r["blokirano"], r["spam"], r["odjave"], r["otvoreno"]))
            for p in ("ukupno", "poslano", "tvrdi_bounce", "meki_bounce", "blokirano", "spam", "odjave", "otvoreno", "klik"):
                z[p] = z.get(p, 0) + (r[p] or 0)
        print("ZBROJ Mailjet:", json.dumps(z, ensure_ascii=False))
    if not a.bez_snov:
        ids = snov_ids(a)
        if ids:
            print("SNOV kampanje (%d)" % len(ids))
            izl["snov"] = snov(ids)
            print("ZBROJ Snov: poslano %d, odgovora koje Snov vidi %d, kampanja završenih %d" % (
                sum(r["poslano"] for r in izl["snov"]), sum(r["odgovora_snov"] for r in izl["snov"]),
                sum(1 for r in izl["snov"] if (r["status"] or "").lower() in ("complete", "completed", "finished"))))
    os.makedirs(OUT, exist_ok=True)
    put = os.path.join(OUT, "slanje_stanje_%s.json" % sad.strftime("%Y-%m-%d"))
    json.dump(izl, io.open(put, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("zapisano", put)


if __name__ == "__main__":
    main()
