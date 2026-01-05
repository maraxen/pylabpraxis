# Dispatch Prompts Index - 2026-01-04

## Overview

This directory contains dispatch prompts for agents to work on the current roadmap items.

## Priority Order

### P1 - Critical (Do First)

| # | Task | File | Difficulty |
|---|------|------|------------|
| 01 | Fix Add Resource Not Working | `01_fix_add_resource.md` | M |

### P2 - High Priority (New Features)

| # | Task | File | Difficulty |
|---|------|------|------------|
| 02 | Visual Index Selection | `02_visual_index_selection.md` | L |
| 03 | REPL → JupyterLite Migration | `03_repl_jupyterlite.md` | XL |
| 04 | Hardware Discovery Menu | `04_hardware_discovery_menu.md` | M |
| 08 | Final Visual QA & Test Suite | `08_final_visual_qa.md` | L |

### P3 - UI/UX Polish

| # | Task | File | Difficulty |
|---|------|------|------------|
| 05 | Resource Inventory Filters | `05_resource_inventory_filters.md` | M |
| 06 | UI Visual Tweaks | `06_ui_visual_tweaks.md` | S |
| 07 | Protocol Inference "Sharp Bits" Docs | `07_sharp_bits_docs.md` | M |

## Usage

To dispatch an agent on a task:

```
Read the prompt file and use it to guide the agent's work.
Each prompt contains:
- Context and background
- Backlog reference
- Scope and phases
- Files to create/modify
- Expected outcomes
```

## Related Documents

- [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) - Full item tracking
- [ROADMAP.md](../../ROADMAP.md) - Current priorities
- [backlog/](../../backlog/) - Detailed feature backlogs
