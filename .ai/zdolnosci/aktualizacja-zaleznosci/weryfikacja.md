# Aktualizacja zależności — weryfikacja

> Rundy weryfikacji krzyżowej: domyślnie inny model niż budujący sprawdza dowiezienie względem specu i planu. Jeśli ustawienie dopuszcza ten sam model, oznacz rundę jako nieniezależną. Najnowsza runda na górze. Format: „Weryfikacja krzyżowa” w `kontrakt/praca.md` w katalogu pluginu warsztatu.

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

- R1.1 [warto] `tests/test_n1_relations_hooks_mixins_ext.py:354` — test `Periodic.iterate` sprawdza tylko `result is None` na zapytaniu bez efektu, a wrapper zawsze zwraca `None` i nie zgłasza błędów zapytania wewnętrznego (`node4j/ext/apoc.py:57`). Dowód: próba na bazie testowej z `SET n.v = 1/0` w zapytaniu wewnętrznym — wrapper zwrócił `None` bez wyjątku, węzeł bez zmian. Po podbiciu serwera albo APOC test przejdzie, nawet jeśli `iterate` przestanie cokolwiek wykonywać — N1 („te same efekty w bazie”) — otwarta (ticket 09)
- R1.2 [warto] `tests/test_n3_config.py` — każdy test podaje `_env_file` jawnie (`None` albo ścieżkę), więc nic nie przypina domyślnego `env_file='.env'` z `node4j/config.py:15` (odczyt `.env` z katalogu roboczego przez `Settings()` bez argumentów) ani globalnego `settings`. Zmiana rozwiązywania domyślnego pliku w pydantic-settings (ticket 06) nie zostanie wykryta — N3 („plik `.env` daje te same ustawienia”) — otwarta (ticket 09)
- R1.3 [warto] `tests/test_n1_relations_hooks_mixins_ext.py:364` — triggery APOC są przypięte wyłącznie mockiem `connection.run` (asercje na mocku), a na obecnym stosie `Triggers.install` nie działa (wymaga bazy `system`; Notatki ticketu 03). Siatka nie pokaże więc żadnej zmiany zachowania triggerów po aktualizacji serwera ani sterownika. To zastany błąd w zakresie N1 — do decyzji: osobna naprawa (`napraw`) albo wpis w Mgle i jawne wyłączenie triggerów z obietnicy N1 w mapie — otwarta (ticket 09)
- R1.4 [drobna] `.ai/lekcje.md` — wpis o triggerach APOC nie ma rozwiązania („trzeba zapewnić kierowanie do `system`”), więc według reguły 6 i 9 powinien trafić do `.ai/proby.md` jako `nierozwiazane` (plik nie istnieje) — otwarta (ticket 09)
- R1.5 [drobna] `tests/test_n1_relations_hooks_mixins_ext.py:211` — prefetch jest sprawdzany tylko przez `match_one` i w postaci słownika; ścieżka `match_all(prefetch=…)` (`node4j/manager.py:176`) i postać listy (`node4j/manager.py:688`) nie mają testu, choć spec wymienia `match_all` z `prefetch` — N1 — otwarta (ticket 09)
