/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DeckResponse } from './DeckResponse';
import type { MachineResponse } from './MachineResponse';
import type { ResourceResponse } from './ResourceResponse';
import type { WorkcellStatusEnum } from './WorkcellStatusEnum';
/**
 * Represents a workcell for API responses.
 *
 * This model extends `WorkcellBase` by adding system-generated identifiers
 * and timestamps for creation and last update, suitable for client-facing
 * responses.
 */
export type WorkcellResponse = {
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
    last_updated?: (string | null);
    /**
     * The unique name of the workcell.
     */
    name: string;
    /**
     * Arbitrary metadata associated with the record.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * The fully qualified name for the workcell. Defaults to name if not provided.
     */
    fqn?: (string | null);
    /**
     * A description of the workcell.
     */
    description?: (string | null);
    /**
     * The physical location of the workcell (e.g., 'Lab 2, Room 301').
     */
    physical_location?: (string | null);
    /**
     * The current status of the workcell.
     */
    status?: WorkcellStatusEnum;
    /**
     * The latest state of the workcell as a JSON object.
     */
    latest_state_json?: (Record<string, any> | null);
    /**
     * The timestamp of the last state update.
     */
    last_state_update_time?: (string | null);
    /**
     * List of machines associated with this workcell.
     */
    machines?: Array<MachineResponse>;
    /**
     * List of resources associated with this workcell.
     */
    resources?: (Array<ResourceResponse> | null);
    /**
     * List of deck configurations associated with this workcell.
     */
    decks?: (Array<DeckResponse> | null);
};

