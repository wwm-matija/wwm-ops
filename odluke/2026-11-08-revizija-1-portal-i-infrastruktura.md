# Revizija neispunjenog, 1: Portal i infrastruktura

Status: ODLUČI

Izvor: `Documents/WWM_SUSTAV_RADA_2026-11-04/NEISPUNJENO_kanon.md` (stanje kanona 4.11.2026., t.350 do t.400, i revizija 17.10.). Stanje »otvoreno« = kanon je ponavlja; »nejasno« = kanon je ne spominje poslije obećanja, pa se ne zna je li riješeno izvan kanona. Uz svaku stavku je Claudeov prijedlog; Matija ispod upiše svoju riječ (ide / pada / kasnije / provjeri).

## ODLUČI

### 1.1 CF Cache Rule za /data/* (karta sporo, JSON DYNAMIC; treba token Zone.Cache Rules.Edit u `/root/.env.cloudflare`)
- izvor: t.398, t.400 · obećano: 4.11. · stanje: **otvoreno** · zadnji spomen: t.400 · odluka: vlasnik
- prijedlog: IDE ODMAH, tehničko: Matija napravi token Zone.Cache Rules.Edit (upiše ga sam u /root/.env.cloudflare), Claude postavi pravilo. Karta je spora bez toga.
- **Matija:** 9.11.: ne čeka, radi odmah. IZVRŠENO 9.11.: Matija dao token wwm-pravila, Claude postavio pravilo WWM-DATA-CACHE (`alati/cf_cache_pravilo.py`): /data/ bez /data/shards/, samo uz Referer naše stranice i bez robotskog agenta. Mjera: prije DYNAMIC 0,35 do 1,24 s, poslije HIT 0,14 do 0,17 s. Brave origina i dalje vrijede za sve ostale zahtjeve. Token wwm-pravila Matija obrisao 9.11., /root/.env.cf_pravila maknut; oba pravila rade i bez njega (provjereno: /data HIT, /admin 302). ZATVORENO.

### 1.2 /admin na api. javno dostupan, zaštita Cloudflare Accessom
- izvor: t.178; revizija G ODLUČI 1 (P0) · obećano: 14.9., ponovljeno 17.10. · stanje: **nejasno** · zadnji spomen: t.183 (18.9.), revizija 17.10. potvrdila 200 · odluka: vlasnik
- prijedlog: IDE: zatvoriti Cloudflare Accessom (login mailom), jedan sat posla, nulti rizik za javni dio. P0 od 14.9.
- **Matija:** 9.11.: DA, zatvoriti Cloudflare Accessom. IZVRŠENO 9.11.: Matija uključio Zero Trust, `alati/cf_access_admin.py --pisi` napravio aplikaciju »WWM admin« za api.worldwinerymap.com/admin (sesija 24 h), pravilo »samo vlasnik« (jedna adresa). Izvana /admin vraća 302 na prijavu; /api/admin i javni API nepromijenjeni; cron ide na 127.0.0.1. Matija 9.11. potvrdio: prijava radi. ZATVORENO.

### 1.3 RareCloud ključ ima root na Hetzneru, maknuti ili dati vlastiti bez roota
- izvor: revizija G ODLUČI 2 (P0); t.183 · obećano: 17.10. · stanje: **nejasno** · zadnji spomen: t.183 · odluka: vlasnik
- prijedlog: IDE: maknuti RareCloud ključ iz authorized_keys na Hetzneru čim Matija potvrdi da nediraj VM ne treba pisati na Hetzner. P0.
- **Matija:** 9.11.: DA, makni. IZVRŠENO 9.11. 09:34 UTC: redak root@rc-s-2vcpu-4gb-3b659a maknut iz /root/.ssh/authorized_keys (0 prijava s 85.121.* u 30 dana), kopija kopije/2026-11-09/authorized_keys.prije-rarecloud-093421, naš ključ provjeren novom prijavom.

