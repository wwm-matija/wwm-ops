# Struganje popisa vinarija i uvjeti korištenja (stavka 1.11 revizije, kanon t.324)

Status: ODLUČI

## ODLUČI

Šest točaka. Uz svaku moj prijedlog; ispod upiši riječ.

1. **Zamke u popisu** (izmišljeni zapisi koji postoje samo kod nas, kao dokaz kopiranja).
   Prijedlog: DA, 10 do 20 zapisa, raspoređenih po zemljama, skrivenih s karte i iz tražilice, vidljivih samo u podacima koje stroj odnese. Popis zamki čuva se izvan repoa.
   - **Matija:**
2. **Uvjeti korištenja koji izričito brane strojno preuzimanje** podataka karte i popisa vinarija.
   Prijedlog: DA, jedan odlomak u Uvjetima (zabrana automatiziranog preuzimanja, ponovne objave i prodaje popisa; dopušteno indeksiranje stranica za tražilice). Tekst ti donosim na pregled; bez odvjetnika je to izjava volje, ne jamstvo.
   - **Matija:**
3. **Zabrana korištenja za treniranje AI modela** u Uvjetima i u `robots.txt` (GPTBot, CCBot, ClaudeBot, Google-Extended i slični).
   Prijedlog: zabrana za `/data/` i API, a javne stranice i Journal ostaviti otvorene jer nam vidljivost u AI odgovorima koristi.
   - **Matija:**
4. **`robots.txt` za `/data/`**: zabraniti svim robotima.
   Prijedlog: DA. Pošteni roboti poslušaju, nepoštene i dalje zaustavljaju Referer brava i Worker.
   - **Matija:**
5. **Crna lista potpisa** koji su 30.9. do 3.10. odnijeli popis: `WineVaultGlobalDataBuild`, `WineDataResearch`, `DoubaoWorkVM`.
   Prijedlog: DA, dodati u `.htaccess` i u Worker. Zaustavlja samo one koji se ne preimenuju, ali ne košta ništa.
   - **Matija:**
6. **Tko stoji iza prva dva potpisa** (šest adresa u Microsoft Azureu, jedna na Filipinima).
   Prijedlog: NE istraživati dalje. Dokazi su spremljeni i ne brišu se (t.325); istraga ne donosi ništa dok se popis ne pojavi negdje objavljen.
   - **Matija:**

## Zašto pitam

Kanon t.324 (3.10.2026.): popis vinarija je u četiri dana odnesen najmanje osam puta. Svi su slali naš Referer, pa ih brava na
originu nije odbila; odneseno je ime, mjesto, koordinate, država, regija i `wwm_id` za sve vinarije, bez kontakata.
Od 3.10. Worker `wwm-vinarije` zaustavlja svako takvo skidanje na 120 datoteka po adresi. Datoteku sa svim parcelama nitko izvana nije dohvaćao.

Revizija 17.10. (G, točka 15) vodi ovo kao »8 odluka«. Dokument revizije nije preseljen na novi laptop
(`Documents\WWM_REVIZIJA_2026-10-17` je ostao na starom), pa je ovdje šest točaka koje se mogu izvesti iz kanona; ako se sjećaš preostale dvije, dopiši ih.

Napomena 9.11.: novo pravilo keša za `/data/` ne dira ovu zaštitu (shardovi se ne keširaju, keš vrijedi samo za zahtjeve s naše stranice bez robotskog agenta; kanon t.404).

## Odluka
(Matija piše uz svaku točku)
