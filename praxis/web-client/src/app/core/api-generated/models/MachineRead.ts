/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetType } from './AssetType';
import type { MachineCategoryEnum } from './MachineCategoryEnum';
import type { MachineStatusEnum } from './MachineStatusEnum';
/**
 * Schema for reading a Machine (API response).
 */
export type MachineRead = {
    accession_id?: string;
    /**
     * The time the record was created.
     */
    created_at?: string;
    /**
     * The time the record was last updated.
     */
    updated_at?: (string | null);
    name: string;
    properties_json?: (Record<string, any> | null);
    asset_type: AssetType;
    fqn?: (string | null);
    location?: (string | null);
    /**
     * Category of the machine
     */
    machine_category?: MachineCategoryEnum;
    description?: (string | null);
    manufacturer?: (string | null);
    model?: (string | null);
    serial_number?: (string | null);
    /**
     * Physical location label
     */
    location_label?: (string | null);
    installation_date?: (string | null);
    /**
     * Status of the machine
     */
    status?: MachineStatusEnum;
    status_details?: (string | null);
    is_simulation_override?: (boolean | null);
    last_seen_online?: (string | null);
    maintenance_enabled?: boolean;
    /**
     * Connection details (backend, address, etc.)
     */
    connection_info?: (Record<string, any> | null);
    /**
     * User-specified capability overrides
     */
    user_configured_capabilities?: (Record<string, any> | null);
    /**
     * Custom maintenance schedule
     */
    maintenance_schedule_json?: (Record<string, any> | null);
    /**
     * Record of last maintenance
     */
    last_maintenance_json?: (Record<string, any> | null);
    plr_state?: (Record<string, any> | null);
    plr_definition?: (Record<string, any> | null);
};

