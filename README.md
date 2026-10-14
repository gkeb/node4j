# node4j

**node4j** is a fully asynchronous Object-Graph Mapper (OGM) for Neo4j. It uses Pydantic models and the official Neo4j Python driver.

Read this guide in [Polish](README_PL.md).

## Requirements

- Python 3.12+.
- Neo4j 5.26 LTS or Neo4j 2026.09.
- APOC and Graph Data Science (GDS) are needed only for their optional extensions.

## Installation

The package is installed from this Git repository:

```bash
uv add git+https://github.com/gkeb/node4j.git
```

```bash
python -m pip install git+https://github.com/gkeb/node4j.git
```

## Quick start

Set these values in the process environment or save them in a `.env` file in the directory where your program runs. `node4j` reads the `NODE4J_*` settings automatically.

```dotenv
NODE4J_URI=bolt://127.0.0.1:7687
NODE4J_USER=neo4j
NODE4J_PASSWORD=change-me
```

Save the following as `quickstart.py` and run it with Python. It creates two nodes, connects them, reads one node back, and loads its relationship.

```python
import asyncio

from node4j.db import connection
from node4j.nodes import Node
from node4j.properties import RelationshipDirection, RelationshipProperty


class Person(Node):
    name: str

    knows = RelationshipProperty("KNOWS", "Person", RelationshipDirection.OUT)


async def main():
    await connection.connect()
    try:
        ada = await Person.q.create(name="Ada Example")
        grace = await Person.q.create(name="Grace Example")
        await ada.knows.connect(grace)

        saved_ada = await Person.q.match_one(filters={"uid": str(ada.uid)})
        connections = await saved_ada.knows
        print(f"{saved_ada.name} has {len(connections)} connection(s).")
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

- [Models and schema](docs/en/models-and-schema.md)
- [Queries and filters](docs/en/queries-and-filters.md)
- [Relationships](docs/en/relationships.md)
- [Bulk operations and aggregations](docs/en/bulk-operations-and-aggregations.md)
- [Transactions](docs/en/transactions.md)
- [Mixins](docs/en/mixins.md)
- [Configuration and logging](docs/en/configuration-and-logging.md)
