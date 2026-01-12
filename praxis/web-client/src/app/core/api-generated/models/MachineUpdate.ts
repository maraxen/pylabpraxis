/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MachineCategoryEnum } from './MachineCategoryEnum';
import type { MachineStatusEnum } from './MachineStatusEnum';
/**
 * Schema for updating a Machine (partial update).
 */
export type MachineUpdate = {
    name?: (string | null);
    fqn?: (string | null);
    location?: (string | null);
    machine_category?: (MachineCategoryEnum | null);
    description?: (string | null);
    manufacturer?: (string | null);
    model?: (string | null);
    serial_number?: (string | null);
    location_label?: (string | null);
    installation_date?: (string | null);
    status?: (MachineStatusEnum | null);
    status_details?: (string | null);
    is_simulation_override?: (boolean | null);
    connection_info?: (Record<string, any> | null);
    user_configured_capabilities?: (Record<string, any> | null);
    maintenance_enabled?: (boolean | null);
};

