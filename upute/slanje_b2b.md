# Uputa: slanje rundi vinarijama (B2B) i medijima kroz Mailjet, praćenje Snova

Posao: složiti listu, očistiti je, napraviti nacrt kampanje, poslati probni, čekati Matijinu riječ, poslati, pratiti brojke.
Radi se iz klona `wwm-ops` na laptopu (ključevi su u `C:\Users\world\wwm\.env.mailjet` i `.env.bevanda`, alati ih čitaju sami;
ključeve nikad ne ispisuj ni ne kopiraj). Prije prvog poteza pročitaj `AGENTS.md` i `KANON_KRATKI.md`.

Alati (svi u `alati/`, svi imaju uputu u zaglavlju):

| alat | što radi | šalje li |
|---|---|---|
| `slanje_stanje.py` | brojke Mailjet kampanja i Snov kampanja (poslano, bounce, blokirano, odjave) | ne |
| `lista_ciscenje.py` | od bilo kojeg CSV-a radi čistu listu (ne kontaktirati, MAIL_VAN, već kontaktirano, PEC, isključene zemlje, dupli) | ne |
| `mailjet_runda.py` | `stanje`, `lista`, `nacrt`, `probni`, `makni`, `salji` | samo `salji` s `--odobrio` |
| `snov_provjera.py` | Snov provjera adresa (troši kredite) | ne, ali troši kredite: samo na Matijinu riječ |
| `mail_unos.py` | novi mailovi iz lova u bazu i listu (Hetzner) | ne |
| `ciscenje_razlozi.py` | zašto neposlana adresa nije otišla (čišćenje 4.10. + lov), s preporukom po adresi | ne |
| `temeljna_baza.py` | jedna baza svega poslanog i ishoda (vidi `upute/temeljna_baza.md`) | ne |
| `kanon_red.py` | red u kanon (Hetzner) | ne |

Tekstovi: `tekstovi/mailjet/tijelo_<GRP>.txt` i `predmet_<GRP>.txt` (odobreni 31.10., runda 2). Za novu rundu vrijedi isti tekst
dok Matija ne kaže drukčije (10.11.: »novi tekst, ostavi stari za ovu rundu«). GRP = IT, FR (FR BE LU), ES, LAT (AR CL MX UY),
PT, CS, SK, ZA, INTL (sve ostalo na engleskom). Locale: it_IT, fr_FR, es_ES, pt_PT, cs_CZ, sk_SK, en_US.
Pošiljatelj: contact@prvoiceglobal.com »PR Voice Global« (HostArmada). Odgovori stižu tamo; čitaju se po `upute/mailovi.md`.

## Korak 0: priprema

```
cd <klon wwm-ops>
git pull
python alati/lista_ciscenje.py --osvjezi
```
`--osvjezi` povlači s Hetznera `out/MAIL_VAN.csv` i `out/KONTAKTIRANO_ADRESE.txt` (sve adrese kojima je WWM pisao ili su u nacrtu).
Pogledaj `odluke/`: datoteka sa `Status: ODLUČI` o slanju = STANI i javi Matiji.

## Korak 1: lista

Ulaz je CSV koji je netko već složio (npr. `out/lov/NOVI_MAILOVI_<datum>.csv` s lova, ili popis iz revizije) sa stupcima
`mail`/`email`, `ime`/`company_name`, `wwm_id`, `cc`. Po skupini jezika:
```
python alati/lista_ciscenje.py --ulaz out/lov/NOVI_MAILOVI_2026-11-10.csv --izlaz out/lista_IT_r3.csv --cc IT --filtar za_slanje=da --body2-jezik it
python alati/lista_ciscenje.py --ulaz ... --izlaz out/lista_FR_r3.csv --cc FR,BE,LU --filtar za_slanje=da --body2-jezik fr
python alati/lista_ciscenje.py --ulaz ... --izlaz out/lista_INTL_r3.csv --cc US,AU,GB,NZ,CA,IE,HU,GR,... --filtar za_slanje=da --body2-jezik en
```
Izvještaj (`<izlaz>.izvjestaj.json`) kaže koliko je izbačeno i zašto. DACH i ex-YU se ne šalju bez Matijine odluke (`--sve-zemlje` samo kad kaže).
Besplatni mailovi (gmail, libero...) idu u ZASEBNU listu (`--filtar vrsta=besplatni`), ne miješaju se s vlastitim domenama.
Pogledaj okom 20 nasumičnih redaka: ime vinarije, adresa, body2 (pozdravni oblik). Krivo ime = ispravi u CSV-u, ne u Mailjetu.

