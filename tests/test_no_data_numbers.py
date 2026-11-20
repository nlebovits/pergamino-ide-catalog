#!/usr/bin/env python3
"""The docs quote no counts or percentages measured from the data.

The data changes on every refresh, so a count or a percentage in the docs
goes stale. The docs describe what the data holds and give queries. The
current row count is `table:row_count` in each `collection.json`.

This gate reads the documents in tests/doc_corpus.py: the repository README
and AGENTS.md, every Markdown file under catalog/, and the description of
the root Catalog and of every Collection. It fails on:

- a thousands-separated number (608,085) or a percentage (94%)
- any row count or geometry count that a collection.json records for any
  version, with or without separators, from 100 up. This catches a count
  copied from the data even when it is small ("195 overlays").

A number inside a URL is an identifier, such as a GeoNode dataset id, and
is not checked.

A Markdown blockquote (a line that starts with ">") is not checked either.
``tools/generate/build_docs.py`` writes blockquotes only for text quoted
from the publisher: a field of the GeoNode record, or the municipality's
terms of use. A number there is the publisher's statement, such as the
"10%" that defines chronic poverty, and each refresh quotes the record
again.

It cannot recognise every count, such as "39 rows", so review those by hand.
ALLOWED lists the few numbers that are configuration, not data.

Run: python3 tests/test_no_data_numbers.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from doc_corpus import ROOT, collections, documents  # noqa: E402

PATTERN = re.compile(r"(?<![\w.])\d{1,3}(?:,\d{3})+(?:\.\d+)?(?!\w)|\d+(?:\.\d+)?%")
COUNT_KEYS = ("table:row_count", "geoparquet:feature_count",
              "pergamino:repaired_geometries", "pergamino:null_geometries")
SMALLEST = 100

# Configuration and definitions, not measurements of the data.
ALLOWED: set[str] = set()
URL = re.compile(r"https?://[^\s)>\]`'\"]+")
QUOTE = re.compile(r"^>.*$", re.M)


def recorded_counts() -> set[int]:
    """Every count a collection.json records, at any level, for any version."""
    counts: set[int] = set()

    def walk(node) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in COUNT_KEYS and isinstance(value, int):
                    counts.add(value)
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    for doc in collections():
        walk(doc)
    return {c for c in counts if c >= SMALLEST}


def count_pattern(counts: set[int]) -> re.Pattern:
    forms = sorted({f"{c:,}" for c in counts} | {str(c) for c in counts},
                   key=len, reverse=True)
    return re.compile(r"(?<![\w.,])(?:" + "|".join(map(re.escape, forms)) + r")(?![\w,])")


errors = []
docs = documents()
counts = recorded_counts()
copied = count_pattern(counts) if counts else None

for path, prose in docs:
    # Blank each URL to spaces of the same length, so line numbers hold.
    prose = URL.sub(lambda m: " " * len(m.group(0)), prose)
    if path.suffix == ".md":
        prose = QUOTE.sub(lambda m: " " * len(m.group(0)), prose)
    hits = [m for m in PATTERN.finditer(prose) if m.group(0) not in ALLOWED]
    if copied:
        hits += [m for m in copied.finditer(prose)
                 if not any(h.start() == m.start() for h in hits)]
    for match in sorted(hits, key=lambda m: m.start()):
        line = prose[:match.start()].count("\n") + 1
        errors.append(f"{path.relative_to(ROOT)}:{line}: {match.group(0)}")

if errors:
    print("\n".join(f"error  data number in the docs: {e}" for e in errors))
    raise SystemExit(1)
print(f"OK: no data counts or percentages in {len(docs)} document(s)")
