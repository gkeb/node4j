# Spec: README aktualne — dokumentacja użytkownika

> Kontrakt zdolności. Bez kodu i bez ścieżek plików — opisuje zachowanie, nie implementację.
> Zaakceptowany: 2026-10-13

## Problem

README w wersji angielskiej i polskiej obiecuje rzeczy, których kod nie robi albo robi inaczej: instalację nieistniejących pakietów, Pythona 3.10, import z CSV, konfigurację przez `load_dotenv`, „absolutną ścieżkę” do pliku APOC i działające triggery. Po aktualizacji zależności rozjazd się powiększył. Programista, który zaczyna od README, kopiuje przykłady, które nie działają, i nie wie, czego biblioteka naprawdę wymaga. Rozjazdy są zebrane w rejestrze źródeł projektu (sekcja „Rozjazdy”).

## Rozwiązanie

Programista używający biblioteki dostaje dokumentację użytkownika (pojęcie ze słownika): krótkie README i zestaw stron tematycznych, w pełni po angielsku i po polsku. Opisuje ona wszystkie metody z wykazu pokrycia, z przykładami, które da się skopiować i uruchomić. Każdy przykład jest wykonywany automatycznie na bazie testowej, a obie wersje językowe są porównywane automatem. Następny rozjazd z kodem zaczerwieni więc testy, zamiast czekać, aż ktoś go zauważy. Rzeczy, które nie działają albo zaskakują, opisuje uczciwie strona „Znane ograniczenia”.

## Scenariusze

S1. README jako punkt wejścia — Zakładając dokumentację użytkownika, gdy czytelnik otwiera README, wtedy znajduje w nim kolejno: czym jest biblioteka, wymagania (Python 3.12+, Neo4j 5.26 LTS albo 2026.09, APOC i GDS tylko dla rozszerzeń), instalację z gita przez uv i przez pip, szybki start oraz link do każdej strony tematycznej. Każdy link prowadzi do istniejącej strony.

| Stan dokumentacji | Wynik testu |
| --- | --- |
| README linkuje każdą stronę, wszystkie linki istnieją | zielony |
| strona tematyczna, do której README nie linkuje | czerwony |
| link z README do strony, której nie ma | czerwony |

S2. Przykłady się wykonują — Zakładając bazę testową z APOC (z włączonym importem i eksportem plików) i GDS, gdy uruchamiane są testy, wtedy każdy blok Pythona w README i na stronach w wersji angielskiej wykonuje się bez błędu. Bloki jednej strony biegną po kolei we wspólnej przestrzeni nazw, jak w notatniku, a każda strona startuje od czystej przestrzeni.

| Blok | Wynik testu |
| --- | --- |
| blok wywołuje istniejącą metodę zgodnie z jej sygnaturą | zielony |
| blok wywołuje metodę, której nie ma (np. import z CSV) | czerwony |
| blok podaje argument, którego metoda nie przyjmuje | czerwony |
| blok rzuca wyjątek, a strona nie mówi, że to oczekiwane | czerwony |
| drugi blok strony korzysta z modelu zdefiniowanego w pierwszym | zielony |

S3. Jawne pominięcie — Zakładając blok oznaczony znacznikiem pominięcia z podanym powodem, gdy uruchamiane są testy, wtedy blok nie jest wykonywany, a raport testów pokazuje go jako pominięty razem z powodem.

| Blok | Wynik testu |
| --- | --- |
| bez znacznika | wykonany (S2) |
| znacznik z powodem | pominięty, powód w raporcie |
| znacznik bez powodu | czerwony |

S4. Zgodność EN ↔ PL — Zakładając obie wersje językowe, gdy uruchamiane są testy, wtedy każda strona angielska ma polski odpowiednik (README ↔ README polskie, strony ↔ strony), z tą samą liczbą nagłówków każdego poziomu i identycznymi blokami kodu w tej samej kolejności. Proza nie jest porównywana automatem, jej równoważność sprawdza przegląd człowieka.

| Różnica | Wynik testu |
| --- | --- |
| strona tylko w wersji angielskiej (albo tylko w polskiej) | czerwony |
| inna liczba nagłówków danego poziomu | czerwony |
| blok kodu w wersji polskiej różni się choćby komentarzem | czerwony |
| inna kolejność bloków kodu | czerwony |
| różni się tylko proza | zielony (wymaga przeglądu) |

