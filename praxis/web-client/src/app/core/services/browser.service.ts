import { Injectable, InjectionToken, inject } from '@angular/core';

/**
 * Injection token for the browser's window object.
 */
export const WINDOW = new InjectionToken<Window>('WINDOW', {
    factory: () => window
});

/**
 * Service to abstract browser-specific operations like window.location.
 * This improves testability by allowing these operations to be mocked.
 */
@Injectable({ providedIn: 'root' })
export class BrowserService {
    private window = inject(WINDOW);

    /**
     * Get the native window object.
     */
    get nativeWindow(): Window {
        return this.window;
    }

    /**
     * Get the location object.
     */
    get location(): Location {
        return this.window.location;
    }

    /**
     * Reload the current page.
     */
    reload(): void {
        this.window.location.reload();
    }
}
