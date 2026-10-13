---
nr: "06"
tytul: Pliki APOC w bazie testowej i strona rozszerzeń APOC
status: do-zrobienia
blokowany-przez: ["01"]
scenariusze: ["S9", "S2", "S4", "S5"]
budowal: null
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

- [ ] S9: test akceptacyjny przechodzi
- [ ] S2: przykłady strony wykonują się na bazie testowej
- [ ] S4: strona ma odpowiednik PL z identycznym kodem
- [ ] S5 (część): `version`, `Periodic`, `Export` i `create_from_json` są w wykonywanych blokach
- [ ] Pytanie `[prototyp]` z mapy, czyli jak plik do importu trafia do katalogu import, rozstrzygnięte i zapisane w mapie (Decyzje albo `proby.md`)
- [ ] CI zielone na obu wersjach Neo4j
- [ ] Walidacja zielona

## Poza zakresem

- Triggery (strona ograniczeń w 08) i import z CSV.
- Montowanie wolumenu z plikami.

## Notatki

- Najwięcej niewiadomych: zacznij od sprawdzenia na bazie testowej, czy wynik `Export.to_json` daje się wczytać przez `create_from_json` (zagnieżdżona mapa `properties`, eksport całej bazy).
- Badanie: [ścieżki plików APOC](../../../badania/2026-10-13-apoc-load-json-sciezki.md).
- Akceptacja wyglądu: RRRR-MM-DD — użytkownik — strona EN i PL — uwagi
