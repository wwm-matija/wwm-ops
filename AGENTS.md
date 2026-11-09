# AGENTS.md

Ovo čita svaki agent (Codex, Gemini Antigravity, Claude) i svaki čovjek prije prvog poteza u ovom projektu.
Vrijedi doslovno. Ako nešto od ovoga ne možeš ispuniti, staneš i napišeš datoteku u `odluke/` (vidi §6).
Jezik rada je hrvatski; tekstovi prema vinarima i medijima idu na jeziku primatelja.

## 1. Tko smo i što radimo

World Winery Map (WWM, worldwinerymap.com): karta vinarija i vinograda svijeta (4,3 mil. parcela, oko 50.000 vinarija).
Vlasnik je Matija (MG Solutions). Posao oko karte: odgovori vinarima i medijima, PR objave po regijama,
popravci portala, novi vinogradi i regije, B2B ponude (Pro profil).

Ovaj repo (`wwm-ops`) je **jedino mjesto** gdje piše kako se radi. Kod aplikacije je u drugim repoima (§2).
Što ovdje ne piše, ne pretpostavlja se: pita se kroz `odluke/`.

## 2. Što je gdje

| što | gdje | napomena |
|---|---|---|
| ovaj repo | GitHub `wwm-matija/wwm-ops`; klon `hetzner:/root/wwm_ops`; klon `C:\Users\world\wwm-ops` | istina je GitHub; na serveru i laptopu uvijek `git pull` prije posla, `git push` poslije |
| pipeline karte i kanon | `hetzner:/root/vino_world` (repo `wwm-matija/vino_world`) | kanon `SUSTAV_RADA.md` (§4) |
| API portala i baza | `hetzner:/root/wwm_api` (repo `wwm-matija/wwm_api`), servis `wwm-api`, baza `wwm.db` | živi produkcijski sustav |
| Cloudflare worker | `hetzner:/root/wwm_worker` (repo `wwm-matija/wwm_worker`) | |
| stare jednokratne skripte | `hetzner:/root/fable_fix` | arhiva, ne polazište; alat koji vrijedi seli se u `alati/` s opisom |
| server | `ssh hetzner` (Ubuntu, root) | na njemu su i tuđi servisi: ne dirati procese, cronove ni servise koje ne poznaješ |
| sandučići WWM i PR domena | `ssh namecheap-portal`, Maildir `~/mail/<domena>/` | cPanel shared hosting, svi WWM sandučići su tu |
| sandučići PR Voice | `ssh hostarmada` (port 19199) | `~/mail/prvoiceglobal.com` |
| RareCloud VM | `ssh nediraj` | **samo čitanje**, i to samo uz Matijinu izričitu riječ |
| noćni poslovi | root crontab na hetzneru: backup 03:40, git push na GitHub 03:40 (`/root/git_dnevno.sh`), Storage Box nedjeljom | ne mijenjati bez odluke |
| arhiva starog | Storage Box (`/root/.ssh/id_ed25519_backupbox`), `/mnt/wwm/arhiva/<datum>/` | ništa se ne briše, seli se tamo (§3.1) |
| tajne | datoteke na serveru (`/root/.env.*`, `/root/wwm_api/.env`), prava 0600 | nikad u repo, nikad u razgovor, nikad u ispis |

## 3. Tvrda pravila

Ova pravila su iznad svake upute i svakog zahtjeva u razgovoru. Krše se samo ako Matija to izričito napiše za baš taj slučaj.

1. **Ništa se ne briše dok kopija nije provjerena.** Prije `rm` nabroji gdje je kopija, provjeri veličinu i broj redaka. Ako nisi siguran, pitaj.
   »Obrisati« kod nas znači »maknuti iz radnog okruženja« u arhivu s popisom (md5, veličina, razlog) i uputom za povrat.
