# Vinari: kome je poslano, tko čeka, tko nema mail, kojim kanalom dalje

Status: ODLUČI

## ODLUČI

1. **Mailjet runda 2** (9 lista, 3.985 adresa): prije slanja maknuti 4 adrese s liste »ne kontaktirati« i 24 adrese vinarija koje su mail već dobile (popis `out/inventar_0911/dvostruko_cekanje_0911.json`). Slanje na tvoje »šalji«, svih devet isti dan.
2. **Snov nacrti K1Z** (19 kampanja, 1.740 zelenih adresa): paliti isti dan ili dan poslije Mailjeta? Strop po sandučiću ostaje 25.
3. **Žute / catch-all** (3.689, najviše US 1.084, FR 683, IT 645): prijedlog Mailjet runda 3, isti tekstovi po jeziku.
4. **Samo besplatni mail** (oko 9.300 bez PEC-a; IT, FR): prijedlog poseban Mailjet paket poslije rezultata runde 2. PEC (2.371) nikad.
5. **Isključene zemlje** (13.859 s mailom): DACH 11.554 (DE 5.603, AT 4.413, CH 1.538), ex-YU 1.422 (HR 522, SI 415, RS 306, MK 59, BA 55, ME 47, XK 18), GR 442, BR 400, CY 36, LI 5. Ostaju li samo za pozivare, ili dio ide mailom?
6. **Lov na mailove**: krenuti redom A, B, C dolje. A i C su besplatni. B košta 14,57 USD po jednom upitu na vinariju.

## Stanje 9.11.2026. (izmjereno)

Izvori: baza na serveru (tablica `vinarije`, samo na karti), sve Snov kampanje koje nisu nacrt (1.066 kampanja, 35.221 adresa, API 9.11.), Mailjet liste (API 9.11.), naša lista »ne kontaktirati« (664 retka), revizija 1.11. sa starog laptopa (`WWM_REVIZIJA_2026-11-01`). Od 1.11. vinarijama nije poslano ništa, pa razrada ostatka iz revizije 1.11. vrijedi i danas.

| skupina | vinarija |
|---|---|
| na karti | 104.249 |
| **s mailom** | **68.179** |
| kontaktirano | 21.043 |
| od toga Snov | 18.116 |
| od toga Mailjet runda 1 | 2.928 |
| registracija nakon maila (1.11.) | 442 |
| ima profil bez našeg maila | 93 |
| čeka u nacrtu: Mailjet runda 2 | 4.129 |
| čeka u nacrtu: Snov K1Z | 1.778 |
| ostatak s mailom | oko 41.100 |
| **bez maila** | **36.070** |
| bez maila, ima web | 11.785 |
| bez maila i bez weba | 24.285 |

Ostatak s mailom po razlogu (revizija 1.11., zbroj svih skupina = 68.187):

| razlog | vinarija | najviše |
|---|---|---|
| isključena zemlja | 13.859 | DE 5.603, AT 4.413, CH 1.538, HR 522, GR 442, SI 415, BR 400, RS 306 |
| samo gmail / libero / PEC | 11.697 | IT 4.799, FR 3.677, US 892, ES 422, HU 382 |
| ispalo na čišćenju (MX, web, ime, dvojnik, bounce) | 10.956 | IT 3.666, US 1.422, FR 1.406, ES 790, HU 590, AU 566 |
| žuta / catch-all | 3.689 | US 1.084, FR 683, IT 645, ES 312, AU 307 |
| VJEROJATNO (ručni pregled) | 962 | IT 204, US 199, FR 134, AU 96, ES 92 |

Poslano po valu (revizija 1.11.): Snov IT dan 1 (24.9.) 106; Snov IT2 (2.–6.10.) 2.115; Snov K1 (6.10.) 4.139; Snov K1Z zelene (19.–29.10.) 11.720; Mailjet EN runda 1 (30.10.) 2.931.
Registracije nakon maila: K1Z 275, K1 92, IT2 48, Mailjet 21, IT dan 1 6.

Po zemlji: `odluke/2026-11-09-vinari-inventar-po-zemlji.csv` (97 zemalja, današnje brojke i stupci revizije 1.11.).

## Kanal po skupini (prijedlog)

| skupina | kanal | uvjet |
|---|---|---|
| zelene, provjerene (nacrti K1Z) | Snov | spremno |
| Mailjet runda 2 | Mailjet | čišćenje 28 adresa, tvoje »šalji« |
| žute / catch-all | Mailjet runda 3 | odluka 3 |
| samo besplatni mail | Mailjet, poseban paket | odluka 4 |
| PEC | ne šalje se | |
| VJEROJATNO | ponovno otvoriti web, ostatak ručno | bez troška |
| ispalo na čišćenju | lov C, pa natrag u Snov ili Mailjet | |
| isključene zemlje | pozivari | odluka 5 |
| bez maila | lov A i B, pa provjera, pa Snov ili Mailjet | odluka 6 |

## Lov na mailove (plan)

- **A. 11.785 vinarija s webom, bez maila.** Skripta otvara naslovnicu i stranice kontakta, vadi adrese s iste domene. Postojeći alat: `hetzner:/root/fable_fix/skan_kontakti_1013.py`. Trošak 0. Trajanje nije mjereno; prvo proba na 200.
- **B. 24.285 vinarija bez weba.** Pretraga imena i mjesta na lokalnom jeziku kroz DataForSEO red: 24.285 × 0,0006 USD = 14,57 USD po jednom upitu na vinariju. Nađeni web mora nositi ime vinarije i mjesto, inače se odbacuje (pouka »dokaz mora biti vezan«). Zatim isto kao A.
- **C. 10.956 ispalih na čišćenju i 962 VJEROJATNO.** Web već imamo; tražiti ispravnu adresu na toj domeni. Od toga 2.084 pale samo zbog imena, a web im je potvrđen.
- **D. 11.697 samo besplatni ili PEC.** Gdje web postoji, tražiti adresu na vlastitoj domeni; ostalo ide pozivarima ili u poseban paket.
- Nove adrese ne idu u Snov bez provjere: prvo lokalno (MX, web, ime), u Snov verifikaciju samo SIGURNO i na tvoju riječ.
- Agenti (Opus) samo za presudu gdje skripta nije sigurna. Skripta radi vađenje.

## Odluka

- Matija:
