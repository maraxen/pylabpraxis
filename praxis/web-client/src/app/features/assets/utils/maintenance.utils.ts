import { Machine } from '../models/asset.models';

export type MaintenanceStatus = 'ok' | 'warning' | 'overdue' | 'disabled';

export function calculateMaintenanceStatus(machine: Machine): MaintenanceStatus {
    if (machine.maintenance_enabled === false) return 'disabled';

    const schedule = machine.maintenance_schedule_json;
    if (!schedule || !schedule.enabled || !schedule.intervals?.length) return 'disabled';

    const nextDue = calculateNextDueDate(machine);
    if (!nextDue) return 'ok';

    const daysUntilDue = Math.ceil((nextDue.getTime() - Date.now()) / (1000 * 60 * 60 * 24));

    if (daysUntilDue < 0) return 'overdue';
    if (daysUntilDue <= 7) return 'warning'; // Warn 1 week in advance
    return 'ok';
}

export function calculateNextDueDate(machine: Machine): Date | null {
    const schedule = machine.maintenance_schedule_json;
    const history = machine.last_maintenance_json || {};

    if (!schedule || !schedule.intervals) return null;

    let earliestNextDue: Date | null = null;

    for (const interval of schedule.intervals) {
        if (!interval.required) continue;

        const lastRecord = history[interval.type];
        const lastDate = lastRecord ? new Date(lastRecord.completed_at) : new Date(machine.created_at || Date.now());

        const nextDate = new Date(lastDate);
        nextDate.setDate(lastDate.getDate() + interval.interval_days);

        if (!earliestNextDue || nextDate < earliestNextDue) {
            earliestNextDue = nextDate;
        }
    }

    return earliestNextDue;
}
