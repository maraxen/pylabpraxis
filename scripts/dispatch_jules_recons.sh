#!/bin/bash
# Jules Recon Dispatch Script
# Purpose: Dispatch 19 reconnaissance tasks to Jules for v0.1-alpha shipping prep
# Date: 2026-01-22
#
# Usage:
#   ./scripts/dispatch_jules_recons.sh           # Dispatch all tasks
#   ./scripts/dispatch_jules_recons.sh --dry-run # Preview tasks without dispatching

set -euo pipefail

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - Tasks will not be dispatched"
    echo "================================================"
fi

# Counter for dispatched tasks
TASK_COUNT=0

dispatch_task() {
    local title="$1"
    local prompt="$2"
    
    TASK_COUNT=$((TASK_COUNT + 1))
    
    if $DRY_RUN; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 Task $TASK_COUNT: $title"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "$prompt" | head -30
        echo "... [truncated for preview]"
    else
        echo "📤 Dispatching Task $TASK_COUNT: $title"
        jules remote new --session "$prompt" 2>&1 | tail -3
        echo "   ✅ Dispatched"
        sleep 2  # Rate limiting
    fi
}

echo ""
echo "🚀 Jules Recon Dispatch - v0.1-alpha Shipping Prep"
echo "=================================================="
echo ""

# ============================================================================
# SECTION 1: SHIM VERIFICATION (3 tasks)
# ============================================================================

dispatch_task "HID Transport Shim Status Verification" \
"Title: RECON - HID Transport Shim Status Verification

## Mission
This is a RECONNAISSANCE task, not debugging. Investigate and report the current state of the WebHID shim implementation.

## Context
Files to examine:
- praxis/web-client/src/assets/pyodide/web_hid_shim.py
- praxis/web-client/src/assets/pyodide/pyodide_io_patch.py
- .agent/TECHNICAL_DEBT.md (search for HID)

Related: Technical Debt item states 'HID Transport Shim: Missing WebHID implementation for pylabrobot.io.hid.HID'

## Requirements
- Determine if WebHID shim exists and is functional
- Document what methods are implemented vs stubbed
- Identify any gaps or issues
- Report bugs/issues found, with potential solutions

## Deliverable
Create a recon report at .agent/reports/recon_hid_shim_status.md with:
- Current implementation status (Complete/Partial/Missing)
- List of implemented methods
- List of missing/stubbed methods
- Known issues and proposed solutions
- Recommendation (ship as-is, needs work, blocker)

## Acceptance Criteria
- Report file created
- Clear status determination
- Actionable recommendations"

dispatch_task "Socket/TCP Transport Shim Status" \
"Title: RECON - Socket/TCP Transport Shim Status

## Mission
This is a RECONNAISSANCE task. Investigate the current state of Socket/TCP shimming for browser mode.

