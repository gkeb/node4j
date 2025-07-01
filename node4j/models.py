# models.py
import uuid
import datetime
from pydantic import Field, BaseModel

from node4j.nodes import Node
from node4j.properties import RelationshipProperty, RelationshipDirection
from node4j.edges import Edge

# --- ZMIENIONA KOLEJNOŚĆ ---


class WorkAt(Edge):
    role: str
    start_year: int


# 1. Definicja AuditLog jest teraz PRZED Person
class AuditLog(Node):
    """Model do zapisywania logów o operacjach na innych węzłach."""

    target_uid: str
    action: str  # np. "CREATE", "UPDATE", "DELETE"
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    message: str


# 2. Teraz klasa Person może bezpiecznie odwoływać się do AuditLog
class Person(Node):
    name: str
    age: int
    email: str | None = None
    last_modified: datetime.datetime | None = None

    works_at = RelationshipProperty(
        "WORK_AT", "Company", RelationshipDirection.OUT, model=WorkAt
    )
    knows = RelationshipProperty("KNOWS", "Person", RelationshipDirection.UNDIRECTED)
    posts = RelationshipProperty("WROTE", "Post", RelationshipDirection.OUT)

    class Meta:
        indexes = ["name"]
        constraints = [("email",)]

    async def pre_save(self, *, is_creating: bool) -> None:
        """Przed zapisem ustawia znacznik czasu modyfikacji."""
        print(f"HOOK: pre_save dla {self.name} (is_creating={is_creating})")
        self.last_modified = datetime.datetime.utcnow()

    async def post_save(self, *, is_creating: bool) -> None:
        """Po zapisie tworzy wpis w logu audytowym."""
        action = "CREATE" if is_creating else "UPDATE"
        print(f"HOOK: post_save dla {self.name} (action={action})")
        await AuditLog.q.create(
            target_uid=str(self.uid),
            action=action,
            message=f"Person '{self.name}' was {action.lower()}d.",
        )

    async def pre_delete(self) -> None:
        """Przed usunięciem można by tu np. zarchiwizować dane."""
        print(f"HOOK: pre_delete dla {self.name}")

    async def post_delete(self) -> None:
        """Po usunięciu tworzy wpis w logu i usuwa powiązane dane."""
        print(f"HOOK: post_delete dla {self.name}")
        await AuditLog.q.create(
            target_uid=str(self.uid),
            action="DELETE",
            message=f"Person '{self.name}' was deleted.",
        )
        await AuditLog.q.delete(filters={"target_uid": str(self.uid)})
        print(f"HOOK: Usunięto logi dla usuniętej osoby '{self.name}'")


class Company(Node):
    name: str
    founded_in: int
    employees = RelationshipProperty("WORK_AT", "Person", RelationshipDirection.IN)

    class Meta:
        constraints = [("name",)]


class Employee(Person):
    employee_id: str = Field(default_factory=lambda: str(uuid.uuid4().hex[:8]))


class HasTag(Edge):
    """Model właściwości dla relacji HAS_TAG."""

    tagged_by: str = "user"


class Tag(Node):
    name: str


class Post(Node):
    title: str
    content: str
    tags = RelationshipProperty(
        "HAS_TAG", "Tag", RelationshipDirection.OUT, model=HasTag
    )
