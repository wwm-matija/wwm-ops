# Mailjet runda 1, Italija: nacrt teksta (29.10.2026.)

**ODLUČI:** tekst ide iz contact@prvoiceglobal.com, pošiljatelj »PR Voice Global«, reply-to ista adresa. Drugačiji od Snov K1Z IT teksta (isti link na WineNews, agencijski glas, bez Matijina imena u pozdravu). Mailjet varijable: `{{var:company_name}}`, `{{var:body2}}`; odjava kroz Mailjetov `[[UNSUB_LINK_IT]]`. Podnožje s pravom adresom (M.G. Solutions d.o.o., Ulica Labinske republike 6B, 52470 Umag, Hrvatska).

## Predmet

`{{var:company_name}} è sulla mappa mondiale del vino`

## Tijelo (IT)

Gentile team {{var:body2}},

Le scrivo da PR Voice Global, l’agenzia che cura le relazioni con i media di World Winery Map, la mappa digitale del vino lanciata quest’autunno: oltre 4,3 milioni di parcelle vitate e più di 104.000 cantine in 90 paesi. Tra queste c’è anche {{var:company_name}}.

In Italia ne ha scritto WineNews; l’articolo spiega come funziona la mappa:
https://winenews.it/it/la-piu-grande-banca-dati-del-vino-a-portata-di-clic-nasce-worldwinerymap-com_603008/

Dall’articolo si arriva alla mappa: cerchi il nome della Sua cantina e clicchi su «This is my winery». Con un indirizzo email del dominio della cantina la conferma è automatica. Il profilo è gratuito: logo, foto, orari per i visitatori, parcelle e vitigni li gestisce la cantina stessa.

Se la Sua cantina non compare nella ricerca, risponda a questa email e Le mandiamo il link diretto.

Cordiali saluti,
PR Voice Global
Media relations per World Winery Map
contact@prvoiceglobal.com

---
PR Voice Global è una divisione di M.G. Solutions d.o.o., Ulica Labinske republike 6B, 52470 Umag, Croazia.
Riceve questa email perché la Sua cantina è presente su World Winery Map. Per non ricevere altre comunicazioni: [[UNSUB_LINK_IT]]

## HR prijevod

Poštovani tim {{body2}},

pišem Vam iz PR Voice Globala, agencije koja vodi odnose s medijima za World Winery Map, digitalnu kartu vina pokrenutu ove jeseni: više od 4,3 milijuna vinogradarskih parcela i preko 104.000 vinarija u 90 zemalja. Među njima je i {{company_name}}.

U Italiji je o tome pisao WineNews; članak objašnjava kako karta radi: (link)

Iz članka se dolazi do karte: potražite ime svoje vinarije i kliknite »This is my winery«. S e-mail adresom na domeni vinarije potvrda je automatska. Profil je besplatan: logo, fotografije, radno vrijeme za posjetitelje, parcele i sorte uređuje sama vinarija.

Ako se Vaša vinarija ne pojavi u pretrazi, odgovorite na ovaj mail i šaljemo Vam izravni link.

Srdačan pozdrav, PR Voice Global, odnosi s medijima za World Winery Map, contact@prvoiceglobal.com

(podnožje) PR Voice Global je odjel M.G. Solutions d.o.o., Ulica Labinske republike 6B, 52470 Umag, Hrvatska. Ovaj mail primate jer je Vaša vinarija na World Winery Mapu. Za odjavu: (Mailjet link)

## Provjere prije slanja

- nema linka na worldwinerymap.com (samo WineNews), nema dugih crtica, nema brojke 100.000, nema nepoznatih varijabli
- Mailjet: SPF `include:spf.mailjet.com` i DKIM `mailjet._domainkey` na prvoiceglobal.com (cPanel DNS), DMARC `rua` dodan
- prvi paket 300 do 500 adresa, 48 h pauza, prag: bounce < 3 %, prijave 0
- bounce i odjave iz Mailjeta na Snov DNE listu i u lokalni ledger
