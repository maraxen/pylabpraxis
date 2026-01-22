#!/bin/bash
# Dispatch atomic tasks to Jules based on recon report findings
# Date: 2026-01-22

set -e

REPO="maraxen/praxis"

echo "=== Dispatching Recon-Based Tasks to Jules ==="
echo ""

# Task 2: Fix Playwright Config
echo "[2/21] Fix Playwright Config: Enable Screenshots on All Runs"
jules new --repo "$REPO" 'Title: Fix Playwright Config - Enable Screenshots on All Runs

## Context
File: praxis/web-client/playwright.config.ts
Current: screenshot option is set to "only-on-failure"
Reference: .agent/reports/recon_e2e_infrastructure.md

## Requirements
- Change screenshot option from "only-on-failure" to "on"
- Explicitly set outputDir: "test-results/" for clarity
- Preserve all other configuration

## Acceptance Criteria
- screenshot setting is "on" in playwright.config.ts
- outputDir is explicitly set to "test-results/"'
sleep 2

# Task 3: Add test-results to .gitignore
echo "[3/21] Add test-results/ to .gitignore"
jules new --repo "$REPO" 'Title: Add test-results/ to web-client .gitignore

## Context
File: praxis/web-client/.gitignore
Reference: .agent/reports/recon_e2e_infrastructure.md

## Requirements
- Add "test-results/" to praxis/web-client/.gitignore
- This prevents Playwright test artifacts from being committed

## Acceptance Criteria
- "test-results/" appears in praxis/web-client/.gitignore'
sleep 2

# Task 4: Fix .gitignore screenshot typo
echo "[4/21] Fix .gitignore Screenshot Typo"
jules new --repo "$REPO" 'Title: Fix .gitignore Screenshot Path Typo

## Context
File: .gitignore (root)
Issue: Pattern has "screenshot" (singular) but directory is "screenshots" (plural)
Reference: .agent/reports/recon_gitignore.md

## Requirements  
- Find pattern "praxis/web-client/e2e/screenshot/" in root .gitignore
- Change to "praxis/web-client/e2e/screenshots/" (plural)

## Acceptance Criteria
- Root .gitignore contains "praxis/web-client/e2e/screenshots/" (with s)'
sleep 2

# Task 5: Add *.db and binary patterns
echo "[5/21] Add *.db and Binary Patterns to Root .gitignore"
jules new --repo "$REPO" 'Title: Add *.db and Binary Patterns to Root .gitignore

## Context
File: .gitignore (root)
Reference: .agent/reports/recon_gitignore.md

## Requirements
- Add "*.db" pattern to prevent SQLite files from being tracked
- Add ".agent/scripts/jules-diff-tool/jules-diff-tool" to ignore compiled binary

## Acceptance Criteria
- "*.db" appears in root .gitignore
- ".agent/scripts/jules-diff-tool/jules-diff-tool" appears in root .gitignore'
sleep 2

# Task 6: Delete stale root files
echo "[6/21] Delete Stale Root Files"
jules new --repo "$REPO" 'Title: Delete Stale Root Files

## Context
Repository root contains orphaned temporary files
Reference: .agent/reports/recon_repo_cleanup.md

## Requirements
Delete these files from repository root:
- modified_changes.diff (accidentally committed patch file)
- temp_state_size_test.py (temporary test script)
- test_resolve_params.py (orphaned test script)

## Acceptance Criteria
- modified_changes.diff does not exist
- temp_state_size_test.py does not exist
- test_resolve_params.py does not exist'
sleep 2

# Task 7: Archive RUNWAY.md
echo "[7/21] Archive Completed RUNWAY.md"
jules new --repo "$REPO" 'Title: Archive Completed RUNWAY.md

## Context
RUNWAY.md documents the completed repository rename from pylabpraxis to praxis
Reference: .agent/reports/recon_root_markdown.md

## Requirements
- Move RUNWAY.md to .agent/archive/RUNWAY.md
- Create .agent/archive/ directory if it does not exist

