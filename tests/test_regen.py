#!/usr/bin/env python3
"""The generated documentation matches its generator.

Everything under `catalog/` that is prose — the README.md and AGENTS.md at the
root, in each sub-catalog, and in each collection — is generated from
collection metadata, the GeoNode records snapshotted in
tools/generate/data/geonode.json, and the facts measured from the data in
tools/generate/data/measured.json. Committing a hand edit to generated output is the failure
mode this gate exists to catch: the edit looks fine in review, survives until
the next regeneration, and then vanishes with no trace of what it said.

The gate regenerates into a scratch copy and diffs. It never writes to
`catalog/`.

Run: python3 tests/test_regen.py
"""
import filecmp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
GEN = ROOT / "tools" / "generate"
INPUTS = [GEN / "build_docs.py", GEN / "data" / "geonode.json",
          GEN / "data" / "measured.json", ROOT / "tools" / "sources.json"]

if not all(path.exists() for path in INPUTS):
    print("SKIP: generator or its inputs are absent")
    raise SystemExit(0)

with tempfile.TemporaryDirectory() as tmp:
    work = Path(tmp) / "catalog"
    shutil.copytree(CATALOG, work)

    proc = subprocess.run(
        [sys.executable, str(GEN / "build_docs.py"), str(work)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print("error  build_docs.py failed:")
        print(proc.stderr.strip()[:2000])
        raise SystemExit(1)

    stale = []
    for generated in sorted(work.rglob("*.md")):
        rel = generated.relative_to(work)
        committed = CATALOG / rel
        if not committed.exists():
            stale.append(f"{rel}: generated but not committed")
        elif not filecmp.cmp(generated, committed, shallow=False):
            stale.append(f"{rel}: committed copy differs from generated")

if stale:
    print("\n".join(f"error  {s}" for s in stale))
    print(
        "\nRegenerate rather than editing the output:\n"
        "  python3 tools/generate/build_docs.py catalog"
    )
    raise SystemExit(1)

print("OK: generated documentation matches its generator")
