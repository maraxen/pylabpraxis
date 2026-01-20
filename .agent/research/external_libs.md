# External Libraries Research

This document tracks research on external libraries used in the PyLabPraxis project.

## 1. Formly UI Hints (Angular)

We use `ngx-formly` for dynamic form generation. The current project version is `^7.0.1` using Material components (`@ngx-formly/material`).

### Current State
*   **Custom Types**: The project already implements several custom types in `src/app/shared/formly-types/`:
    *   `asset-selector`: Selection of machines/resources.
    *   `chips`: Multi-select with chips.
    *   `repeat`: Array-based repeating sections.
    *   `index-selector`: Visual grid/well selector.
*   **Missing Widgets**: There are currently no implementations for `slider` or `stepper`.

### Adding Sliders
Standard `ngx-formly/material` does not include a slider by default in version 7, but it can be added:
1.  **Option A (Module)**: Install and import `@ngx-formly/material/slider` (if available in the installed version).
2.  **Option B (Custom Type)**: Create a custom component extending `FieldType`:
    ```typescript
    @Component({
      selector: 'formly-field-slider',
      template: `
        <mat-slider [min]="to.min" [max]="to.max" [step]="to.step">
          <input matSliderThumb [formControl]="formControl" [formlyAttributes]="field">
        </mat-slider>
      `,
    })
    export class FormlyFieldSlider extends FieldType {}
    ```
3.  **Registration**: Add to `FormlyModule.forRoot({ types: [...] })` in `app.config.ts`.

### Adding Steppers
Steppers are usually higher-level layout components rather than leaf fields.
*   **Standard Pattern**: Create a custom type with `name: 'stepper'` that uses `mat-horizontal-stepper`.
*   **Implementation**: Each `mat-step` contains a `formly-form` or a `fieldGroup` from the stepper's own configuration.
*   **Metadata**: `ParameterConfigComponent.ts` should be updated to check `param.ui_hint` for `slider` or `stepper` and return the appropriate type.

---

## 2. Pyodide Execution & Python Serialization

We use Pyodide (`^0.29.0`) in a Web Worker to run Python code in the browser.

### Cloudpickle Serialization
To run Python code that depends on `pylabrobot` but not `praxis`, functions can be serialized using `cloudpickle`.

*   **Backend (Standard Python)**:
    ```python
    import cloudpickle
    def my_protocol_step(lh):
        # uses pylabrobot
        lh.pick_up_tips(...)
    
    serialized_func = cloudpickle.dumps(my_protocol_step)
    # Send serialized_func (bytes) to the frontend
    ```
*   **Frontend (Pyodide)**:
    1.  Ensure `cloudpickle` is installed: `await micropip.install('cloudpickle')`.
    2.  Deserialize and run:
        ```python
        import cloudpickle
        import pickle
        # bytes_data received from JS
        func = cloudpickle.loads(bytes_data)
        func(my_liquid_handler_instance)
        ```

### exec() vs runPython() in Pyodide

| Feature | `exec(code, globals)` | `pyodide.runPython(code)` |
| :--- | :--- | :--- |
| **Origin** | Standard Python | Pyodide JS API |
| **Return Value** | Always `None` | Returns value of **last expression** |
| **Multi-statement**| Supported | Supported |
| **Scope** | Uses provided `globals` dict | Uses `pyodide.globals` by default |
| **Async** | N/A (use `eval` for Coroutines) | `runPythonAsync` for top-level await |

**Key Findings:**
*   **"Multiple Statements" limitation**: There is no limitation on multiple statements in `exec()`. The confusion often arises because `eval()` only supports single expressions, and `exec()` returns `None`.
*   **Recommendation**: Use `pyodide.runPython(code)` when you want the result of the last line (e.g., `x + 1`). Use `exec()` if you are running a script and manually managing the namespace via a `globals` dictionary.
*   **Pyodide Console**: The current implementation uses `PyodideConsole.push()`, which is best for interactive REPL behavior as it handles incomplete statements and syntax checks. For one-off execution of a "blob" of code, `runPython` is more direct.

### Important Notes
*   **pylabrobot**: Already installed in `python.worker.ts` via `micropip.install(['jedi', 'pylabrobot'])`.
*   **Isolation**: Serializing with `cloudpickle` ensures that the function carries its closure/dependencies, but it must only depend on libraries available in Pyodide (like `pylabrobot`).
