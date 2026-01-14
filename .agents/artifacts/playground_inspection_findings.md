# Playground Inspection Findings

## Summary

Investigation into Playground regressions revealed three primary issues:

1. **WebSerial/WebUSB Unavailable**: The shim injection code path is never executed, causing `NameError` in the Python kernel.
2. **Initial Blank Screen**: The iframe often fails to render content on the first load, likely due to DOM timing/lifecycle issues.
3. **Theme Sync Failure**: The application defaults to Light theme parameters for the iframe on initialization, disregarding the actual AppStore state (or the state has not propagated in time).

## Kernel Load Regression

### Current Behavior

* On navigating to `/app/playground`, the Notebook area is often **blank** (white/empty).
* No iframe content loads until the user click "Restart Kernel".
* "Restart Kernel" forces a teardown (clearing the URL) and reconstruction (setting it again after 100ms), which succeeds.

### Root Cause

* **Initialization Race**: The `iframe` `[src]` binding updates immediately via the `effect` in the constructor. If the iframe DOM element isn't fully ready or if the browser cancels the navigation due to rapid changes (though unlikely here), it fails.
* The "Restart Kernel" fix confirms that a *fresh* DOM mount with a valid URL works. The initial load might be happening too early in the Angular lifecycle or conflicting with the view initialization.

### Proposed Fix

* **Lifecycle Control**: Move the initial URL generation to `ngAfterViewInit` or introduce a slight delay/check ensuring the View is ready.
* **Robust Loading**: Adopt the "Restart Kernel" pattern for the initial load: Ensure `jupyterliteUrl` is `undefined` initially, then set it asynchronously after the component view is initialized and the theme is resolved.
* **Loading State**: Add a visible loading spinner while `jupyterliteUrl` is undefined or the iframe is loading.

## Theme Sync Issue

### Current Behavior

* The JupyterLite iframe loads with `theme=JupyterLab+Light` even if the app is in Dark mode.
* Toggling the theme fixes it (reloads iframe with correct param).

### Root Cause

* **Early Effect Execution**: The `effect` in the `constructor` runs synchronously or very early. At this point, `AppStore` might return its initial signal value (often default/light) before the `localStorage` hydration completes or the signal updates.
* **No Reactive Updates**: While the `effect` *should* re-run when the signal updates, if the iframe is already loading/loaded with the wrong URL, it might cause a "flash" or the first load (which fails blank anyway) "eats" the event.

### Proposed Fix

* **Wait for Store**: Ensure the theme signal is stable or check it in `ngOnInit`.
* **Async Bootstrap**: Changing the bootstrap process to be async (for shims) will naturally delay the URL generation, likely giving the Store enough time to resolve the correct theme from storage.

## WebSerial/WebUSB Not Available

### Current Behavior

* Python Console Error: `NameError: name 'WebSerial' is not defined`.
* Bootstrap code fails to patch `pylabrobot.io`.

### Shim Loading Analysis

* The function `getOptimizedBootstrap()` (which fetches shims and appends them) is defined but **NEVER CALLED**.
* The code currently calls `this.generateBootstrapCode()` which references `WebSerial`/`WebUSB` but assumes they are already injected or mocks them (incorrectly for this context).

### Builtins Injection Analysis

* `WebSerial` and `WebUSB` are NOT added to builtins because the code chunk responsible for that (the shim content) is missing from the injected `code` parameter.

### Root Cause

* **Missing Function Call**: `buildJupyterliteUrl()` calls `generateBootstrapCode()` (sync) instead of `getOptimizedBootstrap()` (async).
* **Sync vs Async**: `buildJupyterliteUrl` is synchronous, but fetching shims requires `await`.

### Proposed Fix

1. Refactor `buildJupyterliteUrl` to be `async` (or handle async flow).
2. Call `await this.getOptimizedBootstrap()` instead of `this.generateBootstrapCode()`.
3. Inject the full shim code (or pre-load it) so `WebSerial` and `WebUSB` classes are defined *before* the patching lines:

    ```python
    _ser.Serial = WebSerial
    _usb.USB = WebUSB
    ```

## Loading Overlay History

### Previous Attempt

* An infinite loading overlay was reported. This happens if the `loading` state is never cleared.
* If we rely on `(load)="onIframeLoad()"` to clear a loading flag, and the iframe never fires `load` (e.g. blank screen issue), the overlay spins forever.

### Proposed Robust Solution

1. **Timeout Fallback**: If `onIframeLoad` doesn't fire within X seconds, clear the loading state and show a "Retry" or "Restart Kernel" button.
2. **State Tracking**: Use a signal `isLoading = signal(true)` and set it to false in `onIframeLoad`.
