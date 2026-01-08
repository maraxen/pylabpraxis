# Maintenance Prompt: Type Checking

**Purpose:** Run Pyright (Python) and tsc (TypeScript) and resolve errors  
**Frequency:** Per health audit  

---

## Prompt

```markdown
Examine .agents/README.md for development context.

## Task

Run type checking on backend and frontend, resolve any errors.

## Phase 1: Triage and Prioritize

1. **Run Type Checkers**:

   **Backend (Python)**:
   ```bash
   uv run pyright praxis/backend > pyright_backend.log 2>&1
   ```

   **Frontend (TypeScript)**:

   ```bash
   cd praxis/web-client && npx tsc --noEmit > ../tsc_frontend.log 2>&1
   ```

1. **Count Errors**:

   ```bash
   tail -n 5 pyright_backend.log tsc_frontend.log
   ```

2. **Prioritize**: Start with the layer that has fewer errors.

## Phase 2: Categorize and Strategize

1. **Review the Log**:

   ```bash
   cat pyright_backend.log | head -n 100
   ```

2. **Categorize Errors**:

   **Python (Pyright)**:

   | Error Type | Typical Fix |
   |:-----------|:------------|
   | `reportGeneralTypeIssues` | Add proper type annotations |
   | `reportArgumentType` | Fix type mismatch in function calls |
   | `reportReturnType` | Update return annotation or fix return value |
   | `reportOptionalMemberAccess` | Add None check |
   | `reportMissingImports` | Add import or install dependency |

   **TypeScript**:

   | Error Code | Typical Fix |
   |:-----------|:------------|
   | TS2322 | Type assignment mismatch |
   | TS2339 | Property does not exist |
   | TS2345 | Argument type mismatch |
   | TS7006 | Parameter implicitly has 'any' type |

3. **Document Strategy** before applying fixes.

4. **Get User Input**: ⏸️ PAUSE for approval.

## Phase 3: Apply Fixes

Follow these patterns:

| Error Type | Typical Fix |
|:-----------|:------------|
| Type mismatch | Update types or add casts |
| Optional access | Add None check or use optional chaining |
| Missing attribute | Add to interface/type or fix property name |
| Import errors | Add import or install @types package |

## Phase 4: Verify and Document

1. **Verify**:

   ```bash
   uv run pyright praxis/backend 2>&1 | tail -n 5
   cd praxis/web-client && npx tsc --noEmit 2>&1 | tail -n 5
   ```

2. **Update Health Audit**:
   - Backend: `.agents/health_audit_backend.md`
   - Frontend: `.agents/health_audit_frontend.md`

## References

- [codestyles/python.md](../../../codestyles/python.md)
- [codestyles/typescript.md](../../../codestyles/typescript.md)

```

---

## Customization

This prompt is pre-configured for Praxis. No placeholders needed.
