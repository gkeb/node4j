import uuid
from collections import Counter
from typing import ClassVar
from unittest.mock import AsyncMock

import pytest
from neo4j.exceptions import ClientError

from node4j.db import connection
from node4j.edges import Edge
from node4j.ext.apoc import apoc
from node4j.ext.gds import gds
from node4j.mixins import SoftDeleteMixin
from node4j.nodes import Node
from node4j.properties import RelationshipDirection, RelationshipProperty


class N1RelationEdge(Edge):
    role: str
    weight: int


class N1RelationNode(Node):
    scope: str
    name: str

    outgoing = RelationshipProperty(
        "N1_REL_OUT", "N1RelationNode", RelationshipDirection.OUT
    )
    incoming = RelationshipProperty(
        "N1_REL_IN", "N1RelationNode", RelationshipDirection.IN
    )
    undirected = RelationshipProperty(
        "N1_REL_UNDIRECTED", "N1RelationNode", RelationshipDirection.UNDIRECTED
    )
    with_edge = RelationshipProperty(
        "N1_REL_EDGE", "N1RelationNode", RelationshipDirection.OUT, model=N1RelationEdge
    )


class N1PrefetchPublisher(Node):
    scope: str
    name: str


class N1PrefetchBook(Node):
    scope: str
    name: str

    publisher = RelationshipProperty(
        "N1_PUBLISHED_BY", "N1PrefetchPublisher", RelationshipDirection.OUT
    )


class N1PrefetchAuthor(Node):
    scope: str
    name: str

    books = RelationshipProperty(
        "N1_WROTE", "N1PrefetchBook", RelationshipDirection.OUT
    )


class N1HookNode(Node):
    scope: str
    name: str

    events: ClassVar[list[tuple[str, str, bool | None]]] = []

    async def pre_save(self, *, is_creating: bool) -> None:
        self.events.append(("pre_save", str(self.uid), is_creating))

    async def post_save(self, *, is_creating: bool) -> None:
        self.events.append(("post_save", str(self.uid), is_creating))

    async def pre_delete(self) -> None:
        self.events.append(("pre_delete", str(self.uid), None))

    async def post_delete(self) -> None:
        self.events.append(("post_delete", str(self.uid), None))


class N1AtomicNode(Node):
    scope: str
    name: str


class N1SoftDeleteNode(SoftDeleteMixin, Node):
    scope: str
    name: str


N1SoftDeleteNode.setup_soft_delete_manager()


class N1ApocNode(Node):
    scope: str
    name: str
    iterate_marker: bool
    iterate_changed: bool


@pytest.fixture
async def n1_scope(db):
    scope = uuid.uuid4().hex
    try:
        yield scope
    finally:
        await db.run(
            "MATCH (n) WHERE n.`scope` = $scope DETACH DELETE n", {"scope": scope}
        )


@pytest.fixture
def n1_hook_events():
    N1HookNode.events.clear()
    try:
        yield N1HookNode.events
    finally:
        N1HookNode.events.clear()


def _names(nodes):
    return [node.name for node, _properties in nodes]


async def test_N1_relationship_lazy_load_caches_results(n1_scope, db):
    source = await N1RelationNode.q.create(scope=n1_scope, name="source")
    first = await N1RelationNode.q.create(scope=n1_scope, name="first")
    second = await N1RelationNode.q.create(scope=n1_scope, name="second")
    await source.outgoing.connect(first)

    initial = await source.outgoing
    assert _names(initial) == ["first"]

    await db.run(
        "MATCH (a:`N1RelationNode`), (b:`N1RelationNode`) "
        "WHERE a.`uid` = $source_uid AND b.`uid` = $target_uid "
        "CREATE (a)-[:`N1_REL_OUT`]->(b)",
        {"source_uid": str(source.uid), "target_uid": str(second.uid)},
    )

    cached = await source.outgoing
    assert _names(cached) == ["first"]

    fresh_source = await N1RelationNode.q.match_one(filters={"uid": str(source.uid)})
    assert fresh_source is not None
    assert set(_names(await fresh_source.outgoing)) == {"first", "second"}


