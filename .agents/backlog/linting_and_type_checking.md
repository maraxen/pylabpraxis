# Backlog: Linting and Type Checking

Generated on: Fri Jan  2 10:38:44 EST 2026

## Executive Summary

We have successfully configured the `ty` type checker to resolve imports from `pylabrobot` (via `extra-paths`).
A comprehensive audit has been performed on the backend submodules.

### Key Findings & Action Plan

#### 1. 🔴 Core Type Errors (27 diagnostics)

The `praxis/backend/core` submodule has significant type safety issues:

* **`invalid-argument-type` (16 errors):** Mismatches in function calls, particularly `schedule_protocol_execution` and dependency injection.
* **`unresolved-attribute` (6 errors):** Missing attributes on objects, likely due to dynamic typing or missing type hints on ORM models/decorators.
* **Action:** Prioritize fixing these to ensure core stability.

#### 2. 🟠 API & Services Issues

* **`praxis/backend/api`:** 5 diagnostics (`MachineOrm` missing definitions, invalid type forms).
* **`praxis/backend/services`:** 3 diagnostics (Unresolved `serial.tools`, `call-non-callable`).
* **Submodule Audit Status:**
  * `api`: 11 diagnostics (unresolved-attribute, S105, S106)
  * `core`: 0 diagnostics (Resolved ✅)
  * `models`: 0 diagnostics (Clean ✅)
  * `services`: 3 diagnostics (call-non-callable, unresolved-import)
  * `utils`: 32 diagnostics (multiple issues)
    Fix `MachineOrm` relationships and resolve `serial` import stubs.

#### 3. 🟡 Linting (Ruff)

* Top-level import violations (`PLC0415`) and minor security warnings (`S105`, `S307`, `S324`) were detected in previous runs but need explicit configuration to separate from noise.

---

## Status Summary

* **Environment**: ✅ Configured (`pyproject.toml` set up for `ty`)

* **Audit Status**: Fresh run completed (except `utils` interrupted).

## Submodule: `praxis/backend/api`

### Ruff Audit

Ruff output present but no codes parsed.

### Ty (Type Check) Audit

Found 5 diagnostics.

| Diagnostic | Count |
|---|---|
| unresolved-attribute | 3 |
| unknown-argument | 1 |
| invalid-type-form | 1 |

<details>
<summary>Raw Ty Output</summary>

```
error[unresolved-attribute]: Class `MachineOrm` has no attribute `definition`
   --> praxis/backend/api/protocols.py:230:50
    |
229 |   # 2. Fetch all machines with definitions
230 |   stmt = select(MachineOrm).options(selectinload(MachineOrm.definition))
    |                                                  ^^^^^^^^^^^^^^^^^^^^^
231 |   result = await db.execute(stmt)
232 |   machines = result.scalars().all()
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Object of type `MachineOrm` has no attribute `definition`
   --> praxis/backend/api/protocols.py:251:27
    |
249 |           "accession_id": str(machine.accession_id),
250 |           "name": machine.name,
251 |           "machine_type": machine.definition.class_type if machine.definition else "unknown",
    |                           ^^^^^^^^^^^^^^^^^^
252 |           # Add other machine details as needed
253 |         },
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Object of type `MachineOrm` has no attribute `definition`
   --> praxis/backend/api/protocols.py:251:60
    |
249 |           "accession_id": str(machine.accession_id),
250 |           "name": machine.name,
251 |           "machine_type": machine.definition.class_type if machine.definition else "unknown",
    |                                                            ^^^^^^^^^^^^^^^^^^
252 |           # Add other machine details as needed
253 |         },
    |
info: rule `unresolved-attribute` is enabled by default

error[unknown-argument]: Argument `required_capabilities_json` does not match any known parameter
   --> praxis/backend/api/scheduler.py:186:7
    |
184 |       released_at=r.released_at,
185 |       expires_at=r.expires_at,
186 |       required_capabilities_json=r.required_capabilities_json,
    |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
187 |       estimated_usage_duration_ms=r.estimated_usage_duration_ms,
188 |     )
    |
info: rule `unknown-argument` is enabled by default

error[invalid-type-form]: Variable of type `type[Unknown]` is not allowed in a type expression
  --> praxis/backend/api/utils/crud_router_factory.py:50:43
   |
48 |     return await service.create(db=db, obj_in=obj_in)
49 |
50 |   @router.get(prefix, response_model=list[response_schema], tags=tags)
   |                                           ^^^^^^^^^^^^^^^
51 |   async def get_multi(
52 |     db: Annotated[AsyncSession, Depends(get_db)],
   |
info: rule `invalid-type-form` is enabled by default

Found 5 diagnostics
```

