#!/usr/bin/env python3
"""Every SQL block in the catalog's AGENTS.md files has to run.

A recipe that fails on the first try costs the reader the time to debug
someone else's mistake, so this gate runs each one through DuckDB and fails
on any error. It also fails when no block is found, because then the
docs lost their examples.

The queries read the published bucket over HTTP. That is the point of the
check: it catches a moved asset, a renamed column, or a stale URL before a
reader does. Set QUERY_CHECK_REMOTE=0 to skip the blocks that read a remote
URL, for a gate that must run before the data is uploaded. Set
QUERY_LOCAL=1 to run every block against the local data files instead: the
public base URL is replaced by the local catalog/ path. The refresh job uses
this to test new data before it uploads it.

Blocks that open with WHERE are fragments and are skipped. Only ```sql fences
run; ```python and ```bash fences are prose.

QUERY_WORKERS blocks (default 8) run at once, so a remote run overlaps its
HTTP waits. Each worker has its own connection, because an ATTACH belongs
to the database instance and every cursor of a connection would see it.
The workers share half the machine's cores and memory, so a run leaves the
rest of the machine usable. QUERY_THREADS and QUERY_MEMORY override the two
totals. After each block the worker detaches what the block attached, as a
reader who runs the block in a fresh session would have it.

    python3 tests/test_queries.py
    QUERY_ONLY=limites python3 tests/test_queries.py   # one subtree
    QUERY_LOCAL=1 python3 tests/test_queries.py        # local data files
"""
from __future__ import annotations

import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from importlib.util import find_spec
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
REMOTE = ("https://", "s3://")
TIMEOUT = 900
WORKERS = int(os.environ.get("QUERY_WORKERS", "8"))
FENCE = re.compile(r"```sql\n(.*?)```", re.S)
LOCAL = os.environ.get("QUERY_LOCAL", "0") == "1"


def public_base() -> str:
    sys.path.insert(0, str(ROOT / "tools"))
    from publish import load_config

    return load_config()["public_base"].rstrip("/")


def sql_blocks():
    """Yield (label, sql, is_remote) for every runnable block."""
    only = os.environ.get("QUERY_ONLY", "")
    base = public_base() if LOCAL else None
    for md in sorted(CATALOG.glob("**/AGENTS.md")):
        rel = md.relative_to(CATALOG)
        if only and not str(rel).startswith(only):
            continue
        for i, m in enumerate(FENCE.finditer(md.read_text())):
            sql = m.group(1).strip()
            if sql.upper().startswith("WHERE"):
                continue
            if base:
                sql = sql.replace(base, str(CATALOG))
            yield f"{rel}#{i}", sql, any(p in sql for p in REMOTE)


def limits(workers: int = 1) -> tuple[int, int]:
    """Threads and memory in MB for one of `workers` connections."""
    threads = int(os.environ.get("QUERY_THREADS")
                  or max(1, (os.cpu_count() or 2) // 2))
    env = os.environ.get("QUERY_MEMORY", "")
    if env:
        number = float(env.upper().rstrip("B").rstrip("GM"))
        memory = number * (1024 if env.upper().rstrip("B").endswith("G")
                           else 1)
    else:
        memory = (os.sysconf("SC_PAGE_SIZE")
                  * os.sysconf("SC_PHYS_PAGES") / 2 / 2**20)
    return max(1, threads // workers), max(256, int(memory // workers))


def connect(workers: int = 1):
    """A connection with the extensions loaded and its share of the limits."""
    import duckdb

    threads, memory = limits(workers)
    con = duckdb.connect(config={"threads": threads,
                                 "memory_limit": f"{memory}MB"})
    con.execute("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
    return con


def run(con, sql: str) -> tuple[int, str]:
    """Run one block; interrupt it after TIMEOUT seconds."""
    import duckdb

    timer = threading.Timer(TIMEOUT, con.interrupt)
    timer.start()
    before = attached(con)
    try:
        result = con.execute(sql)
        if result.description:
            # Arrow, not Python objects: a TIMESTAMPTZ converts to Python
            # only with pytz installed, and the gate checks the query, not
            # the client's conversion.
            result.fetch_arrow_table()
        return 0, ""
    except duckdb.Error as exc:
        if not timer.is_alive():
            return 1, f"timed out after {TIMEOUT}s"
        return 1, str(exc).splitlines()[0][:300]
    finally:
        timer.cancel()
        for name in attached(con) - before:
            con.execute(f'DETACH "{name}"')


def attached(con) -> set[str]:
    return {row[0] for row in con.execute(
        "SELECT database_name FROM duckdb_databases() WHERE NOT internal"
    ).fetchall()}


def main() -> int:
    if find_spec("duckdb") is None:
        print("FAIL: the duckdb module is not installed; this gate checks "
              "nothing")
        print("      pip install -r tools/requirements.txt")
        return 1
    run_remote = os.environ.get("QUERY_CHECK_REMOTE", "1") != "0"
    blocks = list(sql_blocks())
    if not blocks:
        print("FAIL: no SQL blocks found; the docs lost their examples")
        return 1
    todo = [(label, sql) for label, sql, remote in blocks
            if run_remote or not remote]
    skipped = len(blocks) - len(todo)
    os.chdir(CATALOG)
    workers = min(WORKERS, len(todo)) or 1
    local = threading.local()

    def run_block(block):
        if not hasattr(local, "con"):
            local.con = connect(workers)
        return block[0], *run(local.con, block[1])

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(run_block, todo))
    failures = [(label, why) for label, code, why in results if code]
    for label, why in failures:
        print(f"FAIL {label}: {why}")
    tail = f", {skipped} remote skipped" if skipped else ""
    if failures:
        print(f"FAIL: {len(failures)}/{len(todo)} documented queries "
              f"failed{tail}")
        return 1
    print(f"PASS: {len(todo)} documented queries run{tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
