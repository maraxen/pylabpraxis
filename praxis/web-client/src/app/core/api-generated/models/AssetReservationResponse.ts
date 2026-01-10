/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResourceReservationStatus } from './ResourceReservationStatus';
/**
 * Response model for asset reservations (from AssetReservationOrm).
 */
export type AssetReservationResponse = {
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
     * An optional name for the record.
     */
    name?: string;
    /**
     * Arbitrary metadata associated with the record.
     */
    properties_json?: (Record<string, any> | null);
    protocol_run_accession_id: string;
    schedule_entry_accession_id: string;
    asset_type: string;
    asset_name: string;
    asset_accession_id?: (string | null);
    status: ResourceReservationStatus;
    redis_lock_key: string;
    reserved_at?: (string | null);
    released_at?: (string | null);
    expires_at?: (string | null);
    required_capabilities_json?: (Record<string, any> | null);
    estimated_usage_duration_ms?: (number | null);
};

