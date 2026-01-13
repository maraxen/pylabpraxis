/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkcellStatusEnum } from './WorkcellStatusEnum';
/**
 * Schema for reading a Workcell (API response).
 */
export type WorkcellRead = {
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
     * An optional name for the record.
     */
    name?: (string | null);
    /**
     * Arbitrary metadata.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * Fully qualified name
     */
    fqn?: (string | null);
    /**
     * Description of the workcell's purpose
     */
    description?: (string | null);
    /**
     * Physical location (e.g., 'Lab 2, Room 301')
     */
    physical_location?: (string | null);
    /**
     * Current status of the workcell
     */
    status?: WorkcellStatusEnum;
    /**
     * Timestamp of last state update
     */
    last_state_update_time?: (string | null);
    /**
     * Latest state of the workcell
     */
    latest_state_json?: (Record<string, any> | null);
    machines?: Array<any>;
    decks?: Array<any>;
    resources?: Array<any>;
};

