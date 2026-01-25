import { Injector, Type } from '@angular/core';

/**
 * GlobalInjector Utility
 * 
 * Provides access to the Angular Injector from non-injection contexts
 * (e.g. generated API clients, plain functions, etc.).
 * 
 * This must be initialized during application bootstrap.
 */
export class GlobalInjector {
    private static injector: Injector | null = null;

    /**
     * Set the global injector instance.
     * Should be called once during app bootstrap.
     */
    static set(injector: Injector): void {
        this.injector = injector;
    }

    /**
     * Get the global injector instance.
     */
    static getInjector(): Injector {
        if (!this.injector) {
            throw new Error('GlobalInjector not initialized. Call GlobalInjector.set(injector) first.');
        }
        return this.injector;
    }

    /**
     * Look up a dependency from the global injector.
     */
    static get<T>(token: Type<T>): T {
        return this.getInjector().get(token);
    }
}
