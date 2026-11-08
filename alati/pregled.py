#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pregled.py: gradi out/PREGLED.html, jednu statičnu stranicu s filtrima i pretragom nad ledgerom poslanog
(out/POSLANO.csv) i, ako postoje, nad zadnjim skenovima (out/sken_*.json, skinuti s poslužitelja).

Otvara se dvoklikom u pregledniku, bez poslužitelja i bez interneta. Ništa ne šalje, ništa ne mijenja.

    python3 alati/pregled.py              # -> out/PREGLED.html
    python3 alati/pregled.py --izlaz /putanja/PREGLED.html

Filtri: razdoblje, poslužitelj, sandučić, vrsta, status, tko je odobrio; pretraga po primatelju i predmetu.
Kartice: Poslano (ledger) · Stiglo (zadnji skenovi) · Sažetak (brojke po danu, sandučiću i vrsti).
"""
import argparse, csv, glob, io, json, os, time, html

OVDJE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(OVDJE)
OUT = os.path.join(REPO, "out")


def ucitaj_poslano():
    p = os.path.join(OUT, "POSLANO.csv")
    if not os.path.exists(p):
        return []
    with io.open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ucitaj_skenove():
    rows = []
    for p in sorted(glob.glob(os.path.join(OUT, "sken_*.json"))):
        try:
            for r in json.load(io.open(p, encoding="utf-8")):
                r["_dat"] = os.path.basename(p)
                rows.append(r)
        except Exception:
            continue
    # isti mail iz više skenova: zadrži jedan
    vid = set(); jed = []
    for r in rows:
        k = (r.get("box"), r.get("mid"))
        if k in vid:
            continue
        vid.add(k); jed.append(r)
    return jed


HTML = u"""<!doctype html>
<html lang="hr"><head><meta charset="utf-8"><title>WWM mailovi: pregled</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--bg:#f6f4ef;--fg:#1d1b17;--mut:#6b665c;--line:#ddd7c9;--acc:#7a1f2b;--ok:#2d6a3e;--warn:#9a6a00;--bad:#9b2222;--card:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#17161a;--fg:#ece8df;--mut:#a39c8f;--line:#35323a;--acc:#d98a95;--ok:#7fc48f;--warn:#e0b24a;--bad:#ef8a8a;--card:#201f24}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,Segoe UI,Roboto,sans-serif}
header{padding:16px 20px;border-bottom:1px solid var(--line);display:flex;gap:16px;align-items:baseline;flex-wrap:wrap}
h1{font-size:18px;margin:0}header small{color:var(--mut)}
nav{display:flex;gap:6px;padding:10px 20px 0}nav button{background:none;border:1px solid var(--line);color:var(--fg);padding:6px 12px;border-radius:8px 8px 0 0;cursor:pointer}
nav button.on{background:var(--card);border-bottom-color:var(--card);font-weight:600}
section{display:none;padding:14px 20px 40px;background:var(--card);border-top:1px solid var(--line)}section.on{display:block}
.f{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}.f input,.f select{padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);font:inherit}
.f input[type=search]{min-width:240px}.n{color:var(--mut);font-size:13px;margin:4px 0 10px}
table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{position:sticky;top:0;background:var(--card);cursor:pointer;white-space:nowrap}tr:hover td{background:rgba(122,31,43,.05)}
.s-poslano{color:var(--ok);font-weight:600}.s-greska{color:var(--bad);font-weight:600}.s-zapoceto{color:var(--warn)}
.k-odgovor{color:var(--ok)}.k-ostalo{color:var(--warn)}.k-bounce,.k-auto,.k-auto\\?{color:var(--mut)}
.mic{background:var(--bad);color:#fff;border-radius:4px;padding:0 6px;font-size:12px;margin-left:6px}
details summary{cursor:pointer;color:var(--acc)}pre{white-space:pre-wrap;margin:6px 0 0;font:13px/1.4 ui-monospace,Consolas,monospace;color:var(--fg)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}.box{border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.box h3{margin:0 0 6px;font-size:14px;color:var(--mut)}.box table{font-size:13px}
@media(max-width:700px){td.w,th.w{display:none}}
</style></head><body>
<header><h1>WWM mailovi: pregled</h1><small>napravljeno __KAD__ · poslano __NP__ · stiglo __NS__ · izvor: out/POSLANO.csv, out/sken_*.json</small></header>
<nav><button class="on" data-t="poslano">Poslano</button><button data-t="stiglo">Stiglo</button><button data-t="sazetak">Sažetak</button></nav>

<section id="poslano" class="on">
<div class="f">
 <input type="search" id="p_q" placeholder="pretraga: primatelj, predmet, odobrio…">
 <input type="date" id="p_od"><input type="date" id="p_do">
 <select id="p_host"><option value="">poslužitelj: svi</option></select>
 <select id="p_box"><option value="">sandučić: svi</option></select>
 <select id="p_vrsta"><option value="">vrsta: sve</option></select>
 <select id="p_status"><option value="">status: svi</option></select>
 <select id="p_odobrio"><option value="">odobrio: svi</option></select>
 <button onclick="reset('p')">očisti</button>
</div>
<div class="n" id="p_n"></div>
<table id="p_t"><thead><tr><th data-k="vrijeme_utc">vrijeme (UTC)</th><th data-k="to">kome</th><th data-k="subject">predmet</th><th data-k="sanducic">iz sandučića</th><th data-k="vrsta" class="w">vrsta</th><th data-k="predlozak" class="w">predložak</th><th data-k="odobrio" class="w">odobrio</th><th data-k="status">status</th></tr></thead><tbody></tbody></table>
</section>

<section id="stiglo">
<div class="f">
 <input type="search" id="s_q" placeholder="pretraga: pošiljatelj, predmet, tekst…">
 <input type="date" id="s_od"><input type="date" id="s_do">
 <select id="s_host"><option value="">poslužitelj: svi</option></select>
 <select id="s_box"><option value="">sandučić: svi</option></select>
 <select id="s_kat"><option value="">vrsta: sve</option></select>
 <label><input type="checkbox" id="s_mic"> samo micanje s karte</label>
 <button onclick="reset('s')">očisti</button>
</div>
<div class="n" id="s_n"></div>
<table id="s_t"><thead><tr><th data-k="kad">stiglo (UTC)</th><th data-k="od">od</th><th data-k="predmet">predmet</th><th data-k="box">sandučić</th><th data-k="kat">vrsta</th><th>tekst</th></tr></thead><tbody></tbody></table>
</section>

<section id="sazetak"><div class="grid" id="z"></div></section>

<script>
const POSLANO=__POSLANO__;const STIGLO=__STIGLO__;
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
document.querySelectorAll("nav button").forEach(b=>b.onclick=()=>{document.querySelectorAll("nav button,section").forEach(x=>x.classList.remove("on"));b.classList.add("on");document.getElementById(b.dataset.t).classList.add("on");});
function fill(id,vals){const s=document.getElementById(id);[...new Set(vals.filter(Boolean))].sort().forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=v;s.appendChild(o);});}
fill("p_host",POSLANO.map(r=>r.host));fill("p_box",POSLANO.map(r=>r.sanducic));fill("p_vrsta",POSLANO.map(r=>r.vrsta));fill("p_status",POSLANO.map(r=>r.status));fill("p_odobrio",POSLANO.map(r=>r.odobrio));
fill("s_host",STIGLO.map(r=>r.host));fill("s_box",STIGLO.map(r=>r.box));fill("s_kat",STIGLO.map(r=>r.kat));
let sortP={k:"vrijeme_utc",d:-1},sortS={k:"kad",d:-1};
const g=id=>document.getElementById(id).value;
function dan(s){return (s||"").slice(0,10);}
function renderP(){let rows=POSLANO.filter(r=>{const q=g("p_q").toLowerCase();if(q&&!(r.to+" "+r.subject+" "+r.odobrio+" "+r.predlozak).toLowerCase().includes(q))return false;
 if(g("p_od")&&dan(r.vrijeme_utc)<g("p_od"))return false;if(g("p_do")&&dan(r.vrijeme_utc)>g("p_do"))return false;
 for(const [f,k] of [["p_host","host"],["p_box","sanducic"],["p_vrsta","vrsta"],["p_status","status"],["p_odobrio","odobrio"]]){if(g(f)&&r[k]!==g(f))return false;}return true;});
 rows.sort((a,b)=>(a[sortP.k]||"")<(b[sortP.k]||"")?-sortP.d:(a[sortP.k]||"")>(b[sortP.k]||"")?sortP.d:0);
 document.getElementById("p_n").textContent=rows.length+" od "+POSLANO.length+" redaka";
 document.querySelector("#p_t tbody").innerHTML=rows.map(r=>`<tr><td>${esc(r.vrijeme_utc)}</td><td>${esc(r.to)}</td><td>${esc(r.subject)}<br><small style="color:var(--mut)">${esc(r.message_id)}</small></td><td>${esc(r.sanducic)}</td><td class="w">${esc(r.vrsta)}</td><td class="w">${esc(r.predlozak)}</td><td class="w">${esc(r.odobrio)}</td><td class="s-${esc(r.status)}">${esc(r.status)}${r.greska?"<br><small>"+esc(r.greska)+"</small>":""}</td></tr>`).join("");}
