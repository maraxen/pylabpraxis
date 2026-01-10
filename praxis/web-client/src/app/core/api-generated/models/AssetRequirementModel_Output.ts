/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetConstraintsModel } from './AssetConstraintsModel';
import type { LocationConstraintsModel } from './LocationConstraintsModel';
/**
 * Describes a single asset required by a protocol.
 *
 * This includes its name, type information, optionality, default value,
 * description, and specific constraints.
 */
export type AssetRequirementModel_Output = {
    accession_id: string;
    name: string;
    fqn: string;
    type_hint_str: string;
    optional?: boolean;
    default_value_repr?: (string | null);
    description?: (string | null);
    constraints?: AssetConstraintsModel;
    location_constraints?: LocationConstraintsModel;
};

