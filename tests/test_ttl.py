import asyncio
import datetime

import pytest

from node4j.mixins import TTL_CLEANUP_QUERY, TTLMixin


class TtlProbe(TTLMixin):
    name: str


async def _probe_names(db) -> set[str]:
    rows = await db.run("MATCH (n:TtlProbe) RETURN n.name AS name")
    return {row["name"] for row in rows}


@pytest.fixture
async def probes(db):
    await db.run("MATCH (n:TtlProbe) DETACH DELETE n")
    yield
    await db.run("MATCH (n:TtlProbe) DETACH DELETE n")


async def _create_probes():
    expired = await TtlProbe.q.create(name="expired")
    await expired.save_with_expiry(lifespan=datetime.timedelta(minutes=-5))
    live = await TtlProbe.q.create(name="live")
    await live.save_with_expiry(lifespan=datetime.timedelta(hours=1))
    await TtlProbe.q.create(name="no-ttl")


async def test_cleanup_removes_expired_nodes_and_keeps_live_ones(db, probes):
    await _create_probes()

    await db.run(TTL_CLEANUP_QUERY)

    assert await _probe_names(db) == {"live", "no-ttl"}


@pytest.fixture
async def apoc_job(db):
    try:
        await db.run("RETURN apoc.version()")
    except Exception as e:
        pytest.skip(f"Baza testowa bez APOC: {e}")
    yield
    await db.run("CALL apoc.periodic.cancel('ttl_cleanup_job')")


async def test_installed_job_removes_expired_nodes(db, probes, apoc_job):
    await _create_probes()

    # Zadanie apoc.periodic.repeat wykonuje się od razu po instalacji.
    await TTLMixin.setup_ttl_infrastructure()

    for _ in range(20):
        if await _probe_names(db) == {"live", "no-ttl"}:
            break
        await asyncio.sleep(0.25)
    assert await _probe_names(db) == {"live", "no-ttl"}


async def test_cleanup_skips_invalid_ttl_and_handles_native_datetime(db, probes):
    await _create_probes()
    await db.run("CREATE (:TtlProbe:TTLMixin {name: 'bad', ttl: 'nie-data'})")
    await db.run(
        "CREATE (:TtlProbe:TTLMixin {name: 'bad-date', ttl: '2026-13-45T25:00:00Z'})"
    )
    await db.run(
        "CREATE (:TtlProbe:TTLMixin {name: 'native', ttl: $ttl})",
        {
            "ttl": datetime.datetime.now(datetime.timezone.utc)
            - datetime.timedelta(minutes=5)
        },
    )

    await db.run(TTL_CLEANUP_QUERY)

    assert await _probe_names(db) == {"live", "no-ttl", "bad", "bad-date"}


async def test_setup_replaces_existing_job_with_current_query(db, probes, apoc_job):
    # Zadanie o tej samej nazwie z innym zapytaniem — np. z wersji sprzed poprawki.
    await db.run("CALL apoc.periodic.repeat('ttl_cleanup_job', 'RETURN 1', 3600)")
    await _create_probes()

    await TTLMixin.setup_ttl_infrastructure()

    for _ in range(20):
        if await _probe_names(db) == {"live", "no-ttl"}:
            break
        await asyncio.sleep(0.25)
    assert await _probe_names(db) == {"live", "no-ttl"}
