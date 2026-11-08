# Uputa: PR objave

Posao: naći gdje su mediji objavili naše PR tekstove, provjeriti svaku stranicu (spomen, link na kartu, datum) i
dopisati potvrđene u popis objava `out/OBJAVE_SVE.json`. Samo čitanje weba i DataForSEO upiti; ništa se ne šalje mailom,
ništa se ne mijenja na serveru. Prije prvog poteza pročitaj `AGENTS.md` i `KANON_KRATKI.md`.

Alat: `alati/objave.py` (upute na vrhu datoteke, `python alati/objave.py -h`). Radi na laptopu, gdje je ključ
DataForSEO (`C:/Users/world/wwm/.env.bevanda`, varijabla `DATAFORSEO_B64`; nikad je ne ispisuj).
Podaci: `out/objave/` (lokalno, ne ide u git) i `out/OBJAVE_SVE.json` + `.csv` (ide u git, to je popis objava, 257 redaka 3.11.2026.).

## Pravila koja alat drži, a ti ih ne zaobilaziš

- Samo DataForSEO **standard queue** (task_post pa task_get), nikad live endpoint. Live je 30 puta skuplji.
- Pretraga je **točnim frazama** iz PR teksta pod navodnicima (naslov, karakteristična rečenica), ne imenom brenda.
  Mediji prepišu naslov, a ime brenda ostave u tijelu ili izostave.
- Po tekstu: jezik teksta i država za koju je pisan (regionalni tekstovi samo organic, bez news).
- Datumski raspon od dana slanja PR-a, bez `qdr:m`. Depth 50.
- Tvrdi strop u USD pri slanju (`--strop`), nominalno 0,003 USD po upitu. Slanje tek na Matijinu riječ, s brojkama iz `plan`.
- Svaka nova stranica se otvori i zapiše: spomen imena ili adrese, link na kartu (dofollow/nofollow), datum, naslov.
- Već poslane press brojke se ne mijenjaju, što god našao (AGENTS.md §8).

## Korak 0: priprema

```
cd <klon wwm-ops>
git pull
```
Pogledaj `odluke/` za otvorene odluke o PR-u. Ako ih ima, stani i javi.

## Korak 1: fraze

Odakle dolaze fraze ovisi o valu:
- **Val niše (poslan 30.10.)**: popis press stranica `C:/Users/world/Documents/WWM_PR_NISE_2026-10-29/PRESS_POPIS.json` (365 stranica, 197 različitih naslova):
  ```
  python alati/objave.py fraze --izvor press-popis "C:/Users/world/Documents/WWM_PR_NISE_2026-10-29/PRESS_POPIS.json" --val nise
  ```
- **Drugi valovi**: CSV s kolonama `naslov, cc, lang` (jedan redak po tekstu) koji složiš iz PR tekstova toga vala, pa
  `fraze --izvor csv PUTANJA.csv --val <ime>`. Gdje su tekstovi kojeg vala piše u kanonu (t.393 lok vin 27.10., t.396 niše); ako ne znaš, pitaj kroz `odluke/`, ne pogađaj.
Alat ispiše broj fraza po jeziku. Fraze kraće od 8 znakova se odbacuju.

## Korak 2: plan i brojke

```
python alati/objave.py plan --val nise --od 2026-10-30
```
Ispis: broj upita (organic + news), različitih fraza, jezika, raspon datuma i **procjena troška**. Ništa se ne šalje.
Te brojke javiš Matiji u jednoj rečenici: »X upita, Y fraza, Z jezika, procjena N USD, strop predlažem M USD«. Čekaš njegovu riječ.
Ako je upita više od 500, prvo pitaj je li to namjerno; 2.725 upita 3.11. bilo je napuhano (memorija 3.11.).

## Korak 3: slanje upita (tek na »šalji«)

```
python alati/objave.py posalji --val nise --strop 2.00
```
ID-jevi zadataka idu odmah u `out/objave/taskovi.jsonl`; strop zaustavlja slanje. Za probu dva upita: `--samo-proba`.

## Korak 4: kupi rezultate

```
python alati/objave.py kupi --minute 30
```
Besplatno, smije se ponavljati; rezultati u `out/objave/rezultati.json`. Greška »40102 No Search Results« je normalna (fraza
nije nađena), nije kvar. Kad je ≥ 90 % pokupljeno, idi dalje, ostatak uzmi poslije (pravilo 3.11.: ne čekaj zaostatke).

## Korak 5: kandidati i provjera stranica

```
python alati/objave.py kandidati --maks 300
```
Alat izbaci naše domene i društvene mreže, makne URL-ove koji su već u `OBJAVE_SVE`, zadrži one sa signalom (ime karte,
Gavrilović, 4,3 mil., fraza iz upita), otvori stranice i napiše `out/objave/KANDIDATI.md`: potvrđene (spomen na stranici)
s linkom na kartu i datumom, pa nepotvrđene. Pročitaj ga cijelog. Za stranice koje se ne otvaraju (403) a isječak
iz SERP-a jasno pokazuje objavu, označi »potvrđeno isječkom«.

## Korak 6: pregled Matiji i zapis

Matiji daš sažetak: koliko novih potvrđenih objava, po zemlji i jeziku, koliko s linkom na kartu, i popis (medij, datum, naslov, link).
Nije potrebna njegova riječ za upis u popis objava; potrebna je za bilo kakav mail mediju (to je posao »mailovi«, ne ovaj).

Potvrđene složi u `out/objave/potvrdjeno_<datum>.json` kao popis `{url, cc, jezik, datum, naslov, vrsta, status, link_karta}` (polja koja znaš; ostalo alat uzme iz kandidata), pa:
```
python alati/objave.py zapisi --iz out/objave/potvrdjeno_<datum>.json
```
Dopisuje u `out/OBJAVE_SVE.json` i `.csv`, dedupe po URL-u.

## Korak 7: kraj posla

1. Red u kanon (`alati/kanon_red.py`, vidi `upute/mailovi.md` korak 7): naslov »OBJAVE <datum>: <val>, N novih (M s linkom), upita X, trošak Y USD«.
2. `git add out/OBJAVE_SVE.json out/OBJAVE_SVE.csv && git commit -m "objave <datum>: +N" && git push`.
3. Izvještaj Matiji: brojke iz mjere (upiti, trošak iz `taskovi.jsonl`, nove objave), bez procjena.

## Što nikad

- Ne koristiš live endpoint ni `qdr:m`. Ne šalješ upite bez plana i Matijine riječi.
- Ne pišeš medijima iz ovog posla.
- Ne mijenjaš press stranice ni brojke u njima.
- Ne brišeš ništa u `out/objave/`; stari rezultati su trag koliko je potrošeno.
