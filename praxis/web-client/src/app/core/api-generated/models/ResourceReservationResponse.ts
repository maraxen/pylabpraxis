/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResourceReservationStatus } from './ResourceReservationStatus';
/**
 * Response model for resource reservations.
 */
export type ResourceReservationResponse = {
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
    resource_type: string;
    resource_name: string;
    resource_identifier: (string | null);
    status: ResourceReservationStatus;
    redis_lock_key: (string | null);
    redis_reservation_id: (string | null);
    required_capabilities_json: (Record<string, any> | null);
    constraint_details_json: (Record<string, any> | null);
    reserved_at: (string | null);
    released_at: (string | null);
    expires_at: (string | null);
    estimated_duration_ms: (number | null);
    status_details: (string | null);
    error_details_json: (Record<string, any> | null);
};

