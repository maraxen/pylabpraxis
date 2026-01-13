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
    fqn?: (string | null);
    description?: (string | null);
    optional?: boolean;
    default_value_repr?: null;
    default_value?: null;
    constraints?: (ParameterConstraintsModel | null);
    ui_hint?: (Record<string, any> | null);
    linked_to?: (string | null);
    is_deck_param?: boolean;
};

