# Agent Prompt: WebHID Shim Implementation

**Status:** 🟢 Not Started
**Priority:** P1
**Difficulty:** Medium
**Dependencies:** Completed USB/Serial/FTDI shims
**Risk Level:** 🔴 High (Inheco devices are industry standard)

---

## Overview

This is a **Recon-Plan-Execute** workflow for implementing the WebHID shim to enable Inheco heating/shaking devices in browser mode. The task is structured in three phases with a gate between each.

**CRITICAL:** Before proceeding to Plan or Execute phases, present your findings and await user approval.

---

## Phase 1: RECON

### Persona

Use the **Explorer/Recon** persona for this phase. You are a fast codebase navigation specialist conducting reconnaissance.

### Objectives

1. **Find the PLR HID interface** - Locate `pylabrobot.io.hid` and understand its API contract
2. **Map Inheco backends** - Find all backends that use HID transport
3. **Study existing shim patterns** - Analyze `web_usb_shim.py` and `web_ftdi_shim.py` for patterns
4. **Research WebHID API** - Understand browser WebHID API capabilities and constraints

### Search Targets

```
# Find PLR HID module
grep "class.*HID" --include="*.py" pylabrobot/

# Find Inheco backends
grep -r "from pylabrobot.io" --include="*.py" | grep -i "hid\|inheco"

# Study existing shim patterns (these are your pattern sources)
view: praxis/web-client/src/assets/shims/web_usb_shim.py
view: praxis/web-client/src/assets/shims/web_ftdi_shim.py
view: praxis/web-client/src/assets/shims/pyodide_io_patch.py
```

### Skills to Reference

- `systematic-debugging/SKILL.md` - For investigation methodology
- `senior-architect/SKILL.md` - For architectural patterns

### Output Format

Provide your findings in this structure:

```xml
<recon_report>
<hid_interface>
  <location>[path to pylabrobot.io.hid module]</location>
  <methods>[List of methods that need shimming: setup, stop, read, write, etc.]</methods>
  <constructor_args>[Arguments the HID class takes]</constructor_args>
</hid_interface>

<inheco_backends>
  <backend name="[name]" path="[path]">
    <hid_usage>[How it uses HID - constructs, methods called, etc.]</hid_usage>
  </backend>
</inheco_backends>

<shim_patterns>
  <pattern name="BroadcastChannel" source="[shim]">[Description]</pattern>
  <pattern name="Pyodide JS Bridge" source="[shim]">[Description]</pattern>
</shim_patterns>

<webhid_api>
  <capabilities>[What WebHID can do]</capabilities>
  <constraints>[Known limitations]</constraints>
  <mapping>[How WebHID maps to PLR HID interface]</mapping>
</webhid_api>

<risks>
  <risk severity="high|medium|low">[Description]</risk>
</risks>
</recon_report>
```

### Gate 1

**STOP HERE.** Present your recon report and await approval before proceeding to Plan phase.

---

## Phase 2: PLAN

### Persona

Use the **Oracle** persona for this phase. You are a strategic technical advisor creating an implementation plan.

### Prerequisites

- Completed Recon report from Phase 1
- User approval to proceed

### Skills to Reference

- `writing-plans/SKILL.md` - For plan structure (save to `docs/plans/`)
- `senior-architect/SKILL.md` - For architectural decisions

### Objectives

1. Create a detailed implementation plan for `web_hid_shim.py`
2. Plan the patch integration into `pyodide_io_patch.py`
3. Define the BroadcastChannel protocol for HID operations
4. Design the Angular-side HID manager service

### Plan Structure

Create an implementation plan at `docs/plans/YYYY-MM-DD-web-hid-shim.md` with:

