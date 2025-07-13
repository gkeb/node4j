# node4j/ext/gds.py
import logging  # ### ZMIANA ###
from node4j.db import connection
from typing import Any

# ### ZMIANA ###: Inicjalizacja loggera dla modułu
log = logging.getLogger(__name__)


class GDS:
    """
    Przestrzeń nazw dla funkcji pomocniczych opakowujących procedury Graph Data Science.
    """

    class Graph:
        @staticmethod
        async def project(
            graph_name: str, node_projection: Any, relationship_projection: Any
        ) -> dict:
            """
            Tworzy projekcję grafu w pamięci.
            https://neo4j.com/docs/graph-data-science/current/management/graph-project/
            """
            # ### ZMIANA ###: Logowanie operacji
            log.info(
                f"Projecting GDS graph '{graph_name}'.",
                extra={
                    "node_projection": node_projection,
                    "relationship_projection": relationship_projection,
                },
            )
            query = "CALL gds.graph.project($graph_name, $node_projection, $relationship_projection)"
            result = await connection.run(
                query,
                {
                    "graph_name": graph_name,
                    "node_projection": node_projection,
                    "relationship_projection": relationship_projection,
                },
            )
            res_data = result[0] if result else {}
            log.info(f"GDS graph '{graph_name}' projected successfully.", extra=res_data)
            return res_data

        @staticmethod
        async def drop(graph_name: str) -> dict:
            """Usuwa projekcję grafu z pamięci."""
            # ### ZMIANA ###: Logowanie operacji
            log.info(f"Dropping GDS graph '{graph_name}'.")
            query = "CALL gds.graph.drop($graph_name)"
            result = await connection.run(query, {"graph_name": graph_name})
            res_data = result[0] if result else {}
            log.info(f"GDS graph '{graph_name}' dropped successfully.", extra=res_data)
            return res_data

    class Algo:
        @staticmethod
        async def run(graph_name: str, algo: str, config: dict) -> list[dict]:
            """
            Uruchamia algorytm GDS (np. PageRank) w trybie `stream`.
            Przykład algo: 'gds.pageRank.stream'
            """
            # ### ZMIANA ###: Logowanie operacji
            log.info(
                f"Running GDS algorithm '{algo}' in stream mode on graph '{graph_name}'.",
                extra={"config": config},
            )
            # Budujemy dynamicznie zapytanie
            # UWAGA: YIELD może zwracać różne kolumny, więc na razie logujemy ogólnie
            query = f"CALL {algo}($graph_name, $config)" # Usunięto YIELD dla ogólności
            params = {"graph_name": graph_name, "config": config}
            result = await connection.run(query, params)
            log.info(f"GDS algorithm '{algo}' finished, returned {len(result)} records.")
            return result

        @staticmethod
        async def mutate(graph_name: str, algo: str, config: dict) -> dict:
            """
            Uruchamia algorytm GDS i zapisuje wyniki z powrotem do grafu.
            Przykład algo: 'gds.pageRank.mutate'
            """
            # ### ZMIANA ###: Logowanie operacji
            log.info(
                f"Running GDS algorithm '{algo}' in mutate mode on graph '{graph_name}'.",
                extra={"config": config},
            )
            query = f"CALL {algo}($graph_name, $config)"
            params = {"graph_name": graph_name, "config": config}
            result = await connection.run(query, params)
            res_data = result[0] if result else {}
            log.info(f"GDS algorithm '{algo}' mutation finished.", extra=res_data)
            return res_data


# Tworzymy instancję, aby mieć łatwy dostęp
gds = GDS()