/**
 * Semantic parser for PLR resource names.
 * 
 * Extracts meaningful attributes from resource names/FQNs like:
 *   opentrons_96_aluminumblock_generic_pcr_strip_200ul
 *   → vendor: Opentrons, itemCount: 96, volumeUl: 200, displayName: "PCR Strip"
 */

import { ResourceDefinition } from '../models/asset.models';

export interface ParsedResourceInfo {
    /** Vendor/manufacturer (e.g., "Opentrons", "Corning", "Hamilton") */
    vendor: string | null;

    /** Number of items (wells, tips, slots, tubes) */
    itemCount: number | null;

    /** Volume in microliters */
    volumeUl: number | null;

    /** Human-readable display name (e.g., "PCR Strip", "Deep Well Plate") */
    displayName: string | null;

    /** Bottom type for plates (e.g., "Flat", "Round", "V-bottom") */
    bottomType: string | null;

    /** Slot type for carriers (e.g., "Plate", "TipRack", "Trough") */
    slotType: string | null;

    /** Raw PLR name for fallback display */
    rawName: string;
}

// Known vendor prefixes (lowercase for matching)
const VENDOR_PREFIXES: Record<string, string> = {
    'cor': 'Corning',
    'corning': 'Corning',
    'opentrons': 'Opentrons',
    'hamilton': 'Hamilton',
    'greiner': 'Greiner',
    'bld': 'Bio-Rad',
    'biorad': 'Bio-Rad',
    'thermo': 'Thermo Fisher',
    'nunc': 'Nunc',
    'falcon': 'Falcon',
    'eppendorf': 'Eppendorf',
    'axygen': 'Axygen',
    'tecan': 'Tecan',
    'azenta': 'Azenta',
    'nest': 'Nest',
    'sarstedt': 'Sarstedt',
    'revvity': 'Revvity',
    'porvair': 'Porvair',
    'agilent': 'Agilent',
    'beckman': 'Beckman Coulter',
};

// Bottom type codes
const BOTTOM_TYPES: Record<string, string> = {
    'fb': 'Flat',
    'flat': 'Flat',
    'rb': 'Round',
    'rd': 'Round',
    'round': 'Round',
    'vb': 'V-Bottom',
    'v': 'V-Bottom',
    'conical': 'V-Bottom',
    'u': 'U-Bottom',
    'ub': 'U-Bottom',
};

// Slot types for carriers
const SLOT_TYPE_KEYWORDS: Record<string, string> = {
    'plate': 'Plate',
    'plt': 'Plate',
    'tip': 'TipRack',
    'tiprack': 'TipRack',
    'ntr': 'TipRack',  // Hamilton NTR = Nested Tip Rack
    'trough': 'Trough',
    'reservoir': 'Trough',
    'tube': 'TubeRack',
};

// Terms to exclude from display name (common boilerplate)
const EXCLUDE_FROM_DISPLAY = new Set([
    'wellplate', 'well', 'plate', 'tiprack', 'tip', 'rack', 'carrier',
    'generic', 'standard', 'custom', 'module', 'nest', 'holder',
    'ul', 'ml', 'l',  // volume units
]);

// Semantic display name mappings
const SEMANTIC_NAMES: Record<string, string> = {
    'pcr_strip': 'PCR Strip',
    'pcr': 'PCR Plate',
    'deepwell': 'Deep Well',
    'deep_well': 'Deep Well',
    'skirted': 'Skirted Plate',
    'half_skirted': 'Half-Skirted Plate',
    'unskirted': 'Unskirted Plate',
    'reservoir': 'Reservoir',
    'aluminumblock': 'Aluminum Block',
    'aluminum_block': 'Aluminum Block',
    'cooling_block': 'Cooling Block',
    'microplate': 'Microplate',
    'filter': 'Filter Plate',
    'storage': 'Storage Plate',
};

/**
 * Parse a resource name to extract semantic information.
 * Priority:
 *   1. Use structured metadata from ResourceDefinition
 *   2. Parse name/FQN for missing info
 */
