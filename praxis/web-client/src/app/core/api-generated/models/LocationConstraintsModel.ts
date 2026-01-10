/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Defines constraints for the location of an asset in a protocol.
 *
 * This includes required locations, optional locations, and any specific
 * location-related constraints.
 */
export type LocationConstraintsModel = {
    location_requirements?: Array<string>;
    on_resource_type?: string;
    stack?: boolean;
    directly_position?: boolean;
    position_condition?: Array<string>;
};