S5. Pokrycie wykazu metod — Zakładając wykaz pokrycia z decyzji projektowych, gdy uruchamiane są testy, wtedy każda pozycja wykazu występuje w co najmniej jednym wykonywanym bloku dokumentacji (nie w bloku pominiętym).

| Pozycja wykazu | Wynik testu |
| --- | --- |
| użyta w wykonanym bloku | zielony |
| wspomniana tylko w prozie | czerwony |
| użyta tylko w bloku pominiętym | czerwony |

S6. Znane ograniczenia — Zakładając dokumentację użytkownika, gdy czytelnik otwiera stronę „Znane ograniczenia”, wtedy znajduje tam: triggery APOC (nie działają z domyślnej bazy), daty i `uid` zapisywane jako tekst, nieznany sufiks filtra traktowany jako równość, rejestr modeli kluczowany nazwą klasy, rosnącą historię zapytań połączenia oraz parametry zapytań w logach DEBUG. Każda pozycja mówi, co się dzieje i co zrobić.

S7. Dokumentacja nie obiecuje funkcji bez kodu — Zakładając dokumentację użytkownika, gdy uruchamiane są testy, wtedy import z CSV nie występuje nigdzie, a triggery występują tylko na stronie „Znane ograniczenia”.

| Wystąpienie | Wynik testu |
| --- | --- |
| triggery na stronie „Znane ograniczenia” | zielony |
| triggery na liście funkcji albo w przykładzie | czerwony |
| import z CSV gdziekolwiek | czerwony |

S8. Konfiguracja bez dodatkowych pakietów — Zakładając zmienne `NODE4J_URI`, `NODE4J_USER` i `NODE4J_PASSWORD` w środowisku albo w pliku `.env`, gdy czytelnik uruchamia szybki start, wtedy połączenie działa bez dodatkowych pakietów i bez ręcznego wczytywania `.env`. Dokumentacja nie wspomina `load_dotenv` ani `python-dotenv`, a przykładowe wartości są syntetyczne.

S9. Pliki APOC leżą na serwerze — Zakładając czytelnika, który importuje albo eksportuje JSON przez APOC, gdy czyta stronę rozszerzeń, wtedy dowiaduje się, że plik czyta i zapisuje serwer Neo4j, że `file:///nazwa.json` oznacza katalog import serwera i że import oraz eksport plików trzeba włączyć (z podanymi ustawieniami dla Dockera). Przykład eksportu i importu wykonuje się w teście (S2). Dokumentacja nie twierdzi, że potrzebna jest ścieżka absolutna.

S10. GDS testowane — Zakładając bazę testową z pluginem GDS, gdy uruchamiane są testy, wtedy przykłady GDS (projekcja, algorytm w trybie stream i mutate, usunięcie projekcji) wykonują się jak inne. Dokumentacja podaje testowane pary wersji: Neo4j 5.26 ↔ GDS 2.13 i Neo4j 2026.09 ↔ GDS 2026.09. Opis uruchamiania algorytmu ostrzega, że nazwa algorytmu musi być stałą z kodu, a nie wartością od użytkownika, bo trafia do tekstu zapytania (Z02).

S11. Przykłady nie niszczą cudzych danych — Zakładając dokumentację użytkownika, gdy uruchamiane są testy, wtedy żaden przykład nie czyści całej bazy, a po każdej stronie, także po błędzie, baza testowa wraca do stanu sprzed strony: węzły, indeksy, ograniczenia i projekcje GDS. Zadanie okresowego czyszczenia TTL jest anulowane.

| Sytuacja | Wynik |
| --- | --- |
| przykład zawiera usunięcie wszystkich węzłów | test czerwony |
| strona przeszła | baza jak przed stroną |
| blok strony rzucił błąd w połowie | baza jak przed stroną, test czerwony |
| strona uruchomiła zadanie TTL | zadanie anulowane po stronie |
| węzeł istniał przed stroną | nienaruszony |

S12. Bez bazy testowej — Zakładając brak bazy testowej, gdy uruchamiane są testy, wtedy testy wykonywania przykładów (S2, S3, S5, S9, S10, S11) są pominięte jak inne testy integracyjne, a przy wymaganej bazie testowej (tryb CI) brak bazy jest błędem. Testy struktury (S1, S4, S7) biegną zawsze.

## Doświadczenie

