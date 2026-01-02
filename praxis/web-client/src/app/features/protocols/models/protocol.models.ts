
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
