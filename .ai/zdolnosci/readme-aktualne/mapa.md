# README aktualne — mapa

Rodzaj: wyglad
Grill: Claude Code / claude-opus-5-5
Druga opinia: Codex / GPT-6, 2026-10-13 (nie w pełni zaślepiona: omyłkowo odczytana cała mapa przed analizą)
Spec: [spec.md](spec.md) — zaakceptowany 2026-10-13

## Problem

`README.md` i `README_PL.md` obiecują rzeczy, których kod nie robi albo robi inaczej (instalacja, wersja Pythona, import z CSV, przykłady konfiguracji), a po `aktualizacja-zaleznosci` rozjazd się powiększył. Osoba, która zaczyna od README, kopiuje przykłady, które nie działają, i nie wie, czego biblioteka naprawdę wymaga.

## Następny krok

skill buduj readme-aktualne → ticket 07

## Otwarte pytania

- [x] [badanie] Czy nazwa `node4j` jest wolna w PyPI (pod planowaną publikację) — na 2026-10-12 tak (404 w JSON i Simple API na PyPI i TestPyPI). Nie jest jednak rezerwowana do pierwszego uploadu, a listy nazw zabronionych i reguły „too similar” nie da się sprawdzić bez próbnego uploadu (np. na TestPyPI przy wydaniu) — [badanie](../../badania/2026-10-12-nazwa-node4j-pypi.md); nie blokuje spec
- [x] [grill] Lista stron w `docs/` i kolejność czytania — ustalone przy krojeniu 2026-10-13: README → modele i schemat → zapytania i filtry → relacje → operacje masowe i agregacje → transakcje → mixiny → konfiguracja i logowanie → APOC → GDS → znane ograniczenia (tickety 01–08)
- [x] [badanie] Jakie URL-e/ścieżki `apoc.load.json` obsługuje i gdzie plik musi być dostępny — po stronie aplikacji czy serwera Neo4j? — plik czyta i zapisuje **serwer**. Import i eksport plików są domyślnie wyłączone (`apoc.import.file.enabled`, `apoc.export.file.enabled` = `false`, ustawiane w `apoc.conf` albo w Dockerze przez `NEO4J_apoc_*`). `file:///x.json` jest rozwiązywane względem katalogu import serwera, a ścieżka absolutna spoza niego nie działa. HTTP(S) działa bez tych ustawień. `apoc.export.json.all` pisze do katalogu import. Obecny CI dostałby błąd „not enabled” — [badanie](../../badania/2026-10-13-apoc-load-json-sciezki.md); źródło: druga opinia Codex / GPT-6
- [x] [prototyp] Jak plik wejściowy dla przykładu `create_from_json` trafia do katalogu import serwera? `APOC.Export.to_json` zapisuje plik na serwerze w katalogu import, a `apoc.load.json` odczytuje go jako rekord z kluczami `id`, `labels`, `properties`, `type`. Prototyp przed poprawką zgłosił brak parametrów `url` i `path`; poprawkę z testem regresji zawiera osobny commit `565d29a`, a fałszywe założenie zapisano w [lekcjach](../../lekcje.md). [Raport prototypu](../../eksperymenty/2026-10-14-apoc-export-import.md)
- [x] [badanie] Jakie wersje Neo4j i GDS można opisać jako zgodne, skoro CI uruchamia tylko APOC? — według dokumentacji GDS: Neo4j 5.26 ↔ GDS 2.13, Neo4j 2026.09 ↔ GDS 2026.09; plugin `graph-data-science` (Community darmowe, do 4 rdzeni). Wywołania z `node4j/ext/gds.py` pasują do sygnatur w obu wersjach. Niesprawdzone uruchomieniem — CI nie stawia GDS — [badanie](../../badania/2026-10-13-gds-zgodnosc.md); nie blokuje spec; źródło: druga opinia Codex / GPT-6

## Decyzje

