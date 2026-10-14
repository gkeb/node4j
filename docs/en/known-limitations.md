# Known limitations

[Polski](../pl/known-limitations.md) · [README](../../README.md)

These behaviors are important when choosing how to use the library. Each item describes the current behavior and a practical response.

## APOC trigger management

`apoc.Triggers.install()`, `list()`, and `remove()` fail with `ClientError` when called through the library's default database connection in the tested Neo4j configurations. The wrapper does not currently route these operations to the `system` database.

**What to do:** Do not rely on `apoc.Triggers` through the default connection. If your deployment needs trigger management, use an operational workflow configured for the appropriate database outside this wrapper, or avoid these calls until the wrapper supports that route.

## Date and UID values are stored as text

Properties are serialized with Pydantic JSON mode before they are written. Date and datetime values therefore reach Neo4j as text, and `uid` is stored as text too; Neo4j temporal functions do not treat those strings as native temporal values.

**What to do:** Treat persisted date values as strings and parse them in your application when needed. Use explicit Cypher and an explicit conversion path if a query needs Neo4j temporal values. Compare `uid` values as strings.

See [Models and schema](models-and-schema.md) for model fields and `uid`.

## Unknown filter suffixes become equality

An unknown suffix in a `Q` filter, or an unsupported or misspelled suffix, silently falls back to equality. A typo in a comparison suffix can return a different set of nodes than intended.

**What to do:** Use only the documented suffixes and cover non-equality filters with tests. See [Queries and filters](queries-and-filters.md) for the supported operators.

## The model registry uses class names

The global model registry is keyed by class name. If two imported model classes have the same name, the later registration replaces the earlier one.

**What to do:** Give every registered model a unique class name across the application, including models imported from separate modules. See [Relationships](relationships.md) for relationship declarations that refer to a model by name.

## Query history grows for the lifetime of the connection

`connection.queries` keeps every query and its parameters in a list. The list grows as the connection runs and is not automatically bounded or cleared.

**What to do:** Do not use this list as permanent telemetry in a long-lived process. If you inspect it for debugging, clear it after use with `connection.queries.clear()` or send diagnostics to a bounded application-owned store.

See [Configuration and logging](configuration-and-logging.md) for logging behavior.

## Query parameters appear in logs

The `node4j.db` logger includes query parameters in DEBUG records and in ERROR records for failed queries. Parameters may contain sensitive values.

**What to do:** Treat both DEBUG and failed-query ERROR logs as sensitive. Restrict access to them and redact parameter values before sending logs to shared or external systems. See [Configuration and logging](configuration-and-logging.md) for logger setup.
