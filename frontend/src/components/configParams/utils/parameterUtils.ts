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

export interface BaseConstraintProps {
  // Type specification
  type?: string;                         // Data type (string, number, etc.)

  // Array-related constraints
  array?: any[];                         // Allowed values for selection
  array_len?: number;                    // Maximum number of items (if array)

  // String constraints
  min_len?: number;                      // Minimum string length
  max_len?: number;                      // Maximum string length
  regex?: string;                        // Regular expression pattern

  // Numeric constraints
  min_value?: number;                    // Minimum numeric value
  max_value?: number;                    // Maximum numeric value
  step?: number;                         // Step increment for numbers

  // Reference constraints
  param?: string;                        // Referenced parameter name

  // Editability flags
  editable?: boolean;                    // Whether values can be edited
  creatable?: boolean;                   // Whether new values can be created

  // Complex value structure (for objects)
  subvariables?: Record<string, ParameterConfig>; // For object/dict types with subfields
}

// Constraint structure for key and value specific constraints
export interface NestedConstraint extends BaseConstraintProps {
  parent?: BaseConstraintProps;          // Parent constraint structure
}

export interface ParameterConstraints extends BaseConstraintProps {
  // New nested constraints structure (preferred)
  key_constraints?: NestedConstraint;    // Constraints specific to keys
  value_constraints?: NestedConstraint;  // Constraints specific to values
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
