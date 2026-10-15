---
nr: "11"
tytul: "Po weryfikacji R1: wzmocnienie testów dokumentacji i drobne poprawki"
status: zrobione
blokowany-przez: ["01", "06"]
scenariusze: ["S3", "S7", "S9"]
budowal: Codex / GPT-6
github: null
---

# 11 — Po weryfikacji R1: wzmocnienie testów dokumentacji i drobne poprawki

## Co widać po zrobieniu

Testy dokumentacji łapią wszystkie przypadki opisane w scenariuszach, a nie tylko ich część. Działanie importera APOC jest sprawdzone na bazie, a nie tylko na atrapie połączenia. Testy:

- czerwienieją na polskie i angielskie wzmianki o imporcie z CSV (S7) oraz na prozę o ścieżce absolutnej dla plików APOC (S9);
- sprawdzają na bazie testowej, że węzeł zaimportowany przez `create_from_json` dostaje nowy, unikalny `uid`, różny od `uid` ze źródła (Z06, ADR 0003);
- pokazują pominięty blok w raporcie pytest jako pominięty, razem z powodem, i sprawdzają to przebiegiem pytest na stronie ze znacznikiem, a nie przez funkcje pomocnicze (S3);
- wymagają linku powrotnego do README na każdej stronie EN i PL, nie tylko na stronie APOC.

Do tego:

- przykład `apoc.Periodic.iterate` na stronie APOC (EN i PL) pokazuje widoczny efekt na danych;
- metadane ticketów 05 i 06 są poprawione: `budowal` w formacie `<narzędzie> / <model>`, a `blokowany-przez` w 06 zgodne z mapą („po 01”).

## Kryteria akceptacji

- [x] S3: test akceptacyjny przechodzi; pominięty blok ma w raporcie pytest status „pominięty” z powodem
- [x] S7: tekst „import z CSV” albo „CSV import” na dowolnej stronie daje czerwony test
- [x] S9: proza o ścieżce absolutnej („absolute path”, „ścieżka absolutna”) na dowolnej stronie daje czerwony test
- [x] Test na bazie testowej: `uid` węzła zaimportowanego przez `create_from_json` jest UUID i różni się od `uid` węzła źródłowego
- [x] Brak linku do README na dowolnej stronie `docs/` daje czerwony test
- [x] S2 i S4: przykłady strony APOC nadal się wykonują, a kod w wersjach EN i PL jest identyczny
- [x] Walidacja zielona
- [x] Akceptacja wyglądu zmienionej strony APOC wpisana w Notatkach

## Poza zakresem

- Zmiana zachowania `create_from_json` i wrappera `Periodic`.

## Notatki

- R1.7: zgodnie z wyborem użytkownika przykład używa `connection.run` z unikalnym markerem w `config.params`; sprawdza zmianę wskazanego węzła i brak zmiany sąsiedniego. Wrapper `Periodic.iterate` nie przyjmuje parametrów zapytania; jego rozszerzenie jest odłożone w `.ai/proby.md`.
- Akceptacja wyglądu: użytkownik zaakceptował podglądy APOC EN/PL przy 1440 px i 960 px, 2026-10-15. Zrzuty: `.ai/zrzuty/readme-aktualne-11/ticket11-1440.png` i `.ai/zrzuty/readme-aktualne-11/ticket11-960.png`.
- Walidacja: `tests/test_documentation.py` — 45 passed na Neo4j 2026.09 z APOC i GDS; `ruff format --check`, `ruff check`, `scripts/check_ruff_baseline.py` i `git diff --check` zielone.
- Przegląd: zgodność, jakość i bezpieczeństwo sprawdzone niezależnie; po poprawkach S3/S9 brak uwag blokujących.
- Uwagi weryfikacji: R1.3, R1.4, R1.5, R1.6, R1.7, R1.8 ([weryfikacja](../weryfikacja.md)).
