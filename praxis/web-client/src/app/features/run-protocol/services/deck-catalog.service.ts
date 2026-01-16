import { Injectable, inject } from '@angular/core';
import {
    DeckConfiguration,
    DeckRail,
    DeckCarrier,
    CarrierSlot,
    DeckDefinitionSpec,
    DeckSlotSpec,
    CarrierDefinition
} from '../models/deck-layout.models';
import { Machine } from '../../assets/models/asset.models';
import { PlrResource } from '@core/models/plr.models';
import { SqliteService } from '@core/services/sqlite.service';
import { DeckDefinitionCatalog } from '@core/db/schema';
import { map, switchMap, take } from 'rxjs/operators';
import { Observable, of } from 'rxjs';

/**
 * Service for fetching deck and carrier specifications.
 * 
 * Provides hardcoded specifications for standard decks and
 * integrates with SqliteService for persisting user-defined deck configurations.
 */
@Injectable({
    providedIn: 'root'
})
export class DeckCatalogService {
    private sqlite = inject(SqliteService);

    // ========================================================================
    // Hamilton STAR Constants
    // ========================================================================

    /** Hamilton STAR rail spacing in mm */
    private readonly HAMILTON_STAR_RAIL_SPACING = 22.5;

    /** Hamilton STAR first rail X position (offset from deck origin) */
    private readonly HAMILTON_STAR_RAIL_OFFSET = 100.0;

    /** Standard carrier rail spans */
    private readonly STANDARD_CARRIER_RAIL_SPAN = 6;

    // ========================================================================
    // Public API
    // ========================================================================

    /**
     * Get deck definition specification by FQN or type name.
     */
    getDeckDefinition(fqn: string): DeckDefinitionSpec | null {
        // Hamilton STAR detection
        if (fqn === 'pylabrobot.resources.hamilton.HamiltonSTARDeck' ||
            fqn === 'HamiltonSTARDeck' ||
            fqn.includes('STAR')) {
            return this.getHamiltonSTARSpec();
        }
        // Opentrons OT-2 detection
        if (fqn === 'pylabrobot.resources.opentrons.deck.OTDeck' ||
            fqn === 'OTDeck' ||
            fqn.includes('OT2') ||
            fqn.includes('OT-2') ||
            fqn.toLowerCase().includes('opentrons')) {
            return this.getOTDeckSpec();
        }
        return null;
    }

    /**
     * Get deck type (FQN) for a given machine instance.
     */
    getDeckTypeForMachine(machine: Machine | null | undefined): string | null {
        if (!machine) return null;

        // 1. Check machine definition/category
        const category = machine.machine_category || machine.machine_type || '';
        const model = machine.model || '';
        const manufacturer = (machine.manufacturer || '').toLowerCase();

        // Hamilton STAR family
        if (category.includes('Hamilton') || category.includes('STAR') ||
            model.includes('STAR') || manufacturer.includes('hamilton')) {
            return 'pylabrobot.resources.hamilton.HamiltonSTARDeck';
        }

        // Opentrons OT-2
        if (category.includes('Opentrons') || category.includes('OT') ||
            model.includes('OT') || manufacturer.includes('opentrons')) {
            return 'pylabrobot.resources.opentrons.deck.OTDeck';
        }

        // 2. Check connection info (fallback for simulators)
        const connectionInfo = machine.connection_info || {};
        const backend = (connectionInfo['backend'] || '').toString();

        if (backend.includes('hamilton.STAR') || backend.includes('HamiltonDeck')) {
            return 'pylabrobot.resources.hamilton.HamiltonSTARDeck';
        }
        if (backend.includes('opentrons.OT2') || backend.includes('OTDeck')) {
            return 'pylabrobot.resources.opentrons.deck.OTDeck';
        }

        return null;
    }

    /**
     * Get all available carriers compatible with a deck type.
     */
    getCompatibleCarriers(deckFqn: string): CarrierDefinition[] {
        if (!deckFqn) return [];

        // Hamilton STAR Deck (legacy check + FQN check)
        if (deckFqn.includes('Hamilton') || deckFqn.includes('STAR')) {
            return this.getHamiltonCarriers();
        }

        // Opentrons OT-2 Deck
        // Currently we don't have separate carrier definitions for OT-2 since it uses
        // direct slot placement for labware, but we might want to return empty or specific ones.
        // For now, returning empty array is correct as OT-2 doesn't use "carriers" in the same way.

        return [];
    }

