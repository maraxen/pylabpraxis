# Technical Debt

## JupyterLite REPL

- **404 Errors for PyLabRobot Paths**: The JupyterLite REPL console may show 404 errors for paths like `/assets/jupyterlite/api/contents/lib/python3.13/site-packages/pylabrobot/...`. This happens because JupyterLite's contents manager attempts to resolve imported modules on the server, but `pylabrobot` is installed via `micropip` into the Pyodide kernel's virtual filesystem (in-memory). These errors are harmless and do not affect functionality.
  - *Mitigation*: Future improvements could involve configuring `jupyter-lite.json` or a service worker to intercept or suppress these specific requests.

- **Slow Initial Load Time**: The JupyterLite iframe can take several seconds to initialize, causing a race condition where the iframe content isn't ready when the loader disappears, or requiring a manual "Restart" to function correctly. This is due to the sequential downloading and compilation of Pyodide and the customized kernel.
  - *Mitigation*: Explore **JupyterLite pre-bundling** during the build step to bake dependencies into the assets distribution, or implement **eager loading** of the REPL iframe (hidden) when the application starts, rather than waiting for user navigation.

- **pylibftdi Incompatibility**: The `pylibftdi` library (used for some device drivers) depends on C extensions/libftdi that are not compatible with Pyodide. It is currently mocked (`MagicMock`) in the REPL bootstrap code to prevent `ImportError` failures during `pylabrobot` imports, even when using `SimulatorBackend`.
  - *Mitigation*: If physical device control via FTDI is ever needed in browser mode (via WebSerial/WebUSB), a WASM port of `libftdi` or a pure Python alternative would be required.

## Backend / Build Tools

- **Browser Schema Generation Scripts Broken**: The `generate_browser_schema.py` and `generate_browser_db.py` scripts are currently failing.
  - *Current Workaround*: Manual patching of schema files.
  - *Fix*: Debug SQLAlchemy metadata initialization.

## Frontend Type Safety

- **`SqliteService` Blob Casting**: In `exportDatabase`, `this.dbInstance.export()` returns a `Uint8Array`, but `Blob` constructor in some environments/TS configurations might expect strictly `BlobPart[]`. We cast `data as any` to suppress the error.
  - *Fix*: Verify exact type definitions for `sql.js` export and `Blob` constructor compatibility in the current TS config.

- **`SettingsComponent` Tests Location Mocking**: In `settings.component.spec.ts`, mocking `window.location.reload` requires casting `window.location` to `any` because `window.location` is read-only in standard DOM types.
  - *Fix*: Use a more robust window mocking strategy or DI token for `Window`.
