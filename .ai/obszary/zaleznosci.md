---
poznany-commit: 5dde256458a957ffd4d9d82cfc814031d3c4f916
zrodla-kodu: ["pyproject.toml", "uv.lock", ".python-version", "node4j/db.py", "node4j/manager.py", "node4j/nodes.py", "node4j/properties.py", "node4j/config.py", "node4j/models.py", "node4j/ext/", "README.md", "docs/en/", "tests/", "test.py", ".github/workflows/ci.yml", "scripts/check_ruff_baseline.py"]
---

# Obszar: zależności

- Katalogi: `pyproject.toml`, `uv.lock`, `.python-version`; punkty styku w `node4j/`, `tests/`, `test.py`; CI w `.github/workflows/ci.yml`
- Poznany: 2026-10-11, odświeżony 2026-10-12 po zdolności `aktualizacja-zaleznosci` i 2026-10-14 w trakcie `readme-aktualne` (tickety 01–07)

## Za co odpowiada

Zestaw bibliotek, od których zależy node4j, i miejsca w kodzie, które ich używają. Mapa służy zdolności [aktualizacja-zaleznosci](../zdolnosci/aktualizacja-zaleznosci/mapa.md): co może się zepsuć przy podbiciu i gdzie patrzeć.

## Moduły i przepływy

Stan na `uv.lock` po zdolności `aktualizacja-zaleznosci` (`uv tree --outdated --depth 1`, 2026-10-12):

| Biblioteka | Wersja w locku (najnowsza) | Grupa, granice | Używa jej |
| --- | --- | --- | --- |
| `neo4j` | 6.4.0 | runtime, `>=6.4.0,<7` | `node4j/db.py`, `node4j/manager.py`, `node4j/properties.py`, testy |
| `pydantic` | 2.14.1 | runtime, `>=2.14.1,<3` | `node4j/nodes.py`, `node4j/manager.py`, `node4j/properties.py`, `node4j/edges.py`, `node4j/models.py` |
| `pydantic-settings` | 2.15.0 (2.16.0, `uv tree --outdated`, 2026-10-14) | runtime, `>=2.15.0,<3` | `node4j/config.py` |
| `python-dotenv` | 1.1.1 (1.2.4) | dev; do runtime przychodzi przez `pydantic-settings` (`uv tree`) | nikt w repo go nie importuje (`grep dotenv`, 2026-10-14); dokumentacja zakazuje `load_dotenv` ([spec readme-aktualne](../zdolnosci/readme-aktualne/spec.md) → S8, `tests/test_documentation.py` → `test_s8_configuration_uses_only_builtin_settings`); `.env` czyta `pydantic-settings` (`node4j/config.py`), który ciągnie go sam — (wniosek) wpis w dev zbędny, Mgła `zaleznosci-dev-dotenv` |
| `structlog` | 26.1.0 | dev | tylko `test.py` |
| `pytest`, `pytest-asyncio` | 9.1.1, 1.4.0 | dev | `tests/` |
| `ruff` | 0.17.0 | dev | walidacja (`pyproject.toml` → `[tool.ruff]`) |

Runtime to tylko trzy biblioteki z `[project] dependencies`; reszta w `[dependency-groups] dev` (`pyproject.toml`). Podział i granice: [mapa zdolności](../zdolnosci/aktualizacja-zaleznosci/mapa.md) → Decyzje. Wcześniej `pytest` i `structlog` były w runtime (`1bf857a`, `1bb03e3`), przeniesione w `d014c0c`.

**Sterownik `neo4j`** — całe połączenie jest w `node4j/db.py` → `AsyncDatabase`:
- `connect`: `AsyncGraphDatabase.driver(uri, auth=basic_auth(...), disable_auto_commit_retries=True)` + `verify_connectivity()`; `self.driver` ustawiany dopiero po udanym sprawdzeniu, a przy błędzie albo anulowaniu (`BaseException`) sterownik jest zamykany i wyjątek rzucany dalej bez tłumaczenia (`4360472`);
- `run`: w jawnej transakcji `active_tx.run(...)`, poza nią sesja i auto-commit `session.run(...)`; wynik zawsze `await response.data()` (lista słowników);
- `transaction`: `session.begin_transaction()`, `tx.closed()`, `commit()`, `rollback()`, transakcja w `ContextVar`;
- `node4j/manager.py` → `_convert_neo4j_temporals`: `neo4j.time.DateTime/Date/Time/Duration` i `to_native()` przy prefetch;
- `node4j/properties.py`: import `neo4j.graph.Relationship` — nieużywany (F401 w punkcie odniesienia);
- wyjątki: `ServiceUnavailable` (`tests/conftest.py`), `ClientError` z kodem (`tests/test_n1_relations_hooks_mixins_ext.py` → triggery APOC), `DriverError` i `ConnectionAcquisitionTimeoutError` (`tests/test_driver_config.py`), `ConstraintError` (`test.py`).

