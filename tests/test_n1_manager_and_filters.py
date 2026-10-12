import uuid

import pytest

from node4j.nodes import Node
from node4j.query import Q


class N1ManagerParent(Node):
    scope: str
    name: str


class N1ManagerNode(N1ManagerParent):
    age: int
    score: int


class N1SchemaNode(Node):
    name: str

    class Meta:
        indexes = ["name"]
        constraints = [("uid",)]


@pytest.fixture
async def n1_scope(db):
    scope = uuid.uuid4().hex
    try:
        yield scope
    finally:
        await db.run(
            "MATCH (n) WHERE n.`scope` = $scope DETACH DELETE n",
            {"scope": scope},
        )


async def _create_node(scope: str, name: str, age: int, score: int = 0):
    return await N1ManagerNode.q.create(scope=scope, name=name, age=age, score=score)


def _names(nodes):
    return [node.name for node in nodes]


async def test_N1_manager_create_persists_node(n1_scope, db):
    node = await _create_node(n1_scope, "created", age=27, score=8)

    rows = await db.run(
        "MATCH (n:`N1ManagerNode`) WHERE n.`uid` = $uid "
        "RETURN n.`scope` AS scope, n.`name` AS name, "
        "n.`age` AS age, n.`score` AS score",
        {"uid": str(node.uid)},
    )

    assert rows == [{"scope": n1_scope, "name": "created", "age": 27, "score": 8}]


async def test_N1_manager_match_one_returns_matching_node(n1_scope):
    created = await _create_node(n1_scope, "match-one", age=31)

    found = await N1ManagerNode.q.match_one(filters={"uid": str(created.uid)})

    assert found is not None
    assert found.uid == created.uid
    assert found.name == "match-one"


async def test_N1_manager_match_all_orders_ascending_and_descending(n1_scope):
    await _create_node(n1_scope, "older", age=30)
    await _create_node(n1_scope, "younger", age=10)
    await _create_node(n1_scope, "middle", age=20)

    ascending = await N1ManagerNode.q.match_all(
        filters={"scope": n1_scope}, order_by=["age"]
    )
    descending = await N1ManagerNode.q.match_all(
        filters={"scope": n1_scope}, order_by=["-age"]
    )

    assert _names(ascending) == ["younger", "middle", "older"]
    assert _names(descending) == ["older", "middle", "younger"]


async def test_N1_manager_update_persists_changed_fields(n1_scope):
    node = await _create_node(n1_scope, "update", age=20, score=1)

    updated = await N1ManagerNode.q.update(
        filters={"uid": str(node.uid)}, data={"age": 21, "score": 9}
    )
    found = await N1ManagerNode.q.match_one(filters={"uid": str(node.uid)})

    assert updated == 1
    assert found is not None
    assert (found.age, found.score) == (21, 9)


async def test_N1_manager_delete_removes_matching_node(n1_scope):
    node = await _create_node(n1_scope, "delete", age=18)

    deleted = await N1ManagerNode.q.delete(filters={"uid": str(node.uid)})
    found = await N1ManagerNode.q.match_one(filters={"uid": str(node.uid)})

    assert deleted == 1
    assert found is None


async def test_N1_manager_count_applies_filters(n1_scope):
    await _create_node(n1_scope, "count-low", age=10)
    await _create_node(n1_scope, "count-mid", age=20)
    await _create_node(n1_scope, "count-high", age=30)

    count = await N1ManagerNode.q.count(filters={"scope": n1_scope, "age__gte": 20})

    assert count == 2


async def test_N1_manager_aggregate_returns_requested_values(n1_scope):
    await _create_node(n1_scope, "aggregate-low", age=10, score=5)
    await _create_node(n1_scope, "aggregate-mid", age=20, score=20)
    await _create_node(n1_scope, "aggregate-high", age=30, score=30)

    result = await N1ManagerNode.q.aggregate(
        filters={"scope": n1_scope, "age__gte": 20},
        score_total="sum(score)",
        node_count="count(uid)",
    )

    assert result == {"score_total": 50, "node_count": 2}


