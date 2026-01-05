# Task: Fix API Documentation Rendering

**Dispatch Mode**: 🧠 **Planning Mode**

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P1 item "API Docs Not Rendering"
- `.agents/backlog/docs.md`

## Problem

FastAPI documentation (`/docs` or `/redoc`) is not rendering in browser mode (or possibly lite mode), despite several documentation tasks being marked as complete.

## Implementation

1. Check `praxis/backend/main.py` for OpenAPI/Swagger configuration.
2. Verify routing for `/docs` and any security middleware that might be blocking access.
3. Ensure the `docs.md` backlog truly reflects the state of the backend documentation server.

## Testing

1. Attempt to load `http://localhost:8000/docs` and verify the Swagger UI appears and is interactive.

## Definition of Done

- [ ] API documentation is accessible and functional in all applicable modes.
- [ ] Update `.agents/backlog/docs.md` with current state.
- [ ] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "API Docs Not Rendering" as complete

## Files Likely Involved

- `praxis/backend/main.py`
