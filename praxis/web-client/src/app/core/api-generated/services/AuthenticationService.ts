/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LoginRequest } from '../models/LoginRequest';
import type { LoginResponse } from '../models/LoginResponse';
import type { UserResponse } from '../models/UserResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthenticationService {
    /**
     * Login
     * Authenticate user and return access token.
     *
     * Args:
     * credentials: User login credentials (username and password)
     * db: Database session
     *
     * Returns:
     * LoginResponse with user data and JWT token
     *
     * Raises:
     * HTTPException: If authentication fails (401 Unauthorized)
     * @param requestBody
     * @returns LoginResponse Successful Response
     * @throws ApiError
     */
    public static loginApiV1AuthLoginPost(
        requestBody: LoginRequest,
    ): CancelablePromise<LoginResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/login',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Logout
     * Logout endpoint.
     *
     * Note: JWT tokens are stateless, so logout is handled client-side
     * by removing the token from storage. This endpoint exists for
     * API consistency and can be extended to implement token blacklisting
     * if needed in the future.
     *
     * Returns:
     * Success message
     * @returns string Successful Response
     * @throws ApiError
     */
    public static logoutApiV1AuthLogoutPost(): CancelablePromise<Record<string, string>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/logout',
        });
    }
    /**
     * Get Current User Info
     * Get the current authenticated user's information.
     *
     * This is a protected route that requires a valid JWT token.
     *
     * Args:
     * current_user: Current authenticated user (injected by dependency)
     *
     * Returns:
     * UserResponse with current user's data
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    public static getCurrentUserInfoApiV1AuthMeGet(): CancelablePromise<UserResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/auth/me',
        });
    }
}
