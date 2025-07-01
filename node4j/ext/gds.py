# node4j/ext/gds.py

from node4j.db import connection
from typing import Any


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
            query = "CALL gds.graph.project($graph_name, $node_projection, $relationship_projection)"
            result = await connection.run(
                query,
                {
                    "graph_name": graph_name,
                    "node_projection": node_projection,
                    "relationship_projection": relationship_projection,
                },
            )
            return result[0] if result else {}

        @staticmethod
        async def drop(graph_name: str) -> dict:
            """Usuwa projekcję grafu z pamięci."""
            query = "CALL gds.graph.drop($graph_name)"
            result = await connection.run(query, {"graph_name": graph_name})
            return result[0] if result else {}

    class Algo:
        @staticmethod
        async def run(graph_name: str, algo: str, config: dict) -> list[dict]:
            """
            Uruchamia algorytm GDS (np. PageRank) w trybie `stream`.
            Przykład algo: 'gds.pageRank.stream'
            """
            # Budujemy dynamicznie zapytanie
            query = f"CALL {algo}($graph_name, $config) YIELD nodeId, score"
            params = {"graph_name": graph_name, "config": config}
            return await connection.run(query, params)

        @staticmethod
        async def mutate(graph_name: str, algo: str, config: dict) -> dict:
            """

            Uruchamia algorytm GDS i zapisuje wyniki z powrotem do grafu.
            Przykład algo: 'gds.pageRank.mutate'
            """
            query = f"CALL {algo}($graph_name, $config)"
            params = {"graph_name": graph_name, "config": config}
            result = await connection.run(query, params)
            return result[0] if result else {}


# Tworzymy instancję, aby mieć łatwy dostęp
gds = GDS()
