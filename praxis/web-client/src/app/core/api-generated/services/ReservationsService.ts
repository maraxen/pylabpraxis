/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssetReservationCreate } from '../models/AssetReservationCreate';
import type { ReleaseReservationResponse } from '../models/ReleaseReservationResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ReservationsService {
    /**
     * List Reservations
     * List all asset reservations.
     *
     * Admin endpoint for inspecting current reservation state. By default, only
     * shows active reservations (PENDING, RESERVED, ACTIVE). Set include_released=true
     * to see all reservations including released ones.
     * @param includeReleased Include released reservations in results
     * @param assetKey Filter by specific asset key (e.g., 'asset:my_plate')
     * @returns AssetReservationCreate Successful Response
     * @throws ApiError
     */
    public static listReservationsApiV1SchedulerReservationsGet(
        includeReleased: boolean = false,
        assetKey?: (string | null),
    ): CancelablePromise<AssetReservationCreate> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/scheduler/reservations',
            query: {
                'include_released': includeReleased,
                'asset_key': assetKey,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Release Reservation
     * Release asset reservations by asset key.
     *
     * Admin endpoint for manually clearing stuck reservations. This releases
     * all active reservations for the specified asset key.
     *
     * The asset_key format is typically "type:name", e.g., "asset:my_plate".
     *
     * Use force=true to also release ACTIVE reservations (use with caution as
     * this may interrupt running protocols).
     * @param assetKey
     * @param force Force release even for reservations in ACTIVE state
     * @returns ReleaseReservationResponse Successful Response
     * @throws ApiError
     */
    public static releaseReservationApiV1SchedulerReservationsAssetKeyDelete(
        assetKey: string,
        force: boolean = false,
    ): CancelablePromise<ReleaseReservationResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/scheduler/reservations/{asset_key}',
            path: {
                'asset_key': assetKey,
            },
            query: {
                'force': force,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
