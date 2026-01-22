# Agent Prompt: Global Module Shimming (Direct Import Bypass Fix)

**Status:** 🟢 Not Started
**Priority:** P1
**Difficulty:** Medium
**Dependencies:** Existing shims (Serial, USB, FTDI)
**Risk Level:** 🟠 Moderate (Multiple backends affected)

---

## Overview

This is a **Recon-Plan-Execute** workflow for implementing global `sys.modules` shimming. Currently, backends that bypass `pylabrobot.io` and perform `import serial`, `import usb`, or `import hid` directly will fail in Pyodide even if our shims work.

**Problem Statement:**

```python
# Current: We patch pylabrobot.io.Serial = WebSerial
# But this fails:
import serial  # <-- Tries to load pyserial, which doesn't exist in Pyodide
from serial import Serial

# Similar issues:
import usb.core  # <-- pyusb doesn't exist
import hid       # <-- hidapi doesn't exist
```

**Solution:** Inject shim modules into `sys.modules` so that `import serial` returns our WebSerial-based module.

**CRITICAL:** Before proceeding to Plan or Execute phases, present your findings and await user approval.

---

## Phase 1: RECON

### Persona

Use the **Explorer/Recon** persona for this phase.

### Objectives

1. **Find direct imports** - All backends doing `import serial`, `import usb`, `import hid` directly
2. **Catalog constants/classes used** - What do they import from these modules?
3. **Study pyserial API** - What constants and classes need shimming (e.g., `serial.EIGHTBITS`)
4. **Study pyusb API** - What from `usb.core` needs shimming
5. **Study hidapi API** - What needs shimming

### Search Targets

```bash
# Find direct serial imports (NOT from pylabrobot)
grep -r "^import serial\|^from serial" --include="*.py" pylabrobot/ | grep -v "pylabrobot.io"

# Find direct usb imports  
grep -r "^import usb\|^from usb" --include="*.py" pylabrobot/ | grep -v "pylabrobot.io"

# Find direct hid imports
grep -r "^import hid\|^from hid" --include="*.py" pylabrobot/

# Find serial constants usage
grep -r "serial\.[A-Z]" --include="*.py" pylabrobot/

# Check how existing patch works
view: praxis/web-client/src/assets/shims/pyodide_io_patch.py
```

### Reference Documentation

- pyserial API: <https://pyserial.readthedocs.io/en/latest/pyserial_api.html>
- pyusb API: <https://github.com/pyusb/pyusb>
- hidapi API: <https://github.com/trezor/cython-hidapi>

### Output Format

```xml
<recon_report>
<direct_imports>
  <import module="serial" backend="[backend_name]" path="[path]">
    <usage>[What they import: Serial class, constants, etc.]</usage>
    <constants>[EIGHTBITS, PARITY_NONE, etc.]</constants>
  </import>
  
  <import module="usb.core" backend="[backend_name]" path="[path]">
    <usage>[What they import: Device, find, etc.]</usage>
  </import>
</direct_imports>

<required_shim_exports>
  <module name="serial">
    <class name="Serial">[Already have WebSerial]</class>
    <constant name="EIGHTBITS" value="8"/>
    <constant name="PARITY_NONE" value="N"/>
    [...]
  </module>
  
  <module name="usb.core">
    <class name="Device">[Need mock or WebUSB wrapper]</class>
    <function name="find">[Need implementation]</function>
  </module>
  
  <module name="hid">
    <class name="device">[Need WebHID wrapper - depends on HID shim]</class>
    <function name="enumerate">[Need implementation]</function>
  </module>
</required_shim_exports>

<implementation_strategy>
  <approach>[sys.modules injection vs importlib hook vs ...]</approach>
  <rationale>[Why this approach]</rationale>
</implementation_strategy>
</recon_report>
```

### Gate 1

**STOP HERE.** Present your recon report and await approval before proceeding to Plan phase.

---

## Phase 2: PLAN

### Persona

Use the **Oracle** persona for this phase.

### Prerequisites

- Completed Recon report from Phase 1
- User approval to proceed

### Skills to Reference

- `writing-plans/SKILL.md` - For plan structure

