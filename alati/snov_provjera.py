# -*- coding: utf-8 -*-
"""Snov provjera mail adresa (troši kredite: SAMO na riječ vlasnika, samo adrese koje su prošle lokalne provjere).
Vrti se na laptopu (Snov ključevi u .env.bevanda). Nikad paralelno s drugom Snov petljom.

python alati/snov_provjera.py --ulaz out/lov/NOVI_MAILOVI_2026-11-10.csv --oznaka lov1011 --filtar za_slanje=da --filtar vrsta=vlastita \
    --mx out/lov/mx_domene_2026-11-10.json --salji [--strop 4000] [--donja-granica 100]
python alati/snov_provjera.py --ulaz ... --oznaka lov1011 --pokupi        rezultat -> out/snov_provjera_<oznaka>_rezultat.csv i .json

--salji: POST /v1/add-emails-to-verification po 10 adresa; red pun (»too many emails processing«) = čekanje 90 s; stanje
  out/snov_provjera_<oznaka>.json (nastavljivo, adresa se ne predaje dvaput); svakih 20 poziva čita balans i STAJE ispod
  --donja-granica. Redoslijed: prvo adrese izvan isključenih zemalja (stupac iskljucena_zemlja prazan).
--mx: domene bez MX zapisa (ni A) se ne predaju (kredit na mrtvu domenu je bačen), bilježe se kao »bez_mx«.
--pokupi: POST /v1/get-emails-verification-status po 10; status identifier complete/in_progress, smtpStatus valid/not_valid/unknown,
  isCatchall. Zelena = smtp valid i nije catch-all (isti kriterij kao K1Z »samo zelene«).
Ključevi se ne ispisuju. Ulazni CSV: točka-zarez, stupac mail.
"""
import argparse, collections, csv, datetime, io, json, os, sys, time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slanje_stanje import Snov, OUT


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def balans(s):
    st, d = s.get("/v1/get-balance")
    try:
        return float(((d or {}).get("data") or {}).get("balance"))
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ulaz", required=True); ap.add_argument("--oznaka", required=True)
    ap.add_argument("--filtar", action="append", default=[], help="stupac=vrijednost, više puta")
    ap.add_argument("--mx", default="")
    ap.add_argument("--salji", action="store_true"); ap.add_argument("--pokupi", action="store_true")
    ap.add_argument("--strop", type=int, default=5000); ap.add_argument("--donja-granica", type=float, default=100)
    a = ap.parse_args()
    SF = os.path.join(OUT, "snov_provjera_%s.json" % a.oznaka)
    ST = json.load(io.open(SF, encoding="utf-8")) if os.path.exists(SF) else {"predano": {}, "greske": [], "bez_mx": [], "balans": []}

    def spremi():
        json.dump(ST, io.open(SF + ".tmp", "w", encoding="utf-8"), ensure_ascii=False, indent=0); os.replace(SF + ".tmp", SF)

    R = list(csv.DictReader(io.open(a.ulaz, encoding="utf-8-sig", newline=""), delimiter=";"))
    for f in a.filtar:
        k, v = f.split("=", 1); R = [r for r in R if (r.get(k) or "") == v]
    R.sort(key=lambda r: (r.get("iskljucena_zemlja") == "da", r.get("cc", ""), r["mail"]))
    mx = json.load(io.open(a.mx, encoding="utf-8")) if a.mx else None
    red, bez_mx = [], []
    for r in R:
        m = r["mail"].strip().lower()
        if m in red:
            continue
        if mx is not None and not mx.get(m.split("@")[1]):
            bez_mx.append(m); continue
        red.append(m)
    cc_od = {r["mail"].strip().lower(): r.get("cc", "") for r in R}
    print(utc(), "ulaz %d redaka po filtru, adresa %d, bez MX %d, već predano %d, strop %d" % (len(R), len(red), len(bez_mx), len(ST["predano"]), a.strop))
    s = Snov()
    if a.salji:
        b0 = balans(s); ST["balans"].append([utc(), "prije", b0]); ST["bez_mx"] = sorted(set(ST["bez_mx"]) | set(bez_mx)); spremi()
        print(utc(), "balans prije:", b0)
        ost = [m for m in red if m not in ST["predano"]][:max(0, a.strop - len(ST["predano"]))]
        poziva = 0
        for i in range(0, len(ost), 10):
            b = ost[i:i + 10]
            for cek in range(40):
                st, j = s.post("/v1/add-emails-to-verification", data=[("emails[]", m) for m in b], ponovi=False)
                if isinstance(j, dict) and "too many emails processing" in str(j.get("message", "")).lower():
                    spremi(); print(utc(), "red pun, čekam 90 s (predano %d)" % len(ST["predano"])); time.sleep(90); continue
                break
            ok = st == 200 and (not isinstance(j, dict) or j.get("success") is not False)
            for m in b:
                if ok:
                    ST["predano"][m] = utc()
                else:
                    ST["greske"].append([m, st, str(j)[:120]])
            poziva += 1
            if poziva % 20 == 0:
                bb = balans(s); ST["balans"].append([utc(), "tijekom", bb]); spremi()
                print(utc(), "predano %d / %d | greške %d | balans %s" % (len(ST["predano"]), len(red), len(ST["greske"]), bb))
                if bb is not None and bb < a.donja_granica:
                    print(utc(), "STOP: balans %s ispod donje granice %s" % (bb, a.donja_granica)); break
            if not ok and st in (401, 402, 403):
                print(utc(), "STOP: Snov vraća %s %s" % (st, str(j)[:160])); break
        b1 = balans(s); ST["balans"].append([utc(), "poslije", b1]); spremi()
        print(utc(), "GOTOVO predano %d | greške %d | bez MX %d | balans %s -> %s" % (len(ST["predano"]), len(ST["greske"]), len(ST["bez_mx"]), b0, b1))
    if a.pokupi:
        rez = {}; ms = sorted(ST["predano"])
        for i in range(0, len(ms), 10):
            b = ms[i:i + 10]
            st, j = s.post("/v1/get-emails-verification-status", data=[("emails[]", m) for m in b])
            if not isinstance(j, dict):
                continue
            for m in b:
                x = j.get(m) or {}
                stat = ((x.get("status") or {}).get("identifier")) or "?"
                d = x.get("data") if isinstance(x.get("data"), dict) else {}
                rez[m] = {"status": stat, "smtp": d.get("smtpStatus"), "catchall": d.get("isCatchall"), "cc": cc_od.get(m, "")}
            if (i // 10) % 50 == 0:
                print(utc(), "pokupljeno %d / %d" % (len(rez), len(ms)))
        for m, v in rez.items():
            v["zelena"] = "da" if (v["smtp"] == "valid" and not v["catchall"]) else ""
        c = collections.Counter((v["status"], v["smtp"], bool(v["catchall"])) for v in rez.values())
        po = collections.defaultdict(collections.Counter)
        for v in rez.values():
            po[v["cc"]]["zelena" if v["zelena"] else (v["smtp"] or v["status"])] += 1
        put = os.path.join(OUT, "snov_provjera_%s_rezultat" % a.oznaka)
        json.dump({"vrijeme_utc": utc(), "rezultat": rez, "brojke": {str(k): n for k, n in c.items()}, "po_cc": {k: dict(v) for k, v in po.items()}, "balans": balans(s)},
                  io.open(put + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        with io.open(put + ".csv", "w", encoding="utf-8", newline="") as f:
            wr = csv.writer(f, delimiter=";"); wr.writerow(["mail", "cc", "status", "smtp", "catchall", "zelena"])
            for m, v in sorted(rez.items()):
                wr.writerow([m, v["cc"], v["status"], v["smtp"], v["catchall"], v["zelena"]])
        print(utc(), "POKUPLJENO %d: zelenih %d | %s | balans %s" % (len(rez), sum(1 for v in rez.values() if v["zelena"]), dict(c), balans(s)))
        for cc, v in sorted(po.items(), key=lambda kv: -sum(kv[1].values()))[:30]:
            print("  %-3s %s" % (cc, dict(v)))
        print("rezultat:", put + ".csv")


if __name__ == "__main__":
    main()
