import { Injectable } from '@angular/core';
import { ProtocolDefinition } from '@features/protocols/models/protocol.models';
import { PlrDeckData, PlrResource } from '@core/models/plr.models';
import { DeckCatalogService } from './deck-catalog.service';
import { AssetService } from '@features/assets/services/asset.service';
import { Machine } from '@features/assets/models/asset.models';

/**
 * Default dimensions used when PLR definitions are not available.
 * These are SBS standard dimensions for microplates.
 */
const DEFAULT_DIMENSIONS = {
    plate: { size_x: 127.76, size_y: 85.48, size_z: 14.5 },
    tipRack: { size_x: 127.76, size_y: 85.48, size_z: 60 },
    trough: { size_x: 127.76, size_y: 85.48, size_z: 40 },
    carrier: { size_x: 135.0, size_y: 497.0, size_z: 10.0 }
};

interface ResourceDimensions {
    size_x: number;
    size_y: number;
    size_z: number;
    num_items_x?: number;
    num_items_y?: number;
}

@Injectable({
    providedIn: 'root'
})
export class DeckGeneratorService {
    constructor(
        private deckCatalog: DeckCatalogService,
        private assetService: AssetService
    ) { }

    /**
     * Look up resource dimensions from cached PLR definitions.
     * Falls back to defaults if not found.
     */
    async getResourceDimensions(
        resourceType: string,
        fqn?: string
    ): Promise<ResourceDimensions> {
        try {
            const definition = await this.assetService.getResourceDefinition(fqn, resourceType);

            if (definition && definition.size_x_mm && definition.size_y_mm && definition.size_z_mm) {
                return {
                    size_x: definition.size_x_mm,
                    size_y: definition.size_y_mm,
                    size_z: definition.size_z_mm,
                    num_items_x: definition.num_items ? 12 : undefined, // Default 12 columns
                    num_items_y: definition.num_items ? Math.floor(definition.num_items / 12) : undefined
                };
            }
        } catch (error) {
            console.debug('Could not fetch PLR dimensions, using defaults:', error);
        }

        // Fall back to defaults based on resource type
        const typeKey = this.getTypeKey(resourceType);
        const defaults = DEFAULT_DIMENSIONS[typeKey] || DEFAULT_DIMENSIONS.plate;
        return {
            size_x: defaults.size_x,
            size_y: defaults.size_y,
            size_z: defaults.size_z
        };
    }

    private getTypeKey(resourceType: string): keyof typeof DEFAULT_DIMENSIONS {
        const type = resourceType.toLowerCase();
        if (type.includes('tip')) return 'tipRack';
        if (type.includes('trough') || type.includes('reservoir')) return 'trough';
        if (type.includes('carrier')) return 'carrier';
        return 'plate';
    }

    generateDeckForProtocol(
        protocol: ProtocolDefinition,
        assetMap?: Record<string, any>,
        machine?: Machine
    ): PlrDeckData {
        // Priority 1: Use machine's existing PLR state (live state)
        if (machine?.plr_state) {
            return {
                resource: machine.plr_state,
                state: {} // TODO: Populate state if needed
            };
        }

        // Priority 2: Use machine's PLR definition (static definition)
        if (machine?.plr_definition) {
            // If definition is available, use it as the base resource
            // We might need to wrap it if it's just the root resource
            const resource = machine.plr_definition as PlrResource;
            return {
                resource: resource,
                state: {}
            };
        }

        // Priority 3: Fallback to hardcoded generation (legacy)

        // Detect deck type from machine or default to Hamilton STAR
        const deckType = this.detectDeckType(machine);
        const spec = this.deckCatalog.getDeckDefinition(deckType);

        if (!spec) {
            console.warn(`No deck definition found for ${deckType}, falling back to Hamilton STAR`);
            return this.generateHamiltonDeck(protocol, assetMap);
        }

        if (spec.layoutType === 'slot-based') {
            return this.generateSlotBasedDeck(spec, protocol, assetMap);
        } else {
            return this.generateHamiltonDeck(protocol, assetMap);
        }
    }