## Acceptance Criteria
- .agent/archive/RUNWAY.md exists
- RUNWAY.md no longer exists at repository root'
sleep 2

# Task 8: Fix CONTRIBUTING.md command inconsistency
echo "[8/21] Fix CONTRIBUTING.md Command Inconsistency"
jules new --repo "$REPO" 'Title: Fix CONTRIBUTING.md Command Inconsistency

## Context
File: CONTRIBUTING.md
Issue: Uses "make" commands but README.md uses "uv run" commands
Reference: .agent/reports/recon_root_markdown.md

## Requirements
Replace make commands with uv equivalents:
- "make test" -> "uv run pytest"
- "make lint" -> "uv run ruff check"
- "make typecheck" -> "uv run mypy"
- "make docs" -> "uv run mkdocs serve"

Preserve all other content and formatting.

## Acceptance Criteria
- No "make test", "make lint", "make typecheck", "make docs" in CONTRIBUTING.md
- Equivalent uv commands are present instead'
sleep 2

# Task 9: Fix Docker service names in docs
echo "[9/21] Fix Documentation: Docker Service Names"
jules new --repo "$REPO" 'Title: Fix Docker Service Names in Documentation

## Context
Multiple documentation files reference "db" but should reference "praxis-db"
Reference: .agent/reports/recon_documentation.md

## Requirements
Change "db" to "praxis-db" in docker compose commands in:
- docs/getting-started/installation-production.md (around line 27)
- docs/reference/troubleshooting.md (around line 19)
- docs/reference/cli-commands.md (around line 7)
- docs/development/contributing.md (around line 23)
- docs/development/testing.md (around line 13)

## Acceptance Criteria
- All "docker compose up -d db" references changed to "docker compose up -d praxis-db"'
sleep 2

# Task 10: Fix incorrect file paths in docs
echo "[10/21] Fix Documentation: Incorrect File Paths"
jules new --repo "$REPO" 'Title: Fix Incorrect File Paths in Documentation

## Context
Documentation contains doubled "praxis/praxis" paths that should be single "praxis"
Reference: .agent/reports/recon_documentation.md

## Requirements
Fix these paths:
- docs/getting-started/quickstart.md line 15: "cd praxis/praxis/web-client" -> "cd praxis/web-client"
- docs/development/contributing.md line 91: "praxis/praxis/" -> "praxis/"
- docs/reference/cli-commands.md line 179: "praxis/praxis/web-client" -> "praxis/web-client"

## Acceptance Criteria
- No occurrences of "praxis/praxis" in the documentation files listed'
sleep 2

# Task 11: Fix uvicorn command consistency
echo "[11/21] Fix Documentation: Uvicorn Command Consistency"
jules new --repo "$REPO" 'Title: Standardize Uvicorn Commands in Documentation

## Context
Inconsistent uvicorn commands across documentation
Reference: .agent/reports/recon_documentation.md

## Requirements
Standardize to: uvicorn main:app --reload --port 8000
Update in:
- docs/getting-started/quickstart.md (around line 24)
- docs/development/contributing.md (around line 27)
- docs/reference/cli-commands.md (around line 12)

## Acceptance Criteria
- All uvicorn commands use "uvicorn main:app --reload --port 8000"'
sleep 2

# Task 12: Create CHANGELOG.md
echo "[12/21] Create CHANGELOG.md"
jules new --repo "$REPO" 'Title: Create CHANGELOG.md with Keep a Changelog Format

## Context
Repository needs a CHANGELOG.md following Keep a Changelog format
Reference: .agent/reports/recon_changelog_setup.md

## Requirements
Create CHANGELOG.md at repository root with:
1. Header linking to keepachangelog.com and semver.org
2. [Unreleased] section with Added/Changed/Fixed subsections
3. [v0.1-alpha] entry with:
   - Added: Initial project setup
   - Added: PyLabRobot support for hardware-agnostic protocol execution
   - Added: Asset management for machines and resources
   - Added: Real-time monitoring via WebSockets

