# Aktualizacja zależności — mapa

Rodzaj: refaktor
Grill: Claude Code / claude-opus-5-5
Druga opinia: Codex / GPT-6, 2026-10-11
Spec: [spec.md](spec.md) — _powstanie po grillu_

## Problem

Biblioteka nie była rozwijana od ponad roku: zależności są przestarzałe (sterownik `neo4j` 5.28 przy dostępnej wersji głównej 6.x), a zgodność z aktualnymi wydaniami serwera Neo4j nie jest sprawdzona. Kto dziś zainstaluje node4j obok aktualnych bibliotek albo podłączy go do nowego serwera, nie wie, czy to zadziała — a każda kolejna zmiana w projekcie zaczyna się od starego stosu.

## Następny krok

skill pomysl aktualizacja-zaleznosci druga-opinia (inny model niż claude-opus-5-5), potem skill spec aktualizacja-zaleznosci

## Otwarte pytania

- [ ] [grill] Auto-ponowienie błędów w `session.run` od sterownika 6.2 (`disable_auto_commit_retries`) a zapisy auto-commit (`CREATE` w `create`, `connect`) — wyłączyć, czy sprawdzić testem, że nie dubluje? Źródło: [badanie](../../badania/2026-10-11-sterownik-neo4j-6.md) § 10 — nie blokuje spec (może trafić do specu jako scenariusz)
- [ ] [grill] Górne ograniczenie wersji `pydantic` (np. `<3`) albo tylko lock — `NodeBase` dziedziczy po wewnętrznej metaklasie pydantic, więc wersja poboczna może ją zepsuć; Źródło: [obszar zależności](../../obszary/zaleznosci.md) — nie blokuje spec
- [ ] [grill] `datetime.utcnow()` (przestarzałe od Pythona 3.12) w przykładowych modelach `node4j/models.py` — zamiana na `datetime.now(timezone.utc)` w tym refaktorze? Uwaga: zmienia daty z „naiwnych” na ze strefą, czyli format zapisanego tekstu (N2); Źródło: [obszar zależności](../../obszary/zaleznosci.md) — nie blokuje spec

## Decyzje

