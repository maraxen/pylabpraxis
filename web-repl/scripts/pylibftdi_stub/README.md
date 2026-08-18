# pylibftdi Stub Package Source

This directory contains the checked-in source code for the `pylibftdi` stub wheel, which is generated as part of the REPL build pipeline.

## Purpose

The stub package provides a minimal, importable `pylibftdi` module for environments where the real C-extension-based `pylibftdi` cannot be installed (Pyodide/WASM, CI without libftdi, headless test runners, browser environments).

The stub is a compatibility shim — it satisfies `import pylibftdi` and provides the public symbols that PyLabRobot's code actually uses:
- `FtdiError` — exception class
- `LibraryMissingError` — exception class  
- `Device` — phantom class that accepts construction but raises on actual I/O
- `driver` — stub with mutable `USB_VID_LIST` and `USB_PID_LIST` attributes

## Why This Exists

PyLabRobot's hardware backend detection uses module-scope import-time `try/except` checks:

```python
try:
    import pylibftdi
    HAS_PYLIBFTDI = True
except ImportError:
    HAS_PYLIBFTDI = False
```

In the browser (Pyodide/WASM), the real `pylibftdi` (a ctypes binding to libusb) cannot work. Without this stub, the `HAS_PYLIBFTDI` flag would be `False`, breaking REPL boot and disabling device backends.

With the stub, the flag is `True`, but any attempt to actually open an FTDI device raises a clear error directing users to install the real package on hardware that supports it.

## Original Binary

Prior to this source tree, a hand-committed binary wheel existed at `praxis/web-client/src/assets/wheels/pylibftdi-0.0.0-py3-none-any.whl` with no build recipe. This source tree replaces it — the binary is no longer the source of truth.

The binary is **retired, not relocated**, as per ADR §4.3 (`260817_repl-layout-and-delivery-mechanism.md`). A separate Phase 3 task (P3.11) handles deleting the orphaned binary as part of the broader `.gitignore` inversion and asset-path cleanup.

## Building the Wheel

The stub is built as part of the REPL asset pipeline by `web-repl/scripts/build_wheels.py`.

To build locally:

```bash
uv build --wheel web-repl/scripts/pylibftdi_stub/ --out-dir /tmp/wheel-out
```

The wheel will be `pylibftdi-0.0.0-py3-none-any.whl` — a pure-Python, version-independent wheel containing only the `pylibftdi/` package.

## Testing the Stub

Verify the stub provides the expected interface:

```bash
uv run --with /tmp/wheel-out/pylibftdi-0.0.0-py3-none-any.whl python -c \
  "import pylibftdi; print(hasattr(pylibftdi, 'FtdiError')); print(hasattr(pylibftdi, 'Device')); print(hasattr(pylibftdi, 'driver'))"
```

Should print three `True` lines.

The real `pylibftdi` is deliberately **not** vendored here. This stub is a build-time artifact only, generated fresh on each REPL build, with no expectation that it ships in the real PyLabRobot distribution.
