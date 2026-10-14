# Models and schema

[Polski](../pl/models-and-schema.md) · [README](../../README.md)

## Define a node

Create a class that inherits from `Node` and declare its data as Pydantic fields. Every node gets a `uid` UUID4 by default. The library stores `uid` in Neo4j as text. Date and datetime fields are also persisted as text; see [Known limitations](known-limitations.md) for the consequences and handling advice.

The global registry is keyed by class name, so model class names must be unique across the application. See [Known limitations](known-limitations.md) for details.

```python
from node4j.nodes import Node


class GuidePerson(Node):
    name: str
    email: str

    class Meta:
        indexes = ["name"]
        constraints = [("email",)]


class GuideResearcher(GuidePerson):
    field: str


await GuidePerson.q.apply_schema()
researcher = await GuideResearcher.q.create(
    name="Ada Example",
    email="ada@example.com",
    field="graph databases",
)
found = await GuidePerson.q.match_one(filters={"email": "ada@example.com"})

assert GuidePerson.labels() == ["GuidePerson"]
assert GuideResearcher.labels() == ["GuidePerson", "GuideResearcher"]
assert researcher.uid.version == 4
assert found is not None and found.name == "Ada Example"
```

## Inheritance and labels

Each model contributes a Neo4j label. A child model includes the labels of its parent models, so querying with `GuidePerson.q` also finds `GuideResearcher` nodes. The result is loaded as the model used for the query.

## Indexes and constraints

Put property names in `Meta.indexes` to create indexes. Put tuples of property names in `Meta.constraints` to create composite uniqueness constraints; a one-property constraint is a one-item tuple. Call `Model.q.apply_schema()` to create the declared schema. It uses `IF NOT EXISTS`, so calling it again leaves existing indexes and constraints in place.

The example declares an index on `name` and a uniqueness constraint on `email` for the `GuidePerson` label.

## Lifecycle hooks

Models may override these async hooks:

- `pre_save` and `post_save` run before and after create or update, with `is_creating=True` for creation and `False` for update.
- `pre_delete` and `post_delete` run before and after deletion.

The hook can validate or adjust a model before it is stored:

```python
from typing import ClassVar


class GuideCleanPerson(Node):
    name: str
    events: ClassVar[list[str]] = []

    async def pre_save(self, *, is_creating: bool) -> None:
        self.name = self.name.strip()
        self.events.append(f"pre_save:{is_creating}")

    async def post_save(self, *, is_creating: bool) -> None:
        self.events.append(f"post_save:{is_creating}")

    async def pre_delete(self) -> None:
        self.events.append("pre_delete")

    async def post_delete(self) -> None:
        self.events.append("post_delete")


clean_person = await GuideCleanPerson.q.create(name="  Grace Example  ")
assert clean_person.name == "Grace Example"
await GuideCleanPerson.q.update(
    filters={"uid": str(clean_person.uid)}, data={"name": "  Ada Example  "}
)
await GuideCleanPerson.q.delete(filters={"uid": str(clean_person.uid)})
assert GuideCleanPerson.events == [
    "pre_save:True",
    "post_save:True",
    "pre_save:False",
    "post_save:False",
    "pre_delete",
    "post_delete",
]
```
