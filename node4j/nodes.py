# node4j/nodes.py
from __future__ import annotations

import uuid
from pydantic import BaseModel, Field, PrivateAttr
from typing import ClassVar, Any

from .registry import node_registry
from .manager import NodeManager


class NodeBase(type(BaseModel)):
    def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]):
        from .properties import RelationshipProperty

        # --- Przetwarzanie relacji ---
        relationships: dict[str, RelationshipProperty] = {}

        # 1. Zbierz relacje z klas bazowych (rodziców)
        for base in bases:
            if hasattr(base, "_relationships"):
                relationships.update(base._relationships)

        # 2. Zbierz relacje zdefiniowane w bieżącej klasie i usuń je z atrybutów
        current_class_rels = {}
        for attr_name, value in list(attrs.items()):
            if isinstance(value, RelationshipProperty):
                current_class_rels[attr_name] = value
                del attrs[attr_name]

        # 3. Zaktualizuj główny słownik, nadpisując odziedziczone relacje
        relationships.update(current_class_rels)

        # Tworzymy klasę przed dalszymi modyfikacjami
        kls = super().__new__(mcs, name, bases, attrs)

        # Używamy relacji z bieżącej klasy, aby poprawnie ustawić deskryptory
        for attr_name, descriptor in current_class_rels.items():
            if hasattr(descriptor, "__set_name__"):
                descriptor.__set_name__(kls, attr_name)
            setattr(kls, attr_name, descriptor)

        # Ustawiamy pełny, odziedziczony słownik relacji na klasie
        kls._relationships = relationships

        # +++ NOWA SEKCJA: PRZETWARZANIE KLASY META +++
        # Tworzymy domyślny słownik opcji meta
        meta_options = {}

        # Dziedziczymy opcje z klas bazowych (ważne dla rozszerzalności)
        for base in reversed(bases):  # reversed, by klasa bliższa miała priorytet
            if hasattr(base, "_meta"):
                meta_options.update(base._meta)

        # Szukamy klasy Meta w definiowanym modelu i nadpisujemy odziedziczone opcje
        if "Meta" in attrs:
            meta_class = attrs["Meta"]
            # Pobieramy wszystkie atrybuty z klasy Meta, które nie są "magiczne"
            current_meta = {
                k: v for k, v in meta_class.__dict__.items() if not k.startswith("__")
            }
            meta_options.update(current_meta)

        # Zapisujemy finalne, połączone opcje na klasie
        kls._meta = meta_options
        # +++ KONIEC NOWEJ SEKCJI +++

        # --- Przetwarzanie etykiet (__labels__) ---
        all_labels = set()
        for base in bases:
            if hasattr(base, "__labels__"):
                all_labels.update(base.__labels__)

        if name != "Node":
            all_labels.add(name)

        kls.__labels__ = sorted(list(all_labels))

        # --- Rejestracja modelu i managera ---
        if name != "Node":
            node_registry[name] = kls
            kls.q = NodeManager(kls)

        return kls


class Node(BaseModel, metaclass=NodeBase):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)
    _internal_id: str | None = PrivateAttr(default=None)

    # Atrybuty zarządzane przez metaklasę
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

        # +++ NOWA SEKCJA: HOOKI CYKLU ŻYCIA +++

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

    # +++ KONIEC NOWEJ SEKCJI +++
