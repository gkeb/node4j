---
nr: "02"
tytul: Strony o modelach i schemacie oraz o zapytaniach i filtrach Q
status: do-zrobienia
blokowany-przez: ["01"]
scenariusze: ["S2", "S4", "S5"]
budowal: null
github: null
---

# 02 — Strony o modelach i schemacie oraz o zapytaniach i filtrach Q

## Co widać po zrobieniu

- Strona „Modele i schemat” (EN i PL) opisuje:
  - definicję węzła i pola `uid`;
  - etykiety z hierarchii klas i zapytania przez model rodzica;
  - `Meta` (indeksy, ograniczenia) i `apply_schema`;
  - haki cyklu życia.
- Strona „Zapytania i filtry” (EN i PL) opisuje:
  - `create`, `match_one`, `match_all`, `update`, `delete`;
  - `get_or_create`, `update_or_create`, `count`;
  - filtr Q z operatorami, łączeniem `&`, `|`, `~` i sortowaniem.
- README linkuje obie strony, a ich przykłady wykonują się w teście.

## Kryteria akceptacji

- [ ] S2: przykłady obu stron wykonują się na bazie testowej
- [ ] S4: obie strony mają odpowiedniki PL z identycznym kodem
- [ ] S5 (część): pozycje wykazu z tych stron są w wykonywanych blokach
- [ ] Każdy operator filtra opisany na stronie jest zgodny z kodem filtra Q; nieznany sufiks jest wymieniony jako pułapka (odsyłacz do „Znanych ograniczeń” dodaje 08)
- [ ] Walidacja zielona

## Poza zakresem

- Relacje i prefetch (03), operacje masowe i agregacje (04).

## Notatki

- S5 kończy ticket 08.
- Akceptacja wyglądu: RRRR-MM-DD — użytkownik — obie strony EN i PL w podglądzie GitHuba — uwagi
