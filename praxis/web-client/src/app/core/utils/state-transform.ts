/**
 * State transformation utilities for converting PyLabRobot state to frontend format.
 *
 * This is a TypeScript port of praxis/backend/core/state_transform.py
 * for use in browser mode where state comes directly from Pyodide.
 */

import type { StateSnapshot, TipStateSnapshot, WellVolumeMap } from '../models/simulation.models';

/**
 * Raw PyLabRobot state format from serialize_all_state()
 */
export type PlrState = Record<string, PlrResourceState>;

export interface PlrResourceState {
    // TipTracker format (LiquidHandler channels)
    head_state?: Record<string, { tip: unknown | null; tip_state: unknown; pending_tip: unknown }>;

    // VolumeTracker format (Container/Well)
    volume?: number;
    pending_volume?: number;
    thing?: string;
    max_volume?: number;

    // Other resource properties
    [key: string]: unknown;
}

/**
 * Extract tip state from PLR state.
 *
 * Searches for liquid handler state (identified by "head_state" key) and counts
 * how many channels have tips loaded.
 */
export function extractTipState(plrState: PlrState): TipStateSnapshot {
    let tipsLoaded = false;
    let tipsCount = 0;

    for (const resourceState of Object.values(plrState)) {
        if (typeof resourceState !== 'object' || resourceState === null) {
            continue;
        }

        // Check for liquid handler state (has "head_state" key)
        if ('head_state' in resourceState && resourceState.head_state) {
            const headState = resourceState.head_state;

            if (typeof headState === 'object') {
                for (const channelState of Object.values(headState)) {
                    if (
                        typeof channelState === 'object' &&
                        channelState !== null &&
                        'tip' in channelState &&
                        (channelState as any).tip !== null
                    ) {
                        tipsCount++;
                    }
                }
            }

            tipsLoaded = tipsCount > 0;
            break; // Only one liquid handler expected
        }
    }

    return { tips_loaded: tipsLoaded, tips_count: tipsCount };
}

/**
 * Extract liquid volumes from PLR state.
 *
 * Searches for resources with VolumeTracker state (identified by "volume" key)
 * and organizes them by parent resource (plate) and well identifier.
 */
export function extractLiquidVolumes(plrState: PlrState): Record<string, WellVolumeMap> {
    const liquids: Record<string, WellVolumeMap> = {};

    for (const [resourceName, resourceState] of Object.entries(plrState)) {
        if (typeof resourceState !== 'object' || resourceState === null) {
            continue;
        }

        // Check for volume tracker state (has "volume" key)
        if ('volume' in resourceState && typeof resourceState.volume === 'number') {
            const volume = resourceState.volume;

            // Only include resources with non-zero volume
            if (volume > 0) {
                const parentName = inferParentName(resourceName);
                const wellId = inferWellId(resourceName);

                if (!liquids[parentName]) {
                    liquids[parentName] = {};
                }

                liquids[parentName][wellId] = volume;
            }
        }
    }

    return liquids;
}

/**
 * Infer parent plate name from well resource name.
 *
 * Common naming patterns:
 * - "plate_name_A1" -> "plate_name"
 * - "source_plate_well_A1" -> "source_plate"
 * - "A1" -> "unknown_plate"
 */
export function inferParentName(resourceName: string): string {
    // Pattern: anything ending in _[A-P][1-24] or _well_[A-P][1-24]
    const match = resourceName.match(/^(.+?)(?:_well)?_([A-P]\d{1,2})$/i);
    if (match) {
        return match[1];
    }

    // If no pattern match, check if it looks like a standalone well ID
    if (/^[A-P]\d{1,2}$/i.test(resourceName)) {
        return 'unknown_plate';
    }

    // Otherwise, treat the whole name as the resource identifier
    return resourceName;
}

/**
 * Infer well ID from resource name.
 */
export function inferWellId(resourceName: string): string {
    // Pattern: extract [A-P][1-24] from end of name
    const match = resourceName.match(/([A-P]\d{1,2})$/i);
    if (match) {
        return match[1].toUpperCase();
    }

    return resourceName;
}

/**
 * Get list of resource names currently on deck.
 */
export function getOnDeckResources(plrState: PlrState): string[] {
    return Object.keys(plrState);
}

/**
 * Transform PyLabRobot state to frontend StateSnapshot format.
 *
 * This is the main entry point for state transformation.
 */
export function transformPlrState(plrState: PlrState | null | undefined): StateSnapshot | null {
    if (!plrState || Object.keys(plrState).length === 0) {
        return null;
    }

    const tipState = extractTipState(plrState);
    const liquids = extractLiquidVolumes(plrState);
    const onDeck = getOnDeckResources(plrState);

    return {
        tips: tipState,
        liquids,
        on_deck: onDeck,
        raw_plr_state: plrState,
    };
}
