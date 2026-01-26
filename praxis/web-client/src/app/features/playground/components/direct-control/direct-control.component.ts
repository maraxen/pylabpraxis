import { Component, Input, OnChanges, SimpleChanges, Output, EventEmitter, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, FormBuilder } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MachineRead } from '@api/models/MachineRead';
import { MachineDefinitionService } from '@core/services/machine-definition.service';
import { MethodInfo, ArgumentInfo } from '@core/models/machine-definition';

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
    MatIconModule,
    MatProgressBarModule,
  ],
  templateUrl: './direct-control.component.html',
  styleUrls: ['./direct-control.component.scss']
})
export class DirectControlComponent implements OnChanges {
  @Input() machine: MachineRead | null = null;
  @Output() executeCommand = new EventEmitter<{ machineName: string, methodName: string, args: any }>();

  methods = signal<MethodInfo[]>([]);
  selectedMethod = signal<MethodInfo | null>(null);
  form: FormGroup = new FormGroup({});

  // State signals for command execution
  commandResult = signal<any>(null);
  commandError = signal<string | null>(null);
  isExecuting = signal(false);

  private fb = inject(FormBuilder);
  private machineDefinitionService = inject(MachineDefinitionService);

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['machine'] && this.machine) {
      this.loadMethods();
    }
  }

  private loadMethods() {
    if (!this.machine) return;
    // machine_type may be present on extended machine objects but not in base MachineRead type
    const machineAny = this.machine as Record<string, unknown>;
    const machineType = machineAny['machine_type'] as string | undefined;
    if (machineType) {
      this.methods.set(this.getMethodsFromMachineType(machineType));
    }
  }

  private getMethodsFromMachineType(type: string): MethodInfo[] {
    const definition = this.machineDefinitionService.getDefinition(type);
    return definition?.methods ?? [];
  }

  onMethodSelected(method: MethodInfo) {
    this.selectedMethod.set(method);
    this.buildForm(method);
  }

  buildForm(method: MethodInfo) {
    const group: Record<string, FormControl> = {};
    (method.args || []).forEach((arg: ArgumentInfo) => {
      const initialValue = arg.default !== undefined ? arg.default : '';
      group[arg.name] = new FormControl(initialValue);
    });
    this.form = this.fb.group(group);
  }

  getArgType(type: string): 'number' | 'boolean' | 'text' | 'list' | 'select' {
    if (type.includes('int') || type.includes('float')) return 'number';
    if (type.includes('bool')) return 'boolean';
    if (type.startsWith('list[')) return 'list';
    if (type.startsWith('Literal[') || type.includes('enum')) return 'select';
    return 'text';
  }

  runCommand() {
    if (!this.form.valid || !this.machine || !this.selectedMethod()) return;

    this.isExecuting.set(true);
    this.commandError.set(null);
    this.commandResult.set(null);

    const args = this.form.value;
    const currentMethod = this.selectedMethod();
    // Process args to correct types if needed
    (currentMethod?.args || []).forEach((arg: ArgumentInfo) => {
      const type = this.getArgType(arg.type);
      if (type === 'number' && args[arg.name] !== undefined) {
        args[arg.name] = Number(args[arg.name]);
      }
    });

    this.executeCommand.emit({
      machineName: this.machine.name,
      methodName: currentMethod!.name,
      args: args
    });
  }

  // Method for parent to call with result
  handleCommandResult(result: any) {
    this.isExecuting.set(false);
    this.commandResult.set(result);
  }

  handleCommandError(error: string) {
    this.isExecuting.set(false);
    this.commandError.set(error);
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
