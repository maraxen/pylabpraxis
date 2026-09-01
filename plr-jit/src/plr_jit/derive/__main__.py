"""``python -m plr_jit.derive``: the derivation-pipeline CLI (spec 260901
§7.3/§7.4).

Regenerates the two build artifacts derived from the survey:

.. code-block:: bash

    uv run python -m plr_jit.derive \\
        --survey-json training/verify/data/plr_preconditions.json \\
        --out plr-jit/data/derived_contracts.json \\
        --gap-ledger plr-jit/data/gap_ledger.json

``--survey-json PATH`` is REQUIRED, with no default (D19, §7.3): a
hardcoded default would silently couple this workspace-member package to
the caller's repo layout. At least one of ``--out``/``--gap-ledger`` must be
given, or there is nothing to do.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from plr_jit._provenance import survey_stamp
from plr_jit.derive import (
    SCHEMA_VERSION,
    SUPPORTED_TOOLS,
    InlinedGuard,
    build_gap_ledger,
    build_index,
    default_plr_pkg_root,
    derive_contract,
    load_survey,
    resolve_supported_tool,
    scan_dropped_receiver_calls,
)
from plr_jit.derive import _stamp_to_dict  # noqa: SLF001 - same-package reuse


def _guard_to_json(guard: InlinedGuard) -> dict[str, Any]:
    return {
        "condition": guard.condition,
        "scope_trail": list(guard.scope_trail),
        "raises": guard.raises,
        "kind": guard.kind,
        "free_vars": list(guard.free_vars),
        "site": {
            "file": guard.site.file,
            "lineno": guard.site.lineno,
            "qualname": guard.site.qualname,
        },
        "depth": guard.depth,
    }


def build_derived_contracts_payload(
    index: dict[tuple[str, str], Any], stamp: Any
) -> dict[str, Any]:
    """AC-7.2: derive a contract for every SUPPORTED_TOOLS method, via the
    D22-derived name mapping (never a hand-written map). ``derive_contract``
    itself never raises; ``resolve_supported_tool`` fails loudly if a tool
    name is absent from the index (a real failure mode, not a silent skip).
    """
    contracts: dict[str, Any] = {}
    for name in sorted(SUPPORTED_TOOLS):
        module, qualname = resolve_supported_tool(name, index)
        contract = derive_contract(module, qualname, index, stamp=stamp)
        contracts[qualname] = {
            "guards": [_guard_to_json(g) for g in contract.guards],
            "gaps": [list(gap) for gap in contract.gaps],
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "stamp": _stamp_to_dict(stamp),
        "contracts": contracts,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m plr_jit.derive", description=__doc__
    )
    parser.add_argument(
        "--survey-json",
        type=Path,
        required=True,
        help="Path to plr_preconditions.json (required, no default -- D19).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write the derived-contracts table (§7.3) to this path.",
    )
    parser.add_argument(
        "--gap-ledger",
        type=Path,
        default=None,
        help="Write the gap ledger (§7.4) to this path.",
    )
    parser.add_argument(
        "--plr-root",
        type=Path,
        default=None,
        help=(
            "Override the PLR package root scanned by the independent "
            "dropped-receiver AST pass (default: derived from this file's "
            "own location, external/pylabrobot/pylabrobot)."
        ),
    )
    args = parser.parse_args(argv)

    if args.out is None and args.gap_ledger is None:
        parser.error("at least one of --out / --gap-ledger is required")

    records = load_survey(args.survey_json)
    index = build_index(records)
    stamp = survey_stamp()

    if args.out is not None:
        payload = build_derived_contracts_payload(index, stamp)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)

    if args.gap_ledger is not None:
        plr_root = args.plr_root if args.plr_root is not None else default_plr_pkg_root()
        dropped_receiver_counts = scan_dropped_receiver_calls(plr_root)
        ledger = build_gap_ledger(
            index, records, dropped_receiver_counts=dropped_receiver_counts, stamp=stamp
        )
        args.gap_ledger.parent.mkdir(parents=True, exist_ok=True)
        args.gap_ledger.write_text(
            json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"wrote {args.gap_ledger}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
