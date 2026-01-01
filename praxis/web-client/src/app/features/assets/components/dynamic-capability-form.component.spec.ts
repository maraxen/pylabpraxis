import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { DynamicCapabilityFormComponent } from './dynamic-capability-form.component';
import { MachineCapabilityConfigSchema, CapabilityConfigField } from '../models/asset.models';

describe('DynamicCapabilityFormComponent', () => {
    let component: DynamicCapabilityFormComponent;
    let fixture: ComponentFixture<DynamicCapabilityFormComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [
                DynamicCapabilityFormComponent,
                NoopAnimationsModule
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(DynamicCapabilityFormComponent);
        component = fixture.componentInstance;
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    describe('Form Building', () => {
        it('should build form with boolean fields', () => {
            const config: MachineCapabilityConfigSchema = {
                machine_type: 'test',
                config_fields: [
                    {
                        field_name: 'has_feature',
                        display_name: 'Has Feature',
                        field_type: 'boolean',
                        default_value: false
                    }
                ]
            };

            component.config = config;
            fixture.detectChanges();

            expect(component.form.get('has_feature')).toBeTruthy();
            expect(component.form.get('has_feature')?.value).toBe(false);
        });

        it('should build form with number fields', () => {
            const config: MachineCapabilityConfigSchema = {
                machine_type: 'test',
                config_fields: [
                    {
                        field_name: 'max_speed',
                        display_name: 'Max Speed',
                        field_type: 'number',
                        default_value: 100
                    }
                ]
            };

            component.config = config;
            fixture.detectChanges();

            expect(component.form.get('max_speed')).toBeTruthy();
            expect(component.form.get('max_speed')?.value).toBe(100);
        });

        it('should build form with select fields', () => {
            const config: MachineCapabilityConfigSchema = {
                machine_type: 'test',
                config_fields: [
                    {
                        field_name: 'channels',
                        display_name: 'Channels',
                        field_type: 'select',
                        default_value: '8',
                        options: ['1', '4', '8', '16']
                    }
                ]
            };

            component.config = config;
            fixture.detectChanges();

            expect(component.form.get('channels')).toBeTruthy();
            expect(component.form.get('channels')?.value).toBe('8');
        });

        it('should use initial values over defaults', () => {
            const config: MachineCapabilityConfigSchema = {
                machine_type: 'test',
                config_fields: [
                    {
                        field_name: 'has_feature',
                        display_name: 'Has Feature',
                        field_type: 'boolean',
                        default_value: false
                    }
                ]
            };

            component.config = config;
            component.initialValue = { has_feature: true };
            fixture.detectChanges();

            expect(component.form.get('has_feature')?.value).toBe(true);
        });
    });

    describe('Conditional Visibility (depends_on)', () => {
        it('should show field without depends_on', () => {
            const config: MachineCapabilityConfigSchema = {
                machine_type: 'test',
                config_fields: [
                    {
                        field_name: 'always_visible',
                        display_name: 'Always Visible',
                        field_type: 'boolean',
                        default_value: false
                    }
                ]
            };

            component.config = config;
            fixture.detectChanges();

            const visibleFields = component.visibleFields();
            expect(visibleFields.length).toBe(1);
            expect(visibleFields[0].field_name).toBe('always_visible');
        });

        it('should hide field when depends_on condition is false', () => {
            const config: MachineCapabilityConfigSchema = {
                machine_type: 'test',
                config_fields: [
                    {
                        field_name: 'parent_toggle',
                        display_name: 'Parent Toggle',
                        field_type: 'boolean',
                        default_value: false
                    },
                    {
                        field_name: 'child_field',
                        display_name: 'Child Field',
                        field_type: 'number',
                        default_value: 10,
                        depends_on: 'parent_toggle'
                    }
                ]
            };

            component.config = config;
            fixture.detectChanges();

            const visibleFields = component.visibleFields();
            expect(visibleFields.length).toBe(1);
            expect(visibleFields[0].field_name).toBe('parent_toggle');
        });

        it('should show field when depends_on condition becomes true', () => {
            const config: MachineCapabilityConfigSchema = {
                machine_type: 'test',
                config_fields: [
                    {
                        field_name: 'parent_toggle',
                        display_name: 'Parent Toggle',
                        field_type: 'boolean',
                        default_value: false
                    },
                    {
                        field_name: 'child_field',
                        display_name: 'Child Field',
                        field_type: 'number',
                        default_value: 10,
                        depends_on: 'parent_toggle'
                    }
                ]
            };

            component.config = config;
            fixture.detectChanges();

            // Enable parent toggle
            component.form.get('parent_toggle')?.setValue(true);
            fixture.detectChanges();

            const visibleFields = component.visibleFields();
            expect(visibleFields.length).toBe(2);
        });

        it('should handle depends_on with specific value', () => {
            const config: MachineCapabilityConfigSchema = {
                machine_type: 'test',
                config_fields: [
                    {
                        field_name: 'mode',
                        display_name: 'Mode',
                        field_type: 'select',
                        default_value: 'basic',
                        options: ['basic', 'advanced']
                    },
                    {
                        field_name: 'advanced_option',
                        display_name: 'Advanced Option',
                        field_type: 'boolean',
                        default_value: false,
                        depends_on: 'mode=advanced'
                    }
                ]
            };

            component.config = config;
            fixture.detectChanges();

            // Initially hidden (mode=basic)
            expect(component.visibleFields().length).toBe(1);

            // Set to advanced
            component.form.get('mode')?.setValue('advanced');
            fixture.detectChanges();

            expect(component.visibleFields().length).toBe(2);
        });
    });

    describe('Validation', () => {
        it('should apply required validator', () => {
            const config: MachineCapabilityConfigSchema = {
                machine_type: 'test',
                config_fields: [
                    {
                        field_name: 'required_field',
                        display_name: 'Required Field',
                        field_type: 'number',
                        default_value: null,
                        required: true
                    }
                ]
            };

            component.config = config;
            fixture.detectChanges();

            const control = component.form.get('required_field');
            expect(control?.hasError('required')).toBe(true);

            control?.setValue(42);
            expect(control?.hasError('required')).toBe(false);
        });

        it('should apply min validator', () => {
            const config: MachineCapabilityConfigSchema = {
                machine_type: 'test',
                config_fields: [
                    {
                        field_name: 'min_field',
                        display_name: 'Min Field',
                        field_type: 'number',
                        default_value: 0,
                        min: 10
                    }
                ]
            };

            component.config = config;
            fixture.detectChanges();

            const control = component.form.get('min_field');
            expect(control?.hasError('min')).toBe(true);

            control?.setValue(15);
            expect(control?.hasError('min')).toBe(false);
        });

        it('should apply max validator', () => {
            const config: MachineCapabilityConfigSchema = {
                machine_type: 'test',
                config_fields: [
                    {
                        field_name: 'max_field',
                        display_name: 'Max Field',
                        field_type: 'number',
                        default_value: 100,
                        max: 50
                    }
                ]
            };

            component.config = config;
            fixture.detectChanges();

            const control = component.form.get('max_field');
            expect(control?.hasError('max')).toBe(true);

            control?.setValue(25);
            expect(control?.hasError('max')).toBe(false);
        });
    });

    describe('Value Changes', () => {
        it('should emit valueChange on form changes', () => {
            const config: MachineCapabilityConfigSchema = {
                machine_type: 'test',
                config_fields: [
                    {
                        field_name: 'test_field',
                        display_name: 'Test Field',
                        field_type: 'boolean',
                        default_value: false
                    }
                ]
            };

            component.config = config;
            fixture.detectChanges();

            const emittedValues: Record<string, any>[] = [];
            component.valueChange.subscribe(val => emittedValues.push(val));

            component.form.get('test_field')?.setValue(true);

            expect(emittedValues.length).toBe(1);
            expect(emittedValues[0]['test_field']).toBe(true);
        });
    });

    describe('Empty State', () => {
        it('should handle null config', () => {
            component.config = null;
            fixture.detectChanges();

            expect(component.visibleFields().length).toBe(0);
        });

        it('should handle empty config_fields', () => {
            component.config = { machine_type: 'test', config_fields: [] };
            fixture.detectChanges();

            expect(component.visibleFields().length).toBe(0);
        });
    });
});
