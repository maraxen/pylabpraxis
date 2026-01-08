# Task: Protocol Inference "Sharp Bits" Documentation (P3)

## Context

Document edge cases, gotchas, and limitations of the protocol inference system so users understand what to watch out for.

## Backlog Reference

See: `.agents/backlog/docs.md` - Protocol Inference "Sharp Bits" item

## Scope

Create documentation covering:

### Type Inference Limitations

- When explicit types are needed vs inferred
- Complex generic types that may not parse correctly
- Union types handling
- Optional types handling

### Resource Hierarchy Assumptions

- How parent resources are inferred
- When explicit parent hints are needed
- Itemized resource child detection

### Sequences and Container Type Handling

- `list[Well]` vs `Sequence[Well]` differences
- Nested container types
- Variable-length sequences

### Known Unsupported Patterns

- Patterns that the static analysis cannot handle
- Workarounds for unsupported patterns
- When to use explicit decorator hints

### Best Practices

- How to write protocols for best inference
- Decorator hints that help inference
- Common mistakes to avoid

## Files to Create

- `docs/user-guide/protocol-inference-sharp-bits.md`

Or add a section to existing protocol documentation:
- `docs/user-guide/protocols.md`

## Research Required

Examine the static analysis code to understand limitations:
- `praxis/backend/utils/plr_static_analysis/parser.py`
- `praxis/backend/utils/plr_static_analysis/visitors/`
- `praxis/backend/utils/plr_static_analysis/resource_hierarchy.py`

## Expected Outcome

- Clear documentation of protocol inference limitations
- Users know what patterns to avoid
- Troubleshooting guide for inference issues
