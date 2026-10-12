---
nr: "02"
tytul: "Siatka: menedżer `.q` i filtry `Q`"
status: zrobione
blokowany-przez: []
scenariusze: [N1]
budowal: "Codex / GPT-6"
github: null
---

# 02 — Siatka: menedżer `.q` i filtry `Q`

## Co widać po zrobieniu

Na obecnym stosie istnieją zielone testy charakteryzujące N1 dla menedżera węzłów i filtrów.

## Kryteria akceptacji

- [x] N1: testy — `create`, `match_one`, `match_all` (z `order_by` rosnąco i malejąco), `update`, `delete`, `count`, `aggregate`, `get_or_create`, `update_or_create`, `bulk_create`, `bulk_update`, `apply_schema`, `connect`/`disconnect`/`update_relationship` menedżera
- [x] N1: testy — filtry `Q`: operatory `gt`, `gte`, `lt`, `lte`, `in`, `contains`, `startswith`, `endswith`, `ne`, równość, nieznany sufiks (dziś: równość), `&`, `|`, `~`
- [x] N1: test — zapytanie przez model rodzica znajduje węzły podklasy (ADR 0002)
- [x] testy noszą numer niezmiennika w nazwie i są zielone na bazie testowej
- [x] walidacja (ruff) bez błędów spoza punktu odniesienia

## Poza zakresem

- Relacje, haki, transakcje, mixiny — ticket 03.

## Notatki

Testy używają własnych, unikalnie nazwanych modeli albo przykładowych modeli biblioteki i sprzątają tylko swoje węzły.
