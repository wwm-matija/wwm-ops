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

## Odluka
(Matija piše ovdje)
