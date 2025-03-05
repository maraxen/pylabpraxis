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

// Constraint structure for key and value specific constraints
export interface NestedConstraint {
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

export interface ParameterConstraints {
  // Common constraints (apply to both keys and values)
  min_value?: number;                    // Minimum numeric value
  max_value?: number;                    // Maximum numeric value
  step?: number;                         // Step increment for numbers
  regex?: string;                        // Regular expression pattern
  min_len?: number;                      // Minimum string length
  max_len?: number;                      // Maximum string length
  array?: any[];                         // Common array of allowed values
  array_len?: number;                    // Common array length limit

  // Mapping structure specification
  parent?: string;                       // Indicates if this is a 'key' or 'value' parameter

  // New nested constraints structure (preferred)
  key_constraints?: NestedConstraint;    // Constraints specific to keys
  value_constraints?: NestedConstraint;  // Constraints specific to values

  // Legacy support for direct type specification
  key_type?: string;                     // Legacy key type specification
  value_type?: string;                   // Legacy value type specification

  // Legacy support for direct constraints
  key_array?: any[];                     // Legacy: allowed key values
  value_array?: any[];                   // Legacy: allowed value values
  key_param?: string;                    // Legacy: parameter reference for keys
  value_param?: string;                  // Legacy: parameter reference for values
  key_array_len?: number;                // Legacy: max keys allowed
  value_array_len?: number;              // Legacy: max values allowed per key
  hierarchical?: boolean;                // Legacy: indicates hierarchical structure
  key_editable?: boolean;                // Legacy: whether keys can be edited
  value_editable?: boolean;              // Legacy: whether values can be edited
  key_min_len?: number;                  // Legacy: minimum key length
  key_max_len?: number;                  // Legacy: maximum key length
  key_regex?: string;                    // Legacy: key regex pattern
  value_min_len?: number;                // Legacy: minimum value length
  value_max_len?: number;                // Legacy: maximum value length
  value_regex?: string;                  // Legacy: value regex pattern
  value_min_value?: number;              // Legacy: minimum value
  value_max_value?: number;              // Legacy: maximum value
  key_min_value?: number;                // Legacy: minimum key value
  key_max_value?: number;                // Legacy: maximum key value
  key_step?: number;                     // Legacy: key step increment
  value_step?: number;                   // Legacy: value step increment

  // Common flags
  creatable?: boolean;                   // Whether new items can be created (applies to both keys and values)
  editable?: boolean;                    // Whether items can be edited (applies to both keys and values)

  // Legacy flags
  creatable_key?: boolean;               // Legacy: whether new keys can be created
  creatable_value?: boolean;             // Legacy: whether new values can be created
  editable_key?: boolean;                // Legacy: whether keys can be edited
  editable_value?: boolean;              // Legacy: whether values can be edited

  // Subvariables for legacy support
  subvariables?: Record<string, ParameterConfig>; // For object types with subfields
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
