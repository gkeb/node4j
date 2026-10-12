# Aktualizacja zależności — mapa

Rodzaj: refaktor
Grill: Claude Code / claude-opus-5-5
Druga opinia: Codex / GPT-6, 2026-10-11; Codex / GPT-6 Astra, 2026-10-11
Spec: [spec.md](spec.md) — zaakceptowany 2026-10-11

## Problem

Biblioteka nie była rozwijana od ponad roku: zależności są przestarzałe (sterownik `neo4j` 5.28 przy dostępnej wersji głównej 6.x), a zgodność z aktualnymi wydaniami serwera Neo4j nie jest sprawdzona. Kto dziś zainstaluje node4j obok aktualnych bibliotek albo podłączy go do nowego serwera, nie wie, czy to zadziała — a każda kolejna zmiana w projekcie zaczyna się od starego stosu.

## Następny krok

skill `buduj aktualizacja-zaleznosci` → ticket 10, potem 06

## Stan sesji

Ticket 10: w toku — domknięcie siatki po R2.

## Otwarte pytania


## Decyzje

- 2026-10-11 — Aktualizacja zależności i serwera to refaktor (zachowanie bez zmian); README to osobna zdolność `readme-aktualne` po niej; nowe możliwości odkryte po drodze → osobne zdolności w Mgle — rozdzielenie refaktoru od zmian zachowania
- 2026-10-11 — Wspierane serwery Neo4j: najnowsze wydanie kalendarzowe + 5.26 LTS; testy na obu obrazach — wielu użytkowników zostaje na LTS (uwaga: poprawka TTL używa `valueType()`, dostępne od 5.13)
- 2026-10-11 — Zakres zgodności obejmuje bazowy serwer Neo4j i testowane użycie APOC w TTL; zgodność `ext.gds` z wersjami wtyczki GDS jest poza zakresem tej zdolności — nie rozszerzamy obietnicy ponad macierz CI (druga opinia: Codex / GPT-6 Astra; potwierdzone przez użytkownika)
- 2026-10-11 — Konfigurujemy sterownik z `disable_auto_commit_retries=True`, by aktualizacja nie wprowadzała automatycznych ponowień zapisów `session.run` (druga opinia: Codex / GPT-6 Astra; potwierdzone przez użytkownika)
- 2026-10-11 — Zależności runtime tylko `neo4j`, `pydantic`, `pydantic-settings`; `pytest`, `pytest-asyncio`, `structlog`, `python-dotenv` → grupa dev — kod biblioteki ich nie używa (Z03: stdlib `logging`); `.env` nadal działa, bo `python-dotenv` przychodzi przez `pydantic-settings` (sprawdzone `uv tree`)
- 2026-10-11 — Python: bez zmian, `requires-python >=3.12`; testy na najstarszej i najnowszej wspieranej wersji — nie zawężamy użytkownikom bez powodu
- 2026-10-11 — Niezmienniki: (N1) publiczne API bez zmian — `Node`, `.q` (CRUD, bulk, `count`, `aggregate`, `get_or_create`, `update_or_create`, `apply_schema`), `Q`, relacje (lazy, prefetch, `connect`/`disconnect`), haki, `connection` + `atomic`, mixiny, `ext.apoc`, `ext.gds`; (N2) format danych w bazie bez zmian — etykiety, `uid` i daty jako tekst, nazwy indeksów i constraintów; dane zapisane starą wersją czyta nowa, bez migracji; (N3) konfiguracja `NODE4J_*` i `.env` bez zmian — refaktor nie zmienia zachowania; natywne daty to osobna zdolność w Mgle
- 2026-10-11 — W tym refaktorze nie zamieniamy `datetime.utcnow()` na datę ze strefą — N2 wymaga zachowania formatu zapisu, a natywne daty są osobną zdolnością w Mgle (druga opinia: Codex / GPT-6 Astra)
- 2026-10-11 — Cel: sterownik `neo4j` 6.x (najnowszy 6.4); serwery testowe 2026.09 i 5.26 LTS — sterownik 6.x deklaruje zgodność z 4.4, 5.x i 2025.x/2026.x, minimum Python 3.10; API używane przez node4j (driver, `basic_auth`, `run`, jawne transakcje, `neo4j.time`, `to_native()`) bez zmian łamiących; do pilnowania: `DriverError` po zamknięciu, brak zamykania w `__del__`, zmienione klasy niektórych wyjątków ([badanie](../../badania/2026-10-11-sterownik-neo4j-6.md))
- 2026-10-11 — Siatka bezpieczeństwa: najpierw, jeszcze na starym stosie, testy charakteryzujące pytest dla N1 (API) i N2 (format danych w bazie) na jednorazowej bazie testowej; zielone przed podbiciem i po każdym kroku; `test.py` zostaje jako przykład — `test.py` ma mało asercji i czyści całą bazę (AGENTS.md → Pułapki)
- 2026-10-11 — Siatka bezpieczeństwa obejmuje też N3: test charakteryzujący zachowanie `NODE4J_*` i `.env` przed podbiciem oraz po każdym kroku — aktualizacja pydantic-settings nie może zmienić istniejącej konfiguracji (druga opinia: Codex / GPT-6)
- 2026-10-11 — Minimalne wersje `pydantic` i `pydantic-settings` w metadanych odpowiadają wersjom sprawdzonym w tej zdolności; obsługiwana jest linia Pydantic 2.x (`<3`) — nie deklarujemy zgodności ze starszymi ani przyszłymi głównymi wersjami bez testów (druga opinia: Codex / GPT-6; potwierdzone przez użytkownika; podtrzymane po drugiej opinii: osobny job dla minimum byłby redundantny, bo dolne granice runtime są ustawiane na wersje sprawdzane w głównej macierzy)
- 2026-10-11 — Górne granice pozostałych zależności runtime odpowiadają majorom testowanym w CI: `neo4j<7`, `pydantic-settings<3` — nie deklarujemy wsparcia dla nieprzetestowanych majorów (druga opinia: Codex / GPT-6; potwierdzone przez użytkownika)
- 2026-10-11 — Oprócz głównej macierzy na `uv.lock`, CI ma osobny przebieg na najnowszym Pydantic 2.x — chroni deklarowane `<3` przed zmianą wewnętrznej metaklasy w wydaniu pobocznym (druga opinia: Codex / GPT-6 Astra; potwierdzone przez użytkownika)
- 2026-10-11 — Zestaw najnowszych zależności wybieramy na początku kroku aktualizacji; `uv.lock` pozostaje punktem odniesienia do końca zdolności, bez wciągania wydań opublikowanych w trakcie (druga opinia: Codex / GPT-6 Astra; potwierdzone przez użytkownika)
- 2026-10-11 — CI buduje dystrybucję, instaluje ją poza checkoutem w czystym środowisku z zależnościami runtime i sprawdza import/publiczne API — weryfikuje metadane instalacyjne po przeniesieniu narzędzi testowych i `structlog` do grupy dev (druga opinia: Codex / GPT-6)
- 2026-10-11 — Kroki: (1) testy charakteryzujące na starym stosie → (2) porządek zależności runtime/dev bez podbijania → (3) drobne podbicia (pydantic, pydantic-settings, structlog, pytest, pytest-asyncio, ruff) → (4) serwery testowe 2026.09 i 5.26 LTS ze starym sterownikiem → (5) sterownik `neo4j` 6.x — po każdym kroku zielone testy; jedyna zmiana wersji głównej osobno i na końcu, żeby problemy serwera i sterownika się nie mieszały
- 2026-10-11 — CI w tej zdolności: GitHub Actions z macierzą serwer (2026.09, 5.26 LTS) × Python (3.12, najnowszy), Neo4j jako service container, plus ruff; workflow powstaje zaraz po testach charakteryzujących (krok 1), macierz serwerów dochodzi w kroku 4 — cztery kombinacje ręcznie przy każdej zmianie to za dużo; rozstrzyga P-07. Do sprawdzenia przy budowie: widoczność repo (minuty Actions)
- 2026-10-11 — CI kończy się błędem, gdy wymagana baza Neo4j jest niedostępna albo wymagany test integracyjny zostaje pominięty — zielony wynik ma potwierdzać rzeczywiste wykonanie N1–N3 na całej macierzy (druga opinia: Codex / GPT-6 Astra)
- 2026-10-11 — Kryterium końca: zależności w najnowszych wersjach z dnia budowy (zaktualizowany `uv.lock`); testy charakteryzujące i TTL zielone w CI na całej macierzy; ruff bez błędów spoza `odniesienie.znane`; `test.py` przechodzi na nowym stosie na bazie testowej; N1–N3 bez zmian. Poza zakresem: podbicie wersji node4j i wydanie (skill `wydaj`), README (`readme-aktualne`), nowe możliwości

