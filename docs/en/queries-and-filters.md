# Queries and filters

[Polski](../pl/queries-and-filters.md) · [README](../../README.md)

## Create, read, update, and delete

The model manager is available as `Model.q`. These methods are asynchronous:

- `create(**fields)` stores a new node and returns it.
- `match_one(filters=...)` returns the first matching node or `None`. It requires a filter.
- `match_all(filters=..., order_by=...)` returns matching nodes. Filters and sort order are optional.
- `update(filters=..., data=...)` updates matching nodes and returns the number updated.
- `delete(filters=...)` deletes matching nodes and returns the number deleted.

Use a stable property such as `uid` when you want to target one node:

```python
from node4j.nodes import Node


class GuideRecord(Node):
    title: str
    category: str


record = await GuideRecord.q.create(title="First steps", category="guide")
same_record = await GuideRecord.q.match_one(
    filters={"uid": str(record.uid)}
)
guides = await GuideRecord.q.match_all(
    filters={"category": "guide"}, order_by=["title"]
)
updated_count = await GuideRecord.q.update(
    filters={"uid": str(record.uid)}, data={"title": "Getting started"}
)
deleted_count = await GuideRecord.q.delete(filters={"uid": str(record.uid)})

assert same_record is not None and same_record.title == "First steps"
assert [item.title for item in guides] == ["First steps"]
assert updated_count == 1 and deleted_count == 1
```

## Get or create and update or create

Both helpers return `(node, created)`. `get_or_create` returns an existing match without changing it, or creates one from `filters` and `defaults`. `update_or_create` updates an existing match with `defaults`, or creates it when there is no match.

```python
person, created = await GuideRecord.q.get_or_create(
    filters={"title": "Reference", "category": "guide"}
)
assert created
existing, created_again = await GuideRecord.q.get_or_create(
    filters={"title": "Reference", "category": "guide"}
)
assert not created_again and existing.uid == person.uid

updated, created_by_update_or_create = await GuideRecord.q.update_or_create(
    filters={"title": "Reference", "category": "guide"},
    defaults={"title": "Reference guide"},
)
assert not created_by_update_or_create
assert updated is not None and updated.title == "Reference guide"
assert await GuideRecord.q.count(filters={"category": "guide"}) == 1
```

## Filter with `Q`

Use `Q(field=value)` for equality and join conditions with `&` (AND), `|` (OR), and `~` (NOT). Supported suffixes are:

| Suffix | Comparison |
| --- | --- |
| `gt` | greater than (`>`) |
| `gte` | greater than or equal (`>=`) |
| `lt` | less than (`<`) |
| `lte` | less than or equal (`<=`) |
| `in` | value is in a list (`IN`) |
| `contains` | string contains a value (`CONTAINS`) |
| `startswith` | string starts with a value (`STARTS WITH`) |
| `endswith` | string ends with a value (`ENDS WITH`) |
| `ne` | not equal (`<>`) |

An unknown suffix silently falls back to equality. A misspelled suffix can therefore produce a different result than intended. See [Known limitations](known-limitations.md) for a safe response.

```python
from node4j.query import Q


class GuideFilterPerson(Node):
    name: str
    age: int
    role: str


for name, age, role in [
    ("Ada Example", 36, "writer"),
    ("Grace Example", 42, "engineer"),
    ("Alan Example", 27, "artist"),
]:
    await GuideFilterPerson.q.create(name=name, age=age, role=role)

cases = [
    (Q(age__gt=35), {"Ada Example", "Grace Example"}),
    (Q(age__gte=36), {"Ada Example", "Grace Example"}),
    (Q(age__lt=36), {"Alan Example"}),
    (Q(age__lte=36), {"Ada Example", "Alan Example"}),
    (Q(age__in=[27, 36]), {"Ada Example", "Alan Example"}),
    (Q(name__contains="Example"), {"Ada Example", "Grace Example", "Alan Example"}),
    (Q(name__startswith="A"), {"Ada Example", "Alan Example"}),
    (Q(name__endswith="Example"), {"Ada Example", "Grace Example", "Alan Example"}),
    (Q(role__ne="writer"), {"Grace Example", "Alan Example"}),
    (Q(role="writer"), {"Ada Example"}),
]
for condition, expected_names in cases:
    people = await GuideFilterPerson.q.match_all(
        filters=condition, order_by=["name"]
    )
    assert {person.name for person in people} == expected_names

and_result = await GuideFilterPerson.q.match_all(
    filters=Q(age__gte=30) & Q(role="writer"), order_by=["-age"]
)
or_result = await GuideFilterPerson.q.match_all(
    filters=Q(role="writer") | Q(role="artist"), order_by=["name"]
)
not_result = await GuideFilterPerson.q.match_all(
    filters=~Q(role="artist"), order_by=["-age"]
)

assert [person.name for person in and_result] == ["Ada Example"]
assert [person.name for person in or_result] == ["Ada Example", "Alan Example"]
assert [person.name for person in not_result] == ["Grace Example", "Ada Example"]
```
