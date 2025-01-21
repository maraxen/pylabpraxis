export type ParameterType = 'bool' | 'number' | 'float' | 'int' | 'list' | 'string';

export interface ParameterConstraints {
  min_value?: number;
  max_value?: number;
  allowed_values?: any[];
}

export interface Parameter {
  name: string;
  type: ParameterType;
  description?: string;
  default?: any;
  required: boolean;
  constraints?: ParameterConstraints;
}

export interface ConfigFields {
  name: string;
  details: string;
  description: string;
  machines: string[];
  liquid_handler_ids: string[];
  users: string[];
  directory: string;
  deck: string;
  needed_deck_resources: Record<string, any>;
  other_args: Record<string, any>;
}

export interface Protocol {
  name: string;
  file: string;
  description: string;
  parameters: Parameter[];
  config_fields: ConfigFields;
}

export interface ProtocolStatus {
  name: string;
  status: string;
}