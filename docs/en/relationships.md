# Relationships

[Polski](../pl/relationships.md) · [README](../../README.md)

## Declare relationship attributes

Declare a relationship on a `Node` model with `RelationshipProperty`. Its target is the target model's class name, which must be unique in the registry. Direction controls how the relationship is matched: `OUT` points from this model to the target, `IN` points from the target to this model, and `UNDIRECTED` matches either way. A connection made through `UNDIRECTED` still starts at the current node.

Use an `Edge` subclass when relationship properties need validation and typed access:

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

## Connect and lazy-load relationships

`connect` accepts a property dictionary, an `Edge` instance, or no properties. Await the relationship to get `(target_node, relationship_properties)` pairs. When an `Edge` model is declared, properties are returned as that model. `disconnect` removes the relationship and clears this instance's cached value.

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

## Update relationship properties

Use `Model.q.update_relationship` to merge properties into every relationship matching the endpoint UIDs and type. It works directly with the database. If an instance already loaded the relationship, fetch a fresh instance before reading the updated value.

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

## Prefetch nested relationships

Pass a relationship name to prefetch it with the node. A nested mapping describes further relationships to prefetch. The prefetched pairs are placed in the same per-instance cache used by lazy loading, so awaiting the relationship below uses the prefetched data.

The runtime builder accepts nested mappings, although the current `match_one` and `match_all` annotations list `list[str]`; a static type checker may flag the nested form.

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
