#!/usr/bin/env python3
"""bathos entry point for the Coxswain P2.6 fine-tune (one ablation arm per run).

Thin by design: every decision lives in ``praxis_training.finetune`` (recipe
constants in ``versions.py``, row selection in ``mixing.py``, prompt rendering
in ``render.py``, the run itself in ``train.py``). This file exists so the
pre-registration sidecar next to it (``p26_finetune.bth.toml``) binds to a
stable script stem and so ``bth run`` can catalog the run.

Interpreter bootstrap: ``bth run`` (bathos 0.13.0a4) executes
``[sys.executable, script, *args]`` with bathos's OWN interpreter, which does
not have torch/trl/praxis_training. When ``praxis_training`` is not importable
this script re-execs itself under the workspace venv (``<repo>/.venv/bin/python``,
built on the cluster login node with ``uv sync --package training --extra
train``), falling back to ``uv run --offline --no-sync --package training``.
``os.execv`` keeps the environment, so ``BTH_RESULTS_PATH`` / ``BTH_OUTPUT_DIR``
plumbing survives the hop. Provenance (exit code, outputs, sidecar outcome) is
still recorded by the outer ``bth run``.

Cluster invocation (one per arm; args after ``--`` are this script's args)::

    bth submit --remote engaging --preset gpu --name p26-arm-B --no-push-first -- \
        env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false \
        bth run --script-path scripts/experiments/p26_finetune.py \
            --output-paths outputs/p26/B/result.json --tags arm:B -- \
            --arm B --seed 0 --eval-after --out-dir outputs/p26/B
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BOOTSTRAP_FLAG = "PRAXIS_P26_BOOTSTRAPPED"


def _bootstrap_into_training_env() -> None:
    """Re-exec under an interpreter that has the training extra installed."""
    if os.environ.get(_BOOTSTRAP_FLAG):
        sys.stderr.write(
            "p26_finetune: praxis_training still not importable after re-exec; "
            "run `uv sync --package training --extra train` in the repo first\n"
        )
        raise SystemExit(3)
    env = dict(os.environ, **{_BOOTSTRAP_FLAG: "1"})
    venv_python = _REPO_ROOT / ".venv" / "bin" / "python"
    script_args = sys.argv[1:]
    if venv_python.is_file():
        argv = [str(venv_python), str(Path(__file__).resolve()), *script_args]
        os.execve(str(venv_python), argv, env)
    uv = shutil.which("uv")
    if uv is None:
        sys.stderr.write("p26_finetune: neither .venv/bin/python nor uv found\n")
        raise SystemExit(3)
    argv = [uv, "run", "--offline", "--no-sync", "--package", "training", "python",
            str(Path(__file__).resolve()), *script_args]
    os.chdir(_REPO_ROOT)
    os.execve(uv, argv, env)


try:
    from praxis_training.finetune.train import main
except ModuleNotFoundError as exc:  # pragma: no cover - exercised on the cluster
    if exc.name and exc.name.split(".")[0] in {"praxis_training", "torch", "trl", "transformers", "datasets"}:
        _bootstrap_into_training_env()
    raise

if __name__ == "__main__":
    raise SystemExit(main())
