
import { ResourceDefinition } from '../models/asset.models';

export function inferCategory(def: ResourceDefinition): string {
    // If explicitly set, use it
    if (def.plr_category && def.plr_category !== '' && def.plr_category !== 'Other' && def.plr_category !== 'null') {
        return def.plr_category;
    }

    // Fallback to resource_type
    if ((def as any).resource_type && (def as any).resource_type !== '') {
        return (def as any).resource_type;
    }

    // Fallback to FQN inference
    if (def.fqn) {
        const lowerFqn = def.fqn.toLowerCase();
        if (lowerFqn.includes('plate')) return 'Plate';
        if (lowerFqn.includes('tip_rack') || lowerFqn.includes('tiprack')) return 'TipRack';
        if (lowerFqn.includes('trough') || lowerFqn.includes('reservoir')) return 'Trough';
        if (lowerFqn.includes('carrier')) return 'Carrier';
        if (lowerFqn.includes('tube')) return 'Tube';
        if (lowerFqn.includes('lid')) return 'Lid';
        if (lowerFqn.includes('trash')) return 'Trash';
    }

    return 'Other';
}