    // ========================================================================
    // Persistence API
    // ========================================================================

    /**
     * Save a user-defined deck configuration to SQLite.
     * Uses 'deck_definition_catalog' table.
     */
    saveUserDeckConfiguration(config: DeckConfiguration, name: string): Observable<DeckDefinitionCatalog> {
        return this.sqlite.deckDefinitions.pipe(
            take(1),
            map(repo => {
                const now = new Date().toISOString();
                const entity: Partial<DeckDefinitionCatalog> = {
                    accession_id: crypto.randomUUID(),
                    name: name,
                    fqn: `deck_config.user.${name.replace(/\s+/g, '_').toLowerCase()}`,
                    description: `User defined deck configuration for ${config.deckName}`,
                    created_at: now,
                    updated_at: now,
                    properties_json: {
                        is_user_config: true,
                        base_deck_fqn: config.deckType,
                        configuration: config
                    }
                };
                return repo.create(entity as any);
            })
        );
    }

    /**
     * Get all user-defined deck configurations.
     */
    getUserDeckConfigurations(): Observable<{ id: string, name: string, config: DeckConfiguration }[]> {
        return this.sqlite.deckDefinitions.pipe(
            take(1),
            map(repo => {
                const all = repo.findAll();
                // Filter for user configs in memory (could be optimized with a query info logic exists)
                return all
                    .filter(def => {
                        const props = def.properties_json as any;
                        return props && props.is_user_config === true;
                    })
                    .map(def => ({
                        id: def.accession_id!,
                        name: def.name!,
                        config: (def.properties_json as any).configuration as DeckConfiguration
                    }));
            })
        );
    }

    /**
     * Get user configurations compatible with a specific machine definition.
     */
    getUserConfigsForMachine(machineDefFqn: string): Observable<{ id: string, name: string, config: DeckConfiguration }[]> {
        return this.sqlite.deckDefinitions.pipe(
            take(1),
            map(repo => {
                const all = repo.findAll();
                return all
                    .filter(def => {
                        const props = def.properties_json as any;
                        if (!props || !props.is_user_config) return false;

                        // Compatibility check
                        const baseFqn = props.base_deck_fqn;
                        if (machineDefFqn.includes('Hamilton') && baseFqn.includes('Hamilton')) return true;
                        if (machineDefFqn.includes('OT') && baseFqn.includes('OT')) return true;

                        return false;
                    })
                    .map(def => ({
                        id: def.accession_id!,
                        name: def.name!,
                        config: (def.properties_json as any).configuration as DeckConfiguration
                    }));
            })
        );
    }

    // ========================================================================
    // Spec Generators
    // ========================================================================

    /**
     * Get Hamilton STAR deck specification.
     */
    getHamiltonSTARSpec(): DeckDefinitionSpec {
        const numRails = 30;
        const railPositions: number[] = [];

        for (let i = 0; i < numRails; i++) {
            railPositions.push(this.HAMILTON_STAR_RAIL_OFFSET + (i * this.HAMILTON_STAR_RAIL_SPACING));
        }

        return {
            fqn: 'pylabrobot.resources.hamilton.HamiltonSTARDeck',
            name: 'Hamilton STAR Deck',
            manufacturer: 'Hamilton',
            layoutType: 'rail-based',
            numRails: numRails,
            railSpacing: this.HAMILTON_STAR_RAIL_SPACING,
            railPositions: railPositions,
            compatibleCarriers: [
                'pylabrobot.resources.ml_star.plt_car_l5ac',
                'pylabrobot.resources.ml_star.tip_car_480',
                'pylabrobot.resources.ml_star.rgt_car_3r'
            ],
            dimensions: {
                width: 1200,
                height: 653.5,
                depth: 500
            }
        };
    }

