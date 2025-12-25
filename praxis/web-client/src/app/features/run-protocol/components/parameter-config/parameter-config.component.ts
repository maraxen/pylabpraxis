import { Component, ChangeDetectionStrategy, Input, OnChanges, SimpleChanges, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup } from '@angular/forms';
import { FormlyModule, FormlyFieldConfig } from '@ngx-formly/core';
import { MatDividerModule } from '@angular/material/divider';
import { ProtocolDefinition, ParameterMetadata, AssetRequirement } from '../../../protocols/models/protocol.models';

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
      @if (hasAssets()) {
        <section class="section-header">
          <h3>Assets</h3>
          <p class="section-subtitle">Select or create the required resources and machines</p>
        </section>
        <formly-form [form]="formGroup" [fields]="assetFields()" [model]="model"></formly-form>
        <mat-divider></mat-divider>
      }

      @if (hasParameters()) {
        <section class="section-header">
          <h3>Parameters</h3>
          <p class="section-subtitle">Configure the protocol execution parameters</p>
        </section>
        <formly-form [form]="formGroup" [fields]="paramFields()" [model]="model"></formly-form>
      }

      @if (!hasAssets() && !hasParameters()) {
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
  assetFields = signal<FormlyFieldConfig[]>([]);
  paramFields = signal<FormlyFieldConfig[]>([]);

  hasAssets = signal(false);
  hasParameters = signal(false);

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['protocol'] && this.protocol) {
      this.buildForm(this.protocol);
    }
  }

  private buildForm(protocol: ProtocolDefinition) {
    // Track index per PLR type for unique auto-assignment
    const typeIndexMap = new Map<string, number>();

    // Build asset fields with autoSelectIndex for unique assignment
    const assetConfigs: FormlyFieldConfig[] = (protocol.assets || []).map(asset => {
      const plrType = this.extractPlrType(asset.type_hint_str);
      const currentIndex = typeIndexMap.get(plrType) || 0;
      typeIndexMap.set(plrType, currentIndex + 1);
      return this.createAssetField(asset, currentIndex);
    });
    this.assetFields.set(assetConfigs);
    this.hasAssets.set(assetConfigs.length > 0);

    // Build parameter fields (exclude state, deck params, and typed assets)
    const paramConfigs: FormlyFieldConfig[] = (protocol.parameters || [])
      .filter(p => !p.is_deck_param && p.name !== 'state')
      .map(param => this.createParamField(param));
    this.paramFields.set(paramConfigs);
    this.hasParameters.set(paramConfigs.length > 0);

    // Initialize model with defaults
    protocol.assets?.forEach(asset => {
      this.model[asset.name] = { mode: 'auto' }; // Default to auto
    });
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

  private createAssetField(asset: AssetRequirement, autoSelectIndex: number): FormlyFieldConfig {
    // Determine PLR type filter from type_hint_str (e.g., "Plate", "TipRack", "LiquidHandler")
    const plrType = this.extractPlrType(asset.type_hint_str);
    const assetType = this.isResource(plrType) ? 'resource' : 'machine';

    return {
      key: asset.name,
      type: 'asset-selector',
      props: {
        label: this.formatLabel(asset.name),
        variableName: asset.name,  // Pass actual variable name
        placeholder: `Search ${plrType}...`,
        required: !asset.optional,
        description: asset.description,
        assetType: assetType,
        plrTypeFilter: plrType,
        showAutoOption: true,
        autoSelectIndex: autoSelectIndex,  // Index for unique auto-selection
      },
    };
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

  private extractPlrType(typeHint: string): string {
    // Extract the class name from type hints like "pylabrobot.resources.Plate" or just "Plate"
    const parts = typeHint.split('.');
    return parts[parts.length - 1];
  }

  private isResource(plrType: string): boolean {
    // Common resource types vs machine types
    const resourceTypes = ['Plate', 'TipRack', 'Trough', 'Reservoir', 'Tube', 'Lid', 'Resource'];
    const machineTypes = ['LiquidHandler', 'PlateReader', 'Incubator', 'Robot', 'Machine'];

    if (machineTypes.some(t => plrType.includes(t))) {
      return false;
    }
    if (resourceTypes.some(t => plrType.includes(t))) {
      return true;
    }
    // Default to resource
    return true;
  }

  private formatLabel(name: string): string {
    // Convert snake_case to Title Case
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  }
}