# node4j/properties.py (poprawiona i uzupełniona wersja)
from __future__ import annotations
import enum
import logging  # ### ZMIANA ###
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, cast, Type
from pydantic import BaseModel

from neo4j.graph import Relationship

from .registry import node_registry
from .db import connection
from .edges import Edge

if TYPE_CHECKING:
    from .nodes import Node

# ### ZMIANA ###: Inicjalizacja loggera dla modułu
log = logging.getLogger(__name__)

class RelationshipDirection(enum.Enum):
    IN, OUT, UNDIRECTED = "IN", "OUT", "UNDIRECTED"


# +++ NOWA KLASA: RelationshipManager +++
class RelationshipManager:
    def __init__(self, instance: "Node", relationship: "RelationshipProperty"):
        self._instance = instance
        self._relationship = relationship
        self._cache_name = relationship.private_name
        # ### ZMIANA ###: Tworzymy logger specyficzny dla relacji na konkretnej instancji
        # np. 'node4j.properties.RelationshipManager.Person[uid].works_at'
        self._log = log.getChild(
            f"RelationshipManager.{self._instance.__class__.__name__}[{self._instance.uid}].{self._relationship.private_name.strip('_')}"
        )

    def __await__(self):
        """Umożliwia `await alice.works_at` dla lazy loadingu."""
        return self._fetch().__await__()

    async def _fetch(self) -> list[tuple["Node", Edge | dict]]:
        """Logika pobierania danych, przeniesiona z AwaitableRelationship."""
        if hasattr(self._instance, self._cache_name):
            # ### ZMIANA ###: Logowanie trafienia w cache
            self._log.debug("Relationship data loaded from cache.")
            return getattr(self._instance, self._cache_name)
        
        # ### ZMIANA ###: Logowanie pobierania danych z bazy
        self._log.debug("Cache miss. Fetching relationship data from database.")
        fetched_data = await self._relationship._async_fetch(self._instance)
        
        setattr(self._instance, self._cache_name, fetched_data)
        self._log.info(f"Fetched {len(fetched_data)} related nodes.")
        return fetched_data

    def _clear_cache(self):
        """Czyści cache po modyfikacji relacji."""
        if hasattr(self._instance, self._cache_name):
            # ### ZMIANA ###: Logowanie czyszczenia cache
            self._log.debug("Clearing relationship cache due to modification.")
            delattr(self._instance, self._cache_name)

    async def connect(self, target_node: "Node", properties: dict | Edge | None = None):
        """Tworzy relację od bieżącej instancji do węzła docelowego."""
        if not self._instance.uid or not target_node.uid:
            raise ValueError("Oba węzły muszą być zapisane w bazie (mieć UID).")

        # ### ZMIANA ###: Logowanie operacji
        self._log.info(
            f"Connecting to node.",
            extra={
                "target_node_class": target_node.__class__.__name__,
                "target_node_uid": str(target_node.uid),
            },
        )
        
        props_dict = {}
        if isinstance(properties, Edge):
            props_dict = properties.model_dump(mode="json")
        elif isinstance(properties, dict):
            props_dict = properties

        from_uid = self._instance.uid
        to_uid = target_node.uid

        # Ustalenie kierunku zapytania
        if self._relationship.relationship_direction == RelationshipDirection.IN:
            from_uid, to_uid = to_uid, from_uid

        await connection.run(
            f"""
            MATCH (a), (b)
            WHERE a.uid = $from_uid AND b.uid = $to_uid
            CREATE (a)-[r:`{self._relationship.relationship_type}`]->(b)
            SET r += $props
            """,
            params={
                "from_uid": str(from_uid),
                "to_uid": str(to_uid),
                "props": props_dict,
            },
        )
        self._clear_cache()
        self._log.info("Connection successful.")


    async def disconnect(self, target_node: "Node"):
        """Usuwa relację między bieżącą instancją a węzłem docelowym."""
        # ### ZMIANA ###: Logowanie operacji
        self._log.info(
            f"Disconnecting from node.",
            extra={
                "target_node_class": target_node.__class__.__name__,
                "target_node_uid": str(target_node.uid),
            },
        )

        from_uid = self._instance.uid
        to_uid = target_node.uid

        if self._relationship.relationship_direction == RelationshipDirection.IN:
            from_uid, to_uid = to_uid, from_uid

        await connection.run(
            f"""
            MATCH (a)-[r:`{self._relationship.relationship_type}`]->(b)
            WHERE a.uid = $from_uid AND b.uid = $to_uid
            DELETE r
            """,
            params={"from_uid": str(from_uid), "to_uid": str(to_uid)},
        )
        self._clear_cache()
        self._log.info("Disconnection successful.")



# +++ KONIEC NOWEJ KLASY +++


class RelationshipProperty:
    def __init__(
        self,
        relationship_type: str,
        target_node_label: str,
        relationship_direction: RelationshipDirection = RelationshipDirection.UNDIRECTED,
        model: Type[Edge] | None = None,
    ):
        self.relationship_type, self.target_node_label, self.relationship_direction = (
            relationship_type,
            target_node_label,
            relationship_direction,
        )
        self.private_name = ""
        self.model = model

    def __set_name__(self, owner: type["Node"], name: str):
        if not name:
            raise ValueError("RelationshipProperty musi mieć nazwę!")
        self.private_name = f"_{name}"

    def __get__(self, instance: "Node", owner: type["Node"]) -> Any:
        if instance is None:
            return self
        # ZWRACAMY NOWY MENEDŻER ZAMIAST AWAITABLE
        return RelationshipManager(instance=instance, relationship=self)

    def relationship_pattern(self) -> str:
        """Zwraca wzorzec relacji dla zapytania, np. '-[r:WORK_AT]->'."""
        rel_def = f"[r:`{self.relationship_type}`]" if self.relationship_type else "[r]"
        if self.relationship_direction == RelationshipDirection.IN:
            return f"<-{rel_def}-"
        elif self.relationship_direction == RelationshipDirection.OUT:
            return f"-{rel_def}->"
        return f"-{rel_def}-"

    def target_node_pattern(self, alias: str) -> str:
        """Zwraca wzorzec węzła docelowego, np. '(company:Company)'."""
        return f"({alias}:`{self.target_node_label}`)"

    async def _async_fetch(self, instance: "Node") -> list[tuple["Node", Edge | dict]]:
        target_node_class = node_registry.get(self.target_node_label)
        if not target_node_class:
            log.error(
                f"Target model '{self.target_node_label}' for relationship is not registered.",
                extra={"relationship_type": self.relationship_type}
            )
            raise TypeError(
                f"Model '{self.target_node_label}' nie jest zarejestrowany."
            )

        rel_pattern = self.relationship_pattern()
        target_pattern = self.target_node_pattern("node")

        query = f"""
        MATCH (start){rel_pattern}{target_pattern}
        WHERE elementId(start) = $start_id
        RETURN node {{ .*, _internal_id: elementId(node) }} as node_data, r {{ .* }} as rel_props
        """

        params = {"start_id": instance._internal_id}
        result_set = await connection.run(query, params)

        hydrated_results = []
        for row in result_set:
            node_data = row.get("node_data")
            if not node_data:
                continue

            # Tworzymy instancję węzła docelowego
            node = target_node_class.model_validate(node_data)
            node._internal_id = node_data.get("_internal_id")

            rel_properties = row.get("rel_props") or {}

            # Jeśli mamy model dla relacji, użyjmy go!
            if self.model:
                hydrated_props = self.model.model_validate(rel_properties)
            else:
                hydrated_props = rel_properties

            hydrated_results.append((node, hydrated_props))
        return hydrated_results
