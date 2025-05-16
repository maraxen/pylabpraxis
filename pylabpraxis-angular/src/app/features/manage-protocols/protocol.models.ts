// pylabpraxis-angular/src/app/features/manage-protocols/services/protocol.models.ts

/**
 * Represents the basic types for protocol parameters.
 * Based on frontend/src/features/protocols/types/protocol.ts ParameterType
 * and backend praxis/api/protocols.py _map_python_type_to_frontend
 */
export type ProtocolParameterType = 'string' | 'integer' | 'float' | 'boolean' | 'array' | 'dict' | 'number'; // 'number' is a common superset for int/float

/**
 * Base properties for constraints.
 * Based on frontend BaseConstraintProps and backend ParameterConfig constraints.
 */
export interface BaseConstraintProps {
  type?: string; // Data type (string, number, etc.)
  array?: any[]; // Allowed values for selection if type is array-like or for enum
  array_len?: number; // Maximum number of items (if array)
  min_len?: number; // Minimum string length
  max_len?: number; // Maximum string length
  regex?: string; // Regular expression pattern
  min_value?: number; // Minimum numeric value
  max_value?: number; // Maximum numeric value
  step?: number; // Step increment for numbers
  param?: string; // Referenced parameter name
  editable?: boolean; // Whether values can be edited
  creatable?: boolean; // Whether new values can be created
  subvariables?: Record<string, ParameterConfig>; // For object/dict types
}

/**
 * Nested constraint structure.
 * Based on frontend NestedConstraint.
 */
export interface NestedConstraint extends BaseConstraintProps {
  parent?: BaseConstraintProps;
}

/**
 * Defines constraints for protocol parameters.
 * Based on frontend ParameterConstraints.
 */
export interface ParameterConstraints extends BaseConstraintProps {
  key_constraints?: NestedConstraint;
  value_constraints?: NestedConstraint;
}

/**
 * Configuration for a single protocol parameter.
 * Based on frontend ParameterConfig and backend parameter structure in get_protocol_details_from_module.
 */
export interface ParameterConfig {
  type: ProtocolParameterType; // Mapped type
  description?: string;
  default?: any;
  required?: boolean;
  constraints?: ParameterConstraints;
  // 'id' is a frontend-specific concept for UI elements, not typically from backend details.
}

/**
 * Represents a required asset for a protocol.
 * Based on frontend Asset and backend asset structure in get_protocol_details_from_module.
 */
export interface ProtocolAsset {
  name: string;
  type: string; // Type of the asset (e.g., 'PlateReader', 'Pipette')
  required: boolean;
  description?: string;
}

/**
 * Detailed information about a protocol.
 * Based on frontend Protocol and backend ProtocolInfo/details from get_protocol_details.
 */
export interface ProtocolDetails {
  name: string;
  path: string; // File path of the protocol
  description: string;
  parameters: Record<string, ParameterConfig>; // Dictionary of parameter configurations
  assets: ProtocolAsset[]; // List of required assets
  has_assets: boolean;
  has_parameters: boolean;
  requires_config: boolean; // True if neither parameters nor assets are defined
  // config_fields might be relevant if you were to load/save full protocol definitions,
  // but for running, 'parameters' and 'assets' are primary.
}

/**
 * Basic information about a discovered protocol.
 * Based on backend ProtocolInfo model.
 */
export interface ProtocolInfo {
  name: string;
  path: string; // File path of the protocol
  description: string;
  has_assets?: boolean;
  has_parameters?: boolean;
}

/**
 * Represents the status of a protocol.
 * Based on backend ProtocolStatus model.
 */
export interface ProtocolStatusResponse {
  name: string;
  status: string;
}

/**
 * Request payload for preparing a protocol.
 * Based on backend ProtocolPrepareRequest model.
 */
export interface ProtocolPrepareRequest {
  protocol_path: string;
  parameters?: Record<string, any>;
  asset_assignments?: Record<string, string>; // Maps asset requirement name to assigned asset ID/name
}

/**
 * Response from preparing a protocol.
 * Based on backend /prepare endpoint response.
 */
export interface ProtocolPrepareResponse {
  status: 'ready' | 'invalid' | string; // "ready" if valid, or other status
  config?: any; // The validated (or current) configuration
  errors?: any; // Validation errors if status is 'invalid'
  asset_suggestions?: any; // Suggestions if assets were not pre-assigned
}

/**
 * Request payload for starting a protocol.
 * The backend /start endpoint takes a validated configuration object.
 */
export interface ProtocolStartRequest {
  // This is essentially the 'validated_config' from the prepare step.
  name: string;
  parameters: Record<string, any>;
  required_assets: Record<string, string>; // Asset assignments
  protocol_path: string;
  // May include other fields like deck_layout, etc., as per backend needs.
}

/**
 * Response from uploading a file.
 * Based on backend /upload_config_file and /upload_deck_file responses.
 */
export interface FileUploadResponse {
  filename: string;
  path: string;
}

// You can add more specific types as needed, for example, for asset_suggestions
// or the structure of 'config' in ProtocolPrepareResponse.
