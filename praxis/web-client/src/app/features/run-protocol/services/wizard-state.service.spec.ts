import { WizardStateService, WizardStep } from './wizard-state.service';
import { CarrierInferenceService } from './carrier-inference.service';
import { DeckCatalogService } from './deck-catalog.service';
import { ProtocolDefinition } from '@features/protocols/models/protocol.models';
import { describe, it, expect, beforeEach } from 'vitest';

describe('WizardStateService', () => {
    let service: WizardStateService;
    let carrierInference: CarrierInferenceService;
    let deckCatalog: DeckCatalogService;

    beforeEach(() => {
        deckCatalog = new DeckCatalogService();
        carrierInference = new CarrierInferenceService(deckCatalog);
        service = new WizardStateService(carrierInference, deckCatalog);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    describe('initialize', () => {
        it('should initialize with protocol', () => {
            const protocol: ProtocolDefinition = {
                name: 'Test Protocol',
                accession_id: 'test_1',
                version: '1.0',
                is_top_level: true,
                assets: [
                    { name: 'Plate1', accession_id: 'req_1', type_hint_str: 'Plate', fqn: '', optional: false, constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} }, location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] } },
                ],
                parameters: []
            };

            service.initialize(protocol);

            expect(service.currentStep()).toBe('carrier-placement');
            expect(service.protocol()).toBe(protocol);
            expect(service.carrierRequirements().length).toBeGreaterThan(0);
        });

        it('should start with empty assignments for empty protocol', () => {
            const protocol: ProtocolDefinition = {
                name: 'Empty',
                accession_id: 'test_1',
                version: '1.0',
                is_top_level: true,
                assets: [],
                parameters: []
            };

            service.initialize(protocol);

            expect(service.carrierRequirements().length).toBe(0);
            expect(service.slotAssignments().length).toBe(0);
        });
    });

    describe('step navigation', () => {
        beforeEach(() => {
            const protocol: ProtocolDefinition = {
                name: 'Test',
                accession_id: 'test_1',
                version: '1.0',
                is_top_level: true,
                assets: [],
                parameters: []
            };
            service.initialize(protocol);
        });

        it('should start at carrier-placement', () => {
            expect(service.currentStep()).toBe('carrier-placement');
        });

        it('should navigate to next step', () => {
            service.nextStep();
            expect(service.currentStep()).toBe('resource-placement');

            service.nextStep();
            expect(service.currentStep()).toBe('verification');
        });

        it('should navigate to previous step', () => {
            service.nextStep();
            service.nextStep();
            expect(service.currentStep()).toBe('verification');

            service.previousStep();
            expect(service.currentStep()).toBe('resource-placement');

            service.previousStep();
            expect(service.currentStep()).toBe('carrier-placement');
        });

        it('should not go before first step', () => {
            service.previousStep();
            expect(service.currentStep()).toBe('carrier-placement');
        });
    });

    describe('carrier placement tracking', () => {
        beforeEach(() => {
            const protocol: ProtocolDefinition = {
                name: 'Test',
                accession_id: 'test_1',
                version: '1.0',
                is_top_level: true,
                assets: [
                    { name: 'Plate1', accession_id: 'req_1', type_hint_str: 'Plate', fqn: '', optional: false, constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} }, location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] } },
                ],
                parameters: []
            };
            service.initialize(protocol);
        });

        it('should mark carrier as placed', () => {
            const reqs = service.carrierRequirements();
            expect(reqs[0].placed).toBe(false);

            service.markCarrierPlaced(reqs[0].carrierFqn, true);

            expect(service.carrierRequirements()[0].placed).toBe(true);
        });

        it('should compute allCarriersPlaced correctly', () => {
            expect(service.allCarriersPlaced()).toBe(false);

            const reqs = service.carrierRequirements();
            for (const req of reqs) {
                service.markCarrierPlaced(req.carrierFqn, true);
            }

            expect(service.allCarriersPlaced()).toBe(true);
        });
    });

    describe('skip and complete', () => {
        beforeEach(() => {
            const protocol: ProtocolDefinition = {
                name: 'Test',
                accession_id: 'test_1',
                version: '1.0',
                is_top_level: true,
                assets: [],
                parameters: []
            };
            service.initialize(protocol);
        });

        it('should handle skip', () => {
            service.skip();
            expect(service.skipped()).toBe(true);
            expect(service.isComplete()).toBe(true);
        });

        it('should handle complete', () => {
            service.complete();
            expect(service.isComplete()).toBe(true);
            expect(service.skipped()).toBe(false);
        });
    });

    describe('state persistence', () => {
        it('should get and restore state', () => {
            const protocol: ProtocolDefinition = {
                name: 'Test',
                accession_id: 'test_1',
                version: '1.0',
                is_top_level: true,
                assets: [],
                parameters: []
            };
            service.initialize(protocol);
            service.nextStep();

            const state = service.getState();

            service.reset();
            expect(service.currentStep()).toBe('carrier-placement');

            service.restoreState(state);
            expect(service.currentStep()).toBe('resource-placement');
        });
    });

    describe('progress computation', () => {
        it('should compute progress correctly', () => {
            const protocol: ProtocolDefinition = {
                name: 'Test',
                accession_id: 'test_1',
                version: '1.0',
                is_top_level: true,
                assets: [
                    { name: 'Plate1', accession_id: 'req_1', type_hint_str: 'Plate', fqn: '', optional: false, constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} }, location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] } },
                    { name: 'Plate2', accession_id: 'req_2', type_hint_str: 'Plate', fqn: '', optional: false, constraints: { required_methods: [], required_attributes: [], required_method_signatures: {}, required_method_args: {} }, location_constraints: { location_requirements: [], on_resource_type: '', stack: false, directly_position: false, position_condition: [] } },
                ],
                parameters: []
            };
            service.initialize(protocol);

            expect(service.progress()).toBe(0);

            // Mark carrier placed (1 carrier for 2 plates)
            const reqs = service.carrierRequirements();
            service.markCarrierPlaced(reqs[0].carrierFqn, true);

            // 1 carrier + 0 resources / (1 carrier + 2 resources) = 33%
            expect(service.progress()).toBeGreaterThan(0);
        });
    });
});
