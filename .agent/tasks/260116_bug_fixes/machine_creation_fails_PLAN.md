# Machine Creation Fix Plan

## Goal

Fix the "Machine Creation Fails - NOT NULL constraint" issue where adding a new machine in Browser Mode fails due to missing `maintenance_enabled` and `maintenance_schedule_json` fields.

## User Review Required
>
> [!NOTE]
> This fix addresses a critical blocker for machine creation in Browser Mode. It involves changes to both the Repository layer (to allow inserting these fields) and the Service layer (to provide default values).

## Proposed Changes

### Core Database Layer

#### [MODIFY] [repositories.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/db/repositories.ts)

- Update `MachineRepository.create` method.
- Add `'maintenance_enabled'` and `'maintenance_schedule_json'` to the `machineFields` array.
- This ensures these fields are included in the generated `INSERT` statement.

### Asset Service Layer

#### [MODIFY] [asset.service.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/services/asset.service.ts)

- Update `createMachine` method in `AssetService`.
- When creating the `newMachine` object for Browser Mode, add default values:
  - `maintenance_enabled: false`
  - `maintenance_schedule_json: '{}'` (empty JSON object as string, for SQLite TEXT column)
- This satisfies the `NOT NULL` constraint in the SQLite schema.

**Note**: Verify that `maintenance_schedule_json` is stored as a JSON string (TEXT column in SQLite). If the ORM/repository layer expects a parsed object, use `{}` instead of `'{}'`.

## Verification Plan

### Automated Tests

- **Update Unit Test**: Modify `praxis/web-client/src/app/features/assets/services/asset.service.spec.ts`.
  - In `Machine CRUD in Browser Mode` -> `should create machine...`, add expectations to verify that `mockMachineRepo.create` is called with an object containing the new maintenance fields.
- **Run Test**:

  ```bash
  npx vitest run praxis/web-client/src/app/features/assets/services/asset.service.spec.ts
  ```

### Manual Verification

1. Start the application in Browser Mode:

   ```bash
   npm run start:browser
   ```

2. Open the application in the browser.
3. Navigate to **Playground** or **Inventory**.
4. Click **Add Asset** -> **Add Machine**.
5. Fill in required details (Name, Definition, etc.) and click **Create**.
6. **Expectation**: The machine is created successfully without error, and appears in the list.