## Context
Files to examine:
- praxis/web-client/src/assets/pyodide/pyodide_io_patch.py
- praxis/web-client/src/assets/pyodide/*.py (any socket-related)
- .agent/TECHNICAL_DEBT.md (search for Socket, TCP)
- .agent/prompts/260122_socket_shim_research.md (if exists)

Related: Browsers don't support raw TCP sockets. This blocks PreciseFlex and ethernet-controlled hardware.

## Requirements
- Determine current socket/TCP shim status
- Document any WebSocket-to-TCP bridge implementation
- Identify which hardware is blocked without this
- Report findings and potential solutions

## Deliverable
Create .agent/reports/recon_socket_shim_status.md with:
- Current implementation status
- Architecture approach (if any)
- Blocked hardware list
- Proposed solution path
- Recommendation for shipping

## Acceptance Criteria
- Report file created
- Clear status on TCP support
- List of affected hardware"

dispatch_task "Global Module Shimming Status" \
"Title: RECON - Global Module Shimming Status (sys.modules injection)

## Mission
This is a RECONNAISSANCE task. Verify the status of global module shimming for serial, usb, and hid.

## Context
Files to examine:
- praxis/web-client/src/assets/pyodide/pyodide_io_patch.py
- praxis/web-client/src/assets/pyodide/web_serial_shim.py
- praxis/web-client/src/assets/pyodide/web_usb_shim.py
- .agent/prompts/260122_global_module_shimming.md

Problem: Many backends do 'import serial' directly, bypassing pylabrobot.io abstractions.

## Requirements
- Verify sys.modules injection is implemented
- Check for serial, usb, hid, and pyserial constants
- Test if direct imports work (import serial, import usb.core)
- Document any missing constants or methods

## Deliverable
Create .agent/reports/recon_global_shimming_status.md with:
- Modules injected into sys.modules
- Constants available (EIGHTBITS, PARITY_NONE, etc.)
- Direct import test results
- Missing items
- Recommendation

## Acceptance Criteria
- Report file created
- Clear pass/fail for each module
- List of missing constants if any"

# ============================================================================
# SECTION 2: VISUAL/UI RECONS (4 tasks)
# ============================================================================

dispatch_task "Asset Wizard Visual Audit" \
"Title: RECON - Asset Wizard Visual Audit

## Mission
This is a RECONNAISSANCE task. Audit the Asset Wizard component for visual issues.

## Context
Files to examine:
- praxis/web-client/src/app/features/assets/components/asset-wizard/
- praxis/web-client/src/app/shared/components/
- .agent/prompts/260122_asset_wizard_visual_tweaks.md

Known issues: Grid is oversized, UI feels clunky.

## Requirements
- Audit grid layout sizing
- Compare to polished components in the app
- Identify padding/margin inconsistencies
- Document all visual issues found

## Deliverable
Create .agent/reports/recon_asset_wizard_visual.md with:
- Grid analysis
- Spacing issues
- Comparison to reference components
- Full issue list with severity
- CSS fix recommendations

## Acceptance Criteria
- Report file created
- At least 5 specific issues identified
- Fix recommendations included"

dispatch_task "Protocol Runner Visual Audit" \
"Title: RECON - Protocol Runner Visual Audit

## Mission
This is a RECONNAISSANCE task. Audit the Protocol Runner for theme variable usage and visual polish.

## Context
Files to examine:
- praxis/web-client/src/app/features/run-protocol/
- praxis/web-client/src/styles.css (theme variables)
- .agent/prompts/260122_protocol_runner_visual_tweaks.md

## Requirements
- Map component hierarchy
- Identify hardcoded colors vs theme variables
- Document visual inconsistencies
- Capture current state for comparison

## Deliverable
Create .agent/reports/recon_protocol_runner_visual.md with:
- Component hierarchy map
- Hardcoded color audit
- Theme variable usage gaps
- Visual issues list
- Recommendations

## Acceptance Criteria
- Report file created
- Hardcoded colors identified with line numbers
- Theme variable mappings suggested"

dispatch_task "Theme CSS Variable Audit" \
"Title: RECON - Theme CSS Variable Audit (Protocol Detail + Settings)

## Mission
This is a RECONNAISSANCE task. Audit Protocol Detail popup and Settings page for hardcoded colors.

## Context
Files to examine:
- praxis/web-client/src/app/features/protocols/components/protocol-detail/
- praxis/web-client/src/app/features/protocols/components/protocol-detail-dialog/
- praxis/web-client/src/app/features/settings/
- praxis/web-client/src/styles.css

## Requirements
- Find all hardcoded colors (#xxx, rgb(), hsl())
- Map each to appropriate theme variable
- Document which variables exist vs need creation

## Deliverable
Create .agent/reports/recon_theme_variables.md with:
- Hardcoded color inventory (file:line -> value)
- Suggested theme variable replacements
- Variables that need to be created
- Priority ranking

## Acceptance Criteria
- Report file created
- All hardcoded colors catalogued
- Theme variable mapping complete"

dispatch_task "E2E Test Infrastructure Audit" \
"Title: RECON - E2E Test Infrastructure Audit

## Mission
This is a RECONNAISSANCE task. Verify Playwright E2E test infrastructure is properly configured.

## Context
Files to examine:
- praxis/web-client/playwright.config.ts
- praxis/web-client/e2e/
- praxis/web-client/.gitignore
- .agent/prompts/260122_e2e_test_infrastructure.md

## Requirements
- Verify headless execution config
- Check list reporter setup
- Verify screenshot capture on all runs
- Confirm test-results/ is gitignored
- Audit existing test coverage

## Deliverable
Create .agent/reports/recon_e2e_infrastructure.md with:
- Config verification checklist
- Test coverage summary
- Gitignore status
- Missing tests for critical paths
- Recommendations

## Acceptance Criteria
- Report file created
- Infrastructure checklist verified
- Coverage gaps identified"

# ============================================================================
# SECTION 3: SHIPPING PREP RECONS (5 tasks)
# ============================================================================

dispatch_task "Long-term Roadmap and Versioning Strategy" \
"Title: RECON - Long-term Roadmap and Versioning Strategy

## Mission
This is a RECONNAISSANCE task. Research versioning best practices and propose a roadmap structure.

## Context
Files to examine:
- .agent/ROADMAP.md
- .agent/POST_SHIP_ROADMAP.md
- POST_SHIP.md
- pyproject.toml (current version: 0.0.1)

## Requirements
- Review existing roadmap documents
- Research semantic versioning for lab automation
- Propose version numbering scheme
- Suggest milestone structure and release cadence

## Deliverable
Create .agent/reports/recon_versioning_strategy.md with:
- Current state summary
- Recommended versioning scheme
- Milestone proposal (v0.1, v0.2, v1.0)
- Release cadence recommendation
- Roadmap consolidation suggestions

## Acceptance Criteria
- Report file created
- Clear versioning recommendation
- Milestone definitions"

dispatch_task "Repository Cleanup Audit" \
"Title: RECON - Repository Cleanup Audit

## Mission
This is a RECONNAISSANCE task. Identify stale files, unused code, and consolidation opportunities.

## Context
Examine:
- Root directory files
- references/ directory
- .agent/archive/
- Duplicate documentation

## Requirements
- Identify files that appear stale or unused
- Find duplicate information across docs
- Suggest consolidation opportunities
- Check for accidentally committed artifacts

## Deliverable
Create .agent/reports/recon_repo_cleanup.md with:
- Stale files list
- Duplicate content analysis
- Consolidation recommendations
- Files to delete
- Files to archive

## Acceptance Criteria
- Report file created
- At least 10 items identified
- Clear action recommendations"

dispatch_task ".gitignore Audit" \
"Title: RECON - .gitignore Audit

## Mission
This is a RECONNAISSANCE task. Audit what should be added or removed from version control.

## Context
Files to examine:
- .gitignore (root)
- praxis/web-client/.gitignore
- Run: git status --ignored
- Check for large binary files that shouldn't be tracked

## Requirements
- Review current .gitignore patterns
- Identify tracked files that should be ignored
- Check for missing patterns (logs, caches, artifacts)
- Verify standard patterns for Python/Node projects

## Deliverable
Create .agent/reports/recon_gitignore.md with:
- Current pattern analysis
- Missing patterns to add
- Problematic tracked files
- Recommended .gitignore updates

## Acceptance Criteria
- Report file created
- Gap analysis complete
- Specific patterns recommended"

dispatch_task "CHANGELOG.md Setup Research" \
"Title: RECON - CHANGELOG.md Setup Research

## Mission
This is a RECONNAISSANCE task. Research changelog best practices and integration with docs.

## Context
- No CHANGELOG.md currently exists
- Docs site at docs/ and praxis/web-client/src/assets/docs/
- Consider: Keep a Changelog format, conventional commits

## Requirements
- Research changelog formats (Keep a Changelog, etc.)
- Determine integration points with docs site
- Propose initial changelog structure
- Consider automation (git-cliff, standard-version)

## Deliverable
Create .agent/reports/recon_changelog_setup.md with:
- Recommended format
- Integration approach
- Automation options
- Initial CHANGELOG.md draft outline
- v0.1-alpha entry draft

## Acceptance Criteria
- Report file created
- Format recommendation
- Integration plan"

dispatch_task "Documentation Review" \
"Title: RECON - Documentation Review

## Mission
This is a RECONNAISSANCE task. Audit documentation for broken links, outdated content, and accuracy.

## Context
Files to examine:
- docs/ directory
- praxis/web-client/src/assets/docs/
- README.md
- mkdocs.yml

## Requirements
- Check for broken internal links
- Verify code examples still work
- Identify outdated screenshots/content
- Check for references to old name (pylabpraxis)

## Deliverable
Create .agent/reports/recon_documentation.md with:
- Broken link inventory
- Outdated content list
- Accuracy issues
- Screenshot audit
- Update priorities

## Acceptance Criteria
- Report file created
- Links checked
- Content accuracy assessed"

# ============================================================================
# SECTION 4: README/BRANDING RECONS (2 tasks)
# ============================================================================

dispatch_task "README.md Modernization Research" \
"Title: RECON - README.md Modernization Research

## Mission
This is a RECONNAISSANCE task. Research README best practices and propose modernization.

## Context
Files to examine:
- README.md (current state)
- Compare to: PyLabRobot, other lab automation projects
- Check shields.io for relevant badges

## Requirements
- Audit current README structure
- Research badge options (build, coverage, version, license)
- Propose improved structure
- Identify missing sections

## Deliverable
Create .agent/reports/recon_readme_modernization.md with:
- Current README analysis
- Recommended badges (with URLs)
- Proposed structure outline
- Missing sections to add
- Example snippets

## Acceptance Criteria
- Report file created
- Badge recommendations with markdown
- Structure proposal"

dispatch_task "Praxis Logo SVG with Gradient" \
"Title: RECON - Praxis Logo SVG with Gradient Styling

## Mission
This is a RECONNAISSANCE task. Locate or propose creation of Praxis logo SVG styled like in-app gradient.

## Context
Files to examine:
- praxis/web-client/src/assets/ (any existing logos/icons)
- praxis/web-client/src/styles.css (gradient definitions)
- praxis/web-client/src/app/layout/ (header/branding components)

## Requirements
- Find existing logo assets
- Document current gradient colors used in app
- Determine if SVG logo with gradient exists
- Propose creation approach if missing

## Deliverable
Create .agent/reports/recon_logo_branding.md with:
- Existing asset inventory
- Gradient color values (exact HSL/RGB)
- Logo status (exists/needs creation)
- Proposed SVG approach
- Integration points (README, docs, favicon)

## Acceptance Criteria
- Report file created
- Colors documented
- Clear recommendation"

dispatch_task "Base Repo Markdown Audit" \
"Title: RECON - Base Repo Markdown Files Audit

## Mission
This is a RECONNAISSANCE task. Audit all root-level .md files for consistency and accuracy.

## Context
Root markdown files:
- README.md
- CONTRIBUTING.md
- LICENSE.md
- ROADMAP.md
- RUNWAY.md
- POST_SHIP.md
- TECHNICAL_DEBT.md

## Requirements
- Review each file for accuracy
- Check cross-references between files
- Identify outdated information
- Find consolidation opportunities

## Deliverable
Create .agent/reports/recon_root_markdown.md with:
- File-by-file status
- Cross-reference issues
- Outdated content
- Consolidation recommendations
- Update priorities

## Acceptance Criteria
- Report file created
- All root .md files reviewed
- Recommendations provided"

# ============================================================================
# SECTION 5: TESTING & ENVIRONMENT RECONS (4 tasks)
# ============================================================================

dispatch_task "E2E Test Coverage Analysis" \
"Title: RECON - E2E Test Coverage Analysis

## Mission
This is a RECONNAISSANCE task. Analyze current E2E test coverage and identify gaps.

## Context
Files to examine:
- praxis/web-client/e2e/specs/
- praxis/web-client/e2e/fixtures/
- .agent/reports/ (any existing test reports)

## Requirements
- Inventory all existing E2E tests
- Map tests to features/routes
- Identify critical paths not covered
- Document test quality (assertions, stability)

## Deliverable
Create .agent/reports/recon_e2e_coverage.md with:
- Test inventory with descriptions
- Feature coverage matrix
- Critical path gaps
- Flaky test candidates
- Priority additions

## Acceptance Criteria
- Report file created
- All tests catalogued
- Coverage gaps identified"

dispatch_task "Jules Environment Setup for Production vs Browser Mode" \
"Title: RECON - Jules Environment Setup (Production vs Browser Mode)

## Mission
This is a RECONNAISSANCE task. Document how to set up Jules-compatible development environments for both modes.

## Context
Files to examine:
- .agent/README.md
- package.json scripts
- pyproject.toml
- .github/workflows/
- Environment variables used

## Requirements
- Document current setup complexity
- Identify blockers for Jules running tests
- Propose simplified setup commands
- Note differences between production and browser mode

## Deliverable
Create .agent/reports/recon_jules_environment.md with:
- Current setup steps (production mode)
- Current setup steps (browser mode)
- Environment variable requirements
- Blockers for Jules execution
- Proposed Makefile targets or scripts

## Acceptance Criteria
- Report file created
- Both modes documented
- Simplification proposals"

dispatch_task "Playwright Usage with Jules" \
"Title: RECON - Playwright Usage with Jules

## Mission
This is a RECONNAISSANCE task. Research and document how Jules can effectively run Playwright tests.

## Context
Files to examine:
- praxis/web-client/playwright.config.ts
- praxis/web-client/package.json
- .agent/skills/playwright-skill/
- .agent/skills/webapp-testing/

## Requirements
- Document current Playwright setup
- Identify Jules-specific considerations (headless, CI)
- Note any blocking issues for remote execution
- Propose test running conventions for Jules

## Deliverable
Create .agent/reports/recon_playwright_jules.md with:
- Current Playwright config summary
- Jules execution requirements
- Headless mode verification
- Recommended test commands for Jules
- Known issues/gotchas

## Acceptance Criteria
- Report file created
- Jules-compatible commands documented
- Blocking issues identified"

dispatch_task "Backend Testing Coverage Analysis" \
"Title: RECON - Backend Testing Coverage Analysis

## Mission
This is a RECONNAISSANCE task. Analyze backend (Python) test coverage and identify gaps.

## Context
Files to examine:
- tests/ directory
- tests/README.md
- tests/TESTING_PATTERNS.md
- pyproject.toml [tool.pytest] section
- htmlcov/ if exists

## Requirements
- Inventory test directories and types
- Run coverage report if possible
- Identify untested modules/services
- Document test patterns used

## Deliverable
Create .agent/reports/recon_backend_coverage.md with:
- Test directory structure
- Coverage statistics (if available)
- Untested modules list
- Test pattern analysis
- Priority additions

## Acceptance Criteria
- Report file created
- Tests catalogued
- Coverage gaps identified"

# ============================================================================
# COMPLETION
# ============================================================================

echo ""
echo "=================================================="
if $DRY_RUN; then
    echo "🔍 DRY RUN COMPLETE - $TASK_COUNT tasks previewed"
    echo ""
    echo "To dispatch all tasks, run:"
    echo "   ./scripts/dispatch_jules_recons.sh"
else
    echo "✅ DISPATCH COMPLETE - $TASK_COUNT tasks sent to Jules"
    echo ""
    echo "Monitor with:"
    echo "   jules remote list --session 2>&1 | cat | head -50"
fi
