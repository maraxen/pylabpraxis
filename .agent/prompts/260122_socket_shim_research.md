# Agent Prompt: Socket/TCP Shim Research & Strategy

**Status:** 🟢 Not Started
**Priority:** P2
**Difficulty:** Hard
**Dependencies:** None
**Risk Level:** 🔴 Very High (Structural browser limitation)

---

## Overview

This is a **Recon-Plan-Execute** workflow for researching and potentially implementing Socket/TCP support in browser mode. **Unlike other shims, raw TCP sockets are fundamentally blocked by browser security.** This task focuses on:

1. Understanding the scope of the blocker
2. Researching viable workarounds (WebSocket bridge, WebTransport, etc.)
3. Documenting a recommendation

**CRITICAL:** Before proceeding to Plan or Execute phases, present your findings and await user approval.

---

## Phase 1: RECON (Deep Research)

### Persona

Use the **Deep Researcher** persona for this phase. This requires external research, not just codebase search.

### Objectives

1. **Map PLR Socket usage** - Find all backends using socket/TCP transport
2. **Catalog affected hardware** - PreciseFlex, Inheco SiLA, others
3. **Research browser constraints** - Why TCP is blocked, what's allowed
4. **Identify workaround patterns** - WebSocket proxies, WebTransport, etc.
5. **Evaluate trade-offs** - Complexity, latency, security

### Search Targets

```
# Find PLR Socket module
grep "class.*Socket" --include="*.py" pylabrobot/
grep "asyncio.*open_connection\|StreamReader\|StreamWriter" --include="*.py" pylabrobot/

# Find backends using sockets
grep -r "import socket\|from socket\|asyncio.open_connection" --include="*.py" pylabrobot/

# Find SiLA-related backends
grep -ri "sila" --include="*.py" pylabrobot/
```

### External Research Topics

1. **WebSocket-to-TCP proxy patterns** (e.g., websockify)
2. **WebTransport API** - QUIC-based streams in browsers
3. **Service Worker proxying** - Can service workers help?
4. **Electron/Tauri fallback** - Native shell alternatives
5. **Existing solutions** - How do other browser-based lab automation handle this?

### Skills to Reference

- `senior-architect/SKILL.md` - For architectural evaluation

### Output Format

```xml
<recon_report>
<socket_interface>
  <location>[path to pylabrobot.io.socket if exists]</location>
  <methods>[List of methods used: connect, read, write, close, etc.]</methods>
  <patterns>[async vs sync, context managers, etc.]</patterns>
</socket_interface>

<affected_backends>
  <backend name="[name]" path="[path]" hardware="[device]">
    <socket_usage>[How it uses sockets - host, port, protocol]</socket_usage>
    <criticality>[How important is browser support for this device?]</criticality>
  </backend>
</affected_backends>

<browser_constraints>
  <constraint name="Raw TCP blocked">[Explanation]</constraint>
  <constraint name="[other]">[Explanation]</constraint>
</browser_constraints>

<workaround_options>
  <option name="WebSocket-to-TCP Bridge (websockify)">
    <description>[How it works]</description>
    <pros>[Advantages]</pros>
    <cons>[Disadvantages]</cons>
    <complexity>[low|medium|high]</complexity>
    <latency_impact>[Estimate]</latency_impact>
  </option>
  
  <option name="WebTransport API">
    <description>[How it works]</description>
    <pros>[Advantages]</pros>
    <cons>[Disadvantages]</cons>
    <browser_support>[Current support status]</browser_support>
  </option>
  
  <option name="Native Shell (Electron/Tauri)">
    <description>[How it works]</description>
    <pros>[Advantages]</pros>
    <cons>[Disadvantages]</cons>
  </option>
  
  <option name="Accept Limitation">
    <description>[Mark these backends as prod-only]</description>
    <pros>[Simplicity]</pros>
    <cons>[Feature gap]</cons>
  </option>
</workaround_options>

<recommendation>
  <option>[Recommended approach]</option>
  <rationale>[Why]</rationale>
  <implementation_scope>[What would need to be built]</implementation_scope>
</recommendation>
</recon_report>
```

### Gate 1

**STOP HERE.** Present your recon report and await approval before proceeding to Plan phase.

---

## Phase 2: PLAN (Conditional)

### Persona

Use the **Oracle** persona for this phase.

### Gating Condition

Only proceed if the recon phase identified a viable workaround that the user wants to implement. If the recommendation is "Accept Limitation", this phase may be skipped.

### Possible Plan Paths

#### Path A: WebSocket-to-TCP Bridge (websockify)

If this is the chosen approach, plan for:

1. **Bridge server** - Python/Node.js server that proxies WebSocket ↔ TCP
2. **Socket shim** - `web_socket_shim.py` that uses WebSocket instead of raw TCP
3. **Patching** - Update `pyodide_io_patch.py`
4. **Documentation** - How users need to run the bridge

#### Path B: WebTransport Implementation

If browser support is sufficient:

1. **Research WebTransport + QUIC** - Deeper dive
2. **Device compatibility** - Can lab devices handle QUIC?
3. **Shim design** - Browser ↔ WebTransport ↔ device

#### Path C: Native Shell Wrapper

If browser-pure is abandoned for these devices:

1. **Electron/Tauri integration** - How to expose native sockets
2. **Hybrid mode** - Some devices browser, some native
3. **Distribution implications**

### Output Format

```xml
<plan_summary>
<approach>[Selected path]</approach>

<tasks count="[N]">
  <task id="1" title="[title]" difficulty="[easy|medium|hard]">
    <files>[List of files]</files>
    <estimate>[Time estimate]</estimate>
  </task>
</tasks>

<architecture_diagram>
[ASCII or description of data flow]
</architecture_diagram>

<deployment_requirements>
[What users need to run beyond the browser - bridge server, etc.]
</deployment_requirements>

<risks>
  <risk task="[task]">[Mitigation strategy]</risk>
</risks>
</plan_summary>
```

### Gate 2

**STOP HERE.** Present your plan and await approval before proceeding to Execute phase.

---

## Phase 3: EXECUTE (Conditional)

### Persona

Use the **Fixer** persona for this phase.

### Gating Condition

Only proceed if a plan was approved in Phase 2.

### Execution depends on chosen path - implementation details TBD based on Phase 2 decisions

---

## Context & References

**Known Socket Users (from audit):**

| Backend | Hardware | Protocol |
|:--------|:---------|:---------|
| PreciseFlex | Robot arms | Raw TCP |
| Inheco SiLA | Lab devices | SiLA over TCP |

**Related Reports:**

- `.agent/reports/io_transport_audit.md` - Source audit identifying Socket gap

**Knowledge Items:**

- `Praxis V2 Development Hub` - Browser-native execution patterns

**Research Starting Points:**

- websockify: <https://github.com/novnc/websockify>
- WebTransport: <https://developer.mozilla.org/en-US/docs/Web/API/WebTransport_API>
- SiLA specification: <https://sila-standard.com/>

---

## On Completion

**If workaround implemented:**

- [ ] Socket shim created and patched
- [ ] Bridge server (if needed) documented
- [ ] Verification with target hardware
- [ ] Committed and documented

**If limitation accepted:**

- [ ] Documentation updated to clarify prod-only backends
- [ ] Error handling improved for browser mode
- [ ] ROADMAP updated if this affects milestones

---

## References

- `.agent/README.md` - Environment overview
- `.agent/TECHNICAL_DEBT.md` - Related debt items
