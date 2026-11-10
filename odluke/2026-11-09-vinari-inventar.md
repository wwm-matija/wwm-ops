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

## POSLANO 9.11.2026. (Matija: »šalji oboje«)

- **Mailjet runda 2:** 9 kampanja, 3.963 adrese, oko 14:35 UTC, pošiljatelj PR Voice Global <contact@prvoiceglobal.com>. IT 1.185, FR 1.230, ES 519, LAT 131, PT 186, CS 62, SK 17, ZA 213, INTL 420. Zapis `out/inventar_0911/mailjet_r2_poslano_0911.json`.
- **Snov K1Z (C5):** 19 kampanja upaljeno 14:30 do 14:32 UTC, 1.740 zelenih adresa, limit 25 po sandučiću. Dnevnik `skripte_I/pali_c5_pali_log_0911.txt`, ledger `B2B_LEDGER_1710.jsonl`.
- Prije slanja: probni mailovi 9 od 9 u INBOX (desk@worldwinerymap.org), provjere pošiljatelja prolaze, linkovi rade. S Mailjet lista maknute ukupno 22 adrese: 14 (profil, naša lista, već dobili mail) i 8 pod krivim imenom vinarije (nađeno usporedbom s `MAIL_VAN.csv`). Usporedba s 25 starih izvora sa starog laptopa: drugih poklapanja nema.
- U tekstovima ostaje »90 zemalja« (Matija: »ne mijenjaj zemlje, trajat će predugo«).

## Lov na mailove: rezultat (9.11., oba prolaza gotova)

**Prolaz webova** (31.391 domena, 5.339 s u tri procesa; web radi kod 26.360):

| skupina | vinarija | web radi | mail na domeni weba + ime vinarije | ostalo |
|---|---|---|---|---|
| A bez maila, ima web | 11.546 | 10.012 | 3.968 | samo besplatni mail na webu 1.139; bez maila na webu 3.254 |
| P samo PEC | 439 | 321 | 164 | |
| B samo besplatni mail | 6.737 | 6.026 | 638 | naš mail piše na webu 4.061 |
| C vlastita domena, neposlane | 16.056 | 12.993 | | naš mail piše na webu 9.420; pravi web 12.658 |

**AI način** (26.259 vinarija bez weba, 31,51 USD; svaki mail provjeren otvaranjem izvora, `alati/lov_ai.py ocjena`):

| ocjena | vinarija |
|---|---|
| POTVRĐEN + mjesto (mail, ime i mjesto pišu na izvoru) | 5.826 |
| potvrđen bez mjesta (2.330 jer mjesta nemamo u bazi, 1.462 jer ga nema na stranici) | 3.792 |
| mail na izvoru, ime nije | 1.980 |
| ime na izvoru, mail nije | 1.722 |
| izvor se ne otvara | 2.410 |
| samo PEC ili uprava | 2.966 |
| bez maila u odgovoru | 6.833 |
| ni mail ni ime na izvoru | 729 |

- POTVRĐEN + mjesto: vlastita domena 4.023, besplatni mail 1.803. Po zemlji: IT 2.816, FR 1.248, ES 348, AT 309, US 276, DE 214, CH 183, HU 93. U isključenim zemljama 747, za slanje 5.079.
- Od 1.961 vinarije kojoj je jedini mail PEC, novi obični mail potvrđen je za 276.
- **Zbroj novih mailova po strogom pravilu: 3.968 + 164 + 5.826 = 9.958 vinarija.** U bazu nije upisano ništa.
- Popisi: `out/lov/AI_MAILOVI.csv` (laptop), `hetzner:/mnt/HC_Volume_106719381/lov_mailova_2026-11-09/` (web_rezultat_*.jsonl, ai/).

Otvoreno za Matiju: (1) ~~kako novi mailovi ulaze u bazu vinarija~~ odlučeno 10.11.: u oboje (dolje); (2) Snov provjera novih adresa na vlastitoj domeni (krediti: 3.869 na računu); (3) »potvrđen bez mjesta« 3.792: uzeti ili ručni pregled uzorka.

## Upis novih mailova u bazu i lista za slanje (10.11.2026.)

Odluka Matije 10.11.: »ulaze u oboje, da budu za stalno tu za dalje«. Alat `alati/mail_unos.py` (vrti se na Hetzneru), koraci `--kontekst`, `--plan`, `--pisi`. Kanon t.408.

