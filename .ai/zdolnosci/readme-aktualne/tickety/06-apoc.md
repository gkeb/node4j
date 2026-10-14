---
nr: "06"
tytul: Pliki APOC w bazie testowej i strona rozszerzeń APOC
status: zrobione
blokowany-przez: []
scenariusze: ["S9", "S2", "S4", "S5"]
budowal: 2026-10-14 — Codex / GPT-6
github: null
---

# 06 — Pliki APOC w bazie testowej i strona rozszerzeń APOC

## Co widać po zrobieniu

- Baza testowa w CI (obie wersje Neo4j) i komenda w AGENTS.md mają włączony import i eksport plików APOC (`NEO4J_apoc_import_file_enabled=true`, `NEO4J_apoc_export_file_enabled=true`).
- Strona „Rozszerzenia: APOC” (EN i PL) opisuje:
  - instalację pluginu i potrzebne ustawienia (z przykładem dla Dockera);
  - `apoc.version`, `Periodic.iterate`, `Export.to_json`;
  - `install_apoc_manager` i `create_from_json`;
  - zasadę „plik czyta i zapisuje serwer, `file:///nazwa.json` = katalog import”;
  - komunikat błędu przy wyłączonym imporcie i co zrobić.
- Przykład eksportu i importu wykonuje się w teście.

## Kryteria akceptacji

- [x] S9: test akceptacyjny przechodzi
- [x] S2: przykłady strony wykonują się na bazie testowej (Neo4j 2026.09 i 5.26 + APOC)
- [x] S4: strona ma odpowiednik PL z identycznym kodem
- [x] S5 (część): `version`, `Periodic`, `Export` i `create_from_json` są w wykonywanych blokach
- [x] Pytanie `[prototyp]` z mapy, czyli jak plik do importu trafia do katalogu import, rozstrzygnięte i zapisane w mapie (Decyzje albo `proby.md`)
- [x] CI zielone na obu wersjach Neo4j ([run 38632727782](https://github.com/gkeb/node4j/actions/runs/38632727782))
- [x] Walidacja zielona

## Poza zakresem

- Triggery (strona ograniczeń w 08) i import z CSV.
- Montowanie wolumenu z plikami.

## Notatki

- Najwięcej niewiadomych: zacznij od sprawdzenia na bazie testowej, czy wynik `Export.to_json` daje się wczytać przez `create_from_json` (zagnieżdżona mapa `properties`, eksport całej bazy).
- Badanie: [ścieżki plików APOC](../../../badania/2026-10-13-apoc-load-json-sciezki.md).
- Naprawy zachowania `create_from_json` wydzielone z ticketu do commitów `fix:`: `565d29a` przekazuje `url` i `path` przez `config.params`, a `cfc9df6` używa `randomUUID()` dostępnego w obu testowanych wersjach Neo4j. Wyjątek UID zaakceptowany przez użytkownika zapisano w [ADR 0003](../../../decyzje/0003-tozsamosc-wezla-uid.md). Recenzje napraw: bez uwag blokujących; uwagę bezpieczeństwa o SSRF adresuje ostrzeżenie na obu stronach. CI napraw zielone na Neo4j 2026.09 i 5.26 ([run 38631385439](https://github.com/gkeb/node4j/actions/runs/38631385439)). [Raport](../../../eksperymenty/2026-10-14-apoc-export-import.md), [próba](../../../proby.md)
- Walidacja lokalna 2026-10-14: `tests/test_documentation.py` — 23 passed, 10 skipped bez bazy; S2 strony APOC — 1 passed na Neo4j 2026.09 + APOC; lint bazowy — 108 zastanych błędów, bez nowych; `ruff check`, `ruff format --check` i `git diff --check` zielone.
- Przegląd ticketu 06: zgodność, jakość i bezpieczeństwo — brak uwag blokujących; uwagi o linkach, katalogu importu, eksporcie pełnej bazy, logowaniu URL i instalacji produkcyjnej zostały uwzględnione. Po wydzieleniu napraw nie ma zmian zachowania poza zakresem dokumentacyjnej zdolności. CI napraw jest zielone w [run 38631385439](https://github.com/gkeb/node4j/actions/runs/38631385439), a CI ticketu 06 w [run 38632727782](https://github.com/gkeb/node4j/actions/runs/38632727782).
- Akceptacja wyglądu: 2026-10-14 — użytkownik — strony EN i PL — zaakceptowane
