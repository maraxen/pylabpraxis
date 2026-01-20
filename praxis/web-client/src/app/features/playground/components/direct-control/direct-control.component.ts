import { Component, Input, OnChanges, SimpleChanges, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, FormBuilder } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MachineRead } from '../../../../core/api-generated/models/MachineRead';

// Interface for method info from API
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
    MatCheckboxModule
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
  
  private http = inject(HttpClient);
  private fb = inject(FormBuilder);

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['machine'] && this.machine) {
      this.loadMethods();
    }
  }

  loadMethods() {
    if (!this.machine) return;
    
    // Attempt to find definition ID. 
    const machineAny = this.machine as any;
    const defId = machineAny.machine_definition_accession_id || 
                  machineAny.frontend_definition_accession_id;

    if (defId) {
      this.http.get<MethodInfo[]>(`/api/v1/machines/definitions/${defId}/methods`)
        .subscribe({
          next: (methods) => {
            this.methods = methods;
            this.selectedMethod = null;
            this.form = new FormGroup({});
          },
          error: (err) => console.error('Failed to load machine methods', err)
        });
    } else {
      console.warn('No definition ID found for machine', this.machine.name);
      this.methods = [];
    }
  }

  onMethodSelected(method: MethodInfo) {
    this.selectedMethod = method;
    this.buildForm(method);
  }

  buildForm(method: MethodInfo) {
    const group: any = {};
    method.args.forEach(arg => {
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
    this.selectedMethod.args.forEach(arg => {
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
}