**Pouka prije upisa.** Uzorak »POTVRĐEN + mjesto« iz AI načina nije izdržao pregled okom: vinarije s osobnim imenom (SCHIAVONE ANTONIO, BARONI ALESSANDRO, Asperger) pogađaju bilo koju stranicu s tim imenom u tom mjestu (sveučilište, nekretnine, bolnica, savjetovalište). Zato je dodana provjera izvora: svaki od 9.958 izvora ponovno otvoren (379 s, 40 niti), traži se bar 2 vinske riječi na stranici i da mail piše na njoj; adrese ustanova ispadaju po adresi; domena iz DOM_VAN ispada; domena koju na karti nosi 3+ vinarija (grupa ili imenik) ne ide u bazu; adresa koju već nosi druga vinarija na karti ne ide u bazu (najčešće dvojnik iste firme pod registarskim imenom, to je posao za WID_SPOJ, ne za upis maila).

| presuda | vinarija |
|---|---|
| u bazu i na listu | 2.963 (od toga 118 uz postojeći PEC, »pec;novi«) |
| samo lista: adresu već nosi druga vinarija na karti | 3.283 |
| samo lista: ista adresa na više vinarija u lovu | 865 |
| samo lista: domenu nosi 3+ vinarija na karti | 826 |
| ni baza ni slanje: izvor se ne otvara pri ponovnom otvaranju | 900 |
| ni baza ni slanje: izvor bez vinskog konteksta | 795 |
| ni baza ni slanje: mail ne piše na izvoru pri ponovnom otvaranju | 106 |
| ispada: adresa ustanove | 124 |
| ispada: PEC/uprava 43, DOM_VAN 8, lista ne kontaktirati 20, MAIL_VAN 15, baza već nosi adresu 9 | 95 |

**Baza (10.11. 05:20 UTC):** 2.963 redaka dopisano u `out/DOM_ISPRAVAK.csv` (ledger, 52 → 3.015 redaka; čitač `dom_ispravak.ucitaj_dom` prolazi; kopija `arhiva/2026-11-10/DOM_ISPRAVAK.csv.prije-mail-unos-202611100520`) i isti UPDATE u živoj `wwm.db` (provjera natrag 0 razlika; kopija zahvaćenih `lov_mailova_2026-11-09/wwm_mail_prije_202611100520.csv`). Vinarija na karti s mailom: 68.179 → 71.024. Ledger je trajna istina, sljedeća gradnja `searchdb.py` ga primjenjuje sama (rani STOP provjeren: svi widovi su u masteru ili trećem ulazu). Mail u bazi je podloga auto-claima, zato u bazu samo nedvosmislene adrese.

**Lista za slanje:** `NOVI_MAILOVI_2026-11-10.csv` (server `lov_mailova_2026-11-09/`, kopija `out/lov/` na laptopu), 9.739 redaka; `za_slanje=da` **5.030** (vlastita domena 3.854, besplatni 1.176), izvan DACH/ex-YU **4.034**; 2.312 adresa već kontaktirano pod drugim zapisom (`slanje_0911/KONTAKTIRANO_ADRESE.txt`, 43.765 adresa). Po zemlji: IT 1.583, FR 980, US 628, DE 442, AT 341, ES 330, CH 167, AU 131, HU 69. Slanje tek na Matijinu riječ (Snov provjera adresa na vlastitoj domeni prije toga).

Zaliha: »potvrđen bez mjesta« 3.792 (nije dirano), »samo lista« 4.974 (dvojnici i grupe: čeka spajanje zapisa).

## GR, CY, BR: izravni link na profil (nacrti složeni 9.11., NIJE upaljeno)

Matija 9.11.: »sredi snov za ove br gr«, tekst odobren (»Da, složi nacrte«). Paljenje tek na njegovo »šalji«.

- Popis iz prolaza webova: 529 adresa (web radi, na njemu ime vinarije ili naš mail). Snov provjera: 370 zelenih (GR 187, BR 162, CY 21), 43 ne valja, 104 nepoznato, 12 neprovjereno. Potrošeno 169 kredita.
- Link u mailu: `https://worldwinerymap.com/?w=<wwm_id>` (otvara kartu na vinariji s gumbom »This is my winery«), u polju `body1` kao doslovan URL.
- Tekst: listopadski K1 tekst, dva odlomka o članku zamijenjena jednim s linkom; predmet isti kao u listopadu.
- **Nacrt 3229376** »B2B K1Z EL izravni link antilalos.eu 0911«: 208 adresa (GR 187, CY 21), lista 41924377, 3 sandučića antilalos.eu (Elena Vlachou), limit 25 po sandučiću.
- **Nacrt 3229385** »B2B K1Z BR izravni link altofalantemedia.lat 0911«: 162 adrese, lista 41924399, 3 sandučića **worldwinerymap.org** (Matija; ime kampanje nosi krivu domenu). Ti sandučići su do kraja kampanje 3214819 (ZA, 13 adresa) u aktivnoj kampanji: paliti tek kad ona završi.
- Proba: grčki tekst na 3 naše adrese (prvoiceglobal.com), 3 od 3 u INBOX, link ispravno upisan. Snov je slao jedan mail na oko 28 minuta po sandučiću.
- Alat i stanje: `C:/Users/world/Documents/WWM_REVIZIJA_2026-10-17/DANAS_1710/skripte_I/faza_grbrcy_0911.py`, `stanje_grbrcy_0911.json`, `verifikacija_grbrcy_rezultat_0911.json`; ledger `B2B_LEDGER_1710.jsonl`.
- Mjera učinka: registracije prema zelenima s člankom (K1Z: 275 na 11.720).

