---
nr: "08"
tytul: Znane ograniczenia, pełne pokrycie i zamknięcie rozjazdów
status: zrobione
blokowany-przez: ["02", "03", "04", "05", "06", "07"]
scenariusze: ["S6", "S5", "S7"]
budowal: Codex / GPT-6
github: null
---

# 08 — Znane ograniczenia, pełne pokrycie i zamknięcie rozjazdów

## Co widać po zrobieniu

- Strona „Znane ograniczenia” (EN i PL) opisuje:
  - triggery APOC (nie działają z domyślnej bazy);
  - daty i `uid` zapisywane jako tekst;
  - nieznany sufiks filtra traktowany jako równość;
  - rejestr modeli kluczowany nazwą klasy;
  - rosnącą historię zapytań połączenia;
  - parametry zapytań w logach DEBUG.

  Każda pozycja mówi, co się dzieje i co zrobić. Inne strony linkują ją tam, gdzie wspominają pułapkę.
- Test pokrycia ma pełny wykaz metod ze specu.
- Rozjazdy dotyczące README w `zrodla.md` są odhaczone z odsyłaczem do tej zdolności, a wpis o dokumentach jest zaktualizowany.

## Kryteria akceptacji

- [x] S6: strona ograniczeń zawiera wszystkie pozycje ze specu (test treści) i przechodzi przegląd w odbiorze
- [x] S5: test akceptacyjny przechodzi z pełnym wykazem
- [x] S7: test przechodzi także ze stroną ograniczeń, bo triggery są tylko tam
- [x] Rozjazdy README w `zrodla.md` zamknięte. Tag `v0.2.3` i wersja w metadanych zostają otwarte, bo są poza zakresem
- [x] Walidacja zielona

## Poza zakresem

- Naprawa triggerów i import z CSV.

## Notatki

- Ticket kończy S5 i S6.
- Akceptacja wyglądu: 2026-10-15 — użytkownik — strona ograniczeń EN i PL plus przejście całej dokumentacji od README — zaakceptowano
- Walidacja lokalna: pytest 42 passed, 70 skipped (testy bazy Neo4j bez dostępnej bazy); Ruff bez nowych błędów, 108 znanych.
