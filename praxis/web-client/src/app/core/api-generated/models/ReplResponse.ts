/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Response from REPL command execution.
 */
export type ReplResponse = {
    device_id: string;
    command: string;
    output: string;
    success: boolean;
    error?: (string | null);
};

