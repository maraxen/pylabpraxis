import { TestBed } from '@angular/core/testing';
import { WorkcellViewService } from './workcell-view.service';
import { AssetService } from '@features/assets/services/asset.service';
import { Machine, Workcell, MachineStatus } from '@features/assets/models/asset.models';
import { of, firstValueFrom } from 'rxjs';
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('WorkcellViewService', () => {
    let service: WorkcellViewService;
    let assetServiceMock: any;

    const mockWorkcells: Workcell[] = [
        { accession_id: 'wc-1', name: 'Workcell 1', status: 'online' },
        { accession_id: 'wc-2', name: 'Workcell 2', status: 'online' }
    ];

    const mockMachines: Machine[] = [
        { accession_id: 'm1', name: 'Machine 1', status: MachineStatus.IDLE, workcell_accession_id: 'wc-1' },
        { accession_id: 'm2', name: 'Machine 2', status: MachineStatus.RUNNING, workcell_accession_id: 'wc-1' },
        { accession_id: 'm3', name: 'Machine 3', status: MachineStatus.ERROR, workcell_accession_id: 'wc-2' },
        { accession_id: 'm4', name: 'Machine 4', status: MachineStatus.OFFLINE } // Unassigned
    ];

    beforeEach(() => {
        assetServiceMock = {
            getMachines: vi.fn().mockReturnValue(of(mockMachines)),
            getWorkcells: vi.fn().mockReturnValue(of(mockWorkcells))
        };

        TestBed.configureTestingModule({
            providers: [
                WorkcellViewService,
                { provide: AssetService, useValue: assetServiceMock }
            ]
        });

        service = TestBed.inject(WorkcellViewService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    describe('loadWorkcellGroups', () => {
        it('should group machines by workcell', async () => {
            const groups = await firstValueFrom(service.loadWorkcellGroups());
            expect(groups.length).toBe(3); // wc-1, wc-2, and unassigned

            const group1 = groups.find(g => g.workcell?.accession_id === 'wc-1');
            const group2 = groups.find(g => g.workcell?.accession_id === 'wc-2');
            const unassigned = groups.find(g => g.workcell === null);

            expect(group1?.machines.length).toBe(2);
            expect(group2?.machines.length).toBe(1);
            expect(unassigned?.machines.length).toBe(1);

            expect(group1?.machines[0].accession_id).toBe('m1');
            expect(group2?.machines[0].alerts.length).toBe(1);
            expect(group2?.machines[0].alerts[0].severity).toBe('error');
        });

        it('should update workcellGroups signal', async () => {
            await firstValueFrom(service.loadWorkcellGroups());
            const groups = service.workcellGroups();
            expect(groups.length).toBe(3);
        });

        it('should handle machines with workcell_id not in workcells list as unassigned', async () => {
            const machinesWithUnknownWC: Machine[] = [
                ...mockMachines,
                { accession_id: 'm5', name: 'Machine 5', status: MachineStatus.IDLE, workcell_accession_id: 'unknown-wc' }
            ];
            assetServiceMock.getMachines.mockReturnValue(of(machinesWithUnknownWC));

            const groups = await firstValueFrom(service.loadWorkcellGroups());
            const unassigned = groups.find(g => g.workcell === null);
            expect(unassigned?.machines.length).toBe(2); // m4 and m5
        });

        it('should include empty workcells', async () => {
            const emptyWorkcells: Workcell[] = [
                ...mockWorkcells,
                { accession_id: 'wc-3', name: 'Workcell 3', status: 'online' }
            ];
            assetServiceMock.getWorkcells.mockReturnValue(of(emptyWorkcells));

            const groups = await firstValueFrom(service.loadWorkcellGroups());
            const group3 = groups.find(g => g.workcell?.accession_id === 'wc-3');
            expect(group3).toBeDefined();
            expect(group3?.machines.length).toBe(0);
        });
    });

    describe('deriveConnectionState', () => {
        it('should map OFFLINE to disconnected', async () => {
            const groups = await firstValueFrom(service.loadWorkcellGroups());
            const unassigned = groups.find(g => g.workcell === null);
            const m4 = unassigned?.machines.find(m => m.accession_id === 'm4');
            expect(m4?.connectionState).toBe('disconnected');
        });

        it('should map IDLE to connected', async () => {
            const groups = await firstValueFrom(service.loadWorkcellGroups());
            const group1 = groups.find(g => g.workcell?.accession_id === 'wc-1');
            const m1 = group1?.machines.find(m => m.accession_id === 'm1');
            expect(m1?.connectionState).toBe('connected');
        });
    });
});