export function parseResourceInfo(def: ResourceDefinition): ParsedResourceInfo {
    const rawName = def.name || def.fqn?.split('.').pop() || 'Unknown';
    const fqn = def.fqn || '';
    const nameLower = rawName.toLowerCase();
    const parts = nameLower.split(/[_\-\s]+/);

    // Extract from structured metadata first
    let vendor = def.vendor || null;
    let itemCount = def.num_items || null;
    let volumeUl = def.well_volume_ul || def.tip_volume_ul || null;
    let bottomType: string | null = null;
    let slotType: string | null = null;
    let displayName: string | null = null;

    // Parse name for missing info
    for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        const nextPart = parts[i + 1] || '';

        // Vendor detection (first part usually)
        if (!vendor && i === 0 && VENDOR_PREFIXES[part]) {
            vendor = VENDOR_PREFIXES[part];
            continue;
        }

        // Item count (number followed by optional descriptive word)
        if (!itemCount && /^\d+$/.test(part)) {
            const num = parseInt(part, 10);
            // Common well/tip counts: 6, 12, 24, 48, 96, 384, 1536
            if ([6, 12, 24, 48, 96, 384, 1536].includes(num) || num <= 20) {
                itemCount = num;
                continue;
            }
        }

        // Volume detection (number followed by ul/ml)
        if (!volumeUl) {
            const volumeMatch = part.match(/^(\d+)(ul|ml)?$/);
            if (volumeMatch && (volumeMatch[2] || nextPart === 'ul' || nextPart === 'ml')) {
                let vol = parseInt(volumeMatch[1], 10);
                if (nextPart === 'ml' || volumeMatch[2] === 'ml') {
                    vol *= 1000; // Convert ml to ul
                }
                if (vol > 0 && vol <= 100000) { // Reasonable volume range
                    volumeUl = vol;
                    if (nextPart === 'ul' || nextPart === 'ml') i++; // Skip next part
                    continue;
                }
            }
        }

        // Bottom type detection
        if (!bottomType && BOTTOM_TYPES[part]) {
            bottomType = BOTTOM_TYPES[part];
            continue;
        }

        // Slot type detection (for carriers)
        if (!slotType && SLOT_TYPE_KEYWORDS[part]) {
            slotType = SLOT_TYPE_KEYWORDS[part];
            continue;
        }

        // Semantic name detection
        if (!displayName) {
            // Check for multi-word semantic names
            const twoWord = `${part}_${nextPart}`;
            if (SEMANTIC_NAMES[twoWord]) {
                displayName = SEMANTIC_NAMES[twoWord];
                i++; // Skip next part
                continue;
            }
            if (SEMANTIC_NAMES[part]) {
                displayName = SEMANTIC_NAMES[part];
                continue;
            }
        }
    }

    // Build display name from remaining meaningful parts if not found
    if (!displayName) {
        const meaningfulParts = parts.filter(p =>
            !EXCLUDE_FROM_DISPLAY.has(p) &&
            !/^\d+$/.test(p) &&
            !VENDOR_PREFIXES[p] &&
            p.length > 1
        );
        if (meaningfulParts.length > 0) {
            displayName = meaningfulParts
                .slice(0, 3) // Limit to 3 words
                .map(p => p.charAt(0).toUpperCase() + p.slice(1))
                .join(' ');
        }
    }

    return {
        vendor,
        itemCount,
        volumeUl,
        displayName,
        bottomType,
        slotType,
        rawName,
    };
}

/**
 * Get the best display name for a resource.
 * Returns parsed displayName, or falls back to raw name.
 */
export function getDisplayLabel(def: ResourceDefinition): string {
    const info = parseResourceInfo(def);
    return info.displayName || info.rawName;
}

/**
 * Format volume for display.
 * e.g., 200 → "200µL", 2000 → "2mL"
 */
export function formatVolume(volumeUl: number | null | undefined): string | null {
    if (!volumeUl) return null;
    if (volumeUl >= 1000) {
        return `${volumeUl / 1000}mL`;
    }
    return `${volumeUl}µL`;
}

/**
 * Format item count for display with appropriate label.
 * e.g., (96, 'Plate') → "96-well", (96, 'TipRack') → "96 tips"
 */
export function formatItemCount(count: number | null | undefined, category: string): string | null {
    if (!count) return null;
    const catLower = category.toLowerCase();
    if (catLower.includes('plate') || catLower.includes('well')) {
        return `${count}-well`;
    }
    if (catLower.includes('tip')) {
        return `${count} tips`;
    }
    if (catLower.includes('carrier')) {
        return `${count} slots`;
    }
    if (catLower.includes('tube') || catLower.includes('rack')) {
        return `${count} positions`;
    }
    return `${count} items`;
}
