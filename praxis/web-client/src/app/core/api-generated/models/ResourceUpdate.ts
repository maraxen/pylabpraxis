/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResourceStatusEnum } from './ResourceStatusEnum';
/**
 * Schema for updating a Resource (partial update).
 */
export type ResourceUpdate = {
    name?: (string | null);
    fqn?: (string | null);
    location?: (string | null);
    status?: (ResourceStatusEnum | null);
    status_details?: (string | null);
    location_label?: (string | null);
    current_deck_position_name?: (string | null);
    resource_definition_accession_id?: (string | null);
};