async def test_N1_relationship_instance_connect_disconnect_invalidates_cache(n1_scope):
    source = await N1RelationNode.q.create(scope=n1_scope, name="source")
    target = await N1RelationNode.q.create(scope=n1_scope, name="target")

    assert await source.outgoing == []
    await source.outgoing.connect(target, properties={"weight": 4})
    connected = await source.outgoing
    assert _names(connected) == ["target"]
    assert connected[0][1] == {"weight": 4}

    await source.outgoing.disconnect(target)
    assert await source.outgoing == []


async def test_N1_relationship_directions_preserve_in_out_and_undirected(n1_scope, db):
    source = await N1RelationNode.q.create(scope=n1_scope, name="source")
    target = await N1RelationNode.q.create(scope=n1_scope, name="target")

    await source.outgoing.connect(target)
    await source.incoming.connect(target)
    await source.undirected.connect(target)

    assert _names(await source.outgoing) == ["target"]
    assert _names(await source.incoming) == ["target"]
    assert _names(await source.undirected) == ["target"]

    rows = await db.run(
        "MATCH (a:`N1RelationNode`)-[r]->(b:`N1RelationNode`) "
        "WHERE a.`uid` IN $uids AND b.`uid` IN $uids "
        "RETURN type(r) AS relationship_type, a.`uid` AS from_uid, "
        "b.`uid` AS to_uid",
        {"uids": [str(source.uid), str(target.uid)]},
    )
    assert {
        (row["relationship_type"], row["from_uid"], row["to_uid"]) for row in rows
    } == {
        ("N1_REL_OUT", str(source.uid), str(target.uid)),
        ("N1_REL_IN", str(target.uid), str(source.uid)),
        ("N1_REL_UNDIRECTED", str(source.uid), str(target.uid)),
    }


async def test_N1_relationship_hydrates_edge_model(n1_scope):
    source = await N1RelationNode.q.create(scope=n1_scope, name="source")
    target = await N1RelationNode.q.create(scope=n1_scope, name="target")
    edge = N1RelationEdge(role="mentor", weight=7)

    await source.with_edge.connect(target, properties=edge)
    connected = await source.with_edge

    assert len(connected) == 1
    assert connected[0][0].name == "target"
    assert isinstance(connected[0][1], N1RelationEdge)
    assert connected[0][1] == edge


async def test_N1_relationship_prefetches_nested_relations(n1_scope):
    author = await N1PrefetchAuthor.q.create(scope=n1_scope, name="author")
    book = await N1PrefetchBook.q.create(scope=n1_scope, name="book")
    publisher = await N1PrefetchPublisher.q.create(scope=n1_scope, name="publisher")
    await author.books.connect(book)
    await book.publisher.connect(publisher)

    prefetched_author = await N1PrefetchAuthor.q.match_one(
        filters={"uid": str(author.uid)},
        prefetch={"books": {"publisher": {}}},
    )

    assert prefetched_author is not None
    late_book = await N1PrefetchBook.q.create(scope=n1_scope, name="late-book")
    await author.books.connect(late_book)

    books = await prefetched_author.books
    assert len(books) == 1
    assert books[0][0].name == "book"
    prefetched_book = books[0][0]

    late_publisher = await N1PrefetchPublisher.q.create(
        scope=n1_scope, name="late-publisher"
    )
    await book.publisher.connect(late_publisher)
    publishers = await prefetched_book.publisher
    assert len(publishers) == 1
    assert publishers[0][0].name == "publisher"


