# Uputa: mailovi

Posao: pročitati što je stiglo u WWM i PR sandučiće, javiti Matiji, složiti odgovore iz predložaka, poslati
samo ono što on odobri, upisati ledger i kanon. Radi se iz klona `wwm-ops` na laptopu (Codex) ili Hetzneru.
Prije prvog poteza pročitaj `AGENTS.md` (osobito §3.2 i §7) i `KANON_KRATKI.md`.

Alati: `alati/sken.py` (čita poštu na poslužitelju), `alati/posalji.py` (šalje s poslužitelja), `alati/kanon_red.py`.
Poslužitelji: `namecheap-portal` (sandučići WWM i PR domena), `hostarmada` (prvoiceglobal.com i persone).
Podaci na poslužitelju žive u `~/wwm_ops_podaci/` (popis viđenih, skenovi, ledger). Na laptopu se ništa ne pamti osim repoa.

## Korak 0: priprema (svaki put)

```
cd <klon wwm-ops>
git pull
```
Pogledaj `odluke/`: ako postoji datoteka sa `Status: ODLUČI` koja se tiče mailova, STANI i javi Matiji; ne pretpostavljaj odgovor.

## Korak 1: sken

Na oba poslužitelja, redom:
```
scp alati/sken.py alati/sken_iskljuci.txt namecheap-portal:~/wwm_ops_podaci/
ssh namecheap-portal 'PYTHONIOENCODING=utf-8 python3 ~/wwm_ops_podaci/sken.py' > out/sken_namecheap.md
scp alati/sken.py alati/sken_iskljuci.txt hostarmada:~/wwm_ops_podaci/
ssh hostarmada 'PYTHONIOENCODING=utf-8 python3 ~/wwm_ops_podaci/sken.py' > out/sken_hostarmada.md
```
Sken sam gleda od zadnjeg skena (prvi put: `--od 2026-11-06T00:48`, vidi odluke/2026-11-08-mailovi-pilot.md).
Za probu bez upisa viđenih: `--bez-upisa`. Za ponovni prikaz svega u rasponu: `--sve --od 48h`.
Izlazni JSON je na poslužitelju (`~/wwm_ops_podaci/sken_<host>_<vrijeme>.json`); kad trebaš polja za odgovor
(mid, references), skini ga: `scp namecheap-portal:~/wwm_ops_podaci/sken_premium215_<vrijeme>.json out/`.

Ako ssh vrati 255 (Namecheap zna odbiti brze uzastopne veze), pričekaj 20 s i ponovi. Ništa drugo ne mijenjaj.

## Korak 2: javi Matiji, odmah i bez istrage

Odmah nakon skena napiši mu popis, u ovom redoslijedu, bez ikakvog kopanja po bazi ili karti:

1. **MICANJE S KARTE** (sve što sken označi kao micanje i sve što ti prepoznaš kao zahtjev da se vinarija makne, sakrije ili ispravi jer nije vinarija): tko, koji sandučić, kad, cijeli tekst i HR prijevod. Ovo ide prvo, uvijek, i označi ga tako.
2. **Odgovori vinarija i medija**: za svaki: tko (ime, adresa), kad, koji sandučić, cijeli tekst (i dio ispod citata ako postoji), HR prijevod, jedna rečenica što traže. Tekst ispod citata nije šum: ako je iznad citata prazno a ispod ima teksta, to JE odgovor.
3. **Nove poruke koje nisu odgovor** (contact@ i slično): isto kao 2, uz jednu rečenicu je li šum (newsletter, ponuda, spam).
4. **Brojke**: bounce, auto-odgovori, DMARC, warmup, samo brojevi.

Klijentske domene su isključene skenom; ako se ipak pojavi nešto od Sylvie, Bevande ili drugih klijenata, ne spominji ga u WWM izvještaju.
Ništa se ne odgovara i ne radi dok Matija ne pročita popis. Istraga (baza, karta, povijest) tek kad za konkretan mail kaže »provjeri«.

## Korak 3: nacrti odgovora

Za svaku nit za koju Matija kaže da odgovaramo (ili je očito iz predložaka: V1 kako preuzeti profil, M1 mediji pristali):

1. Nađi našu prethodnu poruku u toj niti (mapa `.Sent` tog sandučića na poslužitelju) i uzmi IME kojim je potpisana. Tim imenom potpisuješ. Ako naše poruke nema (pišu prvi put na contact@), potpis je Matija Gavrilović, Founder, World Winery Map.
2. Uzmi predložak iz `predlosci/` koji odgovara vrsti. Ako nijedan ne odgovara (cjenik, pravno, partnerstvo, micanje), napiši nacrt po uzoru i označi »bez predloška«.
3. Prevedi na jezik primatelja vjerno, rečenicu po rečenicu. Izravna poveznica na pin: koordinate uzmi iz `https://worldwinerymap.com/#map=14/<lat>/<lng>` kako stoji u našoj prethodnoj poruci u niti; ako je nema, zatraži od Matije ili Claudea, ne pogađaj.
4. Provjeri programski: u tijelu nema znakova `—` ni `–`; nema fraza iz AGENTS.md §8.
5. Ispravak podataka na karti (ime, položaj, dvojnik) NE radiš ti. To je zaseban posao (Claude ili Matija). Ako odgovor ovisi o ispravku (V2, V3), nacrt čeka dok ispravak nije napravljen i potvrđen.

