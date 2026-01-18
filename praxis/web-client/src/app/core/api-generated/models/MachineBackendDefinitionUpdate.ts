/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BackendTypeEnum } from './BackendTypeEnum';
/**
 * Schema for updating a MachineBackendDefinition (partial update).
 */
export type MachineBackendDefinitionUpdate = {
    name?: (string | null);
    fqn?: (string | null);
    description?: (string | null);
    backend_type?: (BackendTypeEnum | null);
    connection_config?: (Record<string, any> | null);
    manufacturer?: (string | null);
    model?: (string | null);
    is_deprecated?: (boolean | null);
    frontend_definition_accession_id?: (string | null);
};

