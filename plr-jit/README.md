# plr-jit

JIT-style static validation of PyLabRobot execution graphs.

Decomposes a protocol's arguments into PLR resources, static/invariant values,
and dynamic values; maps the execution graph; and validates — on the code side —
that PLR state will not produce an error.

**v1 is a sound static analyzer.** Every verdict is one of `SAFE` / `WILL_FAIL` /
`UNKNOWN`, never a boolean, and `UNKNOWN` is the default for anything derivation
cannot resolve. Error recovery and hardware/command-stream optimization are
later extensions on the same substrate, not v1 scope.

The package is self-contained: nothing under `src/plr_jit/` may import `praxis`,
`verify`, or `training`, enforced by `tests/test_import_boundary.py`.

Specification: `.praxia/docs/specs/260901_plr-jit-pre-corpus-spec.md`
