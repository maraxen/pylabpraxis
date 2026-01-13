/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Schema for reading a User (API response) - excludes hashed_password.
 */
export type UserRead = {
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
    name?: (string | null);
    /**
     * Arbitrary metadata.
     */
    properties_json?: (Record<string, any> | null);
    /**
     * Unique username for login
     */
    username: string;
    /**
     * User's email address
     */
    email: string;
    /**
     * User's full name
     */
    full_name?: (string | null);
    /**
     * Whether the user account is active
     */
    is_active?: boolean;
    /**
     * Phone number for SMS notifications
     */
    phone_number?: (string | null);
    /**
     * Phone carrier for SMS gateway
     */
    phone_carrier?: (string | null);
};