function renderS(){let rows=STIGLO.filter(r=>{const q=g("s_q").toLowerCase();if(q&&!(r.od+" "+r.od_ime+" "+r.predmet+" "+r.iznad+" "+r.ispod).toLowerCase().includes(q))return false;
 if(g("s_od")&&dan(r.kad)<g("s_od"))return false;if(g("s_do")&&dan(r.kad)>g("s_do"))return false;
 for(const [f,k] of [["s_host","host"],["s_box","box"],["s_kat","kat"]]){if(g(f)&&r[k]!==g(f))return false;}
 if(document.getElementById("s_mic").checked&&!r.micanje)return false;return true;});
 rows.sort((a,b)=>(a[sortS.k]||"")<(b[sortS.k]||"")?-sortS.d:(a[sortS.k]||"")>(b[sortS.k]||"")?sortS.d:0);
 document.getElementById("s_n").textContent=rows.length+" od "+STIGLO.length+" poruka";
 document.querySelector("#s_t tbody").innerHTML=rows.map(r=>`<tr><td>${esc(r.kad)}</td><td>${esc(r.od_ime)}<br><small>${esc(r.od)}</small></td><td>${esc(r.predmet)}${r.micanje?'<span class="mic">MICANJE</span>':""}</td><td>${esc(r.box)}</td><td class="k-${esc(r.kat)}">${esc(r.kat)}</td><td><details><summary>${esc((r.iznad||r.ispod||"").slice(0,90))}…</summary><pre>${esc(r.iznad)}${r.ispod?"\\n\\n--- ISPOD CITATA:\\n"+esc(r.ispod):""}</pre></details></td></tr>`).join("");}
