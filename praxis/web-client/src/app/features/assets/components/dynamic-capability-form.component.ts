import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges, inject, signal, computed, effect } from '@angular/core';

import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PraxisSelectComponent, SelectOption } from '@shared/components/praxis-select/praxis-select.component';
import { PraxisMultiselectComponent } from '@shared/components/praxis-multiselect/praxis-multiselect.component';
import { MachineCapabilityConfigSchema, CapabilityConfigField } from '../models/asset.models';

@Component({
  selector: 'app-dynamic-capability-form',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatTooltipModule,
    PraxisSelectComponent,
    PraxisMultiselectComponent
  ],
  template: `
    <form [formGroup]="form" class="flex flex-col gap-3">
      @for (field of visibleFields(); track field.field_name) {
        <div class="capability-field" 
             [attr.data-field]="field.field_name"
             role="group"
             [attr.aria-label]="field.display_name">
          
          <!-- Boolean Toggle -->
          @if (field.field_type === 'boolean') {
            <div class="py-2">
              <mat-slide-toggle 
                [formControlName]="field.field_name" 
                color="primary"
                [id]="'cap-' + field.field_name"
                [attr.aria-describedby]="field.help_text ? 'help-' + field.field_name : null">
                {{ field.display_name }}
                @if (field.required) {
                  <span class="text-red-500 ml-1">*</span>
                }
              </mat-slide-toggle>
              @if (field.help_text) {
                <div [id]="'help-' + field.field_name" 
                     class="text-xs sys-text-secondary mt-1 ml-12">
                  {{ field.help_text }}
                </div>
              }
            </div>
          }

          <!-- Number Input -->
          @if (field.field_type === 'number') {
            <mat-form-field appearance="outline" class="w-full">
              <mat-label>{{ field.display_name }}</mat-label>
              <input matInput 
                     type="number" 
                     [formControlName]="field.field_name"
                     [id]="'cap-' + field.field_name"
                     [attr.min]="field.min"
                     [attr.max]="field.max"
                     [attr.aria-describedby]="field.help_text ? 'help-' + field.field_name : null">
              @if (field.help_text) {
                <mat-hint [id]="'help-' + field.field_name">{{ field.help_text }}</mat-hint>
              }
              @if (form.get(field.field_name)?.hasError('required')) {
                <mat-error>{{ field.display_name }} is required</mat-error>
              }
              @if (form.get(field.field_name)?.hasError('min')) {
                <mat-error>Minimum value is {{ field.min }}</mat-error>
              }
              @if (form.get(field.field_name)?.hasError('max')) {
                <mat-error>Maximum value is {{ field.max }}</mat-error>
              }
            </mat-form-field>
          }

          <!-- Select -->
          @if (field.field_type === 'select') {
            <div class="mb-4">
              <label class="text-xs font-medium text-gray-500 mb-1 block">{{ field.display_name }}</label>
              <app-praxis-select
                [placeholder]="field.display_name"
                [formControlName]="field.field_name"
                [options]="mapToSelectOptions(field.options || [])"
              ></app-praxis-select>
              @if (field.help_text) {
                <div class="text-xs text-gray-400 mt-1">{{ field.help_text }}</div>
              }
              @if (form.get(field.field_name)?.hasError('required')) {
                <div class="text-xs text-red-500 mt-1">{{ field.display_name }} is required</div>
              }
            </div>
          }

          <!-- Multiselect -->
          @if (field.field_type === 'multiselect') {
            <div class="mb-4">
              <label class="text-xs font-medium text-gray-500 mb-1 block">{{ field.display_name }}</label>
              <app-praxis-multiselect
                [placeholder]="field.display_name"
                [formControlName]="field.field_name"
                [options]="mapToFilterOptions(field.options || [])"
                [value]="form.get(field.field_name)?.value"
                (valueChange)="form.get(field.field_name)?.setValue($event)"
              ></app-praxis-multiselect>
              @if (field.help_text) {
                <div class="text-xs text-gray-400 mt-1">{{ field.help_text }}</div>
              }
            </div>
          }

        </div>
      }

      @if (!config || config.config_fields.length === 0) {
        <div class="text-sm sys-text-secondary italic p-3 border border-dashed rounded sys-surface text-center">
          No configurable capabilities for this machine type.
        </div>
      }
    </form>
  `,
  styles: [`
    :host {
      display: block;
    }
    
    .capability-field {
      transition: opacity 0.2s ease, transform 0.2s ease;
    }
    
    /* Theme-aware styling using CSS variables */
    .sys-text-secondary {
      color: var(--mat-sys-on-surface-variant);
    }
    
    .sys-surface {
      background-color: var(--mat-sys-surface-variant);
    }
  `]
})
export class DynamicCapabilityFormComponent implements OnInit, OnChanges {
  @Input() config: MachineCapabilityConfigSchema | undefined | null;
  @Input() initialValue: Record<string, any> | undefined | null;
  @Output() valueChange = new EventEmitter<Record<string, any>>();

  private fb = inject(FormBuilder);
  form: FormGroup = this.fb.group({});

  // Signal to track current form values for conditional visibility
  private formValues = signal<Record<string, any>>({});

  // Computed: filter fields based on depends_on conditions
  visibleFields = computed(() => {
    const fields = this.config?.config_fields || [];
    const values = this.formValues();

    return fields.filter(field => {
      if (!field.depends_on) return true;

      // Parse "field_name" or "field_name=value"
      const parts = field.depends_on.split('=');
      const depField = parts[0];
      const depValue = parts.length > 1 ? parts[1] : undefined;
      const currentValue = values[depField];

      if (depValue !== undefined) {
        return String(currentValue) === depValue;
      }
      // Truthy check for boolean dependencies
      return !!currentValue;
    });
  });

  mapToSelectOptions(options: string[]): SelectOption[] {
    return options.map(opt => ({ label: opt, value: opt }));
  }

  mapToFilterOptions(options: string[]) {
    return options.map(opt => ({ label: opt, value: opt }));
  }

  ngOnInit() {
    this.buildForm();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['config'] && !changes['config'].firstChange) {
      this.buildForm();
    }
    if (changes['initialValue'] && !changes['initialValue'].firstChange) {
      if (this.form && this.initialValue) {
        this.form.patchValue(this.initialValue, { emitEvent: false });
        this.formValues.set({ ...this.form.value });
      }
    }
  }

  private buildForm() {
    if (!this.config?.config_fields) {
      this.form = this.fb.group({});
      this.formValues.set({});
      return;
    }

    const group: Record<string, any> = {};

    this.config.config_fields.forEach(field => {
      // Determine initial value: explicit initial value > field default > null
      let value = field.default_value;
      if (this.initialValue && Object.prototype.hasOwnProperty.call(this.initialValue, field.field_name)) {
        value = this.initialValue[field.field_name];
      }

      // Build validators array
      const validators: ((control: AbstractControl) => ValidationErrors | null)[] = [];

      if (field.required) {
        validators.push(Validators.required);
      }

      if (field.field_type === 'number') {
        if (field.min !== undefined) {
          validators.push(Validators.min(field.min));
        }
        if (field.max !== undefined) {
          validators.push(Validators.max(field.max));
        }
      }

      group[field.field_name] = [value, validators];
    });

    this.form = this.fb.group(group);
    this.formValues.set({ ...this.form.value });

    // Subscribe to changes and update signal
    this.form.valueChanges.subscribe(val => {
      this.formValues.set({ ...val });
      this.valueChange.emit(val);
    });
  }
}