## Korak 4: čista lista za odobrenje

Jedna kartica, samo niti koje se šalju, redom po broju:

```
### 1 · Scott Osborn, Fox Run Vineyards (SAD) · contact@worldwinerymap.com · 6.11. 14:44
NJIHOV MAIL: <doslovno>
HR: <prijevod>
NAŠ ODGOVOR (EN): <cijeli tekst, točno kako ide>
HR: <prijevod našeg odgovora>
Predložak: vinarije/V7 · Potpis: Matija Gavrilović
Šalji? ☐
```

Niti koje se ne šalju (šum, samo micanje, čeka ispravak) idu u zaseban odjeljak »Ne šalje se« s jednom rečenicom zašto.
Svaka nova verzija nacrta je cijeli paket iznova, ne »ostalo kao prije«.

## Korak 5: odobrenje

Matija odgovara brojevima ili imenima uz »šalji« / »da«, ponekad s izmjenom teksta. Vrijedi točno to:
- šalje se samo redak uz koji je napisao da ili broj; njegove izmjene teksta se unose doslovno;
- »spremno«, »može valjda«, tišina = nije odobreno;
- dvosmisleno = pošalji samo sigurno, za ostalo pitaj.

## Korak 6: plan i slanje

1. Složi `out/plan_<datum>.json` po obliku iz zaglavlja `alati/posalji.py`: po jedna stavka za svaki odobreni redak;
   `in_reply_to` = njihov Message-ID iz skena (`mid`), `references` = njihov `references` + razmak + `mid`,
   `odobrio` = njegova riječ doslovno (npr. »Matija 8.11.: šalji 1 i 3«), `predlozak` = koji predložak.
2. Proba (ništa se ne šalje, provjere na poslužitelju):
   ```
   python3 alati/posalji.py --plan out/plan_<datum>.json --host namecheap --proba
   python3 alati/posalji.py --plan out/plan_<datum>.json --host hostarmada --proba
   ```
   Svaka stavka mora biti SPREMNO. Ako nije, popravi plan (ili stani i pitaj), ne zaobilazi bravu.
   Ako brava kaže da je od njih stigla novija poruka: pročitaj je, javi Matiji, tek onda `dopusti_novije`.
3. Slanje, samo za poslužitelj na kojem su stavke:
   ```
   python3 alati/posalji.py --plan out/plan_<datum>.json --host namecheap --posalji
   ```
   Alat šalje jedan po jedan s pauzom, upisuje ledger na poslužitelju i dopisuje `out/POSLANO.csv`. Prva greška zaustavlja sve.
4. Provjeri `out/POSLANO.csv`: svaki poslani redak ima status `poslano` i Message-ID. Bez retka u ledgeru slanje ne postoji.

## Korak 7: kraj posla

1. `odluke/`: sve što čeka Matiju (cjenik, micanje s karte, pravno) ima svoju datoteku sa `Status: ODLUČI`.
2. Red u kanon:
   ```
   python3 alati/kanon_red.py --iz out/kanon_red_<datum>.json          # proba
   python3 alati/kanon_red.py --iz out/kanon_red_<datum>.json --pisi   # upis (na Hetzneru, gdje je kanon)
   ```
   Naslov: »MAILOVI <datum>: <broj> ODGOVORA (<vrste>), <broj> MICANJE, <broj> ČEKA«; tijelo: što je stiglo i što je poslano s brojkama; pouke; otvoreno.
   Kanon je na Hetzneru, pa taj korak ide s Hetznera (`ssh hetzner`, klon `/root/wwm_ops`) ili ga za tebe upiše Claude; u izvještaju ostavi tekst reda.
3. `git add out/POSLANO.csv odluke/ && git commit -m "mailovi <datum>: poslano N, čeka M" && git push`.
4. Izvještaj Matiji: poslano (kome, iz kojeg sandučića), što čeka njegovu riječ, brojke iz skena. Kratko.

## Što nikad

- Ne šalješ bez njegove riječi za baš taj mail. Ne odgovaraš onima koje smo samo maknuli s karte.
- Ne mijenjaš ništa na karti, u bazi ni na serveru. Ne brišeš poštu. Ne diraš `.snovio` ni cron.
- Ne otvaraš Snov za brojke odgovora; sandučići su jedina istina.
- Ne pišeš tajne ni lozinke nigdje; posalji.py ih ne treba.
- Kad zapneš: `odluke/YYYY-MM-DD-<tema>.md` i stani.
