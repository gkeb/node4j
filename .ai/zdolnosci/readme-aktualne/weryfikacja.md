# README aktualne — weryfikacja

> Rundy weryfikacji krzyżowej: domyślnie inny model niż budujący sprawdza dowiezienie względem specu i planu. Jeśli ustawienie dopuszcza ten sam model, oznacz rundę jako nieniezależną. Najnowsza runda na górze. Format: „Weryfikacja krzyżowa” w `kontrakt/praca.md` w katalogu pluginu warsztatu.

## Runda R3 — 2026-10-15 — przeszła

- Zakres: cała zdolność, tickety 01–12 oraz naprawy APOC (`565d29a`, `cfc9df6`); commity `c794a65..1405785`. Od R2 doszły `73943cd..1405785` (ticket 12).
- Weryfikator: Claude Code / claude-opus-5-5 — niezależna
- Budujący: Codex / GPT-6 (pola `budowal` w ticketach 01–12)
- Walidacja: zielona — `check_ruff_baseline.py`: bez nowych błędów, 108 zastanych. Pełny `pytest` z `NODE4J_REQUIRE_TEST_DB=1` na `neo4j:2026.09.0` z APOC i GDS: 121 passed, 1 skipped (zastępczy przypadek S3 „No marked documentation blocks.”, zamierzony).
- CI: zielone dla HEAD `1405785` ([run 38806349703](https://github.com/gkeb/node4j/actions/runs/38806349703)) i dla commita ticketu `73943cd` ([run 38803696593](https://github.com/gkeb/node4j/actions/runs/38803696593)); sprawdzone przez publiczne API GitHuba.
- Usunięte asercje (`usuniete-asercje.mjs 86dbcb4..1405785`): jedna — `tests/test_documentation.py:801` „…as_skipped SKIPPED” zastąpiona mocniejszą (wymaga też identyfikatora parametru `[docs/en/guide.md-block-2]`). Asercje z listami pokrycia S5 bez zmian.
- Testy mutacyjne: niewykonane (`mutacje` = `null`); zamiast nich ręczne próby na `_missing_s5_inventory_symbols` (R3.1)
- Kryteria: 75/75 spełnione (w tym 06 i 08 → S5, przywrócone ticketem 12)
- Scenariusze specu: 12/12 z testem akceptacyjnym — jak w R2, a dodatkowo:
  - S5: `::test_s5_spec_inventory_requires_executable_python_references` (:1016) czyta 29 pozycji wykazu ze specu i sprawdza je w AST wykonywanych bloków; testy mechanizmu :1032–1102; `apoc.Periodic.iterate` wywołany w wykonywanym bloku `docs/en/apoc-extensions.md:142` z asercjami na efekt (:151, :156)
  - S3: `::test_s3_marked_documentation_block_is_reported_as_skipped` zbierany zawsze (:669, :679), a okablowanie `_marked_documentation_block_cases` ćwiczy przebieg pytest na syntetycznym drzewie `docs/en/` (:910)

### Uwagi

- R3.1 [warto] `tests/test_documentation.py` → `_missing_s5_inventory_symbols`, gałąź końcowa `is_referenced`. Pozycje wykazu o ogólnych nazwach (`run`, `version`, `count`, `connect`) są spełniane przez dowolne wywołanie z tym sufiksem. Dowód (próba na kopii źródeł w pamięci): zamiana `gds.Algo.run(` na inne wywołanie albo `apoc.version()` na `apoc.other_version()` daje `missing: []`; dla `gds.Algo.mutate(` → `['mutate']`. Dziś te pozycje chronią nadal testy z jawną listą (`test_s5_gds_methods_are_in_executable_examples`, `test_s5_complete_coverage_inventory_is_in_executable_examples`), więc pokrycie jest pełne. Gwarancja z ticketu 12 („wykazu nie da się zawęzić po cichu”) zależy jednak dla tych pozycji od kopii w teście. Kierunek: kwalifikować pozycję prefiksem sekcji wykazu (`GDS:` → `gds.`, `APOC:` → `apoc.`). Odwołanie: S5, ticket 12 — otwarta
- R3.2 [drobna] `docs/en/apoc-extensions.md:90-93`. Przykład dla czytelnika tworzy modele dynamicznie (`type(f"GuideApocPeriodicSource_{uuid4().hex}", (Node,), {})`), żeby odizolować wrapper bez parametrów. Proza wyjaśnia powód, ale wzorzec skopiowany do aplikacji rejestruje nową klasę przy każdym uruchomieniu w globalnym rejestrze kluczowanym nazwą klasy (AGENTS.md → Pułapki). Treść zaakceptowana w odbiorze (ticket 12), więc to tylko sygnał dla przyszłej zmiany wrappera (`proby.md` 2026-10-15) — otwarta
- R2.3 częściowo: `budowal` w 08 poprawiony w retro (`86dbcb4`); `test_10_…` (:2066) i niepięty komunikat `ServiceUnavailable` bez zmian — pozostaje otwarta.

## Runda R2 — 2026-10-15 — nie przeszła

- Zakres: cała zdolność, tickety 01–11 oraz naprawy APOC (`565d29a`, `cfc9df6`); commity `c794a65..6fb78e0`. Od R1 doszły `02f0ef8..6fb78e0` (tickety 07–11).
- Weryfikator: Claude Code / claude-opus-5-5 — niezależna
- Budujący: Codex / GPT-6 (pola `budowal` w ticketach 01–11)
- Walidacja: zielona — `check_ruff_baseline.py`: bez nowych błędów, 108 zastanych. Pełny `pytest` z `NODE4J_REQUIRE_TEST_DB=1` na `neo4j:2026.09.0` z APOC 2026.09.0 i GDS 2026.09.0 (jednorazowy kontener według AGENTS.md): 115 passed, 0 skipped.
- CI: zielone dla HEAD `6fb78e0` ([run 38787090582](https://github.com/gkeb/node4j/actions/runs/38787090582)) i dla ostatniego commita z kodem `18f7595` ([run 38786614471](https://github.com/gkeb/node4j/actions/runs/38786614471)). Wynik sprawdzony przez publiczne API GitHuba, bo `gh` nie był zalogowany.
- Testy mutacyjne: niewykonane (`mutacje` = `null`)
- Kryteria: 64/66 spełnione, 2 niespełnione: 06 → „S5 (część): `Periodic` w wykonywanych blokach” i 08 → „S5: test przechodzi z pełnym wykazem” (R2.1)
- Scenariusze specu: 11/12 z testem akceptacyjnym, który sprawdza scenariusz:
  - S1: `tests/test_documentation.py::test_s1_readme_is_a_clear_entry_point` (:583) i `::test_s1_markdown_links_exist_and_headings_are_accessible` (:621)
  - S2: `::test_s2_english_documentation_examples_execute` (:1480) oraz testy mechanizmu `test_s2_page_runner_*` (:809–926)
  - S3: `::test_s3_skip_markers_require_a_reason` (:638), `::test_s3_public_pytest_runner_reports_skipped_documentation_block` (:714), `::test_s3_marked_documentation_block_is_reported_as_skipped` (:669, zbierany tylko przy istniejących znacznikach); zob. R2.2
  - S4: `::test_s4_english_and_polish_pages_are_mirrored` (:929)
  - S5: `::test_s5_complete_coverage_inventory_is_in_executable_examples` (:1230) i testy stron `test_s5_*`; **pozycja `Periodic` nie jest sprawdzana (R2.1)**
  - S6: `::test_s6_known_limitations_are_explained_in_both_languages` (:1360) oraz akceptacja w odbiorze (ticket 08)
  - S7: `::test_s7_documentation_does_not_promise_unimplemented_features` (:1318)
  - S8: `::test_s8_configuration_uses_only_builtin_settings` (:1427)
  - S9: `::test_s9_*` (:967, :1000), `::test_documentation_does_not_use_absolute_apoc_file_paths` (:1447) i wykonanie strony APOC w S2
  - S10: `::test_s10_*` (:1014, :1027, :1038)
  - S11: `::test_s11_*` (:1438, :1468, :1504) oraz fikstura `cleanup_ttl_job` (:567)
  - S12: `::test_s12_missing_test_database_uses_public_pytest_runner` (:1654)
- Niezmienniki słownika: „Dokumentacja użytkownika” — S4 (te same strony, nagłówki i bloki) oraz S2 i S3 (każdy blok EN wykonany albo jawnie pominięty).
- Stany „Błąd” (R1.2): brak połączenia (`docs/en/configuration-and-logging.md:31`, link z `README.md:35`), brak pluginu APOC (`docs/en/apoc-extensions.md:26`) i wyłączony import plików — w EN i PL.
- Akceptacja wyglądu: wpisana w ticketach 07, 08, 10 i 11.

### Uwagi

- R2.1 [blokująca] `docs/en/apoc-extensions.md:80-183`, `tests/test_documentation.py:1198-1211`, `tests/test_documentation.py:1283`. Pozycja `Periodic` z wykazu pokrycia nie występuje w żadnym wykonywanym bloku, a testy pokrycia osłabiono tak, że tego nie wykrywają. Ticket 11 (`a498275`), naprawiając R1.7, usunął jedyne wywołanie `await apoc.Periodic.iterate(...)` z wykonywanego bloku. Przykład wywołuje teraz procedurę surowym Cypherem przez `connection.run`. W tym samym commicie asercje `"await apoc.Periodic.iterate("` i `"apoc.Periodic.iterate("` zamieniono na `"CALL apoc.periodic.iterate("`. Wrapper biblioteki pojawia się już tylko w prozie (`docs/en/apoc-extensions.md:57`). Tabela S5 mówi: „wspomniana tylko w prozie → czerwony”. Dowód: `grep -rn "Periodic" docs/ README*.md` zwraca wyłącznie linię 57 w EN i PL, a `git log -p a498275 -- tests/test_documentation.py` pokazuje usunięte asercje. Wpis w `proby.md` (2026-10-15) uzasadnia wybór surowego wywołania dla widocznego efektu z markerem. Nie zmienia to jednak wykazu w specu ani decyzji „Pokrycie” w mapie, które wymieniają `Periodic`. Rozwiązanie wymaga jednego z dwóch: wykonywany blok znów wywołuje `apoc.Periodic.iterate`, a test pokrycia tego wymaga (np. obok obecnego przykładu, na zapytaniu ograniczonym etykietą unikalną dla strony, bez wstawiania wartości do Cyphera), albo decyzja człowieka zmienia wykaz pokrycia (spec i mapa). Odwołanie: S5, kryteria ticketów 06 („S5 (część)”) i 08 („pełny wykaz”), mapa → Decyzje → Pokrycie — naprawiona (ticket 12)
- R2.2 [warto] `tests/test_documentation.py:652-670`, `tests/test_documentation.py:714-806`. Po tickecie 11 S3 sprawdza przebieg pytest, ale na replice, nie na prawdziwym okablowaniu. Test potomny w `test_s3_public_pytest_runner_reports_skipped_documentation_block` definiuje własną funkcję testową, która woła `_report_skipped_blocks`. Prawdziwy test `test_s3_marked_documentation_block_is_reported_as_skipped` jest definiowany warunkowo (`if _MARKED_DOCUMENTATION_BLOCK_CASES:`) i zbiera bloki tylko z `_english_pages()`. Żadna strona nie ma znacznika, więc nie jest zbierany ani w CI, ani lokalnie. Usunięcie go albo zmiana `_marked_documentation_block_cases` (np. pominięcie stron `docs/en/`) nie zaczerwieni żadnego testu. Raport dla stron, które mają zarazem bloki wykonywane i pominięte, zależy właśnie od tego testu. Odwołanie: S3, R1.5 — naprawiona (ticket 12)
- R2.3 [drobna] Ślad i metadane:
  - `tests/test_documentation.py:1740`: `test_10_apoc_unregistered_procedure_error_comes_from_server` nosi numer ticketu, nie scenariusza (spec → Testy → Ślad);
  - komunikat `ServiceUnavailable` w `docs/en/configuration-and-logging.md:36` nie jest przypięty testem, w przeciwieństwie do komunikatu APOC, więc zmiana treści w sterowniku nie zaczerwieni CI (ticket 10: „komunikaty z prawdziwego uruchomienia”);
  - ticket 08 ma `budowal: 2026-10-15 — Codex / GPT-6` zamiast `<narzędzie> / <model>` (ten sam rozjazd co R1.8 w 05 i 06).

  — otwarta

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

- R1.1 [blokująca] `tests/conftest.py:24`, `tests/conftest.py:37`. S12 nie ma testu akceptacyjnego. Żaden test nie nosi numeru S12 i nic nie sprawdza gałęzi „wymagana baza (tryb CI) + brak bazy → błąd” dla testów przykładów. Mechanizm istnieje w conftest i w CI zawsze ma bazę, więc ta gałąź nigdy nie jest ćwiczona. Ticket 01 ma odhaczone „S12: test akceptacyjny przechodzi”. Dowód: brak wystąpień `s12`/`S12` w `tests/`; brak testu z `NODE4J_REQUIRE_TEST_DB` poza conftest. Odwołanie: S12, kryterium ticketu 01 — naprawiona (ticket 09)
- R1.2 [blokująca] `README.md`, `docs/en/configuration-and-logging.md`, `docs/en/apoc-extensions.md`. Spec → Doświadczenie → Stany → „Błąd” wymaga opisu najczęstszych błędów z komunikatem, przyczyną i krokiem: brak połączenia, wyłączony import plików APOC, brak pluginu. Dowiezione jest tylko „wyłączony import” (`docs/en/apoc-extensions.md:37`). Brak połączenia (np. `ServiceUnavailable` przy `connection.connect()`) i brak pluginu APOC (np. „There is no procedure with the name `apoc.…`”) nie występują w żadnej stronie. Żaden ticket, także 07 i 08, nie planuje tych stanów. Rodzaj `wyglad`: stany należą do przeglądu zgodności. Odwołanie: spec → Doświadczenie — naprawiona (ticket 10)
- R1.3 [warto] `tests/test_documentation.py:1022-1036`, `tests/test_documentation.py:1059-1066`. Kontrole zakazanych treści są węższe niż scenariusze. S7 („import z CSV gdziekolwiek → czerwony”) łapie tylko `connect_from_csv` i angielskie „import from CSV”, więc polskie „import z CSV” czy „Import CSV” przejdą. S9 („nie twierdzi, że potrzebna jest ścieżka absolutna”) łapie tylko URL-e `file:///` z typowymi katalogami, a nie prozę („absolute path”, „ścieżka absolutna”). Obecna treść jest zgodna: `grep -i "csv\|absolut"` w `docs/` i README nic nie znajduje. Odwołanie: S7, S9, kryterium ticketu 01 „zakazane treści” — naprawiona (ticket 11)
- R1.4 [warto] `tests/test_n1_relations_hooks_mixins_ext.py:416`. Z06 wskazuje ten test jako automat dla wyjątku UID, ale jest to asercja na mocku `connection.run` i porównuje tylko tekst zapytania. Konsekwencji z ADR 0003, że importowany węzeł dostaje nowy UUID różny od `uid` ze źródła, nie sprawdza żaden test na bazie. Przykład na stronie APOC kopiuje `properties(source)` razem z `uid`, ale nie porównuje `uid` węzła zaimportowanego i źródłowego. Odwołanie: Z06, ADR 0003, naprawa `cfc9df6` — naprawiona (ticket 11)
- R1.5 [warto] `tests/test_documentation.py:204-209`, `tests/test_documentation.py:605-657`. S3 mówi: „raport testów pokazuje [blok] jako pominięty razem z powodem”. Pominięty blok trafia tylko do `UserWarning` i `user_properties`, a test strony ma status `passed`. Testy S3 sprawdzają funkcje pomocnicze (`_parse_markdown`, `_page_runner_source`, `_report_skipped_blocks` z atrapą `Request`), a nie przebieg pytest na stronie z pominiętym blokiem. Dziś żadna strona nie używa znacznika, więc ścieżka nie jest ćwiczona w CI. Odwołanie: S3 — naprawiona (ticket 11)
- R1.6 [drobna] `tests/test_documentation.py:804-814`. Doświadczenie wymaga linku powrotnego do README na każdej stronie, a test wymusza go tylko dla `apoc-extensions.md`. Pozostałe strony mają link, ale kontrola nie chroni ich przed regresją — naprawiona (ticket 11)
- R1.7 [drobna] `docs/en/apoc-extensions.md:86`. Przykład `apoc.Periodic.iterate` działa na pustym wejściu (`UNWIND [] AS source`), więc czytelnik nie widzi efektu wrappera. Działanie pokazuje dopiero `connection.run` z `apoc.periodic.iterate`. Zachowanie wrappera sprawdza `test_N1_apoc_periodic_iterate_changes_matching_nodes`, więc ryzyko dotyczy treści, nie kodu — naprawiona (ticket 11)
- R1.8 [drobna] Rozjazdy w metadanych ticketów:
  - `budowal` w 05 i 06 ma format `2026-10-14 — Codex / GPT-6`, a nie `<narzędzie> / <model>`;
  - ticket 06 ma `blokowany-przez: []`, a mapa → Plasterki mówi „po 01”.
  — naprawiona (ticket 11)
