import { Injectable, inject } from '@angular/core';
import { ProtocolDefinition } from '@features/protocols/models/protocol.models';
import { PlrDeckData, PlrResource } from '@core/models/plr.models';
import { DeckCatalogService } from './deck-catalog.service';
import { AssetService } from '@features/assets/services/asset.service';

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
    private assetService = inject(AssetService);

    constructor(private deckCatalog: DeckCatalogService) { }

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

    generateDeckForProtocol(protocol: ProtocolDefinition, assetMap?: Record<string, any>): PlrDeckData {
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

        // Get hardware-spec rail positions
        const spec = this.deckCatalog.getHamiltonSTARSpec();
        const railPositions = spec.railPositions!;

        // 2. Add Standard Carriers at specific rails
        // Plate Carrier at rail 5
        const plateCarrierRail = 5;
        const plateCarrier = this.createCarrier(
            "plate_carrier",
            "PlateCarrier",
            railPositions[plateCarrierRail]
        );
        deck.children.push(plateCarrier);

        // Tip Carrier at rail 15
        const tipCarrierRail = 15;
        const tipCarrier = this.createCarrier(
            "tip_carrier",
            "TipCarrier",
            railPositions[tipCarrierRail]
        );
        deck.children.push(tipCarrier);

        // Trough/Reservoir Carrier at rail 25
        const troughCarrierRail = 25;
        const troughCarrier = this.createCarrier(
            "trough_carrier",
            "PlateCarrier",
            railPositions[troughCarrierRail]
        );
        deck.children.push(troughCarrier);

        // 3. Place Assets from Protocol
        if (protocol.assets) {
            let plateSlotIndex = 0;
            let tipSlotIndex = 0;
            let troughSlotIndex = 0;

            protocol.assets.forEach((asset, index) => {
                let resource: PlrResource | null = null;
                let parent: PlrResource | null = null;
                let yOffset = 0;
                let isGhost = false;

                // Determine name and ghost status
                let displayName = asset.name;

                // If assetMap is null (initial) or asset not in map -> Ghost
                if (!assetMap || !assetMap[asset.accession_id]) {
                    isGhost = true;
                    displayName = `ghost_${asset.name}`;
                } else {
                    displayName = assetMap[asset.accession_id].name;
                }

                // Simple logic to interpret type hints and place them
                const typeHint = asset.type_hint_str?.toLowerCase() || '';
                const name = asset.name.toLowerCase();

                // If ghost, we default to standard container size roughly match
                // We reuse create functions but will strip children and colorize

                if (typeHint.includes('plate') || name.includes('plate')) {
                    resource = this.createPlate(displayName);
                    parent = plateCarrier;
                    yOffset = 10 + (plateSlotIndex * 100);
                    plateSlotIndex++;
                } else if (typeHint.includes('tip') || name.includes('tip')) {
                    resource = this.createTipRack(displayName);
                    parent = tipCarrier;
                    yOffset = 10 + (tipSlotIndex * 100);
                    tipSlotIndex++;
                } else if (typeHint.includes('trough') || name.includes('reservoir')) {
                    resource = this.createTrough(displayName);
                    parent = troughCarrier;
                    yOffset = 10 + (troughSlotIndex * 100);
                    troughSlotIndex++;
                }

                if (resource && parent) {
                    resource.location.y = yOffset;
                    resource.location.z = 10;

                    if (isGhost) {
                        resource.children = []; // No detailed wells for ghosts
                        // resource.color is REMOVED so CSS class .is-ghost can apply background/border
                    }

                    parent.children.push(resource);
                }
            });
        }

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
        const plateCarrier = this.createCarrierWithDims(
            "plate_carrier", "PlateCarrier", railPositions[5], carrierDims
        );
        deck.children.push(plateCarrier);

        const tipCarrier = this.createCarrierWithDims(
            "tip_carrier", "TipCarrier", railPositions[15], carrierDims
        );
        deck.children.push(tipCarrier);

        const troughCarrier = this.createCarrierWithDims(
            "trough_carrier", "PlateCarrier", railPositions[25], carrierDims
        );
        deck.children.push(troughCarrier);

        // 3. Place Assets from Protocol with cached dimensions
        if (protocol.assets) {
            let plateSlotIndex = 0;
            let tipSlotIndex = 0;
            let troughSlotIndex = 0;

            for (const asset of protocol.assets) {
                let resource: PlrResource | null = null;
                let parent: PlrResource | null = null;
                let yOffset = 0;
                let isGhost = false;

                let displayName = asset.name;
                if (!assetMap || !assetMap[asset.accession_id]) {
                    isGhost = true;
                    displayName = `ghost_${asset.name}`;
                } else {
                    displayName = assetMap[asset.accession_id].name;
                }

                const typeHint = asset.type_hint_str?.toLowerCase() || '';
                const name = asset.name.toLowerCase();

                if (typeHint.includes('plate') || name.includes('plate')) {
                    const dims = await this.getResourceDimensions('plate', asset.fqn);
                    resource = this.createPlateWithDims(displayName, dims);
                    parent = plateCarrier;
                    yOffset = 10 + (plateSlotIndex * 100);
                    plateSlotIndex++;
                } else if (typeHint.includes('tip') || name.includes('tip')) {
                    const dims = await this.getResourceDimensions('tipRack', asset.fqn);
                    resource = this.createTipRackWithDims(displayName, dims);
                    parent = tipCarrier;
                    yOffset = 10 + (tipSlotIndex * 100);
                    tipSlotIndex++;
                } else if (typeHint.includes('trough') || name.includes('reservoir')) {
                    const dims = await this.getResourceDimensions('trough', asset.fqn);
                    resource = this.createTroughWithDims(displayName, dims);
                    parent = troughCarrier;
                    yOffset = 10 + (troughSlotIndex * 100);
                    troughSlotIndex++;
                }

                if (resource && parent) {
                    resource.location.y = yOffset;
                    resource.location.z = 10;
                    if (isGhost) {
                        resource.children = [];
                    }
                    parent.children.push(resource);
                }
            }
        }

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
