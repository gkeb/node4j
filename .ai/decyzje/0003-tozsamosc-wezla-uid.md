# 0003. Tożsamość węzła przez `uid` nadawany po stronie klienta

- Data: 2026-10-11
- Status: zastana
- Źródło: `node4j/nodes.py` → `Node.uid`, `Node._internal_id`; `node4j/manager.py` → `connect`, `_perform_update`, `bulk_update`
- Zdolność: ogólna

## Kontekst

`elementId` z Neo4j nie jest gwarantowanie stały między transakcjami, a użytkownik potrzebuje stabilnego identyfikatora do relacji i aktualizacji.

## Decyzja

Każdy węzeł ma `uid` (UUID4) nadany przez bibliotekę przy tworzeniu instancji i zapisany jako właściwość. `elementId` (`_internal_id`) służy tylko do operacji na świeżo odczytanych węzłach w tej samej pracy.

## Rozważane alternatywy

<!-- Brak źródła. (wniosek) Sam `elementId` — prostsze, ale niestabilne; klucz naturalny z `Meta` — zależny od modelu. -->

## Konsekwencje

- Relacje tworzone przez menedżera i `RelationshipManager` łączą węzły po `uid` (bez etykiet w MATCH).
- `uid` zapisuje się jako tekst (`model_dump(mode="json")`).
- Brak automatycznego indeksu ani ograniczenia unikalności na `uid` — (wniosek) wyszukiwanie po `uid` bez etykiety przegląda wszystkie węzły.