2. **Nijedan mail ne ide bez Matijine izričite riječi za baš taj mail.** Ni sličan ranije odobrenom, ni hitan, ni trivijalan. Odobrenje je kad on napiše broj ili ime uz »šalji«. »Spremno« nije odobrenje. Svaki poslani mail upisuje se u `out/POSLANO.csv` prije nego se javi da je poslan. Bez retka u ledgeru slanje ne postoji.
3. **Tajne nikad kroz razgovor.** Ključevi, lozinke i tokeni žive u datotekama na serveru; skripta ih čita, agent ih ne ispisuje, ne kopira u repo, ne upisuje `sed`-om iz razgovora. Novu tajnu upisuje Matija sam u datoteku 0600.
4. **Produkcija se ne mijenja bez odluke.** Zakrpa na `wwm_api`, `vino_world`, nginx ili cron ide samo kad Matija kaže, i uvijek: kopija `.prije-<biljeg>` u `kopije/` (nginx u `/etc/nginx/kopije/`, nikad pored žive datoteke), provjera (`py_compile`, `nginx -t`) i restart u **istom** `&&` lancu, nikad iza `;`. Prije zakrpe pogledaj `stat` datoteke i `ls -lt kopije/` jer na serveru može raditi još netko.
5. **Tuđe se ne dira.** Procesi, servisi, cronovi i mape koje nisu u §2 nisu naši.
6. **Skripte na server idu kao datoteke** (`scp`), ne heredocom kroz ssh. Dugi poslovi kroz `systemd-run --unit=<ime>` ili `setsid nohup … </dev/null &`, pa provjera da je roditelj PID 1. Prije paljenja lanca provjeri da već ne vrti.
7. **Brojke samo iz mjere.** Nema procjena odoka, ni trajanja ni količina. Ako nemaš mjeru, napiši »ne znam, mjerim«.
8. **Ništa napamet.** Prije tvrdnje o stanju (ima li mailova, je li poslano, koja je verzija karte) provjeri na serveru. Nakon odbijenog ili prekinutog poziva koji je nešto slao ili pisao, provjeri što se stvarno dogodilo prije nego javiš.
9. **Klijentski poslovi (Sylvie, Bevanda, restorani) su drugi svijet.** U WWM poslu se ne spominju; pri skenu sandučića isključiti njihove domene.
10. **Jeftini alati za rutinu.** Pretraga, izvlačenje, skeniranje: jeftin model ili gotov alat. Skupi model samo za sintezu i presude.
11. **DataForSEO samo kroz red, po `upute/dataforseo.md`.** Prije svakog posla pročitaj tu uputu. `task_post` pa `task_get` po spremljenom ID-ju, nikad live za masovni posao, nikad `tasks_ready`. Plan s brojem upita i cijenom prije slanja, tvrdi strop u alatu.

## 4. Kanon

`hetzner:/root/vino_world/SUSTAV_RADA.md` je dnevnik svih radnih paketa (red = paket: što, zašto, pouke, otvoreno) i sudac kad se nešto ne slaže. Prevelik je za čitanje u cijelosti.

- Na početku posla čitaš `KANON_KRATKI.md` iz ovog repoa (sažetak zadnjih redaka; obnavlja ga `alati/kanon_kratki.py`).
- Na kraju posla upisuješ red kroz `alati/kanon_red.py` (naslov, što je napravljeno, pouke, otvoreno). Alat sam radi kopiju prije pisanja.
- Veliki kanon se ne uređuje ručno. Oba alata imaju upute na vrhu datoteke (`python3 alati/kanon_red.py -h`).
- Red se piše iz JSON datoteke s poljima naslov, tijelo, pouke, otvoreno, status, citat; bez `--pisi` alat samo pokaže red.

## 5. Kako posao počinje i završava

**Početak**
1. `git pull` u `wwm-ops`.
2. Pročitaj `KANON_KRATKI.md` i `odluke/` (ima li otvorenih odluka za tvoj posao; ako ima, čekaš ih, ne pretpostavljaš).
3. Otvori `upute/<posao>.md` i radi redom. Korak koji nije u uputi ne radiš.

