import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ResourceAccordionComponent } from './resource-accordion.component';
import { AssetService } from '../../services/asset.service';
import { MatDialog } from '@angular/material/dialog';
import { AppStore } from '../../../../core/store/app.store';
import { of } from 'rxjs';
import { signal } from '@angular/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { vi } from 'vitest';

describe('ResourceAccordionComponent', () => {
    let component: ResourceAccordionComponent;
    let fixture: ComponentFixture<ResourceAccordionComponent>;

    // Mocks
    const mockAssetService = {
        getResources: () => of([]),
        getResourceDefinitions: () => of([]),
        getMachines: () => of([])
    };

    const mockDialog = {
        open: vi.fn()
    };

    const mockAppStore = {
        infiniteConsumables: signal(false)
    };

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [ResourceAccordionComponent, NoopAnimationsModule],
            providers: [
                { provide: AssetService, useValue: mockAssetService },
                { provide: MatDialog, useValue: mockDialog },
                { provide: AppStore, useValue: mockAppStore }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(ResourceAccordionComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should show accordion when groupBy is set', () => {
        // Default is groupBy: 'category'
        component.viewState.set({
            viewType: 'accordion',
            groupBy: 'category',
            filters: {},
            sortBy: 'name',
            sortOrder: 'asc',
            search: ''
        });
        fixture.detectChanges();

        const accordion = fixture.nativeElement.querySelector('mat-accordion');
        const flatList = fixture.nativeElement.querySelector('.definition-list.flat-list');

        expect(accordion).toBeTruthy();
        expect(flatList).toBeFalsy();
    });

    it('should show flat list when groupBy is null (None)', () => {
        component.viewState.set({
            viewType: 'accordion',
            groupBy: null,
            filters: {},
            sortBy: 'name',
            sortOrder: 'asc',
            search: ''
        });
        fixture.detectChanges();

        const accordion = fixture.nativeElement.querySelector('mat-accordion');
        const flatList = fixture.nativeElement.querySelector('.definition-list.flat-list');

        expect(accordion).toBeFalsy();
        expect(flatList).toBeTruthy();
    });
});
