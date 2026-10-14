# Konfiguracja i logowanie

[English](../en/configuration-and-logging.md) · [README](../../README_PL.md)

## Konfiguracja połączenia z Neo4j

`node4j` odczytuje `NODE4J_URI`, `NODE4J_USER` i `NODE4J_PASSWORD` ze środowiska procesu. Automatycznie odczytuje też plik `.env` z bieżącego katalogu aplikacji; nie trzeba wczytywać go samodzielnie.

```dotenv
NODE4J_URI=bolt://127.0.0.1:7687
NODE4J_USER=neo4j
NODE4J_PASSWORD=replace-with-your-password
```

Prawdziwe poświadczenia przechowuj w `.env` i upewnij się, że ten plik jest wykluczony z kontroli wersji.

Odczytane wartości są dostępne w `node4j.config.settings`:

```python
from node4j.config import settings


resolved_settings = {
    "NODE4J_URI": settings.uri,
    "NODE4J_USER": settings.user,
    "NODE4J_PASSWORD": settings.password,
}
assert all(resolved_settings.values())
```

## Włączenie logowania w aplikacji

Biblioteka używa loggerów Pythona z nazwami `node4j.*` i nie konfiguruje handlerów aplikacji. Skonfiguruj logowanie w swojej aplikacji, na przykład przez `basicConfig()`:

```python
import logging


logging.basicConfig(level=logging.INFO)
# For temporary troubleshooting, set node4j to DEBUG in your application.
# logging.getLogger("node4j").setLevel(logging.DEBUG)
```

`connection.queries` przechowuje też wszystkie zapytania i ich parametry przez cały czas działania połączenia. W [Znanych ograniczeniach](known-limitations.md) opisano wpływ tej listy na pamięć.

Logi DEBUG oraz wpisy ERROR dla nieudanych zapytań zawierają parametry Cyphera. Mogą zawierać dane wrażliwe, dlatego włączaj DEBUG tylko wtedy, gdy te wartości mogą trafić do logów, a handlery logów błędów skonfiguruj z taką samą ostrożnością. Zobacz [Znane ograniczenia](known-limitations.md), gdzie opisano środki ostrożności.
