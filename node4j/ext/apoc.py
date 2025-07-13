# node4j/ext/apoc.py
from __future__ import annotations
from typing import TYPE_CHECKING, Any
import logging  # ### ZMIANA ###

from node4j.db import connection

if TYPE_CHECKING:
    from ..nodes import Node

# ### ZMIANA ###: Inicjalizacja loggera dla modułu
log = logging.getLogger(__name__)

# ===================================================================
# CZĘŚĆ 1: Globalna biblioteka pomocnicza dla procedur APOC
# ===================================================================


class APOC:
    """
    Przestrzeń nazw dla funkcji pomocniczych opakowujących ogólne procedury APOC.
    Dostęp: `from node4j.ext.apoc import apoc`
    """

    @staticmethod
    async def version() -> str | None:
        """Zwraca wersję zainstalowanej biblioteki APOC."""
        log.debug("Fetching APOC version.")
        result = await connection.run("RETURN apoc.version() as version")
        version = result[0]["version"] if result else None
        if version:
            log.info(f"APOC version found: {version}")
        else:
            log.warning("Could not determine APOC version.")
        return version

    # Tutaj można dodać inne globalne, niezwiązane z modelami funkcje,
    # np. do pracy na schematach, triggerach, itp.
    # ...

    class Periodic:
        @staticmethod
        async def iterate(
            cypher_to_iterate: str, cypher_to_execute: str, batch_size: int = 1000
        ):
            """Wykonuje operacje w batchach, opakowując `apoc.periodic.iterate`."""
            log.info(
                "Executing periodic iterate.",
                extra={"batch_size": batch_size, "iterate_query": cypher_to_iterate},
            )
            query = "CALL apoc.periodic.iterate($cypher_to_iterate, $cypher_to_execute, {batchSize: $batch_size})"
            params = {
                "cypher_to_iterate": cypher_to_iterate,
                "cypher_to_execute": cypher_to_execute,
                "batch_size": batch_size,
            }
            await connection.run(query, params)
            log.info("Periodic iterate finished.")


    class Export:
        @staticmethod
        async def to_json(file_name: str, config: dict | None = None):
            """Eksportuje całą bazę do pliku JSON."""
            log.info(f"Exporting database to JSON file.", extra={"file_name": file_name, "config": config})
            config = config or {}
            query = "CALL apoc.export.json.all($file_name, $config)"
            await connection.run(query, {"file_name": file_name, "config": config})
            log.info(f"Database export to '{file_name}' finished.")


    # +++ NOWA KLASA WEWNĘTRZNA DLA TRIGGERÓW +++
    class Triggers:
        @staticmethod
        async def install(name: str, cypher: str, selector: dict, config: dict | None = None) -> None:
            """Tworzy i instaluje nowy trigger w bazie danych."""
            log.info(f"Installing APOC trigger '{name}'.")
            config = config or {}
            query = "CALL apoc.trigger.install('neo4j', $name, $cypher, $selector, $config)"
            await connection.run(
                query,
                {"name": name, "cypher": cypher, "selector": selector, "config": config},
            )
            # ### ZMIANA ###: Zastąpienie print loggerem
            log.info(f"Successfully installed trigger: '{name}'")


        @staticmethod
        async def remove(name: str) -> dict:
            """Usuwa trigger o podanej nazwie."""
            log.info(f"Removing APOC trigger '{name}'.")
            query = "CALL apoc.trigger.drop($name)"
            result = await connection.run(query, {"name": name})
            # ### ZMIANA ###: Zastąpienie print loggerem
            log.info(f"Successfully removed trigger: '{name}'")
            return result[0] if result else {}


        @staticmethod
        async def remove_all() -> dict:
            """Usuwa wszystkie triggery z bazy."""
            log.info("Removing all APOC triggers.")
            query = "CALL apoc.trigger.dropAll()"
            result = await connection.run(query)
            # ### ZMIANA ###: Zastąpienie print loggerem
            log.info("Successfully removed all triggers.")
            return result[0] if result else {}


        @staticmethod
        async def list() -> list[dict]:
            """Zwraca listę wszystkich zainstalowanych triggerów."""
            log.debug("Listing all APOC triggers.")
            query = "CALL apoc.trigger.list()"
            return await connection.run(query)



# Singleton - globalna instancja do łatwego importu
apoc = APOC()
apoc.Triggers = APOC.Triggers

# ===================================================================
# CZĘŚĆ 2: Menedżer operacji na modelach z użyciem APOC
# ===================================================================


class ApocManager:
    """
    Dedykowany menedżer dla operacji na modelu, które wykorzystują procedury APOC.
    Dostępny jako `Model.apoc` po instalacji.
    """

    def __init__(self, node_model: type[Node]):
        self.model = node_model
        # ### ZMIANA ###: Logger specyficzny dla modelu
        self.log = log.getChild(f"ApocManager.{self.model.__name__}")

    async def create_from_json(
        self, file_url: str, json_path: str = "$", batch_size: int = 1000
    ) -> dict:
        """Wydajnie tworzy węzły na podstawie danych z pliku JSON."""
        self.log.info(
            f"Creating nodes from JSON.",
            extra={
                "model": self.model.__name__,
                "file_url": file_url,
                "json_path": json_path,
                "batch_size": batch_size,
            },
        )
        labels = ":" + ":".join(self.model.labels())
        cypher_to_execute = f"CREATE (n{labels}) SET n = row, n.uid = apoc.create.uuid()"

        query = """
        CALL apoc.periodic.iterate(
            'CALL apoc.load.json($url, $path) YIELD value as row RETURN row',
            $cypher_to_execute,
            {batchSize: $batch_size, parallel: false}
        )
        """
        params = {
            "url": file_url,
            "path": json_path,
            "cypher_to_execute": cypher_to_execute,
            "batch_size": batch_size,
        }

        result = await connection.run(query, params)
        self.log.info(f"Finished creating nodes from JSON.", extra={"result": result})
        return result[0] if result else {}

    # Tutaj można dodać inne metody specyficzne dla modelu, np. create_from_csv
    # ...


# ===================================================================
# CZĘŚĆ 3: Funkcja instalująca menedżer na modelu
# ===================================================================


def install_apoc_manager(model_class: type[Node]):
    """Instaluje ApocManager na klasie modelu jako atrybut `.apoc`."""
    if not hasattr(model_class, "apoc"):
        # ### ZMIANA ###: Dodajemy logowanie instalacji
        manager_log = log.getChild(f"ApocManager.{model_class.__name__}")
        manager_log.debug("Installing ApocManager on model.")
        model_class.apoc = ApocManager(model_class)

