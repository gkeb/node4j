# Eksperyment: APOC eksportuje plik do importu na serwerze

- Status: rozstrzygniety
- Pytanie: czy wynik `apoc.Export.to_json` można wczytać przez `create_from_json`, i jak plik trafia do katalogu import serwera bez montowania wolumenu? [Pytanie w mapie](../zdolnosci/readme-aktualne/mapa.md)
- Prowadzący: Codex / GPT-6
- Plan zaakceptowany: 2026-10-14 — użytkownik — jednorazowy Neo4j 2026.09 z APOC, syntetyczne dane, najwyżej dwa warianty, limit 20 minut.

## Plan

- Cel i istotna poprawa: potwierdzić zapis pliku po stronie serwera, kształt eksportu JSON i import właściwości przez `create_from_json`.
- Zakres zmian: tymczasowe dane w jednorazowym kontenerze `neo4j:2026.09.0`; flagi importu i eksportu APOC. Poza zakresem: montowanie wolumenu, kod produkcyjny, dane użytkownika i zmiana zachowania biblioteki.
- Poprawność: plik zapisany przez serwer jest widoczny dla `apoc.load.json`; importer tworzy syntetyczny węzeł z oczekiwanymi właściwościami; testowe dane są usunięte po próbie.
- Warunki i ocena: Windows, Docker, Neo4j `2026.09.0`, APOC Core, aplikacja z repozytorium, unikalny syntetyczny identyfikator; wynik oceniany zapytaniami do tej samej bazy.
- Przypadki porównawcze / końcowe: najpierw eksport `apoc.Export.to_json`; jeśli domyślny import nie spełni poprawności, jedna alternatywa dobrana po kształcie JSON: ścieżka `json_path` albo eksport zapytania do pliku.
- Budżet i stop: najwyżej dwa warianty, maksymalnie 20 minut; stop po poprawnym imporcie albo wyczerpaniu limitu.
- Artefakty robocze: wyłącznie baza i plik w kontenerze jednorazowym; bez plików roboczych w repo.

## Punkt odniesienia

Nie wykonano przed uruchomieniem prototypu. W kodzie `Export.to_json` wywołuje `apoc.export.json.all`, a `create_from_json` przekazuje wiersz z JSON do `SET n = row`; formaty nie są potwierdzone jako zgodne.

## Iteracje

| Nr | Wariant / hipoteza | Wynik i poprawność | Decyzja i dowód |
| --- | --- | --- | --- |
| 1 | `APOC.Export.to_json` zapisuje bazę, a `create_from_json(url)` wczyta jej plik | Eksport powstał po stronie serwera; `apoc.load.json` odczytał rekord o kluczach `id`, `labels`, `properties`, `type`. Import zgłosił `ParameterNotFoundException: Expected parameter(s): url, path`; liczba syntetycznych węzłów pozostała 1. | Plik z eksportu jest dostępny dla APOC po stronie serwera, ale import przez wrapper nie działa. Jednorazowy kontener Neo4j 2026.09.0 z APOC; [kod `create_from_json`](../../node4j/ext/apoc.py) |
| 2 | Podanie `json_path="$.nodes[*].properties"` ominie problem z kształtem eksportu | Ten sam `ParameterNotFoundException` dla `url` i `path`; importer nie dotarł do odczytu JSON ani do etapu tworzenia węzłów. | `json_path` nie omija błędu przekazywania parametrów. Nie wykonuję trzeciego wariantu; naprawa wrappera jest poza zakresem eksperymentu i ticketu 06. |

## Ocena końcowa

Eksport serwerowy potwierdza sposób umieszczenia pliku: `apoc.export.json.all` zapisuje go w katalogu import Neo4j, a `apoc.load.json` potrafi odczytać wygenerowany plik. Pełny eksport grafu zawiera metadane i zagnieżdżone `properties`, więc do importera map właściwości potrzebny jest selektywny eksport JSON Lines. Po poprawce przekazywania parametrów próbę blokowała jeszcze niedostępna funkcja `apoc.create.uuid`; poprawka UUID i testy obu wersji są opisane niżej. Kontenery testowe zatrzymano; użyto danych syntetycznych i nie montowano wolumenu.

## Walidacja po poprawce parametrów

Test bloku strony APOC w ticketcie 06, po commicie naprawczym `3f60d50`, utworzył plik przez `apoc.export.json.query`; `apoc.load.json` oraz `json_path="$.row"` odczytały oczekiwaną mapę właściwości. Wywołanie `create_from_json` przekazało parametr `url` i `path`, ale APOC zwrócił `failedOperations=1` i `Unknown function 'apoc.create.uuid'` w zapytaniu wykonującym. Import nadal wymaga osobnej naprawy.

## Walidacja po poprawce UUID

Test regresji najpierw potwierdził stary wynik: generator wysyłał do APOC `apoc.create.uuid()`, a Neo4j 2026.09 zwracał `Unknown function`. Zastąpiono go wbudowaną funkcją Cypher `randomUUID()`. Test przykładu strony APOC przeszedł na jednorazowych kontenerach Neo4j 2026.09.0 i 5.26; oba kontenery zatrzymano. `randomUUID()` zwraca tekst UUID zgodny z właściwością `uid` zapisywaną przez importer.

## Wniosek

Eksport pełnej bazy nie jest bezpośrednim wejściem dla `create_from_json`, bo ma inny kształt danych; selektywny eksport JSON Lines z mapami właściwości działa. Importer przekazuje parametry źródła do `apoc.periodic.iterate`; `randomUUID()` działa na Neo4j 2026.09 i 5.26. Użytkownik wybrał jawny, ograniczony wyjątek w ADR 0003: surowe węzły tego importera dostają UID po stronie Neo4j, a pozostałe ścieżki zachowują generowanie po stronie klienta.

<!-- Statusy: planowany | w-toku | rozstrzygniety | nierozstrzygniety | przerwany. Kod prototypu nie trafia do tego pliku. -->