@pytest.mark.parametrize(
    "prefetch",
    [pytest.param(["books"], id="list"), pytest.param({"books": {}}, id="dict")],
)
async def test_N1_match_all_prefetch_loads_relations_without_lazy_query(
    n1_scope, prefetch
):
    author = await N1PrefetchAuthor.q.create(scope=n1_scope, name="author")
    book = await N1PrefetchBook.q.create(scope=n1_scope, name="book")
    await author.books.connect(book)

    query_count_before_match = len(connection.queries)
    authors = await N1PrefetchAuthor.q.match_all(
        filters={"uid": str(author.uid)}, prefetch=prefetch
    )

    assert len(authors) == 1
    assert len(connection.queries) == query_count_before_match + 1
    query_count_after_match = len(connection.queries)
    books = await authors[0].books

    assert [related.name for related, _properties in books] == ["book"]
    assert len(connection.queries) == query_count_after_match


async def test_N1_hooks_fire_for_create_update_and_delete(n1_scope, n1_hook_events):
    node = await N1HookNode.q.create(scope=n1_scope, name="created")
    uid = str(node.uid)
    assert n1_hook_events == [
        ("pre_save", uid, True),
        ("post_save", uid, True),
    ]

    n1_hook_events.clear()
    updated = await N1HookNode.q.update(filters={"uid": uid}, data={"name": "updated"})
    assert updated == 1
    assert n1_hook_events == [
        ("pre_save", uid, False),
        ("post_save", uid, False),
    ]

    n1_hook_events.clear()
    deleted = await N1HookNode.q.delete(filters={"uid": uid})
    assert deleted == 1
    assert n1_hook_events == [
        ("pre_delete", uid, None),
        ("post_delete", uid, None),
    ]


async def test_N1_hooks_fire_for_bulk_create_and_bulk_update(n1_scope, n1_hook_events):
    created = await N1HookNode.q.bulk_create(
        [
            {"scope": n1_scope, "name": "bulk-a"},
            {"scope": n1_scope, "name": "bulk-b"},
        ]
    )
    created_uids = {str(node.uid) for node in created}

    assert len(created) == 2
    assert Counter(n1_hook_events) == Counter(
        {("pre_save", uid, True) for uid in created_uids}
        | {("post_save", uid, True) for uid in created_uids}
    )

    n1_hook_events.clear()
    updated = await N1HookNode.q.bulk_update(
        [
            {"uid": str(node.uid), "name": f"updated-{index}"}
            for index, node in enumerate(created)
        ]
    )
    assert updated == 2
    assert Counter(n1_hook_events) == Counter(
        {("pre_save", uid, False) for uid in created_uids}
        | {("post_save", uid, False) for uid in created_uids}
    )


async def test_N1_atomic_transaction_commits_changes(n1_scope):
    @connection.atomic()
    async def create_node():
        return await N1AtomicNode.q.create(scope=n1_scope, name="committed")

    created = await create_node()
    found = await N1AtomicNode.q.match_one(filters={"uid": str(created.uid)})

    assert found is not None
    assert found.name == "committed"


async def test_N1_atomic_transaction_rolls_back_after_exception(n1_scope):
    @connection.atomic()
    async def create_then_fail():
        await N1AtomicNode.q.create(scope=n1_scope, name="rolled-back")
        raise ValueError("rollback")

    with pytest.raises(ValueError, match="rollback"):
        await create_then_fail()

    assert await N1AtomicNode.q.match_all(filters={"scope": n1_scope}) == []


async def test_N1_atomic_transaction_rejects_nesting_and_rolls_back(n1_scope):
    @connection.atomic()
    async def inner():
        await N1AtomicNode.q.create(scope=n1_scope, name="inner")

    @connection.atomic()
    async def outer():
        await N1AtomicNode.q.create(scope=n1_scope, name="outer")
        await inner()

    with pytest.raises(RuntimeError, match="zagnieżdżać"):
        await outer()

    assert await N1AtomicNode.q.match_all(filters={"scope": n1_scope}) == []


