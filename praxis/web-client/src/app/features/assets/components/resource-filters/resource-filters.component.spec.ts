import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ResourceFiltersComponent } from './resource-filters.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { ResourceStatus, Resource } from '../../models/asset.models';
import { FilterResultService } from '../../../../shared/services/filter-result.service';

describe('ResourceFiltersComponent', () => {
    let component: ResourceFiltersComponent;
    let fixture: ComponentFixture<ResourceFiltersComponent>;

    const mockResources: Resource[] = [
        { id: '1', name: 'Res 1', status: ResourceStatus.AVAILABLE, plr_category: 'Cat1' } as any,
        { id: '2', name: 'Res 2', status: ResourceStatus.IN_USE, plr_category: 'Cat2' } as any,
    ];

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [ResourceFiltersComponent, NoopAnimationsModule],
            providers: [FilterResultService]
        }).compileComponents();

        fixture = TestBed.createComponent(ResourceFiltersComponent);
        component = fixture.componentInstance;
        component.resources = mockResources;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should emit filter state on change', () => {
        const spy = vi.spyOn(component.filtersChange, 'emit');
        component.searchTerm.set('test');
        component.onFilterChange();
        expect(spy).toHaveBeenCalledWith(expect.objectContaining({ search: 'test' }));
    });

    it('should compute option counts correctly', () => {
        const catOptions = component.categoryOptions();
        // Cat1 should have 1, Cat2 should have 1
        const cat1 = catOptions.find(o => o.value === 'Cat1');
        const cat2 = catOptions.find(o => o.value === 'Cat2');

        expect(cat1?.count).toBe(1);
        expect(cat2?.count).toBe(1);
    });

    it('should update counts when filters change', () => {
        // Set search to 'Res 1'
        component.searchTerm.set('Res 1');
        fixture.detectChanges();

        const catOptions = component.categoryOptions();
        const cat1 = catOptions.find(o => o.value === 'Cat1');
        const cat2 = catOptions.find(o => o.value === 'Cat2');

        expect(cat1?.count).toBe(1);
        expect(cat2?.count).toBe(0);
        expect(cat2?.disabled).toBe(true);
    });

    it('should clear all filters', () => {
        component.searchTerm.set('test');
        component.selectedStatuses.set([ResourceStatus.AVAILABLE]);
        component.clearFilters();
        expect(component.searchTerm()).toBe('');
        expect(component.selectedStatuses()).toEqual([]);
    });
});
