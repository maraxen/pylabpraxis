import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FilterChipBarComponent } from './filter-chip-bar.component';
import { By } from '@angular/platform-browser';
import { ActiveFilter } from '../view-controls/view-controls.types';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('FilterChipBarComponent', () => {
    let component: FilterChipBarComponent;
    let fixture: ComponentFixture<FilterChipBarComponent>;

    const mockFilters: ActiveFilter[] = [
        {
            filterId: 'category',
            label: 'Category',
            values: ['Hardware'],
            displayText: 'Category: Hardware'
        },
        {
            filterId: 'status',
            label: 'Status',
            values: ['Active', 'Pending'],
            displayText: 'Status: Active, Pending'
        }
    ];

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [FilterChipBarComponent, NoopAnimationsModule]
        }).compileComponents();

        fixture = TestBed.createComponent(FilterChipBarComponent);
        component = fixture.componentInstance;
        fixture.componentRef.setInput('filters', mockFilters);
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should render chips for each filter', () => {
        const chips = fixture.debugElement.queryAll(By.css('.filter-chip'));
        expect(chips.length).toBe(2);
    });

    it('should display correct text in chips', () => {
        const chips = fixture.debugElement.queryAll(By.css('.filter-chip'));
        expect(chips[0].nativeElement.textContent).toContain('Category: Hardware');
        // The second one might be truncated or full depending on logic, checking partial
        expect(chips[1].nativeElement.textContent).toContain('Status: Active, Pending');
    });

    it('should emit remove event when close icon is clicked', () => {
        const spy = vi.spyOn(component.remove, 'emit');
        const closeBtns = fixture.debugElement.queryAll(By.css('.chip-remove'));

        closeBtns[0].nativeElement.click();
        expect(spy).toHaveBeenCalledWith('category');
    });

    it('should emit clearAll event when Clear All is clicked', () => {
        const spy = vi.spyOn(component.clearAll, 'emit');
        const clearBtn = fixture.debugElement.query(By.css('.clear-all-link'));

        clearBtn.nativeElement.click();
        expect(spy).toHaveBeenCalled();
    });

    it('should map icons correctly', () => {
        // category -> category
        expect(component.getIcon('category')).toBe('category');
        // status -> flag
        expect(component.getIcon('status')).toBe('flag');
        // unknown -> filter_alt
        expect(component.getIcon('unknown')).toBe('filter_alt');
    });
});
