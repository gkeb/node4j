import asyncio
import io
import json
import os
import re
import socket
import subprocess
import sys
import tokenize
import warnings
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit
from uuid import uuid4

import pytest

ROOT = Path(__file__).parents[1]
SKIP_PREFIX = "<!-- docs-test: skip"


@dataclass(frozen=True)
class CodeBlock:
    number: int
    language: str
    source: str
    skip_reason: str | None


@dataclass(frozen=True)
class MarkdownPage:
    headings: tuple[tuple[int, str], ...]
    links: tuple[str, ...]
    blocks: tuple[CodeBlock, ...]


@dataclass(frozen=True)
class DatabaseSnapshot:
    nodes: dict[str, tuple[tuple[str, ...], dict[str, object]]]
    relationships: tuple[
        tuple[object | None, object | None, str, dict[str, object]], ...
    ]
    nodes_without_unique_uid: int
    indexes: dict[str, tuple[str | None, str | None]]
    constraints: dict[str, str | None]
    gds_projections: frozenset[str]


def _english_pages() -> list[Path]:
    pages = [ROOT / "README.md"]
    docs = ROOT / "docs" / "en"
    if docs.exists():
        pages.extend(sorted(docs.rglob("*.md")))
    return pages


def _polish_pages() -> list[Path]:
    pages = [ROOT / "README_PL.md"]
    docs = ROOT / "docs" / "pl"
    if docs.exists():
        pages.extend(sorted(docs.rglob("*.md")))
    return pages


def _all_pages() -> list[Path]:
    return [*_english_pages(), *_polish_pages()]