## Plasterki

- [01 — Siatka: format danych i konfiguracja](tickety/01-siatka-format-danych-i-konfiguracja.md)
- [02 — Siatka: menedżer `.q` i filtry `Q`](tickety/02-siatka-menedzer-i-filtry.md)
- [03 — Siatka: relacje, haki, transakcje, mixiny, rozszerzenia](tickety/03-siatka-relacje-haki-transakcje-mixiny.md)
- [04 — CI na starym stosie](tickety/04-ci-na-starym-stosie.md) — po 01, 02, 03
- [05 — Porządek zależności runtime/dev](tickety/05-porzadek-zaleznosci.md) — po 04
- [06 — Drobne podbicia i granice wersji](tickety/06-drobne-podbicia-i-granice.md) — po 05, 09 i 10
- [07 — Macierz serwerów i Pythona](tickety/07-macierz-serwerow-i-pythona.md) — po 06
- [08 — Sterownik `neo4j` 6.x](tickety/08-sterownik-neo4j-6.md) — po 07
- [09 — Po weryfikacji R1: wzmocnienie siatki](tickety/09-po-weryfikacji-r1-wzmocnienie-siatki.md) — przed 06; uwagi R1.1–R1.5
- [10 — Po weryfikacji R2: domknięcie siatki](tickety/10-po-weryfikacji-r2-domkniecie-siatki.md) — przed 06; uwagi R2.2–R2.4
