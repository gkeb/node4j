# Bulk operations and aggregations

[Polski](../pl/bulk-operations-and-aggregations.md) · [README](../../README.md)

## Create and update nodes in bulk

`bulk_create` creates nodes from a list of dictionaries. `bulk_update` updates matching nodes; by default it matches on `uid`, and you can choose another model property with `match_on`. Both methods call `pre_save` before writing and `post_save` after writing for each node.

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

## Aggregate matching nodes

Pass Cypher aggregation expressions as keyword arguments. Both aggregation expressions and their aliases are inserted directly into the query. Use only trusted, developer-written expressions and aliases; never pass user input.

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
