import datetime
import uuid

from node4j.mixins import TTLMixin
from node4j.models import AuditLog
from node4j.nodes import Node


class N2FormatParent(Node):
    name: str


class N2FormatNode(N2FormatParent):
    aware_at: datetime.datetime
    naive_at: datetime.datetime

    class Meta:
        indexes = ["name"]
        constraints = [("uid",)]


async def _drop_n2_schema_artifacts(db):
    """Reset globally named schema artifacts in the disposable test database."""
    await db.run("DROP INDEX `index_N2FormatNode_name` IF EXISTS")
    await db.run("DROP CONSTRAINT `constraint_N2FormatNode_uid` IF EXISTS")


async def _drop_ttl_index(db):
    """Reset the globally named TTL index in the disposable test database."""
    await db.run("DROP INDEX `ttl_index` IF EXISTS")


async def test_N2_api_write_preserves_labels_uid_and_datetime_text(db):
    uid = uuid.uuid4()
    aware_at = datetime.datetime(
        2024, 2, 3, 4, 5, 6, tzinfo=datetime.timezone(datetime.timedelta(hours=2))
    )
    naive_at = datetime.datetime(2024, 2, 3, 4, 5, 6)

    try:
        await N2FormatNode.q.create(
            uid=uid,
            name=f"n2-write-{uid.hex}",
            aware_at=aware_at,
            naive_at=naive_at,
        )

        rows = await db.run(
            "MATCH (n:`N2FormatNode` {`uid`: $uid}) "
            "RETURN labels(n) AS labels, n.`uid` AS uid, "
            "n.`aware_at` AS aware_at, n.`naive_at` AS naive_at",
            {"uid": str(uid)},
        )

        assert len(rows) == 1
        record = rows[0]
        assert set(record["labels"]) == {"N2FormatParent", "N2FormatNode"}
        assert isinstance(record["uid"], str)
        assert record["uid"] == str(uid)
        assert record["aware_at"] == aware_at.isoformat()
        assert record["naive_at"] == naive_at.isoformat()
    finally:
        await db.run(
            "MATCH (n:`N2FormatNode` {`uid`: $uid}) DETACH DELETE n",
            {"uid": str(uid)},
        )


async def test_N2_sample_audit_log_default_timestamp_is_naive_text(db):
    uid = uuid.uuid4()

    try:
        audit_log = await AuditLog.q.create(
            uid=uid,
            target_uid="synthetic-target",
            action="CREATE",
            message="synthetic audit event",
        )
        rows = await db.run(
            "MATCH (n:`AuditLog` {`uid`: $uid}) "
            "RETURN n.`uid` AS uid, n.`timestamp` AS timestamp",
            {"uid": str(uid)},
        )

        assert len(rows) == 1
        record = rows[0]
        assert isinstance(record["uid"], str)
        assert record["uid"] == str(uid)
        assert isinstance(record["timestamp"], str)
        assert record["timestamp"] == audit_log.timestamp.isoformat()
        assert audit_log.timestamp.tzinfo is None
    finally:
        await db.run(
            "MATCH (n:`AuditLog` {`uid`: $uid}) DETACH DELETE n",
            {"uid": str(uid)},
        )


async def test_N2_api_reads_legacy_uid_and_datetime_text(db):
    uid = uuid.uuid4()
    aware_at = datetime.datetime(
        2024, 2, 3, 4, 5, 6, tzinfo=datetime.timezone(datetime.timedelta(hours=2))
    )
    naive_at = datetime.datetime(2024, 2, 3, 4, 5, 6)

    try:
        await db.run(
            "CREATE (n:`N2FormatParent`:`N2FormatNode` {"
            "`uid`: $uid, `name`: $name, "
            "`aware_at`: $aware_at, `naive_at`: $naive_at})",
            {
                "uid": str(uid),
                "name": f"n2-legacy-{uid.hex}",
                "aware_at": aware_at.isoformat(),
                "naive_at": naive_at.isoformat(),
            },
        )

        node = await N2FormatNode.q.match_one(filters={"uid": str(uid)})

        assert node is not None
        assert node.uid == uid
        assert node.aware_at == aware_at
        assert node.naive_at == naive_at
        assert node.naive_at.tzinfo is None
    finally:
        await db.run(
            "MATCH (n:`N2FormatNode` {`uid`: $uid}) DETACH DELETE n",
            {"uid": str(uid)},
        )


async def test_N2_apply_schema_keeps_index_and_constraint_names(db):
    await _drop_n2_schema_artifacts(db)

    try:
        await N2FormatNode.q.apply_schema()

        index_rows = await db.run("SHOW INDEXES YIELD `name` RETURN `name`")
        constraint_rows = await db.run("SHOW CONSTRAINTS YIELD `name` RETURN `name`")

        assert "index_N2FormatNode_name" in {row["name"] for row in index_rows}
        assert "constraint_N2FormatNode_uid" in {row["name"] for row in constraint_rows}
    finally:
        await _drop_n2_schema_artifacts(db)


async def test_N2_ttl_infrastructure_keeps_index_name(db):
    await db.run(
        "CALL apoc.periodic.cancel($job_name)", {"job_name": "ttl_cleanup_job"}
    )
    await _drop_ttl_index(db)

    try:
        await TTLMixin.setup_ttl_infrastructure()
        index_rows = await db.run("SHOW INDEXES YIELD `name` RETURN `name`")

        assert "ttl_index" in {row["name"] for row in index_rows}
    finally:
        await db.run(
            "CALL apoc.periodic.cancel($job_name)", {"job_name": "ttl_cleanup_job"}
        )
        await _drop_ttl_index(db)
