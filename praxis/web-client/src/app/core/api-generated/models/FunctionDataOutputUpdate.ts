/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataOutputTypeEnum } from './DataOutputTypeEnum';
/**
 * Schema for updating a FunctionDataOutput (partial update).
 */
export type FunctionDataOutputUpdate = {
    data_type?: (DataOutputTypeEnum | null);
    file_path?: (string | null);
    data_value_json?: (Record<string, any> | null);
    data_quality_score?: (number | null);
    data_key?: (string | null);
    measurement_conditions_json?: (Record<string, any> | null);
    processing_metadata_json?: (Record<string, any> | null);
};

