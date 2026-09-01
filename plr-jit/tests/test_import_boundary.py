"""AC-1 / Spec 260901 §1 import boundary: nothing under plr_jit/src may import
praxis.*, verify, or training. The package is corpus-independent and must remain
independent of the analyzer's training/verification harness.
"""

import ast
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src" / "plr_jit"


def _iter_imports(tree: ast.AST):
    """Yield (node, top_level_module) for every absolute import."""
    if isinstance(tree, ast.Import):
        for alias in tree.names:
            yield tree, alias.name.split(".")[0]
    elif isinstance(tree, ast.ImportFrom):
        if tree.level == 0 and tree.module:
            yield tree, tree.module.split(".")[0]


def test_no_praxis_imports_under_src() -> None:
    """Spec 260901 §1.3 AC-1.2: no import whose top-level module is praxis."""
    offenders: list[str] = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            for import_node, top in _iter_imports(node):
                if top == "praxis":
                    offenders.append(f"{path}: {ast.unparse(import_node)}")
    assert offenders == [], f"Spec violation: {offenders}"


def test_no_verify_or_training_imports_under_src() -> None:
    """Spec 260901 §1.3: no import of verify or training modules.
    The package must not reach into the training harness."""
    offenders: list[str] = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            for import_node, top in _iter_imports(node):
                if top in ("verify", "training"):
                    offenders.append(f"{path}: {ast.unparse(import_node)}")
    assert offenders == [], f"Spec violation: {offenders}"
