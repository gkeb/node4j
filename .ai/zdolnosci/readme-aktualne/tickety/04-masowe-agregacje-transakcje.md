---
nr: "04"
tytul: Strony o operacjach masowych i agregacjach oraz o transakcjach
status: do-zrobienia
blokowany-przez: ["01"]
scenariusze: ["S2", "S4", "S5"]
budowal: null
github: null
---

# 04 — Strony o operacjach masowych i agregacjach oraz o transakcjach

## Co widać po zrobieniu

- Strona „Operacje masowe i agregacje” (EN i PL) opisuje:
  - `bulk_create` i `bulk_update` (z `match_on`), z hakami cyklu życia;
  - `aggregate` z ostrzeżeniem, że wyrażenia agregacji trafiają do tekstu zapytania, więc nie mogą pochodzić od użytkownika (Z02).
- Strona „Transakcje” (EN i PL) opisuje:
  - `connection.transaction()` i `@connection.atomic()`;
  - przykład wycofania po błędzie;
  - brak zagnieżdżania (`RuntimeError`).
- README linkuje obie strony.

## Kryteria akceptacji

- [ ] S2: przykłady obu stron wykonują się na bazie testowej, także przykład wycofania i zagnieżdżenia, z oczekiwanym wyjątkiem pokazanym w kodzie
- [ ] S4: obie strony mają odpowiedniki PL z identycznym kodem
- [ ] S5 (część): `bulk_create`, `bulk_update`, `aggregate`, `transaction()` i `atomic()` są w wykonywanych blokach
- [ ] Walidacja zielona

## Poza zakresem

- Zmiana zachowania `aggregate`. Ewentualna poprawka idzie przez skill `napraw`.

## Notatki

- S5 kończy ticket 08.
- Niezmiennik słownika „transakcje się nie zagnieżdżają” jest pokazany przykładem, który wykonuje S2.
- Akceptacja wyglądu: RRRR-MM-DD — użytkownik — obie strony EN i PL — uwagi
