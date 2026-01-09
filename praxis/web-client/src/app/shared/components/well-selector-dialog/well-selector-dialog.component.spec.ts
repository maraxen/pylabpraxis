import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import {
    WellSelectorDialogComponent,
    WellSelectorDialogData,
    WellSelectorDialogResult,
} from './well-selector-dialog.component';

describe('WellSelectorDialogComponent', () => {
    let component: WellSelectorDialogComponent;
    let fixture: ComponentFixture<WellSelectorDialogComponent>;
    let dialogRef: any;

    const defaultData: WellSelectorDialogData = {
        plateType: '96',
        initialSelection: [],
        mode: 'multi',
    };

    beforeEach(async () => {
        dialogRef = {
            close: vi.fn(),
        };

        await TestBed.configureTestingModule({
            imports: [WellSelectorDialogComponent, NoopAnimationsModule],
            providers: [
                { provide: MatDialogRef, useValue: dialogRef },
                { provide: MAT_DIALOG_DATA, useValue: defaultData },
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(WellSelectorDialogComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    describe('Grid Generation', () => {
        it('should generate correct row labels for 96-well plate', () => {
            expect(component.rowLabels().length).toBe(8);
            expect(component.rowLabels()[0]).toBe('A');
            expect(component.rowLabels()[7]).toBe('H');
        });

        it('should generate correct column labels for 96-well plate', () => {
            expect(component.colLabels().length).toBe(12);
            expect(component.colLabels()[0]).toBe('1');
            expect(component.colLabels()[11]).toBe('12');
        });

        it('should set total wells correctly for 96-well plate', () => {
            expect(component.totalWells).toBe(96);
        });
    });

    describe('384-well Plate', () => {
        beforeEach(async () => {
            const data384: WellSelectorDialogData = {
                plateType: '384',
                initialSelection: [],
                mode: 'multi',
            };

            await TestBed.resetTestingModule();
            await TestBed.configureTestingModule({
                imports: [WellSelectorDialogComponent, NoopAnimationsModule],
                providers: [
                    { provide: MatDialogRef, useValue: dialogRef },
                    { provide: MAT_DIALOG_DATA, useValue: data384 },
                ],
            }).compileComponents();

            fixture = TestBed.createComponent(WellSelectorDialogComponent);
            component = fixture.componentInstance;
            fixture.detectChanges();
        });

        it('should generate correct row labels for 384-well plate', () => {
            expect(component.rowLabels().length).toBe(16);
            expect(component.rowLabels()[0]).toBe('A');
            expect(component.rowLabels()[15]).toBe('P');
        });

        it('should generate correct column labels for 384-well plate', () => {
            expect(component.colLabels().length).toBe(24);
            expect(component.colLabels()[0]).toBe('1');
            expect(component.colLabels()[23]).toBe('24');
        });

        it('should set total wells correctly for 384-well plate', () => {
            expect(component.totalWells).toBe(384);
        });
    });

    describe('Selection Operations', () => {
        it('should initially have no selections', () => {
            expect(component['selectedWellsSet']().size).toBe(0);
        });

        it('should select all wells', () => {
            component.selectAll();
            expect(component['selectedWellsSet']().size).toBe(96);
        });

        it('should clear all selections', () => {
            component.selectAll();
            component.clearSelection();
            expect(component['selectedWellsSet']().size).toBe(0);
        });

        it('should invert selection', () => {
            // Select A1, A2, A3
            component['selectedWellsSet'].set(new Set(['A1', 'A2', 'A3']));
            component.invertSelection();

            expect(component['selectedWellsSet']().size).toBe(93);
            expect(component.isSelected('A1')).toBe(false);
            expect(component.isSelected('A4')).toBe(true);
        });

        it('should remove a single well', () => {
            component['selectedWellsSet'].set(new Set(['A1', 'A2', 'A3']));
            component.removeWell('A2');

            expect(component['selectedWellsSet']().size).toBe(2);
            expect(component.isSelected('A1')).toBe(true);
            expect(component.isSelected('A2')).toBe(false);
            expect(component.isSelected('A3')).toBe(true);
        });
    });

    describe('Row and Column Operations', () => {
        it('should toggle entire row', () => {
            component.toggleRow('A');

            // All columns in row A should be selected
            for (let col = 1; col <= 12; col++) {
                expect(component.isSelected(`A${col}`)).toBe(true);
            }
            expect(component['selectedWellsSet']().size).toBe(12);

            // Toggle again should deselect
            component.toggleRow('A');
            expect(component['selectedWellsSet']().size).toBe(0);
        });

        it('should toggle entire column', () => {
            component.toggleColumn('1');

            // All rows in column 1 should be selected
            for (const row of ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']) {
                expect(component.isSelected(`${row}1`)).toBe(true);
            }
            expect(component['selectedWellsSet']().size).toBe(8);

            // Toggle again should deselect
            component.toggleColumn('1');
            expect(component['selectedWellsSet']().size).toBe(0);
        });

        it('should detect fully selected row', () => {
            expect(component.isRowFullySelected('A')).toBe(false);

            component.toggleRow('A');
            expect(component.isRowFullySelected('A')).toBe(true);
        });

        it('should detect fully selected column', () => {
            expect(component.isColumnFullySelected('1')).toBe(false);

            component.toggleColumn('1');
            expect(component.isColumnFullySelected('1')).toBe(true);
        });
    });

    describe('Initial Selection', () => {
        beforeEach(async () => {
            const dataWithSelection: WellSelectorDialogData = {
                plateType: '96',
                initialSelection: ['A1', 'B2', 'C3'],
                mode: 'multi',
            };

            await TestBed.resetTestingModule();
            await TestBed.configureTestingModule({
                imports: [WellSelectorDialogComponent, NoopAnimationsModule],
                providers: [
                    { provide: MatDialogRef, useValue: dialogRef },
                    { provide: MAT_DIALOG_DATA, useValue: dataWithSelection },
                ],
            }).compileComponents();

            fixture = TestBed.createComponent(WellSelectorDialogComponent);
            component = fixture.componentInstance;
            fixture.detectChanges();
        });

        it('should initialize with provided selection', () => {
            expect(component['selectedWellsSet']().size).toBe(3);
            expect(component.isSelected('A1')).toBe(true);
            expect(component.isSelected('B2')).toBe(true);
            expect(component.isSelected('C3')).toBe(true);
        });
    });

    describe('Sorted Selection', () => {
        it('should sort selected wells by row then column', () => {
            component['selectedWellsSet'].set(new Set(['B2', 'A3', 'A1', 'B1']));

            const sorted = component.sortedSelection();
            expect(sorted).toEqual(['A1', 'A3', 'B1', 'B2']);
        });
    });

    describe('Dialog Actions', () => {
        it('should close with empty result on cancel', () => {
            component.cancel();

            expect(dialogRef.close).toHaveBeenCalledWith({
                wells: [],
                confirmed: false,
            } as WellSelectorDialogResult);
        });

        it('should close with selection on confirm', () => {
            component['selectedWellsSet'].set(new Set(['A1', 'B2']));
            component.confirm();

            expect(dialogRef.close).toHaveBeenCalledWith({
                wells: ['A1', 'B2'],
                confirmed: true,
            } as WellSelectorDialogResult);
        });
    });

    describe('Drag Selection', () => {
        it('should detect if cell is in drag rectangle', () => {
            // Simulate drag from A1 to B2
            component['isDragging'].set(true);
            component['dragStartRow'] = 'A';
            component['dragStartCol'] = '1';
            component['dragEndRow'] = 'B';
            component['dragEndCol'] = '2';

            expect(component.isInDragRect('A', '1')).toBe(true);
            expect(component.isInDragRect('A', '2')).toBe(true);
            expect(component.isInDragRect('B', '1')).toBe(true);
            expect(component.isInDragRect('B', '2')).toBe(true);
            expect(component.isInDragRect('C', '1')).toBe(false);
            expect(component.isInDragRect('A', '3')).toBe(false);
        });

        it('should return false when not dragging', () => {
            component['isDragging'].set(false);
            expect(component.isInDragRect('A', '1')).toBe(false);
        });

        it('should handle mouse up to end drag', () => {
            component['isDragging'].set(true);
            component.onMouseUp();
            expect(component.isDragging()).toBe(false);
        });
    });
});