async def test_N1_soft_delete_hides_shows_and_restores_node(n1_scope):
    node = await N1SoftDeleteNode.q.create(scope=n1_scope, name="document")
    await node.soft_delete()

    assert await N1SoftDeleteNode.q.match_one(filters={"uid": str(node.uid)}) is None
    deleted = await N1SoftDeleteNode.all_objects.match_one(
        filters={"uid": str(node.uid)}
    )
    assert deleted is not None
    assert deleted.is_deleted is True
    assert deleted.deleted_at is not None

    await node.restore()
    restored = await N1SoftDeleteNode.q.match_one(filters={"uid": str(node.uid)})
    assert restored is not None
    assert restored.is_deleted is False
    assert restored.deleted_at is None


async def test_N1_apoc_version_is_available(db):
    version = await apoc.version()

    assert isinstance(version, str)
    assert version


async def test_N1_apoc_periodic_iterate_changes_matching_nodes(n1_scope):
    processed = await N1ApocNode.q.create(
        scope=n1_scope,
        name="processed",
        iterate_marker=True,
        iterate_changed=False,
    )
    skipped = await N1ApocNode.q.create(
        scope=n1_scope,
        name="skipped",
        iterate_marker=False,
        iterate_changed=False,
    )
    label = f"N1Iterate_{n1_scope}"
    await connection.run(
        f"MATCH (n:`N1ApocNode`) WHERE n.`uid` IN $uids SET n:`{label}`",
        {"uids": [str(processed.uid), str(skipped.uid)]},
    )

    await apoc.Periodic.iterate(
        f"MATCH (n:`N1ApocNode`:`{label}`) WHERE n.`iterate_marker` RETURN n",
        "SET n.`iterate_changed` = NOT n.`iterate_changed`",
        batch_size=1,
    )

    processed_after = await N1ApocNode.q.match_one(filters={"uid": str(processed.uid)})
    skipped_after = await N1ApocNode.q.match_one(filters={"uid": str(skipped.uid)})

    assert processed_after is not None
    assert processed_after.iterate_changed is True
    assert skipped_after is not None
    assert skipped_after.iterate_changed is False


async def test_N1_apoc_trigger_install_preserves_current_database_error(db):
    name = f"n1-trigger-{uuid.uuid4().hex}"
    try:
        await apoc.Triggers.install(
            name=name,
            cypher="MATCH (n) RETURN n",
            selector={"phase": "after"},
        )
    except ClientError as error:
        assert error.code == "Neo.ClientError.Procedure.ProcedureCallFailed"
        return

    await apoc.Triggers.remove(name)
    pytest.fail("APOC trigger installation unexpectedly succeeded")


async def test_N1_apoc_trigger_list_preserves_current_database_error(db):
    with pytest.raises(ClientError) as error:
        await apoc.Triggers.list()
    assert error.value.code == "Neo.ClientError.Procedure.ProcedureCallFailed"


async def test_N1_apoc_trigger_remove_preserves_current_database_error(db):
    name = f"n1-trigger-{uuid.uuid4().hex}"

    with pytest.raises(ClientError) as error:
        await apoc.Triggers.remove(name)
    assert error.value.code == "Neo.ClientError.Statement.SyntaxError"


async def test_N1_gds_imports_and_builds_graph_query_without_plugin(monkeypatch):
    run = AsyncMock(return_value=[{"graphName": "n1-graph"}])
    monkeypatch.setattr(connection, "run", run)

    result = await gds.Graph.project(
        "n1-graph",
        {"N1Node": {"label": "N1Node"}},
        {"N1_REL": {"type": "N1_REL"}},
    )

    assert result == {"graphName": "n1-graph"}
    run.assert_awaited_once_with(
        "CALL gds.graph.project($graph_name, $node_projection, "
        "$relationship_projection)",
        {
            "graph_name": "n1-graph",
            "node_projection": {"N1Node": {"label": "N1Node"}},
            "relationship_projection": {"N1_REL": {"type": "N1_REL"}},
        },
    )