async def test_N1_manager_get_or_create_creates_then_reuses_node(n1_scope):
    filters = {"scope": n1_scope, "name": "get-or-create"}
    created, was_created = await N1ManagerNode.q.get_or_create(
        filters=filters, defaults={"age": 24, "score": 6}
    )
    existing, was_created_again = await N1ManagerNode.q.get_or_create(
        filters=filters, defaults={"age": 99, "score": 99}
    )

    assert was_created is True
    assert was_created_again is False
    assert existing.uid == created.uid
    assert (existing.age, existing.score) == (24, 6)


async def test_N1_manager_update_or_create_creates_then_updates_node(n1_scope):
    filters = {"scope": n1_scope, "name": "update-or-create"}
    created, was_created = await N1ManagerNode.q.update_or_create(
        filters=filters, defaults={"age": 24, "score": 6}
    )
    updated, was_created_again = await N1ManagerNode.q.update_or_create(
        filters=filters, defaults={"age": 25, "score": 7}
    )

    assert was_created is True
    assert was_created_again is False
    assert updated.uid == created.uid
    assert (updated.age, updated.score) == (25, 7)


async def test_N1_manager_bulk_create_persists_all_nodes(n1_scope):
    data = [
        {
            "scope": n1_scope,
            "name": "bulk-a",
            "age": 20,
            "score": 2,
            "uid": uuid.uuid4(),
        },
        {
            "scope": n1_scope,
            "name": "bulk-b",
            "age": 30,
            "score": 3,
            "uid": uuid.uuid4(),
        },
    ]

    created = await N1ManagerNode.q.bulk_create(data)
    found = await N1ManagerNode.q.match_all(filters={"scope": n1_scope})

    assert len(created) == 2
    assert {node.name for node in created} == {"bulk-a", "bulk-b"}
    assert {node.uid for node in found} == {node.uid for node in created}


async def test_N1_manager_bulk_update_changes_matching_nodes(n1_scope):
    first = await _create_node(n1_scope, "bulk-update-a", age=20, score=1)
    second = await _create_node(n1_scope, "bulk-update-b", age=30, score=2)

    updated = await N1ManagerNode.q.bulk_update(
        [
            {"uid": str(first.uid), "score": 11},
            {"uid": str(second.uid), "score": 22},
        ]
    )
    found = await N1ManagerNode.q.match_all(
        filters={"scope": n1_scope}, order_by=["name"]
    )

    assert updated == 2
    assert [node.score for node in found] == [11, 22]


async def test_N1_manager_apply_schema_creates_indexes_and_constraints(db):
    await db.run("DROP INDEX `index_N1SchemaNode_name` IF EXISTS")
    await db.run("DROP CONSTRAINT `constraint_N1SchemaNode_uid` IF EXISTS")

    try:
        await N1SchemaNode.q.apply_schema()

        indexes = await db.run("SHOW INDEXES YIELD `name` RETURN `name`")
        constraints = await db.run("SHOW CONSTRAINTS YIELD `name` RETURN `name`")

        assert "index_N1SchemaNode_name" in {row["name"] for row in indexes}
        assert "constraint_N1SchemaNode_uid" in {row["name"] for row in constraints}
    finally:
        await db.run("DROP INDEX `index_N1SchemaNode_name` IF EXISTS")
        await db.run("DROP CONSTRAINT `constraint_N1SchemaNode_uid` IF EXISTS")


async def test_N1_manager_connect_creates_relationship_with_properties(n1_scope, db):
    source = await _create_node(n1_scope, "connect-source", age=20)
    target = await _create_node(n1_scope, "connect-target", age=30)

    await N1ManagerNode.q.connect(
        source.uid, target.uid, "N1_LINK", properties={"weight": 4}
    )
    rows = await db.run(
        "MATCH (a:`N1ManagerNode`)-[r:`N1_LINK`]->(b:`N1ManagerNode`) "
        "WHERE a.`uid` = $source_uid AND b.`uid` = $target_uid "
        "RETURN r.`weight` AS weight",
        {"source_uid": str(source.uid), "target_uid": str(target.uid)},
    )

    assert rows == [{"weight": 4}]


async def test_N1_manager_disconnect_removes_relationship(n1_scope, db):
    source = await _create_node(n1_scope, "disconnect-source", age=20)
    target = await _create_node(n1_scope, "disconnect-target", age=30)
    await N1ManagerNode.q.connect(source.uid, target.uid, "N1_LINK")

    await N1ManagerNode.q.disconnect(source.uid, target.uid, "N1_LINK")
    rows = await db.run(
        "MATCH (a:`N1ManagerNode`)-[r:`N1_LINK`]->(b:`N1ManagerNode`) "
        "WHERE a.`uid` = $source_uid AND b.`uid` = $target_uid "
        "RETURN count(r) AS count",
        {"source_uid": str(source.uid), "target_uid": str(target.uid)},
    )

    assert rows == [{"count": 0}]


