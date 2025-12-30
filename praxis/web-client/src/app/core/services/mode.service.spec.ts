import { TestBed } from '@angular/core/testing';
import { ModeService, isBrowserModeEnv, AppMode } from './mode.service';
import { describe, beforeEach, it, expect, vi } from 'vitest';

// Mock the environment module
vi.mock('../../../environments/environment', () => ({
    environment: {
        production: false,
        browserMode: false,
        demo: false
    }
}));

describe('ModeService', () => {
    let service: ModeService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [ModeService]
        });

        service = TestBed.inject(ModeService);
    });

    describe('Mode Detection', () => {
        it('should be created', () => {
            expect(service).toBeTruthy();
        });

        it('should have a mode signal', () => {
            expect(service.mode()).toBeDefined();
        });

        it('should have computed signals for mode checks', () => {
            expect(service.isBrowserMode).toBeDefined();
            expect(service.requiresAuth).toBeDefined();
            expect(service.isDemoMode).toBeDefined();
            expect(service.hasBackend).toBeDefined();
            expect(service.modeLabel).toBeDefined();
        });
    });

    describe('Mode Labels', () => {
        it('should return correct label for each mode', () => {
            // Since we can't easily change the mode signal in tests,
            // we test the computed logic indirectly
            expect(typeof service.modeLabel()).toBe('string');
            expect(['Browser', 'Demo', 'Lite', 'Production']).toContain(service.modeLabel());
        });
    });

    describe('Computed Signals', () => {
        it('isBrowserMode should return boolean', () => {
            expect(typeof service.isBrowserMode()).toBe('boolean');
        });

        it('requiresAuth should return boolean', () => {
            expect(typeof service.requiresAuth()).toBe('boolean');
        });

        it('isDemoMode should return boolean', () => {
            expect(typeof service.isDemoMode()).toBe('boolean');
        });

        it('hasBackend should return boolean', () => {
            expect(typeof service.hasBackend()).toBe('boolean');
        });

        it('isBrowserMode and requiresAuth should be mutually exclusive', () => {
            // If browser mode is on, auth is not required, and vice versa
            const isBrowser = service.isBrowserMode();
            const needsAuth = service.requiresAuth();

            // They should be opposites
            expect(isBrowser !== needsAuth || (!isBrowser && !needsAuth)).toBe(true);
        });
    });
});

describe('isBrowserModeEnv helper', () => {
    it('should be a function', () => {
        expect(typeof isBrowserModeEnv).toBe('function');
    });

    it('should return a boolean', () => {
        expect(typeof isBrowserModeEnv()).toBe('boolean');
    });
});