## Izvršeno 9.11. poslije odluka

- **Mailjet runda 2:** maknuto 14 adresa s lista (28 redaka u popisu bilo je 14 različitih adresa; ista adresa visi na više zapisa na karti). Liste sada: IT 1.186, FR 1.234, ES 519, LAT 131, PT 187, CS 62, SK 17, ZA 213, INTL 422, ukupno 3.971. Zapis `out/inventar_0911/mailjet_maknuto_0911.json`. Jedna adresa u Snov nacrtu (info@elingforest.com.au, vinarija već dobila mail na drugu adresu) miče se u provjeri prije paljenja.
- **Lov kroz web** (`alati/lov_priprema.py`, `alati/lov_web.py`): ulaz 31.391 domena, 34.778 vinarija: A bez maila 11.546, B samo besplatni mail 6.737, C vlastita domena izvan isključenih zemalja 16.056, P PEC 439. Proba na 200 domena: 1,44 domene/s po procesu. Cijeli prolaz pokrenut 9.11. 13:02 UTC u tri procesa (`lov-web-0..2`), rezultat u `hetzner:/mnt/HC_Volume_106719381/lov_mailova_2026-11-09/web_rezultat_*.jsonl`.
- Proba 200 domena, skupina A (69 vinarija): web radi kod 60, mail na domeni weba kod 27, samo besplatni 4, samo tuđa domena 7, bez maila na webu 21. Skupina C (107): web radi kod 86, ime vinarije na webu 66, naš mail piše na webu kod 58.
- Bez weba, a s mailom koji ne valja: PEC 1.961 i besplatni 5.544 nemaju upisan web, idu u pretragu zajedno s 24.298 bez ičega.

## Test pretrage, 200 vinarija bez weba (9.11., `alati/lov_pretraga.py`)

Jeftini red DataForSEO, 943 upita, 0,57 USD (po odgovoru API-ja), 11 jezika, 18 zemalja. Pet varijanti po vinariji. Svaki kandidat je zatim otvoren i provjereno piše li na njemu ime i mjesto.

| varijanta | našla web s imenom vinarije | jedina koja ga je našla |
|---|---|---|
| V1 "ime" mjesto | 15 | 3 |
| V2 ime mjesto + riječ za vinariju (lokalni jezik) | 28 | 10 |
| V3 ime mjesto + kontakt email | 15 | 1 |
| V4 ime + adresa | 13 | 0 |
| V5 ime mjesto winery (engleski) | 13 | 0 |

- Web s imenom vinarije: 38 od 200 (19 %). Od toga i mjesto na stranici: 15 (7,5 %). Mail na tim stranicama: 27 od 38.
- V1+V2 nalaze 32 od 38, V1+V2+V4 35, svih pet 38. Adresa i engleski ne donose gotovo ništa novo.
- Prvo sito (ime u domeni ili naslovu) pustilo je 134 kandidata, a 82 su bili imenici i tuđe stranice. Bez otvaranja stranice rezultat se ne smije uzeti.
- Facebook ili Instagram stranica s imenom vinarije pojavila se kod 126 od 200 (nije provjereno otvaranjem).
- Italija: mnogo zapisa su osobna imena iz registra (»BIANCO ALDO«), za njih weba najčešće nema.
- Trošak cijelog prolaza (24.298 + 1.961 + 5.544 = 31.803 vinarije): samo V2 19,08 USD; V1+V2 38,16 USD.

## Drugi test na istih 200: panel znanja, mail u isječku, AI odgovor (9.11.)

Matija: »možeš li pitati onaj AI snippet za te pojmove, pa izvući odgovor, ili knowledge«, »probaj istih 200 tražiti mail direktno pa gledati je li došao u rezultatima«.

| metoda | cijena po vinariji | što je dala na 200 | provjereno otvaranjem |
|---|---|---|---|
| obični rezultati, V1+V2 | 0,0012 USD | 32 prava weba | da, ime na stranici |
| panel znanja (iz istih, već plaćenih upita) | 0 | panel s imenom vinarije kod 128, pravi web kod 22 | da |
| obični rezultati + panel zajedno | | 49 pravih webova | da |
| mail u isječku (svih pet varijanti) | | 71 vinarija, kod 47 mail nosi riječ iz imena | ne |
| mail u isječku, samo upit »ime mjesto kontakt email« | 0,0006 USD | 41 vinarija | ne |
| **AI način** (`serp/google/ai_mode`, upit »ime mjesto email«) | 0,0012 USD | mail u 142 od 189 odgovora | **93 potvrđena** (mail i ime pišu na izvoru), od toga 59 i s mjestom |

