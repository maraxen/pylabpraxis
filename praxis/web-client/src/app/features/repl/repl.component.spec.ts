import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReplComponent } from './repl.component';
import { ModeService } from '../../core/services/mode.service';
import { PythonRuntimeService } from '../../core/services/python-runtime.service';
import { BackendReplService } from '../../core/services/backend-repl.service';
import { AppStore } from '../../core/store/app.store';
import { MatSnackBar } from '@angular/material/snack-bar';
import { provideNoopAnimations } from '@angular/platform-browser/animations';
import { BehaviorSubject, of, Subject } from 'rxjs';
import { signal } from '@angular/core';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('ReplComponent', () => {
    let component: ReplComponent;
    let fixture: ComponentFixture<ReplComponent>;

    // Mocks
    let mockModeService: any;
    let mockPythonRuntime: any;
    let mockBackendRepl: any;
    let mockStore: any;
    let mockSnackBar: any;

    beforeEach(async () => {
        mockModeService = {
            isBrowserMode: vi.fn().mockReturnValue(false),
            modeLabel: signal('Backend'),
        };

        mockPythonRuntime = {
            connect: vi.fn().mockReturnValue(of(void 0)),
            disconnect: vi.fn(),
            execute: vi.fn(),
        };

        mockBackendRepl = {
            connect: vi.fn().mockReturnValue(of(void 0)), // Ensure connect returns Observable
            disconnect: vi.fn(),
            execute: vi.fn().mockReturnValue(of({ type: 'result', content: 'done' })),
            variables$: new BehaviorSubject([]),
            saveSession: vi.fn().mockReturnValue(of({ filename: 'test.py' })),
            restart: vi.fn().mockReturnValue(of(void 0)),
        };

        mockStore = {
            theme: signal('light'),
        };

        mockSnackBar = {
            open: vi.fn(),
        };

        await TestBed.configureTestingModule({
            imports: [ReplComponent],
            providers: [
                provideNoopAnimations(),
                { provide: ModeService, useValue: mockModeService },
                { provide: PythonRuntimeService, useValue: mockPythonRuntime },
                { provide: BackendReplService, useValue: mockBackendRepl },
                { provide: AppStore, useValue: mockStore },
                { provide: MatSnackBar, useValue: mockSnackBar },
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(ReplComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should connect to runtime on init', () => {
        expect(mockBackendRepl.connect).toHaveBeenCalled();
    });

    it('should execute code', () => {
        // Access private/protected methods via type assertion or just call public method handling execution
        // ReplComponent execution is triggered by Enter key in terminal or can be tested via executeCode method if public 
        // or by simulating key events.
        // Making executeCode public for testing or using (component as any)

        (component as any).inputBuffer = 'print("hello")';
        (component as any).executeCode();

        expect(mockBackendRepl.execute).toHaveBeenCalledWith('print("hello")');
        expect(component.history[0]).toBe('print("hello")');
    });

    it('should handle variables update', () => {
        const vars = [{ name: 'x', type: 'int', value: '1' }];
        mockBackendRepl.variables$.next(vars);
        fixture.detectChanges();

        expect(component.variables).toEqual(vars);
        // UI check
        const drawer = fixture.nativeElement.querySelector('.variables-drawer');
        expect(drawer.textContent).toContain('x');
        expect(drawer.textContent).toContain('1');
    });

    it('should call saveSession', () => {
        component.history = ['x=1'];
        fixture.detectChanges(); // update button state

        component.saveSession();
        expect(mockBackendRepl.saveSession).toHaveBeenCalledWith(['x=1']);
        expect(mockSnackBar.open).toHaveBeenCalled();
    });

    it('should call restart', () => {
        component.restartKernel();
        expect(mockBackendRepl.restart).toHaveBeenCalled();
    });
});
