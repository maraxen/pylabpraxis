# Status: Complete
# Phase 3 Plan: GitHub Pages Deployment Fix

**Goal**: Fix the GitHub Pages deployment pipeline to deploy the Angular app instead of just documentation.

**Context**:
Currently, `.github/workflows/docs.yml` builds MkDocs and deploys it to `gh-pages`.
We need to shift focus to deploying the Angular application located in `praxis/web-client`.
The repository name is `pylabpraxis` so the base href should be `/pylabpraxis/`.
Current `angular.json` has a `gh-pages` configuration with baseHref set to `/praxis/` which might be incorrect.

## Tasks

### Task 1: Update Workflow (Completed)
- **File**: `.github/workflows/deploy.yml` (Create new, disable `docs.yml`)
- **Steps**:
    1.  Checkout code.
    2.  Setup Node.js (v20+).
    3.  Setup Python (uv).
    4.  Install Python dependencies: `uv sync`.
    5.  Generate Browser DB: `uv run scripts/generate_browser_db.py`.
    6.  Install NPM dependencies: `npm ci` (in `praxis/web-client`).
    7.  Build Angular App: `npm run build -- --base-href /pylabpraxis/` (in `praxis/web-client`).
        -   Note: Override the `gh-pages` config in `angular.json` if needed, or update it.
    8.  Deploy to GH Pages using `peaceiris/actions-gh-pages`.
        -   `publish_dir`: `praxis/web-client/dist/web-client/browser` (Need to verify exact path after build).
        -   `keep_files`: `false` (Clean deploy).

### Task 2: Base Href & Routing Config (Completed)
- **File**: `praxis/web-client/angular.json`
- **Action**:
    -   Update `gh-pages` configuration `baseHref` to `/pylabpraxis/`.
    -   Ensure `404.html` is generated (copy `index.html` to `404.html` for SPA routing on GH Pages). This can be done as a post-build step in the workflow.

### Task 3: Verification (Completed)
- **Local Verification**:
    -   Run `npm run build -- --base-href /pylabpraxis/` inside `praxis/web-client`.
    -   Verify `dist/` contains `index.html` and assets.
    -   Confirm output directory structure (likely `dist/web-client/browser` or `dist/praxis-web-client/browser`).

## Execution Steps
1.  Verify `scripts/generate_browser_db.py` exists.
2.  Run local build verification to confirm output path.
3.  Create `.github/workflows/deploy.yml`.
4.  Disable `.github/workflows/docs.yml` (e.g. rename to `docs.yml.disabled` or comment out triggers).
5.  Commit and push.

## Status Notes
- Deployment workflow created (`deploy.yml`).
- Base Href configured and verified locally.
- Docs workflow disabled.
