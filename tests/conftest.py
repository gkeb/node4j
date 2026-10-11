import os

import pytest
from neo4j.exceptions import ServiceUnavailable

# Testy łączą się wyłącznie z bazą testową — nigdy z bazą z NODE4J_* użytkownika.
# conftest.py wczytuje się przed modułami testów, więc ustawienia node4j
# (tworzone przy pierwszym imporcie) widzą już te wartości.
os.environ["NODE4J_URI"] = os.environ.get("NODE4J_TEST_URI", "bolt://127.0.0.1:7688")
os.environ["NODE4J_USER"] = os.environ.get("NODE4J_TEST_USER", "neo4j")
os.environ["NODE4J_PASSWORD"] = os.environ.get(
    "NODE4J_TEST_PASSWORD", "test-password-123"
)


@pytest.fixture
async def db():
    """Połączenie z bazą testową; test jest pomijany, gdy bazy nie ma."""
    from node4j.db import connection

    try:
        await connection.connect()
    except ServiceUnavailable as e:
        pytest.skip(f"Brak bazy testowej Neo4j ({os.environ['NODE4J_URI']}): {e}")
    try:
        yield connection
    finally:
        await connection.close()
