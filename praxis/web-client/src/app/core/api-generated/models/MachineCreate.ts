/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetType } from './AssetType';
import type { MachineCategoryEnum } from './MachineCategoryEnum';
import type { MachineStatusEnum } from './MachineStatusEnum';
/**
 * Schema for creating a Machine.
 */
export type MachineCreate = {
    /**
     * The unique accession ID of the record.
     */
    accession_id?: string;
    /**
     * The time the record was created.
     */
    created_at?: string;
    /**
     * The time the record was last updated.
     */
    updated_at?: (string | null);
    /**
     * Unique, human-readable name for the asset
     */
    name: string;
    /**
     * Arbitrary metadata.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * Type of asset, e.g., machine, resource, etc.
     */
    asset_type?: AssetType;
    /**
     * Fully qualified name (e.g., 'pylabrobot.resources.Plate')
     */
    fqn?: string;
    /**
     * Location of the asset in the lab.
     */
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
    /**
     * Selected simulation backend name (when is_simulated_frontend = True)
     */
    simulation_backend_name?: (string | null);
    resource_def_name?: (string | null);
    resource_properties_json?: (Record<string, any> | null);
    resource_initial_status?: (string | null);
    resource_counterpart_accession_id?: (string | null);
    frontend_definition_accession_id?: (string | null);
    backend_definition_accession_id?: (string | null);
    backend_config?: (Record<string, any> | null);
};

