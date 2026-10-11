---
poznany-commit: face3137f39d8764f276b52134d4638fa37c9727
zrodla-kodu: ["pyproject.toml", "uv.lock", ".python-version", "node4j/db.py", "node4j/manager.py", "node4j/nodes.py", "node4j/properties.py", "node4j/config.py", "node4j/models.py", "tests/", "test.py"]
---

# Obszar: zależności

- Katalogi: `pyproject.toml`, `uv.lock`, `.python-version`; punkty styku w `node4j/`, `tests/`, `test.py`
- Poznany: 2026-10-11

## Za co odpowiada

Zestaw bibliotek, od których zależy node4j, i miejsca w kodzie, które ich używają. Mapa służy zdolności [aktualizacja-zaleznosci](../zdolnosci/aktualizacja-zaleznosci/mapa.md): co może się zepsuć przy podbiciu i gdzie patrzeć.

## Moduły i przepływy

Stan na `uv.lock` z 2025-07 (`uv tree --outdated`, 2026-10-11):

| Biblioteka | Wersja → najnowsza | Używa jej |
| --- | --- | --- |
| `neo4j` | 5.28.1 → 6.4.0 | `node4j/db.py`, `node4j/manager.py`, `node4j/properties.py`, testy |
| `pydantic` | 2.11.7 → 2.14.1 | `node4j/nodes.py`, `node4j/manager.py`, `node4j/properties.py`, `node4j/edges.py`, `node4j/models.py` |
| `pydantic-settings` | 2.10.1 → 2.15.0 | `node4j/config.py` |
| `python-dotenv` | 1.1.1 → 1.2.4 | tylko przykłady w README; przychodzi też przez `pydantic-settings` (`uv tree`) |
| `structlog` | 25.4.0 → 26.1.0 | tylko `test.py` |
| `pytest`, `pytest-asyncio` | 8.4.1 → 9.1.1, 1.0.0 → 1.4.0 | `tests/` |
| `ruff` (dev) | 0.12.1 → 0.17.0 | walidacja (`pyproject.toml` → `[tool.ruff]`) |

Wszystkie poza `ruff` są w `[project] dependencies`, czyli instalują się u użytkownika biblioteki (`pyproject.toml`). (wniosek) `pytest` trafił tam w `1bf857a`, `structlog` w `1bb03e3` — dodane bez `--dev`.

**Sterownik `neo4j`** — całe połączenie jest w `node4j/db.py` → `AsyncDatabase`:
- `connect`: `AsyncGraphDatabase.driver(uri, auth=basic_auth(...))` + `verify_connectivity()`;
- `run`: w jawnej transakcji `active_tx.run(...)`, poza nią sesja i auto-commit `session.run(...)`; wynik zawsze `await response.data()` (lista słowników);
- `transaction`: `session.begin_transaction()`, `tx.closed()`, `commit()`, `rollback()`, transakcja w `ContextVar`;
- `node4j/manager.py` → `_convert_neo4j_temporals`: `neo4j.time.DateTime/Date/Time/Duration` i `to_native()` przy prefetch;
- `node4j/properties.py`: import `neo4j.graph.Relationship` — nieużywany (F401 w punkcie odniesienia);
- wyjątki: `ServiceUnavailable` (`tests/conftest.py`), `ConstraintError` (`test.py`).

Zmiany 6.x względem tych miejsc: [badanie 2026-10-11](../badania/2026-10-11-sterownik-neo4j-6.md) — bez zmian łamiących w użytym API; do pilnowania ponawianie auto-commit (6.2), `DriverError` po zamknięciu, klasy części wyjątków.

**`pydantic`**:
- `node4j/nodes.py` → `NodeBase(type(BaseModel))` dziedziczy po wewnętrznej `pydantic._internal._model_construction.ModelMetaclass`; przed `super().__new__` wycina z `attrs` atrybuty `RelationshipProperty`, po utworzeniu klasy dopisuje deskryptory, `_relationships`, `_meta`, `__labels__` i `q` — zależy od zachowania wewnętrznego API pydantic;
- publiczne API v2: `model_validate`, `model_dump(mode="json")` (format zapisu w bazie — ADR 0003, pułapka o datach w `AGENTS.md`), `model_fields_set` (`manager.py` → `create`), `PrivateAttr` (`_internal_id`), `ClassVar`, `model_config = {"arbitrary_types_allowed": True}`.

**`pydantic-settings`** — `node4j/config.py` → `Settings(BaseSettings)` z `SettingsConfigDict(env_prefix="NODE4J_", env_file=".env", extra="ignore")`; instancja tworzona przy imporcie modułu.

**Python** — `.python-version` 3.12, `requires-python >=3.12`. `datetime.datetime.utcnow()` (przestarzałe od 3.12) w `node4j/models.py` → `AuditLog.timestamp`, `Person.pre_save`.

## Testy

- `tests/test_ttl.py` — tylko TTL; reszta API bez testów pytest. `test.py` przechodzi większość API, ale z niewieloma asercjami.
- Uruchomienie: `uv run pytest` na bazie testowej (AGENTS.md → Uruchamianie).

## Decyzje

- [ADR 0001](../decyzje/0001-globalne-polaczenie-i-rejestr.md) — globalne `connection`, jedna baza na proces.
- [ADR 0003](../decyzje/0003-tozsamosc-wezla-uid.md) — `uid` jako tekst przez `model_dump(mode="json")`.
- Z03 — biblioteka loguje przez stdlib `logging`, więc `structlog` nie jest jej zależnością.

## Pułapki

- Podbicie `pydantic` może zepsuć `NodeBase` bez zmiany publicznego API pydantic — najpierw testy.
- `connection` to singleton: sterownik jest związany z pętlą zdarzeń, w której powstał; testy otwierają i zamykają go w każdym teście (`tests/conftest.py` → `db`).
- `uv.lock` przypina wszystko; `uv lock --upgrade` podbija naraz — strategia zdolności zakłada podbicia krokami.

## Źródła

- `pyproject.toml`, `uv.lock`, `uv tree --outdated` (2026-10-11), `uv tree --package pydantic-settings`
- Kod: pliki i symbole wymienione wyżej
- Historia: `git log -- pyproject.toml uv.lock` (`1bf857a`, `1bb03e3`, `8a27795`)
- [Badanie sterownika neo4j 6.x](../badania/2026-10-11-sterownik-neo4j-6.md)
