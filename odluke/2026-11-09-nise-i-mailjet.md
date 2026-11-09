# Niše i Mailjet: što treba prije slanja

Status: ODLUČI

Radna verzija za Matiju je Claude Doc (privremeno, dok on gleda i piše): https://claude.ai/artifact/CHqTsBw1qxEVwPvGTsnssq
Ova datoteka je kopija da je vide svi agenti. Kad Matija odluči u dokumentu, odluke se prepisuju ovamo i ova datoteka je istina.

## ODLUČI

**Mailjet runda 2 (vinarije, 3.985 adresa, 9 nacrta u Mailjetu, pošiljatelj contact@prvoiceglobal.com)**
1. Tekstovi: idu kakvi jesu ili se mijenjaju? Cijeli tekstovi: `predlosci/mailjet_b2b_r2.md`.
   - **Matija:** 9.11. (u dokumentu): »ako su takve dobivali već, ok je onda«. Runda 1 je išla s istim kosturom, dakle tekstovi ostaju.
2. Redoslijed: svih devet skupina isti dan, ili prvo IT i FR pa ostale nakon što se vide odjave?
   - **Matija:** 9.11.: isti dan, svih devet.
3. Tko pokreće slanje: Matija klikom u Mailjetu ili agent kroz API na njegovu riječ?
   - **Matija:** 9.11.: agent kroz API, tek kad Matija u razgovoru napiše »šalji«.
4. Prije slanja čišćenje lista prema `out/NE_KONTAKTIRATI.csv` i domenama koje su u međuvremenu preuzele profil?
   - **Matija:** 9.11.: da; i PRIJE svega skupiti stare odjave i odbijanja iz Snova i iz odgovora (»oni stari što su se micali davno«). Slanje ne kreće dok lista nije potpuna.

**Niše (mediji, val od 30.10.)**
5. Novi krug za 1.809 adresa kojima mail nije otišao: ide li i s kojim tekstom (31.10.: »pauziraj, mijenjam body«)?
   - **Matija:**
6. 1.346 žutih adresa Snov ne šalje: idu li kroz Mailjet?
   - **Matija:**
7. Odgovori medija koji čekaju (8 redakcija, dvije plaćene ponude): pregled kroz mailove ovaj tjedan?
   - **Matija:**

## Zašto pitam (izmjereno 9.11.2026.)

Mailjet runda 2: IT 1.189, FR 1.236, ES 520, LAT 134, PT 188, CS 62, SK 17, ZA 213, INTL 426. Članci u mailovima se otvaraju,
spominju kartu i linkaju na nju (INTL, Wine Industry Advisor, stroju vraća 403; otvoriti ručno). Svi nacrti imaju odjavu, bez dugih crtica;
polja company_name i body2 popunjena kod svih kontakata; liste po domeni odgovaraju zemljama (FR lista: FR 856, BE 32, LU 5, ostalo 7).
Runda 1 (EN, 30.10.): poslano 2.739, tvrdo odbijeno 33, blokirano 8, odjava 15, prijava spama 0, 30 registracija do 4.11.
Snov nacrti »B2B K1Z 2910« (19 kampanja, 1.740 adresa) dijele s Mailjet r2 jednu adresu: odvojeni skupovi.
U tekstovima piše »90 zemalja«, karta ih danas ima 97.
Nije provjereno: izgled maila u sandučiću (prijedlog: probni mail po jeziku Matiji prije slanja).

Niše (stanje zapisano 31.10., nije ponovno čitano iz Snova): planirano 4.982, poslano 3.084 (2.979 zelenih, 105 žutih), bounce 89,
preskočeno bez slanja 463, žutih nikad u redu 1.346, ostalo za novi krug 1.809 (`Documents\WWM_PR_NISE_2026-10-29\_ceka_3110.txt`).
Za novi krug treba: novi tekst tijela, nove kampanje (stare se ne mogu ponovno upaliti), lokalno sklapanje i provjere svakog jezika, prikaz kroz sučelje, Matijina riječ »pali«.
Objave vala niše: 339 upita poslano 8.11. (1,017 USD), 275 pokupljeno; kandidate obrađuje Codex po `upute/pr_objave.md`.

## Stare odjave skupljene (9.11.2026., po Matijinu odgovoru na točku 4)

`out/NE_KONTAKTIRATI.csv` ima 664 retka (623 adrese, 41 cijela domena):
- Snov lista zabrana 12680120 (1.318 stavki, čitano kroz `GET /v2/blacklists/{id}/items`): 430 adresa i 291 domena pripada vlasnicima profila (usporedba s bazom: claimovi, korisnici, tablica vinarije) i NE ide na našu listu; 556 adresa i 41 domena nije vezano uz profil i to su stare odjave, odbijanja i micanja: uvezeno.
- Sandučići na oba poslužitelja, sva pošta od kolovoza (`alati/odjave_iz_poste.py`, 6.653 poruke): 132 kandidata, nakon filtra 83, pročitani pojedinačno: 51 prava odjava ili odbijanje (43 »no« na B2B mail, 6 izričitih odjava, 2 micanja); ostalo automatske potvrde, antispam izazovi (Mailinblack, SpamEnMoins) i dva koja žele profil.
- Mailjet runda 1: 33 tvrdo odbijena, 8 blokiranih, 15 odjava.

Proba čišćenja devet Mailjet lista (prema našoj listi, Snov listi zabrana i bazi): za micanje 4 od 3.985 (IT 1 i INTL 2 već imaju profil, LAT 1 s domene koja se odjavila).
Snov nacrti »B2B K1Z 2910« (1.740 adresa): nijedna na listi.
Što nije pokriveno: usmene odjave i odjave koje je Matija sam riješio izvan sandučića; pošta starija od kolovoza koju je cron brisao do 21.9.; popis 22+14 iz revizije 17.10. nije uspoređen jer je dokument na starom laptopu (vjerojatno je sadržan u Snov listi).
Snov i Mailjet se ovime NE mijenjaju; prijenos naše liste u njih je zaseban korak.

## Odluka
(prepisuje se iz dokumenta)
