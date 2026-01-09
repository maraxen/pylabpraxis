import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PraxisSelectComponent, SelectOption } from './praxis-select.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { TestbedHarnessEnvironment } from '@angular/cdk/testing/testbed';
import { MatSelectHarness } from '@angular/material/select/testing';
import { HarnessLoader } from '@angular/cdk/testing';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { describe, it, expect, beforeEach } from 'vitest';

describe('PraxisSelectComponent', () => {
    let component: PraxisSelectComponent;
    let fixture: ComponentFixture<PraxisSelectComponent>;
    let loader: HarnessLoader;

    const mockOptions: SelectOption[] = [
        { label: 'Option A', value: 'a' },
        { label: 'Option B', value: 'b' },
        { label: 'Option C', value: 'c', disabled: true }
    ];

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [
                PraxisSelectComponent,
                NoopAnimationsModule,
                MatFormFieldModule,
                MatSelectModule
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(PraxisSelectComponent);
        component = fixture.componentInstance;
        component.options = mockOptions;
        component.label = 'Choose One';
        loader = TestbedHarnessEnvironment.loader(fixture);
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should open and show options', async () => {
        const select = await loader.getHarness(MatSelectHarness);
        await select.open();
        const options = await select.getOptions();
        expect(options.length).toBe(3);
        expect(await options[0].getText()).toBe('Option A');
    });

    it('should select an option and emit value', async () => {
        let emitted: any;
        component.valueChange.subscribe(v => emitted = v);

        const select = await loader.getHarness(MatSelectHarness);
        await select.open();
        await select.clickOptions({ text: 'Option B' });

        expect(emitted).toBe('b');
        expect(await select.getValueText()).toBe('Option B');
    });

    it('should be disabled when input is set', async () => {
        component.disabled = true;
        fixture.detectChanges();
        const select = await loader.getHarness(MatSelectHarness);
        expect(await select.isDisabled()).toBe(true);
    });

    it('should display placeholder when no selection', async () => {
        component.placeholder = 'Custom Placeholder';
        fixture.detectChanges();
        const select = await loader.getHarness(MatSelectHarness);
        expect(await select.getValueText()).toBe('Custom Placeholder');
    });

    it('should handle programmatic value setting', async () => {
        component.value = 'a';
        fixture.detectChanges();
        const select = await loader.getHarness(MatSelectHarness);
        expect(await select.getValueText()).toBe('Option A');
    });
});
