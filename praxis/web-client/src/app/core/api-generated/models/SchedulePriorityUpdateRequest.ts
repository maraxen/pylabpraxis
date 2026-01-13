/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request model for updating a schedule entry's priority.
 *
 * Accepts both `new_priority` (used by API/tests) and `priority` for
 * backward-compatibility with older clients.
 */
export type SchedulePriorityUpdateRequest = {
    new_priority: number;
    reason?: (string | null);
    priority?: (number | null);
};

