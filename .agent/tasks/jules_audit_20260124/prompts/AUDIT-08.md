# AUDIT-08: GH-Pages Deployment Configuration

## Target

**Jules**

## System Prompt

`general`

## Skills

`playwright-skill`, `systematic-debugging`

---

## Scope

Audit the GH-Pages deployment configuration:

- `/Users/mar/Projects/praxis/praxis/web-client/src/environments/environment.gh-pages.ts`
- `/Users/mar/Projects/praxis/praxis/web-client/angular.json` (gh-pages build config)
- Any GitHub Actions workflows for deployment
- `index.html` base href handling

## Existing E2E Coverage

Review and analyze coverage gaps in:

- `e2e/specs/ghpages-deployment.spec.ts`

---

## Objectives

### 1. Build Configuration Analysis

Document gh-pages specific settings:

- Build target configuration
- Output path
- Base href
- Asset optimization

### 2. Asset Resolution Audit

Verify all assets resolve correctly:

- Images
- Fonts
- Static JSON files
- JupyterLite assets
- Worker files

### 3. Environment Configuration

Compare dev vs gh-pages:

| Setting | Dev | GH-Pages |
|:--------|:----|:---------|
| API URL | ? | ? |
| Base HREF | ? | ? |
| Assets Path | ? | ? |

### 4. Gap Analysis

Identify:

- Broken asset links
- Path resolution issues
- Missing environment variables
- CORS/security header issues
- Service worker conflicts

### 5. Test Coverage Assessment

What deployment scenarios are tested vs missing?

---

## Deliverables

Create audit report at:
`/Users/mar/Projects/praxis/docs/audits/AUDIT-08-ghpages-config.md`

Report must contain:

1. **Build Configuration Summary** - Key settings table
2. **Asset Resolution Checklist** - Pass/fail for each asset type
3. **Environment Comparison** - Dev vs GH-Pages matrix
4. **Gap/Limitation List** - With severity (🔴/🟠/🟡)
5. **Recommended Test Cases** - Atomic descriptions
6. **Shipping Blockers** - Critical issues

---

## IMPORTANT

> ⚠️ **DO NOT** fix any code  
> ⚠️ **DO NOT** create actual tests  
> ⚠️ **DO NOT** debug issues  
> ⚠️ **DO** provide specific file/line references
