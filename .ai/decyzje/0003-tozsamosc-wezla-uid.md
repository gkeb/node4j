# 0003. Tożsamość węzła przez `uid`

- Data: 2026-10-14
- Status: przyjęta
- Źródło: `node4j/nodes.py` → `Node.uid`, `Node._internal_id`; `node4j/manager.py` → `connect`, `_perform_update`, `bulk_update`; `node4j/ext/apoc.py` → `ApocManager.create_from_json`
- Zdolność: ogólna

## Kontekst

`elementId` z Neo4j nie jest gwarantowanie stały między transakcjami, a użytkownik potrzebuje stabilnego identyfikatora do relacji i aktualizacji.

## Decyzja

Węzły tworzone z instancji modelu mają `uid` (UUID4) nadany przez bibliotekę przy tworzeniu instancji i zapisany jako właściwość. `elementId` (`_internal_id`) służy tylko do operacji na świeżo odczytanych węzłach w tej samej pracy.

Wyjątek: `ApocManager.create_from_json` tworzy surowe węzły wewnątrz Neo4j, więc nadaje im `uid` w Cypherze przez wbudowane `randomUUID()`. Zakres wyjątku ogranicza się do tego importera. Wybrano to rozwiązanie, by zachować serwerowy import JSON; przeniesienie generowania UUID do Pythona wymagałoby zmiany przepływu danych. `apoc.create.uuid()` nie jest dostępne w Neo4j 2026.09; `randomUUID()` działa w Neo4j 2026.09 i 5.26 ([raport testu](../eksperymenty/2026-10-14-apoc-export-import.md), [dokumentacja Cypher](https://neo4j.com/docs/cypher-manual/current/functions/uuid/)).

## Rozważane alternatywy

- `elementId` — prostszy, ale nie jest gwarantowanie stabilny między transakcjami.
- Klucz naturalny z `Meta` — zależy od modelu i nie jest dostępny dla każdego modelu.
- UUID generowany w Pythonie dla importera APOC — spójny z pozostałymi ścieżkami tworzenia, ale wymagałby przeniesienia odczytu lub przetwarzania wierszy JSON do klienta.
- UUID generowany w Cypherze przez `randomUUID()` — zachowuje serwerowy import JSON, ale stanowi ograniczony wyjątek od generowania UID po stronie klienta; wybrany dla `create_from_json`.

## Konsekwencje

- Relacje tworzone przez menedżera i `RelationshipManager` łączą węzły po `uid` (bez etykiet w MATCH).
- `uid` zapisuje się jako tekst (`model_dump(mode="json")`).
- `create_from_json` nadpisuje importowane `uid` losowym UUID generowanym po stronie Neo4j; ten wyjątek nie zmienia pozostałych ścieżek tworzenia węzłów.
- Brak automatycznego indeksu ani ograniczenia unikalności na `uid` — (wniosek) wyszukiwanie po `uid` bez etykiety przegląda wszystkie węzły.
