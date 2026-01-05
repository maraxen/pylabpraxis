
export interface ParameterConstraints {
  min_value?: number;
  max_value?: number;
  min_length?: number;
  max_length?: number;
  regex_pattern?: string;
  options?: unknown[];
}

export interface UIHint {
  widget_type?: string;
}

/**
 * Specification for itemized resources (plates, tip racks).
 * Used by IndexSelectorComponent to render the correct grid.
 */
export interface ItemizedSpec {
  items_x: number;
  items_y: number;
  parent_type?: string;
}

export interface ParameterMetadata {
  name: string;
  type_hint: string;
  fqn: string;
  is_deck_param: boolean;
  optional: boolean;
  default_value_repr?: string;
  description?: string;
  constraints: ParameterConstraints;
  ui_hint?: UIHint;
  /** UI field type for rendering (e.g., "text", "number", "index_selector") */
  field_type?: string;
  /** True if the type is an itemized resource (Well, TipSpot) or collection */
  is_itemized?: boolean;
  /** Specification for index selector grid dimensions */
  itemized_spec?: ItemizedSpec;
  /** Link ID for linked index selectors (e.g., source/dest wells) */
  linked_to?: string;
}

export interface AssetConstraints {
  required_methods: string[];
  required_attributes: string[];
  required_method_signatures: Record<string, string>;
  required_method_args: Record<string, string[]>;
  min_volume_ul?: number;
}

export interface LocationConstraints {
  location_requirements: string[];
  on_resource_type: string;
  stack: boolean;
  directly_position: boolean;
  position_condition: string[];
}

export interface AssetRequirement {
  accession_id: string;
  name: string;
  fqn: string;
  type_hint_str: string;
  optional: boolean;
  default_value_repr?: string;
  description?: string;
  constraints: AssetConstraints;
  location_constraints: LocationConstraints;
}

/**
 * Data view definition for protocol input data requirements.
 * Allows protocols to declare what input data they need in a structured way.
 */
export interface DataViewMetadataModel {
  name: string;
  description?: string;
  source_type: string;  // 'plr_state' | 'function_output' | 'external'
  source_filter_json?: Record<string, unknown>;
  data_schema_json?: Record<string, unknown>;
  required: boolean;
  default_value_json?: unknown;
}

export interface ProtocolDefinition {
  accession_id: string;
  name: string;
  description?: string;
  category?: string;
  is_top_level: boolean;
  version: string;
  source_file_path?: string;
  module_name?: string;
  function_name?: string;
  fqn?: string;
  tags?: string[];
  deprecated?: boolean;
  parameters: ParameterMetadata[];
  assets: AssetRequirement[];
  data_views?: DataViewMetadataModel[];
}

export interface ProtocolRun {
  accession_id: string;
  protocol_definition_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  start_time?: string;
  end_time?: string;
}

export interface ProtocolUpload {
  file: File;
  path?: string;
}