async def test_N1_manager_update_relationship_changes_properties(n1_scope, db):
    source = await _create_node(n1_scope, "relationship-source", age=20)
    target = await _create_node(n1_scope, "relationship-target", age=30)
    await N1ManagerNode.q.connect(
        source.uid, target.uid, "N1_LINK", properties={"weight": 1}
    )

    await N1ManagerNode.q.update_relationship(
        source.uid,
        target.uid,
        "N1_LINK",
        properties={"weight": 5, "active": True},
    )
    rows = await db.run(
        "MATCH (a:`N1ManagerNode`)-[r:`N1_LINK`]->(b:`N1ManagerNode`) "
        "WHERE a.`uid` = $source_uid AND b.`uid` = $target_uid "
        "RETURN r.`weight` AS weight, r.`active` AS active",
        {"source_uid": str(source.uid), "target_uid": str(target.uid)},
    )

    assert rows == [{"weight": 5, "active": True}]


@pytest.mark.parametrize(
    ("filter_key", "filter_value", "expected_names"),
    [
        ("age__gt", 10, ["alpine", "beta"]),
        ("age__gte", 20, ["alpine", "beta"]),
        ("age__lt", 20, ["alpha"]),
        ("age__lte", 20, ["alpha", "alpine"]),
        ("age__in", [10, 30], ["alpha", "beta"]),
        ("name__contains", "ha", ["alpha"]),
        ("name__startswith", "al", ["alpha", "alpine"]),
        ("name__endswith", "a", ["alpha", "beta"]),
        ("age__ne", 20, ["alpha", "beta"]),
        ("age", 20, ["alpine"]),
        # Unknown suffixes currently compile as equality; keep that behavior.
        ("age__gtt", 20, ["alpine"]),
    ],
)
async def test_N1_Q_filters_apply_operators(
    n1_scope, filter_key, filter_value, expected_names
):
    await _create_node(n1_scope, "alpha", age=10)
    await _create_node(n1_scope, "alpine", age=20)
    await _create_node(n1_scope, "beta", age=30)

    filters = Q(scope=n1_scope) & Q(**{filter_key: filter_value})
    found = await N1ManagerNode.q.match_all(filters=filters, order_by=["name"])

    assert _names(found) == expected_names


async def test_N1_Q_and_combines_filter_clauses(n1_scope):
    await _create_node(n1_scope, "alpha", age=10)
    await _create_node(n1_scope, "alpine", age=20)
    await _create_node(n1_scope, "beta", age=30)

    filters = Q(scope=n1_scope) & (Q(age__gt=10) & Q(name__startswith="al"))
    found = await N1ManagerNode.q.match_all(filters=filters)

    assert _names(found) == ["alpine"]


async def test_N1_Q_or_combines_filter_clauses(n1_scope):
    await _create_node(n1_scope, "alpha", age=10)
    await _create_node(n1_scope, "alpine", age=20)
    await _create_node(n1_scope, "beta", age=30)

    filters = Q(scope=n1_scope) & (Q(name="alpha") | Q(name="beta"))
    found = await N1ManagerNode.q.match_all(filters=filters, order_by=["name"])

    assert _names(found) == ["alpha", "beta"]


async def test_N1_Q_not_excludes_matching_nodes(n1_scope):
    await _create_node(n1_scope, "alpha", age=10)
    await _create_node(n1_scope, "alpine", age=20)
    await _create_node(n1_scope, "beta", age=30)

    filters = Q(scope=n1_scope) & ~Q(name="alpha")
    found = await N1ManagerNode.q.match_all(filters=filters, order_by=["name"])

    assert _names(found) == ["alpine", "beta"]


async def test_N1_parent_manager_finds_subclass_node(n1_scope):
    await _create_node(n1_scope, "subclass", age=27, score=8)

    found = await N1ManagerParent.q.match_one(filters={"scope": n1_scope})

    assert found is not None
    assert found.name == "subclass"
