#!/usr/bin/env python3
"""The refresh hooks load side by side without taking each other's modules.

tools/refresh.py loads ``tools/<name>/refresh.py`` for every hook directory
(imagery, virtual) in one process. Two of those directories hold a
``common.py``. Imported by bare name, both land in the one ``sys.modules``
slot ``common``, and the hook loaded second gets the first one's module:
the scheduled refresh failed with ``module 'common' has no attribute
'CONFIG'`` when the virtual hook got the imagery ``common``.

Checked here, offline:

- both hooks load through ``refresh.hook`` in one fresh process, in either
  order, and each hook's modules come from its own directory;
- every hook directory is a package, and no module in it imports a sibling
  by bare name.

Run: python3 tests/test_hooks.py
"""
import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
HOOKS = sorted(p.parent.name for p in TOOLS.glob("*/refresh.py"))

# The modules whose source file each hook's load is checked against.
OWN = {
    "imagery": ["imagery.refresh", "imagery.common", "imagery.ortofotos",
                "imagery.s2_quarterly"],
    "virtual": ["virtual.refresh", "virtual.common", "virtual.docs",
                "virtual.glofas", "virtual.overture"],
}


def load(order: list[str]) -> int:
    """Child process: load the hooks in ``order`` as tools/refresh.py does."""
    sys.path.insert(0, str(TOOLS))
    import refresh

    for name in order:
        module = refresh.hook(name)
        if module is None:
            print(f"error  tools/{name}/refresh.py not found")
            return 1
        if not callable(getattr(module, "refresh", None)):
            print(f"error  the {name} hook has no refresh()")
            return 1
    bad = []
    for name in order:
        for qualified in OWN.get(name, [f"{name}.refresh"]):
            module = sys.modules.get(qualified)
            where = Path(getattr(module, "__file__", "") or "").resolve()
            if module is None or where.parent != TOOLS / name:
                bad.append(f"{qualified} is {where or 'not loaded'}")
    for line in bad:
        print(f"error  {line}")
    return 1 if bad else 0


def bare_sibling_imports(directory: Path) -> list[str]:
    """``import x`` or ``from x import y`` where x.py sits beside the module."""
    siblings = {p.stem for p in directory.glob("*.py")} - {"__init__"}
    found = []
    for path in sorted(directory.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(), str(path))):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module or ""]
            else:
                continue
            for name in names:
                if name.split(".")[0] in siblings:
                    found.append(f"{path.relative_to(ROOT)}:{node.lineno} "
                                 f"imports {name} by bare name")
    return found


if len(sys.argv) > 2 and sys.argv[1] == "--load":
    raise SystemExit(load(sys.argv[2:]))

errors: list[str] = []

if set(HOOKS) != set(OWN):
    errors.append(f"hook directories are {HOOKS}; update OWN in this test")

for order in (HOOKS, HOOKS[::-1]):
    result = subprocess.run([sys.executable, __file__, "--load", *order],
                            capture_output=True, text=True)
    if result.returncode != 0:
        tail = (result.stdout + result.stderr).strip().splitlines()[-12:]
        errors.append(f"loading {' then '.join(order)} failed:\n    "
                      + "\n    ".join(tail))

for name in HOOKS:
    directory = TOOLS / name
    if not (directory / "__init__.py").exists():
        errors.append(f"tools/{name}/ has no __init__.py; tools/refresh.py "
                      f"imports the hook as the package {name}")
    errors.extend(bare_sibling_imports(directory))

if errors:
    print("\n".join(f"error  {e}" for e in errors))
    raise SystemExit(1)
print(f"OK: the {', '.join(HOOKS)} hooks load in one process in either "
      "order, each with its own modules")
