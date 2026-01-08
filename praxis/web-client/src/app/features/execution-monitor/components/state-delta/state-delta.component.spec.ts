import { ComponentFixture, TestBed } from '@angular/core/testing';
import { StateDeltaComponent } from './state-delta.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('StateDeltaComponent', () => {
    let component: StateDeltaComponent;
    let fixture: ComponentFixture<StateDeltaComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [StateDeltaComponent, NoopAnimationsModule]
        }).compileComponents();

        fixture = TestBed.createComponent(StateDeltaComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should detect positive changes', () => {
        expect(component.isPositive({ key: 'test', before: 0, after: 10, change: 10 })).toBe(true);
        expect(component.isPositive({ key: 'test', before: 10, after: 0, change: -10 })).toBe(false);
    });

    it('should detect negative changes', () => {
        expect(component.isNegative({ key: 'test', before: 10, after: 0, change: -10 })).toBe(true);
        expect(component.isNegative({ key: 'test', before: 0, after: 10, change: 10 })).toBe(false);
    });

    it('should format keys correctly', () => {
        expect(component.formatKey("source['A1'].volume")).toBe('A1.volume');
        expect(component.formatKey("tips.available")).toBe('tips.available');
    });

    it('should format positive changes with plus sign', () => {
        expect(component.formatChange(50)).toBe('+50');
        expect(component.formatChange(-50)).toBe('-50');
    });

    describe('Rendering', () => {
        it('should display state deltas for operations with state changes', () => {
            fixture.componentRef.setInput('deltas', [
                { key: 'volume', before: 100, after: 50, change: -50 }
            ]);
            fixture.detectChanges();

            const compiled = fixture.nativeElement;
            expect(compiled.querySelector('.delta-row')).toBeTruthy();
            expect(compiled.textContent).toContain('-50');
        });

        it('should show "No state changes" when deltas is empty', () => {
            fixture.componentRef.setInput('deltas', []);
            fixture.detectChanges();

            const compiled = fixture.nativeElement;
            expect(compiled.textContent).toContain('No state changes');
        });
    });
});
