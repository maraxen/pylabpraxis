
import { Injectable } from '@angular/core';
import initSqlJs, { Database, SqlJsStatic } from 'sql.js';
import { from, Observable, of } from 'rxjs';
import { map, shareReplay, switchMap, tap } from 'rxjs/operators';
import { MOCK_PROTOCOLS } from '../../../assets/demo-data/protocols';
import { MOCK_PROTOCOL_RUNS } from '../../../assets/demo-data/protocol-runs';
import { MOCK_RESOURCES } from '../../../assets/demo-data/resources';
import { MOCK_MACHINES } from '../../../assets/demo-data/machines';

@Injectable({
    providedIn: 'root'
})
export class SqliteService {
    private db$: Observable<Database>;

    constructor() {
        this.db$ = from(this.initDb()).pipe(
            shareReplay(1)
        );
    }

    private async initDb(): Promise<Database> {
        try {
            const SQL = await initSqlJs({
                // Locate the wasm file. We'll need to make sure this is served correctly.
                // In Angular, putting it in assets/ is usually the way.
                locateFile: file => `./assets/wasm/${file}`
            });
            const db = new SQL.Database();
            this.seedDatabase(db);
            console.log('[SqliteService] Database initialized successfully');
            return db;
        } catch (error) {
            console.error('[SqliteService] Failed to initialize database:', error);
            // Re-throw to propagate the error through the observable chain
            throw new Error(`SQLite initialization failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }

    private seedDatabase(db: Database): void {
        // Create tables
        db.run(`
      CREATE TABLE IF NOT EXISTS protocols (
        accession_id TEXT PRIMARY KEY,
        name TEXT,
        description TEXT,
        is_top_level BOOLEAN,
        version TEXT,
        parameters_json TEXT
      );
    `);

        db.run(`
      CREATE TABLE IF NOT EXISTS protocol_runs (
        accession_id TEXT PRIMARY KEY,
        protocol_accession_id TEXT,
        status TEXT,
        created_at TEXT,
        parameters_json TEXT,
        user_params_json TEXT
      );
    `);

        db.run(`
      CREATE TABLE IF NOT EXISTS resources (
        accession_id TEXT PRIMARY KEY,
        name TEXT,
        type TEXT,
        properties_json TEXT
      );
    `);

        db.run(`
      CREATE TABLE IF NOT EXISTS machines (
        accession_id TEXT PRIMARY KEY,
        name TEXT,
        type TEXT,
        properties_json TEXT
      );
    `);


        // Seed Data
        const insertProtocol = db.prepare("INSERT INTO protocols VALUES (?, ?, ?, ?, ?, ?)");
        MOCK_PROTOCOLS.forEach(p => {
            const params = (p as any).parameters ? JSON.stringify((p as any).parameters) : null;
            insertProtocol.run([
                p.accession_id,
                p.name,
                (p as any).description || null,
                p.is_top_level ? 1 : 0,
                (p as any).version || null,
                params
            ]);
        });
        insertProtocol.free();

        const insertRun = db.prepare("INSERT INTO protocol_runs VALUES (?, ?, ?, ?, ?, ?)");
        MOCK_PROTOCOL_RUNS.forEach(r => {
            const params = (r as any).parameters ? JSON.stringify((r as any).parameters) : null;
            const userParams = (r as any).user_params ? JSON.stringify((r as any).user_params) : null;
            insertRun.run([
                r.accession_id,
                (r as any).protocol_definition_accession_id || null,
                r.status || null,
                r.created_at || null,
                params,
                userParams
            ]);
        });
        insertRun.free();

        const insertResource = db.prepare("INSERT INTO resources VALUES (?, ?, ?, ?)");
        MOCK_RESOURCES.forEach(r => {
            insertResource.run([
                r.accession_id,
                r.name,
                (r as any).type || 'unknown', // Default to unknown if missing
                JSON.stringify(r)
            ]);
        });
        insertResource.free();

        const insertMachine = db.prepare("INSERT INTO machines VALUES (?, ?, ?, ?)");
        MOCK_MACHINES.forEach(m => {
            insertMachine.run([
                m.accession_id,
                m.name,
                (m as any).type || null,
                JSON.stringify(m)
            ]);
        });
        insertMachine.free();


        console.log('[SqliteService] Database seeded with mock data');
    }

    public getProtocols(): Observable<any[]> {
        return this.db$.pipe(
            map(db => {
                const res = db.exec("SELECT * FROM protocols");
                if (res.length === 0) return [];
                return this.resultToObjects(res[0]);
            }),
            map(protocols => protocols.map(p => ({
                ...p,
                is_top_level: p.is_top_level === 1 || p.is_top_level === 'true', // SQLite boolean check
                parameters: p.parameters_json ? JSON.parse(p.parameters_json) : null
            })))
        );
    }

    public getProtocolRuns(): Observable<any[]> {
        return this.db$.pipe(
            map(db => {
                const res = db.exec("SELECT * FROM protocol_runs");
                if (res.length === 0) return [];
                return this.resultToObjects(res[0]);
            }),
            map(runs => runs.map(r => ({
                ...r,
                parameters: r.parameters_json ? JSON.parse(r.parameters_json) : null,
                user_params: r.user_params_json ? JSON.parse(r.user_params_json) : null,
                // Reconstruct nested protocol object if needed by UI, or fetch join
                protocol: { accession_id: r.protocol_accession_id, name: 'Unknown' }
            })))
        );
    }

    public getProtocolRun(id: string): Observable<any> {
        return this.getProtocolRuns().pipe(
            map(runs => runs.find(r => r.accession_id === id))
        );
    }

    public createProtocolRun(run: any): Observable<any> {
        return this.db$.pipe(
            map(db => {
                const stmt = db.prepare("INSERT INTO protocol_runs VALUES (?, ?, ?, ?, ?, ?)");
                const params = run.parameters ? JSON.stringify(run.parameters) : null;
                const userParams = run.user_params ? JSON.stringify(run.user_params) : null;

                // Handle both property names for protocol ID and fallback to null
                const protocolId = run.protocol_definition_accession_id || run.protocol_accession_id || null;

                stmt.run([
                    run.accession_id,
                    protocolId,
                    run.status || 'QUEUED',
                    run.created_at || new Date().toISOString(),
                    params,
                    userParams
                ]);
                stmt.free();
                return run;
            })
        );
    }


    private resultToObjects(res: { columns: string[], values: any[][] }): any[] {
        return res.values.map(row => {
            const obj: any = {};
            res.columns.forEach((col, i) => {
                obj[col] = row[i];
            });
            return obj;
        });
    }
}
