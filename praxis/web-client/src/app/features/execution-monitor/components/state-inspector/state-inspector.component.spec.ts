import { ComponentFixture, TestBed } from '@angular/core/testing';
import { StateInspectorComponent } from './state-inspector.component';
import { StateSnapshot } from '@core/models/simulation.models';

describe('StateInspectorComponent', () => {
    let component: StateInspectorComponent;
    let fixture: ComponentFixture<StateInspectorComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [StateInspectorComponent]
        }).compileComponents();

        fixture = TestBed.createComponent(StateInspectorComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should compute state diff correctly for volumes', () => {
        const before: StateSnapshot = {
            tips: { tips_loaded: false, tips_count: 0 },
            liquids: {
                'Plate1': { 'A1': 0 }
            },
            on_deck: []
        };

        const after: StateSnapshot = {
            tips: { tips_loaded: false, tips_count: 0 },
            liquids: {
                'Plate1': { 'A1': 50 }
            },
            on_deck: []
        };

        // @ts-ignore - accessing private method for test
        const diffs = component.computeStateDiff(before, after);

        expect(diffs.length).toBe(1);
        expect(diffs[0].key).toBe('liquids.Plate1.A1');
        expect(diffs[0].before).toBe('0µL');
        expect(diffs[0].after).toBe('50µL');
        expect(diffs[0].direction).toBe('increase');
    });

    it('should detect tip changes', () => {
        const before: StateSnapshot = {
            tips: { tips_loaded: false, tips_count: 0 },
            liquids: {},
            on_deck: []
        };

        const after: StateSnapshot = {
            tips: { tips_loaded: true, tips_count: 1 },
            liquids: {},
            on_deck: []
        };

        // @ts-ignore
        const diffs = component.computeStateDiff(before, after);

        expect(diffs.some(d => d.key === 'tips.tips_loaded')).toBe(true);
        expect(diffs.some(d => d.key === 'tips.tips_count')).toBe(true);
    });
});