Zmiany 6.x względem tych miejsc: [badanie 2026-10-11](../badania/2026-10-11-sterownik-neo4j-6.md) — bez zmian łamiących w użytym API; obsłużone w tickecie 08: ponowienia auto-commit wyłączone, `DriverError` na zamkniętym sterowniku i zachowane klasy wyjątków przypięte w `tests/test_driver_config.py`, zamykanie sterownika jawne (6.x nie zamyka w `__del__`; CI uruchamia testy z `-W error::ResourceWarning`).

**`pydantic`**:
- `node4j/nodes.py` → `NodeBase(type(BaseModel))` dziedziczy po wewnętrznej `pydantic._internal._model_construction.ModelMetaclass`; przed `super().__new__` wycina z `attrs` atrybuty `RelationshipProperty`, po utworzeniu klasy dopisuje deskryptory, `_relationships`, `_meta`, `__labels__` i `q` — zależy od zachowania wewnętrznego API pydantic;
- publiczne API v2: `model_validate`, `model_dump(mode="json")` (format zapisu w bazie — ADR 0003, pułapka o datach w `AGENTS.md`), `model_fields_set` (`manager.py` → `create`), `PrivateAttr` (`_internal_id`), `ClassVar`, `model_config = {"arbitrary_types_allowed": True}`.

**`pydantic-settings`** — `node4j/config.py` → `Settings(BaseSettings)` z `SettingsConfigDict(env_prefix="NODE4J_", env_file=".env", extra="ignore")`; instancja tworzona przy imporcie modułu.

**Wtyczki serwera Neo4j** — nie są pakietami Pythona, ale `node4j/ext/apoc.py` i `node4j/ext/gds.py` wywołują ich procedury, a przykłady z dokumentacji wykonują je w testach:
- APOC: import i eksport plików wyłączone domyślnie; baza testowa ma `NEO4J_apoc_import_file_enabled=true` i `NEO4J_apoc_export_file_enabled=true` (`.github/workflows/ci.yml`, AGENTS.md → Uruchamianie); `apoc.create.uuid()` nie działa w Neo4j 2026.09, dlatego importer używa `randomUUID()` ([proby.md](../proby.md) 2026-10-14, [ADR 0003](../decyzje/0003-tozsamosc-wezla-uid.md));
- GDS (Community): testowane pary Neo4j 5.26 ↔ GDS 2.13 i 2026.09 ↔ GDS 2026.09 (`docs/en/gds-extensions.md`, [badanie](../badania/2026-10-13-gds-zgodnosc.md));
- instalacja w CI i lokalnie przez `NEO4J_PLUGINS='["apoc", "graph-data-science"]'` przy starcie kontenera — (wniosek) wersję wtyczki dobiera obraz Neo4j, więc nie ma jej w `uv.lock`, a start bazy wymaga sieci.

**Python** — `.python-version` 3.12, `requires-python >=3.12`. `datetime.datetime.utcnow()` (przestarzałe od 3.12) w `node4j/models.py` → `AuditLog.timestamp`, `Person.pre_save`.

## Testy

