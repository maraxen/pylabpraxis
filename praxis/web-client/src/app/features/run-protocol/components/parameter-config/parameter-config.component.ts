import { Component, ChangeDetectionStrategy, Input, OnChanges, SimpleChanges, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup } from '@angular/forms';
import { FormlyModule, FormlyFieldConfig } from '@ngx-formly/core';
import { MatDividerModule } from '@angular/material/divider';
import { ProtocolDefinition, ParameterMetadata } from '../../../protocols/models/protocol.models';

@Component({
  selector: 'app-parameter-config',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormlyModule,
    MatDividerModule
  ],
  template: `
    <div class="parameter-config-container">
      @if (hasParameters()) {
        <section class="section-header">
          <h3>Parameters</h3>
          <p class="section-subtitle">Configure the protocol execution parameters</p>
        </section>
        <formly-form [form]="formGroup" [fields]="paramFields()" [model]="model"></formly-form>
      }

      @if (!hasParameters()) {
        <div class="empty-state">
          <p>This protocol has no configurable parameters.</p>
        </div>
      }
    </div>
  `,
  styles: [`
    .parameter-config-container {
      padding: 16px 0;
    }
    .section-header {
      margin-bottom: 16px;
    }
    .section-header h3 {
      margin: 0 0 4px;
      font-size: 1.1rem;
    }
    .section-subtitle {
      margin: 0;
      color: var(--sys-on-surface-variant);
      font-size: 0.9rem;
    }
    mat-divider {
      margin: 24px 0;
    }
    .empty-state {
      text-align: center;
      padding: 32px;
      color: var(--sys-on-surface-variant);
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ParameterConfigComponent implements OnChanges {
  @Input() protocol: ProtocolDefinition | null = null;
  @Input() formGroup: FormGroup = new FormGroup({});

  model: Record<string, unknown> = {};
  paramFields = signal<FormlyFieldConfig[]>([]);

  hasParameters = signal(false);

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['protocol'] && this.protocol) {
      this.buildForm(this.protocol);
    }
  }

  private buildForm(protocol: ProtocolDefinition) {
    // Build parameter fields (exclude state, deck params, and typed assets)
    const paramConfigs: FormlyFieldConfig[] = (protocol.parameters || [])
      .filter(p => !p.is_deck_param && p.name !== 'state')
      .map(param => this.createParamField(param));
    this.paramFields.set(paramConfigs);
    this.hasParameters.set(paramConfigs.length > 0);

    // Initialize model with defaults
    protocol.parameters?.forEach(param => {
      if (param.default_value_repr && param.default_value_repr !== 'None') {
        try {
          this.model[param.name] = JSON.parse(param.default_value_repr);
        } catch {
          this.model[param.name] = param.default_value_repr;
        }
      }
    });
  }

  private createParamField(param: ParameterMetadata): FormlyFieldConfig {
    const baseConfig: FormlyFieldConfig = {
      key: param.name,
      props: {
        label: this.formatLabel(param.name),
        required: !param.optional,
        description: param.description,
      },
    };

    // Check for explicit field_type from backend
    if (param.field_type === 'index_selector' && param.itemized_spec) {
      return {
        ...baseConfig,
        type: 'index-selector',
        props: {
          ...baseConfig.props,
          itemsX: param.itemized_spec.items_x,
          itemsY: param.itemized_spec.items_y,
          linkedTo: param.linked_to,
        },
      };
    }

    // Map type to input type
    const typeHint = param.type_hint.toLowerCase();
    if (typeHint.includes('float') || typeHint.includes('int')) {
      return {
        ...baseConfig,
        type: 'input',
        props: {
          ...baseConfig.props,
          type: 'number',
          min: param.constraints.min_value,
          max: param.constraints.max_value,
        },
      };
    } else if (typeHint.includes('bool')) {
      return {
        ...baseConfig,
        type: 'checkbox',
      };
    } else if (param.constraints.options && param.constraints.options.length > 0) {
      return {
        ...baseConfig,
        type: 'select',
        props: {
          ...baseConfig.props,
          options: param.constraints.options.map(opt => ({ label: String(opt), value: opt })),
        },
      };
    } else {
      // Default: text input
      return {
        ...baseConfig,
        type: 'input',
        props: {
          ...baseConfig.props,
          type: 'text',
        },
      };
    }
  }

  private formatLabel(name: string): string {
    // Convert snake_case to Title Case
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  }
}