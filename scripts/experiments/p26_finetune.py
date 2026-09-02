#!/usr/bin/env python3
"""bathos entry point for the Coxswain P2.6 fine-tune (one ablation arm per run).

Thin by design: every decision lives in ``praxis_training.finetune`` (recipe
constants in ``versions.py``, row selection in ``mixing.py``, prompt rendering
in ``render.py``, the run itself in ``train.py``). This file exists so the
pre-registration sidecar next to it (``p26_finetune.bth.toml``) binds to a
stable script stem and so ``bth run`` can catalog the run.

Invoke through the training workspace member so torch/trl resolve::

    bth run --out outputs/p26/B/result.json -- \
        uv run --package training --extra train python scripts/experiments/p26_finetune.py \
        --arm B --eval-after --out-dir outputs/p26/B

Results (flat dict, see ``train.py``) are printed as JSON and written to
``$BTH_RESULTS_PATH`` for outcome evaluation.
"""

from __future__ import annotations

from praxis_training.finetune.train import main

if __name__ == "__main__":
    raise SystemExit(main())
