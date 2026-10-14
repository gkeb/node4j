# Słownik domeny

> Byty, nie-byty, granice i niezmienniki. Najwyżej 1–3 strony. Poprawiaj istniejące wpisy zamiast dopisywać nowe wersje. Format: „Język → zachowanie → test” w `kontrakt/praca.md` w katalogu pluginu warsztatu.

<!-- Konteksty: dopóki każde słowo znaczy w całym projekcie to samo, zostaw tylko „Pojęcia”. Gdy to samo słowo zaczyna znaczyć co innego w dwóch częściach systemu, dodaj sekcje `## Kontekst: <nazwa>` (odpowiedzialność, obszary kodu, relacje z innymi kontekstami), a w „Pojęciach” zostaw tylko to, co wspólne. -->

## Pojęcia

- **Węzeł (model węzła)** — klasa Pydantic dziedzicząca po `Node`, odwzorowana na węzły Neo4j. _Zawsze:_ ma pole `uid`; instancja modelu dostaje UUID po stronie klienta, a surowy węzeł utworzony przez `ApocManager.create_from_json` dostaje go po stronie Neo4j. Źródło: `node4j/nodes.py` → `Node`; wyjątek: [ADR 0003](decyzje/0003-tozsamosc-wezla-uid.md).
- **Etykieta** — etykieta Neo4j węzła. _Zawsze:_ zbiór = nazwa klasy + etykiety wszystkich przodków (bez `Node`), posortowany; zapytanie przez model rodzica znajduje też węzły podklas. Źródło: `node4j/nodes.py` → `NodeBase.__new__`; ADR 0002.
- **Rejestr modeli** — `node_registry`: nazwa klasy → klasa modelu, wypełniany przez metaklasę. Relacje wskazują cel po nazwie i rozwiązują go w rejestrze dopiero przy zapytaniu. _Zawsze:_ klucz to nazwa klasy, nie moduł. Źródło: `node4j/registry.py`; ADR 0002.
- **Menedżer (`.q`)** — `NodeManager` przypięty do modelu; wszystkie operacje na bazie dla tego modelu (CRUD, bulk, `count`, `aggregate`, `apply_schema`). Źródło: `node4j/manager.py`.
- **Relacja** — atrybut modelu typu `RelationshipProperty`: typ relacji, etykieta celu, kierunek (`IN`, `OUT`, `UNDIRECTED`), opcjonalny model relacji. Na instancji zwraca `RelationshipManager` (`await` = lazy load, `connect`, `disconnect`). Źródło: `node4j/properties.py`.
- **Model relacji (Edge)** — klasa Pydantic opisująca właściwości relacji, np. `WorkAt`. _Nie mylić z:_ Relacją — Edge to tylko dane na krawędzi. Źródło: `node4j/edges.py`.
- **Filtr Q** — drzewo warunków `pole__operator=wartość` łączone `&`, `|`, `~`, tłumaczone na WHERE z parametrami. Brak sufiksu albo nieznany sufiks = równość. Źródło: `node4j/query.py`.
- **Prefetch** — wczytanie relacji (także zagnieżdżonych) w tym samym zapytaniu co węzeł; wynik trafia do cache instancji, z którego korzysta lazy load. Źródło: `node4j/manager.py` → `ReturnQueryBuilder`.
- **Hak cyklu życia** — `pre_save`, `post_save`, `pre_delete`, `post_delete` na instancji, nadpisywane przez użytkownika; wywoływane przez `create`, `update`, `delete`, `bulk_create`, `bulk_update`. Źródło: `node4j/nodes.py`, `node4j/manager.py`.
- **`uid` a `_internal_id`** — `uid` to trwała tożsamość węzła nadana przez bibliotekę; `_internal_id` to `elementId` z Neo4j, ustawiany przy odczycie i używany wewnątrz operacji. Źródło: ADR 0003.
- **Miękkie usunięcie** — oznaczenie węzła `is_deleted=True` z `deleted_at` zamiast usunięcia; po `setup_soft_delete_manager()` menedżer `.q` ukrywa takie węzły, a `.all_objects` widzi wszystkie. Źródło: `node4j/mixins.py` → `SoftDeleteMixin`, `node4j/managers.py`.
- **TTL** — czas wygaśnięcia węzła (`ttl`), po którym okresowe zadanie APOC ma go usunąć. Źródło: `node4j/mixins.py` → `TTLMixin`, `TTL_CLEANUP_QUERY`; test `tests/test_ttl.py`.
- **Transakcja atomowa** — blok `connection.transaction()` albo funkcja z `@connection.atomic()`; zapytania w tym samym kontekście asynchronicznym idą przez tę transakcję. _Zawsze:_ transakcje się nie zagnieżdżają (`RuntimeError`). Źródło: `node4j/db.py`.
- **Dokumentacja użytkownika** — `README.md` i strony w `docs/`, w wersji angielskiej (wiodącej) i polskiej, dla programisty używającego biblioteki. _Zawsze:_ wersje EN i PL mają ten sam zestaw stron, nagłówków i identyczne bloki kodu; każdy blok Pythona w wersji EN jest uruchamiany przez test albo ma jawny znacznik pominięcia. Źródło: [readme-aktualne](zdolnosci/readme-aktualne/mapa.md) → Decyzje.
- **Znane ograniczenie** — opisane w dokumentacji zachowanie, które może zaskoczyć użytkownika albo nie działa (np. triggery APOC, daty jako tekst). _Nie mylić z:_ funkcją planowaną — dokumentacja nie zapowiada funkcji bez kodu.

## Czym to nie jest

- Węzeł nie jest rekordem z `elementId` — `_internal_id` nie jest tożsamością i nie trafia do zapisu.
- Model relacji (Edge) nie jest węzłem — nie ma menedżera ani etykiet i nie trafia do rejestru.
- Mixin (`TTLMixin`, `SoftDeleteMixin`) nie jest „czystą” domieszką — dziedziczy po `Node`, więc sam jest modelem z etykietą i wpisem w rejestrze.
