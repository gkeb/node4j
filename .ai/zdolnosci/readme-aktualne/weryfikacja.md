# README aktualne — weryfikacja

> Rundy weryfikacji krzyżowej: domyślnie inny model niż budujący sprawdza dowiezienie względem specu i planu. Jeśli ustawienie dopuszcza ten sam model, oznacz rundę jako nieniezależną. Najnowsza runda na górze. Format: „Weryfikacja krzyżowa” w `kontrakt/praca.md` w katalogu pluginu warsztatu.

## Runda R1 — 2026-10-14 — nie przeszła

- Zakres: tickety 01–06 oraz naprawy APOC (`565d29a`, `cfc9df6`); commity `c794a65..77d2485`. Zdolność jest w `budowa` (07 i 08 do zrobienia), więc runda nie zmienia jej statusu. S5 i S11 są w tym zakresie tylko częściowe, a S6 i S10 nie są objęte.
- Weryfikator: Claude Code / claude-opus-5-5 — niezależna
- Budujący: Codex / GPT-6 (pola `budowal` w ticketach 01–06)
- Walidacja: zielona — `check_ruff_baseline.py`: bez nowych błędów, 108 zastanych. `tests/test_documentation.py` bez bazy: 23 passed, 10 skipped.
- CI: zielone dla HEAD `77d2485` ([run 38633408576](https://github.com/gkeb/node4j/actions/runs/38633408576)): Python 3.12 i 3.15 × Neo4j 5.26 i 2026.09, a także latest Pydantic, z `NODE4J_REQUIRE_TEST_DB=1`. Zielone są też commity ticketów 01–06 i `cfc9df6`. `565d29a` nie ma osobnego runu, bo wypchnięto go razem z `cfc9df6`.
- Testy mutacyjne: niewykonane (`mutacje` = `null`)
- Kryteria: 36/37 spełnione, 1 bez testu (01 → S12)
- Scenariusze w zakresie:
  - z testem akceptacyjnym:
    - S1: `test_s1_readme_is_a_clear_entry_point`, `test_s1_markdown_links_exist_and_headings_are_accessible`
    - S2: `test_s2_english_documentation_examples_execute` i testy mechanizmu `test_s2_page_runner_*`
    - S3: `test_s3_*`
    - S4: `test_s4_english_and_polish_pages_are_mirrored`
    - S7: `test_s7_documentation_does_not_promise_unimplemented_features`
    - S8: `test_s8_configuration_uses_only_builtin_settings`; wczytywanie `.env` pokrywają testy `test_N3_*`
    - S9: `test_s9_*` oraz wykonanie strony APOC w S2
  - z testem dla części dowiezionej w tym zakresie:
    - S5: `test_s5_*`
    - S11: `test_s11_*` i fikstura `cleanup_ttl_job`
  - bez testu: S12

### Uwagi

- R1.1 [blokująca] `tests/conftest.py:24`, `tests/conftest.py:37`. S12 nie ma testu akceptacyjnego. Żaden test nie nosi numeru S12 i nic nie sprawdza gałęzi „wymagana baza (tryb CI) + brak bazy → błąd” dla testów przykładów. Mechanizm istnieje w conftest i w CI zawsze ma bazę, więc ta gałąź nigdy nie jest ćwiczona. Ticket 01 ma odhaczone „S12: test akceptacyjny przechodzi”. Dowód: brak wystąpień `s12`/`S12` w `tests/`; brak testu z `NODE4J_REQUIRE_TEST_DB` poza conftest. Odwołanie: S12, kryterium ticketu 01 — otwarta (ticket 09)
- R1.2 [blokująca] `README.md`, `docs/en/configuration-and-logging.md`, `docs/en/apoc-extensions.md`. Spec → Doświadczenie → Stany → „Błąd” wymaga opisu najczęstszych błędów z komunikatem, przyczyną i krokiem: brak połączenia, wyłączony import plików APOC, brak pluginu. Dowiezione jest tylko „wyłączony import” (`docs/en/apoc-extensions.md:37`). Brak połączenia (np. `ServiceUnavailable` przy `connection.connect()`) i brak pluginu APOC (np. „There is no procedure with the name `apoc.…`”) nie występują w żadnej stronie. Żaden ticket, także 07 i 08, nie planuje tych stanów. Rodzaj `wyglad`: stany należą do przeglądu zgodności. Odwołanie: spec → Doświadczenie — otwarta (ticket 10)
- R1.3 [warto] `tests/test_documentation.py:1022-1036`, `tests/test_documentation.py:1059-1066`. Kontrole zakazanych treści są węższe niż scenariusze. S7 („import z CSV gdziekolwiek → czerwony”) łapie tylko `connect_from_csv` i angielskie „import from CSV”, więc polskie „import z CSV” czy „Import CSV” przejdą. S9 („nie twierdzi, że potrzebna jest ścieżka absolutna”) łapie tylko URL-e `file:///` z typowymi katalogami, a nie prozę („absolute path”, „ścieżka absolutna”). Obecna treść jest zgodna: `grep -i "csv\|absolut"` w `docs/` i README nic nie znajduje. Odwołanie: S7, S9, kryterium ticketu 01 „zakazane treści” — otwarta (ticket 11)
- R1.4 [warto] `tests/test_n1_relations_hooks_mixins_ext.py:416`. Z06 wskazuje ten test jako automat dla wyjątku UID, ale jest to asercja na mocku `connection.run` i porównuje tylko tekst zapytania. Konsekwencji z ADR 0003, że importowany węzeł dostaje nowy UUID różny od `uid` ze źródła, nie sprawdza żaden test na bazie. Przykład na stronie APOC kopiuje `properties(source)` razem z `uid`, ale nie porównuje `uid` węzła zaimportowanego i źródłowego. Odwołanie: Z06, ADR 0003, naprawa `cfc9df6` — otwarta (ticket 11)
- R1.5 [warto] `tests/test_documentation.py:204-209`, `tests/test_documentation.py:605-657`. S3 mówi: „raport testów pokazuje [blok] jako pominięty razem z powodem”. Pominięty blok trafia tylko do `UserWarning` i `user_properties`, a test strony ma status `passed`. Testy S3 sprawdzają funkcje pomocnicze (`_parse_markdown`, `_page_runner_source`, `_report_skipped_blocks` z atrapą `Request`), a nie przebieg pytest na stronie z pominiętym blokiem. Dziś żadna strona nie używa znacznika, więc ścieżka nie jest ćwiczona w CI. Odwołanie: S3 — otwarta (ticket 11)
- R1.6 [drobna] `tests/test_documentation.py:804-814`. Doświadczenie wymaga linku powrotnego do README na każdej stronie, a test wymusza go tylko dla `apoc-extensions.md`. Pozostałe strony mają link, ale kontrola nie chroni ich przed regresją — otwarta (ticket 11)
- R1.7 [drobna] `docs/en/apoc-extensions.md:86`. Przykład `apoc.Periodic.iterate` działa na pustym wejściu (`UNWIND [] AS source`), więc czytelnik nie widzi efektu wrappera. Działanie pokazuje dopiero `connection.run` z `apoc.periodic.iterate`. Zachowanie wrappera sprawdza `test_N1_apoc_periodic_iterate_changes_matching_nodes`, więc ryzyko dotyczy treści, nie kodu — otwarta (ticket 11)
- R1.8 [drobna] Rozjazdy w metadanych ticketów:
  - `budowal` w 05 i 06 ma format `2026-10-14 — Codex / GPT-6`, a nie `<narzędzie> / <model>`;
  - ticket 06 ma `blokowany-przez: []`, a mapa → Plasterki mówi „po 01”.
  — otwarta (ticket 11)
