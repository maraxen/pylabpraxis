import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PraxisAutocompleteComponent } from './praxis-autocomplete.component';
import { SelectOption } from '../praxis-select/praxis-select.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';
import { TestbedHarnessEnvironment } from '@angular/cdk/testing/testbed';
import { MatAutocompleteHarness } from '@angular/material/autocomplete/testing';
import { MatInputHarness } from '@angular/material/input/testing';
import { HarnessLoader } from '@angular/cdk/testing';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { describe, it, expect, beforeEach } from 'vitest';

describe('PraxisAutocompleteComponent', () => {
    let component: PraxisAutocompleteComponent;
    let fixture: ComponentFixture<PraxisAutocompleteComponent>;
    let loader: HarnessLoader;

    const mockOptions: SelectOption[] = [
        { label: 'Apple', value: 'apple' },
        { label: 'Banana', value: 'banana' },
        { label: 'Cherry', value: 'cherry' },
        { label: 'Date', value: 'date' },
    ];

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [
                PraxisAutocompleteComponent,
                NoopAnimationsModule,
                FormsModule,
                MatAutocompleteModule,
                MatInputModule,
                MatFormFieldModule
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(PraxisAutocompleteComponent);
        component = fixture.componentInstance;
        component.options = mockOptions;
        component.label = 'Fruit';
        component.placeholder = 'Select fruit';
        loader = TestbedHarnessEnvironment.loader(fixture);
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should filter options when typing', async () => {
        const input = await loader.getHarness(MatInputHarness);
        await input.setValue('Che');

        const autocomplete = await loader.getHarness(MatAutocompleteHarness);
        const options = await autocomplete.getOptions();

        expect(options.length).toBe(1);
        expect(await options[0].getText()).toBe('Cherry');
    });

    it('should select an option', async () => {
        const input = await loader.getHarness(MatInputHarness);
        await input.setValue('Ban');

        const autocomplete = await loader.getHarness(MatAutocompleteHarness);
        await autocomplete.selectOption({ text: 'Banana' });

        expect(await input.getValue()).toBe('Banana');
    });

    it('should clear selection', async () => {
        const input = await loader.getHarness(MatInputHarness);
        component.writeValue('apple');
        fixture.detectChanges();

        expect(await input.getValue()).toBe('Apple');

        component.writeValue(null);
        fixture.detectChanges();
        expect(await input.getValue()).toBe('');
    });

    it('should handle disabled state', async () => {
        component.setDisabledState(true);
        fixture.detectChanges();
        const input = await loader.getHarness(MatInputHarness);
        expect(await input.isDisabled()).toBe(true);
    });
});
