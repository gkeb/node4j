# node4j/manager.py
from __future__ import annotations
from typing import Type, Any, TYPE_CHECKING, Optional
import uuid
import neo4j  # +++ NOWY IMPORT +++
import logging  # ### ZMIANA ###


from .db import connection, _current_transaction
from .registry import node_registry
from .properties import RelationshipDirection
from .query import Q  # <-- NOWY IMPORT

if TYPE_CHECKING:
    from neo4j import AsyncTransaction
    from .nodes import Node
    from .properties import RelationshipProperty

# ### ZMIANA ###: Inicjalizacja loggera
log = logging.getLogger(__name__)

LABEL_TYPE_MARKER = ":"

# +++ NOWA FUNKCJA POMOCNICZA (Twoja propozycja) +++
def _convert_neo4j_temporals(obj: Any) -> Any:
    """
    Rekurencyjnie przechodzi przez obiekt (słownik/listę) i konwertuje
    specyficzne dla sterownika neo4j typy temporalne (DateTime, Date, etc.)
    na natywne typy Pythona.
    """
    if isinstance(obj, dict):
        return {k: _convert_neo4j_temporals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_neo4j_temporals(v) for v in obj]
    if isinstance(
        obj,
        (
            neo4j.time.DateTime,
            neo4j.time.Date,
            neo4j.time.Time,
            neo4j.time.Duration,
        ),
    ):
        return obj.to_native()
    return obj
# +++ KONIEC NOWEJ FUNKCJI +++


