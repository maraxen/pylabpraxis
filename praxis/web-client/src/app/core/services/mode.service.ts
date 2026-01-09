import { Injectable, signal, computed } from '@angular/core';
import { ONBOARDING_STORAGE_KEYS } from './onboarding.service';
import { environment } from '../../../environments/environment';

/**
 * Application mode types:
 * - browser: Pure client-side, no backend, LocalStorage persistence, pre-loaded assets
 * - lite: Local Python server with SQLite
 * - production: Full Postgres/Redis/FastAPI/Keycloak stack
 */
export type AppMode = 'browser' | 'lite' | 'production';

const MODE_OVERRIDE_KEY = 'praxis_mode_override';

/**
 * Helper function to check if running in browser mode.
 * Can be called before Angular DI is available (e.g., in service constructors).
 */
export function isBrowserModeEnv(): boolean {
    const env = environment as { browserMode?: boolean };
    return env.browserMode === true;
}

/**
 * Centralized service for application mode detection and configuration.
 * 
 * Replaces scattered `environment.browserMode` checks throughout the codebase.
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
        const urlMode = this.getUrlModeOverride();
        if (urlMode) {
            this.persistOverride(urlMode);
            return urlMode;
        }

        const storedMode = this.getStoredModeOverride();
        if (storedMode) {
            return storedMode;
        }

        const env = environment as {
            browserMode?: boolean;
            production?: boolean;
            lite?: boolean;
        };

        if (env.browserMode) {
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

    /**
     * Read mode override from URL query string (?mode=browser|lite|production)
     */
    private getUrlModeOverride(): AppMode | null {
        if (typeof window === 'undefined') return null;
        const modeParam = new URLSearchParams(window.location.search).get('mode');
        if (modeParam === 'browser' || modeParam === 'lite' || modeParam === 'production') {
            return modeParam;
        }
        return null;
    }

    /**
     * Read persisted override so refreshes keep the same mode.
     */
    private getStoredModeOverride(): AppMode | null {
        try {
            const stored = localStorage.getItem(MODE_OVERRIDE_KEY);
            if (stored === 'browser' || stored === 'lite' || stored === 'production') {
                return stored;
            }
        } catch {
            // Ignore storage failures in restricted environments
        }
        return null;
    }

    private persistOverride(mode: AppMode) {
        try {
            localStorage.setItem(MODE_OVERRIDE_KEY, mode);
        } catch {
            // Ignore storage failures in restricted environments
        }
    }
}