- 2026-10-11 — Aktualizacja zależności i serwera to refaktor (zachowanie bez zmian); README to osobna zdolność `readme-aktualne` po niej; nowe możliwości odkryte po drodze → osobne zdolności w Mgle — rozdzielenie refaktoru od zmian zachowania
- 2026-10-11 — Wspierane serwery Neo4j: najnowsze wydanie kalendarzowe + 5.26 LTS; testy na obu obrazach — wielu użytkowników zostaje na LTS (uwaga: poprawka TTL używa `valueType()`, dostępne od 5.13)
- 2026-10-11 — Zależności runtime tylko `neo4j`, `pydantic`, `pydantic-settings`; `pytest`, `pytest-asyncio`, `structlog`, `python-dotenv` → grupa dev — kod biblioteki ich nie używa (Z03: stdlib `logging`); `.env` nadal działa, bo `python-dotenv` przychodzi przez `pydantic-settings` (sprawdzone `uv tree`)
- 2026-10-11 — Python: bez zmian, `requires-python >=3.12`; testy na najstarszej i najnowszej wspieranej wersji — nie zawężamy użytkownikom bez powodu
- 2026-10-11 — Niezmienniki: (N1) publiczne API bez zmian — `Node`, `.q` (CRUD, bulk, `count`, `aggregate`, `get_or_create`, `update_or_create`, `apply_schema`), `Q`, relacje (lazy, prefetch, `connect`/`disconnect`), haki, `connection` + `atomic`, mixiny, `ext.apoc`, `ext.gds`; (N2) format danych w bazie bez zmian — etykiety, `uid` i daty jako tekst, nazwy indeksów i constraintów; dane zapisane starą wersją czyta nowa, bez migracji; (N3) konfiguracja `NODE4J_*` i `.env` bez zmian — refaktor nie zmienia zachowania; natywne daty to osobna zdolność w Mgle
- 2026-10-11 — Cel: sterownik `neo4j` 6.x (najnowszy 6.4); serwery testowe 2026.09 i 5.26 LTS — sterownik 6.x deklaruje zgodność z 4.4, 5.x i 2025.x/2026.x, minimum Python 3.10; API używane przez node4j (driver, `basic_auth`, `run`, jawne transakcje, `neo4j.time`, `to_native()`) bez zmian łamiących; do pilnowania: `DriverError` po zamknięciu, brak zamykania w `__del__`, zmienione klasy niektórych wyjątków ([badanie](../../badania/2026-10-11-sterownik-neo4j-6.md))
- 2026-10-11 — Siatka bezpieczeństwa: najpierw, jeszcze na starym stosie, testy charakteryzujące pytest dla N1 (API) i N2 (format danych w bazie) na jednorazowej bazie testowej; zielone przed podbiciem i po każdym kroku; `test.py` zostaje jako przykład — `test.py` ma mało asercji i czyści całą bazę (AGENTS.md → Pułapki)
- 2026-10-11 — Siatka bezpieczeństwa obejmuje też N3: test charakteryzujący zachowanie `NODE4J_*` i `.env` przed podbiciem oraz po każdym kroku — aktualizacja pydantic-settings nie może zmienić istniejącej konfiguracji (druga opinia: Codex / GPT-6)
- 2026-10-11 — Minimalne wersje `pydantic` i `pydantic-settings` w metadanych odpowiadają wersjom sprawdzonym w tej zdolności; obsługiwana jest linia Pydantic 2.x (`<3`) — nie deklarujemy zgodności ze starszymi ani przyszłymi głównymi wersjami bez testów (druga opinia: Codex / GPT-6; potwierdzone przez użytkownika)
- 2026-10-11 — Górne granice pozostałych zależności runtime odpowiadają majorom testowanym w CI: `neo4j<7`, `pydantic-settings<3` — nie deklarujemy wsparcia dla nieprzetestowanych majorów (druga opinia: Codex / GPT-6; potwierdzone przez użytkownika)
- 2026-10-11 — CI buduje dystrybucję, instaluje ją poza checkoutem w czystym środowisku z zależnościami runtime i sprawdza import/publiczne API — weryfikuje metadane instalacyjne po przeniesieniu narzędzi testowych i `structlog` do grupy dev (druga opinia: Codex / GPT-6)
- 2026-10-11 — Kroki: (1) testy charakteryzujące na starym stosie → (2) porządek zależności runtime/dev bez podbijania → (3) drobne podbicia (pydantic, pydantic-settings, structlog, pytest, pytest-asyncio, ruff) → (4) serwery testowe 2026.09 i 5.26 LTS ze starym sterownikiem → (5) sterownik `neo4j` 6.x — po każdym kroku zielone testy; jedyna zmiana wersji głównej osobno i na końcu, żeby problemy serwera i sterownika się nie mieszały
- 2026-10-11 — CI w tej zdolności: GitHub Actions z macierzą serwer (2026.09, 5.26 LTS) × Python (3.12, najnowszy), Neo4j jako service container, plus ruff; workflow powstaje zaraz po testach charakteryzujących (krok 1), macierz serwerów dochodzi w kroku 4 — cztery kombinacje ręcznie przy każdej zmianie to za dużo; rozstrzyga P-07. Do sprawdzenia przy budowie: widoczność repo (minuty Actions)
- 2026-10-11 — Kryterium końca: zależności w najnowszych wersjach z dnia budowy (zaktualizowany `uv.lock`); testy charakteryzujące i TTL zielone w CI na całej macierzy; ruff bez błędów spoza `odniesienie.znane`; `test.py` przechodzi na nowym stosie na bazie testowej; N1–N3 bez zmian. Poza zakresem: podbicie wersji node4j i wydanie (skill `wydaj`), README (`readme-aktualne`), nowe możliwości

## Plasterki

## Stan sesji

2026-10-11 — grill (bez ticketów)
- Zrobione: grill (decyzje w mapie), [badanie sterownika 6.x](../../badania/2026-10-11-sterownik-neo4j-6.md), [mapa obszaru zależności](../../obszary/zaleznosci.md); wcześniej w tej sesji poprawka TTL (`b6f3fe7`) i pierwsze testy pytest w `tests/`
- W połowie: nic
- Nieoczywiste: testy pytest potrzebują bazy testowej z APOC na porcie 7688 (komenda w AGENTS.md → Uruchamianie); na porcie 7687 działa prywatna baza użytkownika `my-knowledge-graph-db` — nie używać jej w testach. Obraz `neo4j:2025.05.1` jest lokalnie, więc bazę testową da się postawić bez sieci. Połączenie z github.com bywało niedostępne — push ponawiać.
- Niezacommitowane: nie
- Pierwszy ruch w następnej sesji: skill pomysl aktualizacja-zaleznosci druga-opinia w innym modelu niż claude-opus-5-5 (np. Codex), potem skill spec aktualizacja-zaleznosci
