# Mailjet runda 1, SAD: nacrt teksta (30.10.2026.)

**ODLUČI:** pošiljatelj »PR Voice Global« <contact@prvoiceglobal.com>, reply-to ista adresa. Mailjet varijable `{{var:company_name}}`; odjava `[[UNSUB_LINK_EN]]`; podnožje s adresom tvrtke. Link samo na Wine Industry Advisor (isti kao u Snov EN tekstu), nikad na worldwinerymap.com.

## Predmet

`{{var:company_name}} is on the world wine map`

## Tijelo (EN)

Dear {{var:company_name}} team,

I am writing from PR Voice Global, the agency handling media relations for World Winery Map, the digital wine map launched this autumn: more than 4.3 million vineyard parcels and over 104,000 wineries in 90 countries. {{var:company_name}} is one of them.

Wine Industry Advisor covered the launch; the article explains how the map works:
https://wineindustryadvisor.com/2026/09/18/world-winery-map-digitizes-4-3-million-vineyards-and-their-terroir-data-amid-climate-change-2/

From the article you get to the map: search for your winery’s name and click “This is my winery”. With an email address on your winery’s own domain the profile is confirmed automatically. The profile is free: logo, photos, visiting hours, parcels and grape varieties are managed by the winery itself.

If your winery does not show up in the search, reply to this email and we will send you the direct link.

Kind regards,
PR Voice Global
Media relations for World Winery Map
contact@prvoiceglobal.com

---
PR Voice Global is a division of M.G. Solutions d.o.o., Ulica Labinske republike 6B, 52470 Umag, Croatia.
You are receiving this email because your winery is listed on World Winery Map. To stop further messages: [[UNSUB_LINK_EN]]

## HR prijevod

Poštovani tim {{company_name}}, pišem iz PR Voice Globala, agencije koja vodi odnose s medijima za World Winery Map, digitalnu kartu vina pokrenutu ove jeseni: više od 4,3 milijuna parcela i preko 104.000 vinarija u 90 zemalja. {{company_name}} je jedna od njih. Wine Industry Advisor pisao je o pokretanju; članak objašnjava kako karta radi (link). Iz članka se dolazi do karte: potražite ime vinarije i kliknite »This is my winery«. S adresom na domeni vinarije potvrda je automatska. Profil je besplatan: logo, fotografije, radno vrijeme, parcele i sorte uređuje sama vinarija. Ako se vinarija ne pojavi u pretrazi, odgovorite na mail i šaljemo izravni link. Srdačan pozdrav, PR Voice Global, odnosi s medijima za WWM. (podnožje: odjel M.G. Solutions d.o.o., Umag; primate jer ste na karti; odjava = Mailjet link)

## Paketi

- `MAILJET_US_paket1_proba_300.csv`: 300 adresa, sve web POTVRĐENO, nasumično (sjeme 3010)
- `MAILJET_US_paket2_ostatak.csv`: 1.540 (ostatak POTVRĐENO + VJEROJATNO), tek nakon 48 h i bounce < 3 %, prijave 0
- AU 562, NZ 125, CA 212, GB 113 kao zasebne runde (vremenska zona, raspored u Mailjetu)

## Mailjet postavke

- Kontakti: uvoz CSV-a u listu »WWM US r1«, polje `company_name` kao contact property (text)
- Sender: contact@prvoiceglobal.com, ime pošiljatelja »PR Voice Global«; domena prvoiceglobal.com verificirana SPF + DKIM
- Kampanja: bez open/click trackinga (Mailjet: Campaign settings → tracking off), plain + HTML, bez slika
- Slanje: paket 1 odjednom (300), ostatak po 500 dnevno u radno vrijeme SAD-a (16–22 h CET)
- Nakon svakog paketa: izvoz bounce i unsubscribe → DNE lista u Snovu + lokalni ledger