### Objectives

1. Design the sys.modules injection strategy
2. Create compatibility layer for pyserial constants
3. Create compatibility layer for pyusb (if needed)
4. Integrate with existing `pyodide_io_patch.py`

### Plan Considerations

```python
# Proposed pattern for pyodide_io_patch.py
def patch_pylabrobot_io():
    # ... existing patches ...
    
    # NEW: Global module shimming
    inject_serial_shim()
    inject_usb_shim()
    inject_hid_shim()

def inject_serial_shim():
    """Make 'import serial' work in Pyodide."""
    import sys
    from web_serial_shim import WebSerial
    
    # Create a fake 'serial' module
    class SerialModule:
        Serial = WebSerial
        EIGHTBITS = 8
        FIVEBITS = 5
        SIXBITS = 6
        SEVENBITS = 7
        PARITY_NONE = 'N'
        PARITY_EVEN = 'E'
        PARITY_ODD = 'O'
        STOPBITS_ONE = 1
        STOPBITS_TWO = 2
        # ... etc
    
    sys.modules['serial'] = SerialModule()
    sys.modules['serial.tools'] = ...  # If needed
    sys.modules['serial.tools.list_ports'] = ...  # If needed
```

### Output Format

```xml
<plan_summary>
<tasks count="[N]">
  <task id="1" title="Create SerialModule shim">
    <files>Modify: pyodide_io_patch.py</files>
    <constants>[List all pyserial constants to shim]</constants>
  </task>
  
  <task id="2" title="Create USBModule shim (if needed)">
    <files>Modify: pyodide_io_patch.py</files>
    <approach>[Description]</approach>
  </task>
  
  <task id="3" title="Verify affected backends load">
    <backends>[List of backends to test]</backends>
    <verification>[How to verify]</verification>
  </task>
</tasks>

<affected_backends>
  <backend name="[name]" path="[path]" status="should_work_after"/>
</affected_backends>
</plan_summary>
```

### Gate 2

**STOP HERE.** Present your plan and await approval before proceeding to Execute phase.

---

## Phase 3: EXECUTE

### Persona

Use the **Fixer** persona for this phase.

### Prerequisites

- Completed plan from Phase 2
- User approval to proceed

### Skills to Reference

- `verification-before-completion/SKILL.md` - Verify before claiming done
- `atomic-git-commit/SKILL.md` - Commit after each task

### Verification Strategy

```python
# Test imports work in Pyodide (via browser console or JupyterLite)
import serial
print(serial.EIGHTBITS)  # Should print 8
print(serial.Serial)     # Should be WebSerial

from serial import Serial
s = Serial(baudrate=9600)  # Should work

import usb.core
# Should not raise ImportError
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
</task>

<backends_verified>
  <backend name="[name]" loads="yes|no">[Notes]</backend>
</backends_verified>

<summary>
[Overall status and next steps]
</summary>
</execution_report>
```

---

## Context & References

**Primary File to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/assets/shims/pyodide_io_patch.py` | Central patching module |

**Existing Shims:**

| Path | Description |
|:-----|:------------|
| `web_serial_shim.py` | WebSerial class to reuse |
| `web_usb_shim.py` | WebUSB class to reuse |
| `web_ftdi_shim.py` | WebFTDI class (reference) |

**Known Direct Import Offenders (from audit):**

- `BioShake` backend - `import serial`
- `MasterFlex` backend - `import serial`
- `Cytomat` backend - `import serial`

**Reports:**

- `.agent/reports/io_transport_audit.md` - Identified this gap

---

## On Completion

- [ ] `inject_serial_shim()` implemented with all pyserial constants
- [ ] `inject_usb_shim()` implemented (if needed)
- [ ] `inject_hid_shim()` implemented (can stub if HID shim not ready)
- [ ] Affected backends verified to load in Pyodide
- [ ] All lints pass
- [ ] Committed with descriptive message
- [ ] Update DEVELOPMENT_MATRIX.md

---

## References

- `.agent/README.md` - Environment overview
- pyserial constants: <https://pyserial.readthedocs.io/en/latest/pyserial_api.html#constants>
