# DataForSEO: jedini način rada

Vrijedi za svakog agenta i svaki posao. Izvor: Matijin `UPUTE_DATAFORSEO.md` (18.8.2026., dopune 20.8.) i pouke do 9.11.2026.
Prije svakog posla s DataForSEO pročitaj ovu stranicu do kraja.

## Tvrda pravila

1. **Uvijek red (standard queue), nikad live.** `task_post` pa `task_get` po ID-ju. Live je 3,3 puta skuplji (0,002 prema 0,0006 USD) i smije samo za ručnu probu od par upita.
2. **ID zadatka se sprema na disk u istom potezu kad stigne**, u `.jsonl` datoteku, prije ičega drugog. Bez ID-ja je plaćeni rezultat izgubljen.
3. **Kupi se po vlastitim ID-jevima, nikad kroz `tasks_ready`.** Taj popis pokazuje samo zadatke koje još nisi dirnuo.
4. **Plan prije slanja:** broj različitih fraza, jezici, lokacije, broj upita × cijena. Iznad dogovorenog stropa ne šalje se bez Matijine riječi. Alat mora imati tvrdi strop u USD.
5. **Jedna fraza, jedna lokacija po jeziku.** Bez iste fraze po svakoj zemlji, bez dvostrukog slanja (organic + news) ako nije traženo.
6. **Ključ** je u `C:/Users/world/wwm/.env.bevanda`, varijabla `DATAFORSEO_B64` (samo laptop). Šalje se kao `Authorization: Basic <vrijednost>`. Nikad u kod, git, razgovor ni ispis.
7. Google se koristi **kao tražilica**. Adrese i koordinate se ne uzimaju iz Google Mapsa, nego sa stranica koje pretraga nađe.

## Cijene (red, izmjereno iz polja `cost` u odgovoru)

| što | USD po upitu |
|---|---|
| Google organic, do 10 rezultata (`depth` 10) | 0,0006 |
| isto, `depth` 50 | 0,003 |
| upit s operatorom (`site:` i slično) | 0,003 (pet puta više) |
| organic + `load_async_ai_overview: true` (AI odgovor) | 0,0012 |
| Google AI način (`serp/google/ai_mode`) | 0,0012 |
| live, `depth` 10 | 0,002 |

- 1.000 običnih upita = 0,60 USD; 10.000 = 6 USD.
- **Ponovno čitanje je besplatno.** `task_get` (regular, advanced, html) za već plaćen zadatak ne naplaćuje se; provjereno 9.11.2026. na stanju računa. Polje `cost` u odgovoru `task_get` samo ponavlja cijenu slanja.
- Rezultati žive oko 30 dana.
- Stanje računa: `GET /v3/appendix/user_data`, polje `money.balance` (besplatno).

## Postupak

1. `POST /v3/serp/google/organic/task_post`, do 100 upita u jednom pozivu. Polja: `keyword`, `location_name`, `language_code`, `depth`, `tag`.
2. Iz odgovora odmah upiši u ledger: `id`, `keyword`, `tag`, `cost`, `status_code`.
3. `GET /v3/serp/google/organic/task_get/regular/{id}` za obične rezultate ili `.../advanced/{id}` kad trebaš i panel znanja, AI odgovor, lokalni paket.
4. Kupljenje: odmah pa svakih 30 do 60 sekundi. Većina stigne za nekoliko minuta, zadnji znaju trajati do 45 minuta. Javlja se stvarno stanje, ne »traje sat vremena«.

Statusi: 20000 gotovo; 20100, 40601, 40602 još se obrađuje (nije greška); 40501 gotovo uvijek krivo ime lokacije; 40200/40201 nema kredita ili krivi ključ.

## Zamke

- **Turska je `Turkiye`.** Rusije nema kao lokacije: `United States` + `language_code: ru`.
- Imena lokacija: `GET /v3/serp/google/locations` (besplatno), u alatima keširano u `out/objave/dfs_locations.json`.
- U običnom obliku filtriraj `type == "organic"`. U naprednom obliku stižu i `knowledge_graph`, `ai_overview`, `local_pack`, `people_also_ask`.
- AI odgovor u običnom zadatku stiže prazan; tekst se dobije samo uz `load_async_ai_overview: true` pri slanju.
- Isječak pretrage opisuje najpoznatiji posao tog imena. Nađeni web ili mail vrijedi tek kad je vezan uz našu vinariju (ime i mjesto na stranici).

## Alati u ovom repou

- `alati/objave.py`: pretraga objava (plan, posalji --strop, kupi).
- `alati/lov_pretraga.py`: web vinarija bez weba (plan, posalji --strop, kupi, ocjena).
- Novi posao: preuzmi postupak iz ovih alata, ne piši novi kolektor.
