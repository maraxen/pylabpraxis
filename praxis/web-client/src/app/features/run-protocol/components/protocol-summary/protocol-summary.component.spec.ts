import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ProtocolSummaryComponent } from './protocol-summary.component';
import { ProtocolDefinition } from '@features/protocols/models/protocol.models';

describe('ProtocolSummaryComponent', () => {
    let component: ProtocolSummaryComponent;
    let fixture: ComponentFixture<ProtocolSummaryComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [ProtocolSummaryComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(ProtocolSummaryComponent);
        component = fixture.componentInstance;
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should display protocol information', () => {
        const mockProtocol: ProtocolDefinition = {
            accession_id: '123',
            name: 'Test Protocol',
            version: '2.4.1',
            is_top_level: true,
            assets: [],
            parameters: []
        };
        fixture.componentRef.setInput('protocol', mockProtocol);
        fixture.detectChanges();

        const compiled = fixture.nativeElement as HTMLElement;
        expect(compiled.textContent).toContain('Test Protocol');
        expect(compiled.textContent).toContain('Version 2.4.1');
    });

    it('should display parameters excluding well parameters', () => {
        const mockProtocol: ProtocolDefinition = {
            accession_id: '123',
            name: 'Test Protocol',
            version: '1.0.0',
            is_top_level: true,
            assets: [],
            parameters: [
                { name: 'incubation_temp', type_hint: 'float' } as any,
                { name: 'source_wells', type_hint: 'List[Well]' } as any
            ]
        };
        fixture.componentRef.setInput('protocol', mockProtocol);
        fixture.componentRef.setInput('parameters', { incubation_temp: 37, source_wells: ['A1'] });
        fixture.detectChanges();

        const compiled = fixture.nativeElement as HTMLElement;
        // Label should be formatted "Incubation Temp"
        expect(compiled.textContent).toContain('Incubation Temp');
        expect(compiled.textContent).toContain('37');

        // standard parameters section should NOT contain well parameters
        const summarySections = compiled.querySelectorAll('.summary-section');
        const paramsSection = summarySections[0];
        expect(paramsSection?.textContent).not.toContain('Source Wells');
    });

    it('should display well selections when required', () => {
        fixture.componentRef.setInput('wellSelectionRequired', true);
        fixture.componentRef.setInput('wellSelections', { 'source_wells': ['A1', 'A2'], 'target_wells': ['B1'] });
        fixture.detectChanges();

        const compiled = fixture.nativeElement as HTMLElement;
        expect(compiled.textContent).toContain('Well Selections');
        expect(compiled.textContent).toContain('Source Wells');
        expect(compiled.textContent).toContain('2 Wells'); // Rechecked template: {{ item.wells.length }} Wells
        expect(compiled.textContent).toContain('Target Wells');
        expect(compiled.textContent).toContain('1 Wells');
    });
});
