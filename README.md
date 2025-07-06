## node4j – Modern Asynchronous OGM for Neo4j

**node4j** is a modern, fully asynchronous OGM (Object-Graph Mapper) for the Neo4j database, built using Pydantic and the official Neo4j driver. It is designed for simplicity, performance, and flexibility, offering a rich set of features that make working with graph databases in Python easier.

![alt text](https://img.shields.io/badge/python-3.10%2B-blue.svg)

![alt text](https://img.shields.io/badge/dependencies-pydantic%2C%20neo4j-brightgreen.svg)

![alt text](https://img.shields.io/badge/license-MIT-lightgrey.svg)

### Key Features

- **Fully asynchronous API**: Built from the ground up with `async/await`.
- **Pydantic-based models**: Strong data validation, type safety, and serialization out-of-the-box.
- **Declarative schema management**: Define indexes and constraints directly in your models.
- **Powerful query API**: Intuitive query manager (`.q`) with advanced filter support via `Q` objects.
- **Relationship management**:
  - Lazy (`await node.relation`) and eager (`prefetch=[...]`) loading of relationships, including nested.
  - Fully object-oriented API: `node.relation.connect(other_node)` and `node.relation.disconnect(other_node)`.
- **Lifecycle hooks**: `pre_save`, `post_save`, `pre_delete`, `post_delete` methods for business logic.
- **Efficient bulk operations**: `bulk_create` and `bulk_update` for handling large datasets in one query.
- **Atomic transactions**: Handy `@connection.atomic()` decorator for ensuring data consistency.
- **Modular extensions (APOC & GDS)**: Optional, clean integration with popular Neo4j libraries, including:
  - Efficient bulk import from JSON and CSV files.
  - Management of database triggers.
  - Convenient wrappers for Graph Data Science procedures.
- **Model mixin patterns**: Flexible mixin system for adding advanced lifecycle features to your models, including:
  - Automatic data expiration (TTL).
  - Soft deletes.

### Installation

```bash
pip install pydantic neo4j-driver python-dotenv
```

### Quick Start

#### 1. Configuration

Create a `.env` file in the project root:

```
NODE4J_URI="bolt://localhost:7687"
NODE4J_USER="neo4j"
NODE4J_PASSWORD="password"
```

#### 2. Defining Models

Define your nodes and relationships using Pydantic and node4j.

```python
# models.py
import datetime
from node4j.nodes import Node
from node4j.edges import Edge
from node4j.properties import RelationshipProperty, RelationshipDirection
from node4j.query import Q

class WorkAt(Edge):
    role: str
    start_year: int

class Person(Node):
    name: str
    age: int
    last_modified: datetime.datetime | None = None

    works_at = RelationshipProperty("WORK_AT", "Company", RelationshipDirection.OUT, model=WorkAt)

    class Meta:
        indexes = ['name']

    async def pre_save(self, *, is_creating: bool):
        self.last_modified = datetime.datetime.utcnow()
        print(f"Zapisuję {self.name}...")

class Company(Node):
    name: str
    founded_in: int

    class Meta:
        constraints = [('name',)]
```

#### 3. Basic CRUD operations

Use the `.q` manager to interact with the database.

```python
import asyncio
from dotenv import load_dotenv
from node4j.db import connection
from models import Person, Company

async def main():
    load_dotenv()
    await connection.connect()

    # Czyszczenie bazy
    await connection.run("MATCH (n) DETACH DELETE n")
    
    # Stosowanie schematu z modeli
    await Person.q.apply_schema()
    await Company.q.apply_schema()

    # Tworzenie węzłów (wywoła hak pre_save)
    alice = await Person.q.create(name="Alice", age=30)
    neo_inc = await Company.q.create(name="Neo4j Inc.", founded_in=2007)

    # Tworzenie relacji
    await alice.works_at.connect(neo_inc, properties={"role": "Engineer", "start_year": 2020})

    # Wyszukiwanie
    found_alice = await Person.q.match_one(filters={"name": "Alice"})
    print(f"Znaleziono: {found_alice}")

    # Aktualizacja (również wywoła hak pre_save)
    await Person.q.update(filters={"name": "Alice"}, data={"age": 31})

    # Leniwe ładowanie relacji
    alice_reloaded = await Person.q.match_one(filters={"name": "Alice"})
    jobs = await alice_reloaded.works_at
    company, props = jobs[0]
    print(f"{alice_reloaded.name} pracuje w {company.name} jako {props.role}.")

    await connection.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Feature Guide

#### Advanced Filtering with `Q`

Combine conditions using `&` (AND), `|` (OR), and `~` (NOT):

```python
from node4j.query import Q

# Osoby starsze niż 40 LUB młodsze niż 20 lat
people = await Person.q.match_all(
    filters=Q(age__gt=40) | Q(age__lt=20)
)

# Firmy założone po 2000 roku, których nazwa NIE zawiera "Corp"
companies = await Company.q.match_all(
    filters=Q(founded_in__gt=2000) & ~Q(name__contains="Corp")
)
```

#### Eager Loading (Prefetching)

Avoid N+1 query issues by loading relationships upfront:

```python
# Fetch all people and eagerly load their job information
people_with_jobs = await Person.q.match_all(prefetch=["works_at"])

for person in people_with_jobs:
    # The 'await' below uses cached data - it does NOT execute a new DB query
    jobs = await person.works_at
    if jobs: 
        print(f"{person.name} works at {len(jobs)} companies.")
```

#### Bulk Operations

Efficiently create and update many nodes at once:

```python
# Masowe tworzenie
new_people_data = [
    {"name": "Bob", "age": 42},
    {"name": "Charlie", "age": 35},
]
created_people = await Person.q.bulk_create(new_people_data)

# Masowa aktualizacja
update_data = [
    {"uid": str(created_people[0].uid), "age": 43},
    {"uid": str(created_people[1].uid), "age": 36},
]
updated_count = await Person.q.bulk_update(update_data, match_on="uid")
```

#### Atomic Transactions

Use `@connection.atomic()` to ensure all or nothing:

```python
from node4j.db import connection

@connection.atomic()
async def transfer_employee(employee_name: str, from_company_name: str, to_company_name: str):
    employee = await Person.q.match_one(filters={"name": employee_name})
    from_company = await Company.q.match_one(filters={"name": from_company_name})
    to_company = await Company.q.match_one(filters={"name": to_company_name})
    
    await employee.works_at.disconnect(from_company)
    
    # Jeśli tutaj wystąpi błąd, operacja disconnect zostanie wycofana (rollback)
    await employee.works_at.connect(to_company, properties={"role": "Senior", "start_year": 2024})

try:
    await transfer_employee("Bob", "Old Corp", "New Corp")
except Exception as e:
    print("Transfer nie powiódł się, zmiany zostały wycofane.")
```

## Advanced Model Patterns (Mixins)

**node4j** provides ready-to-use mixin classes for easily enriching your models with advanced lifecycle management patterns.

## Automatic Data Expiry (TTL)

`TTLMixin` allows marking nodes to be automatically removed after a certain period—ideal for sessions, tokens, or temporary notifications.

1. Define your TTL model:

```python
# models.py
from node4j.mixins import TTLMixin
import datetime

class TemporaryLink(TTLMixin):
    token: str
    url: str
```

2. Set up TTL infrastructure:

```python
# main.py
from node4j.mixins import TTLMixin

await TTLMixin.setup_ttl_infrastructure()
```

3. Use `save_with_expiry()`:

```python
import datetime

# Tworzymy link, który wygaśnie za 24 godziny
link = await TemporaryLink.q.create(token="xyz", url="/reset")
await link.save_with_expiry(lifespan=datetime.timedelta(hours=24))
```

### Soft Delete
Instead of permanently removing data, the soft delete pattern marks it as inactive—allowing for auditing and potential recovery.

1.  Define a model inheriting `SoftDeleteMixin`:
    ```python
    # models.py
    from node4j.mixins import SoftDeleteMixin

    class Article(SoftDeleteMixin):
        title: str
        content: str
    ```

2.  Activate the dual-manager system:

    The `.setup_soft_delete_manager()` method installs two query managers to give you full control over data visibility:
    *   `.q` – The default manager, which automatically **hides** "deleted" objects.
    *   `.all_objects` – A special manager that **always sees all** objects, including deleted ones.

    ```python
    # main.py
    from models import Article

    Article.setup_soft_delete_manager()
    ```

3.  Use the `.soft_delete()` and `.restore()` methods:
    ```python
    article = await Article.q.create(title="My Article", content="...")

    # Mark the article as deleted
    await article.soft_delete()

    # The default .q manager will not find the article
    results = await Article.q.match_all(filters={"title": "My Article"})
    print(len(results)) # -> 0

    # Use the .all_objects manager to find the deleted article
    deleted_article = await Article.all_objects.match_one(filters={"title": "My Article"})
    if deleted_article:
        print(f"Found deleted article: {deleted_article.title}")
        
        # Restore the article
        await deleted_article.restore()

    # Now, the default .q manager can see it again
    restored_article = await Article.q.match_one(filters={"title": "My Article"})
    print(f"Article restored: {restored_article is not None}") # -> True
    ```


## Extensions: APOC and Graph Data Science

**node4j** offers optional integration with popular Neo4j extensions: **APOC** and **Graph Data Science (GDS)**. These modules provide clean Python wrappers for common procedures, enabling advanced data analysis and manipulation directly from your code.

### Requirements

To use these modules, your Neo4j server must have the appropriate plugins installed. The easiest method is using the official Docker images:

```yaml
# docker-compose.yml
version: '3.8'
services:
  neo4j:
    image: neo4j:5-enterprise  # Obraz z włączonym APOC
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - ./neo4j/data:/data
      - ./neo4j/logs:/logs
      - ./neo4j/plugins:/plugins # Upewnij się, że GDS .jar jest tutaj, jeśli potrzebujesz
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
      - NEO4JLABS_PLUGINS=["apoc", "graph-data-science"] # Dla nowszych wersji Neo4j
```

### Using the APOC Module

```python
from node4j.ext.apoc import apoc

# Sprawdzenie wersji APOC zainstalowanej na serwerze
version = await apoc.version()
print(f"Wersja APOC: {version}")

# Wykonanie operacji w tle na dużych zbiorach danych
# Przykład: Ustawia właściwość `processed = true` dla wszystkich węzłów Person
await apoc.Periodic.iterate(
    "MATCH (p:Person) WHERE p.processed IS NULL RETURN p",
    "SET p.processed = true",
    batch_size=10000
)
```

### Advanced Data Handling with APOC

Activate model-aware `.apoc` manager:

```python
from models import Person
from node4j.ext.apoc import install_apoc_manager

# Aktywuje atrybut `Person.apoc`
install_apoc_manager(Person)
```

#### Bulk JSON Import

```python
# new_people.json
# [{"name": "Frank", "age": 55}, {"name": "Grace", "age": 60}]

# Ładowanie danych. Wymaga absolutnej ścieżki do pliku.
file_url = "file:///path/to/your/data/people.json"
result = await Person.apoc.create_from_json(file_url)

print(f"Załadowano {result.get('total', 0)} nowych osób.")
```

#### Bulk Relationship Creation from CSV

```python
# friendships.csv
# from_id,to_id,since
# 1,2,2020
# 1,3,2021

file_url = "file:///path/to/your/data/friendships.csv"

# Łączy węzły :Person na podstawie ich wspólnego klucza `userId`
await Person.apoc.connect_from_csv(
    file_url=file_url,
    from_node_config={"label": "Person", "key": "userId", "csv_column": "from_id"},
    to_node_config={"label": "Person", "key": "userId", "csv_column": "to_id"},
    rel_type="KNOWS",
    rel_properties=["since"] # Kolumna `since` z CSV staje się właściwością relacji
)
```

### Using the Graph Data Science (GDS) Module

```python
import asyncio
from node4j.db import connection
from node4j.ext.gds import gds

async def run_pagerank():
    graph_name = "my-social-graph"
    
    try:
        # 1. Stwórz projekcję grafu w pamięci GDS
        await gds.Graph.project(
            graph_name,
            "Person", # Projekcja węzłów
            {"KNOWS": {"orientation": "UNDIRECTED"}} # Projekcja relacji
        )
        print(f"Stworzono projekcję grafu '{graph_name}'")

        # 2. Uruchom algorytm PageRank
        results = await gds.Algo.run(
            graph_name,
            "gds.pageRank.stream", # Algorytm w trybie stream
            {"maxIterations": 20, "dampingFactor": 0.85}
        )
        
        print("Top 5 osób wg PageRank:")
        # Sortowanie wyników w Pythonie
        top_5 = sorted(results, key=lambda x: x['score'], reverse=True)[:5]
        for row in top_5:
            # nodeId to wewnętrzny ID GDS, można go użyć do zmapowania z powrotem na węzeł
            print(f"NodeId: {row['nodeId']}, Score: {row['score']:.4f}")

    except Exception as e:
        print(f"Wystąpił błąd podczas pracy z GDS: {e}")
    finally:
        # 3. Zawsze usuwaj projekcję z pamięci po zakończeniu pracy
        await gds.Graph.drop(graph_name)
        print(f"Usunięto projekcję grafu '{graph_name}'")

# Uruchomienie przykładu
# await run_pagerank()
```