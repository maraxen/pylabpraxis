/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetReservationStatusEnum } from './AssetReservationStatusEnum';
import type { AssetType } from './AssetType';
/**
 * Schema for creating an AssetReservation.
 */
export type AssetReservationCreate = {
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
     * An optional name for the record.
     */
    name?: (string | null);
    /**
     * Arbitrary metadata.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * When the asset was reserved
     */
    reserved_at?: (string | null);
    /**
     * When the asset was released
     */
    released_at?: (string | null);
    expires_at?: (string | null);
    /**
     * Whether the reservation is currently active
     */
    is_active?: boolean;
    /**
     * Status of the reservation
     */
    status?: AssetReservationStatusEnum;
    /**
     * Type of the reserved asset
     */
    asset_type?: AssetType;
    asset_name: string;
    redis_lock_key: string;
    redis_lock_value?: (string | null);
    lock_timeout_seconds?: number;
    required_capabilities_json?: (Record<string, any> | null);
    estimated_usage_duration_ms?: (number | null);
    asset_accession_id: string;
    schedule_entry_accession_id: string;
    protocol_run_accession_id: string;
};

