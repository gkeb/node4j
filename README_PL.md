## node4j - Nowoczesny, asynchroniczny OGM dla Neo4j

**node4j** to nowoczesny, w pełni asynchroniczny OGM (Object-Graph Mapper) dla bazy danych Neo4j, zbudowany w oparciu o Pydantic i oficjalny sterownik neo4j. Został zaprojektowany z myślą o prostocie, wydajności i elastyczności, oferując bogaty zestaw funkcji, które ułatwiają pracę z grafową bazą danych w Pythonie.

![alt text](https://img.shields.io/badge/python-3.10%2B-blue.svg)

![alt text](https://img.shields.io/badge/dependencies-pydantic%2C%20neo4j-brightgreen.svg)

![alt text](https://img.shields.io/badge/license-MIT-lightgrey.svg)

### Kluczowe Funkcjonalności
- **W pełni asynchroniczne API**: Zbudowany od podstaw z użyciem `async/await`.
- **Modele oparte na Pydantic**: Solidna walidacja danych, typowanie i serializacja "za darmo".
- **Deklaratywne zarządzanie schematem**: Definiuj indeksy i ograniczenia (constraints) bezpośrednio w modelach.
- **Potężne API zapytań**: Intuicyjny menedżer zapytań (`.q`) z obsługą zaawansowanych filtrów za pomocą obiektów `Q`.
- **Zarządzanie relacjami**: 
  - Zarówno leniwe (`await node.relacja`), jak i chętne (`prefetch=[...]`) ładowanie relacji, w tym zagnieżdżone.
  - W pełni obiektowe API: `node.relacja.connect(other_node)` i `node.relacja.disconnect(other_node)`.
- **Haki cyklu życia**: Metody `pre_save`, `post_save`, `pre_delete`, `post_delete` do implementacji logiki biznesowej.
- **Wydajne operacje masowe**: Metody `bulk_create` i `bulk_update` do pracy z dużymi zbiorami danych w jednym zapytaniu.
- **Transakcje atomowe**: Wygodny dekorator `@connection.atomic()` zapewniający spójność danych.
- **Modułowe Rozszerzenia (APOC & GDS)**: Opcjonalna, czysta integracja z najpopularniejszymi bibliotekami Neo4j. Obejmuje m.in.:
  - Wydajny, masowy import danych z plików JSON i CSV.
  - Zarządzanie triggerami bazodanowymi.
  - Wygodne opakowania dla procedur analitycznych Graph Data Science.
- **Gotowe Wzorce Modeli (Mixins)**: Elastyczny system "mixinów" do dodawania zaawansowanych funkcjonalności do modeli przez dziedziczenie, w tym:
  - Automatyczne wygasanie danych (TTL).
  - Miękkie usuwanie (Soft Delete).
### Instalacja
```bash
pip install pydantic neo4j-driver python-dotenv
```
### Szybki Start

#### 1. Konfiguracja
Utwórz plik `.env` w głównym katalogu projektu:

```
NODE4J_URI="bolt://localhost:7687"
NODE4J_USER="neo4j"
NODE4J_PASSWORD="password"
```

#### 2. Definiowanie Modeli

Zdefiniuj swoje węzły i relacje używając Pydantic i node4j.
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

#### 3. Podstawowe operacje CRUD
Użyj menedżera `.q` do interakcji z bazą danych.

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
### Przewodnik po Funkcjach

#### Zaawansowane Filtrowanie z `Q`

Łącz warunki za pomocą operatorów `&` (AND), `|` (OR) oraz `~` (NOT).

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

Unikaj problemu N+1 zapytań, ładując relacje z góry.
```python
# Pobierz wszystkie osoby i od razu załaduj informacje o ich miejscach pracy
people_with_jobs = await Person.q.match_all(prefetch=["works_at"])

for person in people_with_jobs:
    # Poniższe 'await' używa danych z cache'u - NIE wykonuje nowego zapytania do bazy
    jobs = await person.works_at 
    if jobs: 
        print(f"{person.name} pracuje w {len(jobs)} firmach.")
```

#### Operacje Masowe

Wydajnie twórz i aktualizuj wiele węzłów naraz.
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
#### Transakcje Atomowe
Użyj dekoratora `@connection.atomic()`, aby zapewnić, że wszystkie operacje w funkcji wykonają się pomyślnie, albo żadna.
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
## Zaawansowane Wzorce Modeli (Mixins)

**node4j** dostarcza gotowe do użycia klasy "mixin", które pozwalają w łatwy sposób wzbogacić modele o zaawansowane wzorce zarządzania cyklem życia danych poprzez proste dziedziczenie.

## Automatyczne Wygasanie Danych (TTL)

Mixin `TTLMixin` pozwala na oznaczanie węzłów, aby były automatycznie usuwane z bazy po określonym czasie. Jest to idealne rozwiązanie dla danych tymczasowych, takich jak sesje, tokeny czy powiadomienia.

1. Zdefiniuj model dziedziczący po TTLMixin:
```python
# models.py
from node4j.mixins import TTLMixin
import datetime

class TemporaryLink(TTLMixin):
    token: str
    url: str
```
2. Skonfiguruj infrastrukturę TTL (jednorazowo):
   
W głównym pliku aplikacji należy uruchomić mechanizm czyszczący. Wykorzystuje on apoc.periodic.repeat do cyklicznego usuwania wygasłych węzłów.
```python
# main.py
from node4j.mixins import TTLMixin

await TTLMixin.setup_ttl_infrastructure()
```
3. Ustawiaj czas wygaśnięcia:
```python
import datetime

# Tworzymy link, który wygaśnie za 24 godziny
link = await TemporaryLink.q.create(token="xyz", url="/reset")
await link.save_with_expiry(lifespan=datetime.timedelta(hours=24))
```
### Miękkie Usuwanie (Soft Delete)
Zamiast trwale usuwać dane, wzorzec "soft delete" oznacza je jako nieaktywne. Pozwala to na zachowanie historii, audyt i możliwość łatwego przywrócenia danych.
1.  Zdefiniuj model dziedziczący po `SoftDeleteMixin`:
    ```python
    # models.py
    from node4j.mixins import SoftDeleteMixin

    class Article(SoftDeleteMixin):
        title: str
        content: str
    ```

2.  Aktywuj system podwójnego menedżera:

    Metoda `.setup_soft_delete_manager()` instaluje dwa menedżery zapytań, aby zapewnić pełną kontrolę nad widocznością danych:
    *   `.q` – Domyślny menedżer, który automatycznie **ukrywa** "usunięte" obiekty.
    *   `.all_objects` – Specjalny menedżer, który **zawsze widzi wszystkie** obiekty, również te usunięte.

    ```python
    # main.py
    from models import Article

    Article.setup_soft_delete_manager()
    ```

33.  Używaj metod `.soft_delete()` i `.restore()`:

    ```python
    article = await Article.q.create(title="Mój Artykuł", content="...")

    # Oznacz artykuł jako usunięty
    await article.soft_delete()

    # Domyślny menedżer .q nie znajdzie artykułu
    results = await Article.q.match_all(filters={"title": "Mój Artykuł"})
    print(len(results)) # -> 0

    # Użyj menedżera .all_objects, aby znaleźć usunięty artykuł
    deleted_article = await Article.all_objects.match_one(filters={"title": "Mój Artykuł"})
    if deleted_article:
        print(f"Znaleziono usunięty artykuł: {deleted_article.title}")
        
        # Przywróć artykuł
        await deleted_article.restore()

    # Teraz domyślny menedżer .q znowu go widzi
    restored_article = await Article.q.match_one(filters={"title": "Mój Artykuł"})
    print(f"Przywrócono artykuł: {restored_article is not None}") # -> True
    ```

## Rozszerzenia: APOC i Graph Data Science
**node4j** oferuje opcjonalną, ścisłą integrację z popularnymi bibliotekami rozszerzeń Neo4j: **APOC** i **Graph Data Science (GDS)**. Moduły te dostarczają wygodne, pythonowe opakowania dla najczęściej używanych procedur, umożliwiając zaawansowaną analizę i manipulację danymi bezpośrednio z poziomu Twojego kodu.
### Wymagania
Aby korzystać z tych modułów, serwer Neo4j musi mieć zainstalowane odpowiednie wtyczki. Najprostszym sposobem jest użycie oficjalnych obrazów Docker:
- Dla APOC: Użyj obrazu neo4j z tagiem -enterprise (niektóre funkcje APOC są tylko w wersji Enterprise) lub upewnij się, że plik .jar APOC jest w katalogu plugins Twojej instalacji.
- Dla GDS: Użyj oficjalnego obrazu neo4j/neo4j-experimental lub neo4j/neo4j-graph-data-science, który ma preinstalowaną i skonfigurowaną bibliotekę GDS.

Przykład pliku docker-compose.yml:
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
### Korzystanie z modułu APOC
Moduł apoc udostępnia funkcje opakowujące popularne procedury.
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
### Zaawansowane Zarządzanie Danymi z APOC
Poza ogólnymi procedurami, node4j oferuje specjalny, świadomy modelu menedżer `.apoc`, który pozwala na wykonywanie operacji masowych bezpośrednio z plików.
### Aktywacja menedżera APOC:
Aby uzyskać dostęp do Model.apoc, należy najpierw "zainstalować" menedżer dla konkretnej klasy modelu:
```python
from models import Person
from node4j.ext.apoc import install_apoc_manager

# Aktywuje atrybut `Person.apoc`
install_apoc_manager(Person)
```
#### Masowy import z JSON:
Załóżmy, że mamy plik people.json z listą obiektów. Możemy go załadować do Neo4j jedną komendą:
```python
# new_people.json
# [{"name": "Frank", "age": 55}, {"name": "Grace", "age": 60}]

# Ładowanie danych. Wymaga absolutnej ścieżki do pliku.
file_url = "file:///path/to/your/data/people.json"
result = await Person.apoc.create_from_json(file_url)

print(f"Załadowano {result.get('total', 0)} nowych osób.")
```
#### Masowe tworzenie relacji z CSV:
Jeśli masz już w bazie węzły (np. załadowane z users.csv), możesz masowo utworzyć między nimi relacje na podstawie drugiego pliku, friendships.csv.
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
### Korzystanie z modułu Graph Data Science (GDS)
Moduł gds upraszcza typowy cykl pracy z GDS: projekcja grafu, uruchomienie algorytmu i usunięcie projekcji.
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
