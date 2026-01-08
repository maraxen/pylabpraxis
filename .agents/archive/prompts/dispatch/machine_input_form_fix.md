# Task: Improve Machine Input Params UI

**Dispatch Mode**: 🧠 **Planning Mode**

## Context

Read these files first:

- `.agents/DEVELOPMENT_MATRIX.md` - See P2 item "Machine Input as JSON"
- `.agents/backlog/run_protocol_workflow.md`
- `.agents/backlog/dynamic_form_generation.md`

## Problem

Input parameters and connection information for adding machines are currently displayed as a single raw JSON field. It should be replaced with a structured, user-friendly form.

## Implementation

1. Identify the JSON input field in the "Add/Edit Machine" dialog.
2. Implement dynamic form generation based on the machine type's required parameters (using the schema information from the backend).
3. Use Material form fields (input, select, checkbox) instead of a raw text area.

## Testing

1. Open the "Add Machine" dialog.
2. Verify that parameters appear as individual form fields based on the selected machine type.
3. Verify that the form data correctly serializes back into the expected JSON structure for the backend.

## Definition of Done

- [x] Machine connection and input parameters use structured forms instead of raw JSON.
- [x] Form dynamically updates based on the selected machine type.
- [x] Update `.agents/backlog/run_protocol_workflow.md` - Mark task complete.
- [x] Update `.agents/DEVELOPMENT_MATRIX.md` - Mark "Machine Input as JSON" as complete.
