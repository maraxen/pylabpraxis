import { DeckGeneratorService } from './deck-generator.service';
import { DeckCatalogService } from './deck-catalog.service';
import { ProtocolDefinition } from '@features/protocols/models/protocol.models';
import { describe, it, expect, beforeEach } from 'vitest';

describe('DeckGeneratorService', () => {
    let service: DeckGeneratorService;
    let deckCatalog: DeckCatalogService;

    beforeEach(() => {
        // Create DeckCatalogService instance
        deckCatalog = new DeckCatalogService();

        // Create service instance with dependency
        service = new DeckGeneratorService(deckCatalog);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    it('should generate a deck with correct base dimensions and rails for Hamilton STAR', () => {
        const protocol: ProtocolDefinition = {
            name: 'Test Protocol',
            is_top_level: true,
            accession_id: 'test_1',
            assets: [],
            version: '1.0',
            parameters: []
        };
        const data = service.generateDeckForProtocol(protocol);

        expect(data.resource.type).toBe('HamiltonSTARDeck');
        expect(data.resource.num_rails).toBe(30);
        expect(data.resource.size_x).toBe(1200);
    });

    it('should create ghost resources when asset map is missing', () => {
        const protocol: ProtocolDefinition = {
            name: 'Test',
            accession_id: 'test_1',
            version: '1.0',
            is_top_level: true,
            assets: [
                {
                    name: 'SourcePlate',
                    accession_id: 'req_1',
                    type_hint_str: 'Plate',
                    fqn: 'pylabrobot.resources.Plate',
                    optional: false,
                    constraints: {
                        required_methods: [],
                        required_attributes: [],
                        required_method_signatures: {},
                        required_method_args: {}
                    },
                    location_constraints: {
                        location_requirements: [],
                        on_resource_type: '',
                        stack: false,
                        directly_position: false,
                        position_condition: []
                    }
                }
            ],
            parameters: []
        };

        const data = service.generateDeckForProtocol(protocol); // No asset map

        // Find the plate carrier
        const plateCarrier = data.resource.children.find(c => c.name === 'plate_carrier');
        expect(plateCarrier).toBeTruthy();

        // Check for ghost plate
        const ghost = plateCarrier!.children.find(c => c.name.startsWith('ghost_'));
        expect(ghost).toBeTruthy();

        // Verify ghost properties
        if (ghost) {
            expect(ghost.name).toBe('ghost_SourcePlate');
            expect(ghost.children.length).toBe(0); // Should have no wells
            expect(ghost.color).toBeUndefined(); // Should NOT have manual color override (let CSS handle it)
        }
    });

    it('should create standard dimensions for carriers', () => {
        const protocol: ProtocolDefinition = {
            name: 'Test',
            accession_id: 'test_1',
            assets: [],
            is_top_level: true,
            version: '1.0',
            parameters: []
        };
        const data = service.generateDeckForProtocol(protocol);
        const carrier = data.resource.children.find(c => c.name === 'plate_carrier');

        expect(carrier).toBeTruthy();
        expect(carrier!.size_x).toBe(135.0);
        expect(carrier!.size_y).toBe(497.0);
    });

    it('should place carriers at hardware-accurate rail positions', () => {
        const protocol: ProtocolDefinition = {
            name: 'Test',
            accession_id: 'test_1',
            assets: [],
            is_top_level: true,
            version: '1.0',
            parameters: []
        };
        const data = service.generateDeckForProtocol(protocol);

        const plateCarrier = data.resource.children.find(c => c.name === 'plate_carrier');
        const tipCarrier = data.resource.children.find(c => c.name === 'tip_carrier');
        const troughCarrier = data.resource.children.find(c => c.name === 'trough_carrier');

        // Plate carrier at rail 5: 100 + (5 * 22.5) = 212.5mm
        expect(plateCarrier!.location.x).toBe(212.5);

        // Tip carrier at rail 15: 100 + (15 * 22.5) = 437.5mm
        expect(tipCarrier!.location.x).toBe(437.5);

        // Trough carrier at rail 25: 100 + (25 * 22.5) = 662.5mm
        expect(troughCarrier!.location.x).toBe(662.5);
    });
});

