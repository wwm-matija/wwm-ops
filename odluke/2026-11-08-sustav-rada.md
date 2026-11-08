# Sustav rada: temeljne odluke

Status: ODLUČENO (Matija, 8.11.2026.)

## ODLUČI
Nema otvorenih točaka. Zapis radi povijesti i da svaki agent zna po čemu radi.

## Cilj (Matija, 5.11.2026.)
Ne raditi sve kroz Claude Fable. Codex (ChatGPT) i Gemini Antigravity rade izravno: odu na server, skinu mailove,
po pisanim uputama slože odgovore iz predložaka, šalju tek na Matijino »šalji« za točno taj mail, upišu ledger
i red u kanon. Fable dolazi za velike stvari. Čovjek programer mora iz datoteka vidjeti kako sve radi.

## Odluke
| # | pitanje | odluka |
|---|---|---|
| Q8 | gdje sustav živi | zaseban repo `wwm-ops`; kod aplikacije ostaje u `vino_world`, `wwm_api`, `wwm_worker` |
| Q9 | kanon | veliki `SUSTAV_RADA.md` ostaje arhiv i sudac; dodaju se `KANON_KRATKI.md` i `alati/kanon_red.py`; izvedba po Fableovu prijedlogu |
| Q10 | odobrenje i trag | lista u razgovoru, šalje se samo uz »šalji« po retku; `out/POSLANO.csv` obavezan; uz to vizualan pregled s filtrima (CRM / tablica) nad ledgerom |
| Q11 | odluke | datoteke u `odluke/` s ODLUČI na vrhu; Claude Docs se više ne koriste za odluke |
| Q12 | pilot | prvi posao »mailovi«; gotovo kad Codex tri puta zaredom prođe bez Fablea |
| Q13 | pristup serveru | zasad isti korisnik (root) kroz postojeće ssh aliase; tvrda pravila u `AGENTS.md`; poseban korisnik kasnije |

## Plan (8.11.2026.)
1 potvrda odluka · 2 kostur repoa · 3 `AGENTS.md` · 4 alati za kanon · 5 mailovi (uputa, predlošci, `sken.py`, `posalji.py`, ledger, pregled) · 6 pilot s Codexom · 7 ostale upute istim kalupom.
Trajanja koraka samo iz izmjerenog, ne odoka.
