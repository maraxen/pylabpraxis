import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FilterChipComponent } from './filter-chip.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { By } from '@angular/platform-browser';
import { FilterOption } from '../../services/filter-result.service';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('FilterChipComponent', () => {
    let component: FilterChipComponent;
    let fixture: ComponentFixture<FilterChipComponent>;

    const mockOptions: FilterOption[] = [
        { label: 'Option 1', value: 'opt1', count: 5 },
        { label: 'Option 2', value: 'opt2', count: 0, disabled: true },
    ];

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [FilterChipComponent, NoopAnimationsModule]
        })
            .compileComponents();

        fixture = TestBed.createComponent(FilterChipComponent);
        component = fixture.componentInstance;

        // Use setInput for OnPush components
        fixture.componentRef.setInput('label', 'Test Filter');
        fixture.componentRef.setInput('options', mockOptions);
        fixture.detectChanges();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should display base label even when value selected (per feedback)', () => {
        fixture.componentRef.setInput('selectedValue', 'opt1');
        fixture.detectChanges();
        const chipText = fixture.debugElement.query(By.css('.chip-text')).nativeElement.textContent;
        expect(chipText).toBe('Test Filter');
    });

    it('should toggle active class', () => {
        fixture.componentRef.setInput('selectedValue', 'opt1');
        fixture.detectChanges();
        const chip = fixture.debugElement.query(By.css('.filter-chip')).nativeElement;
        expect(chip.classList).toContain('active');
    });

    it('should emit selectionChange when selectOption is called', () => {
        const spy = vi.spyOn(component.selectionChange, 'emit');
        component.selectOption('opt1');
        expect(spy).toHaveBeenCalledWith('opt1');
    });

    it('should handle multi-select toggling', () => {
        const spy = vi.spyOn(component.selectionChange, 'emit');
        fixture.componentRef.setInput('multiple', true);
        fixture.componentRef.setInput('selectedValue', ['opt1']);
        fixture.detectChanges();

        component.selectOption('opt2');
        expect(spy).toHaveBeenCalledWith(['opt1', 'opt2']);

        component.selectOption('opt1');
        expect(spy).toHaveBeenCalledWith([]);
    });

    it('should trigger shake when disabled and clicked', () => {
        vi.useFakeTimers();
        fixture.componentRef.setInput('disabled', true);
        fixture.detectChanges();

        const chip = fixture.debugElement.query(By.css('.filter-chip'));
        const event = new MouseEvent('click', { bubbles: true });
        const stopSpy = vi.spyOn(event, 'stopPropagation');

        chip.triggerEventHandler('click', event);
        fixture.detectChanges();

        expect(stopSpy).toHaveBeenCalled();
        expect(component.isShaking).toBe(true);

        vi.advanceTimersByTime(300);
        expect(component.isShaking).toBe(false);
    });
});
