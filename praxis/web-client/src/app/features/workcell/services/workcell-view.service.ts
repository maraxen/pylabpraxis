import { Injectable, inject, signal } from '@angular/core';
import { forkJoin, Observable, map } from 'rxjs';
import { AssetService } from '../../assets/services/asset.service';
import { Machine, Workcell, MachineStatus } from '../../assets/models/asset.models';
import { WorkcellGroup, MachineWithRuntime, MachineAlert } from '../models/workcell-view.models';

@Injectable({
    providedIn: 'root'
})
export class WorkcellViewService {
    private assetService = inject(AssetService);

    // Signal-based state
    workcellGroups = signal<WorkcellGroup[]>([]);
    selectedMachine = signal<MachineWithRuntime | null>(null);

    /**
     * Load all machines grouped by workcell
     */
    loadWorkcellGroups(): Observable<WorkcellGroup[]> {
        return forkJoin({
            machines: this.assetService.getMachines(),
            workcells: this.assetService.getWorkcells()
        }).pipe(
            map(({ machines, workcells }) => {
                const groups = this.groupByWorkcell(machines, workcells);
                this.workcellGroups.set(groups);
                return groups;
            })
        );
    }

    /**
     * Group machines by their assigned workcell
     */
    private groupByWorkcell(machines: Machine[], workcells: Workcell[]): WorkcellGroup[] {
        const groups: WorkcellGroup[] = [];
        const workcellMap = new Map<string, MachineWithRuntime[]>();

        // Initialize map with empty lists for each workcell
        workcells.forEach(wc => workcellMap.set(wc.accession_id, []));

        // "Unassigned" group (accession_id: 'unassigned')
        const unassignedMachines: MachineWithRuntime[] = [];

        machines.forEach(m => {
            const machineWithRuntime = this.mapToMachineWithRuntime(m);
            if (m.workcell_accession_id && workcellMap.has(m.workcell_accession_id)) {
                workcellMap.get(m.workcell_accession_id)!.push(machineWithRuntime);
            } else {
                unassignedMachines.push(machineWithRuntime);
            }
        });

        // Add groups for workcells that have machines or just exist
        workcells.forEach(wc => {
            groups.push({
                workcell: wc,
                machines: workcellMap.get(wc.accession_id) || [],
                isExpanded: true
            });
        });

        // Add unassigned group if it contains any machines
        if (unassignedMachines.length > 0) {
            groups.push({
                workcell: null, // "Unassigned"
                machines: unassignedMachines,
                isExpanded: true
            });
        }

        return groups;
    }

    /**
     * Map raw machine data to MachineWithRuntime
     */
    private mapToMachineWithRuntime(machine: Machine): MachineWithRuntime {
        return {
            ...machine,
            connectionState: this.deriveConnectionState(machine.status),
            stateSource: machine.is_simulation_override ? 'simulated' : 'live',
            alerts: this.computeAlerts(machine),
            lastStateUpdate: machine.updated_at ? new Date(machine.updated_at) : undefined
        };
    }

    /**
     * Derive connection state from machine status
     */
    private deriveConnectionState(status: MachineStatus): 'connected' | 'disconnected' | 'connecting' {
        switch (status) {
            case MachineStatus.OFFLINE:
            case MachineStatus.UNKNOWN:
                return 'disconnected';
            default:
                return 'connected';
        }
    }

    /**
     * Compute alerts based on machine state
     */
    private computeAlerts(machine: Machine): MachineAlert[] {
        const alerts: MachineAlert[] = [];

        if (machine.status === MachineStatus.ERROR) {
            alerts.push({
                severity: 'error',
                message: machine.status_details || 'Machine is in error state'
            });
        }

        // Basic logic for simulated maintenance alert
        if (machine.status === MachineStatus.MAINTENANCE) {
            alerts.push({
                severity: 'warning',
                message: 'Scheduled maintenance required'
            });
        }

        return alerts;
    }
}
