/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Configuration for how positions are calculated/managed for this deck type.
 *
 * A general configuration for methods that follow the pattern:
 * `deck.method_name(position_arg)` -> Coordinate
 */
export type PositioningConfig = {
    /**
     * Name of the PyLabRobot deck method to call (e.g., 'rail_to_location','slot_to_location').
     */
    method_name: string;
    /**
     * Name of the argument for the position in the method (e.g., 'rail', 'slot').
     */
    arg_name: string;
    /**
     * Expected type of the position argument ('str' or 'int').
     */
    arg_type?: 'str' | 'int';
    /**
     * Additional parameters for the positioning method.
     */
    params?: (Record<string, any> | null);
};

