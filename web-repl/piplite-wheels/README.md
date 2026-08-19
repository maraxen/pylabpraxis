# piplite-wheels

Third-party wheels handed to `PipliteAddon.piplite_urls` (see
`../jupyter_lite_config.json`) so the kernel can resolve them from this site's own
origin instead of PyPI at boot.

**Why this is not `../vendor/`.** `vendor/` is ignored wholesale by
`web-repl/.gitignore` because it holds the fetched ~430 MB Pyodide tarball. These
wheels are the opposite kind of artifact: small, few, and load-bearing for an
offline boot, so they are committed. Keeping them in a separate tracked directory
avoids reintroducing the `vendor/` negation pattern that commit d7fcc365 removed
as dead.

**Why anything is here at all.** `ipykernel` depends on `comm`, which ships in
neither `pyodide-lock.json` (359 packages) nor the pyodide-kernel extension's own
piplite index (`ipykernel`, `piplite`, `pyodide-kernel`, `widgetsnbextension`). Before
this, every single boot fetched it from `pypi.org` + `files.pythonhosted.org`. The
`--offline` gate in `scripts/repl_smoke.py` is what surfaced it.

## Contents

| wheel | sha256 | why |
| --- | --- | --- |
| `comm-0.2.3-py3-none-any.whl` | `c615d91d75f7f04f095b30d1c1711babd43bdc6419c1be9886a85f2f4e489417` | `ipykernel` dependency, not bundled by Pyodide or piplite |

## Adding one

1. Download the exact wheel and record its sha256 in the table above.
2. Add its path to `PipliteAddon.piplite_urls` in `../jupyter_lite_config.json`.
3. Rebuild, then confirm it landed in the generated index: `dist/pypi/all.json`.
4. Re-run the offline gate — it is the only check that proves the wheel is
   actually being used instead of silently fetched from PyPI:
   `uv run python scripts/repl_smoke.py --probe --offline`

`disablePyPIFallback: true` is set in `../jupyter-lite.json`, so a missing wheel
now fails loudly rather than quietly reaching the network.