- AI način daje tri puta više od obične pretrage za istu cijenu. 58 vinarija je našao samo on, 14 samo obična pretraga. Sve tri metode zajedno pokrivaju 125 od 200.
- Gdje su mail dali i AI i isječak (62 vinarije), isti je kod 42.
- AI odgovor uz običnu pretragu (`load_async_ai_overview: true`, 0,0012 USD) na probi od 3 upita vraća isti sadržaj kao AI način, a u istom zadatku stižu i obični rezultati i panel. To je kandidat za jedini upit po vinariji.
- Zamke koje je test pokazao: kratko ime (»NSP«) prolazi provjeru imena na krivoj stranici; AI zna vratiti mail općine ili zadruge; 12 prvih mailova bili su PEC. Zato pravilo: uzima se samo mail koji piše na izvoru uz ime i mjesto vinarije, bez PEC-a i bez domena uprave.
- AI način ne prima portugalski (`pt`): 11 upita odbijeno bez naplate.
- Trošak testa: 943 obična upita 0,57 USD, 189 AI upita 0,23 USD, proba 6 upita 0,007 USD.
- Cijeli prolaz AI načinom za vinarije bez weba (24.298 bez maila + 1.961 samo PEC = 26.259): 31,51 USD. Besplatni mailovi ne idu u lov (Matija 9.11.: »to ćemo poslati«).

Popisi: `odluke/2026-11-09-lov-pretraga-uzorak.md`, `odluke/2026-11-09-lov-ai-uzorak.md`.

### Treći test: jedan upit, pretraga s AI odgovorom, istih 200 (9.11.)

Upit isti kao u AI načinu (»ime mjesto email«), `load_async_ai_overview: true`, 200 × 0,0012 = 0,24 USD.

| | pretraga s AI odgovorom | AI način |
|---|---|---|
| odgovor AI-ja se pojavio | 143 od 200 | 189 od 189 |
| mail potvrđen iz AI odgovora | 68 (s mjestom 40) | 93 (s mjestom 59) |
| pravi web iz istog upita (panel i obični rezultati), s mailom | 25 | nema |
| **vinarija s potvrđenim mailom** | **79** | **93** |
| isto, bez PT i BR (AI način ih nije primio) | 76 | 93 |

- AI način je bolji: 93 prema 76 na istim vinarijama. Kod obične pretrage Google AI odgovor ne pokaže za 57 od 200 upita.
- Metode se dijelom nadopunjuju: 63 su našle obje, 30 samo AI način, 16 samo pretraga s AI odgovorom, zajedno 109 od 200.
- Prijedlog: svih 26.259 kroz AI način (31,51 USD); PT i BR kroz pretragu s AI odgovorom jer AI način ne prima portugalski. Drugi krug drugom metodom samo za neriješene je moguć kasnije: u testu bi dodao 16 na 200.

## Odluka (Matija 9.11.)

1. Mailjet runda 2: »da makni« (28 adresa). Slanje i dalje samo na njegovo »šalji«.
2. Snov nacrti K1Z: isti dan kad i Mailjet, »ide drugom infrastrukturom«.
3. Žute u Mailjet rundu 3: da.
4. Besplatni mail kao poseban Mailjet paket: da. »PEC nikad, ali PEC mailove treba staviti da se traži novi mail u lovu.«
5. GR, BR, CY (878): bile su isključene jer nije bilo članka s linkom. »Treba probati njima slati direkt link na profil na karti. Ali u manjim rundama, 150 dnevno. Samo zelene. Uz praćenje spam filtera da nismo na listi nekoj. Paziti jako. I tu testirati koliko bolje ide ako je link.« DACH i ex-YU: nije odlučeno.
7. Dopuna 9.11. popodne: Mailjet runda 2 i Snov zelene idu **danas, nakon probnih**; probni mail na naš sandučić koji nije glavna domena. DACH i ex-YU: odgođeno za petak 13.11. GR/BR/CY: link smije ravno na profil na worldwinerymap.com, »ali sporije šaljemo, provjeravaš«. Lov AI načinom za 26.259 bez weba: »može, kreni« (pokrenuto 9.11. 14:54).
6. Lov (dopuna 9.11.): »nemoj loviti ove s besplatnim mailom, to ćemo poslati. PEC samo i ove što nećemo.« Lov: s webom ok, »probaj što jače do kraja kroz web«. Bez weba: prvo test na 50, 100, najmanje 200 pretraga na više jezika, uzorak što daje, treba li dodati riječi po jeziku ili adresu; tek onda cijeli prolaz. Ispale na čišćenju: ok, ali prvo vidjeti imamo li pravi web.
