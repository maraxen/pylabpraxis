import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { AriaAutocompleteComponent, SelectOption } from './aria-autocomplete.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';

describe('AriaAutocompleteComponent', () => {
    let component: AriaAutocompleteComponent;
    let fixture: ComponentFixture<AriaAutocompleteComponent>;

    const mockOptions: SelectOption[] = [
        { label: 'Apple', value: 'apple' },
        { label: 'Banana', value: 'banana' },
        { label: 'Cherry', value: 'cherry' },
        { label: 'Date', value: 'date' },
    ];

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [
                AriaAutocompleteComponent,
                NoopAnimationsModule,
                FormsModule,
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(AriaAutocompleteComponent);
        component = fixture.componentInstance;
        component.options = mockOptions;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should filter options based on query', fakeAsync(() => {
        component.query.set('che');
        fixture.detectChanges();
        tick();

        const filtered = component.filteredOptions();
        expect(filtered.length).toBe(1);
        expect(filtered[0].label).toBe('Cherry');
    }));

    it('should select an option and update query', fakeAsync(() => {
        component.onValueChange(['cherry']);
        fixture.detectChanges();
        tick();

        expect(component.selectedValues()).toContain('cherry');
        expect(component.query()).toBe('Cherry');
    }));

    it('should clear query and reset filtered options', fakeAsync(() => {
        component.query.set('apple');
        fixture.detectChanges();
        tick();

        component.clearQuery(new MouseEvent('click'));
        fixture.detectChanges();
        tick();

        expect(component.query()).toBe('');
        expect(component.filteredOptions().length).toBe(mockOptions.length);
    }));

    it('should implement ControlValueAccessor', fakeAsync(() => {
        component.writeValue('banana');
        fixture.detectChanges();
        tick();

        expect(component.selectedValues()).toContain('banana');
        expect(component.query()).toBe('Banana');
    }));

    it('should handle empty results', fakeAsync(() => {
        component.query.set('xyz');
        fixture.detectChanges();
        tick();

        expect(component.filteredOptions().length).toBe(0);
    }));
});