### 1.4 Kopije: snapshot Storage Boxa, proba povrata, drugi ključ izvan stroja (t.103), `backup.sh` trap ERR (t.98), `fable_fix` u kopiji (t.176)
- izvor: revizija G ODLUČI 3 (P0) · obećano: 8.9. do 17.10. · stanje: **otvoreno** · zadnji spomen: t.98, t.103, t.176 bez zatvaranja · odluka: vlasnik + tehničko
- prijedlog: IDE u popravke: trap ERR u backup.sh, proba povrata jednom mjesečno, drugi ključ Boxa kod Matije offline. P0, bez toga kopije nisu dokazane.
- **Matija:** 9.11.: »Da, sve tri«. IZVRŠENO 9.11.: (a) proba povrata `alati/proba_povrata.py` prošla 5 od 5 za 81 s (dnevna baza, fotografije, off-site Namecheap, Box cijela baza, Box izvor); (b) alarm je već postojao u nadzor.py za dnevnu kopiju, dodan `/root/backup_box.log` u nadzor (zakrpa s kopijom); (c) ključ Boxa: Matija 9.11. potvrdio »jesam«, primjerak je kod njega. Tajne: Matija 9.11. »Nemam, spusti ih«. IZVRŠENO: 8 datoteka (.env API-ja i pipelinea, Cloudflare, Resend, Dodo, Pexels, certbot) spakirano na serveru, preneseno u `C:/Users/world/wwm_tajne_2026-11-09/` (izvan repoa i oblaka, md5 provjeren), privremena arhiva na serveru obrisana, uz arhivu CITAJ_ME.txt s putanjama povrata. Matija je seli na USB uz ključ Boxa. Arhiva zastari kad se neki ključ zamijeni (Roll CF tokena 12.11., novi Resend ključ): tada ponoviti.

### 1.5 Izložene tajne: zamjena Resend ključa (6.9.) i WAF tokena (20.9.), tajne iz memorija u .env
- izvor: revizija G ODLUČI 4 (P0) · obećano: 17.10. · stanje: **nejasno (u kanonu nema)** · zadnji spomen: revizija G · odluka: vlasnik
- prijedlog: IDE: Matija zamijeni Resend ključ i WAF token u sučeljima i upiše nove u .env na serveru; stare vrijednosti iz razgovora smatrati izloženima.
- **Matija:** 9.11.: ovaj tjedan, podsjetnik 12.11. (zakazan). Zamjena Resend ključa i WAF tokena je Matijin posao u sučeljima; novi u .env na serveru.

### 1.6 Selidba portala sa shared hostinga (Namecheap SAD) na Hetzner
- izvor: t.302, t.312; revizija G ODLUČI 9 · obećano: 1.10. · stanje: **otvoreno** · zadnji spomen: t.302; dijagnoza sporosti t.398 · odluka: vlasnik
- prijedlog: ČEKA odluku o terminu: velik posao (DNS, PHP/SQLite, uploadi), ali jedini pravi lijek za sporost i padove pod tuđim opterećenjem. Prijedlog: poslije 1.12. (Wine News start).
- **Matija:** 9.11.: u petak 13.11., kad riješimo PR, mailove i tekuće stvari i kad Matija nastavi s prodajom koja stoji. Claude do tada pripremi plan selidbe kao zasebnu odluku.

### 1.7 gunicorn/Flask rade kao root, selidba na korisnika `wwm`
- izvor: t.112 (P1-20); revizija G #18 · obećano: 8.9. · stanje: **otvoreno** · zadnji spomen: t.112 · odluka: tehničko
- prijedlog: IDE u popravke, ali tek nakon Q13 drugog koraka (korisnik ops); ne odvojeno.
- **Matija:** 9.11.: DA, sve u jedan paket popravaka; Claude radi redom, svaki s kopijom i provjerom.

### 1.8 Pravilo zabrane pod /data/ na api. ne pokriva `.geojsonl` (6,5 GB parcela)
- izvor: t.334 · obećano: 2.10. · stanje: **nejasno** · zadnji spomen: t.334 · odluka: tehničko
- prijedlog: IDE u popravke: jedna linija u nginx pravilu; provjeriti izvana poslije reloada.
- **Matija:** 9.11.: DA, sve u jedan paket popravaka; Claude radi redom, svaki s kopijom i provjerom.