    /**
     * Get Opentrons OT-2 deck specification.
     * Slot positions match PyLabRobot's OTDeck.slot_locations.
     */
    getOTDeckSpec(): DeckDefinitionSpec {
        // OT-2 has 12 slots in a 4x3 grid pattern
        // Positions from pylabrobot/resources/opentrons/deck.py
        const slotWidth = 127.76;  // Standard SBS footprint
        const slotHeight = 85.48;

        const slots: DeckSlotSpec[] = [
            // Row 1 (bottom, y=0)
            { slotNumber: 1, label: '1', slotType: 'standard', position: { x: 0.0, y: 0.0, z: 0 }, dimensions: { width: slotWidth, height: slotHeight }, compatibleResourceTypes: ['Plate', 'TipRack', 'Trough', 'Reservoir', 'TubeRack'] },
            { slotNumber: 2, label: '2', slotType: 'standard', position: { x: 132.5, y: 0.0, z: 0 }, dimensions: { width: slotWidth, height: slotHeight }, compatibleResourceTypes: ['Plate', 'TipRack', 'Trough', 'Reservoir', 'TubeRack'] },
            { slotNumber: 3, label: '3', slotType: 'standard', position: { x: 265.0, y: 0.0, z: 0 }, dimensions: { width: slotWidth, height: slotHeight }, compatibleResourceTypes: ['Plate', 'TipRack', 'Trough', 'Reservoir', 'TubeRack'] },
            // Row 2 (y=90.5)
            { slotNumber: 4, label: '4', slotType: 'standard', position: { x: 0.0, y: 90.5, z: 0 }, dimensions: { width: slotWidth, height: slotHeight }, compatibleResourceTypes: ['Plate', 'TipRack', 'Trough', 'Reservoir', 'TubeRack'] },
            { slotNumber: 5, label: '5', slotType: 'standard', position: { x: 132.5, y: 90.5, z: 0 }, dimensions: { width: slotWidth, height: slotHeight }, compatibleResourceTypes: ['Plate', 'TipRack', 'Trough', 'Reservoir', 'TubeRack'] },
            { slotNumber: 6, label: '6', slotType: 'standard', position: { x: 265.0, y: 90.5, z: 0 }, dimensions: { width: slotWidth, height: slotHeight }, compatibleResourceTypes: ['Plate', 'TipRack', 'Trough', 'Reservoir', 'TubeRack'] },
            // Row 3 (y=181.0)
            { slotNumber: 7, label: '7', slotType: 'standard', position: { x: 0.0, y: 181.0, z: 0 }, dimensions: { width: slotWidth, height: slotHeight }, compatibleResourceTypes: ['Plate', 'TipRack', 'Trough', 'Reservoir', 'TubeRack'] },
            { slotNumber: 8, label: '8', slotType: 'standard', position: { x: 132.5, y: 181.0, z: 0 }, dimensions: { width: slotWidth, height: slotHeight }, compatibleResourceTypes: ['Plate', 'TipRack', 'Trough', 'Reservoir', 'TubeRack'] },
            { slotNumber: 9, label: '9', slotType: 'standard', position: { x: 265.0, y: 181.0, z: 0 }, dimensions: { width: slotWidth, height: slotHeight }, compatibleResourceTypes: ['Plate', 'TipRack', 'Trough', 'Reservoir', 'TubeRack'] },
            // Row 4 (top, y=271.5)
            { slotNumber: 10, label: '10', slotType: 'standard', position: { x: 0.0, y: 271.5, z: 0 }, dimensions: { width: slotWidth, height: slotHeight }, compatibleResourceTypes: ['Plate', 'TipRack', 'Trough', 'Reservoir', 'TubeRack'] },
            { slotNumber: 11, label: '11', slotType: 'standard', position: { x: 132.5, y: 271.5, z: 0 }, dimensions: { width: slotWidth, height: slotHeight }, compatibleResourceTypes: ['Plate', 'TipRack', 'Trough', 'Reservoir', 'TubeRack'] },
            { slotNumber: 12, label: 'Trash', slotType: 'trash', position: { x: 265.0, y: 271.5, z: 0 }, dimensions: { width: slotWidth, height: slotHeight }, compatibleResourceTypes: ['Trash'] },
        ];

        return {
            fqn: 'pylabrobot.resources.opentrons.deck.OTDeck',
            name: 'Opentrons OT-2 Deck',
            manufacturer: 'Opentrons',
            layoutType: 'slot-based',
            numSlots: 12,
            slots: slots,
            dimensions: {
                width: 624.3,
                height: 565.2,
                depth: 900
            }
        };
    }

