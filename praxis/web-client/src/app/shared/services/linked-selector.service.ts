import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { filter, map } from 'rxjs/operators';

/**
 * State of a linked selector group.
 */
export interface LinkedSelectorState {
    /** The link group ID */
    linkId: string;
    /** Currently selected indices (flat) */
    selectedIndices: number[];
    /** Source selector ID that triggered the change */
    sourceId: string;
    /** Timestamp of last update */
    timestamp: number;
}

/**
 * Service for managing linked index selectors.
 * 
 * When multiple selectors share the same `linkId`, selecting in one
 * automatically updates the others. Useful for:
 * - Source ↔ Destination wells
 * - Tips ↔ Wells
 * - Any paired selections
 */
@Injectable({
    providedIn: 'root'
})
export class LinkedSelectorService {
    private readonly linkGroups = new Map<string, BehaviorSubject<LinkedSelectorState>>();
    private readonly selectorRegistry = new Map<string, Set<string>>();

    /**
     * Register a selector with a link group.
     * @param linkId The link group ID
     * @param selectorId Unique ID for this selector instance
     */
    registerSelector(linkId: string, selectorId: string): void {
        if (!this.selectorRegistry.has(linkId)) {
            this.selectorRegistry.set(linkId, new Set());
        }
        this.selectorRegistry.get(linkId)!.add(selectorId);

        if (!this.linkGroups.has(linkId)) {
            this.linkGroups.set(linkId, new BehaviorSubject<LinkedSelectorState>({
                linkId,
                selectedIndices: [],
                sourceId: '',
                timestamp: 0
            }));
        }
    }

    /**
     * Unregister a selector from a link group.
     * @param linkId The link group ID
     * @param selectorId Unique ID for this selector instance
     */
    unregisterSelector(linkId: string, selectorId: string): void {
        const group = this.selectorRegistry.get(linkId);
        if (group) {
            group.delete(selectorId);
            if (group.size === 0) {
                this.selectorRegistry.delete(linkId);
                this.linkGroups.get(linkId)?.complete();
                this.linkGroups.delete(linkId);
            }
        }
    }

    /**
     * Update the selection for a link group.
     * @param linkId The link group ID
     * @param selectorId The selector that triggered the update
     * @param indices The new selected indices
     */
    updateSelection(linkId: string, selectorId: string, indices: number[]): void {
        const subject = this.linkGroups.get(linkId);
        if (subject) {
            subject.next({
                linkId,
                selectedIndices: [...indices],
                sourceId: selectorId,
                timestamp: Date.now()
            });
        }
    }

    /**
     * Get an observable for selection changes in a link group.
     * Filters out updates from the requesting selector to avoid loops.
     * @param linkId The link group ID
     * @param selectorId The requesting selector's ID (optional, to filter self-updates)
     */
    getSelection$(linkId: string, selectorId?: string): Observable<number[]> {
        const subject = this.linkGroups.get(linkId);
        if (!subject) {
            return new BehaviorSubject<number[]>([]).asObservable();
        }

        return subject.pipe(
            // Filter out updates from the same selector to prevent loops
            filter(state => !selectorId || state.sourceId !== selectorId),
            map(state => state.selectedIndices)
        );
    }

    /**
     * Get the current selection for a link group.
     * @param linkId The link group ID
     */
    getCurrentSelection(linkId: string): number[] {
        return this.linkGroups.get(linkId)?.value.selectedIndices ?? [];
    }

    /**
     * Check if a link group exists and has multiple selectors.
     * @param linkId The link group ID
     */
    isLinked(linkId: string): boolean {
        const group = this.selectorRegistry.get(linkId);
        return !!group && group.size > 1;
    }

    /**
     * Get the number of selectors in a link group.
     * @param linkId The link group ID
     */
    getLinkGroupSize(linkId: string): number {
        return this.selectorRegistry.get(linkId)?.size ?? 0;
    }
}
