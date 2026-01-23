import { Component, Input, OnChanges, SimpleChanges, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, FormBuilder } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MachineRead } from '@api/models/MachineRead';

// Interface for method info
interface ArgumentInfo {
  name: string;
  type?: string;
  default?: any;
}

interface MethodInfo {
  name: string;
  doc?: string;
  args: ArgumentInfo[];
}

@Component({
  selector: 'app-direct-control',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatButtonModule,
    MatCheckboxModule,
    MatIconModule
  ],
  templateUrl: './direct-control.component.html',
  styleUrls: ['./direct-control.component.scss']
})
export class DirectControlComponent implements OnChanges {
  @Input() machine: MachineRead | null = null;
  @Output() executeCommand = new EventEmitter<{ machineName: string, methodName: string, args: any }>();

  methods: MethodInfo[] = [];
  selectedMethod: MethodInfo | null = null;
  form: FormGroup = new FormGroup({});

  private fb = inject(FormBuilder);

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['machine'] && this.machine) {
      this.loadMethods();
    }
  }

  loadMethods() {
    if (!this.machine) return;

    const machineAny = this.machine as any;
    const category = machineAny.machine_category || 'Other';

    // Generate methods based on machine category using PyLabRobot frontend interfaces
    this.methods = this.getMockMethodsForCategory(category);
    this.selectedMethod = null;
    this.form = new FormGroup({});
  }

  /**
   * Generate methods for a machine category based on PyLabRobot frontend interfaces.
   * All machines have setup() and close() methods, plus category-specific operations.
   */
  private getMockMethodsForCategory(category: string): MethodInfo[] {
    // Common lifecycle methods ALL machines have
    const commonMethods: MethodInfo[] = [
      { name: 'setup', doc: 'Initialize and connect to the machine', args: [] },
      { name: 'stop', doc: 'Disconnect and cleanup machine resources', args: [] },
    ];

    // Category-specific methods
    const categoryMethods: MethodInfo[] = (() => {
      switch (category) {
        case 'LiquidHandler':
          return [
            {
              name: 'aspirate', doc: 'Aspirate liquid from wells', args: [
                { name: 'volume', type: 'float', default: 100 },
                { name: 'flow_rate', type: 'float', default: null }
              ]
            },
            {
              name: 'dispense', doc: 'Dispense liquid to wells', args: [
                { name: 'volume', type: 'float', default: 100 },
                { name: 'flow_rate', type: 'float', default: null }
              ]
            },
            {
              name: 'pick_up_tips', doc: 'Pick up tips from a tip rack', args: [
                { name: 'use_channels', type: 'list[int]', default: null }
              ]
            },
            { name: 'drop_tips', doc: 'Drop tips to trash or rack', args: [] },
            {
              name: 'move_to', doc: 'Move pipetting head to a position', args: [
                { name: 'x', type: 'float' },
                { name: 'y', type: 'float' },
                { name: 'z', type: 'float' }
              ]
            },
          ];
        case 'PlateReader':
          return [
            { name: 'open', doc: 'Open the plate reader lid for plate loading', args: [] },
            { name: 'close', doc: 'Close the plate reader lid', args: [] },
            {
              name: 'read_absorbance', doc: 'Read absorbance at wavelength', args: [
                { name: 'wavelength', type: 'int', default: 450 }
              ]
            },
            {
              name: 'read_fluorescence', doc: 'Read fluorescence intensity', args: [
                { name: 'excitation', type: 'int', default: 485 },
                { name: 'emission', type: 'int', default: 528 }
              ]
            },
            { name: 'read_luminescence', doc: 'Read luminescence', args: [] },
          ];
        case 'Shaker':
          return [
            {
              name: 'shake', doc: 'Start shaking at specified speed', args: [
                { name: 'speed', type: 'int', default: 300 },
                { name: 'duration', type: 'float', default: null }
              ]
            },
            { name: 'stop', doc: 'Stop shaking', args: [] },
            {
              name: 'set_temperature', doc: 'Set heater temperature', args: [
                { name: 'temperature', type: 'float', default: 37 }
              ]
            },
          ];
        case 'Centrifuge':
          return [
            {
              name: 'spin', doc: 'Spin at specified speed', args: [
                { name: 'speed', type: 'int', default: 3000 },
                { name: 'duration', type: 'float', default: 60 },
                { name: 'acceleration', type: 'int', default: null }
              ]
            },
            { name: 'open_lid', doc: 'Open the centrifuge lid', args: [] },
            { name: 'close_lid', doc: 'Close the centrifuge lid', args: [] },
          ];
        case 'Incubator':
          return [
            {
              name: 'set_temperature', doc: 'Set incubation temperature', args: [
                { name: 'temperature', type: 'float', default: 37 }
              ]
            },
            {
              name: 'set_co2', doc: 'Set CO2 percentage', args: [
                { name: 'co2_percent', type: 'float', default: 5 }
              ]
            },
            {
              name: 'set_humidity', doc: 'Set humidity percentage', args: [
                { name: 'humidity_percent', type: 'float', default: 95 }
              ]
            },
          ];
        default:
          return [
            { name: 'get_status', doc: 'Get current machine status', args: [] },
          ];
      }
    })();

    return [...commonMethods, ...categoryMethods];
  }

  onMethodSelected(method: MethodInfo) {
    this.selectedMethod = method;
    this.buildForm(method);
  }

  buildForm(method: MethodInfo) {
    const group: any = {};
    (method.args || []).forEach(arg => {
      const initialValue = arg.default !== undefined ? arg.default : '';
      group[arg.name] = new FormControl(initialValue);
    });
    this.form = this.fb.group(group);
  }

  getArgType(arg: ArgumentInfo): 'number' | 'checkbox' | 'text' {
    if (!arg.type) return 'text';
    const type = arg.type.toLowerCase();
    if (type.includes('int') || type.includes('float')) return 'number';
    if (type.includes('bool')) return 'checkbox';
    return 'text';
  }

  runCommand() {
    if (!this.machine || !this.selectedMethod) return;

    const args = this.form.value;
    // Process args to correct types if needed
    (this.selectedMethod.args || []).forEach(arg => {
      const type = this.getArgType(arg);
      if (type === 'number' && args[arg.name] !== undefined) {
        args[arg.name] = Number(args[arg.name]);
      }
    });

    this.executeCommand.emit({
      machineName: this.machine.name,
      methodName: this.selectedMethod.name,
      args: args
    });
  }

  // === UI Helper Methods ===

  getMachineCategory(): string {
    const machineAny = this.machine as any;
    return machineAny?.machine_category || 'Machine';
  }

  isLifecycleMethod(name: string): boolean {
    return ['setup', 'stop'].includes(name);
  }

  getMethodIcon(name: string): string {
    const iconMap: Record<string, string> = {
      'setup': 'power_settings_new',
      'stop': 'power_off',
      'aspirate': 'arrow_upward',
      'dispense': 'arrow_downward',
      'pick_up_tips': 'upload',
      'drop_tips': 'download',
      'move_to': 'open_with',
      'open': 'eject',
      'close': 'input',
      'read_absorbance': 'wb_sunny',
      'read_fluorescence': 'flare',
      'read_luminescence': 'light_mode',
      'shake': 'vibration',
      'spin': 'loop',
      'open_lid': 'vertical_align_top',
      'close_lid': 'vertical_align_bottom',
      'set_temperature': 'thermostat',
      'set_co2': 'air',
      'set_humidity': 'water_drop',
      'get_status': 'info',
    };
    return iconMap[name] || 'play_arrow';
  }

  formatMethodName(name: string): string {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  }

  formatArgName(name: string): string {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  }
}