## Korak 2: lista i nacrt u Mailjetu, probni

```
python alati/mailjet_runda.py lista --ime "WWM IT r3" --csv out/lista_IT_r3.csv
python alati/mailjet_runda.py nacrt --ime "WWM IT r3" --naslov "WWM IT r3 (PR Voice Global)" --locale it_IT --predmet tekstovi/mailjet/predmet_IT.txt --tijelo tekstovi/mailjet/tijelo_IT.txt
python alati/mailjet_runda.py probni --naslov "WWM IT r3 (PR Voice Global)" --na desk@worldwinerymap.org
```
Probni ide na naš sandučić koji nije glavna domena (desk@worldwinerymap.org, Namecheap). Provjeri ga čitanjem sandučića
(`upute/mailovi.md`, korak 1): INBOX, SPF/DKIM/DMARC pass, polja popunjena (ime vinarije, pozdrav), link na članak otvara 200.
`python alati/mailjet_runda.py stanje` mora pokazati nacrt sa statusom 0 i listu s očekivanim brojem.

## Korak 3: odobrenje

Matiji jedna kartica: skupina, broj adresa, predmet, prvih 5 redaka liste (ime, adresa), rezultat probnog. Pitanje: »Šaljem <GRP> r3 (<N>)?«
Šalje se samo skupina uz koju napiše »šalji« ili »da«. »Spremno«, »može valjda«, tišina = nije odobreno.

## Korak 4: slanje i zapis

```
python alati/mailjet_runda.py salji --naslov "WWM IT r3 (PR Voice Global)" --odobrio "Matija 11.11.: šalji IT r3"
```
Alat prije slanja provjeri stanje nacrta (0), listu (nije prazna) i sadržaj; upiše `out/MAILJET_POSLANO.csv`. Taj CSV ide u git.
Odmah poslije: dodaj adrese liste u `out/KONTAKTIRANO_ADRESE.txt` na Hetzneru (ili zamoli Claudea), da sljedeće čišćenje zna.

## Korak 5: praćenje

```
python alati/slanje_stanje.py --od 2026-11-11
```
Daje po kampanji: poslano, tvrdi/meki bounce, blokirano, spam, odjave. Odjave i bounce: tvrdi bounce ide u `out/NE_KONTAKTIRATI.csv`
kroz `alati/ne_kontaktirati.py` (vidi zaglavlje). Odgovore ne čitaš iz Mailjeta ni Snova nego iz sandučića (`upute/mailovi.md`).
Snov kampanje u tijeku: popis ID-jeva u `out/snov_kampanje_u_tijeku.txt`; `--snov ID,ID` za druge.

## Korak 6: kraj posla

1. `odluke/YYYY-MM-DD-<tema>.md` za sve što čeka Matiju.
2. Red u kanon (`alati/kanon_red.py`, na Hetzneru): naslov »B2B RUNDA <datum>: <skupine>, <N> ADRESA«, tijelo s brojkama i zapisima.
3. `git add out/MAILJET_POSLANO.csv out/NE_KONTAKTIRATI.csv odluke/ && git commit -m "b2b runda <datum>: ..." && git push`.
4. Izvještaj Matiji: što je poslano (skupina, broj), što čeka, brojke. Kratko, bez AI fraza, brojke samo iz alata.

## Što nikad

- Ne šalješ bez njegove riječi za baš tu skupinu. `salji` bez `--odobrio` s njegovom riječi ne postoji.
- Ne mijenjaš tekst, pošiljatelja ni podnožje bez odluke u `odluke/`. U tekstu nikad worldwinerymap.com (Spamhaus 19.9.), nikad duge crtice.
- Ne diraš Snov kampanje (start/pause) ni kredite bez njegove riječi; Snov je za zelene adrese s vlastite domene po K1Z postupku (Claude).
- Ne stavljaš tajne u repo. Ne brišeš liste u Mailjetu.
- Kad zapneš: `odluke/` i stani.
