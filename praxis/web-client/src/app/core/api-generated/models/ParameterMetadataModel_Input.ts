/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ItemizedSpecModel } from './ItemizedSpecModel';
import type { ParameterConstraintsModel } from './ParameterConstraintsModel';
import type { UIHint } from './UIHint';
/**
 * Provides comprehensive metadata for a protocol parameter.
 *
 * This includes its name, type information, default value, description,
 * constraints, and UI rendering hints.
 */
export type ParameterMetadataModel_Input = {
    accession_id?: null;
    name: string;
    type_hint: string;
    fqn: string;
    is_deck_param?: boolean;
    optional: boolean;
    default_value_repr?: (string | null);
    description?: (string | null);
    field_type?: (string | null);
    is_itemized?: boolean;
    constraints_json?: ParameterConstraintsModel;
    ui_hint_json?: (UIHint | null);
    itemized_spec_json?: (ItemizedSpecModel | null);
    linked_to?: (string | null);
};