def _parse_markdown(source: str) -> MarkdownPage:
    lines = source.splitlines()
    headings: list[tuple[int, str]] = []
    links: list[str] = []
    blocks: list[CodeBlock] = []
    pending_skip: str | None = None
    index = 0
    backtick = chr(96)
    opening_fence = re.compile("^ {0,3}(" + re.escape(backtick) + "{3,}|~{3,})(.*)$")
    closing_fence = re.compile("^ {0,3}(" + re.escape(backtick) + "+|~+)\\s*$")

    while index < len(lines):
        line = lines[index]
        opening = opening_fence.match(line)
        if pending_skip is not None and opening is None:
            raise ValueError("A skip marker must directly precede a code block.")

        if opening:
            marker = opening.group(1)
            info = opening.group(2).strip()
            language = info.split(maxsplit=1)[0].lower() if info else ""
            block_lines: list[str] = []
            index += 1
            while index < len(lines):
                closing = closing_fence.match(lines[index])
                if (
                    closing
                    and closing.group(1)[0] == marker[0]
                    and len(closing.group(1)) >= len(marker)
                ):
                    break
                block_lines.append(lines[index])
                index += 1
            if index == len(lines):
                raise ValueError("A fenced code block is not closed.")
            blocks.append(
                CodeBlock(
                    number=len(blocks) + 1,
                    language=language,
                    source="\n".join(block_lines),
                    skip_reason=pending_skip,
                )
            )
            pending_skip = None
            index += 1
            continue

        marker_match = re.fullmatch(r"\s*<!-- docs-test: skip:\s*(.*?)\s*-->\s*", line)
        if line.strip().startswith(SKIP_PREFIX):
            if marker_match is None or not marker_match.group(1):
                raise ValueError("A skip marker must include a reason.")
            pending_skip = marker_match.group(1)

        heading = re.match(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if heading:
            headings.append((len(heading.group(1)), heading.group(2)))

        for link in re.finditer(r"!?\[[^\]]*\]\((<[^>]+>|[^)]+)\)", line):
            target = link.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            else:
                target = target.split(maxsplit=1)[0]
            links.append(target)
        index += 1

    if pending_skip is not None:
        raise ValueError("A skip marker must directly precede a code block.")
    return MarkdownPage(tuple(headings), tuple(links), tuple(blocks))


def _read_page(path: Path) -> tuple[str, MarkdownPage]:
    source = path.read_text(encoding="utf-8-sig")
    return source, _parse_markdown(source)


def _page_key(path: Path, language: str) -> str:
    if path.parent == ROOT:
        return "README"
    return path.relative_to(ROOT / "docs" / language).as_posix()


def _local_target(path: Path, target: str) -> tuple[Path, str] | None:
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None
    target_path = unquote(parsed.path)
    resolved = (path.parent / target_path).resolve() if target_path else path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return resolved, unquote(parsed.fragment)


def _heading_anchors(headings: tuple[tuple[int, str], ...]) -> set[str]:
    anchors: set[str] = set()
    counts: Counter[str] = Counter()
    for _, title in headings:
        base = title.replace(chr(96), "").lower()
        base = re.sub(r"[^\w -]", "", base)
        base = re.sub(r"\s+", "-", base.strip())
        count = counts[base]
        counts[base] += 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def _relative_links(path: Path) -> list[tuple[Path, str]]:
    _, page = _read_page(path)
    return [
        resolved
        for target in page.links
        if (resolved := _local_target(path, target)) is not None
    ]


def _has_full_database_clear(source: str) -> bool:
    normalized = re.sub(r"\s+", " ", source)
    return (
        re.search(
            r"\bMATCH\s*\(\s*(?P<variable>[a-z_]\w*)\s*\)"
            r"\s*(?:DETACH\s+)?DELETE\s+(?P=variable)\b",
            normalized,
            flags=re.IGNORECASE,
        )
        is not None
    )


def _python_blocks(page: MarkdownPage) -> list[CodeBlock]:
    return [block for block in page.blocks if block.language == "python"]


def _remove_python_comments(source: str) -> str:
    lines = source.splitlines(keepends=True)
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    for token in tokens:
        if token.type != tokenize.COMMENT:
            continue
        line_number, start_column = token.start
        _, end_column = token.end
        line = lines[line_number - 1]
        comment = line[start_column:end_column]
        lines[line_number - 1] = (
            line[:start_column] + " " * len(comment) + line[end_column:]
        )
    return "".join(lines)


def _skip_report(path: Path, blocks: list[CodeBlock]) -> str:
    descriptions = [f"block {block.number}: {block.skip_reason}" for block in blocks]
    return f"{path.name} skipped documentation examples: " + "; ".join(descriptions)


def _report_skipped_blocks(path: Path, blocks: list[CodeBlock], request) -> None:
    if not blocks:
        return
    report = _skip_report(path, blocks)
    request.node.user_properties.append(("skipped_documentation_blocks", report))
    warnings.warn(report, UserWarning, stacklevel=2)


def _page_runner_source(path: Path, blocks: list[CodeBlock]) -> str:
    executable = [
        {"number": block.number, "source": block.source}
        for block in blocks
        if block.skip_reason is None
    ]
    template = """
import ast
import asyncio
import inspect
import sys

sys.path.insert(0, __PROJECT_ROOT__)

page_name = __PAGE_NAME__
blocks = __BLOCKS__
namespace = {"__name__": "__main__"}
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

try:
    for block in blocks:
        try:
            code = compile(
                block["source"],
                f"{page_name} Python block {block['number']}",
                "exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
            result = eval(code, namespace)
            if inspect.isawaitable(result):
                loop.run_until_complete(result)
        except BaseException:
            print(
                f"{page_name} Python block {block['number']} failed",
                file=sys.stderr,
            )
            raise
        finally:
            asyncio.set_event_loop(loop)
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
    asyncio.set_event_loop(None)
"""
    return (
        template.replace("__PROJECT_ROOT__", repr(str(ROOT)))
        .replace("__PAGE_NAME__", repr(path.relative_to(ROOT).as_posix()))
        .replace("__BLOCKS__", json.dumps(executable))
    )


async def _schema_snapshot(
    db,
) -> tuple[dict[str, tuple[str | None, str | None]], dict[str, str | None]]:
    indexes = await db.run(
        "SHOW INDEXES YIELD name, createStatement, owningConstraint "
        "RETURN name, createStatement, owningConstraint"
    )
    constraints = await db.run(
        "SHOW CONSTRAINTS YIELD name, createStatement RETURN name, createStatement"
    )
    return (
        {
            record["name"]: (
                record["createStatement"],
                record["owningConstraint"],
            )
            for record in indexes
        },
        {record["name"]: record["createStatement"] for record in constraints},
    )


async def _gds_projection_names(db) -> frozenset[str]:
    projections = await db.run("CALL gds.graph.list() YIELD graphName RETURN graphName")
    return frozenset(record["graphName"] for record in projections)


def _relationship_sort_key(
    relationship: tuple[object | None, object | None, str, dict[str, object]],
) -> tuple[object, ...]:
    start_uid, end_uid, rel_type, properties = relationship
    return (
        (type(start_uid).__qualname__, repr(start_uid)),
        (type(end_uid).__qualname__, repr(end_uid)),
        rel_type,
        tuple(sorted((name, repr(value)) for name, value in properties.items())),
    )


async def _database_snapshot(db, require_unique_uids: bool = False) -> DatabaseSnapshot:
    nodes = await db.run(
        "MATCH (node) RETURN node.uid AS uid, labels(node) AS labels, "
        "properties(node) AS properties"
    )
    relationships = await db.run(
        "MATCH (start)-[relationship]->(end) "
        "RETURN start.uid AS start_uid, end.uid AS end_uid, "
        "type(relationship) AS type, "
        "properties(relationship) AS properties"
    )
    indexes, constraints = await _schema_snapshot(db)
    node_states: dict[str, tuple[tuple[str, ...], dict[str, object]]] = {}
    nodes_without_unique_uid = 0
    for record in nodes:
        uid = record["uid"]
        if not isinstance(uid, str) or uid in node_states:
            nodes_without_unique_uid += 1
            if require_unique_uids:
                raise AssertionError(
                    "Documentation tests require every existing node to have a "
                    "unique string uid."
                )
            continue
        node_states[uid] = (tuple(sorted(record["labels"])), record["properties"])

    relationship_states = tuple(
        sorted(
            (
                (
                    record["start_uid"],
                    record["end_uid"],
                    record["type"],
                    record["properties"],
                )
                for record in relationships
            ),
            key=_relationship_sort_key,
        )
    )
    return DatabaseSnapshot(
        nodes=node_states,
        relationships=relationship_states,
        nodes_without_unique_uid=nodes_without_unique_uid,
        indexes=indexes,
        constraints=constraints,
        gds_projections=await _gds_projection_names(db),
    )


def _quote_identifier(name: str) -> str:
    quote = chr(96)
    return f"{quote}{name.replace(quote, quote + quote)}{quote}"


async def _restore_database_snapshot(db, baseline: DatabaseSnapshot) -> None:
    current = await _database_snapshot(db)
    for graph_name in current.gds_projections - baseline.gds_projections:
        await db.run("CALL gds.graph.drop($graph_name)", {"graph_name": graph_name})

    graph_changed = (
        current.nodes != baseline.nodes
        or current.relationships != baseline.relationships
        or current.nodes_without_unique_uid > 0
    )

    if graph_changed:
        # Constraints can block restoring the original property values, so remove
        # schema first and recreate its saved definitions after restoring the graph.
        indexes, constraints = await _schema_snapshot(db)
        for name in constraints:
            await db.run(f"DROP CONSTRAINT {_quote_identifier(name)} IF EXISTS")
        indexes, _ = await _schema_snapshot(db)
        for name, definition in indexes.items():
            if baseline.indexes.get(name) != definition and definition[1] is None:
                await db.run(f"DROP INDEX {_quote_identifier(name)} IF EXISTS")

        await db.run("MATCH ()-[relationship]->() DELETE relationship")
        await db.run(
            "MATCH (node) WHERE node.uid IS NULL OR NOT node.uid IN $existing_uids "
            "DETACH DELETE node",
            {"existing_uids": list(baseline.nodes)},
        )
        await db.run(
            "MATCH (node) WITH node.uid AS uid, collect(node) AS matches "
            "WHERE uid IS NOT NULL AND size(matches) > 1 "
            "UNWIND matches AS duplicate DETACH DELETE duplicate"
        )

        current = await _database_snapshot(db)
        for uid, (labels, properties) in baseline.nodes.items():
            if uid not in current.nodes:
                create_labels = "".join(
                    f" SET node:{_quote_identifier(label)}" for label in labels
                )
                await db.run(
                    "CREATE (node) SET node = $properties" + create_labels,
                    {"properties": properties},
                )
            else:
                current_labels, _ = current.nodes[uid]
                for label in set(current_labels) - set(labels):
                    await db.run(
                        "MATCH (node) WHERE node.uid = $uid "
                        f"REMOVE node:{_quote_identifier(label)}",
                        {"uid": uid},
                    )
                for label in set(labels) - set(current_labels):
                    await db.run(
                        "MATCH (node) WHERE node.uid = $uid "
                        f"SET node:{_quote_identifier(label)}",
                        {"uid": uid},
                    )
                await db.run(
                    "MATCH (node) WHERE node.uid = $uid SET node = $properties",
                    {"uid": uid, "properties": properties},
                )

        for (
            start_uid,
            end_uid,
            rel_type,
            properties,
        ) in baseline.relationships:
            if start_uid is None or end_uid is None:
                raise AssertionError(
                    "Cannot restore a relationship without endpoint uids."
                )
            records = await db.run(
                "MATCH (start), (end) "
                "WHERE start.uid = $start_uid AND end.uid = $end_uid "
                f"CREATE (start)-[relationship:{_quote_identifier(rel_type)}]->(end) "
                "SET relationship = $properties "
                "RETURN count(relationship) AS count",
                {
                    "start_uid": start_uid,
                    "end_uid": end_uid,
                    "properties": properties,
                },
            )
            assert records[0]["count"] == 1, (
                "Could not restore a baseline relationship."
            )

        restored = await _database_snapshot(db, require_unique_uids=True)
        assert restored.nodes == baseline.nodes, (
            "Documentation examples did not restore the original nodes."
        )
        assert restored.relationships == baseline.relationships, (
            "Documentation examples did not restore the original relationships."
        )

        for name, statement in baseline.constraints.items():
            if statement is None:
                raise AssertionError(
                    f"Cannot restore constraint {name!r}: Neo4j returned no "
                    "create statement."
                )
            await db.run(statement)
        indexes, _ = await _schema_snapshot(db)
        for name, (statement, owning_constraint) in baseline.indexes.items():
            if name in indexes or owning_constraint is not None:
                continue
            if statement is None:
                raise AssertionError(
                    f"Cannot restore index {name!r}: Neo4j returned no "
                    "create statement."
                )
            await db.run(statement)
    else:
        indexes, constraints = await _schema_snapshot(db)
        for name, definition in constraints.items():
            if baseline.constraints.get(name) != definition:
                await db.run(f"DROP CONSTRAINT {_quote_identifier(name)} IF EXISTS")
        indexes, _ = await _schema_snapshot(db)
        for name, definition in indexes.items():
            if baseline.indexes.get(name) != definition:
                await db.run(f"DROP INDEX {_quote_identifier(name)} IF EXISTS")
        indexes, constraints = await _schema_snapshot(db)
        for name, statement in baseline.constraints.items():
            if name not in constraints:
                if statement is None:
                    raise AssertionError(
                        f"Cannot restore constraint {name!r}: Neo4j returned no "
                        "create statement."
                    )
                await db.run(statement)
        indexes, _ = await _schema_snapshot(db)
        for name, (statement, owning_constraint) in baseline.indexes.items():
            if name not in indexes and owning_constraint is None:
                if statement is None:
                    raise AssertionError(
                        f"Cannot restore index {name!r}: Neo4j returned no "
                        "create statement."
                    )
                await db.run(statement)

    restored = await _database_snapshot(db, require_unique_uids=True)
    assert restored.nodes == baseline.nodes, (
        "Documentation examples did not restore the original nodes."
    )
    assert restored.relationships == baseline.relationships, (
        "Documentation examples did not restore the original relationships."
    )
    assert restored.indexes == baseline.indexes, (
        "Documentation examples did not restore the original indexes."
    )
    assert restored.constraints == baseline.constraints, (
        "Documentation examples did not restore the original constraints."
    )
    assert restored.gds_projections == baseline.gds_projections, (
        "Documentation examples did not restore the original GDS projections."
    )


async def _run_page_blocks(
    db,
    path: Path,
    blocks: list[CodeBlock],
    tmp_path: Path,
    cleanup_ttl_job=None,
) -> subprocess.CompletedProcess[str]:
    baseline = await _database_snapshot(db, require_unique_uids=True)
    runner_path = tmp_path / "run_documentation_examples.py"
    runner_path.write_text(_page_runner_source(path, blocks), encoding="utf-8")
    try:
        return await asyncio.to_thread(
            subprocess.run,
            [sys.executable, str(runner_path)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
    finally:
        try:
            if cleanup_ttl_job is not None:
                await cleanup_ttl_job()
        finally:
            await _restore_database_snapshot(db, baseline)


@pytest.fixture
async def cleanup_ttl_job(db):
    async def cancel_and_check():
        await db.run(
            "CALL apoc.periodic.cancel($job_name)",
            {"job_name": "ttl_cleanup_job"},
        )
        jobs = await db.run("CALL apoc.periodic.list()")
        assert not any(job["name"] == "ttl_cleanup_job" for job in jobs)

    try:
        yield cancel_and_check
    finally:
        await cancel_and_check()


def test_s1_readme_is_a_clear_entry_point():
    readme, page = _read_page(ROOT / "README.md")
    headings = [
        "# node4j",
        "## Requirements",
        "## Installation",
        "## Quick start",
        "## Documentation",
    ]

    assert all(heading in readme for heading in headings)
    positions = [readme.index(heading) for heading in headings]
    assert positions == sorted(positions)
    assert "Python 3.12+" in readme
    assert "Neo4j 5.26 LTS" in readme
    assert "Neo4j 2026.09" in readme
    assert "APOC" in readme and "GDS" in readme
    assert "are needed only for their optional extensions" in readme
    assert "uv add git+https://github.com/gkeb/node4j" in readme
    assert "pip install git+https://github.com/gkeb/node4j" in readme
    assert "NODE4J_URI" in readme
    assert "NODE4J_USER" in readme
    assert "NODE4J_PASSWORD" in readme
    python_blocks = [block for block in page.blocks if block.language == "python"]
    assert len(python_blocks) == 1
    for block in python_blocks:
        compile(block.source, f"README.md block {block.number}", "exec")

    for guide in (ROOT / "docs" / "en").rglob("*.md"):
        assert guide.resolve() in {
            target for target, _ in _relative_links(ROOT / "README.md")
        }
    for guide in (ROOT / "docs" / "pl").rglob("*.md"):
        assert guide.resolve() in {
            target for target, _ in _relative_links(ROOT / "README_PL.md")
        }


def test_s1_markdown_links_exist_and_headings_are_accessible():
    for path in _all_pages():
        _, page = _read_page(path)
        levels = [level for level, _ in page.headings]
        assert levels.count(1) == 1, path.name
        assert all(
            current <= previous + 1 for previous, current in zip(levels, levels[1:])
        ), path.name
        for target, fragment in _relative_links(path):
            assert target.is_file(), f"{path.name} links to missing {target}"
            if fragment:
                _, target_page = _read_page(target)
                assert fragment in _heading_anchors(target_page.headings), (
                    f"{path.name} links to missing anchor #{fragment} in {target}"
                )


def test_s3_skip_markers_require_a_reason():
    fence = chr(96) * 3
    page = _parse_markdown(
        f"<!-- docs-test: skip: Needs an APOC plugin. -->\n"
        f"{fence}python\nraise RuntimeError()\n{fence}"
    )
    assert page.blocks[0].skip_reason == "Needs an APOC plugin."

    with pytest.raises(ValueError, match="reason"):
        _parse_markdown(
            f"<!-- docs-test: skip -->\n{fence}python\nraise RuntimeError()\n{fence}"
        )


def test_s3_skipped_block_is_omitted_and_reported():
    fence = chr(96) * 3
    page = _parse_markdown(
        f"<!-- docs-test: skip: Requires an optional plugin. -->\n"
        f"{fence}python\nraise RuntimeError('must not run')\n{fence}\n"
        f"{fence}python\nprint('still runs')\n{fence}"
    )
    script = _page_runner_source(ROOT / "README.md", _python_blocks(page))

    assert "must not run" not in script
    assert "still runs" in script
    assert "block 1: Requires an optional plugin." in _skip_report(
        ROOT / "README.md", _python_blocks(page)[:1]
    )


def test_s3_skipped_block_report_does_not_skip_the_page():
    fence = chr(96) * 3
    page = _parse_markdown(
        f"<!-- docs-test: skip: Requires an optional plugin. -->\n"
        f"{fence}python\nraise RuntimeError()\n{fence}"
    )

    class Node:
        user_properties = []

    class Request:
        node = Node()

    with pytest.warns(UserWarning, match="Requires an optional plugin"):
        _report_skipped_blocks(ROOT / "README.md", _python_blocks(page), Request())

    assert Request.node.user_properties == [
        (
            "skipped_documentation_blocks",
            "README.md skipped documentation examples: block 1: "
            "Requires an optional plugin.",
        )
    ]


def test_s2_page_runner_shares_names_and_supports_top_level_await(tmp_path):
    blocks = [
        CodeBlock(1, "python", "import asyncio\nimport node4j\nvalue = 41", None),
        CodeBlock(
            2,
            "python",
            "await asyncio.sleep(0)\nassert value + 1 == 42",
            None,
        ),
    ]
    runner_path = tmp_path / "run_examples.py"
    runner_path.write_text(
        _page_runner_source(ROOT / "README.md", blocks), encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(runner_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr


def test_s2_page_runner_keeps_one_event_loop_across_blocks(tmp_path):
    blocks = [
        CodeBlock(
            1,
            "python",
            "import asyncio\n"
            "class LoopBoundResource:\n"
            "    def __init__(self):\n"
            "        self.loop = asyncio.get_running_loop()\n"
            "resource = LoopBoundResource()\n"
            "await asyncio.sleep(0)",
            None,
        ),
        CodeBlock(
            2,
            "python",
            "assert resource.loop is asyncio.get_running_loop()\n"
            "await asyncio.sleep(0)",
            None,
        ),
    ]
    runner_path = tmp_path / "run_examples.py"
    runner_path.write_text(
        _page_runner_source(ROOT / "README.md", blocks), encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(runner_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr


def test_s2_page_runner_supports_standalone_asyncio_run(tmp_path):
    blocks = [
        CodeBlock(
            1,
            "python",
            "import asyncio\n"
            "value = []\n"
            "async def main():\n"
            "    value.append(41)\n"
            "asyncio.run(main())",
            None,
        ),
        CodeBlock(2, "python", "await asyncio.sleep(0)\nassert value == [41]", None),
    ]
    runner_path = tmp_path / "run_examples.py"
    runner_path.write_text(
        _page_runner_source(ROOT / "README.md", blocks), encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(runner_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr


def test_s2_page_runner_reports_the_failing_block(tmp_path):
    blocks = [
        CodeBlock(1, "python", "value = 41", None),
        CodeBlock(2, "python", "raise RuntimeError('broken example')", None),
    ]
    runner_path = tmp_path / "run_examples.py"
    runner_path.write_text(
        _page_runner_source(ROOT / "README.md", blocks), encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(runner_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )

    assert result.returncode != 0
    assert "README.md Python block 2 failed" in result.stderr
    assert "broken example" in result.stderr


def test_s4_english_and_polish_pages_are_mirrored():
    english = {_page_key(path, "en"): path for path in _english_pages()}
    polish = {_page_key(path, "pl"): path for path in _polish_pages()}
    assert set(english) == set(polish)
    assert {
        "apoc-extensions.md",
        "gds-extensions.md",
        "bulk-operations-and-aggregations.md",
        "transactions.md",
        "mixins.md",
        "configuration-and-logging.md",
    } <= set(english)

    for key, english_path in english.items():
        _, english_page = _read_page(english_path)
        _, polish_page = _read_page(polish[key])
        assert Counter(level for level, _ in english_page.headings) == Counter(
            level for level, _ in polish_page.headings
        ), key
        assert [(block.language, block.source) for block in english_page.blocks] == [
            (block.language, block.source) for block in polish_page.blocks
        ], key
        assert polish[key].resolve() in {
            target for target, _ in _relative_links(english_path)
        }, f"{english_path.name} needs a Polish language link"
        if english_path.name == "apoc-extensions.md":
            assert (ROOT / "README.md").resolve() in {
                target for target, _ in _relative_links(english_path)
            }, f"{english_path.name} needs a README link"
        assert english_path.resolve() in {
            target for target, _ in _relative_links(polish[key])
        }, f"{polish[key].name} needs an English language link"
        if polish[key].name == "apoc-extensions.md":
            assert (ROOT / "README_PL.md").resolve() in {
                target for target, _ in _relative_links(polish[key])
            }, f"{polish[key].name} needs a Polish README link"


def test_s9_apoc_files_are_read_and_written_by_the_neo4j_server():
    english_path = ROOT / "docs" / "en" / "apoc-extensions.md"
    polish_path = ROOT / "docs" / "pl" / "apoc-extensions.md"
    english, _ = _read_page(english_path)
    polish, _ = _read_page(polish_path)

    for source in (english, polish):
        assert "NEO4J_apoc_import_file_enabled=true" in source
        assert "NEO4J_apoc_export_file_enabled=true" in source
        assert "file:///" in source
        assert "apoc.import.file.enabled=true" in source
        assert "Import from files not enabled" in source

    assert "Neo4j server" in english
    assert "serwerze Neo4j" in polish
    assert (
        "`file:///people.json` means `people.json` in that server's import directory"
        in english
    )
    assert (
        "`file:///people.json` oznacza plik `people.json` "
        "w katalogu import tego serwera" in polish
    )
    assert "user-controlled URLs" in english
    assert "kontrolowanych przez użytkownika" in polish
    assert "credentials or tokens" in english
    assert "danych logowania ani tokenów" in polish
    assert "test database" in english
    assert "bazie testowej" in polish
    assert "does not recommend it for production" in english
    assert "nie zaleca tej metody na produkcji" in polish


def test_s9_apoc_file_access_is_enabled_for_local_and_ci_test_databases():
    agent_instructions = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
    ci_workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8-sig"
    )

    for setting in (
        "NEO4J_apoc_import_file_enabled",
        "NEO4J_apoc_export_file_enabled",
    ):
        assert f"-e {setting}=true" in agent_instructions
        assert ci_workflow.count(f'{setting}: "true"') == 2


def test_s10_gds_versions_security_and_missing_projection_are_documented():
    source = (ROOT / "docs" / "en" / "gds-extensions.md").read_text(
        encoding="utf-8-sig"
    )

    assert "| 5.26 LTS | 2.13 |" in source
    assert "| 2026.09 | 2026.09 |" in source
    assert "NEO4J_PLUGINS" in source
    assert "never pass a user-provided algorithm name" in source
    assert "failIfMissing=true" in source
    assert "does not expose that option" in source


def test_s10_gds_is_enabled_for_local_and_ci_test_databases():
    agent_instructions = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
    ci_workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8-sig"
    )

    expected_plugins = '["apoc", "graph-data-science"]'
    assert expected_plugins in agent_instructions
    assert ci_workflow.count(expected_plugins) == 2


async def test_s10_gds_documentation_examples_execute(db, tmp_path, cleanup_ttl_job):
    path = ROOT / "docs" / "en" / "gds-extensions.md"
    _, page = _read_page(path)
    blocks = _python_blocks(page)

    assert blocks
    assert all(block.skip_reason is None for block in blocks)

    result = await _run_page_blocks(
        db, path, blocks, tmp_path, cleanup_ttl_job=cleanup_ttl_job
    )
    assert result.returncode == 0, (
        f"{path.name} documentation example failed:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def test_s5_models_and_queries_methods_are_in_executable_examples():
    page_paths = [
        ROOT / "docs" / "en" / "models-and-schema.md",
        ROOT / "docs" / "en" / "queries-and-filters.md",
    ]
    executable_sources = []
    for path in page_paths:
        _, page = _read_page(path)
        executable_sources.extend(
            block.source for block in _python_blocks(page) if block.skip_reason is None
        )
    source = "\n".join(executable_sources)

    for method in (
        "apply_schema",
        "create",
        "match_one",
        "match_all",
        "update",
        "delete",
        "get_or_create",
        "update_or_create",
        "count",
    ):
        assert re.search(rf"\.q\.{method}\s*\(", source), method

    assert re.search(r"\bQ\s*\(", source)
    for operator in (
        "gt",
        "gte",
        "lt",
        "lte",
        "in",
        "contains",
        "startswith",
        "endswith",
        "ne",
    ):
        assert re.search(rf"__{operator}\s*=", source), operator
    assert "order_by=" in source
    for hook in ("pre_save", "post_save", "pre_delete", "post_delete"):
        assert re.search(rf"async def {hook}\s*\(", source), hook

    english_text = _read_page(page_paths[1])[0].lower()
    polish_path = ROOT / "docs" / "pl" / "queries-and-filters.md"
    polish_text = _read_page(polish_path)[0].lower()
    assert "unknown suffix" in english_text and "equality" in english_text
    assert "nieznany sufiks" in polish_text and "równość" in polish_text


def test_s5_relationships_update_and_prefetch_are_in_executable_examples():
    path = ROOT / "docs" / "en" / "relationships.md"
    _, page = _read_page(path)
    source = "\n".join(
        block.source for block in _python_blocks(page) if block.skip_reason is None
    )

    for public_api in (
        "RelationshipProperty",
        "RelationshipDirection.IN",
        "RelationshipDirection.OUT",
        "RelationshipDirection.UNDIRECTED",
        "model=GuideAuthorship",
        ".connect(",
        ".disconnect(",
        ".q.update_relationship(",
        "prefetch={",
    ):
        assert public_api in source, public_api


def test_s5_bulk_operations_and_aggregations_are_in_executable_examples():
    english_path = ROOT / "docs" / "en" / "bulk-operations-and-aggregations.md"
    polish_path = ROOT / "docs" / "pl" / "bulk-operations-and-aggregations.md"
    _, english_page = _read_page(english_path)
    english_source = "\n".join(
        block.source
        for block in _python_blocks(english_page)
        if block.skip_reason is None
    )

    for method in ("bulk_create", "bulk_update", "aggregate"):
        assert re.search(rf"\.q\.{method}\s*\(", english_source), method
    assert 'match_on="sku"' in english_source
    for hook in ("pre_save", "post_save"):
        assert re.search(rf"async def {hook}\s*\(", english_source), hook

    english_text, _ = _read_page(english_path)
    polish_text, _ = _read_page(polish_path)
    assert (
        "aggregation expressions and their aliases are inserted directly"
        in english_text
    )
    assert "trusted, developer-written expressions and aliases" in english_text
    assert "never pass user input" in english_text
    assert "wyrażeń agregacji i ich aliasy trafiają bezpośrednio" in polish_text
    assert "zaufanych wyrażeń i aliasów zapisanych przez programistę" in polish_text
    assert "danych użytkownika" in polish_text


def test_s5_transactions_are_in_executable_examples():
    path = ROOT / "docs" / "en" / "transactions.md"
    _, page = _read_page(path)
    source = "\n".join(
        block.source for block in _python_blocks(page) if block.skip_reason is None
    )

    assert "async with connection.transaction():" in source
    assert "@connection.atomic()" in source
    assert 'raise ValueError("rollback example")' in source
    assert re.search(r"except RuntimeError(?:\s+as\s+\w+)?:", source)
    assert "nested_transaction_rejected" in source
    assert 'filters={"label": rollback_label}' in source


def test_s5_mixins_and_configuration_are_in_executable_examples():
    page_paths = [
        ROOT / "docs" / "en" / "mixins.md",
        ROOT / "docs" / "en" / "configuration-and-logging.md",
    ]
    executable_sources = []
    for path in page_paths:
        _, page = _read_page(path)
        executable_sources.extend(
            block.source for block in _python_blocks(page) if block.skip_reason is None
        )
    source = "\n".join(executable_sources)

    for method in (
        "set_expiry",
        "save_with_expiry",
        "setup_ttl_infrastructure",
        "soft_delete",
        "restore",
        "setup_soft_delete_manager",
    ):
        assert re.search(rf"\.{method}\s*\(", source), method

    assert ".all_objects" in source
    for variable in ("NODE4J_URI", "NODE4J_USER", "NODE4J_PASSWORD"):
        assert variable in source


def test_s5_apoc_methods_are_in_executable_examples():
    path = ROOT / "docs" / "en" / "apoc-extensions.md"
    _, page = _read_page(path)
    source = "\n".join(
        block.source for block in _python_blocks(page) if block.skip_reason is None
    )

    assert "await apoc.version()" in source
    assert "await apoc.Periodic.iterate(" in source
    assert "CALL apoc.periodic.iterate(" in source
    assert "params: {marker: $marker}" in source
    assert "await apoc.Export.to_json(" in source
    assert ".apoc.create_from_json(" in source


def test_s5_gds_methods_are_in_executable_examples():
    path = ROOT / "docs" / "en" / "gds-extensions.md"
    _, page = _read_page(path)
    source = "\n".join(
        block.source for block in _python_blocks(page) if block.skip_reason is None
    )

    for method in (
        "gds.Graph.project(",
        "gds.Algo.run(",
        "gds.Algo.mutate(",
        "gds.Graph.drop(",
    ):
        assert method in source, method


def test_s5_complete_coverage_inventory_is_in_executable_examples():
    source = "\n".join(
        _remove_python_comments(block.source)
        for path in _english_pages()
        for block in _python_blocks(_read_page(path)[1])
        if block.skip_reason is None
    )

    manager_methods = (
        "apply_schema",
        "create",
        "match_one",
        "match_all",
        "update",
        "delete",
        "get_or_create",
        "update_or_create",
        "count",
        "aggregate",
        "bulk_create",
        "bulk_update",
        "update_relationship",
    )
    for method in manager_methods:
        assert re.search(rf"\.q\.{method}\s*\(", source), method

    for public_api in (
        "RelationshipProperty",
        "RelationshipDirection.IN",
        "RelationshipDirection.OUT",
        "RelationshipDirection.UNDIRECTED",
        ".connect(",
        ".disconnect(",
        "await author.books",
        "prefetch={",
        "Q(",
        "async def pre_save(",
        "async def post_save(",
        "async def pre_delete(",
        "async def post_delete(",
        "connection.transaction()",
        "@connection.atomic()",
        "set_expiry(",
        "save_with_expiry(",
        "setup_ttl_infrastructure(",
        "soft_delete(",
        "restore(",
        "setup_soft_delete_manager(",
        ".all_objects",
        "NODE4J_URI",
        "NODE4J_USER",
        "NODE4J_PASSWORD",
        "await apoc.version()",
        "apoc.Periodic.iterate(",
        "apoc.Export.to_json(",
        ".apoc.create_from_json(",
        "gds.Graph.project(",
        "gds.Algo.run(",
        "gds.Algo.mutate(",
        "gds.Graph.drop(",
    ):
        assert public_api in source, public_api

    for operator in (
        "gt",
        "gte",
        "lt",
        "lte",
        "in",
        "contains",
        "startswith",
        "endswith",
        "ne",
    ):
        assert re.search(rf"__{operator}\s*=", source), operator


def test_s5_coverage_ignores_commented_out_calls():
    source = _remove_python_comments(
        "# await GuidePerson.q.create(name='not executed')\n"
        "await GuidePerson.q.match_all()  # .q.delete()\n"
    )

    assert ".q.create(" not in source
    assert ".q.match_all(" in source
    assert ".q.delete(" not in source


def test_s7_documentation_does_not_promise_unimplemented_features():
    csv_import_pattern = re.compile(
        r"\bconnect_from_csv\b|\bcsv\s+import\w*\b|"
        r"\bimport\w*(?:\s+(?:from|z))?\s+csv\b",
        flags=re.IGNORECASE,
    )
    for phrase in (
        "connect_from_csv",
        "CSV import",
        "CSV imports",
        "import from CSV",
        "import CSV",
        "importing CSV",
        "importing from CSV",
        "import z CSV",
        "importowanie CSV",
        "importowanie z CSV",
    ):
        assert csv_import_pattern.search(phrase), phrase

    trigger_pattern = re.compile(
        r"\b(?:apoc\.trigger|trigger\w*)\b",
        flags=re.IGNORECASE,
    )
    for phrase in (
        "APOC trigger",
        "triggers",
        "triggery",
        "triggerów",
        "triggerami",
        "triggerach",
    ):
        assert trigger_pattern.search(phrase), phrase

    for path in _all_pages():
        source, _ = _read_page(path)
        assert not csv_import_pattern.search(source), path.name
        mentions_triggers = trigger_pattern.search(source)
        if mentions_triggers:
            assert path.stem in {"known-limitations", "znane-ograniczenia"}


def test_s6_known_limitations_are_explained_in_both_languages():
    expected_phrases = {
        "en": (
            "triggers",
            "default database",
            "datetime values",
            "uid",
            "stored as text",
            "unknown suffix",
            "equality",
            "registry",
            "class name",
            "connection.queries",
            "grows",
            "DEBUG",
            "ERROR",
            "parameters",
            "What to do:",
        ),
        "pl": (
            "triggerami",
            "domyślnej bazie",
            "daty",
            "uid",
            "jako tekst",
            "nieznany sufiks",
            "równość",
            "rejestr",
            "nazwą klasy",
            "connection.queries",
            "rośnie",
            "DEBUG",
            "ERROR",
            "parametry",
            "Co zrobić:",
        ),
    }
    for language, phrases in expected_phrases.items():
        stem = "known-limitations"
        source, _ = _read_page(ROOT / "docs" / language / f"{stem}.md")
        normalized = source.lower()
        for phrase in phrases:
            assert phrase.lower() in normalized, (language, phrase)
        action_label = "What to do:" if language == "en" else "Co zrobić:"
        assert source.count(action_label) == 6

    linked_pages = {
        "en": (
            ("README.md", "docs/en/known-limitations.md"),
            ("docs/en/models-and-schema.md", "known-limitations.md"),
            ("docs/en/queries-and-filters.md", "known-limitations.md"),
            ("docs/en/configuration-and-logging.md", "known-limitations.md"),
        ),
        "pl": (
            ("README_PL.md", "docs/pl/known-limitations.md"),
            ("docs/pl/models-and-schema.md", "known-limitations.md"),
            ("docs/pl/queries-and-filters.md", "known-limitations.md"),
            ("docs/pl/configuration-and-logging.md", "known-limitations.md"),
        ),
    }
    for language_pages in linked_pages.values():
        for page_name, target in language_pages:
            page_path = ROOT / page_name
            _, page = _read_page(page_path)
            assert target in page.links, (page_name, target)


def test_s8_configuration_uses_only_builtin_settings():
    readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
    all_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in _all_pages())

    assert "NODE4J_URI=bolt://127.0.0.1:7687" in readme
    assert "NODE4J_USER=neo4j" in readme
    assert "NODE4J_PASSWORD=change-me" in readme
    assert "automatically" in readme
    assert not re.search(r"load_dotenv|python-dotenv", all_text, re.IGNORECASE)


def test_s11_documentation_does_not_clear_every_node():
    for path in _all_pages():
        _, page = _read_page(path)
        for block in page.blocks:
            assert not _has_full_database_clear(block.source), (
                f"{path.name} block {block.number} clears every node"
            )


def test_documentation_does_not_use_absolute_apoc_file_paths():
    absolute_apoc_path = re.compile(
        r"file:///(?:[a-z]:/|(?:path/to|home|users|var|tmp|mnt|etc)/)",
        flags=re.IGNORECASE,
    )
    for path in _all_pages():
        source, _ = _read_page(path)
        assert absolute_apoc_path.search(source) is None, path.name


def test_s11_full_database_clear_detector_rejects_a_bad_example():
    assert _has_full_database_clear('await connection.run("MATCH (n) DETACH DELETE n")')
    assert not _has_full_database_clear(
        'await connection.run("MATCH (n:Person) DETACH DELETE n")'
    )


@pytest.mark.parametrize(
    "path",
    _english_pages(),
    ids=lambda path: path.relative_to(ROOT).as_posix(),
)
async def test_s2_english_documentation_examples_execute(
    db, tmp_path, path, request, cleanup_ttl_job
):
    _, page = _read_page(path)
    blocks = _python_blocks(page)
    executable = [block for block in blocks if block.skip_reason is None]
    skipped = [block for block in blocks if block.skip_reason is not None]
    for block in blocks:
        assert not _has_full_database_clear(block.source), (
            f"{path.name} block {block.number} clears every node"
        )
    if not executable:
        _report_skipped_blocks(path, skipped, request)
        return

    result = await _run_page_blocks(
        db, path, blocks, tmp_path, cleanup_ttl_job=cleanup_ttl_job
    )
    assert result.returncode == 0, (
        f"{path.name} documentation example failed:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    _report_skipped_blocks(path, skipped, request)


async def test_s11_page_state_is_restored_after_an_example_error(
    db, tmp_path, cleanup_ttl_job
):
    suffix = uuid4().hex
    baseline_marker = f"baseline_{suffix}"
    removed_marker = f"removed_{suffix}"
    baseline_uid = str(uuid4())
    removed_uid = str(uuid4())
    index_name = f"docs_probe_index_{suffix}"
    constraint_name = f"docs_probe_constraint_{suffix}"
    baseline_graph_name = f"docs_baseline_{suffix}"
    failure_graph_name = f"docs_failure_{suffix}"
    original_projections = await _gds_projection_names(db)
    try:
        await db.run(
            "CREATE (first:`DocsBaseline`:`DocsOriginal` "
            "{`uid`: $first_uid, `marker`: $marker, `value`: $kept}), "
            "(second:`DocsBaseline` "
            "{`uid`: $removed_uid, `marker`: $removed, `value`: $restored}), "
            "(first)-[:`DOCS_LINK` {`value`: $relationship_value}]->(second)",
            {
                "first_uid": baseline_uid,
                "marker": baseline_marker,
                "kept": "kept",
                "removed_uid": removed_uid,
                "removed": removed_marker,
                "restored": "restored",
                "relationship_value": "original",
            },
        )
        await db.run(
            "CALL gds.graph.project($graph_name, $node_projection, "
            "$relationship_projection)",
            {
                "graph_name": baseline_graph_name,
                "node_projection": "DocsBaseline",
                "relationship_projection": {"DOCS_LINK": {"orientation": "UNDIRECTED"}},
            },
        )
        baseline_projections = original_projections | {baseline_graph_name}
        before = await _schema_snapshot(db)
        source = f'''
import asyncio

from node4j.db import connection
from node4j.ext.gds import gds
from node4j.mixins import TTLMixin


async def main():
    await TTLMixin.setup_ttl_infrastructure()
    await connection.run(
        "MATCH (node:`DocsBaseline` {{`marker`: $marker}}) "
        "SET node.`value` = $changed SET node:`DocsChanged`",
        {{"marker": "{baseline_marker}", "changed": "changed"}},
    )
    await connection.run(
        "MATCH (node:`DocsBaseline` {{`marker`: $marker}}) DETACH DELETE node",
        {{"marker": "{removed_marker}"}},
    )
    await connection.run(
        "CREATE (:`DocsProbe` "
        "{{`index_value`: $value, `unique_value`: $value}})",
        {{"value": "{suffix}"}},
    )
    await connection.run(
        "CREATE INDEX {chr(96)}{index_name}{chr(96)} IF NOT EXISTS "
        "FOR (node:`DocsProbe`) ON (node.`index_value`)"
    )
    await connection.run(
        "CREATE CONSTRAINT {chr(96)}{constraint_name}{chr(96)} IF NOT EXISTS "
        "FOR (node:`DocsProbe`) REQUIRE node.`unique_value` IS UNIQUE"
    )
    await gds.Graph.project(
        "{failure_graph_name}",
        "DocsBaseline",
        {{"DOCS_LINK": {{"orientation": "UNDIRECTED"}}}},
    )
    raise RuntimeError("intentional documentation example failure")


asyncio.run(main())
'''
        block = CodeBlock(1, "python", source, None)
        result = await _run_page_blocks(
            db,
            ROOT / "docs" / "en" / "failing-example.md",
            [block],
            tmp_path,
            cleanup_ttl_job=cleanup_ttl_job,
        )

        assert result.returncode != 0
        assert "failing-example.md Python block 1 failed" in result.stderr
        assert "intentional documentation example failure" in result.stderr
        restored_nodes = await db.run(
            "MATCH (node:`DocsBaseline`) WHERE node.`marker` IN $markers "
            "RETURN labels(node) AS labels, node.`marker` AS marker, "
            "node.`value` AS value ORDER BY marker",
            {"markers": [baseline_marker, removed_marker]},
        )
        assert [dict(record) for record in restored_nodes] == [
            {
                "labels": ["DocsBaseline", "DocsOriginal"],
                "marker": baseline_marker,
                "value": "kept",
            },
            {
                "labels": ["DocsBaseline"],
                "marker": removed_marker,
                "value": "restored",
            },
        ]
        restored_relationships = await db.run(
            "MATCH (first:`DocsBaseline` {`marker`: $first}) "
            "-[relationship:`DOCS_LINK`]->"
            "(second:`DocsBaseline` {`marker`: $second}) "
            "RETURN relationship.`value` AS value",
            {"first": baseline_marker, "second": removed_marker},
        )
        assert [dict(record) for record in restored_relationships] == [
            {"value": "original"}
        ]
        restored_schema = await _schema_snapshot(db)
        assert restored_schema == before
        assert await _gds_projection_names(db) == baseline_projections
        assert (
            await db.run(
                "MATCH (node:`DocsProbe` {`unique_value`: $value}) RETURN node",
                {"value": suffix},
            )
            == []
        )
    finally:
        current_projections = await _gds_projection_names(db)
        for graph_name in current_projections - original_projections:
            await db.run("CALL gds.graph.drop($graph_name)", {"graph_name": graph_name})
        await db.run(f"DROP CONSTRAINT {_quote_identifier(constraint_name)} IF EXISTS")
        await db.run(f"DROP INDEX {_quote_identifier(index_name)} IF EXISTS")
        await db.run(
            "MATCH (node:`DocsProbe` {`unique_value`: $value}) DETACH DELETE node",
            {"value": suffix},
        )
        await db.run(
            "MATCH (node:`DocsBaseline`) WHERE node.`marker` IN $markers "
            "DETACH DELETE node",
            {"markers": [baseline_marker, removed_marker]},
        )


def test_s12_missing_test_database_uses_public_pytest_runner(tmp_path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as unavailable_database:
        unavailable_database.bind(("127.0.0.1", 0))
        port = unavailable_database.getsockname()[1]
        test_uri = f"bolt://127.0.0.1:{port}"

        def run_documentation_tests(*, database_required, basetemp_name):
            child_env = {
                name: os.environ[name]
                for name in ("PATH", "SYSTEMROOT", "TEMP", "TMP")
                if name in os.environ
            }
            child_env.update(
                {
                    "NODE4J_TEST_URI": test_uri,
                    "NODE4J_URI": test_uri,
                    "NODE4J_TEST_USER": "neo4j",
                    "NODE4J_USER": "neo4j",
                    "NODE4J_TEST_PASSWORD": "test-password-123",
                    "NODE4J_PASSWORD": "test-password-123",
                    "PYTHONUTF8": "1",
                }
            )
            if database_required:
                child_env["NODE4J_REQUIRE_TEST_DB"] = "1"

            return subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-v",
                    "-rA",
                    "-p",
                    "no:cacheprovider",
                    "--basetemp",
                    str(tmp_path / basetemp_name),
                    "-k",
                    "not test_s12_missing_test_database_uses_public_pytest_runner "
                    "and (not test_s2_english_documentation_examples_execute "
                    "or README)",
                    "tests/test_documentation.py",
                ],
                cwd=ROOT,
                env=child_env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
                check=False,
            )

        optional_database = run_documentation_tests(
            database_required=False, basetemp_name="optional-database"
        )
        optional_report = optional_database.stdout + optional_database.stderr
        assert optional_database.returncode == 0, optional_report
        for test_name in (
            "test_s1_markdown_links_exist_and_headings_are_accessible",
            "test_s4_english_and_polish_pages_are_mirrored",
            "test_s7_documentation_does_not_promise_unimplemented_features",
        ):
            assert any(
                test_name in line and "PASSED" in line
                for line in optional_report.splitlines()
            ), optional_report
        for test_name in (
            "test_s2_english_documentation_examples_execute",
            "test_s10_gds_documentation_examples_execute",
            "test_s11_page_state_is_restored_after_an_example_error",
        ):
            assert any(
                test_name in line and "SKIPPED" in line
                for line in optional_report.splitlines()
            ), optional_report

        required_database = run_documentation_tests(
            database_required=True, basetemp_name="required-database"
        )
        required_report = required_database.stdout + required_database.stderr
        assert required_database.returncode != 0, required_report
        assert "test_s2_english_documentation_examples_execute" in required_report
        assert "Wymagana baza testowa Neo4j jest niedostępna" in required_report
