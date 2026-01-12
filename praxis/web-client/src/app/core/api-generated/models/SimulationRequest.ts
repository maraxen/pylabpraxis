/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request body for protocol simulation.
 *
 * This endpoint serves as a backend fallback for browser-mode simulation
 * when the browser can't execute the graph replay directly.
 */
export type SimulationRequest = {
    /**
     * Pre-extracted computation graph. If not provided, will use the graph from the protocol definition.
     */
    computation_graph?: (Record<string, any> | null);
};