    /**
     * Create a PlrResource (PyLabRobot tree) from a specification.
     * Useful for synthesizing deck layouts when full state is not available.
     */
    createPlrResourceFromSpec(spec: DeckDefinitionSpec): PlrResource {
        const deck: PlrResource = {
            name: "deck",
            type: spec.fqn,
            location: { x: 0, y: 0, z: 0, type: "Coordinate" },
            size_x: spec.dimensions.width,
            size_y: spec.dimensions.height,
            size_z: spec.dimensions.depth,
            children: []
        };

        if (spec.numRails) {
            deck.num_rails = spec.numRails;
        }

        // If slot-based, add slots as children (as trash or modules)
        if (spec.layoutType === 'slot-based' && spec.slots) {
            spec.slots.forEach(slot => {
                if (slot.slotType === 'trash' || slot.slotType === 'module') {
                    deck.children.push({
                        name: slot.label,
                        type: slot.slotType === 'trash' ? 'Trash' : 'Resource',
                        location: {
                            x: slot.position.x,
                            y: slot.position.y,
                            z: slot.position.z,
                            type: "Coordinate"
                        },
                        size_x: slot.dimensions.width,
                        size_y: slot.dimensions.height,
                        size_z: 10,
                        children: [],
                        slot_id: slot.slotNumber.toString()
                    });
                }
            });
        }

        return deck;
    }

    /**
     * Synthesize a PlrResource tree from a saved DeckConfiguration.
     * This allows rendering user-designed layouts in the Workcell View.
     */
    createPlrResourceFromConfig(config: DeckConfiguration): PlrResource {
        // Start with the base deck definition
        const spec = this.getDeckDefinition(config.deckType);
        const deck = spec ? this.createPlrResourceFromSpec(spec) : {
            name: config.deckName,
            type: config.deckType,
            location: { x: 0, y: 0, z: 0, type: "Coordinate" },
            size_x: config.dimensions.width,
            size_y: config.dimensions.height,
            size_z: config.dimensions.depth,
            children: []
        };

        config.carriers.forEach(carrier => {
            let x = 0;
            let y = 63.0; // Default Y offset for STAR
            let z = 100.0; // Default Z height

            // Calculate position based on rail/slot
            if (spec?.layoutType === 'rail-based') {
                const rail = config.rails.find(r => r.index === carrier.railPosition);
                if (rail) {
                    x = rail.xPosition;
                } else {
                    x = this.HAMILTON_STAR_RAIL_OFFSET + (carrier.railPosition * this.HAMILTON_STAR_RAIL_SPACING);
                }
            } else if (spec?.layoutType === 'slot-based' && spec.slots) {
                const slot = spec.slots.find(s => s.slotNumber === carrier.railPosition);
                if (slot) {
                    x = slot.position.x;
                    y = slot.position.y;
                    z = slot.position.z;
                }
            }

            const carrierRes: PlrResource = {
                name: carrier.id,
                type: carrier.fqn,
                location: { x, y, z, type: "Coordinate" },
                size_x: carrier.dimensions.width,
                size_y: carrier.dimensions.height,
                size_z: carrier.dimensions.depth,
                children: []
            };

            // Add Slots/Sites
            carrier.slots.forEach(slot => {
                const siteRes: PlrResource = {
                    name: slot.id,
                    type: 'Site',
                    location: slot.position,
                    size_x: slot.dimensions.width,
                    size_y: slot.dimensions.height,
                    size_z: 10,
                    children: []
                };

                // Add Labware/Resource if present
                if (slot.resource) {
                    const labwareRes: PlrResource = {
                        name: slot.resource.name,
                        type: slot.resource.type,
                        location: { x: 0, y: 0, z: 0, type: "Coordinate" },
                        size_x: slot.dimensions.width,
                        size_y: slot.dimensions.height,
                        size_z: slot.resource.size_z || 15,
                        children: []
                    };
                    siteRes.children.push(labwareRes);
                }

                carrierRes.children.push(siteRes);
            });

            deck.children.push(carrierRes);
        });

        return deck;
    }

    /**
     * Create a DeckConfiguration from a deck specification.
     */
    createDeckConfiguration(spec: DeckDefinitionSpec): DeckConfiguration {
        const rails = this.createRailsFromSpec(spec);

        return {
            deckType: spec.fqn,
            deckName: spec.name,
            rails: rails,
            carriers: [], // Empty until carriers are placed
            dimensions: spec.dimensions,
            numRails: spec.numRails || 0
        };
    }

