/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ParameterConstraintsModel } from './ParameterConstraintsModel';
import type { UIHint } from './UIHint';
/**
 * Provides comprehensive metadata for a protocol parameter.
 *
 * This includes its name, type information, default value, description,
 * constraints, and UI rendering hints.
 */
export type ParameterMetadataModel = {
    name: string;
    type_hint: string;
    fqn: string;
    is_deck_param?: boolean;
    optional: boolean;
    default_value_repr?: (string | null);
    description?: (string | null);
    constraints?: ParameterConstraintsModel;
    ui_hint?: (UIHint | null);
};

