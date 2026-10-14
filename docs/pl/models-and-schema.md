# Modele i schemat

[English](../en/models-and-schema.md) · [README](../../README_PL.md)

## Definiowanie węzła

Utwórz klasę dziedziczącą po `Node` i zadeklaruj dane jako pola Pydantic. Każdy węzeł dostaje domyślnie `uid` typu UUID4. Biblioteka zapisuje `uid` w Neo4j jako tekst. Pola daty i czasu także są zapisywane jako tekst; zobacz [Znane ograniczenia](known-limitations.md), gdzie opisano skutki i sposób postępowania.

Globalny rejestr jest kluczowany nazwą klasy, dlatego nazwy klas modeli muszą być unikalne w całej aplikacji. Szczegóły opisują [Znane ograniczenia](known-limitations.md).

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

## Dziedziczenie i etykiety

Każdy model wnosi etykietę Neo4j. Model potomny ma też etykiety modeli rodziców, dlatego zapytanie przez `GuidePerson.q` znajduje również węzły `GuideResearcher`. Wynik jest wczytywany jako model użyty w zapytaniu.

## Indeksy i ograniczenia

Nazwy pól w `Meta.indexes` tworzą indeksy. Krotki nazw pól w `Meta.constraints` tworzą złożone ograniczenia unikalności; ograniczenie dla jednego pola zapisuje się jako krotkę jednoelementową. Wywołaj `Model.q.apply_schema()`, aby utworzyć zadeklarowany schemat. Używa ono `IF NOT EXISTS`, więc ponowne wywołanie nie zmienia istniejących indeksów ani ograniczeń.

Przykład deklaruje indeks dla `name` i ograniczenie unikalności `email` dla etykiety `GuidePerson`.

## Haki cyklu życia

Model może nadpisać asynchroniczne haki:

- `pre_save` i `post_save` uruchamiają się przed zapisem i po nim, przy tworzeniu lub aktualizacji. Dla tworzenia `is_creating=True`, a dla aktualizacji `False`.
- `pre_delete` i `post_delete` uruchamiają się przed usunięciem i po nim.

Hak może sprawdzić lub poprawić model przed zapisem:

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
