# Spec refaktoryzacji: Aktualizacja zależności

> Kontrakt refaktoryzacji. Zachowanie widoczne z zewnątrz się nie zmienia — zmienia się struktura. Bez kodu; moduły nazywasz słowami.
> Zaakceptowany: 2026-10-11

## Dlaczego teraz

Biblioteka nie była rozwijana od ponad roku. Sterownik `neo4j` jest w linii 5.28, choć dostępna jest wersja główna 6.x; zgodność z aktualnymi wydaniami serwera Neo4j (2026.09, 5.26 LTS) nie jest sprawdzona. Instalacja node4j wciąga do projektu użytkownika narzędzia testowe i `structlog`, których biblioteka nie używa. Każda kolejna zdolność (`readme-aktualne`, `natywne-daty`, nowe możliwości) zaczynałaby się od starego, niesprawdzonego stosu.

## Stan obecny

Szczegóły: [mapa obszaru zależności](../../obszary/zaleznosci.md).

- Zależności runtime: `neo4j` 5.28, `pydantic` 2.11, `pydantic-settings` 2.10 oraz — choć biblioteka ich nie używa — `pytest`, `pytest-asyncio`, `python-dotenv`, `structlog`. Wersje przypięte w pliku blokady z 2025-07. Python `>=3.12`.
- Cała komunikacja z bazą przechodzi przez moduł połączenia (globalne `connection`, [ADR 0001](../../decyzje/0001-globalne-polaczenie-i-rejestr.md)): tworzenie sterownika z uwierzytelnieniem podstawowym, sprawdzenie łączności, zapytania w trybie auto-commit albo w jawnej transakcji, wynik jako lista słowników.
- Metaklasa modelu węzła dziedziczy po wewnętrznej metaklasie pydantic — najbardziej wrażliwy punkt przy podbiciu pydantic.
- Konfiguracja: ustawienia `NODE4J_*` i plik `.env` czytane przez pydantic-settings przy imporcie.
- Testy: pytest pokrywa tylko TTL na jednorazowej bazie testowej z APOC (2025.05); reszta API jest przechodzona wyłącznie przez skrypt demonstracyjny. Brak CI.

## Stan docelowy

- Zależności runtime: tylko `neo4j` 6.x, `pydantic` 2.x i `pydantic-settings` 2.x, z dolnymi granicami równymi wersjom sprawdzonym w tej zdolności i górnymi `<7`, `<3`, `<3`. `pytest`, `pytest-asyncio`, `structlog`, `python-dotenv` w grupie deweloperskiej. Wersje najnowsze z dnia rozpoczęcia kroku aktualizacji, przypięte w pliku blokady.
- Sterownik skonfigurowany bez automatycznych ponowień zapisów auto-commit (`disable_auto_commit_retries`), żeby aktualizacja nie zmieniła semantyki zapisów.
- Python bez zmian: `>=3.12`.
- Testy charakteryzujące pytest dla N1–N3 na jednorazowej bazie testowej.
- CI (GitHub Actions): macierz serwer (2026.09, 5.26 LTS) × Python (3.12, najnowszy) na pliku blokady; osobny przebieg na najnowszym `pydantic` 2.x; ruff; budowa dystrybucji i instalacja w czystym środowisku poza katalogiem źródeł z importem publicznego API. CI kończy się błędem, gdy baza jest niedostępna albo wymagany test integracyjny zostaje pominięty.
- Zasady: Z01–Z04 bez zmian; P-05 i P-07 w profilu rozstrzygnięte.

## Niezmienniki

N1. **Publiczne API.** Dla tych samych wywołań i danych zwraca te same wyniki i wywołuje te same efekty w bazie: model węzła (pola, etykiety, rejestr), menedżer `.q` (`create`, `match_one`, `match_all` z `prefetch` i `order_by`, `update`, `delete`, `count`, `aggregate`, `get_or_create`, `update_or_create`, `bulk_create`, `bulk_update`, `apply_schema`, `connect`, `disconnect`, `update_relationship`), filtry `Q` (operatory i `&`, `|`, `~`), relacje (lazy load, prefetch zagnieżdżony, `connect`/`disconnect` na instancji, modele relacji), haki cyklu życia, transakcja atomowa (zatwierdzenie i wycofanie, zakaz zagnieżdżania), miękkie usunięcie (`.q` i `.all_objects`), TTL, opakowania APOC.
N2. **Format danych w bazie.** Etykiety (nazwa klasy i przodków), `uid` jako tekst, daty jako tekst ISO w dotychczasowej postaci (także daty „naiwne” z przykładowych modeli), nazwy indeksów i constraintów z `apply_schema` i TTL. Węzły zapisane przed aktualizacją są czytane po niej bez migracji.
N3. **Konfiguracja.** Zmienne `NODE4J_URI`, `NODE4J_USER`, `NODE4J_PASSWORD` i plik `.env` dają te same ustawienia co dziś, łącznie z wartościami domyślnymi i pierwszeństwem zmiennych środowiska przed `.env`.