- Siatka niezmienników zdolności `aktualizacja-zaleznosci`: N1 — `tests/test_n1_manager_and_filters.py`, `tests/test_n1_relations_hooks_mixins_ext.py`, `tests/test_ttl.py`; N2 — `tests/test_n2_data_format.py`; N3 — `tests/test_n3_config.py`; sterownik — `tests/test_driver_config.py` (bez bazy).
- Uruchomienie: `uv run pytest` na bazie testowej (AGENTS.md → Uruchamianie). `NODE4J_REQUIRE_TEST_DB=1` zamienia brak bazy i pominięty test integracyjny (test z fiksturą `db`) w błąd (`tests/conftest.py` → `db`, `pytest_sessionfinish`).
- CI (`.github/workflows/ci.yml`): job `test` — macierz Python 3.12/3.15 × Neo4j `2026.09.0`/`5.26` z APOC i GDS (dostęp APOC do plików włączony) na `uv.lock`, potem `test.py`, ruff względem `odniesienie.znane` (`scripts/check_ruff_baseline.py` sam uruchamia `python -m ruff`), budowa paczki i import 10 modułów publicznego API z instalacji poza checkoutem z samymi zależnościami runtime; job `latest-pydantic` — najnowszy Pydantic 2.x na Neo4j 2026.09.
- Test dokumentacji (`tests/test_documentation.py`) wykonuje bloki Pythona z README i `docs/en/` w podprocesie przez `sys.executable` — przykłady widzą tylko zainstalowane zależności (runtime + dev). Zrzut stanu bazy przed i po stronie wywołuje `gds.graph.list()` (`_gds_projection_names`), więc każdy test wykonujący przykłady wymaga GDS na bazie testowej, także dla stron bez GDS.
- `test.py` przechodzi większość API, ale z niewieloma asercjami; w CI dostaje `NODE4J_*` jawnie zmapowane z `NODE4J_TEST_*`.

## Decyzje

- [ADR 0001](../decyzje/0001-globalne-polaczenie-i-rejestr.md) — globalne `connection`, jedna baza na proces.
- [ADR 0003](../decyzje/0003-tozsamosc-wezla-uid.md) (`przyjęta` 2026-10-14) — `uid` jako tekst przez `model_dump(mode="json")`; wyjątek: importer APOC nadaje `uid` po stronie Neo4j przez `randomUUID()` (Z06 w `ZASADY.md`).
- Z03 — biblioteka loguje przez stdlib `logging`, więc `structlog` nie jest jej zależnością.

## Pułapki

- Podbicie `pydantic` może zepsuć `NodeBase` bez zmiany publicznego API pydantic — najpierw testy.
- `connection` to singleton: sterownik jest związany z pętlą zdarzeń, w której powstał; testy otwierają i zamykają go w każdym teście (`tests/conftest.py` → `db`).
- `uv.lock` przypina wszystko; `uv lock --upgrade` podbija naraz — strategia zdolności zakłada podbicia krokami.
- Job `latest-pydantic` działa tylko na Neo4j 2026.09 i nie uruchamia `test.py`; zgodność najnowszego Pydantic z 5.26 nie jest sprawdzana osobno.
- `scripts/check_ruff_baseline.py` porównuje z licznikami `odniesienie.znane` w `.ai/warsztat.json`. Licznik wyższy niż stan kodu kończy się błędem z podpowiedzią nowej wartości (`main` → `stale`, retro 2026-10-12), więc rozwiązany problem z weryfikacji R3.2 pilnuje automat; poprawka zmniejsza licznik w tym samym commicie.
- Wtyczka niedostępna albo w złej wersji (np. GDS niepasujące do Neo4j) czerwieni testy dokumentacji wszystkich stron, nie tylko strony GDS — zob. Testy.

## Źródła

- `pyproject.toml`, `uv.lock`, `uv tree --outdated` (2026-10-11, 2026-10-12), `uv tree --package pydantic-settings`
- `.github/workflows/ci.yml`, `scripts/check_ruff_baseline.py`, `tests/conftest.py`
- Kod: pliki i symbole wymienione wyżej
- `docs/en/apoc-extensions.md`, `docs/en/gds-extensions.md`, `tests/test_documentation.py`, `node4j/ext/`
- Historia: commity `readme-aktualne#01`–`#07` i naprawy `565d29a`, `cfc9df6` (`c794a65..5dde256`); `git log -- pyproject.toml uv.lock` (`1bf857a`, `1bb03e3`, `8a27795`); commity `aktualizacja-zaleznosci#01`–`#10` (`bfdeb3d..4e84cab`)
- [Badanie sterownika neo4j 6.x](../badania/2026-10-11-sterownik-neo4j-6.md)