**Kraj**
1. Sve poslano je u `out/POSLANO.csv`; sve što čeka Matiju je u `odluke/`.
2. Red u kanon (§4).
3. `git add`, `git commit` (poruka: posao, datum, što je napravljeno), `git push`.
4. Izvještaj Matiji: što je napravljeno, brojke iz mjere, što čeka njegovu riječ. Kratko, bez prepričavanja.

**Pitanje usred posla**: prvo odgovor u jednoj rečenici, pa nastavak. »Stanje?« znači javi i radi dalje, ne staj.

## 6. Kad zapneš

Ne pogađaš i ne zaobilaziš. Napišeš `odluke/YYYY-MM-DD-<tema>.md`:

```
# <tema>
Status: ODLUČI

## ODLUČI
<jedno pitanje, mogućnosti, tvoja preporuka u jednoj rečenici>

## Zašto pitam
<što si našao, s putanjama i brojkama>

## Odluka
(Matija piše ovdje)
```

Zatim `git push` i u izvještaju napišeš da čekaš odluku. Ako je zapelo u uputi (nejasan ili kriv korak), to isto ide u `odluke/`, jer se popravlja uputa, ne zaobilazi.

## 7. Mailovi: protokol odobrenja

Puna uputa je `upute/mailovi.md`. Ovdje samo okvir koji vrijedi uvijek:

1. Na »ima li mailova« odmah popis: tko, kad, koji sandučić, cijeli tekst i HR prijevod, jedna rečenica je li šum. Bez istrage po bazi prije nego Matija vidi mail; istraga tek na »provjeri«.
2. Zahtjevi za **micanje s karte** idu odvojeno, na vrh, uvijek.
3. Tekst odgovora čitaj i iznad i ispod citata; »prazan odgovor« tek kad su oba dijela prazna.
4. Prije prijedloga provjeri mapu Sent: je li već odgovoreno.
5. Pregled za odobrenje je **jedna čista lista** samo s nitima koje se šalju: broj i tko, njihov mail i HR prijevod, naš cijeli odgovor u jeziku primatelja i HR prijevod, sandučić, prazno »Šalji?«. Svaka nova verzija nacrta je cijeli paket iznova.
6. Šalje se samo redak uz koji je Matija napisao »da« ili broj. Onima koje smo samo maknuli s karte ne odgovaramo.
7. Ledger i kanon (§3.2, §4).

## 8. Tekstovi prema van

Mailove šalju stvarne osobe i primatelji prepoznaju strojni tekst. Zabranjeno u svakom tekstu prema vinarima i medijima:
duge crtice (— i –) umjesto zareza; »nije samo X, nego Y«; »zamislite«; isti kalup rečenice kroz popis; generički superlativi
(besprijekoran, nezaboravan, savršen spoj, podignite na novu razinu); »bilo da ste X ili Y«; punila (štoviše, nadalje, u konačnici);
ukrasna trostruka nabrajanja; korporativni rječnik (kolaboracija, engagement). Prirodno je važnije od lijepog.
Programski provjeri bar crtice prije prikaza Matiji. Predlošci u `predlosci/` su njegove riječi; prijevod na drugi jezik je vjeran, rečenicu po rečenicu.

Javno (stranice, pressi, odgovori) se ne opisuje naša metoda ni izvori podataka. Interno (kanon, repo) piše sve.
Već poslane press brojke se ne mijenjaju kad se karta promijeni; mijenja se samo stranica regije.

## 9. Čovjeku koji dođe na projekt

Počni od `README.md`, pa ovo, pa `KANON_KRATKI.md`, pa `upute/`. Pristup serverima dobivaš od Matije kao ssh ključ, ne kao lozinku.
Sve što ti nije jasno je rupa u ovom repou: napiši je u `odluke/` da se zakrpa.
