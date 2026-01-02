import { Injectable } from '@angular/core';
import {
    DeckConfiguration,
    DeckRail,
    DeckCarrier,
    CarrierSlot,
    DeckDefinitionSpec,
    CarrierDefinition,
    CarrierType
} from '../models/deck-layout.models';

/**
 * Service for fetching deck and carrier specifications.
 * 
 * Currently provides hardcoded Hamilton STAR specifications.
 * Future: Will integrate with SqliteService/API for dynamic deck definitions.
 */
@Injectable({
    providedIn: 'root'
})
export class DeckCatalogService {

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
     * Get deck definition specification by FQN.
     */
    getDeckDefinition(fqn: string): DeckDefinitionSpec | null {
        if (fqn === 'pylabrobot.resources.hamilton.HamiltonSTARDeck' ||
            fqn === 'HamiltonSTARDeck') {
            return this.getHamiltonSTARSpec();
        }
        return null;
    }

    /**
     * Get all available carriers compatible with a deck type.
     */
    getCompatibleCarriers(deckFqn: string): CarrierDefinition[] {
        // For now, return standard Hamilton carriers for any Hamilton deck
        if (deckFqn.includes('Hamilton') || deckFqn.includes('STAR')) {
            return this.getHamiltonCarriers();
        }
        return [];
    }

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
            numRails: spec.numRails
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

        for (let i = 0; i < spec.numRails; i++) {
            rails.push({
                index: i,
                xPosition: positions[i],
                width: spec.railSpacing,
                compatibleCarrierTypes: spec.compatibleCarriers
            });
        }

        return rails;
    }

    private calculateRailPositions(spec: DeckDefinitionSpec): number[] {
        const positions: number[] = [];
        for (let i = 0; i < spec.numRails; i++) {
            positions.push(this.HAMILTON_STAR_RAIL_OFFSET + (i * spec.railSpacing));
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
