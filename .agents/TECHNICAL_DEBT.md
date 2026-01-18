# Technical Debt Log

## E2E Testing
- [ ] **Data Seeding in Browser Mode**: The E2E tests for charts (`medium-priority-capture.spec.ts`) fail because the mock database is not reliably seeded with protocol runs when `resetdb=true` is used. This prevents the "Capture Charts" test from finding protocol cards to execute.
  - **Impact**: Cannot automatically validate charts/visualizations in E2E pipeline.
  - **Mitigation**: Manually verify charts or fix `SqliteService` seeding logic in browser mode.
