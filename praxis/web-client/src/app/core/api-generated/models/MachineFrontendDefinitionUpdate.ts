/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MachineCategoryEnum } from './MachineCategoryEnum';
/**
 * Schema for updating a MachineFrontendDefinition (partial update).
 */
export type MachineFrontendDefinitionUpdate = {
    name?: (string | null);
    fqn?: (string | null);
    description?: (string | null);
    plr_category?: (string | null);
    machine_category?: (MachineCategoryEnum | null);
    capabilities?: (Record<string, any> | null);
    capabilities_config?: (Record<string, any> | null);
    has_deck?: (boolean | null);
    manufacturer?: (string | null);
    model?: (string | null);
};

