# Phase 1 Extension: Offline Protocol Execution

**Goal**: Enable offline protocol execution by pre-compiling protocol pickles.

## Context
Currently, protocols are executed by sending requests to the backend, which serializes the protocol function. To support offline mode (Browser Mode), we need to pre-compile these protocols into pickle files that can be served as static assets and loaded directly by the frontend.

## Tasks

### 1. Refactor Serializer
- [x] Move `serialize_protocol_function` to `praxis/backend/utils/protocol_serialization.py`.
  - Ensure this new module does not depend on the heavy service layer so it can be imported by lightweight scripts.
  - Update existing imports of `serialize_protocol_function` in the codebase to point to the new location.

### 2. Update `generate_browser_db.py`
- [x] Update `scripts/generate_browser_db.py`:
    - Import `serialize_protocol_function` from the new utility module.
    - Import `cloudpickle`.
    - Modify `discover_protocols_static` to handle serialization:
        - During protocol analysis, dynamically import the module and function.
        - Serialize the function using `serialize_protocol_function`.
        - Write the serialized output to `praxis/web-client/src/assets/protocols/{accession_id}.pkl`.
        - Ensure the target directory `praxis/web-client/src/assets/protocols/` exists.

### 3. Update `ExecutionService` (Frontend)
- [x] Modify `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts`:
    - Update `fetchProtocolBlob(id)` method:
        - Check if running in Browser Mode (`this.modeService.isBrowserMode()`).
        - If **Browser Mode**: Return `this.http.get('/assets/protocols/' + id + '.pkl', {responseType: 'arraybuffer'})`.
        - If **Server Mode**: Keep the existing API call logic.

## Verification
- [x] Run generation script:
    ```bash
    uv run scripts/generate_browser_db.py
    ```
- [x] Verify pickle files are generated:
    ```bash
    ls -l praxis/web-client/src/assets/protocols/
    ```
- [x] Check that file sizes are > 0.

## Status Update
- Offline pickle generation and fetching is implemented and verified.
- Ran `tests/verify_pickle.py` and confirmed:
  1. Pickles load without `praxis` dependency errors.
  2. Closures are clean (no globals).
  3. Signatures are preserved.
