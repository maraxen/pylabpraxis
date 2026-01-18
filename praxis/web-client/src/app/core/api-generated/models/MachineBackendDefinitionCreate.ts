/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BackendTypeEnum } from './BackendTypeEnum';
/**
 * Schema for creating a MachineBackendDefinition.
 */
export type MachineBackendDefinitionCreate = {
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
     * Fully qualified name
     */
    fqn: string;
    /**
     * Description of the backend
     */
    description?: (string | null);
    /**
     * Type of backend (hardware, simulator, etc.)
     */
    backend_type?: BackendTypeEnum;
    /**
     * JSON schema for connection parameters
     */
    connection_config?: (Record<string, any> | null);
    manufacturer?: (string | null);
    model?: (string | null);
    is_deprecated?: boolean;
    frontend_definition_accession_id: string;
};

