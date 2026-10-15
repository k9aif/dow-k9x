# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""Failures propagate Agent -> Squad -> Orchestrator (CLAUDE.md "Failures propagate").

Static checks over the source: no handler in agents/squads swallows an error silently,
every loop agent re-raises a failed step, and the two layers that must catch do catch.
The behaviour itself is tested in test_loop_agent_errors.py.
"""

import ast
from pathlib import Path

import k9_dow

ROOT = Path(k9_dow.__file__).parent
SWALLOW_DIRS = [ROOT / "agents" / "src", ROOT / "squads"]


def _silent(handler: ast.ExceptHandler) -> bool:
    """True when the handler neither raises, logs, returns nor records anything."""
    for node in ast.walk(ast.Module(body=handler.body, type_ignores=[])):
        if isinstance(node, (ast.Raise, ast.Return, ast.Assign, ast.AugAssign, ast.Call)):
            return False
    return True


def _is_import_guard(handler: ast.ExceptHandler) -> bool:
    t = handler.type
    return isinstance(t, ast.Name) and t.id in ("ImportError", "ModuleNotFoundError")


def test_no_silent_exception_handlers_in_agents_or_squads():
    found = []
    for d in SWALLOW_DIRS:
        for f in sorted(d.glob("*.py")):
            for node in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
                if isinstance(node, ast.ExceptHandler) and _silent(node) and not _is_import_guard(node):
                    found.append(f"{f.relative_to(ROOT)}:{node.lineno}")
    assert not found, f"silent except handlers (raise, or log and record what was skipped): {found}"


def test_every_loop_agent_reraises_a_failed_step():
    missing = []
    for f in sorted((ROOT / "agents" / "src").glob("*.py")):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            bases = {getattr(b, "id", getattr(b, "attr", "")) for b in cls.bases}
            if not bases & {"K9ValidationLoopAgent", "BaseValidationLoopAgent"}:
                continue
            fail = next((m for m in cls.body if isinstance(m, ast.FunctionDef) and m.name == "fail"), None)
            calls = {getattr(c.func, "id", "") for c in ast.walk(fail) if isinstance(c, ast.Call)} if fail else set()
            if "raise_if_step_failed" not in calls:
                missing.append(f"{f.name}:{cls.name}")
    assert not missing, f"loop agents whose fail() doesn't call raise_if_step_failed: {missing}"


def test_the_catching_layers_record_the_failure():
    stage = (ROOT / "orchestrators" / "stage_base.py").read_text(encoding="utf-8")
    assert 'save_stage_result' in stage and '"status": "error"' in stage
    process = (ROOT / "runtime" / "dow_orchestrator_process.py").read_text(encoding="utf-8")
    assert '"status": "error"' in process
