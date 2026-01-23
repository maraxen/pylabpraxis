/**
 * SQLite Service Module
 * 
 * Browser-mode database operations using OPFS-backed SQLite.
 */

// Core Types
export type { SqliteStatus, DatabaseExportMeta } from './sqlite.types';

// Core Services
export { SqliteService } from './sqlite.service';
export { SqliteOpfsService } from './sqlite-opfs.service';

// Sub-services (when extracted)
// export { SqliteSeedingService } from './sqlite-seeding.service';
// export { SqliteQueriesService } from './sqlite-queries.service';
// export { SqliteStateService } from './sqlite-state.service';
// export { SqliteExportService } from './sqlite-export.service';
