# Temeljna baza slanja

Jedna SQLite baza u kojoj je sve što je WWM poslao mailom, kome, i što se nakon toga dogodilo.
Datoteka: `out/temeljna/slanja.db` (ne ide u git). Alat: `alati/temeljna_baza.py`. Baza se uvijek gradi iznova iz izvora, u nju se ništa ne upisuje ručno.

## Čemu služi

- Prije svakog slanja: je li adresa već dobila mail, u kojoj temi, i ima li zabranu, bounce ili odjavu.
- Nakon slanja: koliko je poslano po temi i valu, i što se dogodilo (registracija, odgovor, bounce, odjava, objava).
- Jedno mjesto za pitanje »što znamo o ovoj adresi ili domeni«.

## Naredbe

```
py -I alati/temeljna_baza.py mailjet-povuci    Mailjet kampanje i status po poruci (samo čita)
py -I alati/temeljna_baza.py snov-odgovori     tko je odgovorio po Snov kampanji (samo čita, oko 20 min, nastavlja gdje je stao)
py -I alati/temeljna_baza.py gradi             složi bazu iznova i ispiši stanje
py -I alati/temeljna_baza.py stanje            samo ispis brojki
py -I alati/temeljna_baza.py adresa info@vinarija.it     sve o jednoj adresi
py -I alati/temeljna_baza.py adresa @vinarija.it         sve adrese na domeni
```

Redoslijed nakon svakog slanja: `slanje_stanje.py` (svježi popis poslanog iz Snova), `mailjet-povuci`, `gradi`.
Nikad dvije Snov petlje u isto vrijeme (`snov-odgovori` i `slanje_stanje.py` ne idu zajedno).

## Što je unutra

| tablica | što je |
|---|---|
| `kampanja`, `kampanja_tema` | kampanja u Snovu ili Mailjetu: kanal, naziv, tema (jedna ili dvije), val, jezik, domena pošiljatelja, od, do, broj poruka |
| `slanje` | jedan red = jedna adresa u jednoj kampanji |
| `ishod` | što se dogodilo s adresom: registracija, pro, odgovor (Snov), bounce, meki bounce, blokirano, odjava, spam, zabrana, odbijanje, micanje s karte |
| `kontakt` | svaka adresa koju znamo: vrsta (vinarija, medij, institucija, nepoznato), zemlja, naziv, wwm_id |
| `baza`, `baza_clan` | popis baza i lista (vinarije, mediji, institucije, rasporedi valova) i koja je adresa u kojoj |
| `objava` | članci medija o karti (iz `alati/objave.py`) |
| `izvan_wwm` | kampanje klijenata i stare probe: samo naziv i broj poruka, adrese se ne učitavaju |
| `v_slanje`, `v_adresa`, `v_val` | pogledi: slanje s temom, sažetak po adresi i po valu |

Teme se određuju iz naziva kampanje: `B2B` (vinarije), `PR` (mediji), `WINE_NEWS` (poziv medijima na suradnju), `INSTITUCIJE` (WWM regije 17.9.), `TEST`.
Kampanja može imati dvije teme (tablica `kampanja_tema`, pogled `v_slanje`): val niša (WWM NISE 30.10. i Mailjet NISE) u istom mailu nosi poziv za Wine News
i press priču, pa je i `PR` i `WINE_NEWS`. Samo poziv su WWM VINSKI (1.10.) i WWM AGRO, TURIZAM, POSLOVNI (2.10.).

## Izvori

| izvor | gdje | kako se osvježava |
|---|---|---|
| Snov, poslano po kampanji | `out/snov_poslano_sve_0911.json` + `out/slanje_stanje_*.json` | `alati/slanje_stanje.py` |
| Snov, tko je odgovorio | `out/temeljna/izvori/snov_odgovori.json` | `snov-odgovori` |
| Mailjet, poruke i status | `out/temeljna/izvori/mailjet_poruke.json` | `mailjet-povuci` |
| vinarije, registracije, profili | `out/temeljna/izvori/vinarije.csv`, `claims.csv`, `profiles.csv` | izvoz iz `hetzner:/root/wwm_api/wwm.db` (samo čitanje), `scp` |
| zabrane, odjave, bounce | `out/NE_KONTAKTIRATI.csv` | `alati/ne_kontaktirati.py`, `alati/lista_ciscenje.py --osvjezi` |
| objave medija | `out/OBJAVE_SVE.json` | `alati/objave.py` |
| baze medija i institucija, rasporedi valova | `C:/Users/world/stari_laptop_2026-11-11/`, `C:/Users/world/GTWT_baze/` | ne mijenjaju se |

## Što nikad

- Baza ne služi za slanje. Lista za slanje radi se s `alati/lista_ciscenje.py`, a slanje ide samo na Matijinu riječ.
- Tekst odgovora se ne sprema; sandučići se čitaju samo na Matijinu naredbu.
- Adrese klijenata (MC, Bevanda, Sylvie, Elite) ne ulaze u ovu bazu.
