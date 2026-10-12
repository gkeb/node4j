import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import ConnectionAcquisitionTimeoutError, DriverError

import node4j.db as db_module
from node4j.db import AsyncDatabase


@pytest.fixture
def fake_driver_factory(monkeypatch):
    driver = SimpleNamespace(
        close=AsyncMock(),
        verify_connectivity=AsyncMock(),
    )
    factory = Mock(return_value=driver)
    monkeypatch.setattr(
        db_module,
        "AsyncGraphDatabase",
        SimpleNamespace(driver=factory),
    )
    monkeypatch.setattr(
        db_module,
        "settings",
        SimpleNamespace(uri="bolt://localhost:7687", user="neo4j", password="test"),
    )
    return driver, factory


@pytest.mark.asyncio
async def test_driver_disables_auto_commit_retries(fake_driver_factory):
    driver, factory = fake_driver_factory
    database = AsyncDatabase()

    await database.connect()

    assert factory.call_args.kwargs["disable_auto_commit_retries"] is True
    assert database.driver is driver
    await database.close()
    driver.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_closes_driver_when_connectivity_check_fails(fake_driver_factory):
    driver, _ = fake_driver_factory
    driver.verify_connectivity.side_effect = DriverError("driver already closed")
    database = AsyncDatabase()

    with pytest.raises(DriverError, match="driver already closed"):
        await database.connect()

    assert database.driver is None
    driver.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_closes_driver_when_cancelled(fake_driver_factory):
    driver, _ = fake_driver_factory
    driver.verify_connectivity.side_effect = asyncio.CancelledError
    database = AsyncDatabase()

    with pytest.raises(asyncio.CancelledError):
        await database.connect()

    assert database.driver is None
    driver.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_propagates_driver_error_after_real_driver_is_closed():
    database = AsyncDatabase()
    database.driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "test"),
        disable_auto_commit_retries=True,
    )
    await database.driver.close()

    with pytest.raises(DriverError):
        await database.run("RETURN 1")


@pytest.mark.asyncio
async def test_run_preserves_connection_acquisition_timeout():
    error = ConnectionAcquisitionTimeoutError("connection acquisition timed out")
    session = SimpleNamespace(run=AsyncMock(side_effect=error))

    class SessionContext:
        async def __aenter__(self):
            return session

        async def __aexit__(self, exc_type, exc, traceback):
            return False

    database = AsyncDatabase()
    database.driver = SimpleNamespace(session=lambda: SessionContext())

    with pytest.raises(ConnectionAcquisitionTimeoutError) as exc_info:
        await database.run("RETURN 1")

    assert exc_info.value is error


@pytest.mark.asyncio
async def test_close_allows_a_fresh_driver_connection(fake_driver_factory):
    driver, factory = fake_driver_factory
    replacement = SimpleNamespace(
        close=AsyncMock(),
        verify_connectivity=AsyncMock(),
    )
    factory.side_effect = [driver, replacement]
    database = AsyncDatabase()

    await database.connect()
    await database.close()
    await database.connect()

    assert factory.call_count == 2
    assert database.driver is replacement
    await database.close()