- **Kto i jakie zadanie.** Programista Pythona (async, podstawy Neo4j) chce dodać bibliotekę do swojej aplikacji. Najkrótsza droga: README → instalacja → szybki start, który działa po skopiowaniu → strona tematyczna przy konkretnej potrzebie.
- **Środowisko.** Markdown czytany na GitHubie (podgląd repozytorium), w obu językach. Każda strona ma u góry przełącznik języka (link do odpowiednika) i link powrotny do README.
- **Stany.**
  - „Pusty”, czyli pierwsze uruchomienie: szybki start zaczyna od wymagań i konfiguracji połączenia.
  - „Błąd”: najczęstsze błędy (brak połączenia, wyłączony import plików APOC, brak pluginu) są opisane z komunikatem, przyczyną i krokiem do wykonania.
  - „Sukces”: każdy przykład pokazuje, co powinien zobaczyć czytelnik.
- **Treści.** Proza po angielsku (wiodąca) i po polsku. Kod, nazwy i komentarze w kodzie po angielsku w obu wersjach. Dane w przykładach są syntetyczne (`example.com`, wymyślone nazwy). Treść zatwierdza człowiek w odbiorze.
- **Dostępność.** Nagłówki tworzą poprawną hierarchię (jeden tytuł na stronę, bez przeskoków poziomów). Linki mają opisowy tekst, nie „tutaj”.

## Zakres

- Nowe README w obu językach i strony tematyczne w obu językach. Propozycja podziału do potwierdzenia przy pokrojeniu: wprowadzenie i szybki start, modele i schemat, zapytania i filtry, relacje i prefetch, operacje masowe i agregacje, transakcje, mixiny (TTL, miękkie usunięcie), konfiguracja i logowanie, rozszerzenia APOC, rozszerzenia GDS, znane ograniczenia.
- Wykaz pokrycia (S5):
  - menedżer `.q`: CRUD, `get_or_create`, `update_or_create`, `count`, `aggregate`, operacje masowe, `apply_schema`, `update_relationship`;
  - relacje (`connect`, `disconnect`, lazy load), filtr Q, prefetch, haki cyklu życia, transakcja atomowa (`transaction()` i `atomic()`);
  - mixiny TTL i miękkiego usunięcia, konfiguracja `NODE4J_*`;
  - APOC: `version`, `Periodic`, `Export`, `create_from_json`;
  - GDS: projekcja, `run`, `mutate`, usunięcie projekcji.
- Test dokumentacji: wykonywanie bloków, znacznik pominięcia, zgodność EN ↔ PL, pokrycie, linki, zakazane treści.
- Baza testowa w CI i w instrukcji projektu: APOC z włączonym importem i eksportem plików oraz plugin GDS.
- Zamknięcie rozjazdów dotyczących README w rejestrze źródeł.

## Poza zakresem

- Generowana strona dokumentacji (MkDocs, hosting) — odłożone w próbach, wraca po publikacji pakietu.
- Strona dla kontrybutorów — ta wiedza zostaje w instrukcji projektu dla agentów.
- Publikacja pakietu w indeksie i zmiana instrukcji instalacji na indeks — krok wydania.
- Import z CSV (`import-csv-apoc` w Mgle) i naprawa triggerów APOC (`proby.md`) — dokumentacja tylko opisuje ich stan.
- Zmiany zachowania biblioteki. Jeśli przykład ujawni błąd w kodzie, idzie on do skilla `napraw`, a nie do tej zdolności.
- Rozjazd wersji w tagu `v0.2.3` i w metadanych pakietu — wydanie.
- Automatyczne sprawdzanie równoważności prozy EN ↔ PL — robi to przegląd człowieka.
- Dokumentacja API generowana z docstringów.

## Decyzje projektowe

- **Forma:** README plus strony Markdown w osobnym katalogu dokumentacji, w dwóch lustrzanych drzewach językowych. Bez nowych zależności runtime ani generatora.
- **Wersja wiodąca:** angielska. Polska jest tłumaczeniem prozy z identycznym kodem. Wykonywane są tylko bloki angielskie, polskie są z nimi porównywane (S4).
- **Test dokumentacji** to zwykły test pytest w zestawie testów projektu:
  - wyciąga bloki Pythona z Markdown i wykonuje je jako asynchroniczny kod najwyższego poziomu, stronę po stronie;
  - znacznik pominięcia to komentarz Markdown tuż przed blokiem, z powodem; jest niewidoczny na GitHubie;
  - połączenie z bazą testową idzie przez te same zmienne `NODE4J_*`, które opisuje dokumentacja;
  - działa na tej samej bazie testowej co reszta testów i według tej samej reguły pomijania (S12).