class NodeManager:
    def __init__(self, node_model: Type["Node"]):
        self.model = node_model
        # ### ZMIANA ###: Dodajemy kontekst loggera specyficzny dla modelu
        self.log = log.getChild(self.model.__name__)


    def _hydrate_node(self, record: dict) -> "Node":
        if "node" not in record or "internal_id" not in record:
            self.log.error(
                "Invalid record structure for hydration",
                extra={"record_keys": list(record.keys())}
            )
            raise ValueError(
                "Rekord z bazy danych ma nieprawidłową strukturę do hydratacji."
            )
        hydrated_node = self.model.model_validate(record["node"])
        hydrated_node._internal_id = record["internal_id"]
        return hydrated_node

    async def apply_schema(self, *, tx: "AsyncTransaction" | None = None) -> None:
        """
        Czyta opcje `indexes` i `constraints` z klasy Meta modelu i tworzy
        odpowiednie struktury w bazie danych Neo4j.
        Operacja jest idempotentna (używa CREATE ... IF NOT EXISTS).
        """
        label = self.model.__name__
        meta = self.model._meta
        queries = []

        for prop_name in meta.get("indexes", []):
            index_name = f"index_{label}_{prop_name}"
            query = f"CREATE INDEX {index_name} IF NOT EXISTS FOR (n:`{label}`) ON (n.`{prop_name}`)"
            queries.append(query)

        for prop_tuple in meta.get("constraints", []):
            prop_names = [f"`{p}`" for p in prop_tuple]
            constraint_name = f"constraint_{label}_{'_'.join(prop_tuple)}"
            prop_cypher = ", ".join([f"n.{p}" for p in prop_names])
            query = f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS FOR (n:`{label}`) REQUIRE ({prop_cypher}) IS UNIQUE"
            queries.append(query)

        if not queries:
            self.log.info(f"No schema (indexes/constraints) defined for model.")
            return

        self.log.info(f"Applying schema for model...")
        for query in queries:
            self.log.debug("Executing schema query", extra={"schema_query": query})
            await connection.run(query, tx=tx)
        self.log.info(f"Schema applied successfully.")

    async def create(self, **kwargs: Any) -> "Node":
        # ### ZMIANA ###: Logowanie operacji
        self.log.debug("Create operation started.", extra={"initial_data": kwargs})        
        
        node_instance = self.model.model_validate(kwargs)

        # --- Wywołanie hooka pre_save ---
        await node_instance.pre_save(is_creating=True)

        params = node_instance.model_dump(
            mode="json", exclude=self.model._relationships.keys()
        )
        node_alias = "node"
        labels = LABEL_TYPE_MARKER + LABEL_TYPE_MARKER.join(self.model.labels())
        set_clauses = [f"{node_alias}.{key}=${key}" for key in params.keys()]
        set_statement = "SET " + ", ".join(set_clauses) if set_clauses else ""
        query = (
            f"CREATE ({node_alias}{labels}) {set_statement} "
            f"RETURN {node_alias}, elementId({node_alias}) as internal_id"
        )
        result = await connection.run(query, params)
        if not result:
            self.log.error("Node creation failed in database, no result returned.")
            raise RuntimeError("Node creation failed in database, no result returned.")

        # Nawadniamy instancję z bazy, żeby mieć _internal_id
        hydrated_instance = self._hydrate_node(result[0])
        # Przenosimy stan z oryginalnej instancji, jeśli zaszły zmiany w pre_save
        for field in node_instance.model_fields_set:
            setattr(hydrated_instance, field, getattr(node_instance, field))

        # --- Wywołanie hooka post_save ---
        await hydrated_instance.post_save(is_creating=True)

        # ### ZMIANA ###: Logowanie sukcesu
        self.log.info(
            "Node created successfully.",
            extra={"node_uid": str(hydrated_instance.uid)},
        )

        return hydrated_instance

    async def match_one(
        self, filters: dict | Q, prefetch: list[str] | None = None
    ) -> Optional["Node"]:
        if not filters:
            raise ValueError("Metoda match_one wymaga podania filtrów.")

        node_alias = "node"
        labels = LABEL_TYPE_MARKER + LABEL_TYPE_MARKER.join(self.model.labels())
        where_clause, params = self._where_statement(node_alias, filters)

        builder = ReturnQueryBuilder(node_alias, self.model, prefetch)
        return_clause = builder.build()

        query = f"MATCH ({node_alias}{labels}) {where_clause} {return_clause} LIMIT 1"
        result = await connection.run(query, params)
        if not result:
            # ### ZMIANA ###: Logowanie, gdy nic nie znaleziono
            self.log.debug("match_one did not find any matching node.")
            return None

        return self._hydrate_prefetched(result[0]["node"])

    async def match_all(
        self,
        filters: dict | Q | None = None,
        prefetch: list[str] | None = None,
        order_by: list[str] | None = None,
    ) -> list["Node"]:
        filters = filters or {}
        node_alias = "node"
        labels = LABEL_TYPE_MARKER + LABEL_TYPE_MARKER.join(self.model.labels())
        where_clause, params = self._where_statement(node_alias, filters)

        builder = ReturnQueryBuilder(node_alias, self.model, prefetch)
        return_clause = builder.build()

        orderby_clause = (
            self._orderby_statement(node_alias, order_by) if order_by else ""
        )

        query = (
            f"MATCH ({node_alias}{labels}) {where_clause} "
            f"{return_clause} "
            f"{orderby_clause}"
        )
        result_set = await connection.run(query, params)

        # ### ZMIANA ###: Logowanie liczby znalezionych obiektów
        self.log.debug(f"match_all found {len(result_set)} nodes.")

        return [self._hydrate_prefetched(record["node"]) for record in result_set]

    async def update(self, filters: dict | Q, data: dict) -> int:
        if not filters:
            raise ValueError("Metoda update wymaga podania filtrów...")
        if not data:
            self.log.warning("Update called with empty data, no action taken.")
            return 0

        # ### ZMIANA ###: Logowanie operacji
        self.log.debug(
            "Update operation started.", extra={"filters": filters, "update_data": data}
        )

        nodes_to_update = await self.match_all(filters=filters)
        if not nodes_to_update:
            self.log.info("Update operation found no nodes to update.")
            return 0

        self.log.info(f"Found {len(nodes_to_update)} nodes to update.")

        active_tx = _current_transaction.get()
        if active_tx:
            updated_count = await self._perform_update(nodes_to_update, data, active_tx)
        else:
            async with connection.transaction() as tx:
                updated_count = await self._perform_update(nodes_to_update, data, tx)
        
        # ### ZMIANA ###: Logowanie wyniku
        self.log.info(f"Successfully updated {updated_count} nodes.")
        return updated_count

    async def _perform_update(
        self, nodes: list["Node"], data: dict, tx: "AsyncTransaction"
    ) -> int:
        """Wewnętrzna metoda wykonująca logikę aktualizacji w ramach danej transakcji."""
        updated_count = 0
        for node_instance in nodes:
            self.log.debug("Updating node", extra={"node_uid": str(node_instance.uid)})
            for key, value in data.items():
                setattr(node_instance, key, value)

            await node_instance.pre_save(is_creating=False)

            update_params = node_instance.model_dump(
                mode="json", exclude={"uid", *self.model._relationships.keys()}
            )
            query = "MATCH (node) WHERE elementId(node) = $element_id SET node += $data"
            await connection.run(
                query,
                {"element_id": node_instance._internal_id, "data": update_params},
                tx=tx,
            )

            await node_instance.post_save(is_creating=False)
            updated_count += 1
        return updated_count
        # +++ KONIEC POPRAWKI +++

    async def delete(self, filters: dict | Q) -> int:
        if not filters:
            raise ValueError("Metoda delete wymaga podania filtrów...")

        self.log.debug("Delete operation started.", extra={"filters": filters})

        nodes_to_delete = await self.match_all(filters=filters)
        if not nodes_to_delete:
            self.log.info("Delete operation found no nodes to delete.")
            return 0
            
        self.log.info(f"Found {len(nodes_to_delete)} nodes to delete.")

        active_tx = _current_transaction.get()
        if active_tx:
            deleted_count = await self._perform_delete(nodes_to_delete, active_tx)
        else:
            async with connection.transaction() as tx:
                deleted_count = await self._perform_delete(nodes_to_delete, tx)
        
        self.log.info(f"Successfully deleted {deleted_count} nodes.")
        return deleted_count

    async def _perform_delete(self, nodes: list["Node"], tx: "AsyncTransaction") -> int:
        deleted_count = 0
        for node_instance in nodes:
            self.log.debug("Deleting node", extra={"node_uid": str(node_instance.uid)})
            await node_instance.pre_delete()
            query = (
                "MATCH (node) WHERE elementId(node) = $element_id DETACH DELETE node"
            )
            await connection.run(
                query, {"element_id": node_instance._internal_id}, tx=tx
            )
            await node_instance.post_delete()
            deleted_count += 1
        return deleted_count

    async def get_or_create(
        self, filters: dict, defaults: dict | None = None
    ) -> tuple["Node", bool]:
        self.log.debug("get_or_create operation started.", extra={"filters": filters, "defaults": defaults})
        
        found_node = await self.match_one(filters)
        if found_node:
            self.log.info("get_or_create found an existing node.", extra={"node_uid": str(found_node.uid)})
            return found_node, False

        self.log.info("get_or_create did not find a node, creating a new one.")
        create_data = filters.copy()
        if defaults:
            create_data.update(defaults)

        new_node = await self.create(**create_data) # Logowanie jest już w .create()
        return new_node, True

    async def update_or_create(
        self, filters: dict, defaults: dict
    ) -> tuple["Node", bool]:
        self.log.debug("update_or_create operation started.", extra={"filters": filters, "defaults": defaults})
        
        found_node = await self.match_one(filters)

        if found_node:
            self.log.info("update_or_create found an existing node, updating it.", extra={"node_uid": str(found_node.uid)})
            await self.update(filters={"uid": str(found_node.uid)}, data=defaults)
            updated_node = await self.match_one(filters={"uid": str(found_node.uid)})
            return updated_node, False
        else:
            self.log.info("update_or_create did not find a node, creating a new one.")
            create_data = {**filters, **defaults}
            new_node = await self.create(**create_data)
            return new_node, True

    async def count(self, filters: dict | Q | None = None) -> int:
        # Logowanie jest w connection.run
        filters = filters or {}
        node_alias = "node"
        labels = LABEL_TYPE_MARKER + LABEL_TYPE_MARKER.join(self.model.labels())
        where_clause, params = self._where_statement(node_alias, filters)

        query = (
            f"MATCH ({node_alias}{labels}) {where_clause} "
            f"RETURN count({node_alias}) as count"
        )
        result = await connection.run(query, params)
        count = result[0]["count"] if result else 0
        self.log.debug(f"Count operation returned {count}.")
        return count


    async def aggregate(self, filters: dict | None = None, **aggregations: str) -> dict:
        if not aggregations:
            raise ValueError(
                "Metoda aggregate wymaga podania co najmniej jednej agregacji."
            )

        filters = filters or {}
        node_alias = "node"
        labels = LABEL_TYPE_MARKER + LABEL_TYPE_MARKER.join(self.model.labels())
        where_clause, params = self._where_statement(node_alias, filters)

        return_clauses = []
        for key, func in aggregations.items():
            if f"{node_alias}." not in func:
                func = func.replace("(", f"({node_alias}.", 1)
            return_clauses.append(f"{func} as {key}")

        return_statement = "RETURN " + ", ".join(return_clauses)

        query = f"MATCH ({node_alias}{labels}) {where_clause} {return_statement}"

        self.log.debug("Aggregate operation started.", extra={"aggregations": aggregations})
        result = await connection.run(query, params)
        data = result[0] if result else {}
        self.log.debug("Aggregate operation finished.", extra={"result": data})
        return data


    async def bulk_create(self, data: list[dict]) -> list["Node"]:
        """
        Tworzy wiele węzłów w jednym zapytaniu za pomocą UNWIND.
        W pełni wspiera haki pre_save i post_save.

        :param data: Lista słowników, gdzie każdy słownik to dane dla jednego węzła.
        :return: Lista utworzonych i nawodnionych instancji węzłów.
        """
        if not data:
            return []

        self.log.info(f"Starting bulk_create for {len(data)} nodes.")

        
        # Krok 1: Walidacja i wywołanie haków pre_save
        instances_to_create: list["Node"] = []
        props_list: list[dict] = []
        for item_data in data:
            instance = self.model.model_validate(item_data)
            await instance.pre_save(is_creating=True)
            instances_to_create.append(instance)
            # Upewniamy się, że uid jest stringiem dla JSON
            props = instance.model_dump(
                mode="json", exclude=self.model._relationships.keys()
            )
            props_list.append(props)

        # Krok 2: Przygotowanie i wykonanie zapytania UNWIND
        node_alias = "node"
        labels = LABEL_TYPE_MARKER + LABEL_TYPE_MARKER.join(self.model.labels())

        query = f"""
        UNWIND $props_list as props
        CREATE ({node_alias}{labels})
        SET {node_alias} = props
        RETURN {node_alias}, elementId({node_alias}) as internal_id
        """

        result_set = await connection.run(query, {"props_list": props_list})
        if not result_set:
            self.log.warning("bulk_create did not return any created nodes from DB.")
            return []


        # Krok 3: Hydratacja i wywołanie haków post_save
        created_nodes: list["Node"] = []
        for record in result_set:
            hydrated_node = self._hydrate_node(record)
            await hydrated_node.post_save(is_creating=True)
            created_nodes.append(hydrated_node)

        self.log.info(f"Successfully finished bulk_create, created {len(created_nodes)} nodes.")
        return created_nodes

    async def bulk_update(self, data: list[dict], match_on: str = "uid") -> int:
        """
        Aktualizuje wiele węzłów w jednym zapytaniu za pomocą UNWIND.
        Wspiera haki pre_save i post_save.

        :param data: Lista słowników. Każdy słownik MUSI zawierać klucz określony
                     przez `match_on` (domyślnie 'uid') oraz pola do aktualizacji.
        :param match_on: Klucz używany do znalezienia węzła do aktualizacji.
        :return: Liczba zaktualizowanych węzłów.
        """
        self.log.info(f"Starting bulk_update for {len(data)} nodes, matching on '{match_on}'.")
        if not data:
            self.log.warning("bulk_update called with empty data, no action taken.")
            return 0

        # Krok 1: Pobranie obiektów i wywołanie haków pre_save
        match_values = [item[match_on] for item in data]
        nodes_to_update = await self.match_all(
            filters={f"{match_on}__in": match_values}
        )

        # Mapowanie uid -> instance dla łatwego dostępu
        node_map = {str(getattr(node, match_on)): node for node in nodes_to_update}

        props_list = []
        for item_data in data:
            match_value = str(item_data.get(match_on))
            instance = node_map.get(match_value)

            if not instance:
                self.log.warning(
                    f"Node not found for bulk_update.",
                    extra={"match_on": match_on, "match_value": match_value}
                )
                continue


            # Aktualizacja pól na instancji i wywołanie pre_save
            update_payload = {k: v for k, v in item_data.items() if k != match_on}
            for key, value in update_payload.items():
                setattr(instance, key, value)

            await instance.pre_save(is_creating=False)

            # Zbieramy dane do zapytania
            props_list.append(
                instance.model_dump(
                    mode="json", exclude=self.model._relationships.keys()
                )
            )

        if not props_list:
            self.log.info("No valid nodes to update after filtering in bulk_update.")
            return 0

        # Krok 2: Wykonanie zapytania UNWIND
        node_alias = "node"
        labels = LABEL_TYPE_MARKER + LABEL_TYPE_MARKER.join(self.model.labels())

        query = f"""
        UNWIND $props_list as props
        MATCH ({node_alias}{labels} {{ {match_on}: props.{match_on} }})
        SET {node_alias} += props
        RETURN count({node_alias}) as updated_count
        """

        result = await connection.run(query, {"props_list": props_list})
        updated_count = result[0]["updated_count"] if result else 0

        # Krok 3: Wywołanie haków post_save
        for item_data in data:
            match_value = str(item_data.get(match_on))
            instance = node_map.get(match_value)
            if instance:
                await instance.post_save(is_creating=False)

        self.log.info(f"Successfully finished bulk_update, updated {updated_count} nodes.")
        return updated_count


    async def connect(
        self,
        from_node_uid: uuid.UUID,
        to_node_uid: uuid.UUID,
        rel_type: str,
        properties: dict | None = None,
    ):
        # Logowanie jest w connection.run
        self.log.debug(
            f"Connecting nodes.",
            extra={
                "from_uid": str(from_node_uid),
                "to_uid": str(to_node_uid),
                "rel_type": rel_type,
            }
        )
        query = """
        MATCH (a), (b)
        WHERE a.uid = $from_uid AND b.uid = $to_uid
        CREATE (a)-[r:`{rel_type}`]->(b)
        SET r += $props
        RETURN r
        """.format(rel_type=rel_type)
        params = {
            "from_uid": str(from_node_uid),
            "to_uid": str(to_node_uid),
            "props": properties or {},
        }
        await connection.run(query, params)

    async def disconnect(
        self, from_node_uid: uuid.UUID, to_node_uid: uuid.UUID, rel_type: str
    ):
        # Logowanie jest w connection.run
        self.log.debug(
            f"Disconnecting nodes.",
            extra={
                "from_uid": str(from_node_uid),
                "to_uid": str(to_node_uid),
                "rel_type": rel_type,
            }
        )
        query = """
        MATCH (a)-[r:`{rel_type}`]->(b)
        WHERE a.uid = $from_uid AND b.uid = $to_uid
        DELETE r
        """.format(rel_type=rel_type)
        params = {"from_uid": str(from_node_uid), "to_uid": str(to_node_uid)}
        await connection.run(query, params)

    async def update_relationship(
        self,
        from_node_uid: uuid.UUID,
        to_node_uid: uuid.UUID,
        rel_type: str,
        properties: dict,
    ):
        if not properties:
            return

        self.log.debug(
            f"Updating relationship.",
            extra={
                "from_uid": str(from_node_uid),
                "to_uid": str(to_node_uid),
                "rel_type": rel_type,
                "properties": properties,
            }
        )

        query = """
        MATCH (a)-[r:`{rel_type}`]->(b)
        WHERE a.uid = $from_uid AND b.uid = $to_uid
        SET r += $props
        RETURN r
        """.format(rel_type=rel_type)
        params = {
            "from_uid": str(from_node_uid),
            "to_uid": str(to_node_uid),
            "props": properties,
        }
        await connection.run(query, params)

    def _hydrate_prefetched(self, data: dict) -> "Node":
        return self._hydrate_recursive(self.model, data)

    def _hydrate_recursive(self, model_class: Type["Node"], node_data: dict) -> "Node":
        fields_to_validate = {}
        prefetched_rels = {}
        internal_id = node_data.pop("_internal_id", None)

        for key, value in node_data.items():
            if key in model_class._relationships:
                rel_descriptor = model_class._relationships[key]
                target_model_class = node_registry.get(rel_descriptor.target_node_label)
                if not target_model_class:
                    raise TypeError(
                        f"Nie znaleziono modelu dla etykiety '{rel_descriptor.target_node_label}'"
                    )

                # +++ WYWOŁANIE KONWERSJI DLA DANYCH RELACJI +++
                # Robimy to tutaj, aby mieć pewność, że właściwości na relacjach też są konwertowane
                value = _convert_neo4j_temporals(value)
                
                hydrated_rel_list = []
                for rel_map in value:
                    nested_node_data = rel_map.get("node")
                    rel_props_data = rel_map.get("rel", {})

                    if not nested_node_data:
                        continue

                    rel_node = self._hydrate_recursive(
                        target_model_class, nested_node_data
                    )

                    if rel_descriptor.model:
                        hydrated_props = rel_descriptor.model.model_validate(
                            rel_props_data
                        )
                    else:
                        hydrated_props = rel_props_data

                    hydrated_rel_list.append((rel_node, hydrated_props))

                prefetched_rels[rel_descriptor.private_name] = hydrated_rel_list
            else:
                fields_to_validate[key] = value

        # +++ WYWOŁANIE KONWERSJI PRZED WALIDACJĄ PYDANTIC +++
        fields_to_validate = _convert_neo4j_temporals(fields_to_validate)
        
        node_instance = model_class.model_validate(fields_to_validate)
        if internal_id:
            node_instance._internal_id = internal_id

        for private_name, rel_list in prefetched_rels.items():
            setattr(node_instance, private_name, rel_list)

        return node_instance

    def _orderby_statement(self, node_alias: str, fields: list[str]) -> str:
        if not fields:
            return ""
        clauses = [
            f"{node_alias}.`{f[1:]}` DESC"
            if f.startswith("-")
            else f"{node_alias}.`{f}` ASC"
            for f in fields
        ]
        return "ORDER BY " + ", ".join(clauses)

    def _where_statement(self, node_alias: str, filters: dict | Q) -> tuple[str, dict]:
        """
        Tłumaczy słownik filtrów lub obiekt Q na klauzulę WHERE i parametry.
        """
        if not filters:
            return "", {}

        q_obj = filters if isinstance(filters, Q) else Q(**filters)

        # Licznik do generowania unikalnych nazw parametrów
        param_counter = [0]
        cypher, params = q_obj.to_cypher(node_alias, param_counter)

        if not cypher:
            return "", {}

        return f"WHERE {cypher}", params