## Acceptance Criteria
- CHANGELOG.md exists at repository root
- Contains [Unreleased] section
- Contains [v0.1-alpha] section with Added entries'
sleep 2

# Task 13: Add cross-reference sentences
echo "[13/21] Add Cross-Reference Sentences to Roadmap Files"
jules new --repo "$REPO" 'Title: Add Cross-Reference Sentences to Roadmap Files

## Context
ROADMAP.md, POST_SHIP.md, and TECHNICAL_DEBT.md need clarifying scope sentences
Reference: .agent/reports/recon_root_markdown.md

## Requirements
Add at top of each file (after title, before content):
- ROADMAP.md: "For immediate post-release plans, see [POST_SHIP.md](./POST_SHIP.md). For known issues and smaller improvements, see [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md)."
- POST_SHIP.md: "For long-term strategic goals, see [ROADMAP.md](./ROADMAP.md). For known issues, see [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md)."
- TECHNICAL_DEBT.md: "For long-term goals, see [ROADMAP.md](./ROADMAP.md). For post-release priorities, see [POST_SHIP.md](./POST_SHIP.md)."

## Acceptance Criteria
- Each file has cross-reference sentence(s) near the top'
sleep 2

# Task 14: Replace colors in run-protocol.component.ts
echo "[14/21] Replace Hardcoded Colors in run-protocol.component.ts"
jules new --repo "$REPO" 'Title: Replace Hardcoded Colors in run-protocol.component.ts

## Context
File: praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts
Reference: .agent/reports/recon_protocol_runner_visual.md