    private detectDeckType(machine?: Machine): string {
        if (!machine) return 'HamiltonSTARDeck';

        // NEW: Check backend definition name/fqn first
        const backendName = machine.backend_definition?.name?.toLowerCase() || '';
        const backendFqn = machine.backend_definition?.fqn?.toLowerCase() || '';

        if (backendName.includes('ot-2') || backendName.includes('ot2') ||
            backendFqn.includes('opentrons.ot2')) {
            return 'OT2Deck';
        }

        if (backendName.includes('flex') || backendFqn.includes('opentrons.flex')) {
            return 'OT2Deck'; // or 'FlexDeck' if we have one
        }

        // Fallback to legacy detection
        if (machine.machine_category?.includes('OT-2') ||
            machine.machine_type?.includes('OT-2') ||
            machine.model?.includes('OT-2')) {
            return 'OT2Deck';
        }

        return 'HamiltonSTARDeck';
    }

    private generateSlotBasedDeck(
        spec: any, // DeckDefinitionSpec
        protocol: ProtocolDefinition,
        assetMap?: Record<string, any>
    ): PlrDeckData {
        const deck: PlrResource = {
            name: "deck",
            type: spec.fqn || "OT2Deck", // Fallback if fqn missing
            location: { x: 0, y: 0, z: 0, type: "Coordinate" },
            size_x: spec.dimensions.width,
            size_y: spec.dimensions.height,
            size_z: spec.dimensions.depth,
            children: []
        };

        // Create trash if deck has one defined in slots
        // OT-2 Trash is typically in slot 12
        const slots = spec.slots || [];
        const trashSlot = slots.find((s: any) => s.slotType === 'trash');

        if (trashSlot) {
            deck.children.push({
                name: 'Trash',
                type: 'Trash',
                location: {
                    x: trashSlot.position.x,
                    y: trashSlot.position.y,
                    z: trashSlot.position.z,
                    type: "Coordinate"
                },
                size_x: trashSlot.dimensions.width,
                size_y: trashSlot.dimensions.height,
                size_z: 100, // Arbitrary height
                children: [],
                slot_id: trashSlot.slotNumber
            } as PlrResource);
        }

        // Only place resources that are explicitly in the assetMap (user-assigned)
        if (protocol.assets && assetMap) {
            // Logic for placing assigned assets can go here if we want pre-population of assigned items.
            // For "Guided Setup" strictly starting empty, we might want to skip this loop entirely?
            // The prompt says "Guided Deck Setup Empty Start... only including machine-specific defaults".
            // However, if the user has already assigned assets in valid slots (e.g. re-entering wizard?), they should show up.
            // But the CarrierInferenceService is typically what places them.
            // DeckGeneratorService is seemingly used for VISUALIZATION.
            // If we remove logic here, the Deck View of the "Asset Selection" or "Wizard" steps might be empty even if successful?

            // Re-reading: "Deck state should be pulled from the database."
            // "The deck should start empty except for immutable machine defaults. Users add labware matching protocol requirements."

            // For now, we REMOVE the auto-placement logic.
            // The WizardStateService/CarrierInferenceService will handle adding things back one by one.
            // If assetMap is provided, we assume those assets are ALREADY known and placed?
            // Actually, in the current app flow, DeckGenerator is used to create the BACKGROUND deck.
            // The items on top are often handled by the wizard state overlay.
            // But let's stick to the plan: START EMPTY.
        }

        return { resource: deck, state: {} };
    }

    private generateHamiltonDeck(protocol: ProtocolDefinition, assetMap?: Record<string, any>): PlrDeckData {
        // 1. Base Deck (Hamilton STAR)
        const deck: PlrResource = {
            name: "deck",
            type: "HamiltonSTARDeck",
            location: { x: 0, y: 0, z: 0, type: "Coordinate" },
            size_x: 1200,
            size_y: 653.5,
            size_z: 500,
            num_rails: 30,
            children: []
        };

        // No default carriers created. 
        // The deck starts empty. Users must add carriers.

        return {
            resource: deck,
            state: {}
        };
    }

    /**
     * Async version that uses cached PLR dimensions.
     * Recommended for production use.
     */
    async generateDeckForProtocolAsync(
        protocol: ProtocolDefinition,
        assetMap?: Record<string, any>
    ): Promise<PlrDeckData> {
        // 1. Base Deck (Hamilton STAR) - try to get dimensions from cache
        const deckDims = await this.getResourceDimensions('HamiltonSTARDeck');

        const deck: PlrResource = {
            name: "deck",
            type: "HamiltonSTARDeck",
            location: { x: 0, y: 0, z: 0, type: "Coordinate" },
            size_x: deckDims.size_x || 1200,
            size_y: deckDims.size_y || 653.5,
            size_z: deckDims.size_z || 500,
            num_rails: 30,
            children: []
        };

        // Get hardware-spec rail positions
        const spec = this.deckCatalog.getHamiltonSTARSpec();
        const railPositions = spec.railPositions!;

        // Get carrier dimensions from cache
        const carrierDims = await this.getResourceDimensions('carrier');

        // 2. Add Standard Carriers at specific rails
        // Removed default carriers: Deck starts empty.

        // 3. Place Assets from Protocol with cached dimensions
        // Removed auto-placement logic.

        return { resource: deck, state: {} };
    }

