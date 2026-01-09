import { Injectable, signal, computed, inject } from '@angular/core';
import { LocalStorageAdapter } from './local-storage.adapter';
import { BrowserService } from './browser.service';

export const ONBOARDING_STORAGE_KEYS = {
    ONBOARDING_COMPLETED: 'praxis_onboarding_completed',
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
    private browserService = inject(BrowserService);

    readonly hasCompletedOnboarding = signal<boolean>(this.checkOnboardingStatus());

    // We treat "tutorial completed" separately in case they skip onboarding but want to do tutorial later
    readonly hasCompletedTutorial = signal<boolean>(this.checkTutorialStatus());

    readonly shouldShowWelcome = computed(() => !this.hasCompletedOnboarding());

    constructor() { }

    private checkOnboardingStatus(): boolean {
        return !!localStorage.getItem(ONBOARDING_STORAGE_KEYS.ONBOARDING_COMPLETED);
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


    resetOnboarding(): void {
        localStorage.removeItem(ONBOARDING_STORAGE_KEYS.ONBOARDING_COMPLETED);
        localStorage.removeItem(ONBOARDING_STORAGE_KEYS.TUTORIAL_COMPLETED);
        localStorage.removeItem(ONBOARDING_STORAGE_KEYS.TUTORIAL_STATE);
        this.hasCompletedOnboarding.set(false);
        this.hasCompletedTutorial.set(false);
        this.browserService.reload();
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