## Requirements
Replace these hardcoded colors with theme variables:
- text-blue-400 -> use var(--sys-tertiary) or themed class
- !from-green-500 !to-emerald-600 -> var(--gradient-primary) or create themed gradient
- shadow-green-500/* -> use theme shadow variables
- .border-green-500-30 (rgba(74, 222, 128, 0.3)) -> var(--theme-status-success-border)
- .bg-green-500-05 (rgba(74, 222, 128, 0.05)) -> var(--theme-status-success-muted)

## Acceptance Criteria
- No hardcoded green-500 or emerald-600 colors remain
- All status colors use --theme-status-* variables'
sleep 2

# Task 15: Replace colors in guided-setup.component.ts
echo "[15/21] Replace Hardcoded Colors in guided-setup.component.ts"
jules new --repo "$REPO" 'Title: Replace Hardcoded Colors in guided-setup.component.ts

## Context
File: praxis/web-client/src/app/features/run-protocol/components/guided-setup/guided-setup.component.ts
Reference: .agent/reports/recon_protocol_runner_visual.md

## Requirements
Replace hardcoded RGB values:
- rgb(34, 197, 94) -> var(--theme-status-success) [lines 268, 272, 300, 310]
- rgb(251, 191, 36) -> var(--theme-status-warning) [line 306]

## Acceptance Criteria
- No rgb(34, 197, 94) in the file
- No rgb(251, 191, 36) in the file
- Theme variables used instead'
sleep 2

# Task 16: Replace colors in protocol-summary.component.ts
echo "[16/21] Replace Hardcoded Colors in protocol-summary.component.ts"
jules new --repo "$REPO" 'Title: Replace Hardcoded Colors in protocol-summary.component.ts

## Context
File: praxis/web-client/src/app/features/run-protocol/components/protocol-summary/protocol-summary.component.ts
Reference: .agent/reports/recon_protocol_runner_visual.md

## Requirements
Replace Tailwind color classes:
- bg-green-500/10 -> var(--theme-status-success-muted)
- text-green-500 -> var(--theme-status-success)
- border-green-500/20 -> var(--theme-status-success-border)
- text-red-500 -> var(--status-error)

## Acceptance Criteria
- No green-500 or red-500 Tailwind classes remain
- Themed CSS used instead'
sleep 2

# Task 17: Replace colors in live-dashboard.component.ts
echo "[17/21] Replace Hardcoded Colors in live-dashboard.component.ts"
jules new --repo "$REPO" 'Title: Replace Hardcoded Colors in live-dashboard.component.ts

## Context
Search for file: live-dashboard.component.ts in praxis/web-client
Reference: .agent/reports/recon_protocol_runner_visual.md

## Requirements
Replace Tailwind color classes:
- text-green-600 -> var(--theme-status-success)
- text-gray-400 -> var(--theme-text-tertiary)
- bg-green-100 -> var(--theme-status-success-muted)
- bg-red-100 -> var(--theme-status-error-muted)
- bg-gray-900 -> var(--mat-sys-surface-container)

## Acceptance Criteria
- No green-600, gray-400, green-100, red-100, gray-900 Tailwind classes'
sleep 2

# Task 18: Replace colors in protocol-detail-dialog.component.ts
echo "[18/21] Replace Tailwind Colors in protocol-detail-dialog.component.ts"
jules new --repo "$REPO" 'Title: Replace Tailwind Colors in protocol-detail-dialog.component.ts

## Context
File: praxis/web-client/src/app/features/protocols/components/protocol-detail-dialog/protocol-detail-dialog.component.ts
Reference: .agent/reports/recon_theme_variables.md

## Requirements
- Find text-yellow-500 Tailwind class (around line 200)
- Replace with proper themed class using var(--theme-status-warning)

## Acceptance Criteria
- No text-yellow-500 Tailwind class in the file
- Warning color uses theme variable'
sleep 2

# Task 19: Replace colors in settings.component.ts
echo "[19/21] Replace Tailwind Colors in settings.component.ts"
jules new --repo "$REPO" 'Title: Replace Tailwind Colors in settings.component.ts

## Context
File: praxis/web-client/src/app/features/settings/components/settings.component.ts
Reference: .agent/reports/recon_theme_variables.md

## Requirements
- Find text-green-600 and dark:text-green-400 (around line 136)
- Replace with proper themed class using var(--theme-status-success)

## Acceptance Criteria
- No text-green-600 or dark:text-green-400 in the file
- Success color uses theme variable'
sleep 2

# Task 20: Create gradient logo SVG
echo "[20/21] Create Gradient Logo SVG"
jules new --repo "$REPO" 'Title: Create Gradient Logo SVG

## Context
File: praxis/web-client/src/assets/logo/praxis_logo.svg (base logo)
Reference: .agent/reports/recon_logo_branding.md

## Requirements
Copy praxis_logo.svg to praxis_logo_gradient.svg and modify:
1. Add <defs> section before paths with:
   <linearGradient id="praxis-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
     <stop offset="0%" style="stop-color:#ED7A9B"/>
     <stop offset="50%" style="stop-color:#ff8fa8"/>
     <stop offset="100%" style="stop-color:#73A9C2"/>
   </linearGradient>
2. Change fill="#000000" to fill="url(#praxis-gradient)" on all paths

## Acceptance Criteria
- praxis/web-client/src/assets/logo/praxis_logo_gradient.svg exists
- Contains linearGradient definition
- Paths use url(#praxis-gradient) fill'
sleep 2

# Task 21: Move port_docstrings.py
echo "[21/21] Move port_docstrings.py to scripts/"
jules new --repo "$REPO" 'Title: Move port_docstrings.py to scripts/

## Context
port_docstrings.py is a utility script at repository root
Reference: .agent/reports/recon_repo_cleanup.md

## Requirements
- Move port_docstrings.py from repository root to scripts/ directory
- Ensure the file contents are preserved

## Acceptance Criteria
- scripts/port_docstrings.py exists
- port_docstrings.py no longer exists at repository root'

echo ""
echo "=== All 21 tasks dispatched ==="
echo "Use: jules remote list --session | head -25  to check status"
