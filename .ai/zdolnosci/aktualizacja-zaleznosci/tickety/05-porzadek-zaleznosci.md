---
nr: "05"
tytul: "Porządek zależności runtime/dev"
status: do-zrobienia
blokowany-przez: ["04"]
scenariusze: [N1, N2, N3]
budowal: null
github: null
---

# 05 — Porządek zależności runtime/dev

## Co widać po zrobieniu

Metadane pakietu mają w zależnościach runtime tylko `neo4j`, `pydantic`, `pydantic-settings`; `pytest`, `pytest-asyncio`, `structlog`, `python-dotenv` są w grupie deweloperskiej. Wersje bez zmian.

## Kryteria akceptacji

- [ ] N1, N2, N3: testy zielone (lokalnie i w CI)
- [ ] kontrola instalacji w CI zielona — zainstalowana dystrybucja importuje API bez zależności deweloperskich
- [ ] `.env` nadal działa (N3) — `python-dotenv` przychodzi przez `pydantic-settings`
- [ ] plik blokady zaktualizowany bez podbijania wersji

## Poza zakresem

- Podbijanie wersji — ticket 06.

## Notatki

