/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ParameterConstraintsModel } from './ParameterConstraintsModel';
/**
 * Model for parameter metadata.
 */
export type ParameterMetadataModel = {
    name: string;
    type_hint: string;
    description?: (string | null);
    default_value?: null;
    constraints?: (ParameterConstraintsModel | null);
};

