# node4j/nodes.py
from __future__ import annotations

import uuid
import logging  # ### ZMIANA ###
from pydantic import BaseModel, Field, PrivateAttr
from typing import ClassVar, Any

from .registry import node_registry
from .manager import NodeManager

# ### ZMIANA ###: Inicjalizacja loggera dla modułu
log = logging.getLogger(__name__)


class NodeBase(type(BaseModel)):
    def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]):
        # ### ZMIANA ###: Logowanie rozpoczęcia tworzenia nowej klasy modelu
        # Używamy loggera specyficznego dla tworzonej klasy, np. "node4j.nodes.Person"
        class_log = log.getChild(name)
        if name != "Node":
            class_log.debug(f"Node class '{name}' is being created by metaclass.")

        from .properties import RelationshipProperty

        # --- Przetwarzanie relacji ---
        relationships: dict[str, RelationshipProperty] = {}
        for base in bases:
            if hasattr(base, "_relationships"):
                relationships.update(base._relationships)
        current_class_rels = {}
        for attr_name, value in list(attrs.items()):
            if isinstance(value, RelationshipProperty):
                current_class_rels[attr_name] = value
                del attrs[attr_name]
        relationships.update(current_class_rels)
        
        # ### ZMIANA ###: Logowanie znalezionych relacji
        if name != "Node" and relationships:
             class_log.debug(
                f"Processed {len(relationships)} relationships.",
                extra={"relationship_names": list(relationships.keys())}
            )

        kls = super().__new__(mcs, name, bases, attrs)

        for attr_name, descriptor in current_class_rels.items():
            if hasattr(descriptor, "__set_name__"):
                descriptor.__set_name__(kls, attr_name)
            setattr(kls, attr_name, descriptor)
            
        kls._relationships = relationships

        # --- Przetwarzanie klasy Meta ---
        meta_options = {}
        for base in reversed(bases):
            if hasattr(base, "_meta"):
                meta_options.update(base._meta)
        if "Meta" in attrs:
            meta_class = attrs["Meta"]
            current_meta = {
                k: v for k, v in meta_class.__dict__.items() if not k.startswith("__")
            }
            meta_options.update(current_meta)
        kls._meta = meta_options
        
        # ### ZMIANA ###: Logowanie przetworzonych opcji Meta
        if name != "Node" and meta_options:
            class_log.debug(f"Processed Meta options.", extra={"meta_options": meta_options})


        # --- Przetwarzanie etykiet (__labels__) ---
        all_labels = set()
        for base in bases:
            if hasattr(base, "__labels__"):
                all_labels.update(base.__labels__)
        if name != "Node":
            all_labels.add(name)
        kls.__labels__ = sorted(list(all_labels))

        # ### ZMIANA ###: Logowanie finalnych etykiet
        if name != "Node":
            class_log.debug(f"Final labels set.", extra={"labels": kls.__labels__})


        # --- Rejestracja modelu i managera ---
        if name != "Node":
            node_registry[name] = kls
            kls.q = NodeManager(kls)
            # ### ZMIANA ###: Logowanie rejestracji modelu
            class_log.info(f"Node class '{name}' registered successfully with a NodeManager.")
            
        return kls


class Node(BaseModel, metaclass=NodeBase):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)
    _internal_id: str | None = PrivateAttr(default=None)

    _relationships: ClassVar[dict[str, "RelationshipProperty"]]
    _meta: ClassVar[dict[str, Any]] = {}
    __labels__: ClassVar[list[str]] = []

    q: ClassVar[NodeManager]

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def labels(cls) -> list[str]:
        return cls.__labels__

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} uid={self.uid}>"

    def __repr__(self) -> str:
        return str(self)

    # --- Haki cyklu życia ---
    # Te metody są puste i mają być nadpisywane przez użytkownika.
    # Logowanie powinno być implementowane w nadpisanych wersjach.

    async def pre_save(self, *, is_creating: bool) -> None:
        """Wywoływane przed operacją create lub update."""
        pass

    async def post_save(self, *, is_creating: bool) -> None:
        """Wywoływane po operacji create lub update."""
        pass

    async def pre_delete(self) -> None:
        """Wywoływane przed operacją delete."""
        pass

    async def post_delete(self) -> None:
        """Wywoływane po operacji delete."""
        pass