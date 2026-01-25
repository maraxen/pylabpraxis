# AUDIT-07: JupyterLite Integration

## Target

**Jules**

## System Prompt

`general`

## Skills

`playwright-skill`, `systematic-debugging`

---

## Scope

Audit the JupyterLite integration at:

- `/Users/mar/Projects/praxis/praxis/web-client/src/assets/jupyterlite/`
- JupyterLite configuration files:
  - `jupyter-lite.json`
  - `jupyter-lite.gh-pages.json`
- Bootstrap/initialization code in the app

## Existing E2E Coverage

Review and analyze coverage gaps in:

- `e2e/specs/jupyterlite-bootstrap.spec.ts`
- `e2e/specs/jupyterlite-paths.spec.ts`

---

## Objectives

### 1. Integration Analysis

Map how JupyterLite is embedded:

- Iframe integration
- Messaging between app and JupyterLite
- Kernel initialization

### 2. Configuration Analysis

Document environment-specific configs:

| Config | Dev | GH-Pages |
|:-------|:----|:---------|
| Base URL | ? | ? |
| Kernel | ? | ? |
| OPFS | ? | ? |

### 3. Expected vs Actual Behaviors

- Kernel loading sequence
- OPFS integration for notebook storage
- Cross-origin communication
- Error display

### 4. Gap Analysis

Identify:

- CORS issues
- Loading failures
- Path resolution problems
- Kernel startup failures
- Memory issues

### 5. Test Coverage Assessment

What JupyterLite scenarios are tested vs missing?

---

## Deliverables

Create audit report at:
`/Users/mar/Projects/praxis/docs/audits/AUDIT-07-jupyterlite.md`

Report must contain:

1. **Integration Architecture** - Mermaid diagram
2. **Configuration Matrix** - Dev vs GH-Pages comparison
3. **Initialization Sequence** - Mermaid sequence diagram
4. **Gap/Limitation List** - With severity (🔴/🟠/🟡)
5. **Recommended Test Cases** - Atomic descriptions
6. **Shipping Blockers** - Critical issues

---

## IMPORTANT

> ⚠️ **DO NOT** fix any code  
> ⚠️ **DO NOT** create actual tests  
> ⚠️ **DO NOT** debug issues  
> ⚠️ **DO** provide specific file/line references