- 2026-10-14 — importer `ApocManager.create_from_json` tworzy `uid` po stronie Neo4j przez `randomUUID()` jako ograniczony wyjątek od generowania UID po stronie klienta — [ADR 0003](../../decyzje/0003-tozsamosc-wezla-uid.md)
- 2026-10-12 — Zakres: przepisanie dokumentacji od nowa (nowa struktura), a nie tylko poprawki istniejącego README — decyzja użytkownika; zastępuje otwarte pytanie o zakres (poprawność / brakujące API)
- 2026-10-12 — Forma: krótkie README (czym jest, instalacja, szybki start, linki) + strony Markdown w `docs/`, czytane na GitHubie; bez generatora stron i hostingu — zero nowych zależności, pakiet i tak nie jest publikowany (P-17 otwarte); generowana strona (MkDocs) odłożona (`proby.md` 2026-10-12)
- 2026-10-12 — Czytelnik: programista znający Pythona, async i podstawy Neo4j, który używa biblioteki we własnej aplikacji; dokumentacja prowadzi od instalacji po rozszerzenia, a pułapki (daty jako tekst, nieznany sufiks filtra = równość) opisuje wprost. Strona dla kontrybutorów jest poza zakresem — ta wiedza zostaje w AGENTS.md (rozstrzyga P-01)
- 2026-10-12 — Języki: README i `docs/` w pełni po angielsku i po polsku, z tą samą treścią — decyzja użytkownika mimo kosztu dwóch kopii; stąd potrzeba ustalenia, czym pilnujemy ich zgodności (otwarte pytanie)
- 2026-10-12 — Pokrycie: jawny wykaz obsługiwanych metod z tej decyzji — `.q` (CRUD, `get_or_create`, `update_or_create`, `count`, `aggregate`, bulk, `apply_schema`, `update_relationship`), relacje, `Q`, prefetch, haki, `transaction()` i `atomic()`, mixiny, konfiguracja `NODE4J_*`, APOC (`version`, `Periodic`, `Export`, `create_from_json`) i GDS (z `mutate`) — czytelnik nie musi czytać kodu; granicą nie są wszystkie publiczne symbole z modułów CI; doprecyzowane po drugiej opinii (było: „całe publiczne API, które działa na serwerze” bez jawnej granicy); decyzja użytkownika po drugiej opinii (druga opinia: Codex / GPT-6)
- 2026-10-12 — Niedziałające obietnice: `connect_from_csv` (brak kodu) i triggery APOC (`ClientError` na serwerze, `proby.md` 2026-10-12) znikają z listy funkcji; osobna strona „Znane ograniczenia” wymienia triggery i pułapki z AGENTS.md (daty i `uid` jako tekst, nieznany sufiks filtra = równość, rejestr kluczowany nazwą klasy, rosnące `connection.queries`, parametry w logach DEBUG). Import z CSV zostaje w Mgle (`import-csv-apoc`) — dokumentacja nie obiecuje funkcji bez kodu. Przykłady: triggery → ograniczenia; `count` → API; `connect_from_csv` → nigdzie
- 2026-10-12 — Instalacja: dokumentacja podaje instalację z gita (`github.com/gkeb/node4j`) przez uv i pip, obok wymagania: Python 3.12+, Neo4j (wersje z CI), APOC/GDS tylko dla `node4j.ext` — bo dziś pakiet jest tylko w gicie. Publikacja w indeksie pakietów dla uv/pip jest planowana; przy tym wydaniu instrukcja zmienia się na instalację z indeksu (krok wydania, nie ta zdolność)
- 2026-10-12 — Parametr `algo` w `gds.Algo.run` i `mutate` dokumentacja pokaże jako zaufaną, stałą nazwę procedury; przykłady i opis ostrzegą, by nie przekazywać danych użytkownika, bo wartość jest wstawiana do tekstu Cyphera (Z02) — decyzja użytkownika po drugiej opinii (druga opinia: Codex / GPT-6)
- 2026-10-12 — Sprawdzanie przykładów: test pytest wyciąga bloki Pythona z dokumentacji i uruchamia je na bazie testowej jak inne testy integracyjne (sprzątanie po `scope`, Z05); blok, którego nie da się uruchomić (fragment), ma jawny znacznik pominięcia (zmienione 2026-10-13, było: „fragment, GDS — CI ma tylko APOC” — GDS trafia do CI) — rozjazd przykładu z kodem ma czerwienić CI, a nie czekać na kolejny przegląd; podtrzymane po drugiej opinii: sprawdzamy bloki Markdown, żeby test obejmował kod, który czytelnik kopiuje; osobne skrypty `.py` zwiększałyby ryzyko rozjazdu drugiego źródła
- 2026-10-13 — Test przykładu konfiguracji TTL używa osobnej fixture, która w teardownie anuluje globalne zadanie `ttl_cleanup_job`, także po błędzie; samo sprzątanie węzłów po `scope` go nie izoluje — decyzja użytkownika po drugiej opinii (druga opinia: Codex / GPT-6)
- 2026-10-13 — Przykłady APOC na plikach są uruchamiane w teście: baza testowa (CI i komenda w AGENTS.md) dostaje `NEO4J_apoc_import_file_enabled=true` i `NEO4J_apoc_export_file_enabled=true`, a plik trafia do katalogu import serwera bez montowania wolumenu. Dokumentacja pokazuje te same ustawienia, których potrzebuje użytkownik, oraz zasadę „plik leży na serwerze, `file:///nazwa.json` = katalog import”. Zdanie o „absolutnej ścieżce” znika. Pominięcie zostawiłoby niesprawdzone metody, w których zaczął się rozjazd; wolumen komplikuje CI i ścieżki Windows/Linux — decyzja użytkownika, [badanie](../../badania/2026-10-13-apoc-load-json-sciezki.md)
- 2026-10-13 — GDS w CI: baza testowa (CI i komenda w AGENTS.md) dostaje `NEO4J_PLUGINS='["apoc", "graph-data-science"]'` (Community), a przykłady GDS są wykonywane jak reszta. Dokumentacja podaje testowane pary: Neo4j 5.26 ↔ GDS 2.13, 2026.09 ↔ GDS 2026.09. Bez tego GDS byłoby jedynym niesprawdzanym miejscem dokumentacji. Instalacja przez `NEO4J_PLUGINS` na tagach z CI nie została jeszcze uruchomiona; jeśli zawiedzie, wracamy do tej decyzji — decyzja użytkownika, [badanie](../../badania/2026-10-13-gds-zgodnosc.md)
- 2026-10-13 — Sprzątanie w teście przykładów: różnica stanu (węzły, indeksy, ograniczenia, projekcje GDS sprzed strony) zamiast `scope`, bo przykłady to kod czytelnika bez `scope` — wyjątek wpisany w Z05; doprecyzowuje „sprzątanie po `scope`” z decyzji o sprawdzaniu przykładów; osobna baza odrzucona, bo Community ma jedną bazę użytkownika — decyzja użytkownika przy specu
- 2026-10-12 — Zgodność EN ↔ PL: wiodąca jest wersja angielska; lustrzane pliki (`README.md` ↔ `README_PL.md`, `docs/en/` ↔ `docs/pl/`); test sprawdza ten sam zestaw stron, tę samą liczbę nagłówków i identyczne bloki kodu (kod i komentarze w kodzie po angielsku w obu wersjach); uruchamiane są tylko bloki EN, a PL tłumaczy prozę. Automat sprawdza strukturę i kod, a przegląd człowieka — równoważność znaczenia prozy; zmienione po drugiej opinii (było: „zgodność sprawdza automat, nie przegląd”); decyzja użytkownika po drugiej opinii: test nie wykrywa rozjazdu znaczenia prozy (druga opinia: Codex / GPT-6). Przykłady: strona tylko w `docs/en/` → czerwony test; blok PL różniący się komentarzem → czerwony; inna proza → zielony i wymaga przeglądu

