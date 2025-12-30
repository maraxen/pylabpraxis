import { Injectable } from '@angular/core';
import { ProtocolDefinition } from '@features/protocols/models/protocol.models';
import { PlrDeckData, PlrResource } from '@core/models/plr.models';

@Injectable({
    providedIn: 'root'
})
export class DeckGeneratorService {

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

        // 2. Add Standard Carriers
        // Plate Carrier at rail 5 (approx x=100)
        const plateCarrier = this.createCarrier("plate_carrier", "PlateCarrier", 100);
        deck.children.push(plateCarrier);

        // Tip Carrier at rail 15 (approx x=300)
        const tipCarrier = this.createCarrier("tip_carrier", "TipCarrier", 300);
        deck.children.push(tipCarrier);

        // Trough/Reservoir Carrier at rail 25 (approx x=500)
        const troughCarrier = this.createCarrier("trough_carrier", "PlateCarrier", 500); // Using PlateCarrier for simplicity
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

    private createCarrier(name: string, type: string, x: number): PlrResource {
        return {
            name: name,
            type: type, // "PlateCarrier", "TipCarrier"
            location: { x: x, y: 63, z: 0, type: "Coordinate" },
            size_x: 135.0,
            size_y: 497.0,
            size_z: 10.0,
            children: []
        };
    }

    private createPlate(name: string): PlrResource {
        const plate = {
            name: name,
            type: "Plate",
            location: { x: 10, y: 0, z: 0, type: "Coordinate" }, // relative to carrier
            size_x: 127.76,
            size_y: 85.48,
            size_z: 14.5,
            num_items_x: 12,
            num_items_y: 8,
            children: [] as PlrResource[]
        };
        plate.children = this.generateWells(name, 12, 8, 'circle');
        return plate;
    }

    private createTipRack(name: string): PlrResource {
        const rack = {
            name: name,
            type: "TipRack",
            location: { x: 10, y: 0, z: 0, type: "Coordinate" },
            size_x: 127.76,
            size_y: 85.48,
            size_z: 60, // taller than plate
            num_items_x: 12,
            num_items_y: 8,
            children: [] as PlrResource[]
        };
        rack.children = this.generateWells(name, 12, 8, 'circle'); // Tips use same well naming/structure usually in visualizer
        return rack;
    }

    private createTrough(name: string): PlrResource {
        // 12 column trough
        const trough = {
            name: name,
            type: "Plate", // Visualizer handles troughs usually as plates or specific types. Using Plate for safety.
            location: { x: 10, y: 0, z: 0, type: "Coordinate" },
            size_x: 127.76,
            size_y: 85.48,
            size_z: 40,
            num_items_x: 12,
            num_items_y: 1,
            children: [] as PlrResource[]
        };
        // Generate standard rect wells
        trough.children = this.generateWells(name, 12, 1, 'rect');
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
