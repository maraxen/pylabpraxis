import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WorkcellExplorerComponent } from './workcell-explorer.component';
import { WorkcellGroup, MachineWithRuntime } from '../../../../features/workcell/models/workcell-view.models';
import { MachineStatus } from '../../../../features/assets/models/asset.models';

describe('WorkcellExplorerComponent', () => {
  let component: WorkcellExplorerComponent;
  let fixture: ComponentFixture<WorkcellExplorerComponent>;

  const mockMachines: MachineWithRuntime[] = [
    {
      accession_id: 'm1',
      name: 'Hamilton STAR',
      machine_type: 'Liquid Handler',
      status: MachineStatus.IDLE,
      connectionState: 'connected',
      stateSource: 'live',
      alerts: []
    },
    {
      accession_id: 'm2',
      name: 'OT-2',
      machine_type: 'Pipettor',
      status: MachineStatus.RUNNING,
      connectionState: 'connected',
      stateSource: 'live',
      alerts: []
    }
  ];

  const mockGroups: WorkcellGroup[] = [
    {
      workcell: { accession_id: 'wc1', name: 'Main Lab', status: 'active' },
      machines: [mockMachines[0]],
      isExpanded: false
    },
    {
      workcell: null,
      machines: [mockMachines[1]],
      isExpanded: false
    }
  ];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WorkcellExplorerComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(WorkcellExplorerComponent);
    component = fixture.componentInstance;
    component.groups = mockGroups;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should filter machines based on search query', () => {
    component.searchQuery.set('Hamilton');
    fixture.detectChanges();
    
    const filtered = component.filteredGroups();
    expect(filtered.length).toBe(1);
    expect(filtered[0].machines[0].name).toBe('Hamilton STAR');
  });

  it('should filter machines based on machine type', () => {
    component.searchQuery.set('Pipettor');
    fixture.detectChanges();
    
    const filtered = component.filteredGroups();
    expect(filtered.length).toBe(1);
    expect(filtered[0].machines[0].name).toBe('OT-2');
  });

  it('should expand groups when searching', () => {
    component.searchQuery.set('OT-2');
    fixture.detectChanges();
    
    const filtered = component.filteredGroups();
    expect(filtered[0].isExpanded).toBe(true);
  });

  it('should emit machineSelect when a machine is selected', () => {
    const spy = vi.spyOn(component.machineSelect, 'emit');
    component.onMachineSelect(mockMachines[0]);
    expect(spy).toHaveBeenCalledWith(mockMachines[0]);
  });
});
