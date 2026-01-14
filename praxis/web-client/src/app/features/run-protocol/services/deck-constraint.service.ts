import { Injectable } from '@angular/core';
import { PlrResource } from '@core/models/plr.models';
import { DeckRail, DeckSlotSpec } from '@features/run-protocol/models/deck-layout.models';

export interface ValidationResult {
    valid: boolean;
    reason?: string;
    warning?: string;
}

@Injectable({
    providedIn: 'root'
})
export class DeckConstraintService {

    constructor() { }

    /**
     * Validate if a resource can be dropped onto a specific target (Slot or Rail).
     * 
     * @param resource The resource being dragged (e.g., a Plate or TipRack).
     * @param target The drop target (Slot specification or Rail definition).
     * @param rootDeck The root deck resource (to check context if needed).
     * @returns ValidationResult
     */
    validateDrop(
        resource: PlrResource,
        target: DeckSlotSpec | DeckRail,
        rootDeck: PlrResource
    ): ValidationResult {

        // 1. Basic Type Check
        if (this.isRail(target)) {
            return this.validateRailDrop(resource, target as DeckRail);
        } else {
            return this.validateSlotDrop(resource, target as DeckSlotSpec);
        }
    }

    private validateRailDrop(resource: PlrResource, rail: DeckRail): ValidationResult {
        // Check if the resource is a Carrier (compatible with rails)
        if (!resource.type.includes('Carrier')) {
            // Exception: Some PLR models put plates directly on rails, but usually via a carrier.
            // For now, enforce Carrier-only on Rails unless specific exceptions exist.
            return { valid: false, reason: `Only Carriers can be placed directly on Rails.` };
        }

        // Check compatibility list if available
        if (rail.compatibleCarrierTypes && rail.compatibleCarrierTypes.length > 0) {
            const isCompatible = rail.compatibleCarrierTypes.some(t => resource.type.includes(t));
            if (!isCompatible) {
                return { valid: false, reason: `Carrier '${resource.type}' is not compatible with this rail.` };
            }
        }

        return { valid: true };
    }

    private validateSlotDrop(resource: PlrResource, slot: DeckSlotSpec): ValidationResult {
        // Check slot type restrictions
        if (slot.slotType === 'trash' && !resource.type.toLowerCase().includes('trash')) {
            return { valid: false, reason: 'Only Trash containers can be placed in Trash slots.' };
        }

        // Check dimensions (basic box fitting)
        if (slot.dimensions) {
            // Allow some tolerance (e.g. 1mm)
            const fitsX = resource.size_x <= slot.dimensions.width + 1;
            const fitsY = resource.size_y <= slot.dimensions.height + 1;

            if (!fitsX || !fitsY) {
                return { valid: false, reason: `Resource is too large for this slot.` };
            }
        }

        return { valid: true };
    }

    private isRail(target: any): boolean {
        return 'xPosition' in target && 'compatibleCarrierTypes' in target;
    }
}