</details>

---

## Submodule: `praxis/backend/core`

**Status:** Resolved ✅ (All 27 diagnostics fixed)

### Summary of Fixes

- **Dependency Injection**: Fixed `ProtocolScheduler` provider in `container.py`.
* **Decorator System**: Introduced `DecoratedProtocolFunc` protocol to type-safe attribute access on protocol functions.
* **Orchestrator**: Fixed `IProtocolScheduler` protocol, attribute casting, and synchronous state calls.
* **Infrastructure**: Refined `filesystem.py` overloads and solved `asyncio.to_thread` typing in `protocol_code_manager.py`.

### Ruff Audit

Ruff output present but no codes parsed.

### Ty (Type Check) Audit

Found 27 diagnostics.

| Diagnostic | Count |
|---|---|
| invalid-argument-type | 16 |
| unresolved-attribute | 6 |
| unresolved-import | 1 |
| invalid-ignore-comment | 1 |
| invalid-overload | 1 |
| invalid-await | 1 |
| possibly-missing-attribute | 1 |

<details>
<summary>Raw Ty Output</summary>

```
error[unresolved-import]: Module `praxis.backend.models.orm.asset` has no member `ResourceOrm`
   --> praxis/backend/core/consumable_assignment.py:231:49
    |
229 |     # Query resources matching the type
230 |     # This is a simplified query - in production, filter by type columns
231 |     from praxis.backend.models.orm.asset import ResourceOrm
    |                                                 ^^^^^^^^^^^
232 |
233 |     type_hint = requirement.type_hint_str.lower()
    |
info: rule `unresolved-import` is enabled by default

warning[invalid-ignore-comment]: Invalid `type: ignore` comment: no whitespace after `ignore`
   --> praxis/backend/core/container.py:131:30
    |
129 |   # as a context manager to create and close the session.
130 |   # `pyright` struggles to infer the provided type from the Resource provider,
131 |   # so we use `# type: ignore` to suppress the incorrect error.
    |                              ^
