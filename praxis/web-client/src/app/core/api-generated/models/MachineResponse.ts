/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetType } from './AssetType';
import type { MachineStatusEnum } from './MachineStatusEnum';
export type MachineResponse = {
    accession_id?: string;
    /**
     * The time the record was created.
     */
    created_at?: string;
    /**
     * The time the record was last updated.
     */
    last_updated?: (string | null);
    /**
     * An optional name for the record.
     */
    name?: string;
    /**
     * Arbitrary metadata associated with the record.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * The type of the asset.
     */
    asset_type: (AssetType | null);
    /**
     * Fully qualified name of the asset's class, if applicable.
     */
    fqn?: (string | null);
    /**
     * The location of the asset.
     */
    location?: (string | null);
    status?: (MachineStatusEnum | null);
    status_details?: (string | null);
    workcell_id?: (string | null);
    resource_counterpart_accession_id?: (string | null);
    /**
     * Indicates if this machine has a deck resource as a child.
     */
    has_deck_child?: boolean;
    /**
     * Indicates if this machine has a resource child.
     */
    has_resource_child?: boolean;
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
    /**
     * A dictionary for additional state information about the asset.
     */
    plr_state?: (Record<string, any> | null);
    /**
     * A dictionary for the PyLabRobot definition of the asset.
     */
    plr_definition?: (Record<string, any> | null);
};

