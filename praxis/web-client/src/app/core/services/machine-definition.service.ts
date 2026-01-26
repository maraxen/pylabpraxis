
import { Injectable } from '@angular/core';
import { PLR_MACHINE_DEFINITIONS, PlrMachineDefinition } from '@assets/browser-data/plr-definitions';
import { MachineDefinition, MethodInfo } from '@core/models/machine-definition';

// Placeholder method definitions until real introspection is available
const DEFAULT_LIQUID_HANDLER_METHODS: MethodInfo[] = [
  { name: 'setup', description: 'Initialize the machine', args: [] },
  { name: 'stop', description: 'Stop the machine', args: [] },
  {
    name: 'aspirate', description: 'Aspirate liquid', args: [
      { name: 'volume', type: 'float', description: 'Volume in µL' },
      { name: 'well', type: 'str', description: 'Target well (e.g., A1)' }
    ]
  },
  {
    name: 'dispense', description: 'Dispense liquid', args: [
      { name: 'volume', type: 'float', description: 'Volume in µL' },
      { name: 'well', type: 'str', description: 'Target well (e.g., A1)' }
    ]
  },
];

const DEFAULT_PLATE_READER_METHODS: MethodInfo[] = [
  { name: 'setup', description: 'Initialize the reader', args: [] },
  { name: 'stop', description: 'Stop the reader', args: [] },
  {
    name: 'read_absorbance', description: 'Read absorbance', args: [
      { name: 'wavelength', type: 'int', description: 'Wavelength in nm' }
    ]
  },
];

const DEFAULT_SHAKER_METHODS: MethodInfo[] = [
  { name: 'setup', description: 'Initialize the shaker', args: [] },
  { name: 'stop', description: 'Stop the shaker', args: [] },
  {
    name: 'shake', description: 'Start shaking', args: [
      { name: 'speed', type: 'int', description: 'Speed in RPM' },
      { name: 'duration', type: 'float', description: 'Duration in seconds' }
    ]
  },
];

@Injectable({
  providedIn: 'root'
})
export class MachineDefinitionService {
  private definitions: PlrMachineDefinition[] = PLR_MACHINE_DEFINITIONS;

  getDefinition(machineType: string): MachineDefinition | undefined {
    const plrDef = this.definitions.find(def => def.machine_type === machineType);
    if (!plrDef) return undefined;

    // Map PLR definition to MachineDefinition with placeholder methods
    let methods: MethodInfo[] = [];
    switch (plrDef.machine_type) {
      case 'LiquidHandler':
        methods = DEFAULT_LIQUID_HANDLER_METHODS;
        break;
      case 'PlateReader':
        methods = DEFAULT_PLATE_READER_METHODS;
        break;
      case 'Shaker':
        methods = DEFAULT_SHAKER_METHODS;
        break;
      default:
        methods = [
          { name: 'setup', description: 'Initialize', args: [] },
          { name: 'stop', description: 'Stop', args: [] },
        ];
    }

    return {
      machine_type: plrDef.machine_type,
      methods
    };
  }
}
