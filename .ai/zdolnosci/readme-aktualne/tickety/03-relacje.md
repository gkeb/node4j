---
nr: "03"
tytul: Strona o relacjach i prefetchu
status: zrobione
blokowany-przez: ["01"]
scenariusze: ["S2", "S4", "S5"]
budowal: "Codex / GPT-6"
github: null
---

# 03 — Strona o relacjach i prefetchu

## Co widać po zrobieniu

Strona „Relacje” (EN i PL) opisuje:
- relację jako atrybut modelu, kierunki i cel wskazany nazwą klasy;
- model relacji (Edge);
- `connect` z właściwościami (słownik albo Edge), `disconnect`;
- lazy load przez `await`;
- `update_relationship`;
- prefetch, w tym zagnieżdżony, i to, że lazy load korzysta z danych z prefetchu.

README linkuje stronę.

## Kryteria akceptacji

- [x] S2: przykłady strony wykonują się na bazie testowej
- [x] S4: strona ma odpowiednik PL z identycznym kodem
- [x] S5 (część): relacje, `update_relationship` i prefetch są w wykonywanych blokach
- [x] Walidacja zielona

## Poza zakresem

- Menedżerowe `connect` i `disconnect` na `.q` — nie ma ich w wykazie pokrycia.

## Notatki

- S5 kończy ticket 08.
- Akceptacja wyglądu: 2026-10-14 — użytkownik — podgląd stron EN i PL na GitHubie — bez uwag
