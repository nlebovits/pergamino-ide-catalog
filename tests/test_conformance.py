#!/usr/bin/env python3
"""Portolan conformance gate, via rashid.

Fails on any error-severity finding whose rule and path are not in ACCEPTED.

ACCEPTED ships empty, and the rule for growing it is not negotiable: every
entry needs a row in docs/conformance.md giving the rule, where it fires, why
it is accepted, and the issue tracking its removal. A known deviation with an
issue number is a debt. A silently widened allow-list is a lie about what this
catalog conforms to.

Runs with --no-data. The byte checks read every asset, which over remote hrefs
makes CI slow and dependent on a third-party host being up. Run the full check
yourself before publishing:

    rashid check catalog/

SKIPs when rashid is not installed, so a clean checkout needs no setup. CI
installs it and enforces this.

Run: python3 tests/test_conformance.py
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from publish import load_config  # noqa: E402

# (rule id, path) pairs. A pair waives one rule on one object, so an accepted
# deviation cannot hide the same rule failing anywhere else.
ACCEPTED: set[tuple[str, str]] = {
    # rashid 0.4.0 asks an overview COG for a style. rashid main exempts it.
    ("PTL-VIZ-002", "imagenes/ortofotos_10cm_2022/collection.json"),
}

config = load_config()
target = ROOT / config["publish_dir"]

if shutil.which("rashid") is None:
    print("SKIP: rashid is not installed; conformance not checked here.")
    print("      CI installs it and enforces this.")
    raise SystemExit(0)

result = subprocess.run(
    ["rashid", "check", str(target), "--no-data", "--json"],
    capture_output=True,
    text=True,
)

try:
    report = json.loads(result.stdout)
except json.JSONDecodeError:
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    raise SystemExit("rashid produced no JSON report")

findings = report.get("findings", [])


def accepted(finding: dict) -> bool:
    return (finding.get("rule_id"), finding.get("path")) in ACCEPTED


blocking = [
    f for f in findings
    if f.get("severity") == "error" and not accepted(f)
]

for finding in blocking:
    where = finding.get("path", "?")
    print(f"error  {finding.get('rule_id')}  {where}: {finding.get('message')}")
    if finding.get("fix_hint"):
        print(f"       hint: {finding['fix_hint']}")

waived = [f for f in findings if accepted(f)]
if waived:
    print(f"\n{len(waived)} accepted finding(s); see docs/conformance.md")

if blocking:
    raise SystemExit(1)
print(f"OK: rashid found no blocking errors in {config['publish_dir']}/")
