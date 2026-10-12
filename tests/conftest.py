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
        if os.environ.get("NODE4J_REQUIRE_TEST_DB") == "1":
            pytest.fail(
                f"Wymagana baza testowa Neo4j jest niedostępna "
                f"({os.environ['NODE4J_URI']}): {e}",
                pytrace=False,
            )
        pytest.skip(f"Brak bazy testowej Neo4j ({os.environ['NODE4J_URI']}): {e}")
    try:
        yield connection
    finally:
        await connection.close()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Wymagaj wykonania testów integracyjnych w CI."""
    if os.environ.get("NODE4J_REQUIRE_TEST_DB") != "1":
        return

    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    if reporter is None:
        session.exitstatus = pytest.ExitCode.INTERNAL_ERROR
        return

    integration_tests = {
        item.nodeid for item in session.items if "db" in item.fixturenames
    }
    skipped_tests = {report.nodeid for report in reporter.stats.get("skipped", ())}
    skipped_integration_tests = sorted(integration_tests & skipped_tests)
    if not skipped_integration_tests:
        return

    reporter.write_sep("=", "Wymagane testy integracyjne nie mogą być pomijane")
    for nodeid in skipped_integration_tests:
        reporter.write_line(nodeid)
    session.exitstatus = pytest.ExitCode.TESTS_FAILED
