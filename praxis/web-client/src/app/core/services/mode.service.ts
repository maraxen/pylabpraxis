import { Injectable, signal, computed } from '@angular/core';
import { ONBOARDING_STORAGE_KEYS } from './onboarding.service';
import { environment } from '../../../environments/environment';

/**
 * Application mode types:
 * - browser: Pure client-side, no backend, LocalStorage persistence
 * - demo: Browser mode + pre-loaded fake assets/protocols
 * - lite: Local Python server with SQLite
 * - production: Full Postgres/Redis/FastAPI/Keycloak stack
 */
export type AppMode = 'browser' | 'lite' | 'production';

/**
 * Helper function to check if running in browser mode.
 * Can be called before Angular DI is available (e.g., in service constructors).
 */
export function isBrowserModeEnv(): boolean {
    const env = environment as { browserMode?: boolean; demo?: boolean };
    return env.browserMode === true || env.demo === true;
}

/**
 * Centralized service for application mode detection and configuration.
 * 
 * Replaces scattered `environment.demo` checks throughout the codebase.
 * All mode-dependent logic should inject this service and use its computed signals.
 */
@Injectable({ providedIn: 'root' })
export class ModeService {
    /**
     * Current application mode, determined from environment configuration.
     */
    readonly mode = signal<AppMode>(this.detectMode());

    /**
     * True if running in browser-only mode.
     * These modes bypass authentication and use client-side storage.
     */
    readonly isBrowserMode = computed(() =>
        this.mode() === 'browser'
    );

    /**
     * True if authentication is required (production or lite modes).
     */
    readonly requiresAuth = computed(() =>
        this.mode() === 'production' || this.mode() === 'lite'
    );

    /**
     * True if a backend server is available.
     */
    readonly hasBackend = computed(() =>
        this.mode() === 'production' || this.mode() === 'lite'
    );

    /**
     * Human-readable mode label for UI display.
     */
    readonly modeLabel = computed(() => {
        switch (this.mode()) {
            case 'browser': return 'Browser';
            case 'lite': return 'Lite';
            case 'production': return 'Production';
        }
    });

    /**
     * Detect application mode from environment configuration.
     */
    private detectMode(): AppMode {
        const env = environment as {
            browserMode?: boolean;
            demo?: boolean;
            production?: boolean;
            lite?: boolean;
        };

        if (env.browserMode || env.demo) {
            return 'browser';
        }
        if (env.lite) {
            return 'lite';
        }
        if (env.production) {
            return 'production';
        }
        // Default to production for safety
        return 'production';
    }
}