    private createCarrier(name: string, type: string, x: number): PlrResource {
        return this.createCarrierWithDims(name, type, x, DEFAULT_DIMENSIONS.carrier);
    }

    private createCarrierWithDims(
        name: string,
        type: string,
        x: number,
        dims: ResourceDimensions
    ): PlrResource {
        return {
            name: name,
            type: type,
            location: { x: x, y: 63, z: 0, type: "Coordinate" },
            size_x: dims.size_x,
            size_y: dims.size_y,
            size_z: dims.size_z,
            children: []
        };
    }

    private createPlate(name: string): PlrResource {
        return this.createPlateWithDims(name, {
            ...DEFAULT_DIMENSIONS.plate,
            num_items_x: 12,
            num_items_y: 8
        });
    }

    private createPlateWithDims(name: string, dims: ResourceDimensions): PlrResource {
        const plate = {
            name: name,
            type: "Plate",
            location: { x: 10, y: 0, z: 0, type: "Coordinate" },
            size_x: dims.size_x,
            size_y: dims.size_y,
            size_z: dims.size_z,
            num_items_x: dims.num_items_x || 12,
            num_items_y: dims.num_items_y || 8,
            children: [] as PlrResource[]
        };
        plate.children = this.generateWells(name, plate.num_items_x, plate.num_items_y, 'circle');
        return plate;
    }

    private createTipRack(name: string): PlrResource {
        return this.createTipRackWithDims(name, {
            ...DEFAULT_DIMENSIONS.tipRack,
            num_items_x: 12,
            num_items_y: 8
        });
    }

    private createTipRackWithDims(name: string, dims: ResourceDimensions): PlrResource {
        const rack = {
            name: name,
            type: "TipRack",
            location: { x: 10, y: 0, z: 0, type: "Coordinate" },
            size_x: dims.size_x,
            size_y: dims.size_y,
            size_z: dims.size_z,
            num_items_x: dims.num_items_x || 12,
            num_items_y: dims.num_items_y || 8,
            children: [] as PlrResource[]
        };
        rack.children = this.generateWells(name, rack.num_items_x, rack.num_items_y, 'circle');
        return rack;
    }

    private createTrough(name: string): PlrResource {
        return this.createTroughWithDims(name, {
            ...DEFAULT_DIMENSIONS.trough,
            num_items_x: 12,
            num_items_y: 1
        });
    }

    private createTroughWithDims(name: string, dims: ResourceDimensions): PlrResource {
        const trough = {
            name: name,
            type: "Plate",
            location: { x: 10, y: 0, z: 0, type: "Coordinate" },
            size_x: dims.size_x,
            size_y: dims.size_y,
            size_z: dims.size_z,
            num_items_x: dims.num_items_x || 12,
            num_items_y: dims.num_items_y || 1,
            children: [] as PlrResource[]
        };
        trough.children = this.generateWells(name, trough.num_items_x, trough.num_items_y, 'rect');
        return trough;
    }


    private generateWells(parentName: string, cols: number, rows: number, shape: 'circle' | 'rect'): PlrResource[] {
        const wells: PlrResource[] = [];
        const wellSpacing = 9.0;
        const wellSize = 7.0;

        // This loop creates children. Position logic is simplified.
        // Real PLR uses sophisticated resource files.
        for (let i = 0; i < cols; i++) {
            for (let j = 0; j < rows; j++) {
                wells.push({
                    name: `${parentName}_well_${i}_${j}`,
                    type: "Well",
                    location: {
                        x: 14 + i * wellSpacing,
                        y: 11 + j * wellSpacing,
                        z: 2,
                        type: "Coordinate"
                    },
                    size_x: wellSize,
                    size_y: wellSize,
                    size_z: 10,
                    max_volume: 300,
                    volume: 0,
                    cross_section_type: shape,
                    children: []
                });
            }
        }
        return wells;
    }
}
