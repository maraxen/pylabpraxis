/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserResponse } from './UserResponse';
/**
 * Login response model with user data and token.
 */
export type LoginResponse = {
    user: UserResponse;
    access_token: string;
    token_type?: string;
};

