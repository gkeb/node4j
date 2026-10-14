# Relacje

[English](../en/relationships.md) · [README](../../README_PL.md)

## Deklarowanie atrybutów relacji

Zadeklaruj relację na modelu `Node` za pomocą `RelationshipProperty`. Cel wskazuje nazwa klasy modelu docelowego, która musi być unikalna w rejestrze; szczegóły opisują [Znane ograniczenia](known-limitations.md). Kierunek określa sposób wyszukiwania relacji: `OUT` prowadzi od tego modelu do celu, `IN` prowadzi od celu do tego modelu, a `UNDIRECTED` dopasowuje ją w obu kierunkach. Połączenie utworzone przez `UNDIRECTED` nadal zaczyna się w bieżącym węźle.

Użyj podklasy `Edge`, gdy właściwości relacji mają być walidowane i dostępne z typami:

```python
from node4j.edges import Edge
from node4j.nodes import Node
from node4j.properties import RelationshipDirection, RelationshipProperty


class GuideAuthorship(Edge):
    role: str
    year: int


class GuideAuthor(Node):
    name: str
    books = RelationshipProperty(
        "AUTHORED", "GuideBook", RelationshipDirection.OUT, model=GuideAuthorship
    )
    collaborators = RelationshipProperty(
        "COLLABORATES_WITH", "GuideAuthor", RelationshipDirection.UNDIRECTED
    )


class GuideBook(Node):
    title: str
    author = RelationshipProperty(
        "AUTHORED", "GuideAuthor", RelationshipDirection.IN, model=GuideAuthorship
    )
    publisher = RelationshipProperty(
        "PUBLISHED_BY", "GuidePublisher", RelationshipDirection.OUT
    )


class GuidePublisher(Node):
    name: str
    books = RelationshipProperty(
        "PUBLISHED_BY", "GuideBook", RelationshipDirection.IN
    )
```

## Tworzenie i lazy load relacji

`connect` przyjmuje słownik właściwości, instancję `Edge` albo brak właściwości. Oczekuj relacji przez `await`, aby dostać pary `(węzeł_docelowy, właściwości_relacji)`. Gdy zadeklarowano model `Edge`, właściwości są zwracane jako jego instancja. `disconnect` usuwa relację i czyści jej wartość z pamięci podręcznej bieżącej instancji.

```python
author = await GuideAuthor.q.create(name="Ada Example")
book = await GuideBook.q.create(title="Graph Basics")
other_book = await GuideBook.q.create(title="Async Graphs")

await author.books.connect(book, {"role": "author", "year": 2026})
await author.books.connect(
    other_book, GuideAuthorship(role="editor", year=2025)
)

loaded_books = await author.books
assert {target.title: edge.role for target, edge in loaded_books} == {
    "Graph Basics": "author",
    "Async Graphs": "editor",
}

await author.books.disconnect(other_book)
remaining_books = await author.books
assert [target.title for target, _ in remaining_books] == ["Graph Basics"]
```

## Aktualizacja właściwości relacji

`Model.q.update_relationship` scala właściwości we wszystkich relacjach pasujących do UID-ów końców i typu. Działa bezpośrednio na bazie. Jeśli instancja wcześniej wczytała relację, pobierz nową instancję przed odczytem zmienionej wartości.

```python
await GuideAuthor.q.update_relationship(
    author.uid,
    book.uid,
    "AUTHORED",
    {"year": 2027},
)

fresh_author = await GuideAuthor.q.match_one(
    filters={"uid": str(author.uid)}
)
assert fresh_author is not None
updated_book, updated_edge = (await fresh_author.books)[0]
assert updated_book.title == "Graph Basics"
assert updated_edge.year == 2027
```

## Prefetch zagnieżdżonych relacji

Przekaż nazwę relacji, aby wczytać ją razem z węzłem. Zagnieżdżony słownik opisuje kolejne relacje do pobrania. Prefetch zapisuje pary w tej samej pamięci podręcznej instancji, z której korzysta lazy load, więc poniższe `await` używa pobranych danych.

Builder w czasie wykonania przyjmuje zagnieżdżone słowniki, choć adnotacje `match_one` i `match_all` podają obecnie `list[str]`; checker typów może zgłosić błąd przy tej postaci.

```python
publisher = await GuidePublisher.q.create(name="Example Press")
await book.publisher.connect(publisher)

prefetched_author = await GuideAuthor.q.match_one(
    filters={"uid": str(author.uid)},
    prefetch={"books": {"publisher": {}}},
)
assert prefetched_author is not None

prefetched_books = await prefetched_author.books
assert len(prefetched_books) == 1
prefetched_publishers = await prefetched_books[0][0].publisher
assert prefetched_publishers[0][0].name == "Example Press"
```
