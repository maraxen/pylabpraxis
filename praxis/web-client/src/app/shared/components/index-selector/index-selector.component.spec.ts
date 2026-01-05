import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { IndexSelectorComponent } from './index-selector.component';

describe('IndexSelectorComponent', () => {
    let component: IndexSelectorComponent;
    let fixture: ComponentFixture<IndexSelectorComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [IndexSelectorComponent, NoopAnimationsModule],
        }).compileComponents();

        fixture = TestBed.createComponent(IndexSelectorComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    describe('Grid initialization', () => {
        it('should initialize with default 96-well spec (12x8)', () => {
            expect(component.rows.length).toBe(8);
            expect(component.columns.length).toBe(12);
        });

        it('should initialize with custom spec', () => {
            component.spec = { itemsX: 6, itemsY: 4 };
            component.ngOnChanges({
                spec: {
                    currentValue: component.spec,
                    previousValue: null,
                    firstChange: true,
                    isFirstChange: () => true,
                },
            });

            expect(component.rows.length).toBe(4);
            expect(component.columns.length).toBe(6);
        });

        it('should generate correct row labels', () => {
            expect(component.rows[0]).toBe('A');
            expect(component.rows[7]).toBe('H');
        });
    });

    describe('Selection', () => {
        it('should emit selected indices on selection', () => {
            const spy = vi.spyOn(component.selectionChange, 'emit');

            // Simulate clicking a cell
            component.onCellClick(0, 0, new MouseEvent('click'));

            expect(spy).toHaveBeenCalled();
            const emittedIndices = spy.mock.calls[0][0];
            expect(emittedIndices).toContain(0);
        });

        it('should emit well IDs on selection', () => {
            const spy = vi.spyOn(component.wellIdsChange, 'emit');

            component.onCellClick(0, 0, new MouseEvent('click'));

            expect(spy).toHaveBeenCalled();
            const emittedWellIds = spy.mock.calls[0][0];
            expect(emittedWellIds).toContain('A1');
        });

        it('should select all cells on selectAll', () => {
            component.selectAll();

            const totalCells = component.spec.itemsX * component.spec.itemsY;
            let selectedCount = 0;
            for (let r = 0; r < component.spec.itemsY; r++) {
                for (let c = 0; c < component.spec.itemsX; c++) {
                    if (component.selectionGrid[r][c]) selectedCount++;
                }
            }

            expect(selectedCount).toBe(totalCells);
        });

        it('should clear selection on clearSelection', () => {
            component.selectAll();
            component.clearSelection();

            let selectedCount = 0;
            for (let r = 0; r < component.spec.itemsY; r++) {
                for (let c = 0; c < component.spec.itemsX; c++) {
                    if (component.selectionGrid[r][c]) selectedCount++;
                }
            }

            expect(selectedCount).toBe(0);
        });

        it('should select entire row on selectRow', () => {
            component.selectRow(0);

            let rowSelectedCount = 0;
            for (let c = 0; c < component.spec.itemsX; c++) {
                if (component.selectionGrid[0][c]) rowSelectedCount++;
            }

            expect(rowSelectedCount).toBe(component.spec.itemsX);
        });

        it('should select entire column on selectColumn', () => {
            component.selectColumn(0);

            let colSelectedCount = 0;
            for (let r = 0; r < component.spec.itemsY; r++) {
                if (component.selectionGrid[r][0]) colSelectedCount++;
            }

            expect(colSelectedCount).toBe(component.spec.itemsY);
        });
    });

    describe('Well ID conversion', () => {
        it('should return correct well ID', () => {
            expect(component.getWellId(0, 0)).toBe('A1');
            expect(component.getWellId(0, 11)).toBe('A12');
            expect(component.getWellId(7, 0)).toBe('H1');
            expect(component.getWellId(7, 11)).toBe('H12');
        });
    });

    describe('Single selection mode', () => {
        beforeEach(() => {
            component.mode = 'single';
        });

        it('should only allow one selection at a time', () => {
            component.onCellClick(0, 0, new MouseEvent('click'));
            component.onCellClick(1, 1, new MouseEvent('click'));

            let selectedCount = 0;
            for (let r = 0; r < component.spec.itemsY; r++) {
                for (let c = 0; c < component.spec.itemsX; c++) {
                    if (component.selectionGrid[r][c]) selectedCount++;
                }
            }

            expect(selectedCount).toBe(1);
            expect(component.selectionGrid[1][1]).toBe(true);
        });
    });

    describe('Disabled state', () => {
        beforeEach(() => {
            component.disabled = true;
        });

        it('should not allow selection when disabled', () => {
            component.onCellClick(0, 0, new MouseEvent('click'));

            expect(component.selectionGrid[0][0]).toBe(false);
        });

        it('should not allow selectAll when disabled', () => {
            component.selectAll();

            let selectedCount = 0;
            for (let r = 0; r < component.spec.itemsY; r++) {
                for (let c = 0; c < component.spec.itemsX; c++) {
                    if (component.selectionGrid[r][c]) selectedCount++;
                }
            }

            expect(selectedCount).toBe(0);
        });
    });

    describe('Selection summary', () => {
        it('should return "No selection" when nothing selected', () => {
            component.selectedIndices = [];
            expect(component.getSelectionSummary()).toBe('No selection');
        });

        it('should return singular form for one selection', () => {
            component.selectedIndices = [0];
            expect(component.getSelectionSummary()).toBe('1 position selected');
        });

        it('should return plural form for multiple selections', () => {
            component.selectedIndices = [0, 1, 2];
            expect(component.getSelectionSummary()).toBe('3 positions selected');
        });
    });
});