### 1.9 Lightbox ne lista slike dodirom (swipe) na mobitelu
- izvor: t.385 · obećano: 21.10. · stanje: **otvoreno** · zadnji spomen: t.385 · odluka: tehničko
- prijedlog: PADA ili kasnije: sitnica za mobitel, nema pritužbi; ostaviti za paket popravaka.
- **Matija:** 9.11.: DA, sve u jedan paket popravaka; Claude radi redom, svaki s kopijom i provjerom.

### 1.10 Isporuka sustavskih mailova se ne mjeri (nema Resend webhooka)
- izvor: t.376; revizija N · obećano: 19.10. · stanje: **otvoreno** · zadnji spomen: t.376 · odluka: tehničko
- prijedlog: IDE u popravke: webhook za delivered/bounced u mail_greske.log; bez toga ne znamo stižu li potvrde računa.
- **Matija:** 9.11.: DA, sve u jedan paket popravaka; Claude radi redom, svaki s kopijom i provjerom.

### 1.11 Uvjeti korištenja i struganje: 8 odluka (AI trening, robots za /data/, zamke, crna lista)
- izvor: t.324; revizija G #15 · obećano: 3.10. · stanje: **nejasno** · zadnji spomen: t.324 · odluka: vlasnik
- prijedlog: ČEKA: 8 odluka iz t.324 prepisati u zasebnu odluku kad Matija ima vremena; nije hitno dok Worker brani popis.
- **Matija:** 9.11.: pripremi kao kratku odluku (8 točaka s prijedlogom).

### 1.12 DMARC dopune (365promo.shop, prvoice.site, wwm.eu...), Postmaster Tools, 769 nepročitanih DMARC izvještaja
- izvor: revizija G ODLUČI 11, 12 · obećano: 17.10. · stanje: **nejasno (u kanonu nema)** · zadnji spomen: revizija G · odluka: vlasnik
- prijedlog: IDE djelomično: DMARC zapisi za domene koje šalju (tehničko); 769 izvještaja ne čitati ručno, sken ih broji.
- **Matija:** 9.11.: DA, sve u jedan paket popravaka; Claude radi redom, svaki s kopijom i provjerom.

### 1.13 Ime regije na hladnom učitavanju QR linka (»HU BV 22« umjesto »Tokaj«)
- izvor: DANAS_1710/IZVJESTAJ_A_embed_agnes · obećano: 17.10. · stanje: **nejasno (u kanonu nema)** · zadnji spomen: revizija · odluka: tehničko
- prijedlog: IDE u popravke: sitnica u map.js (naslov iz regije_indeks umjesto koda).
- **Matija:** 9.11.: DA, sve u jedan paket popravaka; Claude radi redom, svaki s kopijom i provjerom.

### 1.14 contact@: obećanje odgovora u 2 radna dana bez alarma; 177 nezatvorenih upozorenja u adminu
- izvor: t.182; revizija G ODLUČI 15 · obećano: 14.9., 17.10. · stanje: **nejasno** · zadnji spomen: t.299 (52 nova), revizija G · odluka: vlasnik + tehničko
- prijedlog: ČEKA odluku: ili maknuti obećanje »2 radna dana« s weba, ili sken mailova dnevno (sad postoji). Prijedlog: ostaviti obećanje, sken svaki radni dan kroz Codex.
- **Matija:** 9.11.: obećanje ostaje, sken svaki radni dan (Codex jutrom pokrene posao mailovi, Matija odobrava).

### 1.15 Natpis registracije u vinar.html r.615 odvraća od Gmaila, a mailovi kažu da je potvrda automatska
- izvor: DANAS_1710/IZVJESTAJ_F_obecanja · obećano: 17.10. · stanje: **nejasno (u kanonu nema)** · zadnji spomen: revizija · odluka: tehničko
- prijedlog: IDE u popravke: uskladiti tekst na vinar.html s mailovima (potvrda je automatska s domenom vinarije, ručna s Gmaila).
- **Matija:** 9.11.: DA, sve u jedan paket popravaka; Claude radi redom, svaki s kopijom i provjerom.

