# Transakcje

[English](../en/transactions.md) · [README](../../README_PL.md)

## Jawna transakcja

`connection.transaction()` zatwierdza zmiany po normalnym zakończeniu bloku, a wycofuje je, gdy z bloku wydostanie się wyjątek. Operacje OGM wykonane wewnątrz bloku korzystają z tej samej transakcji.

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

## Dekorator `atomic`

`@connection.atomic()` opakowuje funkcję asynchroniczną transakcją. Jej zmiany są zatwierdzane po normalnym zwrocie z funkcji i wycofywane, gdy funkcja rzuci wyjątek.

```python
@connection.atomic()
async def create_entry(label: str):
    return await LedgerEntry.q.create(label=label)


saved_entry = await create_entry("committed-example")
assert saved_entry.label == "committed-example"
```

## Transakcje się nie zagnieżdżają

Otwarcie kolejnej transakcji w aktywnej transakcji rzuca `RuntimeError`. To samo dotyczy wywołania funkcji z `@connection.atomic()` wewnątrz aktywnej transakcji.

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
