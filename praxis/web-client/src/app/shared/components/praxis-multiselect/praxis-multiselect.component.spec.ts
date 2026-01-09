import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PraxisMultiselectComponent } from './praxis-multiselect.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { FilterOption } from '../../services/filter-result.service';
import { TestbedHarnessEnvironment } from '@angular/cdk/testing/testbed';
import { MatSelectHarness } from '@angular/material/select/testing';
import { HarnessLoader } from '@angular/cdk/testing';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';
import { describe, it, expect, beforeEach } from 'vitest';

describe('PraxisMultiselectComponent', () => {
    let component: PraxisMultiselectComponent;
    let fixture: ComponentFixture<PraxisMultiselectComponent>;
    let loader: HarnessLoader;

    const mockOptions: FilterOption[] = [
        { label: 'Option 1', value: 'opt1', count: 5 },
        { label: 'Option 2', value: 'opt2', count: 3 },
        { label: 'Option 3', value: 'opt3', count: 0, disabled: true },
        { label: 'Option 4', value: 'opt4', count: 1 },
        { label: 'Option 5', value: 'opt5', count: 2 }
    ];

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [
                PraxisMultiselectComponent,
                NoopAnimationsModule,
                MatFormFieldModule,
                MatSelectModule,
                MatTooltipModule
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(PraxisMultiselectComponent);
        component = fixture.componentInstance;
        component.options = mockOptions;
        component.label = 'Test Filter';
        loader = TestbedHarnessEnvironment.loader(fixture);
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should open and close', async () => {
        const select = await loader.getHarness(MatSelectHarness);
        expect(await select.isOpen()).toBe(false);
        await select.open();
        expect(await select.isOpen()).toBe(true);
        await select.close();
        expect(await select.isOpen()).toBe(false);
    });

    it('should display options correctly', async () => {
        const select = await loader.getHarness(MatSelectHarness);
        await select.open();
        const options = await select.getOptions();
        expect(options.length).toBe(5);
        expect(await options[0].getText()).toContain('Option 1');
        expect(await options[2].isDisabled()).toBe(true);
    });

    it('should select multiple options and show chips below', async () => {
        const select = await loader.getHarness(MatSelectHarness);
        await select.open();
        await select.clickOptions({ text: /Option 1/ });
        await select.clickOptions({ text: /Option 2/ });

        fixture.detectChanges();
        // Chips are now outside in .praxis-chip-grid
        const chips = fixture.nativeElement.querySelectorAll('.praxis-chip-grid .selection-chip');
        expect(chips.length).toBe(2);
        expect(chips[0].textContent).toContain('Option 1');
        expect(chips[1].textContent).toContain('Option 2');
    });

    it('should show trigger label correctly', async () => {
        const select = await loader.getHarness(MatSelectHarness);
        const text = await select.getValueText();
        // Trigger should simply show label or placeholder, not the values
        expect(text).toBe('Test Filter');
    });

    it('should emit changes on selection', async () => {
        let emittedValue: any[] = [];
        component.valueChange.subscribe((val) => emittedValue = val);

        const select = await loader.getHarness(MatSelectHarness);
        await select.open();
        await select.clickOptions({ text: /Option 1/ });

        expect(emittedValue).toEqual(['opt1']);
    });

    it('should show "None" when no selection', async () => {
        component.value = [];
        fixture.detectChanges();
        const noneChip = fixture.nativeElement.querySelector('.chip-none');
        expect(noneChip).toBeTruthy();
        expect(noneChip.textContent).toContain('None');
    });

    it('should remove chip when close icon clicked', async () => {
        component.value = ['opt1', 'opt2'];
        fixture.detectChanges();

        let chips = fixture.nativeElement.querySelectorAll('.selection-chip');
        expect(chips.length).toBe(2);

        const removeIcon = chips[0].querySelector('.remove-icon');
        expect(removeIcon).toBeTruthy();
        removeIcon.click();
        fixture.detectChanges();

        const currentChips = fixture.nativeElement.querySelectorAll('.selection-chip');
        const labels = Array.from(currentChips).map((c: any) => c.querySelector('.chip-label').textContent.trim());
        expect(labels).toEqual(['Option 2']);
        chips = fixture.nativeElement.querySelectorAll('.selection-chip');
        expect(chips.length).toBe(1);
        expect(chips[0].textContent).toContain('Option 2');
    });

    it('should show all selected items (no overflow limit)', async () => {
        component.value = ['opt1', 'opt2', 'opt4', 'opt5'];
        fixture.detectChanges();

        const chips = fixture.nativeElement.querySelectorAll('.selection-chip');
        expect(chips.length).toBe(4);
    });

    it('should respect disabled state', async () => {
        component.disabled = true;
        fixture.detectChanges();
        const select = await loader.getHarness(MatSelectHarness);
        expect(await select.isDisabled()).toBe(true);
    });
});
