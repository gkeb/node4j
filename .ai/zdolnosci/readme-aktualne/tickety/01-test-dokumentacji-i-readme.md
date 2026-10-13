---
nr: "01"
tytul: Test dokumentacji i nowe README z szybkim startem
status: do-zrobienia
blokowany-przez: []
scenariusze: ["S1", "S2", "S3", "S4", "S7", "S8", "S11", "S12"]
budowal: null
github: null
---

# 01 — Test dokumentacji i nowe README z szybkim startem

## Co widać po zrobieniu

- Nowe README w wersji angielskiej i polskiej:
  - czym jest biblioteka;
  - wymagania: Python 3.12+, Neo4j 5.26 LTS albo 2026.09, APOC i GDS tylko dla rozszerzeń;
  - instalacja z gita przez uv i pip;
  - szybki start, który działa po skopiowaniu: konfiguracja przez `NODE4J_*` albo `.env`, model, zapis, odczyt, relacja;
  - spis stron tematycznych (na razie tylko istniejące) i przełącznik języka.
- W zestawie testów projektu jest test dokumentacji, który:
  - wykonuje bloki Pythona z wersji EN stroną po stronie (wspólna przestrzeń nazw w obrębie strony), na bazie testowej;
  - obsługuje znacznik pominięcia z powodem;
  - porównuje EN z PL: strony, liczbę nagłówków, identyczne bloki kodu;
  - sprawdza linki i hierarchię nagłówków (jeden tytuł, bez przeskoków poziomów);
  - sprawdza zakazane treści: import z CSV, triggery poza stroną ograniczeń, `load_dotenv` i `python-dotenv`, czyszczenie całej bazy, ścieżka absolutna dla plików APOC;
  - sprząta po różnicy stanu (węzły, indeksy, ograniczenia), także po błędzie.
- Zepsuty przykład czerwieni testy, a z `NODE4J_REQUIRE_TEST_DB=1` brak bazy jest błędem.

## Kryteria akceptacji

- [ ] S1: test akceptacyjny przechodzi
- [ ] S2: test akceptacyjny przechodzi (mechanizm i bloki README)
- [ ] S3: test akceptacyjny przechodzi
- [ ] S4: test akceptacyjny przechodzi
- [ ] S7: test akceptacyjny przechodzi
- [ ] S8: test akceptacyjny przechodzi
- [ ] S12: test akceptacyjny przechodzi
- [ ] S11 (część): przy wykonywaniu strony węzły, indeksy i ograniczenia wracają do stanu sprzed strony, także gdy blok rzuci błąd w połowie; przykład z usunięciem wszystkich węzłów daje czerwony test
- [ ] Test wykonujący przykłady jest parametryzowany stronami, a raport wskazuje stronę i numer bloku
- [ ] Testy struktury biegną bez bazy testowej
- [ ] Dane w przykładach są syntetyczne
- [ ] Walidacja z `warsztat.json` zielona (bez nowych błędów ruff)

## Poza zakresem

- Strony tematyczne (02–07) i strona „Znane ograniczenia” (08).
- Sprzątanie zadania TTL (05) i projekcji GDS (07).
- Zmiany konfiguracji bazy testowej w CI (06, 07).

## Notatki

- Ticket kończy scenariusze S1, S2, S3, S4, S7, S8 i S12. Kolejne tickety trzymają S1, S2, S4 i S7 na zielono dla nowych stron.
- S11 kończy ticket 07.
- Sprzątanie po różnicy stanu to wyjątek w Z05; warunek: testy nie biegną równolegle.
- Stare treści README znikają w tym tickecie. Rozjazdy w `zrodla.md` odhacza ticket 08.
- Akceptacja wyglądu: RRRR-MM-DD — użytkownik — README EN i PL w podglądzie GitHuba, równoważność prozy — uwagi