```markdown
# WebHID Shim Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable browser-mode Inheco device support via WebHID API shim

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** Python (Pyodide), TypeScript (Angular), WebHID API

---

### Task 1: Create web_hid_shim.py

**Files:**
- Create: `praxis/web-client/src/assets/shims/web_hid_shim.py`

**Step 1:** [Detailed implementation with code]
**Step 2:** [...]

### Task 2: Update pyodide_io_patch.py

**Files:**
- Modify: `praxis/web-client/src/assets/shims/pyodide_io_patch.py`

[...]

### Task 3: Create Angular HID Manager Service (if needed)

[...]
```

### Output Format

```xml
<plan_summary>
<tasks count="[N]">
  <task id="1" title="[title]" difficulty="[easy|medium|hard]">
    <files>[List of files]</files>
    <estimate>[Time estimate]</estimate>
  </task>
</tasks>

<dependencies>
  <dependency from="[task]" to="[task]">[Reason]</dependency>
</dependencies>

<risks>
  <risk task="[task]">[Mitigation strategy]</risk>
</risks>
</plan_summary>
```

### Gate 2

**STOP HERE.** Present your plan and await approval before proceeding to Execute phase.

---

## Phase 3: EXECUTE

### Persona

Use the **Fixer** persona for this phase. You are a fast, focused implementation specialist.

### Prerequisites

- Completed plan from Phase 2
- User approval to proceed

### Skills to Reference

- `test-driven-development/SKILL.md` - Write tests alongside implementation
- `verification-before-completion/SKILL.md` - Verify before claiming done
- `atomic-git-commit/SKILL.md` - Commit after each task

### Execution Rules

1. Follow the plan task-by-task
2. Run verification after each task
3. Commit after each logical unit of work
4. Report blockers immediately, don't guess

### Verification Commands

```bash
# Type check shims
cd praxis/web-client && npm run lint

# Check Pyodide bootstrap loads shims
grep -r "web_hid_shim" praxis/web-client/src/

# Verify patch is applied correctly (after Full integration)
# (Manual browser test with Inheco device)
```

### Output Format

```xml
<execution_report>
<task id="[N]" status="complete|blocked|partial">
  <changes>
    <file path="[path]">[What changed]</file>
  </changes>
  <verification>
    <check name="[check]" result="pass|fail">[Details]</check>
  </verification>
  <commit>[Commit hash or message]</commit>
</task>

<blockers>
  <blocker task="[N]">[Description and resolution needed]</blocker>
</blockers>

<summary>
[Overall status and next steps]
</summary>
</execution_report>
```

---

## Context & References

**Existing Shims (Pattern Sources):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/assets/shims/web_serial_shim.py` | WebSerial implementation with SerialProxy |
| `praxis/web-client/src/assets/shims/web_usb_shim.py` | WebUSB implementation |
| `praxis/web-client/src/assets/shims/web_ftdi_shim.py` | WebFTDI for CLARIOstar |
| `praxis/web-client/src/assets/shims/pyodide_io_patch.py` | Central patching module |

**Knowledge Items:**

- `Praxis V2 Development Hub` - Browser-native execution patterns
- `Standardized Agent Infrastructure` - MCP dispatch patterns

**Reports:**

- `.agent/reports/io_transport_audit.md` - Source audit identifying HID gap

**Constraints:**

- Use `uv run` for Python, `npm` for Angular
- Follow existing shim patterns exactly
- Backend: `praxis/backend`, Frontend: `praxis/web-client`
- Styling: Use existing service patterns

---

## On Completion

- [ ] `web_hid_shim.py` created and follows existing patterns
- [ ] `pyodide_io_patch.py` updated to patch HID
- [ ] HID patch status added to `get_io_status()`
- [ ] Angular HID manager service created (if needed)
- [ ] All lint/type checks pass
- [ ] Committed with descriptive message
- [ ] Update DEVELOPMENT_MATRIX.md
- [ ] Mark this prompt complete

---

## References

- `.agent/README.md` - Environment overview
- `.agent/TECHNICAL_DEBT.md` - Related debt items
- WebHID API: <https://developer.mozilla.org/en-US/docs/Web/API/WebHID_API>
