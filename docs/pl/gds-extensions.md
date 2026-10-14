# Rozszerzenia GDS

Graph Data Science (GDS) dodaje do Neo4j procedury projekcji i analizy grafów. Moduł `node4j.ext.gds` opakowuje projekcję i usuwanie grafów oraz wywołania algorytmów w trybach stream i mutate.

Language: [English](../en/gds-extensions.md) · [README](../../README_PL.md).

## Obsługiwane wersje

Użyj wydania GDS zgodnego z serwerem Neo4j. Przykłady projektu są testowane z następującymi parami Community Edition:

| Neo4j | GDS |
| --- | --- |
| 5.26 LTS | 2.13 |
| 2026.09 | 2026.09 |

Pozostałe wersje sprawdzisz w [oficjalnej macierzy zgodności](https://neo4j.com/docs/graph-data-science/current/installation/supported-neo4j-versions/).

## Instalacja pluginu GDS

GDS działa wewnątrz Neo4j. W Neo4j Desktop zainstaluj zgodny plugin GDS na karcie Plugins. W oficjalnym obrazie Dockera dodaj GDS przy uruchamianiu. Testowa baza projektu używa także APOC:

```yaml
services:
  neo4j:
    image: neo4j:2026.09.0
    environment:
      NEO4J_AUTH: neo4j/change-me
      NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
```

Instalator pluginów Dockera to ułatwienie dla środowisk deweloperskich, którego nie zaleca się w produkcji. W produkcji zainstaluj wydanie pluginu GDS zgodne z Neo4j; skorzystaj z [oficjalnego przewodnika instalacji w Dockerze](https://neo4j.com/docs/graph-data-science/current/installation/installation-docker/). Przykład używa też APOC `apoc.create.addLabels`, aby nadać etykietę unikalną dla danego uruchomienia, dlatego zainstaluj także APOC.

## Projekcja grafu i PageRank

Algorytmy GDS działają na nazwanych, przechowywanych w pamięci projekcjach grafu. Ten przykład tworzy dwa syntetyczne węzły i relację, nadaje im unikalną etykietę dla tego uruchomienia, projektuje je, uruchamia PageRank w trybie stream, a potem mutate, usuwa projekcję i węzły.

```python
from uuid import uuid4

from node4j.db import connection
from node4j.ext.gds import gds
from node4j.nodes import Node


class GuideGDSNode(Node):
    marker: str


suffix = uuid4().hex
graph_name = f"node4j_guide_{suffix}"
PAGE_RANK_STREAM = "gds.pageRank.stream"
PAGE_RANK_MUTATE = "gds.pageRank.mutate"
projection_label = f"GuideGDSNode_{suffix}"
source = None
target = None
projection_created = False
try:
    source = await GuideGDSNode.q.create(marker=f"source_{suffix}")
    target = await GuideGDSNode.q.create(marker=f"target_{suffix}")

    await connection.run(
        "MATCH (source), (target) "
        "WHERE source.`uid` = $source_uid AND target.`uid` = $target_uid "
        "CREATE (source)-[:`LINKS_TO`]->(target) "
        "WITH source, target "
        "CALL apoc.create.addLabels([source, target], [$projection_label]) "
        "YIELD node RETURN count(node)",
        {
            "source_uid": str(source.uid),
            "target_uid": str(target.uid),
            "projection_label": projection_label,
        },
    )

    projected = await gds.Graph.project(
        graph_name,
        projection_label,
        {"LINKS_TO": {"orientation": "UNDIRECTED"}},
    )
    projection_created = True
    assert projected["nodeCount"] == 2, projected
    assert projected["relationshipCount"] == 2, projected

    scores = await gds.Algo.run(
        graph_name,
        PAGE_RANK_STREAM,
        {"maxIterations": 20, "dampingFactor": 0.85},
    )
    assert len(scores) == 2
    assert {"nodeId", "score"} <= set(scores[0])

    mutation = await gds.Algo.mutate(
        graph_name,
        PAGE_RANK_MUTATE,
        {
            "mutateProperty": "guide_page_rank",
            "maxIterations": 20,
            "dampingFactor": 0.85,
        },
    )
    assert mutation["nodePropertiesWritten"] == 2

    dropped = await gds.Graph.drop(graph_name)
    projection_created = False
    assert dropped["graphName"] == graph_name
finally:
    try:
        if projection_created:
            await gds.Graph.drop(graph_name)
    finally:
        uids = [str(node.uid) for node in (source, target) if node is not None]
        if uids:
            await connection.run(
                "MATCH (node) WHERE node.`uid` IN $uids DETACH DELETE node",
                {"uids": uids},
            )
```

`gds.Algo.run` zwraca wiersze z wynikami algorytmu stream. `mutate` zapisuje skonfigurowaną właściwość w projekcji przechowywanej w pamięci; nie zapisuje jej we właściwościach węzłów Neo4j. Projekcja jest oddzielona od zapisanych węzłów i relacji, więc jej usunięcie nie kasuje danych bazy.

Wrapper wstawia nazwę algorytmu do tekstu Cyphera. Przekazuj stałą z kodu aplikacji, jak w przykładzie; nigdy nie używaj nazwy algorytmu podanej przez użytkownika. Konfiguracja trafia jako parametr zapytania.

`gds.Graph.drop` zgłasza błąd Neo4j, gdy nazwana projekcja nie istnieje, ponieważ GDS domyślnie używa `failIfMissing=true`. Wrapper nie udostępnia tej opcji. Zobacz [referencję GDS o usuwaniu grafu](https://neo4j.com/docs/graph-data-science/current/management-ops/graph-drop/).
