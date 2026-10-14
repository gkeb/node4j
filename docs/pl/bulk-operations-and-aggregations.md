# Operacje masowe i agregacje

[English](../en/bulk-operations-and-aggregations.md) · [README](../../README_PL.md)

## Masowe tworzenie i aktualizowanie węzłów

`bulk_create` tworzy węzły z listy słowników. `bulk_update` aktualizuje pasujące węzły; domyślnie dopasowuje je po `uid`, a przez `match_on` możesz wskazać inną właściwość modelu. Obie metody wywołują `pre_save` przed zapisem i `post_save` po zapisie dla każdego węzła.

```python
from node4j.nodes import Node


lifecycle_events = []


class InventoryItem(Node):
    sku: str
    quantity: int

    async def pre_save(self, *, is_creating: bool) -> None:
        self.sku = self.sku.upper()

    async def post_save(self, *, is_creating: bool) -> None:
        action = "created" if is_creating else "updated"
        lifecycle_events.append((action, self.sku))


created_items = await InventoryItem.q.bulk_create(
    [
        {"sku": "SKU-001", "quantity": 4},
        {"sku": "SKU-002", "quantity": 2},
    ]
)
assert len(created_items) == 2

updated_count = await InventoryItem.q.bulk_update(
    [{"sku": "SKU-001", "quantity": 7}],
    match_on="sku",
)
assert updated_count == 1
```

## Agregowanie pasujących węzłów

Przekaż wyrażenia agregacji Cyphera jako argumenty nazwane. Tekst wyrażeń agregacji i ich aliasy trafiają bezpośrednio do zapytania. Używaj wyłącznie zaufanych wyrażeń i aliasów zapisanych przez programistę; nigdy nie przekazuj danych użytkownika.

```python
totals = await InventoryItem.q.aggregate(
    filters={"sku__in": ["SKU-001", "SKU-002"]},
    total_quantity="sum(quantity)",
    item_count="count(uid)",
)
assert totals == {"total_quantity": 9, "item_count": 2}
assert lifecycle_events == [
    ("created", "SKU-001"),
    ("created", "SKU-002"),
    ("updated", "SKU-001"),
]
```
