# Roadmapa

> Jedyne źródło statusu zdolności. Kolejność i priorytety ustala człowiek — przegląd raz w tygodniu: `skill gdzie tydzien`.
> Statusy: `pomysl → grill → spec → plan → budowa → weryfikacja → gotowe | porzucone`
> Teraz: najwyżej 1 w `budowa` / `weryfikacja` + najwyżej 1 w `grill` / `spec` / `plan`.

## Cel

<!-- 3–5 zdań: po co jest produkt, dla kogo, czego celowo nie robi. Ustala skill `pomysl produkt`; zmiana tylko za zgodą. -->

## Teraz

- [`readme-aktualne`](zdolnosci/readme-aktualne/mapa.md) — README EN i PL zgodne z kodem po aktualizacji (w tym rozjazdy z `zrodla.md`) — `plan`

## Dalej

## Mgła

<!-- Duże albo niejasne. Pod każdą linią 1–3 decyzje do rozstrzygnięcia (nie zadania). -->

- `natywne-daty` — daty i `ttl` zapisywane w Neo4j jako typy temporalne zamiast tekstu ISO (filtry `Q` po datach, indeksy) — `pomysl`
  - migracja istniejących danych: automatyczna, skrypt czy odczyt obu formatów?
  - czy `uid` też zmienia typ?

- `import-csv-apoc` — import węzłów i relacji z CSV przez APOC (`connect_from_csv` z README) — `pomysl`
  - czy rozszerzać `ApocManager`? (obietnica znika z dokumentacji — `readme-aktualne`, 2026-10-12)
  - klucz dopasowania węzłów: `uid` czy dowolna właściwość?

- `porzadek-lint` — wyzerowanie znanych błędów ruff z punktu odniesienia (113 po `aktualizacja-zaleznosci`, 2026-10-12: głównie długie linie, białe znaki, importy, f-stringi; dwa F821 w adnotacjach `nodes.py` i `query.py`) i usunięcie `odniesienie.znane` z `warsztat.json` — po `aktualizacja-zaleznosci`, żeby nie mieszać diffów — `pomysl`
  - jeden commit `ruff --fix` + ręczne poprawki, czy plik po pliku?
  - czy przy okazji formatować `ruff format` (zmienia prawie każdy plik)?

- [`wydanie-pypi`](zdolnosci/wydanie-pypi/mapa.md) — powtarzalne wydanie całej biblioteki jako pakietu `node4j` w PyPI (uv/pip): wersja = tag, changelog, `uv build`, TestPyPI → PyPI przez Trusted Publishing, `yank` jako wycofanie — `pomysl`
  - czy `node4j/models.py` (przykładowe modele z globalną rejestracją) zostaje w paczce?
  - backend budowania i wersja startowa (rozjazd `0.2.2` w `pyproject.toml` vs tag `v0.2.3`)
  - publikacja z CI przez Trusted Publishing — do zbadania przed specem


## Zrobione

- [`aktualizacja-zaleznosci`](zdolnosci/aktualizacja-zaleznosci/mapa.md) — aktualne biblioteki i serwer Neo4j, zachowanie bez zmian — gotowe 2026-10 — weryfikacja R3, odbiór 2026-10-12

## Porzucone
