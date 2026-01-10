/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request body for starting a protocol run.
 */
export type StartRunRequest = {
    /**
     * Accession ID of the protocol definition
     */
    protocol_definition_accession_id: string;
    /**
     * Name for the run
     */
    name?: (string | null);
    /**
     * Input parameters for the protocol
     */
    parameters?: (Record<string, any> | null);
    /**
     * If True, run in simulation mode
     */
    simulation_mode?: boolean;
};

