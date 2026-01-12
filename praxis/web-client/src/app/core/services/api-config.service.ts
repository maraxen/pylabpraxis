import { Injectable } from '@angular/core';
import { OpenAPI } from '../api-generated/core/OpenAPI';

@Injectable({
    providedIn: 'root'
})
export class ApiConfigService {
    /**
     * Initialize the OpenAPI configuration.
     * This should be called early in the app lifecycle (e.g., in AppModule constructor or via APP_INITIALIZER).
     */
    initialize(): void {
        // Strip /v1 if present in BASE as generated client often appends it or uses full paths
        // Actually, looking at generated services, they use /api/v1 prefix in urls.
        // OpenAPI.BASE in the generated core is prepended to the url in request.ts.

        // Environment apiUrl is '/api/v1'
        // Generated service url is '/api/v1/resources/'
        // If OpenAPI.BASE is '', it works. If we want to set a host, we set it here.

        OpenAPI.BASE = window.location.origin;

        console.debug('[API-CONFIG] Initialized OpenAPI.BASE:', OpenAPI.BASE);
    }

    setToken(token: string | undefined): void {
        OpenAPI.TOKEN = token;
    }
}
