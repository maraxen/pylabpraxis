import { TestBed } from '@angular/core/testing';
import { LinkedSelectorService } from './linked-selector.service';
import { take } from 'rxjs/operators';
import { describe, it, expect, beforeEach } from 'vitest';

describe('LinkedSelectorService', () => {
    let service: LinkedSelectorService;

    beforeEach(() => {
        TestBed.configureTestingModule({});
        service = TestBed.inject(LinkedSelectorService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    it('should register and unregister selectors', () => {
        const linkId = 'group1';
        const selectorId = 'sel1';

        service.registerSelector(linkId, selectorId);
        expect(service.getLinkGroupSize(linkId)).toBe(1);

        service.unregisterSelector(linkId, selectorId);
        expect(service.getLinkGroupSize(linkId)).toBe(0);
    });

    it('should identify linked groups', () => {
        const linkId = 'group1';

        // 0 selectors
        expect(service.isLinked(linkId)).toBe(false);

        // 1 selector
        service.registerSelector(linkId, 'sel1');
        expect(service.isLinked(linkId)).toBe(false); // Needs > 1 to be "linked"

        // 2 selectors
        service.registerSelector(linkId, 'sel2');
        expect(service.isLinked(linkId)).toBe(true);
    });

    it('should broadcast selection changes', () => {
        const linkId = 'group1';
        const sourceId = 'source';
        const destId = 'dest';
        const indices = [1, 2, 3];

        service.registerSelector(linkId, sourceId);
        service.registerSelector(linkId, destId);

        let receivedIndices: number[] = [];
        service.getSelection$(linkId, destId).subscribe(val => {
            receivedIndices = val;
        });

        service.updateSelection(linkId, sourceId, indices);

        expect(receivedIndices).toEqual(indices);
    });

    it('should filter out self-updates', () => {
        const linkId = 'group1';
        const sourceId = 'source';
        const indices = [1, 2, 3];

        service.registerSelector(linkId, sourceId);

        const receivedValues: number[][] = [];
        service.getSelection$(linkId, sourceId).subscribe(val => {
            receivedValues.push(val);
        });

        // Initial value should be received (empty array)
        expect(receivedValues.length).toBe(1);
        expect(receivedValues[0]).toEqual([]);

        // Update from self
        service.updateSelection(linkId, sourceId, indices);

        // Should NOT receive the update
        expect(receivedValues.length).toBe(1);
    });

    it('should maintain current selection state', () => {
        const linkId = 'group1';
        const indices = [1, 2, 3];

        service.registerSelector(linkId, 'sel1');
        service.updateSelection(linkId, 'sel1', indices);

        expect(service.getCurrentSelection(linkId)).toEqual(indices);
    });
});
