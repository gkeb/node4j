---
nr: "05"
tytul: "Porządek zależności runtime/dev"
status: zrobione
blokowany-przez: ["04"]
scenariusze: [N1, N2, N3]
budowal: "Codex / GPT-6"
github: null
---

# 05 — Porządek zależności runtime/dev

## Co widać po zrobieniu

Metadane pakietu mają w zależnościach runtime tylko `neo4j`, `pydantic`, `pydantic-settings`; `pytest`, `pytest-asyncio`, `structlog`, `python-dotenv` są w grupie deweloperskiej. Wersje bez zmian.

## Kryteria akceptacji

- [x] N1, N2, N3: testy zielone (lokalnie i w CI)
- [x] kontrola instalacji w CI zielona — zainstalowana dystrybucja importuje API bez zależności deweloperskich
- [x] `.env` nadal działa (N3) — `python-dotenv` przychodzi przez `pydantic-settings`
- [x] plik blokady zaktualizowany bez podbijania wersji

## Poza zakresem

- Podbijanie wersji — ticket 06.

## Notatki

- Lokalnie: N1–N3 — 58 testów zaliczonych; testy konfiguracji N3 — 4 zaliczone; Ruff bez nowych błędów (119 błędów zastanych).
- CI GitHub Actions: N1–N3 i TTL, Ruff oraz instalacja dystrybucji poza checkoutem przeszły — [run 2](https://github.com/gkeb/node4j/actions/runs/38272595987).

