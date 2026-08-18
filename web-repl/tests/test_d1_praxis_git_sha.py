"""D1 negative test (ADR Sec 2.3): the shell-injected ``praxis_git_sha``
compare must fail closed on a genuine mismatch, including the asymmetric
dev-vs-real case the wheel spec's negative arm (4b) calls out by name, and
must pass -- WITHOUT any special-casing -- when both sides read the literal
"dev" sentinel.

Pure CPython, no browser/Pyodide/pytest-web dependency: this exercises
``stages.assert_praxis_git_sha`` directly, which is exactly the function the
(not-yet-written) ``praxis_bootstrap.py`` is specified to call after
receiving a ``praxis:shell-pong`` (see ``web-repl/shell/praxis-shell.js`` for
the wire protocol this stands in for).

Per ADR Sec 2.4, this file must NOT append
``web-repl/overlay/assets/python`` to ``sys.path`` (it shadows the real
top-level ``praxis`` package) -- it does not need to, since it only imports
``web-repl/bootstrap/stages.py``, which lives outside that subtree.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_BOOTSTRAP_DIR = Path(__file__).resolve().parents[1] / "bootstrap"
if str(_BOOTSTRAP_DIR) not in sys.path:
    sys.path.insert(0, str(_BOOTSTRAP_DIR))

import stages  # noqa: E402 -- path setup must precede this import

REAL_SHA_A = "c3a95c1eeb9701a1085f85940d68690b32b0079a"
REAL_SHA_B = "0000000000000000000000000000000000000000"


def test_matching_real_shas_pass() -> None:
    stages.assert_praxis_git_sha(REAL_SHA_A, REAL_SHA_A)  # must not raise


def test_dev_dev_passes_with_no_special_case() -> None:
    """The dev-loop escape hatch: build_manifest.py --dev and
    inject_shell.py --dev both write the literal sentinel, and the compare
    must pass -- as an emergent property of `!=`, not a branch.
    """
    stages.assert_praxis_git_sha(stages.DEV_SENTINEL, stages.DEV_SENTINEL)


def test_mismatched_real_shas_fail_closed() -> None:
    """THE OBSERVED-FAILING NEGATIVE TEST the task brief requires: a genuine
    mismatch between two real superproject shas must raise, naming both.
    """
    with pytest.raises(stages.PraxisDriftError) as exc_info:
        stages.assert_praxis_git_sha(REAL_SHA_A, REAL_SHA_B)
    message = str(exc_info.value)
    assert REAL_SHA_A in message
    assert REAL_SHA_B in message


def test_dev_manifest_real_shell_fails_closed() -> None:
    """Wheel-spec negative arm (4b), asymmetric case 1: manifest says "dev"
    but the shell was built for real -- must NOT be masked by the dev
    sentinel on only one side.
    """
    with pytest.raises(stages.PraxisDriftError) as exc_info:
        stages.assert_praxis_git_sha(stages.DEV_SENTINEL, REAL_SHA_A)
    message = str(exc_info.value)
    assert stages.DEV_SENTINEL in message
    assert REAL_SHA_A in message


def test_real_manifest_dev_shell_fails_closed() -> None:
    """Wheel-spec negative arm (4b), asymmetric case 2 (the mirror image):
    a real manifest against a shell still serving the dev sentinel -- e.g. a
    prod deploy that forgot to re-run inject_shell.py without --dev.
    """
    with pytest.raises(stages.PraxisDriftError) as exc_info:
        stages.assert_praxis_git_sha(REAL_SHA_A, stages.DEV_SENTINEL)
    message = str(exc_info.value)
    assert REAL_SHA_A in message
    assert stages.DEV_SENTINEL in message