## Plasterki

- [01 — Test dokumentacji i nowe README z szybkim startem](tickety/01-test-dokumentacji-i-readme.md)
- [02 — Strony o modelach i schemacie oraz o zapytaniach i filtrach Q](tickety/02-modele-i-zapytania.md) — po 01
- [03 — Strona o relacjach i prefetchu](tickety/03-relacje.md) — po 01
- [04 — Strony o operacjach masowych i agregacjach oraz o transakcjach](tickety/04-masowe-agregacje-transakcje.md) — po 01
- [05 — Strony o mixinach oraz o konfiguracji i logowaniu](tickety/05-mixiny-konfiguracja.md) — po 01
- [06 — Pliki APOC w bazie testowej i strona rozszerzeń APOC](tickety/06-apoc.md) — po 01
- [07 — GDS w bazie testowej i strona rozszerzeń GDS](tickety/07-gds.md) — po 01
- [08 — Znane ograniczenia, pełne pokrycie i zamknięcie rozjazdów](tickety/08-ograniczenia-i-pokrycie.md) — po 02–07
- [09 — Po weryfikacji R1: test akceptacyjny S12](tickety/09-test-s12.md) — po 01; [weryfikacja](weryfikacja.md) R1.1
- [10 — Po weryfikacji R1: stany błędów w dokumentacji](tickety/10-stany-bledow.md) — po 01, 05, 06; [weryfikacja](weryfikacja.md) R1.2
- [11 — Po weryfikacji R1: wzmocnienie testów dokumentacji i drobne poprawki](tickety/11-wzmocnienie-testow.md) — po 01, 06; [weryfikacja](weryfikacja.md) R1.3–R1.8

## Stan sesji

2026-10-14 — ticket 06 (zrobione)
- Zrobione: naprawy `create_from_json` rozdzielone do commitów `565d29a` i `cfc9df6`, wypchnięte na `origin/main`; ich CI zielone na Neo4j 2026.09 i 5.26 ([run 38631385439](https://github.com/gkeb/node4j/actions/runs/38631385439)). Strony EN/PL zaakceptowane; konfiguracja testów APOC w CI i AGENTS.md; przykłady strony przechodzą na obu wersjach Neo4j; lokalna walidacja: 23 passed, 10 skipped bez bazy; recenzje zgodności, jakości i bezpieczeństwa bez uwag blokujących.
- Commit ticketu: `2ab4c88`, CI zielone dla obu wersji Neo4j oraz latest Pydantic ([run 38632727782](https://github.com/gkeb/node4j/actions/runs/38632727782)). Wyniki prototypu są w [raporcie](../../eksperymenty/2026-10-14-apoc-export-import.md).
- Końcowy commit statusu `25238f0` jest wypchnięty, a jego CI zielone na obu wersjach Neo4j ([run 38633082656](https://github.com/gkeb/node4j/actions/runs/38633082656)).
- Następny ruch: `skill buduj readme-aktualne → ticket 07`.
