import { Injectable, signal, computed, inject } from '@angular/core';
import { LocalStorageAdapter } from './local-storage.adapter';

export const ONBOARDING_STORAGE_KEYS = {
    ONBOARDING_COMPLETED: 'praxis_onboarding_completed',
    DEMO_MODE_ENABLED: 'praxis_demo_mode_enabled',
    TUTORIAL_COMPLETED: 'praxis_tutorial_completed',
    TUTORIAL_STATE: 'praxis_tutorial_state'
} as const;

export interface TutorialState {
    sessionId: number;
    stepId: string;
}

@Injectable({ providedIn: 'root' })
export class OnboardingService {
    private localStorageAdapter = inject(LocalStorageAdapter);

    readonly hasCompletedOnboarding = signal<boolean>(this.checkOnboardingStatus());
    readonly isDemoModeEnabled = signal<boolean>(this.checkDemoModeStatus());

    // We treat "tutorial completed" separately in case they skip onboarding but want to do tutorial later
    readonly hasCompletedTutorial = signal<boolean>(this.checkTutorialStatus());

    readonly shouldShowWelcome = computed(() => !this.hasCompletedOnboarding());

    constructor() { }

    private checkOnboardingStatus(): boolean {
        return !!localStorage.getItem(ONBOARDING_STORAGE_KEYS.ONBOARDING_COMPLETED);
    }

    private checkDemoModeStatus(): boolean {
        return localStorage.getItem(ONBOARDING_STORAGE_KEYS.DEMO_MODE_ENABLED) === 'true';
    }

    private checkTutorialStatus(): boolean {
        return !!localStorage.getItem(ONBOARDING_STORAGE_KEYS.TUTORIAL_COMPLETED);
    }

    markOnboardingComplete(): void {
        localStorage.setItem(ONBOARDING_STORAGE_KEYS.ONBOARDING_COMPLETED, 'true');
        this.hasCompletedOnboarding.set(true);
    }

    markTutorialComplete(): void {
        localStorage.setItem(ONBOARDING_STORAGE_KEYS.TUTORIAL_COMPLETED, 'true');
        this.hasCompletedTutorial.set(true);
    }

    /**
     * Sets the demo mode preference.
     * @param enabled Whether demo mode should be enabled
     * @param reload Whether to reload the page immediately (default: true)
     */
    setDemoMode(enabled: boolean, reload: boolean = true): void {
        localStorage.setItem(ONBOARDING_STORAGE_KEYS.DEMO_MODE_ENABLED, String(enabled));
        this.isDemoModeEnabled.set(enabled);

        if (reload) {
            window.location.reload();
        }
    }

    resetOnboarding(): void {
        localStorage.removeItem(ONBOARDING_STORAGE_KEYS.ONBOARDING_COMPLETED);
        localStorage.removeItem(ONBOARDING_STORAGE_KEYS.TUTORIAL_COMPLETED);
        localStorage.removeItem(ONBOARDING_STORAGE_KEYS.TUTORIAL_STATE);
        this.hasCompletedOnboarding.set(false);
        this.hasCompletedTutorial.set(false);
        window.location.reload();
    }

    // Tutorial Session Tracking
    startTutorialSession(): void {
        const state: TutorialState = {
            sessionId: Date.now(),
            stepId: 'intro' // Default start
        };
        this.saveTutorialState(state);
    }

    saveTutorialStep(stepId: string): void {
        const current = this.getTutorialState();
        if (current) {
            this.saveTutorialState({ ...current, stepId });
        }
    }

    getTutorialState(): TutorialState | null {
        try {
            const raw = localStorage.getItem(ONBOARDING_STORAGE_KEYS.TUTORIAL_STATE);
            return raw ? JSON.parse(raw) : null;
        } catch {
            return null;
        }
    }

    clearTutorialState(): void {
        localStorage.removeItem(ONBOARDING_STORAGE_KEYS.TUTORIAL_STATE);
    }

    private saveTutorialState(state: TutorialState): void {
        localStorage.setItem(ONBOARDING_STORAGE_KEYS.TUTORIAL_STATE, JSON.stringify(state));
    }
}
