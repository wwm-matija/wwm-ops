# Granice: zamjena geometrije EuroGeographicsa (stavka 4.13 revizije, kanon t.316)

Status: ODLUČI

## ODLUČI

1. **Izvor za hrvatska vinogorja (72 regije).** geoBoundaries za Hrvatsku ima općine (560 jedinica), ali pod licencom
   CC BY-SA 2.0 (izvedeno iz OpenStreetMapa): tko gradi na tome, mora svoje izvedeno dati pod istom licencom.
   Državna geodetska uprava (Registar prostornih jedinica) daje iste općine pod Otvorenom dozvolom RH: samo navođenje izvora.
   Preporuka: **HR iz DGU-a**, ES i FR iz geoBoundaries (obje samo uz navođenje izvora).
2. **Kad.** Posao traži novo pečenje regija i objavu karte. Preporuka: poslije starta Wine Newsa, osim ako želiš ranije.

## Što je izmjereno (9.11.2026., ništa nije mijenjano)

Odluka vlasnika 9.11.: »Zamijeni geoBoundaries«. Opseg na serveru (`/root/vino_world/regions2.geojson`, 9.124 regije):

| sloj | regija | kako je građeno | što piše u izvoru |
|---|---|---|---|
| hrvatska vinogorja (`HR-vg-*`) | 72 (10.425 točaka geometrije) | unija općina po Pravilniku NN 76/2019 | »Eurostat GISCO LAU 2023 (© EuroGeographics)« |
| podzone ES (`ES-sz-*`: Rioja, Navarra, Rías Baixas) | 13 | unija općina po pliegu | LAU 2023 |
| IGP i VT zone ES (`ES-igp-*`) | 42, od toga 8 izravno na NUTS 2021, ostale po popisu općina | LAU 2023 / NUTS 2021 | © EuroGeographics |
| IGP zone FR (`FR-igp-*`) | 73, od toga 21 na granici departmana s geo.api.gouv.fr (Licence Ouverte, **nije problem**), oko 52 po popisu općina | LAU 2023 / NUTS 2021 | © EuroGeographics |
| ostalo | 2 (crémant, Sainte-Foy) | LAU | |

U izvoru doslovno LAU nosi 88 regija; s onima građenim po popisu općina i na NUTS-u opseg je **oko 170 regija od 9.124**.
Ulazna datoteka: `/root/vino_world/vinogorja/LAU_2023.geojson` (127 MB). Popisi općina po regiji i skripte gradnje su 8.9.
preseljeni u `/mnt/wwm/arhiva/predaja_2026-09-08/vinogorja` (povrat opisan u `POVRAT.md` ondje).

Što nudi geoBoundaries (provjereno kroz njihov API 9.11.):

| zemlja | razina općina | jedinica | licenca | izvor |
|---|---|---|---|---|
| Hrvatska | ADM2 | 560 | CC BY-SA 2.0 | OpenStreetMap |
| Španjolska | ADM3 | 8.205 | CC BY 4.0 | IGN, Registro Central de Cartografía |
| Francuska | ADM5 | 35.010 | ODC-By 1.0 | Republika Francuska |

## Plan (kad odlučiš)

1. Vratiti popise općina po regiji iz arhive od 8.9. u probnu mapu (ne u živo).
2. Skinuti nove granice općina (HR, ES, FR) i spojiti po šifri općine (LAU šifra = matični broj općine / INE / INSEE).
3. Ponovno izgraditi oko 170 poligona unijom, usporediti svaki sa starim (površina, pomak ruba), popis razlika većih od praga.
4. Probno pečenje regija kroz omotač samo za čitanje, provjera da nijedna vinarija ni parcela ne promijeni regiju bez razloga.
5. Zamjena u `regions2.geojson` s kopijom, izmjena redaka izvora u `gradi_izvore.py`, pečenje, objava, red u kanon.

Trajanje ne procjenjujem; korak 3 ću izmjeriti na 10 regija i onda dati brojku.

## Proba na 10 regija (9.11.2026., pomoćni agent, ništa živo nije mijenjano)

Izvještaj: `hetzner:/mnt/HC_Volume_106719381/proba_granice_2026-11-09/IZVJESTAJ_PROBA_GRANICE.md`. Rađeno po službenim izvorima, ne geoBoundaries.

Izvori, sva tri se skidaju bez prijave: HR DGU INSPIRE Upravne jedinice (556 jedinica, šifra = matični broj); ES IGN WFS INSPIRE (CC BY 4.0); FR ADMIN EXPRESS COG 2026 (Licence Ouverte 2.0).

| regija | razlika površine | najveći pomak ruba | vinarija mijenja stranu |
|---|---|---|---|
| HR Hvar | -0,28 % | 5.734 m (otočići) | 0 |
| HR Srijem | +0,58 % | 4.046 m (Dunav, sporna granica) | 0 |
| HR Daruvar | -0,33 % | 451 m | 0 |
| HR Zelina | +0,27 % | 1.066 m | 0 |
| ES Rioja Alavesa | -0,11 % | 244 m | 0 |
| ES Valdizarbe | -0,02 % | 229 m | 0 |
| ES Bailén | -0,14 % | 559 m | 0 |
| ES Ribera del Jiloca | -0,05 % | 252 m | 0 |
| FR Côtes de Thongue | -0,01 % | 343 m | 1 (52 m od ruba) |
| FR Côtes du Tarn | +0,04 % | 396 m | 0 |

