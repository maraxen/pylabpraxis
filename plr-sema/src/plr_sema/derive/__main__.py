"""``python -m plr_sema.derive``: the derivation-pipeline CLI (spec 260901
§7.3/§7.4).

Regenerates the two build artifacts derived from the survey:

.. code-block:: bash

    uv run python -m plr_sema.derive \\
        --survey-json training/verify/data/plr_preconditions.json \\
        --out plr-sema/data/derived_contracts.json \\
        --gap-ledger plr-sema/data/gap_ledger.json

``--survey-json PATH`` is REQUIRED, with no default (D19, §7.3): a
hardcoded default would silently couple this workspace-member package to
the caller's repo layout. At least one of ``--out``/``--gap-ledger`` must be
given, or there is nothing to do.

**260901 T13 (backlog #4859): the analyzed surface is a parameter.**
``--plr-root``/``--surface-name``/``--surface-pin`` together name the
``Surface`` (``plr_sema._provenance.Surface``) this run is against, recorded
in the emitted stamp. A second, non-legacy upstream surface (extracted via
``git archive <sha> | tar -x``, no ``.git`` to introspect) is derived the
same way, into DIFFERENT output paths so both coexist on disk:

.. code-block:: bash

    uv run python -m plr_sema.derive \\
        --survey-json training/verify/data/plr_preconditions.upstream_nonlegacy.json \\
        --out plr-sema/data/derived_contracts.upstream_nonlegacy.json \\
        --gap-ledger plr-sema/data/gap_ledger.upstream_nonlegacy.json \\
        --plr-root /path/to/extracted/upstream/pylabrobot \\
        --surface-name upstream_nonlegacy \\
        --surface-pin <upstream commit sha>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from plr_sema._provenance import DEFAULT_SURFACE, Surface, survey_stamp
from plr_sema.derive import (
    SCHEMA_VERSION,
    InlinedGuard,
    SurveyRecord,
    build_contract_keys,
    build_gap_ledger,
    build_index,
    build_unique_index,
    default_plr_pkg_root,
    derive_contract,
    load_survey,
    scan_dropped_receiver_calls,
)
from plr_sema.derive import _stamp_to_dict  # noqa: SLF001 - same-package reuse


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
    records: list[SurveyRecord], index: dict[tuple[str, str], Any], stamp: Any
) -> dict[str, Any]:
    """AC-7.2 (260901 T11): derive a contract for every record the survey
    indexed -- the WHOLE analyzed PLR surface (4,770 methods across 345
    classes / 28 subpackages at the current pin), not just the 10
    ``SUPPORTED_TOOLS`` names. ``derive_contract`` itself never raises, so
    this never skips a record.

    **Population, not just the 1,314 finding-bearing methods (T11 item 4's
    zero-findings decision).** Every record in ``records`` -- including the
    3,456 that bear no ``PreconditionFinding`` of their own -- gets an entry
    point run through ``derive_contract``. This is NOT free of consequence:
    measured 260901, 580 of those 3,456 zero-own-finding methods inherit
    >=1 REAL guard through their ``delegates_to`` closure (e.g.
    ``PlateReader.read_absorbance`` has zero own findings but delegates to
    ``get_plate``, which has one) -- restricting the payload to
    finding-bearing entry points only, as an entry-point-selection choice,
    would have silently dropped every one of those 580 inherited guards for
    any operation naming one of those methods, which is exactly the
    own-body-only failure mode §7.2 exists to prevent, now recurring one
    level up (at entry-point selection rather than closure-walking). A
    zero-finding method with an empty closure (2,178 measured) still gets
    an entry -- guards=[], gaps=[] -- which ``check/``'s existing "resolved
    contract, zero guards, zero gaps, no loop" fallback (round-4 B1/B2)
    already turns into one ``no_contract_derived`` Finding: "known to the
    survey, unconstrained as far as it sees" is a real, different fact from
    "not resolvable to anything the survey analyzed at all"
    (``unsupported_tool``, redefined by this same task -- see
    ``plr_sema.check``'s module docstring).

    **Keying (T11 item 2, the collision fix).** ``build_index``'s
    ``(module, qualname)`` collapses 12 property/setter pairs at whole-survey
    scale (8 finding-bearing) -- using it here would silently derive a
    contract for only ONE twin per pair and never even attempt the other
    (see ``build_index``'s own docstring). This function therefore iterates
    ``build_unique_index(records)`` (every record individually addressable)
    for entry-point selection, while ``derive_contract``'s own closure walk
    keeps using ``index`` (the collapsing one) for ``resolve()``'s bare-name
    delegate lookup, unchanged -- the two have different jobs and the fix
    only touches the first. Output dict keys come from
    ``build_contract_keys`` -- see its docstring for the two independent
    collision sources (getter/setter pairs; same-named module-level
    functions in different modules) and the ``@module:lineno`` disambiguator.
    """
    unique_records = build_unique_index(records)
    contract_keys = build_contract_keys(records)
    contracts: dict[str, Any] = {}
    for record_key in sorted(unique_records):
        rec = unique_records[record_key]
        contract = derive_contract(rec.module, rec.qualname, index, stamp=stamp)
        out_key = contract_keys[record_key]
        assert out_key not in contracts, (
            f"contract key collision building payload: {out_key!r} "
            f"(record_key={record_key!r}) -- build_contract_keys should make "
            f"this structurally impossible"
        )
        contracts[out_key] = {
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
        prog="python -m plr_sema.derive", description=__doc__
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
            "own location, external/pylabrobot/pylabrobot). Also the "
            "surface's tree_path (260901 T13) -- what --surface-name/"
            "--surface-pin describe is THIS root."
        ),
    )
    parser.add_argument(
        "--surface-name",
        default=DEFAULT_SURFACE.name,
        help=(
            "260901 T13 (backlog #4859): name of the analyzed PLR surface "
            "(--plr-root's tree) recorded in the emitted stamp. Defaults to "
            "plr_sema._provenance.DEFAULT_SURFACE's own name, not a second "
            "hand-typed copy of it, so the two cannot drift apart -- this "
            "is the pre-T13 behavior (our checked-out submodule)."
        ),
    )
    parser.add_argument(
        "--surface-pin",
        default=None,
        help=(
            "260901 T13: explicit commit identity for --plr-root, for a "
            "tree that cannot answer that itself (e.g. an out-of-repo "
            "upstream extraction with no .git dir -- capture_git_state "
            "degrades to the 'nogit' sentinel on those, by design; this is "
            "how the real pin still ends up in the stamp). Leave unset for "
            "a live git checkout, where GitState.hash already answers it."
        ),
    )
    args = parser.parse_args(argv)

    if args.out is None and args.gap_ledger is None:
        parser.error("at least one of --out / --gap-ledger is required")

    records = load_survey(args.survey_json)
    index = build_index(records)
    surface_tree = args.plr_root if args.plr_root is not None else default_plr_pkg_root()
    surface = Surface(name=args.surface_name, tree_path=surface_tree, pin=args.surface_pin)
    stamp = survey_stamp(surface)

    if args.out is not None:
        payload = build_derived_contracts_payload(records, index, stamp)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)

    if args.gap_ledger is not None:
        dropped_receiver_counts = scan_dropped_receiver_calls(surface_tree)
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
