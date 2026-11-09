# Revizija neispunjenog, 6: Održavanje i rokovi

Status: ODLUČI

Izvor: `Documents/WWM_SUSTAV_RADA_2026-11-04/NEISPUNJENO_kanon.md` (stanje kanona 4.11.2026., t.350 do t.400, i revizija 17.10.). Stanje »otvoreno« = kanon je ponavlja; »nejasno« = kanon je ne spominje poslije obećanja, pa se ne zna je li riješeno izvan kanona. Uz svaku stavku je Claudeov prijedlog; Matija ispod upiše svoju riječ (ide / pada / kasnije / provjeri).

## ODLUČI

### 6.1 **CF tokeni istječu 13. i 15.11.2026.** (rok ostaje, Matija produžuje)
- izvor: t.400 · obećano: 4.11. · stanje: **otvoreno, rok** · zadnji spomen: t.400 · odluka: vlasnik
- prijedlog: ROK 13. i 15.11.: Matija produžuje tokene u Cloudflareu (pravilo: rok ostaje). Podsjetnik 12.11.
- **Matija:** 9.11.: produžio odmah oba tokena na 90 dana. Provjereno na serveru alatom provjeri_cf_token.py: CLOUDFLARE_API_TOKEN i CF_DNS_TOKEN active do 7.2.2027. (iste vrijednosti, samo novi rok, na serveru ništa za mijenjati). ZATVORENO do veljače; nadzor javlja 7 dana prije.

### 6.2 Stara baza atributa v26 bez indeksa (1,5 GB) na Storage Box »za koji dan«
- izvor: t.399, t.400 · obećano: 4.11. · stanje: **otvoreno** · zadnji spomen: t.400 · odluka: tehničko
- prijedlog: IDE tehničko: rsync na Box po postupku selidba_box, pa izvor van.
- **Matija:** 

### 6.3 Kopija wwm.db prije vacuuma ide u retenciju
- izvor: t.399 · obećano: 4.11. · stanje: **otvoreno** · zadnji spomen: t.399 · odluka: tehničko
- prijedlog: IDE tehničko: kopija wwm.db prije vacuuma u retenciju.
- **Matija:** 

### 6.4 Pečenje da samo arhivira prethodnu generaciju na Box
- izvor: t.399 · obećano: 4.11. · stanje: **otvoreno** · zadnji spomen: t.399 · odluka: tehničko
- prijedlog: IDE tehničko: u lanac pečenja dodati korak arhive prethodne generacije na Box.
- **Matija:** 

### 6.5 Test »admin vidi brojke po vinariji« (LIMIT 100) pada od 6.10.
- izvor: t.364, t.366, t.367, t.397 · obećano: 9.10. · stanje: **otvoreno** · zadnji spomen: t.400 (»star od 21.10.«) · odluka: tehničko
- prijedlog: IDE u popravke: test pada od 6.10., popraviti ili maknuti test.
- **Matija:** 

### 6.6 Retencija kopija ledgera (brava staje), jednom s `--ipak`
- izvor: t.62; revizija G ODLUČI 16 · obećano: 17.10. · stanje: **nejasno** · zadnji spomen: revizija G · odluka: vlasnik
- prijedlog: ČEKA Matiju: jednom --ipak nakon kopije 64 .prije datoteka na Box (iz t.402).
- **Matija:** 

### 6.7 v19 pmtiles na volumenu, nikad uživo
- izvor: t.366 · obećano: 11.10. · stanje: **nejasno (selidbe t.383 i t.399 ga ne imenuju)** · zadnji spomen: t.366 · odluka: tehničko
- prijedlog: IDE u paket popravaka (uputa popravci, kad nastane); ne traži odluku, samo termin.
- **Matija:** 

### 6.8 Prijevodi novih ključeva dashboarda (22 ključa)
- izvor: t.372, t.375, t.377 · obećano: 16.10. · stanje: **nejasno** · zadnji spomen: t.377 · odluka: tehničko
- prijedlog: IDE u paket popravaka (uputa popravci, kad nastane); ne traži odluku, samo termin.
- **Matija:** 

### 6.9 `kontrola_20` nema točku za podlogu i generaciju atributa
- izvor: t.371, t.372 · obećano: 15.10. · stanje: **nejasno (t.400 pušta kontrola_20, ne kaže je li točka dodana)** · zadnji spomen: t.372 · odluka: tehničko
- prijedlog: IDE u paket popravaka (uputa popravci, kad nastane); ne traži odluku, samo termin.
- **Matija:** 

### 6.10 Search Console: ishod tri validacije, 30 dana nepogledan
- izvor: t.239; revizija G #11 · obećano: 17.9. · stanje: **otvoreno** · zadnji spomen: t.239 · odluka: vlasnik
- prijedlog: IDE Matija: pogledati ishod validacija (5 minuta u sučelju).
- **Matija:** 

### 6.11 Disk na PC-u vlasnika pun
- izvor: t.385 · obećano: 21.10. · stanje: **nejasno** · zadnji spomen: t.385 · odluka: vlasnik
- prijedlog: RIJEŠENO selidbom na novi laptop 5.–8.11.
- **Matija:** 

### 6.12 Snov warmup aktivan na 69 sandučića protivno odluci 19.9.: ostaviti ili pauzirati
- izvor: DANAS_1710/IZVJESTAJ_K_spam · obećano: 19.10. · stanje: **nejasno** · zadnji spomen: revizija K · odluka: vlasnik
- prijedlog: ČEKA Matiju: ostaviti ili pauzirati warmup na 69 sandučića.
- **Matija:** 

### 6.13 Cron brisanja pošte (pauza od 21.9.), ciljano `[WRM]` starije od 3 dana
- izvor: revizija G ODLUČI 17 · obećano: 23.9., 17.10. · stanje: **nejasno** · zadnji spomen: revizija G · odluka: vlasnik
- prijedlog: ČEKA Matiju: uključiti ciljano brisanje [WRM] starijih od 3 dana (sad pauzirano od 21.9.).
- **Matija:** 