## Siatka bezpieczeństwa

| Niezmiennik | Chroni dziś | Brakuje (pierwszy ticket, na starym stosie) |
| --- | --- | --- |
| N1 | testy TTL (część N1: TTL); skrypt demonstracyjny bez asercji dla większości API | testy pytest dla każdej grupy API wymienionej w N1 |
| N2 | nic | test: węzeł zapisany przez API ma w bazie oczekiwane etykiety i typy wartości (`uid`, daty jako tekst w dotychczasowym formacie); test: węzeł wstawiony surowym zapytaniem w starym formacie jest czytany przez API; test: nazwy indeksów i constraintów |
| N3 | nic | test: ustawienia ze zmiennych środowiska, z `.env`, wartości domyślne i pierwszeństwo |

Testy noszą numer niezmiennika w nazwie. Są zielone na starym stosie, zanim cokolwiek zostanie podbite, i po każdym kroku. Opakowania GDS: tylko import i budowa zapytania bez wtyczki — zgodność z wersjami GDS jest poza zakresem.

## Strategia

Każdy krok zostawia zielone testy i działający system; każdy da się wycofać osobno.

1. **Siatka** — testy charakteryzujące N1–N3 na obecnym stosie (sterownik 5.28, serwer 2025.05); CI z jednym serwerem i Pythonem 3.12, ruff, kontrola instalacji.
2. **Porządek zależności** — runtime/dev rozdzielone, bez podbijania wersji; kontrola instalacji w czystym środowisku potwierdza, że biblioteka działa bez narzędzi testowych.
3. **Drobne podbicia** — `pydantic`, `pydantic-settings`, `structlog`, `pytest`, `pytest-asyncio`, `ruff` do najnowszych z dnia kroku; granice wersji w metadanych; przebieg CI na najnowszym `pydantic` 2.x.
4. **Serwery** — macierz CI 2026.09 i 5.26 LTS × Python 3.12 i najnowszy, nadal na starym sterowniku.
5. **Sterownik `neo4j` 6.x** — jedyna zmiana wersji głównej, osobno i na końcu; wyłączone ponowienia auto-commit; obsługa zmian z [badania](../../badania/2026-10-11-sterownik-neo4j-6.md) (zamknięty sterownik, zmienione klasy wyjątków).

## Kryterium końca

- Plik blokady zawiera wersje najnowsze z dnia rozpoczęcia kroku 3 i 5; metadane pakietu mają tylko trzy zależności runtime z granicami ze „Stanu docelowego”.
- Testy N1–N3 i TTL zielone w CI na całej macierzy oraz w przebiegu z najnowszym `pydantic` 2.x; żaden wymagany test nie jest pominięty.
- Zainstalowana dystrybucja importuje publiczne API w czystym środowisku bez zależności deweloperskich.
- Ruff bez błędów spoza punktu odniesienia.
- Skrypt demonstracyjny przechodzi na nowym stosie na bazie testowej.

## Poza zakresem

- Podbicie wersji node4j i wydanie (skill `wydaj`).
- README EN i PL — zdolność `readme-aktualne`.
- Natywne typy temporalne w bazie i zamiana `datetime.utcnow()` na datę ze strefą — zdolność `natywne-daty` (zmienia N2).
- Zgodność opakowań GDS z wersjami wtyczki GDS.
- Nowe możliwości sterownika 6.x, pydantic i serwera (np. HTTP Query API) — osobne zdolności w Mgle, gdy wyjdą.
- Poprawki znanych błędów lint i pułapek z `AGENTS.md`, o ile aktualizacja ich nie wymusza.

## Decyzje projektowe

Z [mapy](mapa.md) → Decyzje (2026-10-11), w skrócie: serwery 2026.09 + 5.26 LTS; sterownik 6.x bez ponowień auto-commit; trzy zależności runtime z granicami majorów; Python bez zmian; siatka przed podbiciem; kolejność kroków 1–5; CI z macierzą, przebiegiem na najnowszym `pydantic` 2.x, kontrolą instalacji i błędem przy pominiętych testach; zestaw wersji ustalony na początku kroku. Druga opinia: Codex / GPT-6 i Codex / GPT-6 Astra.