    /**
     * Create a carrier instance from a definition.
     */
    createCarrierFromDefinition(
        definition: CarrierDefinition,
        id: string,
        railPosition: number
    ): DeckCarrier {
        const slots = this.createSlotsForCarrier(definition, id);

        return {
            id: id,
            fqn: definition.fqn,
            name: definition.name,
            type: definition.type,
            railPosition: railPosition,
            railSpan: definition.railSpan,
            slots: slots,
            dimensions: definition.dimensions
        };
    }

    // ========================================================================
    // Private Helpers
    // ========================================================================

    private createRailsFromSpec(spec: DeckDefinitionSpec): DeckRail[] {
        const rails: DeckRail[] = [];
        const positions = spec.railPositions || this.calculateRailPositions(spec);

        for (let i = 0; i < (spec.numRails || 0); i++) {
            rails.push({
                index: i,
                xPosition: positions[i],
                width: spec.railSpacing || 0,
                compatibleCarrierTypes: spec.compatibleCarriers || []
            });
        }

        return rails;
    }

    private calculateRailPositions(spec: DeckDefinitionSpec): number[] {
        const positions: number[] = [];
        const numRails = spec.numRails || 0;
        const railSpacing = spec.railSpacing || 22.5;
        for (let i = 0; i < numRails; i++) {
            positions.push(this.HAMILTON_STAR_RAIL_OFFSET + (i * railSpacing));
        }
        return positions;
    }

    private createSlotsForCarrier(definition: CarrierDefinition, carrierId: string): CarrierSlot[] {
        const slots: CarrierSlot[] = [];
        const slotHeight = definition.dimensions.height / definition.numSlots;

        for (let i = 0; i < definition.numSlots; i++) {
            slots.push({
                id: `${carrierId}_slot_${i}`,
                index: i,
                name: `Position ${i + 1}`,
                compatibleResourceTypes: definition.compatibleResourceTypes,
                occupied: false,
                resource: null,
                position: {
                    x: 10, // Offset from carrier edge
                    y: 10 + (i * slotHeight),
                    z: 0
                },
                dimensions: {
                    width: definition.dimensions.width - 20,
                    height: slotHeight - 10
                }
            });
        }

        return slots;
    }

    private getHamiltonCarriers(): CarrierDefinition[] {
        return [
            {
                fqn: 'pylabrobot.resources.ml_star.plt_car_l5ac',
                name: 'Plate Carrier L5AC',
                type: 'plate',
                railSpan: this.STANDARD_CARRIER_RAIL_SPAN,
                numSlots: 5,
                compatibleResourceTypes: ['Plate', 'Microplate', 'WellPlate', 'Lid'],
                dimensions: { width: 135.0, height: 497.0, depth: 10.0 }
            },
            {
                fqn: 'pylabrobot.resources.ml_star.tip_car_480',
                name: 'Tip Carrier 480',
                type: 'tip',
                railSpan: this.STANDARD_CARRIER_RAIL_SPAN,
                numSlots: 5,
                compatibleResourceTypes: ['TipRack', 'NestedTipRack'],
                dimensions: { width: 135.0, height: 497.0, depth: 10.0 }
            },
            {
                fqn: 'pylabrobot.resources.ml_star.rgt_car_3r',
                name: 'Reagent Carrier 3R',
                type: 'trough',
                railSpan: this.STANDARD_CARRIER_RAIL_SPAN,
                numSlots: 3,
                compatibleResourceTypes: ['Trough', 'Reservoir'],
                dimensions: { width: 135.0, height: 497.0, depth: 10.0 }
            },
            {
                fqn: 'pylabrobot.resources.ml_star.tube_car_24',
                name: 'Tube Carrier 24',
                type: 'tube',
                railSpan: this.STANDARD_CARRIER_RAIL_SPAN,
                numSlots: 6,
                compatibleResourceTypes: ['TubeRack', 'Tube'],
                dimensions: { width: 135.0, height: 497.0, depth: 10.0 }
            },
            {
                fqn: 'pylabrobot.resources.ml_star.mfx_car_l5',
                name: 'MFX Carrier L5',
                type: 'mfx',
                railSpan: this.STANDARD_CARRIER_RAIL_SPAN,
                numSlots: 5,
                compatibleResourceTypes: ['Plate', 'TipRack', 'Trough'],
                dimensions: { width: 135.0, height: 497.0, depth: 10.0 }
            }
        ];
    }
}