# ReturnQueryBuilder i reszta pomocniczych klas i metod pozostają bez zmian


class ReturnQueryBuilder:
    def __init__(
        self,
        node_alias: str,
        model: Type["Node"],
        prefetch: Optional[list[str] | dict] = None,
    ):
        self.node_alias = node_alias
        self.model = model
        if isinstance(prefetch, list):
            self.prefetch = {key: {} for key in prefetch}
        else:
            self.prefetch = prefetch or {}

    def build(self) -> str:
        projection_body = self._build_projection_for_model(
            self.model, self.node_alias, self.prefetch
        )
        return f"RETURN {projection_body} AS node"

    def _build_projection_for_model(
        self, model_class: Type["Node"], alias: str, prefetch_config: dict
    ) -> str:
        parts = [".*", f"_internal_id: elementId({alias})"]
        for field_name, nested_prefetch in prefetch_config.items():
            rel_descriptor = model_class._relationships.get(field_name)
            if rel_descriptor is None:
                raise ValueError(
                    f"'{field_name}' nie jest poprawną relacją w modelu '{model_class.__name__}'"
                )
            comprehension = self._build_comprehension_for_rel(
                alias, rel_descriptor, nested_prefetch
            )
            parts.append(f"{field_name}: {comprehension}")
        return f"{alias} {{ {', '.join(parts)} }}"

    def _build_comprehension_for_rel(
        self, parent_alias: str, rel: "RelationshipProperty", prefetch_config: dict
    ) -> str:
        target_model_class = node_registry.get(rel.target_node_label)
        if not target_model_class:
            raise TypeError(
                f"Nie znaleziono modelu dla etykiety '{rel.target_node_label}'"
            )

        target_alias = f"_{parent_alias}_{rel.private_name.strip('_')}"
        target_projection = self._build_projection_for_model(
            target_model_class, target_alias, prefetch_config
        )

        rel_alias = f"r_{target_alias}"
        rel_pattern_body = f"[{rel_alias}:`{rel.relationship_type}`]"

        if rel.relationship_direction == RelationshipDirection.IN:
            path_pattern = f"<-{rel_pattern_body}-"
        elif rel.relationship_direction == RelationshipDirection.OUT:
            path_pattern = f"-{rel_pattern_body}->"
        else:
            path_pattern = f"-{rel_pattern_body}-"

        full_path = f"({parent_alias}){path_pattern}{rel.target_node_pattern(alias=target_alias)}"

        return (
            f"[{full_path} | {{ rel: {rel_alias} {{.*}}, node: {target_projection} }}]"
        )
