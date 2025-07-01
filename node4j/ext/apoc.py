# node4j/ext/apoc.py

from __future__ import annotations
from typing import TYPE_CHECKING, Any

from node4j.db import connection

if TYPE_CHECKING:
    from ..nodes import Node

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
        result = await connection.run("RETURN apoc.version() as version")
        return result[0]["version"] if result else None

    # Tutaj można dodać inne globalne, niezwiązane z modelami funkcje,
    # np. do pracy na schematach, triggerach, itp.
    # ...

    class Periodic:
        @staticmethod
        async def iterate(
            cypher_to_iterate: str, cypher_to_execute: str, batch_size: int = 1000
        ):
            """
            Wykonuje operacje w batchach, opakowując `apoc.periodic.iterate`.
            https://neo4j.com/labs/apoc/4.4/background-operations/periodic-execution/
            """
            query = """
            CALL apoc.periodic.iterate($cypher_to_iterate, $cypher_to_execute, {batchSize: $batch_size})
            """
            params = {
                "cypher_to_iterate": cypher_to_iterate,
                "cypher_to_execute": cypher_to_execute,
                "batch_size": batch_size,
            }
            # Ta procedura nie zwraca wyników, więc nie ma `return`
            await connection.run(query, params)

    class Export:
        @staticmethod
        async def to_json(file_name: str, config: dict | None = None):
            """
            Eksportuje całą bazę do pliku JSON.
            https://neo4j.com/labs/apoc/4.4/export/json/
            """
            config = config or {}
            query = "CALL apoc.export.json.all($file_name, $config)"
            await connection.run(query, {"file_name": file_name, "config": config})

    # +++ NOWA KLASA WEWNĘTRZNA DLA TRIGGERÓW +++
    class Triggers:
        @staticmethod
        async def install(
            name: str, cypher: str, selector: dict, config: dict | None = None
        ) -> None:  # <-- Zmiana nazwy metody
            """
            Tworzy i instaluje nowy trigger w bazie danych.
            Używa `apoc.trigger.install` dla nowszych wersji APOC.

            :param name: Unikalna nazwa triggera.
            :param cypher: Zapytanie Cypher do wykonania przez trigger.
                          Może używać zmiennych jak `node`, `relationship`, `createdNodes`.
            :param selector: Słownik określający, kiedy trigger ma się uruchomić.
                           Przykład: `{"label": "Person"}`.
            :param config: Dodatkowa konfiguracja, np. `{"phase": "after"}`.
            """
            config = config or {}
            # --- POPRAWIONE ZAPYTANIE ---
            query = (
                "CALL apoc.trigger.install('neo4j', $name, $cypher, $selector, $config)"
            )
            # `install` wymaga dodatkowego pierwszego argumentu - nazwy bazy danych.
            # Dla większości przypadków będzie to 'neo4j'.
            await connection.run(
                query,
                {
                    "name": name,
                    "cypher": cypher,
                    "selector": selector,
                    "config": config,
                },
            )
            print(f"Zainstalowano trigger: '{name}'")

        @staticmethod
        async def remove(name: str) -> dict:
            """Usuwa trigger o podanej nazwie. Używa `apoc.trigger.drop`."""
            # Konsekwentnie, `remove` zostało zastąpione przez `drop`
            query = "CALL apoc.trigger.drop($name)"  # <-- POPRAWKA
            result = await connection.run(query, {"name": name})
            print(f"Usunięto trigger: '{name}'")
            return result[0] if result else {}

        @staticmethod
        async def remove_all() -> dict:
            """Usuwa wszystkie triggery z bazy. Używa `apoc.trigger.dropAll`."""
            # Analogicznie dla `removeAll`
            query = "CALL apoc.trigger.dropAll()"  # <-- POPRAWKA
            result = await connection.run(query)
            print("Usunięto wszystkie triggery.")
            return result[0] if result else {}

        @staticmethod
        async def list() -> list[dict]:
            """Zwraca listę wszystkich zainstalowanych triggerów."""
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

    async def create_from_json(
        self, file_url: str, json_path: str = "$", batch_size: int = 1000
    ) -> dict:
        """
        Wydajnie tworzy węzły na podstawie danych z pliku JSON.
        """
        labels = ":" + ":".join(self.model.labels())

        cypher_to_execute = (
            f"CREATE (n{labels}) SET n = row, n.uid = apoc.create.uuid()"
        )

        # Zamiast pisać zapytanie ręcznie, można by użyć `apoc.periodic.iterate`,
        # ale na razie dla prostoty zostawmy je w tej formie.
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
        return result[0] if result else {}

    # Tutaj można dodać inne metody specyficzne dla modelu, np. create_from_csv
    # ...


# ===================================================================
# CZĘŚĆ 3: Funkcja instalująca menedżer na modelu
# ===================================================================


def install_apoc_manager(model_class: type[Node]):
    """
    Instaluje ApocManager na klasie modelu jako atrybut `.apoc`.
    """
    if not hasattr(model_class, "apoc"):
        model_class.apoc = ApocManager(model_class)
