# models.py
import uuid
import datetime
import logging  # ### ZMIANA ###
from pydantic import Field, BaseModel

from node4j.nodes import Node
from node4j.properties import RelationshipProperty, RelationshipDirection
from node4j.edges import Edge

# ### ZMIANA ###: Inicjalizacja loggera dla modułu
log = logging.getLogger(__name__)


class WorkAt(Edge):
    role: str
    start_year: int


class AuditLog(Node):
    """Model do zapisywania logów o operacjach na innych węzłach."""
    target_uid: str
    action: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    message: str


class Person(Node):
    name: str
    age: int
    email: str | None = None
    last_modified: datetime.datetime | None = None

    works_at = RelationshipProperty("WORK_AT", "Company", RelationshipDirection.OUT, model=WorkAt)
    knows = RelationshipProperty("KNOWS", "Person", RelationshipDirection.UNDIRECTED)
    posts = RelationshipProperty("WROTE", "Post", RelationshipDirection.OUT)

    class Meta:
        indexes = ["name"]
        constraints = [("email",)]

    # ### ZMIANA ###: Wprowadzenie dedykowanego loggera dla haków
    def _get_hook_logger(self):
        """Pomocnicza metoda do tworzenia loggera z kontekstem instancji."""
        # Tworzy logger np. 'models.Person' i dodaje kontekst
        logger = logging.getLogger(f"models.{self.__class__.__name__}")
        return logger.getChild(str(self.uid))


    async def pre_save(self, *, is_creating: bool) -> None:
        """Przed zapisem ustawia znacznik czasu modyfikacji."""
        # ### ZMIANA ###: Zastąpienie print loggerem
        hook_log = self._get_hook_logger()
        hook_log.debug(
            "Executing pre_save hook", 
            extra={"is_creating": is_creating, "person_name": self.name}
        )
        self.last_modified = datetime.datetime.utcnow()

    async def post_save(self, *, is_creating: bool) -> None:
        """Po zapisie tworzy wpis w logu audytowym."""
        action = "CREATE" if is_creating else "UPDATE"
        # ### ZMIANA ###: Zastąpienie print loggerem
        hook_log = self._get_hook_logger()
        hook_log.info(
            "Executing post_save hook, creating audit log.",
            extra={"action": action, "person_name": self.name}
        )
        await AuditLog.q.create(
            target_uid=str(self.uid),
            action=action,
            message=f"Person '{self.name}' was {action.lower()}d.",
        )

    async def pre_delete(self) -> None:
        """Przed usunięciem można by tu np. zarchiwizować dane."""
        # ### ZMIANA ###: Zastąpienie print loggerem
        hook_log = self._get_hook_logger()
        hook_log.debug(
            "Executing pre_delete hook",
            extra={"person_name": self.name}
        )

    async def post_delete(self) -> None:
        """Po usunięciu tworzy wpis w logu i usuwa powiązane dane."""
        # ### ZMIANA ###: Zastąpienie print loggerem
        hook_log = self._get_hook_logger()
        hook_log.info(
            "Executing post_delete hook, creating and cleaning up audit logs.",
            extra={"person_name": self.name}
        )
        await AuditLog.q.create(
            target_uid=str(self.uid),
            action="DELETE",
            message=f"Person '{self.name}' was deleted.",
        )
        # ### ZMIANA ###: Logowanie operacji czyszczenia
        hook_log.debug("Deleting audit logs for the deleted person.")
        await AuditLog.q.delete(filters={"target_uid": str(self.uid)})
        hook_log.info("Audit logs for deleted person have been removed.")


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
    tags = RelationshipProperty("HAS_TAG", "Tag", RelationshipDirection.OUT, model=HasTag)