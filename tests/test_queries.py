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

One connection runs every block in turn. It loads spatial and httpfs once
and uses at most half the machine's cores and memory, so a local run leaves
the rest of the machine usable. QUERY_THREADS and QUERY_MEMORY override the
two limits.

    python3 tests/test_queries.py
    QUERY_ONLY=limites python3 tests/test_queries.py   # one subtree
    QUERY_LOCAL=1 python3 tests/test_queries.py        # local data files
"""
from __future__ import annotations

import os
import re
import sys
import threading
from importlib.util import find_spec
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
REMOTE = ("https://", "s3://")
TIMEOUT = 900
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


def connect():
    """One connection with the extensions loaded and half the machine."""
    import duckdb

    threads = int(os.environ.get("QUERY_THREADS")
                  or max(1, (os.cpu_count() or 2) // 2))
    memory = os.environ.get("QUERY_MEMORY") or (
        f"{os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') // 2**31}GB")
    con = duckdb.connect(config={"threads": threads, "memory_limit": memory})
    con.execute("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
    return con


def run(con, sql: str) -> tuple[int, str]:
    """Run one block; interrupt it after TIMEOUT seconds."""
    import duckdb

    timer = threading.Timer(TIMEOUT, con.interrupt)
    timer.start()
    try:
        con.execute(sql).fetchall()
        return 0, ""
    except duckdb.Error as exc:
        if not timer.is_alive():
            return 1, f"timed out after {TIMEOUT}s"
        return 1, str(exc).splitlines()[0][:300]
    finally:
        timer.cancel()


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
    con = connect()
    failures = []
    for label, sql in todo:
        code, why = run(con, sql)
        if code:
            failures.append((label, why))
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
