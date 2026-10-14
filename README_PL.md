# node4j — asynchroniczny OGM dla Neo4j

**node4j** to w pełni asynchroniczny OGM (Object-Graph Mapper) dla Neo4j. Korzysta z modeli Pydantic i oficjalnego sterownika Neo4j dla Pythona.

Przeczytaj tę instrukcję po [angielsku](README.md).

## Wymagania

- Python 3.12 lub nowszy.
- Neo4j 5.26 LTS albo Neo4j 2026.09.
- APOC i Graph Data Science (GDS) są potrzebne tylko do używania opcjonalnych rozszerzeń.

## Instalacja

Pakiet instalujemy z tego repozytorium Git:

```bash
uv add git+https://github.com/gkeb/node4j.git
```

```bash
python -m pip install git+https://github.com/gkeb/node4j.git
```

## Szybki start

Ustaw te wartości w zmiennych środowiskowych procesu albo zapisz je w pliku `.env` w katalogu, z którego uruchamiasz program. `node4j` automatycznie odczytuje ustawienia `NODE4J_*`.

```dotenv
NODE4J_URI=bolt://127.0.0.1:7687
NODE4J_USER=neo4j
NODE4J_PASSWORD=change-me
```

Zapisz poniższy kod w pliku `quickstart.py` i uruchom go Pythonem. Tworzy dwa węzły, łączy je, odczytuje jeden węzeł i ładuje jego relację.

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

## Dokumentacja

- [Modele i schemat](docs/pl/models-and-schema.md)
- [Zapytania i filtry](docs/pl/queries-and-filters.md)
- [Relacje](docs/pl/relationships.md)
- [Operacje masowe i agregacje](docs/pl/bulk-operations-and-aggregations.md)
- [Transakcje](docs/pl/transactions.md)
- [Mixiny](docs/pl/mixins.md)
- [Konfiguracja i logowanie](docs/pl/configuration-and-logging.md)
- [Rozszerzenia APOC](docs/pl/apoc-extensions.md)
- [Rozszerzenia GDS](docs/pl/gds-extensions.md)
- [Znane ograniczenia](docs/pl/known-limitations.md)
