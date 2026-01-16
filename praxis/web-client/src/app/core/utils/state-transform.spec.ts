/**
 * Unit tests for state transformation utilities
 */
import {
    extractTipState,
    extractLiquidVolumes,
    inferParentName,
    inferWellId,
    transformPlrState
} from './state-transform';
import { describe, it, expect } from 'vitest';

describe('State Transformation Utils', () => {

    describe('extractTipState', () => {
        it('should correctly identify when tips are loaded', () => {
            const plrState = {
                'head': {
                    head_state: {
                        '0': { tip: { has_tip: true }, tip_state: {}, pending_tip: null }
                    }
                }
            };

            const result = extractTipState(plrState);
            expect(result.tips_loaded).toBe(true);
            expect(result.tips_count).toBe(1);
        });

        it('should correctly identify when no tips are loaded', () => {
            const plrState = {
                'head': {
                    head_state: {
                        '0': { tip: null, tip_state: {}, pending_tip: null }
                    }
                }
            };

            const result = extractTipState(plrState);
            expect(result.tips_loaded).toBe(false);
            expect(result.tips_count).toBe(0);
        });
    });

    describe('extractLiquidVolumes', () => {
        it('should extract volumes from resources with volume tracker', () => {
            const plrState = {
                'plate_A1': { volume: 100 },
                'plate_A2': { volume: 0 },
                'plate_B1': { volume: 50 }
            };

            const result = extractLiquidVolumes(plrState);

            expect(result['plate']['A1']).toBe(100);
            expect(result['plate']['B1']).toBe(50);
            expect(result['plate']['A2']).toBeUndefined();
        });
    });

    describe('Naming Inference', () => {
        it('should infer parent name correctly', () => {
            expect(inferParentName('source_plate_A1')).toBe('source_plate');
            expect(inferParentName('dest_plate_well_B2')).toBe('dest_plate');
        });

        it('should infer well ID correctly', () => {
            expect(inferWellId('source_plate_A1')).toBe('A1');
            expect(inferWellId('dest_plate_well_B2')).toBe('B2');
        });
    });

    describe('transformPlrState', () => {
        it('should transform complete state correctly', () => {
            const plrState = {
                'head': {
                    head_state: {
                        '0': { tip: {}, tip_state: {}, pending_tip: null }
                    }
                },
                'plate_A1': { volume: 100 }
            };

            const result = transformPlrState(plrState);

            expect(result).toBeTruthy();
            if (result) {
                expect(result.tips.tips_loaded).toBe(true);
                expect(result.liquids['plate']['A1']).toBe(100);
                expect(result.on_deck).toContain('head');
                expect(result.on_deck).toContain('plate_A1');
            }
        });

        it('should return null for empty or null state', () => {
            expect(transformPlrState(null)).toBeNull();
            expect(transformPlrState({})).toBeNull();
        });
    });
});
