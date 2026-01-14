import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WorkcellDashboardComponent } from './workcell-dashboard.component';
import { WorkcellViewService } from '../services/workcell-view.service';
import { of } from 'rxjs';
import { signal } from '@angular/core';

describe('WorkcellDashboardComponent', () => {
  let component: WorkcellDashboardComponent;
  let fixture: ComponentFixture<WorkcellDashboardComponent>;
  let mockWorkcellService: any;

  beforeEach(async () => {
    mockWorkcellService = {
      loadWorkcellGroups: vi.fn().mockReturnValue(of([])),
      workcellGroups: signal([])
    };

    await TestBed.configureTestingModule({
      imports: [WorkcellDashboardComponent],
      providers: [
        { provide: WorkcellViewService, useValue: mockWorkcellService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(WorkcellDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with grid view mode', () => {
    expect(component.viewMode()).toBe('grid');
  });

  it('should call loadWorkcellGroups on init', () => {
    expect(mockWorkcellService.loadWorkcellGroups).toHaveBeenCalled();
  });

  it('should change view mode', () => {
    component.setViewMode('list');
    expect(component.viewMode()).toBe('list');
    
    component.setViewMode('focus');
    expect(component.viewMode()).toBe('focus');
  });
});
