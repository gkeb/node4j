# Configuration and logging

[Polski](../pl/configuration-and-logging.md) · [README](../../README.md)

## Configure the Neo4j connection

`node4j` reads `NODE4J_URI`, `NODE4J_USER`, and `NODE4J_PASSWORD` from the process environment. It also reads a `.env` file in the application's current working directory automatically; there is no need to load it yourself.

```dotenv
NODE4J_URI=bolt://127.0.0.1:7687
NODE4J_USER=neo4j
NODE4J_PASSWORD=replace-with-your-password
```

Keep real credentials in `.env` and make sure that file is excluded from version control.

The resolved values are available from `node4j.config.settings`:

```python
from node4j.config import settings


resolved_settings = {
    "NODE4J_URI": settings.uri,
    "NODE4J_USER": settings.user,
    "NODE4J_PASSWORD": settings.password,
}
assert all(resolved_settings.values())
```

## Enable application logging

The library uses Python loggers under `node4j.*` and does not configure application handlers. Configure logging in your application, for example with `basicConfig()`:

```python
import logging


logging.basicConfig(level=logging.INFO)
# For temporary troubleshooting, set node4j to DEBUG in your application.
# logging.getLogger("node4j").setLevel(logging.DEBUG)
```

DEBUG records and ERROR records for failed queries include Cypher parameters. They can contain sensitive data, so enable DEBUG only when those values are safe to write to your logs and configure error log handlers with the same care.