Strojno vrijeme: jednokratno 382 s, po regiji 0,19 do 2,50 s; izračun za 171 regiju oko 9 minuta. Ljudski pregled i lanac objave nisu mjereni.

Što je proba otkrila, a traži odluku ili pregled:
1. **Greška na današnjoj karti:** vinogorja Hvar, Krk, Korčula i Vis pokrivaju samo istoimeni grad, ne otok (Hvar 75,9 od 313,4 km², Krk 107,2 od 427,7, Korčula 111,8 od 276,2, Vis 53,6 od 101,1). Za cijeli Hvar u vinogorje bi ušlo još 13 vinarija. Brač je ispravan.
2. **Licenca DGU nije jednoznačna:** data.gov.hr navodi Otvorenu dozvolu, a ATOM zapis istog skupa piše »ograničenje javnog pristupa prema članku 13. stavku 1. točki (e) INSPIRE Direktive«. Treba presuditi prije upotrebe.
3. Popisi općina su na Storage Boxu (`wwm/arhiva_hladno/2026-09-20/predaja_2026-09-08`), ne na volumenu. HR i FR imaju samo imena, Rioja i ES-igp šifre, za Navarru i Rías Baixas popisa nema; skripte gradnje za ES i FR nisu nađene. Arhivski popis Rioja Alavesa je zagađen (4 krivo sparene općine).
4. Srijem: 11 km² uz Dunav dolazi iz katastarske granice DGU-a; ide pod doktrinu teritorija.
5. Nije mjereno: 8 ES-igp regija na NUTS 2021, rez Zagreba Savom, Plešivica po katastarskim općinama, parohije Rías Baixas.

Predloženi prag za »normalno«: razlika površine do 1 %, simetrična razlika do 4 %, pomak ruba do 600 m, nijedna nespojena šifra, vinarija koja mijenja stranu najviše 100 m od ruba. Otoci, sporne granice i podijeljene općine uvijek na pregled.

## Puna proba, svih 179 regija (9.11.2026., izvještaj pomoćnog agenta; brojke nisu ponovno mjerene)

Datoteke: `hetzner:/mnt/HC_Volume_106719381/proba_granice_2026-11-09/` (`IZVJESTAJ_PUNA_PROBA.md`, `kandidat_regije.geojson`, `USPOREDBA_SVE.csv`, `VINARIJE_MIJENJAJU.csv`, `licenca_dgu/`). Ništa živo nije mijenjano.

**Licenca DGU:** data.gov.hr za skup navodi Otvorenu dozvolu; INSPIRE metapodaci kažu da su uvjeti ponovne uporabe u skladu s otvorenom dozvolom i da nema ograničenja javnog pristupa; ATOM zapis spominje ograničenje pristupa po čl. 13. i proturječi metapodacima. Po NN 67/2017 (čl. 4. i 5.) komercijalna uporaba je dopuštena uz navođenje izvora i datuma izmjene. Ocjena agenta: za korištenje vrijedi Otvorena dozvola, ATOM je pogrešna oznaka pristupa.

**Vinogorja koja ne odgovaraju Pravilniku NN 76/2019** (danas / po Pravilniku, km²): Hvar 75,9 / 313,4; Krk 107,2 / 427,7; Korčula 111,8 / 276,2; Pag 154,7 / 317,8 (fale Novalja, Kolan, Povljana); Rab 75,9 / 102,1 (fali Lopar); Vis 53,5 / 101,1; Zadar-Biograd 1.290,9 / 1.303,4 (fali Tkon). Sedam, ne četiri.

**Izgrađeno:** HR 72 (po Prilogu I.), ES 55 (32 po čistom popisu, 8 po službenoj granici IGN-a, 15 izvedeno iz današnje geometrije), FR 52 (izvedeno; propisi daju samo imena). 21 FR-igp na departmanima nije dirano.

**Ocjena po pragu:** 58 normalno, 121 na pregled (HR 29/43, ES 14/41, FR 15/37). Razlozi pregleda: pomak ruba iznad 600 m (81), podijeljene općine (37), simetrična razlika iznad 4 % (24), otoci (21), nespojene šifre (13 FR regija, 41 općina koja je u međuvremenu spojena). Tri regije su na spornoj granici na Dunavu; Baranja +8,62 % površine.

**Vinarije:** 91 mijenja regiju; 50 ulazi u ispravljena otočna vinogorja, 59 je dalje od 100 m od ruba.

**Samo približno, kao i danas:** Plešivica-Okić, Zagreb i Vukomeričke gorice (rez Savom), Rías Baixas (parohije), Navarra (concejos), 11 ES-igp koje uzimaju dijelove općina. Sveta Jana nije izgrađena (definirana katastarskim općinama).

**Trajanje:** cijeli prolaz 441,7 s; jednokratna priprema 382 s.

**Otvoreno za Matiju:** (1) prihvaća li ocjenu licence DGU; (2) prag od 600 m baca 81 regiju na pregled, vjerojatno je prestrog za velike regije: pregled po uzorku ili prag razmjeran veličini; (3) ispravak svih sedam vinogorja, ne samo četiri; (4) 59 vinarija koje mijenjaju regiju daleko od ruba treba pogledati prije zamjene.

## Odluka
- Matija 9.11.: »ok, kreni«, po čistoj varijanti (službeni nacionalni izvori), odmah.
- Matija 9.11.: otočna vinogorja (Hvar, Krk, Korčula, Vis) ispraviti na cijeli otok u istom poslu.
- Otvoreno: licenca DGU (točka 2 gore) i pregled iznimaka iz pune probe prije zamjene i objave.
