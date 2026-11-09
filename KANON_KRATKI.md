# KANON KRATKI

Sažetak zadnjih 30 radnih paketa iz `/root/vino_world/SUSTAV_RADA.md` (ukupno paketa: 320, najnoviji t.405). Napravio `alati/kanon_kratki.py` 09.11.2026. 10:33 UTC. Ovo je izvod, ne izvor: kod neslaganja vrijedi veliki kanon.

Čitaj odozgo: najnoviji paket je prvi. Za svaki: što je napravljeno (naslov), pouke, što je ostalo otvoreno.

## t.405 · 9.11.2026. · bez objave (Access uzivo 9.11.)

**/admin NA api.worldwinerymap.com IZA CLOUDFLARE ACCESSA (P0 OD 14.9. ZATVOREN, t.178 I REVIZIJA G ODLUCI 1)**

(9.11.2026.; vlasnik: »Da, zatvori (preporuka)«, »Gmail s računa«, »Uključeno«)

Biljezi: `ADMIN-ACCESS-2026-11-09`

Pouke: Ovlast »Access: Apps and Policies« postoji na razini zone i racuna; zonska radi kroz /zones/<zona>/access/apps, racunski put vraca 403. Access se ne moze ukljuciti kroz API, prvi put samo u sucelju.

Otvoreno: Vlasnik da jednom proba prijavu na /admin. Token wwm-pravila i dalje bez roka i s DNS Edit: obrisati ili postaviti rok. Razmotriti i /api/admin/* iza Accessa (obrana ako kljuc procuri) kad se potvrdi da nista izvana ne zove taj put.

## t.404 · 9.11.2026. · bez objave (CF pravilo uzivo 9.11.)

**SUSTAV RADA wwm-ops USPOSTAVLJEN (8.11.); 9.11.: RARECLOUD KLJUC MAKNUT S HETZNERA, CLOUDFLARE CACHE RULE ZA /data/ (BEZ shards, SAMO S NASE STRANICE), REVIZIJA NEISPUNJENOG U odluke/ (100 STAVKI), PRVIH 8 ODLUKA VLASNIKA**

(9.11.2026.; vlasnik: »Da, makni (preporuka)«, »reci sto moram odmah za to, ne cekam petak s popravcima«, »daj mi kakav token oces za to da ti sredis«)

Biljezi: `WWM-OPS-2026-11-08`

Pouke: (1) Rubni kes zaobilazi brave origina: prva verzija pravila (cijeli /data/) kesirala je i shardove s tockama vinarija i davala kesirane datoteke curlu i python-requestsu, koje .htaccess odbija; otkriveno u provjeri za par minuta, shardovi izuzeti, a kes suzen izrazom na zahtjeve koje bi i origin pustio (Referer nase stranice, agent nije robot). Provjera: preglednik s nasim Refererom HIT; bez Referera DYNAMIC 200; curl, python i tudji Referer 403. Svako buduce pravilo kesa prvo procitati .htaccess origina. (2) Bash heredoc u ovom okruzenju gubi dvostruke kose crte: skripte s putanjama pisati alatom Write ili s kosim crtama naprijed. (3) sken.py --od je UTC (posluzitelji imaju lokalne zone).

Otvoreno: Token wwm-pravila nema rok i ima DNS Edit vise nego treba: vlasnik da postavi rok ili ga obrise nakon /admin posla. /admin kroz Cloudflare Access ceka ukljucen Zero Trust na racunu i adresu vlasnika. Kopije (alarm, proba povrata, kljuc Boxa kod vlasnika) cekaju odgovor. Podsjetnik 12.11. za CF tokene i zamjenu Resend kljuca i WAF tokena. 92 stavke revizije bez odgovora. Objave vala nise: 339 upita poslano 8.11. (1,017 USD), 275 pokupljeno, kandidate i upis radi Codex po upute/pr_objave.md.

## t.403 · 8.11.2026. · bez objave

**MAILOVI 8.11.: prvi redovni pregled, 4 poruke za čitanje, 0 zahtjeva za micanje**

(8.11.2026.; vlasnik: »mailovi«)

Biljezi: `MAILOVI-SKEN-2026-11-08`

Pouke: Za izričit početak u UTC-u postaviti TZ=UTC. Prvi prolaz počeo je u 05:48 UTC zbog lokalnog vremena poslužitelja, dopunski sken našao je još 6 strojnih poruka. Riječ delete u upitu Fox Run odnosila se na odabir Worda.

Otvoreno: Fox Run Vineyards, San Leonardo, Kalyan Kumar i Dutchbloggeronthemove čekaju Matijinu riječ za daljnju provjeru.

## t.402 · 5.11.2026. · bez objave (API i nginx uzivo 10:19 UTC)

**ADMIN RED 5.11.: 15 TEKSTOVA PUSTENO (9 EN PRIJEVODA), NGINX 503 NA SLIKAMA POPRAVLJEN (limit_conn 96 ZA /uploads/), STARE KOPIJE KONFIGURACIJE VAN IZ sites-enabled; DOKUMENT ODLUKA ZA OSTATAK REDA**

(5.11.2026., 04:30 do 10:25 UTC; vlasnik: »daj mi vidi ove tekstove provjere greske i to da prvo sredimo..api sucelje«, »rijsi prijevode, pusti web u tekstu... objavi, a za kopeceka, istrazi«, »popravi 3, kopeceka moram razmislit«)

Biljezi: `ADMIN-RED-2026-11-05`, `LIMITCONN-UPLOADS-2026-11-05`

Pouke: (1) kopije konfiguracije NIKAD u sites-enabled/ ni conf.d/ (nginx ucitava sve); kopije u /etc/nginx/kopije/. (2) HTTP/2 i limit_conn: svaki stream je veza; galerija = 12+ veza. (3) admin handler se smije pozvati test clientom uz je_admin zamijenjen (bez kljuca iz .env), trag u admin_trag tada ne nastaje. (4) `cat > "$PRAZNO/x"` opet zapeo (TMPDIR prazan): skripte samo Write + scp.

Otvoreno: odluke 2 i 4 do 8 iz dokumenta (Kopecek, retencija --ipak, 406 upozorenja, 100 slika, 2 journala, webhook); odgovori vinarima za 4 prijave; uplata Carpate Diem do 18.11.; revizija sustava rada krug 1 (Q1 do Q7) ceka odgovore.

## t.401 · 4.11.2026. · #112 (prazna), #113 (vinarije, SHV 202611041410), #114 (plocice v28, karta v10083, SHV 202611041746)

**PRVI PRO KUPAC U PRVOM SATU: CARPATE DIEM (SK) PONUDA P-2026-0002, PRO UKLJUCEN PRIJE UPLATE NA 14 DANA; DVOJNIK RIJESEN (OBJAVE #112 PRAZNA, #113); OBJAVA #114: PLOCICE v28 + KARTA v10083 (PETI PAKET OBRISA, 6 U 4 ZEMLJE, 4.307.739 PARCELA); BRAVA LJUDSKOG SLOJA: KLJUC KOJEG NEMA U ZIVOJ NIJE GUBITAK (BRAVA-NEZIVA-1104)**

(4.11.2026., 12:30 do 17:52 UTC; vlasnik: »NOVI JE GOLD ZATRAZIO NE VIDIM UPLATU JOS. PREGLEDJ SVE O NJEMU«, »rijesi dvojnika, odobri mu to i ispeci sve«, »ajmo mu aktivirat gold, pa ak ne dode u 14 dana uplata maknuti«, »aktiviraj i salji«)

Biljezi: `PRIVREMENO-PRO-2026-11-04`, `DVOJNIK-CARPATE-2026-11-04`, `V28-DRW5-2026-11-04`

Pouke: (1) `python skripta | cut` u `&&` lancu skriva pad skripte (izlaz je od `cut`): u lancima bez pipea ili `set -o pipefail`; zbog toga je #112 krenuo prazan. (2) Brava ljudskog sloja cuva od gubitka u OVOJ zamjeni; sve sto vec nije u zivoj `parcele` ne moze se izgubiti, pa provjera ide: parcele_novo -> ziva parcele -> napomena. Zakrpe po jednom slucaju (SKRIVENO-1021, ISPOD-1104) bile su krpanje simptoma. (3) Pro prije uplate = redak pretplate s kratkom obnovom, nista drugo; sustav sam salje »plan is now Pro« pa nas mail to ne smije ponavljati. (4) Dva susjedna obrisa iste vinarije uvijek u `WWM_RUCNI_PAROVI`, i kad su 180 do 300 m. (5) Nastavne skripte: `grep -c` upisnih koraka = 0 prije pokretanja (drzalo).

Otvoreno: `tiles/generacije.json` status ostaje »CEKA OBJAVU« i za zive generacije (ZIVO_5 ne azurira); kontrola_20 t.26 »PAD press: 102 stranice bez jezika s popisa paketa« star od v27 ili ranije; volumen 81 %: v25 i starije na Box (dvije generacije unatrag ostaju); uplata Carpate Diem do 18.11. (admin »Uplata primljena«), inace cron gasi 19.11. i treba kratki mail; Sottoilnoce dvojnici; CF Cache Rule i tokeni 13./15.11.; odgovori (Kathryn i 7 medija, Lyons, Ve Oh Lay, Traerte, Kristancic); Mailjet r2; revizija sustava rada krug 2.

## t.400 · 4.11.2026. · #110 (vinarije, SHV 202611040445) i #111 (plocice v27, karta v10082, SHV 202611041146)

**OBJAVA #111: PLOCICE v27 + KARTA v10082 (CETVRTI PAKET OBRISA VINARA WWM-DRW-<CC>-1104, 66 U 12 ZEMALJA; 4.307.734 PARCELA); OBJAVA #110 (LANAC VINARIJA): 12 PRIJAVA S KARTE RIJESENO, 7 SKRIVENIH, 1 SPOJ, TIDEWATER I LUNELLI; BRAVA LJUDSKOG SLOJA POJACANA (BRAVA-ISPOD-1104); CHELSA KES 1981-2010 NA /mnt/wwm/kes_chelsa_1981_2010**

(4.11.2026., 06:00 do 11:52 UTC; vlasnik: »1. napravi to sve 2. odradio ja 3 odradi 4. kakav token trebas za to 5. odgovore poslje 6 i 7 kasnije«)

Biljezi: `V27-DRW4-2026-11-04`, `PRIJAVE-2026-11-04`, `OBJAVA110-2026-11-04`

Pouke: (1) BRAVA-SKRIVENO-1021 je vrijedila samo dok je skrivena parcela jos u zivoj `parcele`; od iduce generacije kljuc nestaje i brava laze gubitak -> k->pid mora ici i iz ledgera skrivenih ispod nacrtanih (sad jest). (2) `cat > "$PRAZNO/x"` bez stdin-a u lokalnoj ljusci visi zauvijek i pojede heredoc: skripte na server iskljucivo Write + scp. (3) Nastavni ZIVO_*_4d sklapati brojanjem redaka iz izvornika je krhko (dvaput krivi redci, jednom bi ponovio migraciju --pisi): prije pokretanja `grep -c` za svaki upisni korak (migracija --pisi, uvoz_baza, digni_plocice) mora biti 0. (4) Lanac vinarija donosi nove zemlje -> `_cc_jezik.json` treba popuniti u istom paketu (test 3s). (5) Zivi map.js portala je `js/map.js`, ne `/map.js` (ta putanja vraca index).

Otvoreno: CF Cache Rule /data/* (token Zone.Cache Rules.Edit u `/root/.env.cloudflare` kao CF_CACHE_RULES_TOKEN, vlasnik); odgovori (Kathryn + 7 medija, Lyons, Ve Oh Lay, Traerte + 3 granice, Kristancic, Piedras Blancas ne treba); Sottoilnoce dvojnici (vlasniku); Mailjet r2; CF tokeni rok 13./15.11.; stari atributi v26 na Box za koji dan; 3 obrisa 989/990/992 za iduce pecenje.

## t.399 · 4.11.2026. · bez objave

**SELIDBA PROSTORA: SUSTAVNI DISK 62 -> 22 GB (31 %), 7 ULAZNIH MAPA PECENJA NA VOLUMEN SA SIMLINKOM, 26 GB NA STORAGE BOX, n8n I qdrant ARHIVIRANI I MAKNUTI, VACUUM wwm.db 4,06 -> 1,82 GB**

(4.11.2026., 06:23 do 06:42 UTC; vlasnik: »sto nam puni disk ne kuzim???? cistili smo nedavno«, »sto sa sistemskog moze na volume? a sto s volume u arhivu?«, »rekli smo n8n i qdrant i sve od projekata starih da nam ne treba, stavi u arhivu, i ostalo ovo odradi«)

Biljezi: `SELIDBA-2026-11-04`

Pouke: (1) **`/mnt/wwm/arhiva/ciscenje_2026-09-03` NIJE arhiva**: u njoj je `enrich_kes/chelsa` (38 rastera, 9,9 GB) iz kojeg citaju `alati/dopuna/k10_klima_dodatno.py` i `k11_srad.py` (KES = ...). Prva selidba je stala na sukobu imena s kopijom od 21.10. na Boxu (rsync 23) prije micanja; brava je spasila pecenje kao sto 21.10. nije (modis). Mapu NIKAD ne seliti; kes bi trebalo preseliti u `kes_chelsa_2011_2040` i ispraviti KES u k10/k11 (otvoreno). (2) Provjera referenci prije selidbe mora obuhvatiti `alati/dopuna/*.py`, `enrich/*.py`, `PROBA_teren/*.py`, `searchdb.py`, `retencija.sh`, ne samo alati/*.sh. (3) Od sada pecenje cita 7 ulaznih mapa s volumena (mrezni disk): korak obogacivanja ide sporije; peci `mv tiles/parcels.geojsonl /mnt/wwm/arhiva/vN_*` ce premjestiti SIMLINK, cilj ostaje u s_glavnog_diska. (4) wwm.db ne vraca prostor sam: VACUUM nakon svakog vecih brisanja tablica.

Otvoreno: CHELSA kes u ispravnu mapu; stara baza atributa v26 bez indeksa (1,5 GB) na Box nakon par dana; kopija wwm.db prije vacuuma ide u retenciju; pecenje lanca da sam arhivira prethodnu generaciju na Box.

## t.398 · 4.11.2026. · #109 (sardovi + trazilica + portal; MAPV/SHV nepromijenjeni)

**OBJAVA #109 (LANAC VINARIJA + PORTAL, PRVI OD 29.10.): 4 ZAPISA SKRIVENA NA ZAHTJEV VLASNIKA (TWO SISTERS / STONE EAGLE, NIAGARA); INDEKS `a_k` U parcele_atributi (/winery/ 15,8 s -> 0,013 s); DIJAGNOZA SPOROSTI KARTE (CF NE KESIRA /data/*.json, ORIGIN NAMECHEAP SAD); MAILJET B2B RUNDA 30.10. NAKNADNO UPISANA; 3 NOVA ODGOVORA MEDIJA**

(4.11.2026., 03:40 do 05:00 UTC; vlasnik: »brisi s karte te sto zele brisanje«, »da se update sve u pravo na karti«, »karta steka zadnjih dana... jel se moze ubrzat«)

Biljezi: `OBJAVA109-2026-11-04`

Pouke: (1) `grep -o "| 395 |.\{0,3000\}"` nad kanonom (6.300 redaka) stoji minutama i ssh ga ne prekida: redak kanona vaditi s `grep -n` + `sed -n Np`; `pkill -f` s uzorkom iz iste naredbe ubije vlastiti ssh (exit 255). (2) Svaka nova baza iz pecenja mora imati indeks po svakom stupcu po kojem se trazi; `EXPLAIN QUERY PLAN` prije pustanja, cProfile prije nagadjanja. (3) Dijagnoza sporosti: prvo `cf-cache-status` i `time_starttransfer` po hostu iz preglednika, karta nije na Hetzneru. (4) Sken odgovora mora obuhvatiti i HostArmada sanducic (PR Voice); Mailjet stanje citati iz API-ja (campaigndraft Status 2 = poslano). (5) `alati/atributi_parcela.py` i `report.py` zive i u journal generatoru, pa i u gunicornu (t.397).

Otvoreno: CF Cache Rule (vlasnik); pecenje plocica za 17 nacrtanih vinograda (disk / 86 %, 11 GB); Tidewater i Lunelli odluke; odgovori Lyons/Ve Oh Lay/Kathryn i 7 medija; r2 Mailjet nacrti; Kristancic dobrodoslica; 12 prijava s karte pending.

## t.397 · 3.11.2026. · bez objave (samo wwm-api)

**JAVNA STRANICA /winery/<w> = CLANAK JOURNALA, UZIVO IZ GENERATORA (t.386 ZATVOREN); NAZIV VINOGRADA I U CLANKU; PRVI KARTICNI PRO KUPAC (WINERY KRISTANCIC, SI); KARTA I PLOCICE NEPROMIJENJENE, BEZ OBJAVE**

(3.11.2026., 15:30 do 16:20 UTC; vlasnik: »e to oko javnih stranica, to moramo sad popravit ... ugl, to treba bit isto ko clanak na naslovnoj, on je ok«)

Biljezi: `CLANAK-UZIVO-2026-11-03`

Pouke: (1) `gradi_journal_vinarije.py` i `journal_predlozak.py` od danas zive i u gunicornu (ucitani po putanji, grep po imenu modula u wwm_api ih NE nalazi, kao zaglavlje.py): svaka njihova izmjena trazi `systemctl restart wwm-api` da stigne na /winery/<w>, i postupak §4.7 vrijedi i za njih; (2) stranice koje sluzi api. ne mogu uzeti /fonts/ s portala (nema CORS), pisma idu iz `lib/pisma.css`; (3) na api. je CF Email Obfuscation + CSP bez skripti = necitljiva adresa; `<!--email_off-->` je lijek; (4) `--red` cron NE prepeca clanak kad se mijenja generator, samo `--sve` (04:40).

Otvoreno: Pomfyjev objavljeni clanak dobiva nazive parcela (Grefty, Letne...) tek u 04:40 prolazu; 3 stara LOSE u test_novo (»admin vidi brojke po vinariji« LIMIT 100 od 6.10., »_cc_jezik.json pokriva 97 zemalja«, »provjeri_jezike.py: 11 provjera«) nisu od ovoga; Kristancicu nije poslana dobrodoslica (ceka rijec vlasnika).

## t.396 · 30.10.2026. · objavljeno #105, #107, #108; Snov UPALJENO 30.10. ~05:00 UTC, 64 kampanje / 4.982 primatelja

**VAL »NISE«: PR NISNIM MEDIJIMA (TURIZAM, TEHNOLOGIJA, POSLOVNO, FINANCIJE, AGRO, STARTUP), 236 PR TEKSTOVA NA 35 JEZIKA (183 DRZAVNIH + 53 REGIONALNA), PRESS NA 15 SENDER DOMENA I NA PORTALU (OBJAVA #105, SHV `202610290829`), SNOV NACRTI 64 KAMPANJE / 5.440 ADRESA**

(29.10.2026., 06:00 do 09:00 UTC; vlasnik: »opce smo slali jucer vecinom, necemo to danas. i necemo vinske... ali ocemo sve ovo drugo«, »ex yu van komplet«, »jezik treba bit onaj kojim medij pise«, »C da, regija di je mapirano, rusija ne«, »u mail treba uplesti i prijedlog suradnje wine news«, »nisne recenice ne trebaju, jedino kod startupa«, »svaki pr mora i na glavnoj bit kopija«, »fable provjeri jesu tekstovi kao da je pisao native novinar«)

Biljezi: `WT-NISE-2026-10-29`

Pouke: 1) uzorak vlasnika imao »regije/drzave« u naslovu, brief 27.10. to izgubio: rupa {REGIJA} obavezna; 2) pregledi mailova moraju citati i tekst ISPOD citata (Wine Art Culture »da« od 2.10. 27 dana neodgovoren); 3) `regija` u listi je pokrajina, mapiranje na vinsku regiju samo kroz 19.9. tablicu, ostalo drzava; 4) auto mode klasifikator blokira Snov POST i archive: vlasnik daje dozvolu izricito; 5) 24 prazne Active kampanje od 2./3.10. jos stoje u Snovu (arhiviranje blokirano). **DOPUNA 29.10. popodne (10:00 do 15:00 UTC) <!-- WT-NISE-2026-10-29-C -->:** probni mailovi (5 kampanja, sklopljeni lokalno iz istih polja, poslani sendmailom s cPanel servera s pravom adresom sendera na press@worldwinerymap.com; SPF pokriva 66.29.141.137) otkrili: a) body polje OPET s {{naslov}}/{{Hook}} (digni_nise.py kopiran iz digni_lokvin.py prije popravka od 27.10.) -> `popravi_body_nise.py SVE` (doslovan naslov i link, sva 4 polja, ledger); b) sklapanje u `gen_press_nise.py`: literal IZOSTAJE u GB_en bazi (50 EN stranica), rastavljac recenica na »nr.« (RO dupla recenica), odlomak izvora po podnizu »38« hvatao 438 m / 1.838 m (22 EN teksta), CJK bez razmaka iza 。 (US_zh-cn), startup fallback `startup_recenice.json` (16 jezika), varijanta B: kuka ponavlja naslov pa je maknuta iz maila; c) vlasnik: »We launch« nejasno -> nova recenica u 44 jezika »We launch the geomapping of partner news on our map on 1 December. If you are interested, just reply...« (4 Opus agenta po 11 datoteka, kopija izlaz_prije_1325); d) ar/he kampanje: <div dir="rtl"> PATCH koraka (3 kampanje). Press: 54 stranice ponovno na 15 domena (`--samo` popis) i na portal (uvoz 236, gradi_press, objava #107 SHV 202610291259; #106 pala jer sam press_ulaz mijenjao tijekom objave, pouka: za vrijeme objave ulaz se ne dira). Snov: ponovni upis svih 5.440 body/body1 (petlja ~2 h), pa 229 primatelja na 23 teksta mijenjana nakon starta petlje (`TEKST` nacin), pa verifikacija; paljenje samo na rijec. POUKE: 6) svaka digni skripta mora imati assert '{{' not in custom polja i probni mail PRIJE dizanja; 7) strukturna provjera cijelog sklopljenog maila (ostaci, IZOSTAJE, duple recenice, link, startup, rtl) za sve tekstove prije Snova; 8) ne mijenjati press_ulaz dok objava tece. **DOPUNA 15:45 UTC <!-- WT-NISE-2026-10-29-D -->:** vlasnik: »Makni moju sliku ipak s press stranica osim za startup, poslovne i financijske medije« -> stranica je po drzavi/jeziku, ne po nisi, pa poslovni i financijski mediji (1.502 primatelja, 129 tekstova) dobivaju zasebne stranice `world-winery-map-<cc>-<lang>-business` s portretom (`bf_kljucevi.json`, `gen_press_nise.py` portret=True samo za _st i _bf), 236 osnovnih bez portreta; sve 365 na 15 domena (`--index-ponovno`) i portal (uvoz 365 + dopuna.json kopirana s osnovne mape, objava #108 SHV 202610291535, portal 404 priopcenja); Snov: Hook i body (doslovan link) ponovno upisani za 1.502 poslovno/financijskih + 229 s promijenjenom pricom (`popravi_body_nise.py TEKST`, 1.668 redaka), RASPORED_NISE.csv tekst `<kljuc>_bf` (kopija RASPORED_NISE.prije-bf-1630.csv); verifikacija slijedi, paljenje samo na rijec. **DOPUNA 18:50 UTC <!-- WT-NISE-2026-10-29-E -->:** verifikacija gotova 18:44 UTC (5.436 adresa: zeleno 3.494, zuto 1.488, crveno 454, 0 neprovjereno; krediti 7.964 -> 4.038, potroseno 2.247; `VERIFIKACIJA_PO_JEZIKU_2910.md`). Vlasnik: »ovdje saljemo i zute« -> svih 64 kampanja PATCH sending_settings skip_unverifiable=false (skip_unverified ostaje true), potvrdjeno citanjem natrag; `pali_nise.py` preduvjet prilagodjen; u slanje ide 4.982 (zeleno+zuto). FINALNI AUDIT (`audit_kampanje_nise.py`, `audit_predlosci_nise.py`): 64 kampanje new, senderi valjani i na vlastitoj domeni, raspored i lista po registru, tracking off, predlosci s {{body}}/{{body1}} bez drugih varijabli, predmet = predmet jezika, potpis po grupi, 683 press linkova HTTP 200; 14 probnih mailova iz PRAVIH predlozaka koraka na editor@pr-voice.info. INCIDENT: popodnevni rtl PATCH (rtl_nise.py) upisao je PRAZNO tijelo u 3 ar/he kampanje jer GET /v2/campaigns/{id} ne vraca body koraka; otkriveno auditom, popravljeno `rtl_nise2.py` (tijelo lokalno kao u digni, PATCH, kontrola GET .../steps/{sid}/content/{cid}). POUKE: 9) sadrzaj koraka cita se SAMO kroz content endpoint i svaki PATCH se cita natrag; 10) audit predlozaka svih kampanja je obavezan korak prije paljenja. Arhiviranje 24 supljih Active kampanja i dalje blokira klasifikator (vlasnik rucno ili dozvola). **DOPUNA 30.10. 05:05 UTC <!-- WT-NISE-2026-10-30-F -->:** vlasnik u 03:5x vidio dva Snov preview-a: AM (US_en) uredan, AS (SG_en) sliven u jedan odlomak s golim linkom, i trazio: isti stil prijevoda, EN predmet s imenom World Winery Map, rucna provjera svih kampanja. UCINJENO: (1) EN pitch ujednacen (IE_en/SG_en osnova, 57 tekstova, na US formulaciju »propose a partnership… place it on the map, free of charge«), isto ES (CO/PA osnova, 6 tekstova), AR (MA_ar, 2), ZH (MY, 1), PT namjerno dvojak (BR/PT); kopije `izlaz_prije_0400/`; (2) EN predmet »Your news on the World Winery Map + one story« u 90 EN datoteka i PATCH subject u 21 EN kampanji (`predmet_en_nise.py`), ostali jezici ostaju »vinska karta«; (3) UZROK SLIVENOG MAILA, potvrdjen pokusima kroz sucelje (content-preview istog prospekta s istim predloskom): Snov skida HTML iz custom polja ciji je sadrzaj cisti ASCII, a jedan ne-ASCII znak (°, ’, U+00A0) cuva HTML; pogodjeno 56 tekstova / 393 primatelja (EN varijanta C bez temperature + indonezijski); lijek: `popravi_body_nise.py` ubacuje U+00A0 u »World Winery Map« kad je body cisti ASCII + assert; prepisano 393 (0 gresaka); (4) RENDER SVIH 5.436 primatelja kroz Snov sucelje (crawler u pregledniku: /back/campaigns/{cid}/prospects + content-preview s pravim predloskom; limit sucelja ~2.000 zahtjeva/5 min -> 429; pozadinska kartica guši setTimeout na 1/min, zato bez cekanja): 0 ogoljenih, 0 ostataka varijabli, 0 bez linka, 0 linkova na krivoj domeni (`RENDER_PROVJERA_3010.md`); (5) 14 probnih mailova kroz Snovov send-test-email (svjezi render, pravi sender) na editor@pr-voice.info, procitani iz Maildira na cPanelu i pregledani u pregledniku (EN, AR, HE, ID…): odlomci, jedan link, potpisi, RTL ispravni; (6) ZAMKA: ucitavanje nacrta u Snov sucelju okida autosave koji {{body}}/{{body1}} zamota u <p>; vraceno PATCH-em za 3215151, 3215255, 3215137, sken svih 64 cist; (7) audit postavki: 64 nacrta, senderi/rasporedi/liste po registru, tracking off, zuti ukljuceni. PALJENJE: vlasnik 30.10. ~05:00 UTC »pali sve« -> `pali_nise.py PALI` (prvi prolaz 27 kampanja pa pad na ne-JSON citanju natrag, skripta ocvrsnuta, drugi prolaz ostalih 37): 64/64 active, 4.982 primatelja (zeleno+zuto), 255 sandučića po 25 dnevno. POUKE: 11) custom polje s HTML-om mora sadrzavati bar jedan ne-ASCII znak; 12) prije paljenja renderati SVE primatelje kroz sucelje, lokalno sklapanje nije dokaz; 13) nacrte ne otvarati u sucelju (autosave).

## t.395 · 29.10.2026. · objavljeno #103, #104

**TANZANIJA PROVJERENA PRIJE ODGOVORA REDAKCIJI (Dira Makini, Godfrey Nnko): 10 NA KARTI, +2 NOVE (ALKO VINTAGES, DANE WINE), CETAWICO POMAKNUT, KISUTU -> KISITU, 6 VINTNERS I BROTHER’S U REZ; OBJAVE #103 (SHV `202610290715`) I #104 (SHV `202610290727`), KARTA v10081 NEPROMIJENJENA, SARDOVI 103.800/97/754**

(29.10.2026., 06:40 do 07:32 UTC; vlasnik: »ocu prave podatke prije neg mu se javim«, »moramo zavrsiti na 10 ... ispravi sve na karti, ispeci to«, »napravi kako mislis da ima najvece sanse da je tocno«)

Biljezi: `WU-TZ-2026-10-29`

Pouke: (1) Google-only zapisi u malim zemljama idu na kartu tek nakon IG/FB/tisak provjere, inace se pred redakcijom sramotimo ([[male-zemlje-karta-kao-stvarnost]]); (2) `grep -o "SHV..." | tail -1` u lancu hvata stari SHV iz brave 6/7, pravi je u retku »SHV u map_ZIVI.js«; (3) rang nesigurnih traziti PRIJE prvog pecenja, ne paralelno, inace dva prolaza.

Otvoreno: odgovor Godfreyju (Dira Makini) ceka rijec vlasnika; 6 Vintners i Brother’s vracaju se ako se vlasnik javi; DOVE najslabija od desetorke (rezerva NELY WINE).

## t.394 · 27.10.2026. · UPALJENO 95

**VAL »LOK VIN« U SNOVU: 101 LISTA/KAMPANJA, 3.280 PRIMATELJA, VERIFIKACIJA ZELENO 1.737 / ZUTO 1.000 / CRVENO 543, UPALJENO 95 KAMPANJA (3.216 PRIMATELJA, 1.708 ZELENIH) 27.10. 17:39 CET; ALBANIJA (6 SQ KAMPANJA, 64) OSTAJE NACRT**

(27.10.2026., 09:40 do 15:40 UTC; vlasnik: »kreni«, »mozemo mi pokrenut kampanje«, »makni albaniju i kosovo«, »prije paljenja trebam ja provjerit«, »pali«)

Biljezi: `WT-LOKVIN-SNOV-2026-10-27`

Pouke: (1) Snov NE zamjenjuje {{varijable}} ugnijezdene u custom polju: body je imao {{naslov}} i {{Hook}}, u pregledu crvena upozorenja, vlasnik uhvatio prije paljenja; popravak = doslovan naslov i doslovan <a href> u body za svih 3.280 (updateContact=true, createDuplicates=false), pri cemu update BRISE sva custom polja koja nisu poslana (prva proba ispraznila naslov/Hook/body1), pa uvijek slati sva polja. (2) Snov verifikacija: `success:false` nije uvijek pun red; »Emails list is empty« = paket vec provjeren (preskoci), »too many emails processing« = pun red na racunu (cekaj); red je 13:52 do 14:49 bio pun tudjim predajama. (3) Prije paljenja vlasnik sam gleda Preview u Snovu; paljenje tek na njegovu rijec. (4) `call()` koji u zaglavlje stavlja JSON content-type ne smije slati form `data=` (prospect-list vracao prazno).

## t.393 · 27.10.2026. · press objavljen #102, slanje ceka

**VAL »LOK VIN«: 62 PR TEKSTA NA 25 JEZIKA (39 ZEMALJA BEZ REGIONALNE PRICE) + 4 STANDARDNA (EE, SE, AL, CY), PRESS STRANICE NA 10 SENDER DOMENA I NA PORTALU (OBJAVA #102, SHV `202610270913`), LISTE OPCIH I LOKALNIH REDAKCIJA 3.280 ADRESA U 42 ZEMLJE**

(27.10.2026., 06:00 do 09:20 UTC; vlasnik: »prilagodit i prevest u duhu jezika, novinarski stil«, »samo na nove redakcije«, »opce i lokalne, ne nisne i vinske«, »sumnjive ne saljemo«, »kopije svih pressa dodaj i na glavnu stranicu wwm com pod press«)

Biljezi: `WT-LOKVIN-2026-10-27`

Pouke: kolegino ciscenje baci CIJELU staru listu (`izvor` staro -> van `stara_lista`) i zemlje bez vinograda na cekanje, pa prije svakog vala provjeriti obje baze; Snov liste sadrze 10.753 adresa bez ijednog `sent` dogadjaja (pauzirane kampanje), pa »vec poslano« mjeriti dogadjajima, a clanstvo u listi voditi zasebno; ssh heredoc s ugnijezdjenim navodnicima je opet pukao (OBJAVA102 prvi put), skripte slati scp-om.

Otvoreno: slanje ceka Snov verifikaciju i vlasnikovo »dizemo«; izvorni govornik za mt, ne, km, my, th; Bahami bez redakcija; CY turske redakcije (10) bez turskog teksta; 105 adresa u pokrenutim Snov kampanjama bez slanja ceka odluku.

## t.392 · 27.10.2026. · objavljeno #101

**EGIPAT DOBIO DRUGU VINARIJU: KOUROUM OF THE NILE (EGYBEV), EL GOUNA; OBJAVA #101, KARTA v10081 NEPROMIJENJENA, SHV `202610270720`, SARDOVI 103.795/97/754**

(27.10.2026., 06:56 do 07:27 UTC; vlasnik: »mozes li egiptu nac tocku, i jel smo imali 1 ili 2 onda«)

Biljezi: `WT-EG-2026-10-27`

## t.391 · 27.10.2026. · objavljeno #100

**DVIJE NOVE VINARIJE PO RIJECI VLASNIKA: BODEGA GIACOMETTI (PY, ASUNCION) I SOCIETE DES GRANDS CRUS DE L'OUEST (DZ, SIDI CHAMI); PY IZNIMKA OD PRAVILA BODEGA U KONTROLI SARDOVA; OBJAVA #100, KARTA v10081, SHV `202610270424`, SARDOVI 103.794/97/753**

(27.10.2026., 04:10 do 04:28 UTC; vlasnik: »alzir i paragvaj nadji di su vinarije te, guglaj ... mora bit neki trag lokacije ili bar dodaj zgradu uprave«)

Biljezi: `WS-DZ-PY-2026-10-27`

Pouke: zemlja koju je ranije zabranila brava trazi i zakrpu brave, ne samo novu kartu (prvi put od 23.8.); lanac iz ssh-a pokretati kroz `systemd-run`, ne `setsid nohup ... &`.

Otvoreno: PR tekst za Alzir i Paragvaj pise vlasnik; GCO podrumi bez tocke; karta Algerije ima 555 parcela (Corine) i od sada 1 vinariju.

## t.390 · 27.10.2026. · objavljeno #99

**PAKET ZEMALJA IZ REVIZIJE POPISA 26.10. NA KARTI: 535 U REZ (209 DVOJNIKA SPOJENO), +237 NOVIH VINARIJA, 18 VRACENIH, 5 NOVIH ZEMALJA (CV, TJ, PF, KG, MG), DOM_VAN PRVI PUT PUN (108), IME_VINARIJE 75; OBJAVA #99, KARTA v10080, SHV `202610270301`, SARDOVI 103.791/95/751**

(27.10.2026., 02:10 do 03:06 UTC; vlasnik 26./27.10.: »mađarsku, gruziju ignoriraj i prebaci«, »afrika me zanima i azija najviše … svaku oću provjeru je li prava«, »dataforseo krediti su došli, koristi tamo«, »ajde kreni«)

Biljezi: `WR-PAKET-ZEMLJE-2026-10-27`

## t.389 · 26.10.2026. · objavljeno #98

**CHARMOCORT: 24 CORTON CLIMATA S `village-denomination` NA `grand-cru-climat`, 5 BURGUNDSKIH GRAND CRU AOC BEZ RAZINE DOBILO `grand-cru`; OBJAVA #98, SHV `202610261608`, map.js i plocice nepromijenjeni**

(26.10.2026. navecer; prijava vinara Charmocort (mail nit 101, prijava #1484); vlasnik: »popravi odmah ako mozes, to je bitno«)

Biljezi: `WQ-CHARMOCORT-2026-10-26`

## t.388 · 26.10.2026. · objavljeno #97

**PAKET C PO ODLUKAMA VLASNIKA (4 SKRIVANJA, LA TORRETTA SPOJ, RUCNE POTVRDE FONTECUORE I BASILESCU), LEDGER IMENA VINARIJA `out/IME_VINARIJE.csv` + `ime_vinarije.py`; OBJAVA #97, karta v10079, SHV `202610261521`, sardovi 104.071/90/737**

(26.10.2026. popodne; vlasnik u kartici »Vinarije: sto prije odgovora«: »sakriti pa onda gledat iduci tj« (Oliveta), »sakriti« (Halcon), »ne« (medovina), »odmah mici« (Romero), »napravi ledger«, »potvrdi racun rucno«, »rucno ako mozes«; pravilo vlasnika istog dana: svaki zahtjev za micanje s karte javiti ODMAH i na vrhu, ne zakopan u popisu)

Biljezi: `WP-PAKET-C-2026-10-26`

## t.387 · 26.10.2026. · bez statusa

**CISCENJE PO MAILOVIMA VINARA I PRIJAVAMA S KARTE: 23 ZAPISA SKRIVENO, 14 DVOJNIKA SPOJENO (WID_SPOJ 34 PARA), 5 TOCAKA, 2 REGIJE, 1 NOVA, 23 TUDJA MAILA VAN; ZAKRPA ISPRAVAK-ZATVARA-PRIJAVU; SELIDBA 3,06 GB NA STORAGE BOX; OBJAVE #95 (SHV `202610260940`) I #96 (SHV `202610261001`), karta v10079 nepromijenjena, sardovi 104.076/90/737**

(26.10.2026.; vlasnik: »makni to sve s karte sakrij«, »kreni«, odluke 1 do 14 na Claude Docu mailova 22.10.)

Biljezi: `WO-CISCENJE-2026-10-26`

## t.386 · 21.10.2026. · bez statusa

**PRO STRANICA VINARIJE BEZ HRVATSKOG TEKSTA O REGIJI**

(21.10.2026.; revizija 21.10. nalaz ATR-01, jedini P0; vlasnik: »zasad samo makni rucno taj hr tekst, a sutra to treba izjednacit sa onom stranicom koja je na journalu ionako«)

Biljezi: `HR-TEKST-VAN-2026-10-21`

## t.385 · 21.10.2026. · bez statusa

**LIGHTBOX U POPUPU (slika se otvara preko karte, ne u novoj kartici); OBJAVE #92, #93 i #94, karta v10079, style_v9982, index_v26, SHV `202610211625`**

(21.10.2026.; vlasnik: »kad u galeriji klikneš na slike, otvara se novi page.. to je loše, treba nekak se popup proširit«)

Biljezi: `WM-LIGHTBOX-2026-10-21`

Otvoreno: lightbox ne lista slike dodirom (swipe) na mobitelu, samo strelicama i dodirom na sliku; video i dalje otvara vanjsku stranicu (nije trazeno); disk na PC-u vlasnika pun

## t.384 · 21.10.2026. · bez statusa

**PROWEIN PROBNE STRANICE ZA PONUDU: naslovnica s plasmanima i stranica izlagaca s embed kodom; karta v10074/v10075 s prekidacem sloja; SUDAR s lightbox zakrpom druge sesije**

(21.10.2026., zakrpa `wk`; nalog vlasnika: »naslovnicu sa standard kartom i tipkom ProWein filter, landing samo izlagaci + embed kod, banner u meniju, ProWein 2027 u meniju, journal, banner na dnu«)

## t.383 · 21.10.2026. · bez statusa

**GENERACIJA v26: TRECI PAKET OBRISA VINARA (17), OBJAVA #88, karta v10073, SHV `202610211036`; MODERACIJA 34 RETKA (POMFY 3 OPISA); SELIDBA 136,7 GB NA STORAGE BOX GOTOVA**

(21.10.2026.; vlasnik: »pripremi za pecenje da odmah specemo kad ovo obavis«, »takve stvari ne brises, nego ... stavis tamo«, »prevedi«)

Biljezi: `WI-V26-DRW3-2026-10-21`

Otvoreno: 4 odobrena obrisa poslije izvoza (#920 US ispravak Mafia Princess, #921 AU, #922, #923) cekaju cetvrti paket; svjetski izvori vinograda (Claude Doc a0ba35dd) cekaju ODLUCI; CF tokeni rok 28.10.

## t.382 · 21.10.2026. · bez statusa

**KARTICA VINOGRADA ZA PRO (slike, ime, vina, video), SEKCIJA VINEYARDS S IMENOM, MORE BEZ SKOKA, PRAG JEZIKA ZA OPIS VINOGRADA; OBJAVA #87, karta v10072, SHV `202610210548`**

(21.10.2026.; revizija popupa Martina Pomfyja, Claude Doc d1845847; vlasnik: »1. dodati slike i vise da se moze nekako listat... i naslov i video... nek tamo cita na vinogradu 2. da 3. da 4. da 5. prevesti, i ostavit kak on zeli 6. pripremi za pecenje«)

Biljezi: `WG-VINOGRAD-POPUP-2026-10-21`

## t.381 · 20.10.2026. · bez statusa

**ISPRAVAK #85: 18 OD 25 PROWEIN VINARIJA BILI DUPLIKATI POSTOJECIH; OBJAVA #86, karta v10071, SHV `202610201540`, sardovi 104.101**

(20.10.2026., zakrpa `wg`)

## t.380 · 20.10.2026. · bez statusa

**25 VINARIJA IZLAGACA PROWEIN 2027 NA KARTI REDOVNIM LANCEM: OBJAVA #85, karta v10071, SHV `202610201521`, sardovi 104.119 — ISPRAVLJENO t.381: 18 od 25 bili duplikati, ostaje 7**

(20.10.2026., zakrpa `wf`; nalog vlasnika »ubaci ih redovnim putem, peci i sto treba, i kanon i sve«)

## t.379 · 20.10.2026. · bez statusa

**PROWEIN-2027-PREVIEW: privremeni pregled za ponudu Messe Düsseldorf (objava #84, karta v10071, SHV `202610201438`)**

(20.10.2026., zakrpa `we`, nalog vlasnika »za sada samo pregled, bez dopuna i crona, kreni sa svime«)

## t.378 · 20.10.2026. · bez statusa

**PAKET EU: SLUZBENI SLOJEVI PL, VALONIJA, LV, EE, FI, IE; GENERACIJA v25, OBJAVA #83, karta v10070, SHV `202610200954`; RUFFUS PREMAPIRANJE; MODERACIJA 32 TEKSTA**

(20.10.2026.; vlasnik: »koje zemlje EU jos mozemo dodati vinograde? latvija, litva?« pa »cilj samo dodati one zemlje koje nisu PR prosle s vise od 2-3 objave... polj, val, la, es, fi - idemo odmah to.. zaboravi na njem, slovacku... ne preskaci irsku i maltu, nisam ti reko da gledas broj vinarija« pa »nadi jos zemalja po svijetu«)

Biljezi: `WD-V25-EU-2026-10-20`

Otvoreno: volumen 5 G (revizija diskova); 1 novi tekst ceka (id 1899); `eu_1020_privremeno` 3,7 GB na `/`; test_novo 1337 OK, 5 LOSE (JOURNAL_RED dirnut iz druge sesije, P1-28 slike/tekstovi mijenjani tijekom testa, admin brojke); Malta LPIS 2021 portal 403

## t.377 · 19.10.2026. · bez statusa

**DRUGI PAKET OBRISA VINARA (41), GENERACIJA v24, OBJAVA #82, karta v10069, SHV `202610191917`; MODERACIJA 19.10.**

(19.10.2026.; vlasnik: »gdje su od Martina vinogradi?« pa »moze li pecenje sad?« pa »moze«)

Biljezi: `WC-V24-DRW2-2026-10-19`

Otvoreno: 1 obris pending (id 744); CF token rok 28.10.; prijevodi novih kljuceva dashboarda

## t.376 · 19.10.2026. · bez statusa

**SUSTAVSKI MAILOVI: OMOT, TEXT/PLAIN, REPLY-TO, POTPIS I PODACI TVRTKE**

(19.10.2026., oko 12:40 UTC; povod: Fontecuore 19.10.2026., potvrda racuna isporucena u spam kod Alpimedije)

Biljezi: `WB-MAIL-OMOT-2026-10-19`

Otvoreno: isporuka u sandučić se i dalje ne mjeri (nema Resend webhooka); novi mail u app.py ne treba nista posebno, omot ga pokriva sam (samo tijelo, bez vlastitog potpisa, ili s `MAIL_POTPIS_IME` ako ga ima); u tijelo maila nikad brojke nase mjere (parcele, hektari).

