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

## Odluka (Matija 9.11.)

1. Mailjet runda 2: »da makni« (28 adresa). Slanje i dalje samo na njegovo »šalji«.
2. Snov nacrti K1Z: isti dan kad i Mailjet, »ide drugom infrastrukturom«.
3. Žute u Mailjet rundu 3: da.
4. Besplatni mail kao poseban Mailjet paket: da. »PEC nikad, ali PEC mailove treba staviti da se traži novi mail u lovu.«
5. GR, BR, CY (878): bile su isključene jer nije bilo članka s linkom. »Treba probati njima slati direkt link na profil na karti. Ali u manjim rundama, 150 dnevno. Samo zelene. Uz praćenje spam filtera da nismo na listi nekoj. Paziti jako. I tu testirati koliko bolje ide ako je link.« DACH i ex-YU: nije odlučeno.
6. Lov: s webom ok, »probaj što jače do kraja kroz web«. Bez weba: prvo test na 50, 100, najmanje 200 pretraga na više jezika, uzorak što daje, treba li dodati riječi po jeziku ili adresu; tek onda cijeli prolaz. Ispale na čišćenju: ok, ali prvo vidjeti imamo li pravi web.
