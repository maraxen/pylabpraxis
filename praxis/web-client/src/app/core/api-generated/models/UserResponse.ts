/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Represents a user for API responses.
 */
export type UserResponse = {
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
    /**
     * The unique name of the user.
     */
    username: string;
    /**
     * The user's email address.
     */
    email: string;
    /**
     * The user's full name.
     */
    full_name?: (string | null);
    /**
     * Whether the user is active.
     */
    is_active?: boolean;
};