132 |   db_session: providers.Provider[AsyncSession] = providers.Resource(
133 |     db_session_factory,
    |

error[invalid-argument-type]: Argument to bound method `__init__` is incorrect
   --> praxis/backend/core/container.py:187:5
    |
186 |   scheduler: providers.Singleton[IProtocolScheduler] = providers.Singleton(
187 |     ProtocolScheduler,
    |     ^^^^^^^^^^^^^^^^^ Expected `((...) -> IProtocolScheduler) | str | None`, found `<class 'ProtocolScheduler'>`
188 |     db_session_factory=db_session_factory,
189 |     celery_app=celery_app,
    |
info: Method defined here
   --> .venv/lib/python3.13/site-packages/dependency_injector/providers.pyi:385:9
    |
383 | class BaseSingleton(Provider[T]):
384 |     provided_type = Optional[Type]
385 |     def __init__(
    |         ^^^^^^^^
386 |         self,
387 |         provides: Optional[Union[_Callable[..., T], str]] = None,
    |         -------------------------------------------------------- Parameter declared here
388 |         *args: Injection,
389 |         **kwargs: Injection,
    |
info: rule `invalid-argument-type` is enabled by default

error[unresolved-attribute]: Object of type `(...) -> Unknown` has no attribute `__name__`
  --> praxis/backend/core/decorators/definition_builder.py:42:32
   |
40 | ) -> tuple[FunctionProtocolDefinitionCreate, dict[str, Any] | None]:
41 |   """Parse a function signature and decorator args to create a protocol definition."""
42 |   resolved_name = data.name or data.func.__name__
   |                                ^^^^^^^^^^^^^^^^^^
43 |   if not resolved_name:
44 |     msg = (
   |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Object of type `(...) -> Unknown` has no attribute `__name__`
   --> praxis/backend/core/decorators/definition_builder.py:105:19
    |
103 |     source_file_path=inspect.getfile(data.func),
104 |     module_name=data.func.__module__,
105 |     function_name=data.func.__name__,
    |                   ^^^^^^^^^^^^^^^^^^
106 |     is_top_level=data.is_top_level,
107 |     solo_execution=data.solo,
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Object of type `(...) -> Unknown` has no attribute `__qualname__`
   --> praxis/backend/core/decorators/models.py:113:31
    |
112 |   """
113 |   return f"{func.__module__}.{func.__qualname__}"
    |                               ^^^^^^^^^^^^^^^^^
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Object of type `(...) -> Unknown` has no attribute `__code__`
  --> praxis/backend/core/decorators/protocol_decorator.py:71:41
   |
69 |   if (
70 |     "__praxis_run_context__" in processed_kwargs_for_call
71 |     and "__praxis_run_context__" not in func.__code__.co_varnames
   |                                         ^^^^^^^^^^^^^
72 |     and not any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig_check.parameters.values())
73 |   ):
   |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Object of type `(...) -> Unknown` has no attribute `_protocol_runtime_info`
   --> praxis/backend/core/decorators/protocol_decorator.py:251:22
    |
249 |     async def wrapper(*args: Any, **kwargs: Any) -> Any:
250 |       # Get the runtime metadata from the function itself, not a global registry.
251 |       current_meta = func._protocol_runtime_info
    |                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^
252 |       protocol_unique_key = (
... and 407 more lines
```

</details>

---

## Submodule: `praxis/backend/models`

### Ruff Audit

Ruff output present but no codes parsed.

### Ty (Type Check) Audit

✅ No type errors found.

<details>
<summary>Raw Ty Output</summary>

```
All checks passed!
```

</details>

---

## Submodule: `praxis/backend/services`

### Ruff Audit

Ruff output present but no codes parsed.

### Ty (Type Check) Audit

Found 3 diagnostics.

| Diagnostic | Count |
|---|---|
| call-non-callable | 2 |
| unresolved-import | 1 |

<details>
<summary>Raw Ty Output</summary>

```
error[unresolved-import]: Cannot resolve imported module `serial.tools`
   --> praxis/backend/services/hardware_discovery.py:102:12
    |
100 |     try:
101 |       # Try to import serial.tools.list_ports
102 |       from serial.tools import list_ports
    |            ^^^^^^^^^^^^
103 |
104 |       ports = list_ports.comports()
    |
info: Searched in the following paths during module resolution:
info:   1. /Users/mar/Projects/pylabpraxis/lib/pylabrobot (extra search path specified on the CLI or in your config file)
info:   2. /Users/mar/Projects/pylabpraxis (first-party code)
info:   3. vendored://stdlib (stdlib typeshed stubs vendored by ty)
info:   4. /Users/mar/Projects/pylabpraxis/.venv/lib/python3.13/site-packages (site-packages)
info: make sure your Python environment is properly configured: https://docs.astral.sh/ty/modules/#python-environment
info: rule `unresolved-import` is enabled by default

error[call-non-callable]: Object of type `object` is not callable
  --> praxis/backend/services/protocol_definition.py:51:9
   |
49 |       # efficient data handling whether it's model or dict
50 |       param_dict = (
51 |         param_data.model_dump(exclude={"accession_id", "created_at", "updated_at"})
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
52 |         if hasattr(param_data, "model_dump")
53 |         else param_data
   |
info: rule `call-non-callable` is enabled by default

error[call-non-callable]: Object of type `object` is not callable
  --> praxis/backend/services/protocol_definition.py:81:9
   |
79 |     for asset_data in assets:
80 |       asset_dict = (
81 |         asset_data.model_dump(exclude={"accession_id", "created_at", "updated_at"})
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
82 |         if hasattr(asset_data, "model_dump")
83 |         else asset_data
   |
info: rule `call-non-callable` is enabled by default

Found 3 diagnostics
```

</details>

---

## Submodule: `praxis/backend/utils`

### Ruff Audit

Ruff output present but no codes parsed.

### Ty (Type Check) Audit
