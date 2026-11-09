# Pozivari: gdje ulazi sve što dobiju na svoj Gmail i na telefon

Status: ODLUČENO (redoslijed), gradnja čeka

## Odluka

- Matija 9.11.: »to se gradi prije Wine Newsa, čim sredimo sve drugo ovo hitno, a to su B2B mailovi, niše, funnel prodaje.«
- Redoslijed: (1) B2B mailovi vinarijama, (2) niše, (3) funnel prodaje, (4) **unos pozivara**, (5) Wine News.

## Što se gradi

Deset pozivara piše i prima mail kroz vlastite Gmail račune. Tamo im stižu odjave, ispravci, pitanja. Danas to ne ulazi nigdje.

1. **Jedna naša adresa za prosljeđivanje** (sandučić na našem cPanelu, ime još nije odabrano). Pozivar proslijedi mail; u prvi red smije upisati jednu riječ: ODJAVA, ISPRAVAK, PITANJE, ZOVI KASNIJE.
2. **`alati/sken.py` čita taj sandučić** kao i ostale. Novo: iz proslijeđenog maila izvući izvornog pošiljatelja (ne pozivara), razvrstati, u pregledu pokazati tko je proslijedio.
3. **Odjave** idu u `out/NE_KONTAKTIRATI.csv` kroz `alati/ne_kontaktirati.py`, s izvorom »pozivar <ime>«. Usmena odjava s poziva ulazi istim putem: jedan redak na istu adresu.
4. **Skrivena kopija (Bcc) na izlazu**: što pozivar pošalje s Gmaila ide u Bcc na istu adresu, da znamo kome je tko pisao i da ista vinarija ne dobije mail s tri strane.
5. **Provjera prije poziva**: pregled s pretragom je li vinarija na listi »ne kontaktirati« (ne CSV).
6. **Obrazac u adminu** (vinarija, ishod poziva, napomena) iza Cloudflare prijave, pozivari se prijavljuju svojim Gmailom. Početak pregleda nalik CRM-u (Q10 od 8.11.).

## Otvoreno

- Ime adrese i tko otvara sandučić.
- Popis Gmail adresa pozivara (za Cloudflare prijavu i za prepoznavanje tko je proslijedio).
- Ispravci podataka o vinariji: u `odluke/` ili u red u adminu.
