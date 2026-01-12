/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MachineStatusEnum } from './MachineStatusEnum';
/**
 * Schema for updating a Machine (partial update).
 */
export type MachineUpdate = {
    name?: (string | null);
    fqn?: (string | null);
    location?: (string | null);
    plr_state?: (Record<string, any> | null);
    plr_definition?: (Record<string, any> | null);
    properties_json?: (Record<string, any> | null);
    status?: (MachineStatusEnum | null);
    status_details?: (string | null);
    workcell_accession_id?: (string | null);
    resource_counterpart_accession_id?: (string | null);
    has_deck_child?: (boolean | null);
    has_resource_child?: (boolean | null);
    description?: (string | null);
    manufacturer?: (string | null);
    model?: (string | null);
    serial_number?: (string | null);
    installation_date?: null;
    connection_info?: (Record<string, any> | null);
    is_simulation_override?: (boolean | null);
    user_configured_capabilities?: (Record<string, any> | null);
    current_protocol_run_accession_id?: (string | null);
    location_label?: (string | null);
    maintenance_enabled?: (boolean | null);
    maintenance_schedule_json?: (Record<string, any> | null);
    last_maintenance_json?: (Record<string, any> | null);
    resource_def_name?: (string | null);
    resource_properties_json?: (Record<string, any> | null);
    resource_initial_status?: (string | null);
};

