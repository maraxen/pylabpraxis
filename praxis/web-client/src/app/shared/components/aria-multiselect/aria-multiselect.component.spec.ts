import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AriaMultiselectComponent } from './aria-multiselect.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { By } from '@angular/platform-browser';
import { FilterOption } from '../../services/filter-result.service';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('AriaMultiselectComponent', () => {
    let component: AriaMultiselectComponent;
    let fixture: ComponentFixture<AriaMultiselectComponent>;

    const mockOptions: FilterOption[] = [
        { label: 'Option 1', value: 'opt1', count: 5 },
        { label: 'Option 2', value: 'opt2', count: 3 },
        { label: 'Option 3', value: 'opt3', count: 0, disabled: true },
    ];

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [AriaMultiselectComponent, NoopAnimationsModule],
        }).compileComponents();

        fixture = TestBed.createComponent(AriaMultiselectComponent);
        component = fixture.componentInstance;

        fixture.componentRef.setInput('label', 'Test Filter');
        fixture.componentRef.setInput('options', mockOptions);
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should display the label', () => {
        const triggerText = fixture.debugElement.query(By.css('.trigger-text'));
        expect(triggerText.nativeElement.textContent).toBe('Test Filter');
    });

    it('should not have active class when no selection', () => {
        const trigger = fixture.debugElement.query(By.css('.multiselect-trigger'));
        expect(trigger.nativeElement.classList.contains('active')).toBe(false);
    });

    it('should have active class when selection exists', () => {
        fixture.componentRef.setInput('selectedValue', 'opt1');
        fixture.detectChanges();
        const trigger = fixture.debugElement.query(By.css('.multiselect-trigger'));
        expect(trigger.nativeElement.classList.contains('active')).toBe(true);
    });

    it('should have disabled class when disabled', () => {
        fixture.componentRef.setInput('disabled', true);
        fixture.detectChanges();
        const trigger = fixture.debugElement.query(By.css('.multiselect-trigger'));
        expect(trigger.nativeElement.classList.contains('disabled')).toBe(true);
    });

    describe('single select mode', () => {
        it('should emit single value on selection change', () => {
            const spy = vi.spyOn(component.selectionChange, 'emit');
            component.onValuesChange(['opt1']);
            expect(spy).toHaveBeenCalledWith('opt1');
        });

        it('should emit null when clearing selection', () => {
            const spy = vi.spyOn(component.selectionChange, 'emit');
            component.clearSelection();
            expect(spy).toHaveBeenCalledWith(null);
        });
    });

    describe('multiple select mode', () => {
        beforeEach(() => {
            fixture.componentRef.setInput('multiple', true);
            fixture.detectChanges();
        });

        it('should emit array on selection change', () => {
            const spy = vi.spyOn(component.selectionChange, 'emit');
            component.onValuesChange(['opt1', 'opt2']);
            expect(spy).toHaveBeenCalledWith(['opt1', 'opt2']);
        });

        it('should emit empty array when clearing selection', () => {
            const spy = vi.spyOn(component.selectionChange, 'emit');
            component.clearSelection();
            expect(spy).toHaveBeenCalledWith([]);
        });

        it('should correctly identify selected values', () => {
            fixture.componentRef.setInput('selectedValue', ['opt1', 'opt2']);
            fixture.detectChanges();
            expect(component.isSelected('opt1')).toBe(true);
            expect(component.isSelected('opt2')).toBe(true);
            expect(component.isSelected('opt3')).toBe(false);
        });
    });

    describe('hasSelection', () => {
        it('should return false when no selection', () => {
            expect(component.hasSelection()).toBe(false);
        });

        it('should return true when has selection', () => {
            fixture.componentRef.setInput('selectedValue', 'opt1');
            fixture.detectChanges();
            expect(component.hasSelection()).toBe(true);
        });
    });

    describe('accessibility', () => {
        it('should have aria-label on trigger', () => {
            const trigger = fixture.debugElement.query(By.css('.multiselect-trigger'));
            expect(trigger.nativeElement.getAttribute('aria-label')).toBe('Test Filter');
        });

        it('should have aria-disabled when disabled', () => {
            fixture.componentRef.setInput('disabled', true);
            fixture.detectChanges();
            const trigger = fixture.debugElement.query(By.css('.multiselect-trigger'));
            expect(trigger.nativeElement.getAttribute('aria-disabled')).toBe('true');
        });
    });
});
