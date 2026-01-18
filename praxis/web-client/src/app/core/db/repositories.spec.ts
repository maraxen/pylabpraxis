import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ProtocolDefinitionRepository } from './repositories';
import type { Database } from 'sql.js';

describe('ProtocolDefinitionRepository', () => {
    let mockDb: any;
    let repo: ProtocolDefinitionRepository;

    beforeEach(() => {
        mockDb = {
            prepare: vi.fn().mockReturnValue({
                run: vi.fn(),
                free: vi.fn(),
                step: vi.fn().mockReturnValue(false),
                getAsObject: vi.fn(),
                bind: vi.fn().mockReturnValue(true)
            }),
            exec: vi.fn()
        };
        repo = new ProtocolDefinitionRepository(mockDb as unknown as Database);
    });

    it('should map database rows to ProtocolDefinition domain objects', () => {
        const rawRow = {
            accession_id: 'proto_1',
            name: 'Test Protocol',
            is_top_level: 1,
            simulation_result_json: JSON.stringify({
                passed: true,
                level_completed: 'exact',
                simulation_version: '1.0.0'
            }),
            inferred_requirements_json: JSON.stringify([{ requirement_type: 'tips' }]),
            failure_modes_json: '[]'
        };

        mockDb.exec.mockReturnValue([{
            columns: Object.keys(rawRow),
            values: [Object.values(rawRow)]
        }]);

        const protocols = repo.findTopLevel();
        const proto = protocols[0];

        expect(proto.accession_id).toBe('proto_1');
        expect(proto.name).toBe('Test Protocol');

        // Verify mapping
        expect(proto.simulation_result).toBeDefined();
        expect(proto.simulation_result?.passed).toBe(true);
        expect(proto.simulation_result?.level_completed).toBe('exact');

        expect(proto.inferred_requirements).toBeDefined();
        expect(proto.inferred_requirements?.length).toBe(1);
        expect(proto.inferred_requirements?.[0].requirement_type).toBe('tips');

        expect(proto.failure_modes).toEqual([]);

        // Verify raw fields are cleared
        expect((proto as any).simulation_result_json).toBeUndefined();
        expect((proto as any).inferred_requirements_json).toBeUndefined();
        expect((proto as any).failure_modes_json).toBeUndefined();
    });

    it('should handle null simulation result gracefully', () => {
        const rawRow = {
            accession_id: 'proto_2',
            simulation_result_json: null
        };

        mockDb.exec.mockReturnValue([{
            columns: Object.keys(rawRow),
            values: [Object.values(rawRow)]
        }]);

        const proto = repo.findTopLevel()[0];
        expect(proto.simulation_result).toBeUndefined();
    });

    it('should handle invalid JSON gracefully', () => {
        const rawRow = {
            accession_id: 'proto_3',
            simulation_result_json: '{ invalid json }'
        };

        mockDb.exec.mockReturnValue([{
            columns: Object.keys(rawRow),
            values: [Object.values(rawRow)]
        }]);

        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { });
        const proto = repo.findTopLevel()[0];

        expect(proto.simulation_result).toBeUndefined();
        expect(consoleSpy).toHaveBeenCalled();
        consoleSpy.mockRestore();
    });
});
