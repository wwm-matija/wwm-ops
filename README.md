# wwm-ops

Radni sustav World Winery Map (WWM): upute, predlošci, alati i odluke po kojima rade **svi** agenti
(Codex, Gemini Antigravity, Claude) i svaki čovjek koji dođe na projekt. Kod aplikacije **nije** ovdje:
pipeline i kanon su u `vino_world`, API u `wwm_api`, worker u `wwm_worker` (isti GitHub račun).

## Gdje ovo živi
- GitHub: `wwm-matija/wwm-ops` (istina)
- Hetzner: `/root/wwm_ops` (klon; agenti rade odavde na serveru)
- Laptop Matije: `C:\Users\world\wwm-ops` (klon; odavde se pokreću Codex i Antigravity)

## Struktura
| mapa / datoteka | što je |
|---|---|
| `AGENTS.md` | pravila i način rada; Codex ga čita sam. `CLAUDE.md` i `GEMINI.md` samo pokazuju na njega |
| `upute/` | jedna datoteka po poslu, korak po korak (`mailovi.md`, kasnije `pr_objave.md`, `popravci.md` …) |
| `predlosci/` | tekstovi mailova po vrsti i jeziku, Matijine riječi |
| `alati/` | skripte koje upute pozivaju; svaka ima opis na vrhu |
| `odluke/` | `YYYY-MM-DD-tema.md` s ODLUČI na vrhu; Matija upiše odluku ispod |
| `out/POSLANO.csv` | ledger svakog poslanog maila (datum, kome, sandučić, predložak, tko odobrio) |
| `KANON_KRATKI.md` | sažetak zadnjih redaka kanona `SUSTAV_RADA.md`; obnavlja ga `alati/kanon_kratki.py` |

## Kako početi (čovjek ili agent)
1. Pročitaj `AGENTS.md`.
2. Pročitaj `KANON_KRATKI.md`.
3. Otvori `upute/<posao>.md` i radi redom. Posao nije gotov dok red nije upisan u kanon (`alati/kanon_red.py`)
   i dok poslano nije u `out/POSLANO.csv`.