- **Sprzątanie:** po różnicy stanu (węzły, indeksy, ograniczenia, projekcje GDS) z anulowaniem zadania TTL, zgodnie z wyjątkiem wpisanym w Z05.
- **Baza testowa:** APOC z `NEO4J_apoc_import_file_enabled=true` i `NEO4J_apoc_export_file_enabled=true` oraz plugin `graph-data-science` (Community) na obu wersjach Neo4j z CI. Te same ustawienia trafiają do komendy w instrukcji projektu. Plik do importu powstaje w katalogu import serwera bez montowania wolumenu (sposób — otwarte pytanie `[prototyp]` w mapie).
- **Instalacja w dokumentacji:** z gita przez uv i pip. Po publikacji pakietu zmieni ją krok wydania.
- **Bezpieczeństwo:** opis uruchamiania algorytmów GDS i agregacji ostrzega przed przekazywaniem do nich danych użytkownika (Z02 — wyjątki wstawiane do tekstu zapytania).
- Dziennik decyzji z uzasadnieniami: mapa zdolności → Decyzje. Badania: zgodność GDS, ścieżki plików APOC, nazwa pakietu w indeksie.

## Testy

- **Poziom:** publiczny interfejs dokumentacji, czyli pliki Markdown czytane tak, jak czyta je czytelnik, oraz publiczne API biblioteki wywoływane przez przykłady na prawdziwej bazie testowej. Niczego nie mockujemy, a granica systemu (Neo4j z pluginami) to prawdziwy kontener.
- **Ślad:** każdy test akceptacyjny ma numer scenariusza w nazwie (`test_s2_…`), a test wykonujący przykłady jest parametryzowany stronami, żeby raport wskazywał stronę i blok.
- **Testy struktury** (S1, S4, S7, części S3, S5, S8 i S11 sprawdzające treść) nie potrzebują bazy.
- **Testy wykonania** (S2, S3, S5, S9, S10, S11) potrzebują bazy testowej z APOC i GDS.
- **Ręcznie** (przegląd w odbiorze, bo test nie oceni znaczenia tekstu): równoważność prozy EN ↔ PL (S4), kompletność i użyteczność opisów na stronie „Znane ograniczenia” (S6), dostępność nagłówków i linków (Doświadczenie).
- **Niezmienniki słownika:** „Dokumentacja użytkownika — wersje EN i PL mają ten sam zestaw stron, nagłówków i identyczne bloki kodu” sprawdza S4. „Każdy blok Pythona w wersji EN jest uruchamiany przez test albo ma jawny znacznik pominięcia” sprawdzają S2 i S3. Niezmiennik transakcji atomowej (brak zagnieżdżania) pokazuje przykład na stronie transakcji, a wykonuje go S2.

## Ryzyka i kwestie nieblokujące

- **Największe ryzyko:** wykonywanie bloków Markdown jak notatnika (stan między blokami, `await` na najwyższym poziomie, znaczniki pominięcia) może okazać się kruche. Warunek powrotu do osobnych skryptów jest zapisany w próbach.
- **Plik do importu:** sposób, w jaki trafia do katalogu import serwera, nie jest pewny, bo eksport całej bazy daje rekordy z zagnieżdżonymi właściwościami. Pytanie `[prototyp]` w mapie, do sprawdzenia przy budowie.
- **Instalacja GDS:** nie była jeszcze uruchomiona na tagach Neo4j z CI. Jeśli zawiedzie, wracamy do decyzji o GDS w CI.
- **Pliki w katalogu import:** pliki zapisane przez przykłady eksportu zostają w katalogu import kontenera. Kontener testowy jest jednorazowy, a przykłady używają stałych, syntetycznych nazw plików.
- **Wyjątek Z05** zakłada brak równoległych testów na tej samej bazie. Wprowadzenie równoległości wymaga powrotu do tej decyzji.
- **Lista stron** to propozycja. Ostateczny podział ustala pokrojenie, bez zmiany scenariuszy.
- **Koszt utrzymania:** dwa języki i dwie wersje Neo4j w CI wydłużają przebieg i każdą zmianę dokumentacji.
