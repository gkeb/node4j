# Źródła

> Pliki z zamiarem użytkownika i zastana dokumentacja projektu: co jest, gdzie, na ile aktualne. Treści nie kopiujemy — linkujemy. Wypełniają skille `start`, `poznaj` i `pomysl`.

## Zamiar

<!-- Pliki, w których użytkownik spisał, czego chce. Rozbiera je skill `pomysl`.
- `POMYSL.md` — cały projekt — rozebrany 2026-10-02 (commit a1b2c3d)
- `docs/platnosci.md` — zdolność platnosci — rozebrany 2026-10-05 (commit e4f5a6b)
-->

## Dokumenty

- `README.md`, `README_PL.md` — punkt wejścia do biblioteki, instalacji, szybkiego startu i stron tematycznych; wersje EN i PL — aktualność: sprawdzone 2026-10-15, zgodne z kodem poza wpisami oznaczonymi niżej jako poza zakresem zdolności `readme-aktualne`
- `docs/en/*.md`, `docs/pl/*.md` — lustrzane strony tematyczne biblioteki po angielsku i polsku, z wykonywalnymi przykładami i stroną znanych ograniczeń — aktualność: sprawdzone 2026-10-15 w zdolności [readme-aktualne](zdolnosci/readme-aktualne/mapa.md)

## Decyzje

Brak zastanych ADR-ów w repo. Katalog `.ai/decyzje/`, format z szablonu warsztatu; 3 ADR-y `zastana` odtworzone z kodu 2026-10-11 (0001–0003).

## Rozjazdy

<!-- Dokument mówi X, kod robi Y. Rozstrzyga człowiek.
- [ ] `docs/api.md` § Limity: 100 zapytań/min — kod: 60 (`…`) — dokument nieaktualny | bug | do ustalenia
-->

- [x] `README.md` § Installation: `pip install pydantic neo4j-driver python-dotenv` — kod: zależności runtime `neo4j`, `pydantic`, `pydantic-settings` (`pyproject.toml`, od 2026-10-12) — ustalone w zdolności [readme-aktualne](zdolnosci/readme-aktualne/mapa.md)
- [x] `README.md` odznaka „python 3.10+” — kod: `requires-python = ">=3.12"`, `.python-version` 3.12 — ustalone w zdolności [readme-aktualne](zdolnosci/readme-aktualne/mapa.md)
- [x] `README.md` § Bulk Relationship Creation from CSV: `Person.apoc.connect_from_csv(...)` i „import z JSON i CSV” — kod: `ApocManager` ma tylko `create_from_json` (`node4j/ext/apoc.py`) — ustalone w zdolności [readme-aktualne](zdolnosci/readme-aktualne/mapa.md); import CSV pozostaje poza zakresem
- [x] `README.md` § Automatic Data Expiry (TTL): węzły usuwane automatycznie — kod czyścił `MATCH (n:TTL)` i porównywał tekst ISO z `datetime()` — bug, naprawiony 2026-10-11 (`fix: TTL usuwa wygasłe węzły`, test `tests/test_ttl.py`); README zgodne
- [x] `README.md` § Quick Start: `load_dotenv()` i `from dotenv import load_dotenv` — kod: `.env` czyta `pydantic-settings` (`node4j/config.py`), `python-dotenv` jest tylko zależnością dev — ustalone w zdolności [readme-aktualne](zdolnosci/readme-aktualne/mapa.md)
- [x] `README.md` § Defining Models: `datetime.datetime.utcnow()` — przestarzałe od Pythona 3.12, a projekt wymaga 3.12 — ustalone w zdolności [readme-aktualne](zdolnosci/readme-aktualne/mapa.md)
- [x] `README.md` § Key Features: „Management of database triggers” — kod: `apoc.Trigger.*` istnieje, ale na serwerze rzuca `ClientError` (`proby.md` 2026-10-12) — README nie obiecuje tej funkcji; stan opisuje [readme-aktualne](zdolnosci/readme-aktualne/mapa.md)
- [x] `README.md` § Requirements: `docker-compose` z `neo4j:5-enterprise`, `NEO4JLABS_PLUGINS` i `version: '3.8'` — projekt testuje na `neo4j:2026.09.0` i `5.26` z `NEO4J_PLUGINS` (AGENTS.md → Uruchamianie, CI) — ustalone w zdolności [readme-aktualne](zdolnosci/readme-aktualne/mapa.md)
- [x] `README.md`: komentarze i komunikaty w przykładach po polsku w wersji angielskiej — ustalone w zdolności [readme-aktualne](zdolnosci/readme-aktualne/mapa.md)
- [x] `README.md` § Bulk JSON Import: „Wymaga absolutnej ścieżki do pliku” (`file:///path/to/...`) — APOC: plik leży na serwerze, `file:///` jest rozwiązywane względem katalogu import, a import z plików jest domyślnie wyłączony ([badanie](badania/2026-10-13-apoc-load-json-sciezki.md)) — ustalone w zdolności [readme-aktualne](zdolnosci/readme-aktualne/mapa.md)
- [ ] tag `v0.2.3` (2025-07-13, `1bb03e3`) — `pyproject.toml`: `version = "0.2.2"` — do ustalenia

