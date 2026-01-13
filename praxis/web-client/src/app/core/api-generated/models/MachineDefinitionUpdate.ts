/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MachineCategoryEnum } from './MachineCategoryEnum';
/**
 * Schema for updating a MachineDefinition (partial update).
 */
export type MachineDefinitionUpdate = {
    name?: (string | null);
    fqn?: (string | null);
    description?: (string | null);
    plr_category?: (string | null);
    machine_category?: (MachineCategoryEnum | null);
    material?: (string | null);
    manufacturer?: (string | null);
    model?: (string | null);
    size_x_mm?: (number | null);
    size_y_mm?: (number | null);
    size_z_mm?: (number | null);
    has_deck?: (boolean | null);
    frontend_fqn?: (string | null);
    nominal_volume_ul?: (number | null);
    plr_definition_details_json?: (Record<string, any> | null);
    rotation_json?: (Record<string, any> | null);
    setup_method_json?: (Record<string, any> | null);
    capabilities?: (Record<string, any> | null);
    compatible_backends?: (Record<string, any> | null);
    capabilities_config?: (Record<string, any> | null);
    connection_config?: (Record<string, any> | null);
};

