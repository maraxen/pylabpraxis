# SDET Static Analysis: {FILE_NAME}.spec.ts

**Target File:** [{FILE_NAME}.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/{FILE_NAME}.spec.ts)  
**Review Date:** {DATE}  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
[Concisely summarize the exact functionality, UI elements, and state changes this test file verifies.]

### Assertions (Success Criteria)
[List the key assertions (what defines "success" for this test?).]

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code
[Identify brittle logic (e.g., hardcoded waits, relying on non-unique CSS selectors, ignoring strict mode).]

### Modern Standards (2026) Evaluation
[Evaluate against current best practices for Playwright/TypeScript/Angular:]
- **User-Facing Locators**: [getByRole, getByLabel vs. CSS/XPaths]
- **Test Isolation**: [afterEach cleanup, side effects]
- **Page Object Model (POM)**: [Effectiveness of abstraction]
- **Async Angular Handling**: [Waiting for signals/state vs. timeouts]

---

## 3. Test Value & Classification

### Scenario Relevance
[Critical journey ("Happy Path") vs. edge case. Realistic user scenario?]

### Classification
[True E2E Test vs. Interactive Unit Test (mocking levels).]

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow
[Step-by-step description of the intended user workflow.]

### Contextual Fit
[Role in the larger application ecosystem.]

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths
[Specific gaps in logic relative to complexity.]

### Domain Specifics
- **Data Integrity**: [Validation of data parsing/loading]
- **Simulation vs. Reality**: [Environment instantiation]
- **Serialization**: [Correctness of arguments passed to workers]
- **Error Handling**: [Failure state coverage]

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 0/10 | |
| **Best Practices** | 0/10 | |
| **Test Value** | 0/10 | |
| **Isolation** | 0/10 | |
| **Domain Coverage** | 0/10 | |

**Overall**: **0/10**
