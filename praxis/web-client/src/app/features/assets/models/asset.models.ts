
export enum MachineStatus {
  OFFLINE = 'offline',
  IDLE = 'idle',
  RUNNING = 'running',
  ERROR = 'error',
  MAINTENANCE = 'maintenance',
  UNKNOWN = 'unknown'
}

export enum ResourceStatus {
  AVAILABLE = 'available',
  IN_USE = 'in_use',
  DEPLETED = 'depleted',
  EXPIRED = 'expired',
  UNKNOWN = 'unknown'
}

export interface AssetBase {
  accession_id: string;
  name: string;
  created_at?: string;
  updated_at?: string;
}

export interface Machine extends AssetBase {
  status: MachineStatus;
  status_details?: string;
  description?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  connection_info?: Record<string, any>;
  is_simulation_override?: boolean;
}

export interface MachineCreate {
  name: string;
  status?: MachineStatus;
  description?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  connection_info?: Record<string, any>;
  is_simulation_override?: boolean;
  machine_definition_accession_id?: string;
}

export interface Resource extends AssetBase {
  status: ResourceStatus;
  status_details?: string;
  resource_definition_accession_id?: string;
  parent_accession_id?: string;
  children?: Resource[];
}

export interface ResourceCreate {
  name: string;
  status?: ResourceStatus;
  resource_definition_accession_id?: string;
  parent_accession_id?: string;
}

export interface MachineDefinition {
    accession_id: string;
    name: string;
    fqn?: string;
    description?: string;
    machine_category?: string;
    manufacturer?: string;
    model?: string;
    nominal_volume_ul?: number;
}
export interface ResourceDefinition {
    accession_id: string;
    name: string;
    fqn?: string;
    description?: string;
    resource_type?: string;
    manufacturer?: string;
    model?: string;
    nominal_volume_ul?: number;
    is_consumable: boolean;
    // Dynamic filter fields
    num_items?: number;
    plate_type?: string;
    well_volume_ul?: number;
    tip_volume_ul?: number;
    vendor?: string;
    plr_category?: string;
}

