---
poznany-commit: bbd4308046ffa202b058da65efa43fe091e9c3ac
zrodla-kodu: ["node4j/properties.py", "node4j/edges.py", "node4j/nodes.py", "node4j/manager.py", "node4j/registry.py", "tests/test_n1_relations_hooks_mixins_ext.py"]
---

# Obszar: relacje

- Katalogi: `node4j/`, `tests/`
- Poznany: 2026-10-13

## Za co odpowiada

Deklarowanie relacji na modelach węzłów, ich ładowanie i modyfikowanie oraz pobieranie zagnieżdżonych relacji w tym samym zapytaniu co węzły.

## Moduły i przepływy

- [`NodeBase`](../../node4j/nodes.py) zbiera atrybuty [`RelationshipProperty`](../../node4j/properties.py), ustawia je jako deskryptory i zapisuje w `_relationships` modelu. Przy tworzeniu klasy model jest rejestrowany pod nazwą klasy; cel relacji rozwiązuje się z tego rejestru przy odczycie ([`registry.py`](../../node4j/registry.py), [ADR 0002](../decyzje/0002-etykiety-z-hierarchii-klas.md)).
- Deskryptor zwraca [`RelationshipManager`](../../node4j/properties.py). `await node.relation` pobiera listę `(węzeł_docelowy, właściwości_relacji)` i zapisuje ją w atrybucie prywatnym tej instancji; kolejne odczyty używają cache. `connect` przyjmuje słownik, model [`Edge`](../../node4j/edges.py) albo brak właściwości; `disconnect` usuwa połączenie. Obie metody czyszczą lokalny cache tej relacji.
- Kierunek relacji jest opisany przez `RelationshipDirection.IN`, `OUT` albo `UNDIRECTED`; wpływa na wzorzec Cyphera dla odczytu i prefetchu oraz na kolejność końców przy `connect` i `disconnect` ([`RelationshipProperty.relationship_pattern`](../../node4j/properties.py), [`RelationshipManager.connect`](../../node4j/properties.py)). `model=EdgeSubclass` waliduje właściwości relacji przy lazy load i prefetchu.
- [`NodeManager.match_one`](../../node4j/manager.py) i `match_all` przekazują konfigurację do [`ReturnQueryBuilder`](../../node4j/manager.py). Lista nazw prefetchuje wskazane relacje, a słownik pozwala konfigurować kolejne poziomy. Hydratacja zapisuje projekcje do tego samego atrybutu prywatnego co lazy load, więc `await node.relation` używa danych z prefetchu ([`_hydrate_prefetched`](../../node4j/manager.py), testy `test_N1_relationship_prefetches_nested_relations` i `test_N1_match_all_prefetch_loads_relations_without_lazy_query`).
- [`NodeManager.update_relationship`](../../node4j/manager.py) scala przekazany słownik właściwości we wszystkich relacjach pasujących do dwóch UID-ów końców i typu relacji (`SET r += $props`). Jest to operacja managera, osobna od deskryptora relacji.

## Testy

- [`tests/test_n1_relations_hooks_mixins_ext.py`](../../tests/test_n1_relations_hooks_mixins_ext.py) obejmuje lazy load i cache, invalidację po `connect`/`disconnect`, kierunki, walidację `Edge`, prefetch zagnieżdżony oraz odczyt prefetched bez dodatkowego lazy query.
- Uruchomienie wymaga bazy testowej: `uv run pytest tests/test_n1_relations_hooks_mixins_ext.py` (konfiguracja w `tests/conftest.py`).

## Decyzje

- [ADR 0002 — etykiety z hierarchii klas, rejestr po nazwie klasy](../decyzje/0002-etykiety-z-hierarchii-klas.md) ustala sposób rejestracji i rozwiązywania celu relacji.
- Nazwy `Relacja`, `Model relacji (Edge)` i `Prefetch` są opisane w [słowniku](../SLOWNIK.md).

## Pułapki

- Cel relacji jest nazwą klasy w globalnym rejestrze, nie ścieżką importu. Dwie klasy o tej samej nazwie nadpisują się w rejestrze ([ADR 0002](../decyzje/0002-etykiety-z-hierarchii-klas.md)).
- Cache jest lokalny dla instancji. `connect` i `disconnect` go czyszczą; `update_relationship` operuje bezpośrednio na bazie i nie odświeża istniejących instancji (wniosek z [`NodeManager.update_relationship`](../../node4j/manager.py) i [`RelationshipManager._fetch`](../../node4j/properties.py)).
- Sygnatury `match_one` i `match_all` deklarują `prefetch` jako `list[str]`, choć [`ReturnQueryBuilder`](../../node4j/manager.py) obsługuje też zagnieżdżony słownik, pokryty testem.

## Źródła

- Kod: [`node4j/properties.py`](../../node4j/properties.py), [`node4j/edges.py`](../../node4j/edges.py), [`node4j/nodes.py`](../../node4j/nodes.py), [`node4j/manager.py`](../../node4j/manager.py), [`node4j/registry.py`](../../node4j/registry.py).
- Testy relacji: [`tests/test_n1_relations_hooks_mixins_ext.py`](../../tests/test_n1_relations_hooks_mixins_ext.py).
- Decyzja o rejestrze: [ADR 0002](../decyzje/0002-etykiety-z-hierarchii-klas.md).