function renderZ(){const grp=(arr,k)=>{const m={};arr.forEach(r=>{const v=r[k]||"(prazno)";m[v]=(m[v]||0)+1;});return Object.entries(m).sort((a,b)=>b[1]-a[1]);};
 const tbl=(t,rows)=>`<div class="box"><h3>${t}</h3><table>${rows.slice(0,25).map(([k,v])=>`<tr><td>${esc(k)}</td><td style="text-align:right">${v}</td></tr>`).join("")}</table></div>`;
 document.getElementById("z").innerHTML=tbl("Poslano po danu",grp(POSLANO.map(r=>({d:dan(r.vrijeme_utc)})),"d"))+tbl("Poslano po sandučiću",grp(POSLANO,"sanducic"))+tbl("Poslano po vrsti",grp(POSLANO,"vrsta"))+tbl("Poslano po statusu",grp(POSLANO,"status"))+tbl("Stiglo po vrsti",grp(STIGLO,"kat"))+tbl("Stiglo po sandučiću",grp(STIGLO,"box"))+tbl("Micanje s karte (poruke)",grp(STIGLO.filter(r=>r.micanje).map(r=>({d:r.od})),"d"));}
function reset(p){document.querySelectorAll("#"+(p==="p"?"poslano":"stiglo")+" input, #"+(p==="p"?"poslano":"stiglo")+" select").forEach(e=>{if(e.type==="checkbox")e.checked=false;else e.value="";});p==="p"?renderP():renderS();}
document.querySelectorAll("#poslano input,#poslano select").forEach(e=>e.addEventListener("input",renderP));
document.querySelectorAll("#stiglo input,#stiglo select").forEach(e=>e.addEventListener("input",renderS));
document.querySelectorAll("#p_t th[data-k]").forEach(th=>th.onclick=()=>{sortP={k:th.dataset.k,d:sortP.k===th.dataset.k?-sortP.d:-1};renderP();});
document.querySelectorAll("#s_t th[data-k]").forEach(th=>th.onclick=()=>{sortS={k:th.dataset.k,d:sortS.k===th.dataset.k?-sortS.d:-1};renderS();});
renderP();renderS();renderZ();
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--izlaz", default=os.path.join(OUT, "PREGLED.html"))
    a = ap.parse_args()
    poslano = ucitaj_poslano(); stiglo = ucitaj_skenove()
    for r in stiglo:
        r["iznad"] = (r.get("iznad") or "")[:4000]; r["ispod"] = (r.get("ispod") or "")[:1500]
        for k in ("references", "datoteka", "_dat"):
            r.pop(k, None)
    page = (HTML.replace("__KAD__", time.strftime("%d.%m.%Y. %H:%M"))
                .replace("__NP__", str(len(poslano))).replace("__NS__", str(len(stiglo)))
                .replace("__POSLANO__", json.dumps(poslano, ensure_ascii=False).replace("</", "<\\/"))
                .replace("__STIGLO__", json.dumps(stiglo, ensure_ascii=False).replace("</", "<\\/")))
    os.makedirs(os.path.dirname(a.izlaz), exist_ok=True)
    io.open(a.izlaz, "w", encoding="utf-8", newline="\n").write(page)
    print("PREGLED.html: poslano %d, stiglo %d, %d kB -> %s" % (len(poslano), len(stiglo), len(page.encode("utf-8")) // 1024, a.izlaz))


if __name__ == "__main__":
    main()
