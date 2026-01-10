/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Defines constraints for an asset required by a protocol.
 */
export type AssetConstraintsModel = {
    required_methods?: Array<string>;
    required_attributes?: Array<string>;
    required_method_signatures?: Record<string, string>;
    required_method_args?: Record<string, Array<string>>;
    min_volume_ul?: (number | null);
};

