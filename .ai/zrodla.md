# Źródła

> Pliki z zamiarem użytkownika i zastana dokumentacja projektu: co jest, gdzie, na ile aktualne. Treści nie kopiujemy — linkujemy. Wypełniają skille `start`, `poznaj` i `pomysl`.

## Zamiar

<!-- Pliki, w których użytkownik spisał, czego chce. Rozbiera je skill `pomysl`.
- `POMYSL.md` — cały projekt — rozebrany 2026-10-02 (commit a1b2c3d)
- `docs/platnosci.md` — zdolność platnosci — rozebrany 2026-10-05 (commit e4f5a6b)
-->

## Dokumenty

- `README.md`, `README_PL.md` — opis biblioteki, konfiguracji, mixinów i rozszerzeń; wersje EN i PL o tej samej treści — aktualność: częściowa (sprawdzone 2026-10-11, rozjazdy niżej)

## Decyzje

Brak zastanych ADR-ów w repo. Katalog `.ai/decyzje/`, format z szablonu warsztatu; 3 ADR-y `zastana` odtworzone z kodu 2026-10-11 (0001–0003).

## Rozjazdy

<!-- Dokument mówi X, kod robi Y. Rozstrzyga człowiek.
- [ ] `docs/api.md` § Limity: 100 zapytań/min — kod: 60 (`…`) — dokument nieaktualny | bug | do ustalenia
-->

- [ ] `README.md` § Installation: `pip install pydantic neo4j-driver python-dotenv` — kod: zależności `neo4j`, `pydantic-settings`, `structlog` (`pyproject.toml`) — do ustalenia
- [ ] `README.md` odznaka „python 3.10+” — kod: `requires-python = ">=3.12"`, `.python-version` 3.12 — do ustalenia
- [ ] `README.md` § Bulk Relationship Creation from CSV: `Person.apoc.connect_from_csv(...)` i „import z JSON i CSV” — kod: `ApocManager` ma tylko `create_from_json` (`node4j/ext/apoc.py`) — do ustalenia
- [ ] `README.md` § Automatic Data Expiry (TTL): węzły usuwane automatycznie — kod: zadanie czyści `MATCH (n:TTL)`, a węzły dostają etykiety `TTLMixin` + nazwę klasy (`node4j/nodes.py` → `NodeBase`), `ttl` zapisuje się jako tekst ISO (`model_dump(mode="json")`), więc `n.ttl < datetime()` nie zachodzi; `test.py` krok 25 omija mechanizm — sprawdzone bez bazy 2026-10-11 — bug (wniosek)
- [ ] tag `v0.2.3` (2025-07-13, `1bb03e3`) — `pyproject.toml`: `version = "0.2.2"` — do ustalenia

