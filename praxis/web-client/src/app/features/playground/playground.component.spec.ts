
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { PlaygroundComponent } from './playground.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { AppStore } from '@core/store/app.store';
import { ModeService } from '@core/services/mode.service';
import { AssetService } from '@features/assets/services/asset.service';
import { SerialManagerService } from '@core/services/serial-manager.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { signal, WritableSignal } from '@angular/core'; // Import signal
import { of } from 'rxjs';

// Mock BroadcastChannel
class MockBroadcastChannel {
    name: string;
    onmessage: ((event: MessageEvent) => void) | null = null;
    closed = false;

    constructor(name: string) {
        this.name = name;
        // Store reference to this instance for testing
        (globalThis as any).mockChannels = (globalThis as any).mockChannels || {};
        (globalThis as any).mockChannels[name] = this;
    }

    postMessage(message: any) {
        // No-op for now unless we need to simulate self-messages
    }

    close() {
        this.closed = true;
    }
}

describe('PlaygroundComponent', () => {
    let component: PlaygroundComponent;
    let fixture: ComponentFixture<PlaygroundComponent>;

    // Signals for mocks
    let themeSignal: WritableSignal<string>; // Use WritableSignal
    let modeLabelSignal: WritableSignal<string>; // Use WritableSignal

    beforeEach(async () => {
        // Initialize signals here
        themeSignal = signal('light');
        modeLabelSignal = signal('Test Mode');

        (globalThis as any).BroadcastChannel = MockBroadcastChannel;
        (globalThis as any).mockChannels = {};

        await TestBed.configureTestingModule({
            imports: [PlaygroundComponent, NoopAnimationsModule],
            providers: [
                {
                    provide: AppStore,
                    useValue: { theme: themeSignal } // Pass the signal directly
                },
                {
                    provide: ModeService,
                    useValue: { modeLabel: modeLabelSignal } // Pass the signal directly
                },
                {
                    provide: AssetService,
                    useValue: {
                        getMachines: () => of([]),
                        getResources: () => of([])
                    }
                },
                { provide: SerialManagerService, useValue: {} },
                { provide: MatSnackBar, useValue: { open: vi.fn() } }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(PlaygroundComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    afterEach(() => {
        delete (globalThis as any).BroadcastChannel;
        delete (globalThis as any).mockChannels;
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should set up ready listener on init', () => {
        const channel = (globalThis as any).mockChannels['praxis_repl'];
        expect(channel).toBeDefined();
        expect(channel.onmessage).toBeDefined();
    });

    it('should handle ready signal', async () => {
        expect(component.isLoading).toBe(true);

        const channel = (globalThis as any).mockChannels['praxis_repl'];
        channel.onmessage!({ data: { type: 'praxis:ready' } } as MessageEvent);

        // Ready signal processing is direct, but let's be safe
        expect(component.isLoading).toBe(false);
    });

    it('should reset state on reload', async () => {
        // First Simulate ready
        const channel = (globalThis as any).mockChannels['praxis_repl'];
        channel.onmessage!({ data: { type: 'praxis:ready' } } as MessageEvent);
        expect(component.isLoading).toBe(false);

        // Now reload
        component.reloadNotebook();
        expect(component.isLoading).toBe(true);
        expect(component.jupyterliteUrl).toBeUndefined();

        // Wait for timeout in reloadNotebook (100ms)
        await new Promise(resolve => setTimeout(resolve, 150));

        // Check if URL is rebuilt
        expect(component.jupyterliteUrl).toBeDefined();
    });
});
