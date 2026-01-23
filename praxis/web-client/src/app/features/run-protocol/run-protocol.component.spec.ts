import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RunProtocolComponent } from './run-protocol.component';
import { ProtocolService } from '@features/protocols/services/protocol.service';
import { ExecutionService } from './services/execution.service';
import { DeckGeneratorService } from './services/deck-generator.service';
import { WizardStateService } from './services/wizard-state.service';
import { ModeService } from '@core/services/mode.service';
import { SqliteService } from '@core/services/sqlite'; // Import SqliteService
import { AppStore } from '@core/store/app.store';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { signal } from '@angular/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { RouterTestingModule } from '@angular/router/testing';

describe('RunProtocolComponent', () => {
    let component: RunProtocolComponent;
    let fixture: ComponentFixture<RunProtocolComponent>;
    let mockStore: any;

    beforeEach(async () => {
        mockStore = {
            simulationMode: signal(false), // Default to physical
            setSimulationMode: vi.fn()
        };

        const mockProtocolService = {
            getProtocols: () => of([])
        };

        const mockExecutionService = {
            getCompatibility: () => of([]),
            startRun: () => of({}),
            isRunning: signal(false)
        };

        const mockDeckGenerator = {
            generateDeckForProtocol: () => null
        };

        const mockWizardState = {
            getAssetMap: () => ({})
        };

        const mockModeService = {
            isBrowserMode: () => false
        };

        const mockSqliteService = {
            initDb: vi.fn(),
            // Add other methods as needed
        };

        await TestBed.configureTestingModule({
            imports: [
                RunProtocolComponent,
                NoopAnimationsModule,
                HttpClientTestingModule,
                RouterTestingModule
            ],
            providers: [
                { provide: ProtocolService, useValue: mockProtocolService },
                { provide: ExecutionService, useValue: mockExecutionService },
                { provide: DeckGeneratorService, useValue: mockDeckGenerator },
                { provide: WizardStateService, useValue: mockWizardState },
                { provide: ModeService, useValue: mockModeService },
                { provide: SqliteService, useValue: mockSqliteService }, // Provide mock SqliteService
                { provide: AppStore, useValue: mockStore },
                {
                    provide: ActivatedRoute,
                    useValue: {
                        queryParams: of({}),
                        snapshot: { queryParams: {} }
                    }
                }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(RunProtocolComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    describe('Machine Validation', () => {
        it('should identify simulated machine correctly', () => {
            // 1. is_simulation_override = true
            component.selectedMachine.set({
                machine: { is_simulation_override: true, connection_info: {} } as any,
                compatibility: { is_compatible: true } as any
            });
            expect(component.isMachineSimulated()).toBe(true);

            // 2. is_simulated = true (legacy/duck type)
            component.selectedMachine.set({
                machine: { is_simulated: true, connection_info: {} } as any,
                compatibility: { is_compatible: true } as any
            });
            expect(component.isMachineSimulated()).toBe(true);

            // 3. backend includes 'Simulator'
            component.selectedMachine.set({
                machine: { connection_info: { backend: 'SomethingSimulatorBackend' } } as any,
                compatibility: { is_compatible: true } as any
            });
            expect(component.isMachineSimulated()).toBe(true);

            // 4. Real machine
            component.selectedMachine.set({
                machine: { connection_info: { backend: 'HamiltonSTAR' } } as any,
                compatibility: { is_compatible: true } as any
            });
            expect(component.isMachineSimulated()).toBe(false);
        });

        it('should show error when in Physical mode and machine is simulated', () => {
            // Physical Mode
            mockStore.simulationMode.set(false);

            // Simulated Machine
            component.selectedMachine.set({
                machine: { is_simulation_override: true } as any,
                compatibility: { is_compatible: true } as any
            });

            expect(component.showMachineError()).toBe(true);
        });

        it('should NOT show error when in Simulation mode', () => {
            // Simulation Mode
            mockStore.simulationMode.set(true);

            // Simulated Machine
            component.selectedMachine.set({
                machine: { is_simulation_override: true } as any,
                compatibility: { is_compatible: true } as any
            });

            expect(component.showMachineError()).toBe(false);
        });

        it('should NOT show error for real machine', () => {
            // Physical Mode
            mockStore.simulationMode.set(false);

            // Real Machine
            component.selectedMachine.set({
                machine: { connection_info: { backend: 'RealBackend' } } as any,
                compatibility: { is_compatible: true } as any
            });

            expect(component.showMachineError()).toBe(false);
        });
    });
});
