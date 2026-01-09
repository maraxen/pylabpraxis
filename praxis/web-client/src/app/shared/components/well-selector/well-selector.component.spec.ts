import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WellSelectorComponent } from './well-selector.component';

describe('WellSelectorComponent', () => {
    let component: WellSelectorComponent;
    let fixture: ComponentFixture<WellSelectorComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [WellSelectorComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(WellSelectorComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should generate correct row and column labels', () => {
        expect(component.rowLabels().length).toBe(8);
        expect(component.rowLabels()[0]).toBe('A');
        expect(component.colLabels().length).toBe(12);
    });

    it('should toggle selection on click', () => {
        const well = 'A1';
        component.onMouseDown(well, { button: 0, preventDefault: () => { } } as MouseEvent);
        component.onMouseUp();

        expect(component.isSelected(well)).toBe(true);

        component.onMouseDown(well, { button: 0, preventDefault: () => { } } as MouseEvent);
        component.onMouseUp();

        expect(component.isSelected(well)).toBe(false);
    });

    it('should clear selection', () => {
        component.onMouseDown('A1', { button: 0, preventDefault: () => { } } as MouseEvent);
        expect(component.isSelected('A1')).toBe(true);

        component.clearSelection();
        expect(component.isSelected('A1')).toBe(false);
    });

    it('should invert selection', () => {
        component.rows = 2; // A, B
        component.cols = 2; // 1, 2
        fixture.detectChanges(); // Trigger computed updates if mechanism requires (signals are auto but effect might need cycle, here logic is direct)

        // Total 4 wells: A1, A2, B1, B2

        component.onMouseDown('A1', { button: 0, preventDefault: () => { } } as MouseEvent);
        expect(component.isSelected('A1')).toBe(true);

        component.invertSelection();

        expect(component.isSelected('A1')).toBe(false);
        expect(component.isSelected('A2')).toBe(true);
        expect(component.isSelected('B1')).toBe(true);
        expect(component.isSelected('B2')).toBe(true);
    });
});
