/**
 * Category inference utility for PLR resources.
 *
 * IMPORTANT: This is a FALLBACK mechanism. The preferred approach is:
 * 1. Use plr_category from the backend (populated from PLR class .category attribute)
 * 2. Only use this function when backend data is unavailable
 *
 * This function uses the canonical PLRCategory enum values.
 */

import { PLRCategory } from '@app/core/db/plr-category';
import { ResourceDefinition } from '../models/asset.models';

export function inferCategory(def: ResourceDefinition): string {
    // Primary: Use backend-provided category (from PLR class .category attribute)
    if (def.plr_category && def.plr_category !== '' && def.plr_category !== 'Other' && def.plr_category !== 'null') {
        return def.plr_category;
    }

    // Secondary: Fallback to resource_type if available
    if ((def as any).resource_type && (def as any).resource_type !== '') {
        return (def as any).resource_type;
    }

    // Tertiary: FQN inference (BRITTLE - avoid when possible)
    // These use canonical PLRCategory enum values
    if (def.fqn) {
        const lowerFqn = def.fqn.toLowerCase();
        if (lowerFqn.includes('plate') && !lowerFqn.includes('carrier') && !lowerFqn.includes('reader')) {
            return PLRCategory.PLATE;
        }
        if (lowerFqn.includes('tip_rack') || lowerFqn.includes('tiprack')) {
            return PLRCategory.TIP_RACK;
        }
        if (lowerFqn.includes('trough') || lowerFqn.includes('reservoir')) {
            return PLRCategory.TROUGH;
        }
        if (lowerFqn.includes('carrier')) {
            return PLRCategory.CARRIER;
        }
        if (lowerFqn.includes('tube') && !lowerFqn.includes('rack')) {
            return PLRCategory.TUBE;
        }
        if (lowerFqn.includes('tuberack') || (lowerFqn.includes('tube') && lowerFqn.includes('rack'))) {
            return PLRCategory.TUBE_RACK;
        }
        if (lowerFqn.includes('lid')) {
            return PLRCategory.LID;
        }
        if (lowerFqn.includes('trash')) {
            return 'Trash'; // Not a canonical PLR category
        }
    }

    return 'Other';
}
