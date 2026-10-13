# Zapytania i filtry

[English](../en/queries-and-filters.md) · [README](../../README_PL.md)

## Tworzenie, odczyt, aktualizacja i usuwanie

Menedżer modelu jest dostępny jako `Model.q`. Jego metody są asynchroniczne:

- `create(**fields)` zapisuje nowy węzeł i go zwraca.
- `match_one(filters=...)` zwraca pierwszy pasujący węzeł albo `None`. Wymaga filtra.
- `match_all(filters=..., order_by=...)` zwraca pasujące węzły. Filtr i kolejność są opcjonalne.
- `update(filters=..., data=...)` aktualizuje pasujące węzły i zwraca ich liczbę.
- `delete(filters=...)` usuwa pasujące węzły i zwraca ich liczbę.

Użyj stabilnej właściwości, takiej jak `uid`, aby wskazać jeden węzeł:

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

## Pobierz lub utwórz oraz zaktualizuj lub utwórz

Obie metody zwracają `(węzeł, utworzono)`. `get_or_create` zwraca znaleziony węzeł bez zmian albo tworzy go z `filters` i `defaults`. `update_or_create` aktualizuje znaleziony węzeł przez `defaults` albo tworzy nowy, gdy nie ma dopasowania.

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

## Filtrowanie przez `Q`

Użyj `Q(pole=wartość)` do równości i łącz warunki operatorami `&` (AND), `|` (OR) oraz `~` (NOT). Obsługiwane sufiksy to:

| Sufiks | Porównanie |
| --- | --- |
| `gt` | większe niż (`>`) |
| `gte` | większe lub równe (`>=`) |
| `lt` | mniejsze niż (`<`) |
| `lte` | mniejsze lub równe (`<=`) |
| `in` | wartość znajduje się na liście (`IN`) |
| `contains` | tekst zawiera wartość (`CONTAINS`) |
| `startswith` | tekst zaczyna się od wartości (`STARTS WITH`) |
| `endswith` | tekst kończy się wartością (`ENDS WITH`) |
| `ne` | nierówność (`<>`) |

Nieznany sufiks po cichu zamienia warunek na równość. Literówka w sufiksie może więc dać inny wynik, niż oczekujesz.

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
