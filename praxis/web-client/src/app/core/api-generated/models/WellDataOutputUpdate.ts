/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Schema for updating a WellDataOutput (partial update).
 */
export type WellDataOutputUpdate = {
    well_position?: (string | null);
    measurement_type?: (string | null);
    value?: (number | null);
    unit?: (string | null);
    well_name?: (string | null);
    data_value?: (number | null);
    metadata_json?: (Record<string, any> | null);
};

