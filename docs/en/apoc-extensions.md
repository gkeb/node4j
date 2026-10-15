# APOC extensions

APOC adds procedures and functions to the Neo4j server. The `node4j.ext.apoc` module wraps a small set of them: version lookup, batched Cypher, JSON export, and JSON-based node creation.

Language: [Polski](../pl/apoc-extensions.md) · [README](../../README.md).

## Install the APOC plugin

APOC runs inside Neo4j, so install a plugin version compatible with your Neo4j server. In Neo4j Desktop, install APOC from the Plugins tab. For the official Docker image, list the plugin at startup:

```yaml
services:
  neo4j:
    image: neo4j:2026.09.0
    environment:
      NEO4J_AUTH: neo4j/change-me
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_apoc_import_file_enabled: "true"
      NEO4J_apoc_export_file_enabled: "true"
```

The import and export flags enable server-side file access. In Docker, these are `NEO4J_apoc_import_file_enabled=true` and `NEO4J_apoc_export_file_enabled=true`. The same APOC settings are used by the project's test database in CI and in [AGENTS.md](../../AGENTS.md).

Neo4j describes `NEO4J_PLUGINS` as a development convenience and does not recommend it for production. For production, install the APOC release compatible with your Neo4j version as a plugin JAR and mount it in `/plugins`; see the [official APOC installation guide](https://neo4j.com/docs/apoc/current/installation/).

## Troubleshoot missing APOC procedures

If `await apoc.version()` or another APOC call fails with `Neo.ClientError.Procedure.ProcedureNotFound`, Neo4j did not register that procedure on the connected server. The server message has this form:

```text
There is no procedure with the name `apoc.version` registered for this database instance. Please ensure you've spelled the procedure name correctly and that the procedure is properly deployed.
```

Check that APOC is installed for the Neo4j version in use, enabled, and loaded after a server restart. For Docker, see the plugin setup above; for other installations, follow the [official APOC installation guide](https://neo4j.com/docs/apoc/current/installation/). If only one APOC call is missing, check that the procedure is included in the installed APOC release.

## File access on the Neo4j server

APOC reads and writes files on the **Neo4j server**. With the default server configuration, `file:///people.json` means `people.json` in that server's import directory. A file that exists only on the Python application's computer is not available through this URL. APOC's import and export file access are disabled by default.

For a non-Docker installation, set these values in `apoc.conf` and restart Neo4j:

```properties
apoc.import.file.enabled=true
apoc.export.file.enabled=true
```

If import remains disabled, APOC reports an error similar to:

```text
Import from files not enabled, please set apoc.import.file.enabled=true in apoc.conf
```

The procedures and settings are described in the [APOC JSON export guide](https://neo4j.com/docs/apoc/current/export/json/) and [APOC `load.json` reference](https://neo4j.com/docs/apoc/current/overview/apoc.load/apoc.load.json/).

## Check APOC and run batches

`await apoc.version()` returns the version installed on the connected server. `apoc.Periodic.iterate()` wraps a read query and an update query that run in batches; `batch_size` defaults to 1000. The wrapper has no argument for runtime query values. For a parameterized batch, call the APOC procedure through `connection.run` and pass values in `config.params`, as in the example. Keep the query text developer-written and never interpolate user input.

## Export and import JSON

`apoc.Export.to_json(file_name, config=None)` exports the **whole database** to JSON Lines in the server's import directory. A graph export contains metadata such as labels and nested `properties`; it is not the same shape as the property maps expected by `create_from_json`.

Run the full-database export example only against a test database unless you intend to create a complete snapshot. The exported file may contain sensitive data; restrict access to it and delete it when it is no longer needed.

`install_apoc_manager(Model)` adds `Model.apoc.create_from_json(file_url, json_path="$", batch_size=1000)`. The importer reads property maps selected by `json_path`, creates nodes with the model's label, and assigns new `uid` values. It does not restore exported labels, relationships, or original identifiers. The example exports a full database snapshot, then uses APOC's query export to write a focused JSON Lines fixture containing one property map for the importer.

`create_from_json` passes `file_url` to `apoc.load.json`, which can also fetch remote URLs. Do not pass user-controlled URLs: this can let the Neo4j server access internal network services. The API logs `file_url` at INFO level, so never include credentials or tokens in it. Follow the [APOC SSRF security guidance](https://neo4j.com/docs/apoc/current/security-guidelines/) for your Neo4j edition.

```python
from uuid import uuid4

from node4j.db import connection
from node4j.ext.apoc import apoc, install_apoc_manager
from node4j.nodes import Node


class GuideApocSource(Node):
    marker: str


class GuideApocImported(Node):
    marker: str


install_apoc_manager(GuideApocImported)
marker = str(uuid4())
other_marker = str(uuid4())
backup_file = f"node4j-apoc-backup-{marker}.json"
import_file = f"node4j-apoc-import-{marker}.json"

try:
    version = await apoc.version()
    assert version is not None

    await apoc.Periodic.iterate(
        "UNWIND [] AS source RETURN source",
        "SET source.`apoc_processed` = true",
        batch_size=100,
    )

    await GuideApocSource.q.create(marker=marker)
    await GuideApocSource.q.create(marker=other_marker)
    await connection.run(
        """
        CALL apoc.periodic.iterate(
            $cypher_to_iterate,
            $cypher_to_execute,
            {batchSize: $batch_size, params: {marker: $marker}}
        )
        """,
        {
            "cypher_to_iterate": (
                "MATCH (source:`GuideApocSource`) "
                "WHERE source.`marker` = $marker RETURN source"
            ),
            "cypher_to_execute": "SET source.`apoc_processed` = true",
            "batch_size": 100,
            "marker": marker,
        },
    )
    processed = await connection.run(
        "MATCH (source:`GuideApocSource`) WHERE source.`marker` = $marker "
        "RETURN source.`apoc_processed` AS processed",
        {"marker": marker},
    )
    assert processed[0]["processed"] is True
    untouched = await connection.run(
        "MATCH (source:`GuideApocSource`) WHERE source.`marker` = $marker "
        "RETURN source.`apoc_processed` IS NULL AS unchanged",
        {"marker": other_marker},
    )
    assert untouched[0]["unchanged"] is True

    await apoc.Export.to_json(backup_file, {"jsonFormat": "JSON_LINES"})

    exported = await connection.run(
        """
        CALL apoc.export.json.query(
            $statement,
            $file_name,
            {params: {marker: $marker}}
        )
        YIELD file, done
        RETURN file, done
        """,
        {
            "statement": (
                "MATCH (source:`GuideApocSource`) "
                "WHERE source.`marker` = $marker "
                "RETURN properties(source) AS row"
            ),
            "file_name": import_file,
            "marker": marker,
        },
    )
    assert exported[0]["done"] is True

    loaded = await connection.run(
        "CALL apoc.load.json($url) YIELD value RETURN value",
        {"url": f"file:///{import_file}"},
    )
    assert loaded[0]["value"]["row"]["marker"] == marker
    selected = await connection.run(
        "CALL apoc.load.json($url, $path) YIELD value RETURN value",
        {"url": f"file:///{import_file}", "path": "$.row"},
    )
    assert selected[0]["value"]["marker"] == marker

    import_result = await GuideApocImported.apoc.create_from_json(
        f"file:///{import_file}",
        json_path="$.row",
        batch_size=100,
    )
    imported = await connection.run(
        "MATCH (node:`GuideApocImported`) "
        "WHERE node.`marker` = $marker "
        "RETURN count(node) AS total",
        {"marker": marker},
    )
    assert imported[0]["total"] == 1, import_result
finally:
    await connection.run(
        "MATCH (node) WHERE node.`marker` IN $markers DETACH DELETE node",
        {"markers": [marker, other_marker]},
    )
```

The export files stay in the Neo4j server's import directory. Use unique file names and manage those server-side files according to your deployment's retention policy. The example uses synthetic data and removes its temporary nodes.
