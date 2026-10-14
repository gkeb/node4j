---
nr: "07"
tytul: GDS w bazie testowej i strona rozszerzeń GDS
status: w-toku
blokowany-przez: ["01"]
scenariusze: ["S10", "S11", "S2", "S4", "S5"]
budowal: "Codex / GPT-6"
github: null
---

# 07 — GDS w bazie testowej i strona rozszerzeń GDS

## Co widać po zrobieniu

- Baza testowa w CI (obie wersje Neo4j) i komenda w AGENTS.md mają plugin `graph-data-science` (Community) obok APOC.
- Strona „Rozszerzenia: GDS” (EN i PL) opisuje:
  - instalację i testowane pary wersji (Neo4j 5.26 ↔ GDS 2.13, 2026.09 ↔ GDS 2026.09);
  - projekcję, `Algo.run` (tryb stream), `Algo.mutate` (z `mutateProperty`), usunięcie projekcji;
  - ostrzeżenie, że nazwa algorytmu musi być stałą z kodu (Z02);
  - co się dzieje przy usuwaniu nieistniejącej projekcji.
- Test dokumentacji usuwa projekcje GDS powstałe na stronie.

## Kryteria akceptacji

- [x] S10: test akceptacyjny przechodzi
- [x] S11: test akceptacyjny przechodzi w całości (węzły, schemat, TTL, projekcje GDS)
- [x] S2: przykłady strony wykonują się na bazie testowej
- [x] S4: strona ma odpowiednik PL z identycznym kodem
- [x] S5 (część): projekcja, `run`, `mutate` i usunięcie projekcji są w wykonywanych blokach
- [ ] CI zielone na obu wersjach Neo4j — pełny zestaw uruchomiony lokalnie: 108 passed na każdej wersji; GitHub CI czeka na push
- [x] Walidacja zielona

## Poza zakresem

- GDS Enterprise i licencje.

## Notatki

- Ticket kończy S10 i S11.
- Instalacji GDS przez `NEO4J_PLUGINS` na tagach z CI nikt jeszcze nie uruchomił. Jeśli zawiedzie, zatrzymaj się i wróć do decyzji o GDS w CI (skill `pomysl readme-aktualne`), zamiast oznaczać bloki do pominięcia.
- Badanie: [zgodność GDS](../../../badania/2026-10-13-gds-zgodnosc.md).
- Akceptacja wyglądu: 2026-10-14 — użytkownik — strona EN i PL — uwagi: brak
