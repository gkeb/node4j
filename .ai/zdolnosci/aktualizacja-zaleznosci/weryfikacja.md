# Aktualizacja zależności — weryfikacja

> Rundy weryfikacji krzyżowej: domyślnie inny model niż budujący sprawdza dowiezienie względem specu i planu. Jeśli ustawienie dopuszcza ten sam model, oznacz rundę jako nieniezależną. Najnowsza runda na górze. Format: „Weryfikacja krzyżowa” w `kontrakt/praca.md` w katalogu pluginu warsztatu.

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
