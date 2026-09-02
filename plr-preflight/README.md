# plr-preflight

> Renamed from `plr-jit` on 260902. Nothing here is compiled just-in-time; the package is a
> pre-execution ("preflight") sound static check. Historical task_ids (`260901_plr-jit-*`) and
> commit messages keep the old name.

Preflight static validation of PyLabRobot execution graphs: SAFE / WILL_FAIL / UNKNOWN before anything runs.

Decomposes a protocol's arguments into PLR resources, static/invariant values,
and dynamic values; maps the execution graph; and validates — on the code side —
that PLR state will not produce an error.

**v1 is a sound static analyzer.** Every verdict is one of `SAFE` / `WILL_FAIL` /
`UNKNOWN`, never a boolean, and `UNKNOWN` is the default for anything derivation
cannot resolve. Error recovery and hardware/command-stream optimization are
later extensions on the same substrate, not v1 scope.

The package is self-contained: nothing under `src/plr_preflight/` may import `praxis`,
`verify`, or `training`, enforced by `tests/test_import_boundary.py`.

Specification: `.praxia/docs/specs/260901_plr-preflight-pre-corpus-spec.md`
