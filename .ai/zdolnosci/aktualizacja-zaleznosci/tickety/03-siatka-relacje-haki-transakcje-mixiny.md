---
nr: "03"
tytul: "Siatka: relacje, haki, transakcje, mixiny, rozszerzenia"
status: zrobione
blokowany-przez: []
scenariusze: [N1]
budowal: "Codex / GPT-6"
github: null
---

# 03 — Siatka: relacje, haki, transakcje, mixiny, rozszerzenia

## Co widać po zrobieniu

Na obecnym stosie istnieją zielone testy charakteryzujące pozostałą część N1. Siatka N1 jest kompletna.

## Kryteria akceptacji

- [x] N1: testy — relacje: lazy load (z cache), prefetch i prefetch zagnieżdżony, `connect`/`disconnect` na instancji, kierunki `IN`/`OUT`/`UNDIRECTED`, model relacji (Edge)
- [x] N1: testy — haki `pre_save`, `post_save`, `pre_delete`, `post_delete` wywoływane przez `create`, `update`, `delete`, `bulk_create`, `bulk_update`
- [x] N1: testy — transakcja atomowa: zatwierdzenie, wycofanie po wyjątku, zakaz zagnieżdżania
- [x] N1: testy — miękkie usunięcie: `.q` ukrywa, `.all_objects` widzi, `soft_delete`, `restore`
- [x] N1: testy — opakowania APOC (`version`, `Periodic.iterate`, triggery, `create_from_json` z pliku dostępnego dla serwera albo pominięte z powodem w Notatkach); GDS: import i budowa zapytania bez wtyczki
- [x] testy noszą numer niezmiennika w nazwie i są zielone na bazie testowej
- [x] walidacja (ruff) bez błędów spoza punktu odniesienia

## Poza zakresem

- Zgodność z wersjami wtyczki GDS (poza zakresem specu).

## Notatki

TTL ma już testy (`fix: TTL usuwa wygasłe węzły`) — tu nie powtarzamy.

`create_from_json` pominięto: wymaga pliku dostępnego z serwera Neo4j oraz włączonego importu plików APOC, których jednorazowy kontener testowy nie konfiguruje ([APOC load.json](https://neo4j.com/docs/apoc/current/overview/apoc.load/apoc.load.json/), [instalacja APOC](https://neo4j.com/docs/apoc/current/installation/)).

Wrappery triggerów są charakteryzowane przez mock granicy `connection.run`; test sprawdza parametry wywołania, ale nie utrwala wartości domyślnej bazy `neo4j` zapisanej obecnie w query wrappera. Integracyjna próba `install` na Dockerze nie powiodła się, ponieważ obecne połączenie kieruje sesję do bazy domyślnej, a administracja triggerami APOC wymaga bazy `system` ([APOC Triggers](https://neo4j.com/docs/apoc/current/background-operations/triggers/)). Routing wymaga osobnej naprawy poza testowym zakresem tego ticketu.
