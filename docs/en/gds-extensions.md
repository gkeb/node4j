# GDS extensions

Graph Data Science (GDS) adds graph projection and analytics procedures to Neo4j. The `node4j.ext.gds` module wraps graph projection and removal, plus algorithm calls in stream and mutate modes.

Language: [Polski](../pl/gds-extensions.md) · [README](../../README.md).

## Supported versions

Use a GDS release that matches the Neo4j server. The project examples are tested with these Community Edition pairs:

| Neo4j | GDS |
| --- | --- |
| 5.26 LTS | 2.13 |
| 2026.09 | 2026.09 |

See the [official compatibility matrix](https://neo4j.com/docs/graph-data-science/current/installation/supported-neo4j-versions/) for other versions.

## Install the GDS plugin

GDS runs inside Neo4j. In Neo4j Desktop, install the matching GDS plugin from the Plugins tab. For the official Docker image, list GDS at startup. The project test database also uses APOC:

```yaml
services:
  neo4j:
    image: neo4j:2026.09.0
    environment:
      NEO4J_AUTH: neo4j/change-me
      NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
```

The Docker plugin installer is a development convenience and is not recommended for production. For production, install the GDS plugin release that matches Neo4j; follow the [official Docker installation guide](https://neo4j.com/docs/graph-data-science/current/installation/installation-docker/). This example also uses APOC's `apoc.create.addLabels` to assign a per-run label, so install APOC as well.

## Project a graph and run PageRank

GDS algorithms operate on named, in-memory graph projections. This example creates two synthetic nodes and a relationship, gives them a unique label for this run, projects them, runs PageRank in stream mode, then in mutate mode, drops the projection, and deletes the nodes.

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

`gds.Algo.run` returns the algorithm's stream rows. `mutate` writes the configured property to the in-memory projection; it does not write that property to Neo4j nodes. A projection is separate from the stored nodes and relationships, so dropping it does not delete database data.

The algorithm name is inserted into Cypher text by the wrapper. Keep it as a constant from application code, as above; never pass a user-provided algorithm name. The configuration is passed as a query parameter.

`gds.Graph.drop` raises a Neo4j error if the named projection does not exist because GDS uses `failIfMissing=true` by default. The wrapper does not expose that option. See the [GDS graph drop reference](https://neo4j.com/docs/graph-data-science/current/management-ops/graph-drop/).
