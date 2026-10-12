# Aktualizacja zależności — weryfikacja

> Rundy weryfikacji krzyżowej: domyślnie inny model niż budujący sprawdza dowiezienie względem specu i planu. Jeśli ustawienie dopuszcza ten sam model, oznacz rundę jako nieniezależną. Najnowsza runda na górze. Format: „Weryfikacja krzyżowa” w `kontrakt/praca.md` w katalogu pluginu warsztatu.

## Runda R3 — 2026-10-12 — przeszła

- Zakres: cała zdolność (tickety 01–10; nowe od R2: 06, 07, 08, 10) — commity bfdeb3d..4e84cab, w tej rundzie szczegółowo b702527..4e84cab. Status w `ROADMAP.md` nadal `budowa`, choć 10/10 ticketów zrobione (R3.1) — runda prowadzona mimo to, bo nic poza statusem nie jest otwarte
- Weryfikator: Claude Code / claude-opus-5-5 — niezależna
- Budujący: Codex / GPT-6 (pole `budowal` we wszystkich ticketach 01–10; commity kodu bez stopki Claude)
- Walidacja: zielona — `uv run ruff check .` + `scripts/check_ruff_baseline.py`: bez nowych, 113 zastanych. `uv run pytest -W error::ResourceWarning` z `NODE4J_REQUIRE_TEST_DB=1` na jednorazowej bazie `neo4j:2026.09.0` z APOC: 69 passed, 0 skipped; `test.py` na tej bazie: „All tests completed successfully!”
- CI: 4e84cab (głowa, pełny hash `4e84cab…`) — success ([run 38292868940](https://github.com/gkeb/node4j/actions/runs/38292868940)): Python 3.12/3.15 × Neo4j 2026.09.0/5.26 oraz Latest Pydantic 2.x — wszystkie kroki zielone (pytest, `test.py`, ruff, build, instalacja poza checkoutem z importem 10 modułów)
- Kryteria: 06 — 3/3, 07 — 3/3, 08 — 5/5, 10 — 6/6 spełnione; 01–05 i 09 potwierdzone w R1–R2
- Niezmienniki i kryterium końca (refaktor):
  - N1 — `tests/test_n1_manager_and_filters.py`, `tests/test_n1_relations_hooks_mixins_ext.py`, `tests/test_ttl.py`, `tests/test_driver_config.py` (bez ponowień auto-commit, sprzątanie sterownika po błędzie i anulowaniu, `DriverError` na zamkniętym sterowniku, zachowany `ConnectionAcquisitionTimeoutError`); `connect()` przed zmianą też zostawiał `driver = None` przy błędzie (wczesny `return`, gdy driver istnieje), więc zmiana w `node4j/db.py` dodaje tylko zamknięcie sterownika
  - N2 — `tests/test_n2_data_format.py` (zapis, odczyt starego formatu, nazwy indeksów, constraintów i `ttl_index`)
  - N3 — `tests/test_n3_config.py`
  - Kryterium końca: lock `neo4j 6.4.0`, `pydantic 2.14.1`, `pydantic-settings 2.15.0`, `pytest 9.1.1`, `pytest-asyncio 1.4.0`, `ruff 0.17.0`, `structlog 26.1.0` (zgodne z Notatkami 06 i badaniem); `pyproject.toml` — trzy zależności runtime z granicami `<7`, `<3`, `<3`; pozostałe punkty — CI wyżej
- Poza zakresem i decyzje z mapy: nie złamane (bez podbicia wersji node4j, README, `utcnow()` i GDS bez zmian; `disable_auto_commit_retries=True` w `node4j/db.py:53`)
- ZASADY Z01–Z03: bez naruszeń w diffie kodu produkcyjnego (`node4j/db.py`: tylko async, bez nowego Cypher, `log = logging.getLogger(__name__)`)
- Testy mutacyjne: nie skonfigurowane (`mutacje: null`)

### Uwagi

- R3.1 [drobna] `.ai/ROADMAP.md:13` — zdolność ma status `budowa`, choć ostatni ticket jest zrobiony; według przebiegu w kontrakcie powinna przejść w `weryfikacja` przed tą rundą — kontrakt/praca.md → Przebieg — naprawiona (zamknięcie, `ROADMAP.md` → Zrobione)
- R3.2 [drobna] `.ai/warsztat.json` → `odniesienie.znane` — punkt odniesienia ma 119 błędów, w kodzie zostało 113 (formatowanie `node4j/db.py` usunęło 6); limit z punktu odniesienia pozwala dziś dodać do 6 nowych błędów tego samego kodu w `db.py` bez wykrycia. Zdolność `porzadek-lint` w Mgle i tak go wyzeruje — Kryterium końca („Ruff bez błędów spoza punktu odniesienia”) — naprawiona (zamknięcie: usunięte 3 wpisy `db.py`, 113 = stan kodu)
- R3.3 [drobna] `.ai/profil.md:14` (P-07: „obecnie Neo4j 2025.05.1 / Python 3.12”) i `.ai/obszary/zaleznosci.md:29` („Wszystkie poza `ruff` są w `[project] dependencies`”) opisują stan sprzed zdolności; hook zgłasza zmienione źródła mapy obszaru — do odświeżenia przez `poznaj zaleznosci` i edycję profilu — Stan docelowy („P-05 i P-07 w profilu rozstrzygnięte”) — naprawiona (`735054e`)

## Runda R2 — 2026-10-12 — nie przeszła

- Zakres: tickety 04, 05, 09, zdolność nadal w `budowa` — commity 3101889..bfe9d5f
- Weryfikator: Claude Code / claude-opus-5-5 — niezależna
- Budujący: Codex / GPT-6 (pole `budowal` w ticketach 04, 05, 09)
- Walidacja: zielona — `uv run ruff check .` 119 błędów, `scripts/check_ruff_baseline.py`: bez nowych; ten sam skrypt z dopisanym sztucznym F401 kończy się kodem 1. `uv run pytest` z `NODE4J_REQUIRE_TEST_DB=1` na jednorazowej bazie 2025.05.1 z APOC: 63 passed, 0 skipped; bez bazy w tym trybie: 57 errors, exit 1; bez bazy w trybie domyślnym: 57 skipped
- CI: 514a6a7 (głowa ticketów 04–05) — success ([run](https://github.com/gkeb/node4j/actions/runs/38272909921)); 3101889 — success; bfe9d5f (ticket 09) — brak przebiegu, commit niewypchnięty
- Kryteria: 04 — 5/5, 05 — 4/4, 09 — 7/7 spełnione; zastrzeżenia w R2.2–R2.3
- Niezmienniki: N1 — nowe testy `match_all` z prefetch, `Periodic.iterate` z efektem, triggery na prawdziwej bazie; N3 — `test_N3_default_settings_read_cwd_dotenv_and_environment_overrides`; N2 bez zmian
- Testy mutacyjne: nie skonfigurowane (`mutacje: null`)
- Domknięcie uwag R2.2–R2.4: ticket 10, commit `c5f11a9fa886f5f48946ee35e0edb432172f55d5`; CI success ([run](https://github.com/gkeb/node4j/actions/runs/38281973210))

### Uwagi

- R2.1 [blokująca] commit bfe9d5f (ticket 09) — brak przebiegu CI, bo commit nie jest wypchnięty (`main` ahead 1). Lokalnie zielony; do zamknięcia wystarczy push i zielony przebieg dla pełnego hasha, bez ticketu — DoD ticketu, „Wynik rundy” — naprawiona: push 6ae56e0 (ten sam kod co bfe9d5f + tylko `.ai/`), CI success ([run](https://github.com/gkeb/node4j/actions/runs/38279662319))
- R2.2 [warto] `.github/workflows/ci.yml:71` — kontrola instalacji importuje tylko `node4j`, `node4j.db`, `node4j.nodes`, `node4j.query`; spec wymaga importu publicznego API, a N1 obejmuje też `node4j.mixins`, `node4j.managers`, `node4j.properties`, `node4j.edges`, `node4j.ext.apoc`, `node4j.ext.gds`. Dziś żaden moduł pakietu nie importuje zależności deweloperskich (`grep structlog|pytest|dotenv node4j/` — pusto), więc to luka na przyszłość, nie błąd — ticket 04, Stan docelowy specu — naprawiona (ticket 10)
- R2.3 [drobna] `tests/test_n1_relations_hooks_mixins_ext.py` (testy `test_N1_apoc_trigger_*`) — przypinają dowolny `ClientError`, bez kodu błędu; zmiana przyczyny (np. procedura usunięta z APOC zamiast „wymaga bazy `system`”) przejdzie niezauważona. Przypięcie `e.code` uściśliłoby siatkę przed ticketem 08 (zmienione klasy wyjątków w sterowniku 6) — N1 — naprawiona (ticket 10)
- R2.4 [drobna] `.ai/zdolnosci/aktualizacja-zaleznosci/mapa.md` → Stan sesji — nadal „Ticket 09: w toku”, choć ticket ma status `zrobione`; `AGENTS.md` → Uruchamianie nie wspomina `NODE4J_REQUIRE_TEST_DB` (tryb CI, w którym brak bazy jest błędem) — naprawiona (ticket 10)
- R1.1–R1.5 — potwierdzone jako naprawione w tickecie 09 (statusy poniżej)

## Runda R1 — 2026-10-12 — przeszła

- Zakres: tickety 01–03 (siatka bezpieczeństwa), zdolność nadal w `budowa` — commity bfdeb3d..4048586 (niewypchnięte)
- Weryfikator: Claude Code / claude-opus-5-5 — niezależna
- Budujący: Codex / GPT-6 (pole `budowal` w ticketach 01–03)
- Walidacja: zielona — `uv run ruff check .` 119 błędów, zgodnych co do kodu i pliku z `odniesienie.znane` (119); `uv run pytest` na jednorazowej bazie 2025.05.1 z APOC: 58 passed, 0 skipped
- CI: brak w projekcie (powstaje w tickecie 04) — nie dotyczy
- Kryteria: 18/18 spełnione formalnie; zastrzeżenia co do siły testów w R1.1–R1.3
- Niezmienniki: N1 — `tests/test_n1_manager_and_filters.py`, `tests/test_n1_relations_hooks_mixins_ext.py`, TTL w `tests/test_ttl.py`; N2 — `tests/test_n2_data_format.py`; N3 — `tests/test_n3_config.py`; bez testu: —
- Testy mutacyjne: nie skonfigurowane (`mutacje: null`)

### Uwagi

- R1.1 [warto] `tests/test_n1_relations_hooks_mixins_ext.py:354` — test `Periodic.iterate` sprawdza tylko `result is None` na zapytaniu bez efektu, a wrapper zawsze zwraca `None` i nie zgłasza błędów zapytania wewnętrznego (`node4j/ext/apoc.py:57`). Dowód: próba na bazie testowej z `SET n.v = 1/0` w zapytaniu wewnętrznym — wrapper zwrócił `None` bez wyjątku, węzeł bez zmian. Po podbiciu serwera albo APOC test przejdzie, nawet jeśli `iterate` przestanie cokolwiek wykonywać — N1 („te same efekty w bazie”) — naprawiona (ticket 09)
- R1.2 [warto] `tests/test_n3_config.py` — każdy test podaje `_env_file` jawnie (`None` albo ścieżkę), więc nic nie przypina domyślnego `env_file='.env'` z `node4j/config.py:15` (odczyt `.env` z katalogu roboczego przez `Settings()` bez argumentów) ani globalnego `settings`. Zmiana rozwiązywania domyślnego pliku w pydantic-settings (ticket 06) nie zostanie wykryta — N3 („plik `.env` daje te same ustawienia”) — naprawiona (ticket 09)
- R1.3 [warto] `tests/test_n1_relations_hooks_mixins_ext.py:364` — triggery APOC są przypięte wyłącznie mockiem `connection.run` (asercje na mocku), a na obecnym stosie `Triggers.install` nie działa (wymaga bazy `system`; Notatki ticketu 03). Siatka nie pokaże więc żadnej zmiany zachowania triggerów po aktualizacji serwera ani sterownika. To zastany błąd w zakresie N1 — do decyzji: osobna naprawa (`napraw`) albo wpis w Mgle i jawne wyłączenie triggerów z obietnicy N1 w mapie — naprawiona (ticket 09)
- R1.4 [drobna] `.ai/lekcje.md` — wpis o triggerach APOC nie ma rozwiązania („trzeba zapewnić kierowanie do `system`”), więc według reguły 6 i 9 powinien trafić do `.ai/proby.md` jako `nierozwiazane` (plik nie istnieje) — naprawiona (ticket 09)
- R1.5 [drobna] `tests/test_n1_relations_hooks_mixins_ext.py:211` — prefetch jest sprawdzany tylko przez `match_one` i w postaci słownika; ścieżka `match_all(prefetch=…)` (`node4j/manager.py:176`) i postać listy (`node4j/manager.py:688`) nie mają testu, choć spec wymienia `match_all` z `prefetch` — N1 — naprawiona (ticket 09)
