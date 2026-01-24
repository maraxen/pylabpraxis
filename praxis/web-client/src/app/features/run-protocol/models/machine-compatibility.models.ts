
import { Machine } from '@features/assets/models/asset.models';

export interface MachineCompatibility {
  machine: Machine;
  compatibility: {
    is_compatible: boolean;
    missing_capabilities: any[];
    matched_capabilities: string[];
    warnings: string[];
  };
}
