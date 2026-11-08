# Mailovi: pilot s Codexom, otvorena pitanja prije prvog pravog pokretanja

Status: ODLUČI

## ODLUČI

1. **Nesigurne domene** na Namecheapu: `luxurious.fit`, `aesthetic-place.biz`, `sale365.shop`, `cityranking.space`,
   `cityranking.website`, `365promo.shop`. Jesu li to WWM/PR sender domene (skenirati) ili klijentske/tuđe (ne skenirati)?
   Sad su isključene. Preporuka: reci za svaku »naše« ili »klijent«, upišem u `alati/sken_iskljuci.txt`.

2. **Sandučić `matija@mg-solutions.digital`** je isključen iz skena jer je privatan. Ostaje tako? Preporuka: da.

3. **Prvi pravi sken**: od kojeg trenutka? Zadnji stari sken bio je 6.11. 00:48 UTC. Preporuka: `--od 2026-11-06T00:48`,
   pa sve poslije toga ide u prvi izvještaj (3 odgovora i par novih poruka po probi od 8.11.).

4. **Tko smije pokretati slanje**: zasad samo Matija osobno kroz Codex na svom laptopu (ključevi su tamo). Antigravity
   tek kad mailovi prođu tri čista kruga. Preporuka: da.

5. **Pregled s filtrima** (Q10 dodatak): statična HTML stranica `out/PREGLED.html` koju gradi `alati/pregled.py` iz
   `out/POSLANO.csv` i zadnjih skenova (filtri po datumu, sandučiću, vrsti, statusu, tko odobrio; pretraga po primatelju),
   otvara se dvoklikom, bez servera. Alternativa je Artifact na claude.ai (uređuje ga samo Claude). Preporuka: HTML u repou.

## Zašto pitam

- Sken 8.11. (proba, bez upisa, 72 h): Namecheap 73 nove poruke u 42 domene (3 odgovora, 4 nove, 21 bounce, 25 DMARC,
  20 warmup/spam); HostArmada 0 novih u 13 domena. Isključeno 19 domena po `alati/sken_iskljuci.txt`.
- Kod pogrešno isključene domene propuštamo odgovore; kod pogrešno uključene klijentski mail ulazi u WWM izvještaj (AGENTS.md §3.9).
- Stari popis viđenih (82 adrese na laptopu) se ne prenosi; novi popis je po poruci (sandučić + Message-ID) na poslužitelju.

## Odluka
(Matija piše ovdje)
