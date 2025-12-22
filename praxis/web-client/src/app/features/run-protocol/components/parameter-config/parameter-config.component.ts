import { Component, ChangeDetectionStrategy, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup } from '@angular/forms';
import { FormlyModule, FormlyFieldConfig } from '@ngx-formly/core';
import { ProtocolDefinition } from '../../../protocols/models/protocol.models';
import { of } from 'rxjs';

@Component({
  selector: 'app-parameter-config',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormlyModule
  ],
  template: `
    <div class="parameter-config-container">
      <formly-form [form]="formGroup" [fields]="fields" [model]="model"></formly-form>
    </div>
  `,
  styles: [`
    .parameter-config-container {
      padding: 16px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ParameterConfigComponent implements OnChanges {
  @Input() protocol: ProtocolDefinition | null = null;
  @Input() formGroup: FormGroup = new FormGroup({});

  model: any = {};
  fields: FormlyFieldConfig[] = [];

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['protocol'] && this.protocol) {
      this.buildForm(this.protocol);
    }
  }

  private buildForm(protocol: ProtocolDefinition) {
    // Demo: If protocol name contains "Complex", show complex fields.
    // Otherwise show simple placeholder.
    
    if (protocol.name.includes('Complex')) {
      this.fields = [
        {
          key: 'machine',
          type: 'asset-selector',
          templateOptions: {
            label: 'Select Machine',
            placeholder: 'Search for a machine',
            required: true,
            assetType: 'machine'
          },
        },
        {
          key: 'mode',
          type: 'chips',
          templateOptions: {
            label: 'Execution Mode',
            required: true,
            multiple: false,
            options: of([
              { value: 'dry_run', label: 'Dry Run' },
              { value: 'live', label: 'Live' }
            ])
          },
        },
        {
          key: 'volumes',
          type: 'repeat',
          templateOptions: {
            addText: 'Add Volume',
          },
          fieldArray: {
            type: 'input',
            templateOptions: {
              type: 'number',
              label: 'Volume (uL)',
              required: true
            }
          }
        }
      ];
    } else {
      this.fields = [
        {
          key: 'example_param',
          type: 'input',
          templateOptions: {
            label: 'Example Parameter (Placeholder)',
            placeholder: 'Enter value',
            required: true,
          },
        }
      ];
    }
  }
}