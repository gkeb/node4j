# Transactions

[Polski](../pl/transactions.md) · [README](../../README.md)

## Use an explicit transaction

`connection.transaction()` commits when its block finishes normally and rolls back when an exception escapes. Operations made through the OGM inside the block use the same transaction.

```python
from node4j.db import connection
from node4j.nodes import Node


class LedgerEntry(Node):
    label: str


rollback_label = "rollback-example"
try:
    async with connection.transaction():
        await LedgerEntry.q.create(label=rollback_label)
        raise ValueError("rollback example")
except ValueError as error:
    assert str(error) == "rollback example"
else:
    raise AssertionError("The transaction should have rolled back.")

assert await LedgerEntry.q.match_one(filters={"label": rollback_label}) is None
```

## Use the atomic decorator

`@connection.atomic()` wraps an async function in a transaction. Its changes commit when the function returns normally and roll back if it raises an exception.

```python
@connection.atomic()
async def create_entry(label: str):
    return await LedgerEntry.q.create(label=label)


saved_entry = await create_entry("committed-example")
assert saved_entry.label == "committed-example"
```

## Transactions cannot be nested

Opening another transaction while one is active raises `RuntimeError`. The same applies when an `@connection.atomic()` function is called from inside an active transaction.

```python
nested_transaction_rejected = False
try:
    async with connection.transaction():
        async with connection.transaction():
            raise AssertionError("The nested transaction should not start.")
except RuntimeError:
    nested_transaction_rejected = True

assert nested_transaction_rejected
```
