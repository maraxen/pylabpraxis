# web-repl

Site build root for the standalone browser REPL, and the home of praxis's own
browser-side Python. See the governing ADR for the full design:
`.praxia/docs/decisions/260817_repl-layout-and-delivery-mechanism.md`.

Two rules a future contributor will otherwise get wrong:

## 1. The boundary with `praxis/` is directional, and the sanctioned edge is build-time (ADR §5.2)

There is **no Python import path in either direction** between `web-repl/` and
`praxis/`. The **one** sanctioned edge is build-time: `praxis/web-client` embeds
a **pinned, copied artifact** of `web-repl/dist/` — never a live directory, and
never a Python import. Do not add an import from either tree into the other;
if you find yourself wanting one, the boundary is telling you the code is in
the wrong tree.

## 2. `overlay/assets/python/praxis/` shadows the repo's real `praxis` package (ADR §2.4)

The package here is deliberately named `praxis` (not renamed) because
`interactive.py` is the user-facing REPL API (`praxis.pause()`,
`praxis.confirm()`, `praxis.input()`) and renaming it would break that
contract. The consequence: this directory **shadows the repo's real
top-level `praxis` package** in any interpreter that puts
`overlay/assets/python` on `sys.path`.

**`web-repl/tests/` must NEVER append `overlay/assets/python` to `sys.path`.**
Test the code here by copying the subtree to `tmp_path`, or by running in a
subprocess with an explicit `PYTHONPATH` — not by mutating the test process's
own `sys.path`.
