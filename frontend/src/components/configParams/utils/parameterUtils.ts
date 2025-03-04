import { UniqueIdentifier } from '@dnd-kit/core';

// Base properties for all value types
export interface BaseValueProps {
  id: string; // Unique identifier generated with crypto.randomUUID()
  value: any; // The actual value (string, number, boolean, etc.)
  type?: string; // Type of the value (string, number, boolean, etc.)
  isFromParam?: boolean; // Whether this value comes from a parameter
  paramSource?: string; // The parameter source name
  isEditable?: boolean; // Whether this value can be edited
}

// Value data with optional subvariables
export interface ValueData extends BaseValueProps {
  subvariables?: Record<string, SubvariableValue>; // Optional subvariables
}

// Subvariable value extends base props
export interface SubvariableValue extends BaseValueProps {
  // Specific subvariable properties can be added here
}

export interface ValueMetadata {
  isFromParam: boolean;
  paramSource?: string;
  isEditable: boolean;
  type: string;
}

// Group data structure
export interface GroupData {
  id: string; // Unique group identifier
  name: string; // Group display name (what was previously the key)
  values: ValueData[]; // Array of value data
  isFromParam?: boolean;
  paramSource?: string;
  isEditable?: boolean;
}

// Parameter configuration types

export interface ParameterConstraints {
  // Common constraints
  min_value?: number;
  max_value?: number;
  step?: number;

  // Array-related constraints
  array?: any[];
  array_len?: number;

  // Mapping-related constraints
  parent?: string;
  key_type?: string;
  value_type?: string;
  key_array?: any[];
  value_array?: any[];
  key_param?: string;
  value_param?: string;
  key_array_len?: number;
  value_array_len?: number;
  hierarchical?: boolean;

  // Creatable flags
  creatable?: boolean;
  creatable_key?: boolean;
  creatable_value?: boolean;

  // Subvariables for complex mappings
  subvariables?: Record<string, ParameterConfig>;
}

export interface ParameterConfig {
  type: any;
  description?: string;
  default?: any;
  required?: boolean;
  constraints?: ParameterConstraints;
  id?: string;
}

export interface SubvariableConfig extends ParameterConfig {
  // Additional properties for subvariables
}

export interface SubvariablesData {
  values: ValueData[];
  [key: string]: any;  // For subvariable values
}

// Define the types for group data to properly handle both array and object with values
export interface NestedMappingProps {
  name: string;
  value: Record<string, GroupData>; // Changed to map group IDs to GroupData
  config: ParameterConfig;
  onChange: (value: any) => void;
  parameters?: Record<string, ParameterConfig>;
}

// Other utility types
export interface DragState {
  active: string | null;
  over: string | null;
}

export interface SortableItemProps {
  id: string;
  value: string;
  keyValue: string;
  type?: string;
  isFromParam?: boolean;
  paramSource?: string;
  isEditable?: boolean;
  isEditing?: boolean;
  onFocus?: () => void;
  onValueChange?: (newValue: any) => void;
  onBlur?: () => void;
  onRemove?: () => void;
}
