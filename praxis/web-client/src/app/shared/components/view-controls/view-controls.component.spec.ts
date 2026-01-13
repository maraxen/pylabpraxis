import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ViewControlsComponent } from './view-controls.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { By } from '@angular/platform-browser';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { ViewControlsConfig, ViewControlsState } from './view-controls.types';

describe('ViewControlsComponent', () => {
    let component: ViewControlsComponent;
    let fixture: ComponentFixture<ViewControlsComponent>;

    const mockConfig: ViewControlsConfig = {
        viewTypes: ['card', 'list'],
        groupByOptions: [
            { label: 'Status', value: 'status' },
            { label: 'Type', value: 'type' }
        ],
        filters: [
            {
                key: 'category',
                label: 'Category',
                type: 'multiselect',
                options: [{ label: 'Hardware', value: 'hardware' }]
            }
        ],
        sortOptions: [
            { label: 'Name', value: 'name' }
        ],
        storageKey: 'test-controls'
    };

    beforeEach(async () => {
        localStorage.clear();
        await TestBed.configureTestingModule({
            imports: [ViewControlsComponent, NoopAnimationsModule]
        }).compileComponents();

        fixture = TestBed.createComponent(ViewControlsComponent);
        component = fixture.componentInstance;
        fixture.componentRef.setInput('config', mockConfig);
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should initialize with defaults if no persistence exists', () => {
        expect(component.state.viewType).toBe('card');
        expect(component.state.search).toBe('');
        expect(component.state.filters['category']).toEqual([]);
    });

    it('should update search with debounce', () => {
        vi.useFakeTimers();
        const spy = vi.spyOn(component.searchChange, 'emit');
        const input = fixture.debugElement.query(By.css('.search-input')).nativeElement;

        input.value = 'test query';
        input.dispatchEvent(new Event('input'));

        vi.advanceTimersByTime(100);
        expect(spy).not.toHaveBeenCalled();

        vi.advanceTimersByTime(200);
        expect(spy).toHaveBeenCalledWith('test query');
        expect(component.state.search).toBe('test query');
        vi.useRealTimers();
    });

    it('should emit viewTypeChange', () => {
        const spy = vi.spyOn(component.viewTypeChange, 'emit');
        component.onViewTypeChange('list');
        expect(spy).toHaveBeenCalledWith('list');
        expect(component.state.viewType).toBe('list');
    });

    it('should emit filtersChange', () => {
        const spy = vi.spyOn(component.filtersChange, 'emit');
        component.onFilterChange('category', ['hardware']);
        expect(spy).toHaveBeenCalledWith({ category: ['hardware'] });
        expect(component.state.filters['category']).toEqual(['hardware']);
    });

    it('should persist state to localStorage', () => {
        component.onViewTypeChange('list');
        fixture.detectChanges();
        const stored = localStorage.getItem('viewControls.test-controls');
        expect(stored).toBeTruthy();
        const parsed = JSON.parse(stored!);
        expect(parsed.viewType).toBe('list');
    });

    it('should clear all filters', () => {
        component.onSearchInput({ target: { value: 'query' } } as any);
        component.onFilterChange('category', ['hardware']);
        component.onGroupByChange('status');

        expect(component.hasActiveFilters).toBe(true);

        component.clearAll();

        expect(component.state.search).toBe('');
        expect(component.state.filters['category']).toEqual([]);
        expect(component.state.groupBy).toBeNull();
        expect(component.hasActiveFilters).toBe(false);
    });
});
