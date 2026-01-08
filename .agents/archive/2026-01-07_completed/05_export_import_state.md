# Prompt 5: Export/Import Browser State

**Priority**: P2
**Difficulty**: Small
**Type**: Easy Win

> **IMPORTANT**: Do NOT use the browser agent. Verify with automated tests only.

---

## Context

Users want to backup/restore browser mode data. Implement download/upload of the SQLite database.

---

## Tasks

### 1. Add Export Method to SqliteService

In `praxis/web-client/src/app/core/services/sqlite.service.ts`:

```typescript
/**
 * Export the current database as a downloadable file
 */
async exportDatabase(): Promise<void> {
  if (!this.db) {
    throw new Error('Database not initialized');
  }
  
  const data = this.db.export();
  const blob = new Blob([data], { type: 'application/x-sqlite3' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = `praxis-backup-${new Date().toISOString().slice(0,10)}.db`;
  a.click();
  
  URL.revokeObjectURL(url);
}

/**
 * Import a database file, replacing current data
 */
async importDatabase(file: File): Promise<void> {
  const buffer = await file.arrayBuffer();
  const data = new Uint8Array(buffer);
  
  // Close current database
  if (this.db) {
    this.db.close();
  }
  
  // Initialize with imported data
  this.db = new this.SQL.Database(data);
  
  // Save to IndexedDB
  await this.saveToIndexedDB();
  
  console.log('[SqliteService] Database imported successfully');
}
```

### 2. Add UI in Settings

In `praxis/web-client/src/app/features/settings/components/settings.component.ts`:

Add to template:

```html
<!-- Export/Import Section -->
<mat-card>
  <mat-card-header>
    <mat-icon mat-card-avatar>save_alt</mat-icon>
    <mat-card-title>Data Management</mat-card-title>
  </mat-card-header>
  <mat-card-content>
    <p class="text-sys-text-secondary mb-4">
      Export your browser data for backup or import a previous backup.
    </p>
    <div class="flex gap-4">
      <button mat-stroked-button (click)="exportData()">
        <mat-icon>download</mat-icon> Export Database
      </button>
      <button mat-stroked-button (click)="fileInput.click()">
        <mat-icon>upload</mat-icon> Import Database
      </button>
      <input #fileInput type="file" accept=".db" hidden (change)="importData($event)" />
    </div>
  </mat-card-content>
</mat-card>
```

Add methods:

```typescript
async exportData(): void {
  try {
    await this.sqliteService.exportDatabase();
    this.snackBar.open('Database exported', 'OK', { duration: 3000 });
  } catch (err) {
    this.snackBar.open('Export failed', 'OK', { duration: 3000 });
  }
}

async importData(event: Event): Promise<void> {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  
  const confirmed = confirm('This will replace all current data. Continue?');
  if (!confirmed) return;
  
  try {
    await this.sqliteService.importDatabase(file);
    this.snackBar.open('Database imported - refreshing...', 'OK', { duration: 2000 });
    setTimeout(() => window.location.reload(), 2000);
  } catch (err) {
    this.snackBar.open('Import failed', 'OK', { duration: 3000 });
  }
}
```

---

## Verification

```bash
cd praxis/web-client && npm test -- --include='**/settings*'
```

---

## Success Criteria

- [x] `exportDatabase()` downloads .db file
- [x] `importDatabase()` loads uploaded file
- [x] Settings UI has export/import buttons
- [x] Confirmation dialog on import
- [x] Page refresh after import
