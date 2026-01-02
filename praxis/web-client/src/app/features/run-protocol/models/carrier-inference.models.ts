import { PlrResource } from '@core/models/plr.models';
import { DeckCarrier, CarrierSlot, CarrierType } from './deck-layout.models';

/**
 * Result of carrier inference for a resource type.
 */
export interface CarrierRequirement {
    /** The resource type (e.g., 'Plate', 'TipRack') */
    resourceType: string;
    /** Number of carriers needed */
    count: number;
    /** FQN of the recommended carrier */
    carrierFqn: string;
    /** Carrier type */
    carrierType: CarrierType;
    /** Display name of the carrier */
    carrierName: string;
    /** Total slots needed for this resource type */
    slotsNeeded: number;
    /** Total slots available with the recommended carriers */
    slotsAvailable: number;
    /** Suggested rail positions for placement */
    suggestedRails: number[];
    /** Whether user has confirmed placement */
    placed: boolean;
}

/**
 * Assignment of a resource to a specific slot.
 */
export interface SlotAssignment {
    /** The resource being placed */
    resource: PlrResource;
    /** The slot it's assigned to */
    slot: CarrierSlot;
    /** The carrier containing the slot */
    carrier: DeckCarrier;
    /** Order in placement sequence (for z-axis ordering) */
    placementOrder: number;
    /** Whether user has confirmed placement */
    placed: boolean;
    /** The accession ID of the physical asset assigned to this slot */
    assignedAssetId?: string;
}

/**
 * Hint for stacking order when multiple resources share a slot.
 */
export interface StackingHint {
    /** Slot ID where stacking occurs */
    slotId: string;
    /** Order of resources (bottom to top) */
    order: string[];
    /** Reason for this stacking order */
    reason: string;
}

/**
 * Complete deck setup result.
 */
export interface DeckSetupResult {
    /** Carrier requirements */
    carrierRequirements: CarrierRequirement[];
    /** Resource-to-slot assignments */
    slotAssignments: SlotAssignment[];
    /** Stacking hints for complex placements */
    stackingHints: StackingHint[];
    /** Whether setup is complete */
    complete: boolean;
}
