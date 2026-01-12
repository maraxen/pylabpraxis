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
    accession_id: string;
    /**
     * The time the record was created.
     */
    created_at?: string;
    /**
     * The time the record was last updated.
     */
    updated_at?: (string | null);
    /**
     * An optional name for the record.
     */
    name: string;
    /**
     * Type of asset, e.g., machine, resource, etc.
     */
    asset_type?: AssetType;
    /**
     * Fully qualified name of the asset's class, if applicable.
     */
    fqn?: string;
    /**
     * Location of the asset in the lab.
     */
    location?: (string | null);
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
    status?: MachineStatusEnum;
    status_details?: (string | null);
    is_simulation_override?: (boolean | null);
    last_seen_online?: (string | null);
    maintenance_enabled?: boolean;
    connection_info?: (Record<string, any> | null);
    user_configured_capabilities?: (Record<string, any> | null);
};

