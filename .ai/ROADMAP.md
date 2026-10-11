# Roadmapa

> Jedyne źródło statusu zdolności. Kolejność i priorytety ustala człowiek — przegląd raz w tygodniu: `skill gdzie tydzien`.
> Statusy: `pomysl → grill → spec → plan → budowa → weryfikacja → gotowe | porzucone`
> Teraz: najwyżej 1 w `budowa` / `weryfikacja` + najwyżej 1 w `grill` / `spec` / `plan`.

## Cel

<!-- 3–5 zdań: po co jest produkt, dla kogo, czego celowo nie robi. Ustala skill `pomysl produkt`; zmiana tylko za zgodą. -->

## Teraz

- [`aktualizacja-zaleznosci`](zdolnosci/aktualizacja-zaleznosci/mapa.md) — aktualne biblioteki i serwer Neo4j, zachowanie bez zmian — `plan`

## Dalej

- `readme-aktualne` — README EN i PL zgodne z kodem po aktualizacji (w tym rozjazdy z `zrodla.md`) — `pomysl`

## Mgła

<!-- Duże albo niejasne. Pod każdą linią 1–3 decyzje do rozstrzygnięcia (nie zadania). -->

- `natywne-daty` — daty i `ttl` zapisywane w Neo4j jako typy temporalne zamiast tekstu ISO (filtry `Q` po datach, indeksy) — `pomysl`
  - migracja istniejących danych: automatyczna, skrypt czy odczyt obu formatów?
  - czy `uid` też zmienia typ?

- `import-csv-apoc` — import węzłów i relacji z CSV przez APOC (`connect_from_csv` z README) — `pomysl`
  - czy rozszerzać `ApocManager`, czy usunąć obietnicę z README?
  - klucz dopasowania węzłów: `uid` czy dowolna właściwość?


## Zrobione

## Porzucone
