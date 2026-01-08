# REPL Autocompletion Backlog

**Priority**: Medium
**Owner**: Full Stack
**Created**: 2025-12-30
**Status**: MVP In Progress

---

## Overview

Implement Jedi-based autocompletion for the PyLabRobot REPL in browser mode (Pyodide). Jedi provides intelligent code completion with type inference, documentation, and signature help.

---

## Current State

- **Tab completion**: Uses `rlcompleter` which only completes based on globals dictionary
- **Limitations**:
  - No attribute completion for imported modules
  - No type inference
  - No documentation/signature hints
  - No method parameter completion

---

## Implementation Phases

### Phase 1: MVP - Basic Jedi Integration ✅ COMPLETED 2025-12-30

**Goal**: Replace `rlcompleter` with Jedi for basic tab completion.

**Tasks**:
- [x] Install `jedi` via micropip during Pyodide bootstrap
- [x] Create `get_jedi_completions()` function in `web_bridge.py`
- [x] Update worker to call Jedi completions
- [x] Pass full source context for better completions
- [x] Handle Jedi installation failure gracefully (fallback to rlcompleter)
- [x] Common prefix completion for multiple matches
- [x] Column-based display for completion list
- [x] Add `get_signatures()` API for future signature help

**Known Constraints**:
- Jedi is ~1.5MB, may increase load time
- Some Jedi features may not work in Pyodide (e.g., file-based project analysis)

### Phase 2: Enhanced Completion UX

**Goal**: Improve the completion experience with UI enhancements.

**Tasks**:
- [ ] Show completion popup instead of inline list
- [ ] Display completion type icons (function, class, variable, module)
- [ ] Show brief documentation in popup
- [ ] Support cycling through completions with Tab
- [ ] Add fuzzy matching for completions

### Phase 3: Signature Help

**Goal**: Show function signatures when typing `(`.

**Tasks**:
- [ ] Detect `(` keypress after function name
- [ ] Call Jedi's `get_signatures()` API
- [ ] Display signature popup above cursor
- [ ] Highlight current parameter as user types
- [ ] Show parameter documentation

### Phase 4: PLR-Specific Completions

**Goal**: Enhance completions with PLR-specific context.

**Tasks**:
- [ ] Pre-populate Jedi with PLR type stubs
- [ ] Complete deck positions (e.g., `lh.deck.get_resource("plate_")`
- [ ] Complete machine method parameters based on capabilities
- [ ] Suggest protocol patterns (common PLR workflows)

### Phase 5: Multi-line and Context-Aware

**Goal**: Support completions across multi-line inputs.

**Tasks**:
- [ ] Track full input buffer across lines for context
- [ ] Handle async/await completions
- [ ] Complete inside function definitions
- [ ] Complete class method arguments

---

## Technical Details

### Jedi API in Pyodide

```python
import jedi

def get_jedi_completions(source: str, line: int = 1, column: int = None) -> list[dict]:
    """
    Get completions using Jedi.

    Args:
        source: Full source code up to cursor
        line: Line number (1-indexed)
        column: Column position (0-indexed), defaults to end of source

    Returns:
        List of completion dicts with name, type, docstring
    """
    if column is None:
        column = len(source.split('\n')[-1])

    script = jedi.Script(source)
    completions = script.complete(line, column)

    return [
        {
            'name': c.name,
            'type': c.type,  # 'function', 'class', 'module', 'param', etc.
            'description': c.description,
            'docstring': c.docstring(fast=True),  # fast=True avoids full parsing
        }
        for c in completions
    ]
```

### Frontend Integration

The REPL component needs to be updated to:
1. Pass full source context (not just last token)
2. Handle structured completion responses (not just string list)
3. Display completion popup with metadata

### Worker Message Flow

```
[User types Tab]
     ↓
[ReplComponent.handleTabCompletion()]
     ↓ sends { type: 'COMPLETE', code: fullSource, line, column }
[python.worker.ts]
     ↓ calls bridge.get_jedi_completions()
[web_bridge.py]
     ↓ returns [{ name, type, docstring }, ...]
[python.worker.ts]
     ↓ posts { type: 'COMPLETE_RESULT', matches: [...] }
[PythonRuntimeService]
     ↓ returns structured completions
[ReplComponent]
     ↓ displays popup or inline completions
```

---

## Dependencies

- `jedi>=0.19.0` (pure Python, Pyodide compatible)
- `parso` (Jedi dependency, pure Python)

---

## Success Metrics

1. **MVP**: Tab completion works for Python builtins, PLR classes, and imported modules
2. **Phase 2**: Completion popup displays in <100ms
3. **Phase 3**: Signature help appears for all PLR machine methods
4. **Phase 4**: PLR-specific completions reduce typing by 50%+

---

## Related Files

**Frontend**:
- `praxis/web-client/src/app/features/repl/repl.component.ts`
- `praxis/web-client/src/app/core/services/python-runtime.service.ts`
- `praxis/web-client/src/app/core/workers/python.worker.ts`

**Python**:
- `praxis/web-client/src/assets/python/web_bridge.py`

---

## Risk Mitigation

1. **Jedi fails to install**: Fallback to rlcompleter with console warning
2. **Jedi is slow**: Cache Script objects, use fast=True for docstrings
3. **Pyodide incompatibility**: Test all Jedi features, document limitations
