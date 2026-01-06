/**
 * Auto-generated TypeScript interfaces from SQLAlchemy ORM models
 * Generated at: 2026-01-01T14:15:59.780340
 * DO NOT EDIT MANUALLY - regenerate using: uv run scripts/generate_browser_schema.py
 */

 

import type {
  AssetType,
  DataOutputType,
  FunctionCallStatus,
  MachineCategory,
  MachineStatus,
  ProtocolRunStatus,
  ProtocolSourceStatus,
  ResourceStatus,
  SpatialContext,
} from './enums';

/**
 * Interface for the 'assets' table
 */
export interface Asset {
  /** Type of asset, e.g., machine, resource, etc. */
  asset_type: AssetType | null;
  /** Name of the asset. */
  name: string;
  /** Fully qualified name of the asset's class, if applicable. */
  fqn: string | null;
  /** Location of the asset in the lab. */
  location: string | null;
  /** PLR state of the asset, if applicable. */
  plr_state: Record<string, unknown> | null;
  /** PLR definition of the asset, if applicable. */
  plr_definition: Record<string, unknown> | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
}

/**
 * Interface for the 'deck_definition_catalog' table
 */
export interface DeckDefinitionCatalog {
  /** Default size in X dimension in mm. */
  default_size_x_mm: number | null;
  /** Default size in Y dimension in mm. */
  default_size_y_mm: number | null;
  /** Default size in Z dimension in mm. */
  default_size_z_mm: number | null;
  serialized_constructor_args_json: Record<string, unknown> | null;
  serialized_assignment_methods_json: Record<string, unknown> | null;
  serialized_constructor_hints_json: Record<string, unknown> | null;
  additional_properties_json: Record<string, unknown> | null;
  positioning_config_json: Record<string, unknown> | null;
  /** Foreign key to the asset requirement this deck definition satisfies. */
  asset_requirement_accession_id: string | null;
  /** Fully qualified name of the PyLabRobot class. */
  fqn: string;
  /** Human-readable name for the type definition. Not unique since fqn is the unique identifier. */
  name: string;
  /** Detailed description of the type. */
  description: string | null;
  /** Category of the type in PyLabRobot (e.g., 'Deck', 'LiquidHandler'). */
  plr_category: string | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
}

/**
 * Interface for the 'deck_position_definitions' table
 */
export interface DeckPositionDefinition {
  /** Foreign key to the parent deck type definition. */
  deck_type_id: string;
  /** Human-readable identifier for the position (e.g., 'A1', 'trash_bin'). */
  position_accession_id: string;
  /** X-coordinate of the position's center. */
  nominal_x_mm: number | null;
  /** Y-coordinate of the position's center. */
  nominal_y_mm: number | null;
  /** Z-coordinate of the position's center. */
  nominal_z_mm: number | null;
  /** PyLabRobot specific position type name. */
  pylabrobot_position_type_name: string | null;
  /** List of specific resource definition names allowed at this position. */
  allowed_resource_definition_names: Record<string, unknown> | null;
  /** Indicates if the position accepts tips. */
  accepts_tips: boolean | null;
  /** Indicates if the position accepts plates. */
  accepts_plates: boolean | null;
  /** Indicates if the position accepts tubes. */
  accepts_tubes: boolean | null;
  /** Additional notes for the position. */
  notes: string | null;
  /** JSONB field to store additional, position-specific details. */
  compatible_resource_fqns: Record<string, unknown> | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
  /** Unique, human-readable name for the object. */
  name: string;
}

/**
 * Interface for the 'decks' table
 */
export interface Deck {
  /** Primary key, linked to the resource's accession_id. */
  accession_id: string;
  /** Foreign key to the machine this deck is part of. */
  parent_machine_accession_id: string | null;
  /** Foreign key to the deck type definition. */
  deck_type_id: string;
}

/**
 * Interface for the 'file_system_protocol_sources' table
 */
export interface FileSystemProtocolSource {
  /** The name of the protocol source */
  name: string;
  /** The base path for the file system protocol source. */
  base_path: string | null;
  /** Whether to recursively scan subdirectories. */
  is_recursive: boolean | null;
  status: ProtocolSourceStatus | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
}

/**
 * Interface for the 'function_call_logs' table
 */
export interface FunctionCallLog {
  /** Foreign key to the protocol run this function call belongs to. */
  protocol_run_accession_id: string;
  /** Sequence number of this function call within the protocol run, starting from 0. */
  sequence_in_run: number;
  /** Foreign key to the function protocol definition that this call executes. */
  function_protocol_definition_accession_id: string;
  /** Foreign key to the parent function call log, if this call is a child of another call. */
  parent_function_call_log_accession_id: string | null;
  /** The start time of the function call, automatically set when the call is created. */
  start_time: string;
  /** The end time of the function call, automatically set when the call is completed. */
  end_time: string | null;
  /** Duration of the function call in milliseconds. */
  duration_ms: number | null;
  /** Input arguments for the function call. */
  input_args_json: Record<string, unknown> | null;
  /** Return value of the function call. */
  return_value_json: Record<string, unknown> | null;
  status: FunctionCallStatus | null;
  /** Error message, if any. */
  error_message_text: string | null;
  /** Error traceback, if any. */
  error_traceback_text: string | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
  /** Unique, human-readable name for the object. */
  name: string;
}

/**
 * Interface for the 'function_data_outputs' table
 */
export interface FunctionDataOutput {
  /** Foreign key to the protocol run this data output belongs to */
  protocol_run_accession_id: string;
  /** Foreign key to the function call log this data output belongs to */
  function_call_log_accession_id: string;
  /** Type of data output (e.g., measurement, image, file, etc.) */
  data_type: DataOutputType | null;
  /** Unique key within the function call (e.g., 'absorbance_580nm', 'well_A1_od') */
  data_key: string | null;
  spatial_context: SpatialContext | null;
  /** Foreign key to the resource this data output is associated with (e.g., plate, well) */
  resource_accession_id: string | null;
  /** Foreign key to the machine this data output is associated with (e.g., plate reader) */
  machine_accession_id: string | null;
  /** Foreign key to the deck this data output is associated with */
  deck_accession_id: string | null;
  /** Spatial coordinates within resource (e.g., {'well': 'A1', 'row': 0, 'col': 0}) */
  spatial_coordinates_json: Record<string, unknown> | null;
  /** Numeric data values */
  data_value_numeric: number | null;
  /** Structured data (arrays, objects, etc.) */
  data_value_json: Record<string, unknown> | null;
  /** Text data or serialized content */
  data_value_text: string | null;
  /** Binary data (images, files) */
  data_value_binary: Uint8Array | null;
  /** Path to external file */
  file_path: string | null;
  /** File size in bytes */
  file_size_bytes: number | null;
  /** Units of measurement (e.g., 'nm', 'μL', 'OD') */
  data_units: string | null;
  /** Quality score (0.0-1.0) */
  data_quality_score: number | null;
  /** Measurement conditions (temperature, wavelength, etc.) */
  measurement_conditions_json: Record<string, unknown> | null;
  /** When the measurement/data was captured */
  measurement_timestamp: string | null;
  /** Sequence number within the function call */
  sequence_in_function: number | null;
  /** Foreign key to the data output this is derived from (if applicable) */
  derived_from_data_output_accession_id: string | null;
  /** Metadata about data processing/transformation */
  processing_metadata_json: Record<string, unknown> | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
  /** Unique, human-readable name for the object. */
  name: string;
}

/**
 * Interface for the 'function_protocol_definitions' table
 */
export interface FunctionProtocolDefinition {
  /** The fully qualified name of the protocol function. */
  fqn: string;
  /** The version of the protocol function, following semantic versioning. */
  version: string | null;
  /** A human-readable description of the protocol function. */
  description: string | null;
  /** The file path where the protocol function is defined, relative to its source       repository or file system source. */
  source_file_path: string | null;
  /** The module name where the protocol function is defined, used for import resolution. */
  module_name: string | null;
  /** The name of the function that implements the protocol logic. */
  function_name: string | null;
  /** Foreign key to the protocol source repository where this function is defined. */
  source_repository_accession_id: string | null;
  /** The commit hash of the source repository where this function is defined. */
  commit_hash: string | null;
  /** Foreign key to the file system protocol source where this function is defined. */
  file_system_source_accession_id: string | null;
  is_top_level: boolean | null;
  solo_execution: boolean | null;
  preconfigure_deck: boolean | null;
  /** Name of the deck parameter in the function signature. */
  deck_param_name: string | null;
  /** FQN of the function to construct the deck. */
  deck_construction_function_fqn: string | null;
  /** Name of the state parameter in the function signature. */
  state_param_name: string | null;
  /** Category of the protocol function, used for grouping or filtering. */
  category: string | null;
  /** Arbitrary tags associated with the protocol function for categorization. */
  tags: Record<string, unknown> | null;
  deprecated: boolean | null;
  /** Inferred hardware requirements from static analysis (ProtocolRequirements). */
  hardware_requirements_json: Record<string, unknown> | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
  /** Unique, human-readable name for the object. */
  name: string;
}

/**
 * Interface for the 'machine_definition_catalog' table
 */
export interface MachineDefinitionCatalog {
  /** Category of the machine, e.g., liquid handler, centrifuge, etc. */
  machine_category: MachineCategory | null;
  /** Material of the resource, e.g., 'polypropylene', 'glass'. */
  material: string | null;
  /** Manufacturer of the resource, if applicable. */
  manufacturer: string | null;
  /** Additional PyLabRobot specific definition details as JSONB. */
  plr_definition_details_json: Record<string, unknown> | null;
  /** Size in X dimension (mm). */
  size_x_mm: number | null;
  /** Size in Y dimension (mm). */
  size_y_mm: number | null;
  /** Size in Z dimension (mm). */
  size_z_mm: number | null;
  /** Model of the resource, if applicable. */
  model: string | null;
  /** Represents PLR Resource.rotation, e.g., {'x_deg': 0, 'y_deg': 0, 'z_deg': 90} or PLR rotation object serialized */
  rotation_json: Record<string, unknown> | null;
  /** Foreign key to the resource definition catalog, if this resource is also a machine. */
  resource_definition_accession_id: string | null;
  /** Flag indicating if this machine has a deck. */
  has_deck: boolean | null;
  /** Foreign key to the deck definition catalog, if this machine has a deck. */
  deck_definition_accession_id: string | null;
  /** JSONB representation of setup method for this machine definition. */
  setup_method_json: Record<string, unknown> | null;
  /** JSONB representation of hardware capabilities (channels, modules). */
  capabilities: Record<string, unknown> | null;
  /** JSON list of compatible backend class FQNs. */
  compatible_backends: Record<string, unknown> | null;
  /** Schema for user-configurable capabilities (questions for the user). */
  capabilities_config: Record<string, unknown> | null;
  /** Foreign key to the asset requirement this machine definition satisfies. */
  asset_requirement_accession_id: string | null;
  /** Fully qualified name of the PyLabRobot class. */
  fqn: string;
  /** Human-readable name for the type definition. Not unique since fqn is the unique identifier. */
  name: string;
  /** Detailed description of the type. */
  description: string | null;
  /** Category of the type in PyLabRobot (e.g., 'Deck', 'LiquidHandler'). */
  plr_category: string | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
}

/**
 * Interface for the 'machines' table
 */
export interface Machine {
  /** Unique identifier for the machine, derived from the Asset base class. */
  accession_id: string;
  /** Category of the machine, e.g., liquid handler, centrifuge, etc. */
  machine_category: MachineCategory | null;
  /** Description of the machine's purpose or capabilities. */
  description: string | null;
  /** Manufacturer of the machine. */
  manufacturer: string | null;
  /** Model of the machine. */
  model: string | null;
  /** Unique serial number of the machine, if applicable. */
  serial_number: string | null;
  /** Date when the machine was installed or commissioned. */
  installation_date: string | null;
  status: MachineStatus | null;
  /** Additional details about the current status, e.g., error message */
  status_details: string | null;
  /** e.g., {'backend': 'hamilton', 'address': '192.168.1.1'} */
  connection_info: Record<string, unknown> | null;
  /** If True, this machine is a simulation override for testing purposes. */
  is_simulation_override: boolean | null;
  /** User-specified capability overrides (e.g., 'has_iswap': true). */
  user_configured_capabilities: Record<string, unknown> | null;
  /** Foreign key to the workcell this machine belongs to, if applicable. */
  workcell_accession_id: string | null;
  /** Foreign key to the resource counterpart of this machine, if applicable. */
  resource_counterpart_accession_id: string | null;
  /** Foreign key to the deck this machine has, if applicable. */
  deck_child_accession_id: string | null;
  /** Foreign key to the deck definition this machine uses, if applicable. */
  deck_child_definition_accession_id: string | null;
  /** Timestamp of the last time the machine was seen online. */
  last_seen_online: string | null;
  /** Foreign key to the current protocol run this machine is executing, if applicable. */
  current_protocol_run_accession_id: string | null;
}

/**
 * Interface for the 'parameter_definitions' table
 */
export interface ParameterDefinition {
  /** Foreign key to the protocol definition this parameter belongs to. */
  protocol_definition_accession_id: string;
  /** The name of the parameter. */
  name: string | null;
  /** The type hint of the parameter. */
  type_hint: string | null;
  /** The fully qualified name of the parameter. */
  fqn: string | null;
  is_deck_param: boolean | null;
  /** Whether the parameter is optional. */
  optional: boolean | null;
  /** String representation of the default value for the parameter. */
  default_value_repr: string | null;
  /** A human-readable description of the parameter. */
  description: string | null;
  /** JSONB representation of any constraints on the parameter, such as allowed values or       ranges. */
  constraints: Record<string, unknown> | null;
  /** JSONB representation of UI hints for the parameter. */
  ui_hint: Record<string, unknown> | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
}

/**
 * Interface for the 'protocol_asset_requirements' table
 */
export interface ProtocolAssetRequirement {
  /** Foreign key to the protocol definition this asset requirement belongs to. */
  protocol_definition_accession_id: string;
  /** The name of the asset requirement. */
  name: string | null;
  /** The type hint of the asset requirement. */
  type_hint_str: string | null;
  /** The actual type of the asset requirement. */
  actual_type_str: string | null;
  /** The fully qualified name of the asset requirement's class. */
  fqn: string | null;
  /** Whether the asset requirement is optional. */
  optional: boolean | null;
  /** String representation of the default value for the asset requirement. */
  default_value_repr: string | null;
  /** A human-readable description of the asset requirement. */
  description: string | null;
  /** JSONB representation of any constraints on the asset requirement, such as allowed       values or ranges. */
  constraints: Record<string, unknown> | null;
  /** JSONB representation of location constraints for the asset requirement. */
  location_constraints: Record<string, unknown> | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
}

/**
 * Interface for the 'protocol_runs' table
 */
export interface ProtocolRun {
  /** Foreign key to the top-level protocol definition that this run executes. */
  top_level_protocol_definition_accession_id: string;
  status: ProtocolRunStatus | null;
  /** The start time of the protocol run. Null if not yet started. */
  start_time: string | null;
  /** The end time of the protocol run. Null if not yet completed. */
  end_time: string | null;
  /** Input parameters for the protocol run. */
  input_parameters_json: Record<string, unknown> | null;
  /** Resolved assets for the protocol run. */
  resolved_assets_json: Record<string, unknown> | null;
  /** Output data for the protocol run. */
  output_data_json: Record<string, unknown> | null;
  /** Initial state for the protocol run. */
  initial_state_json: Record<string, unknown> | null;
  /** Final state for the protocol run. */
  final_state_json: Record<string, unknown> | null;
  /** File path to the data directory for the protocol run. */
  data_directory_path: string | null;
  /** Information about the user who created this protocol run. */
  created_by_user: Record<string, unknown> | null;
  /** Foreign key to the previous protocol run in a continuation chain. */
  previous_accession_id: string | null;
  /** Duration of the protocol run in milliseconds. */
  duration_ms: number | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
  /** Unique, human-readable name for the object. */
  name: string;
}

/**
 * Interface for the 'protocol_source_repositories' table
 */
export interface ProtocolSourceRepository {
  /** The name of the protocol source */
  name: string;
  /** The URL of the Git repository containing protocol definitions. */
  git_url: string | null;
  /** The default branch or tag in the Git repository where protocols are defined. */
  default_ref: string | null;
  /** Local file system path where the repository is checked out. If None, it is not checked      out locally. */
  local_checkout_path: string | null;
  /** The last commit SHA that was synced from the remote repository. */
  last_synced_commit: string | null;
  status: ProtocolSourceStatus | null;
  auto_sync_enabled: boolean | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
}

/**
 * Interface for the 'resource_definition_catalog' table
 */
export interface ResourceDefinitionCatalog {
  /** Human-readable type of the resource. */
  resource_type: string | null;
  is_consumable: boolean | null;
  /** Nominal volume in microliters, if applicable. */
  nominal_volume_ul: number | null;
  /** Material of the resource, e.g., 'polypropylene', 'glass'. */
  material: string | null;
  /** Manufacturer of the resource, if applicable. */
  manufacturer: string | null;
  /** Additional PyLabRobot specific definition details as JSONB. */
  plr_definition_details_json: Record<string, unknown> | null;
  /** Ordering information for the resource, if applicable. */
  ordering: string | null;
  /** Size in X dimension (mm). */
  size_x_mm: number | null;
  /** Size in Y dimension (mm). */
  size_y_mm: number | null;
  /** Size in Z dimension (mm). */
  size_z_mm: number | null;
  /** Model of the resource, if applicable. */
  model: string | null;
  /** Represents PLR Resource.rotation, e.g., {'x_deg': 0, 'y_deg': 0, 'z_deg': 90} or PLR rotation object serialized */
  rotation_json: Record<string, unknown> | null;
  /** Number of items (wells for plates, tips for tip racks). */
  num_items: number | null;
  /** Plate skirt type: 'skirted', 'semi-skirted', 'non-skirted'. */
  plate_type: string | null;
  /** Well volume in microliters for plates. */
  well_volume_ul: number | null;
  /** Tip volume in microliters for tip racks. */
  tip_volume_ul: number | null;
  /** Vendor/manufacturer extracted from FQN (e.g., 'corning', 'opentrons'). */
  vendor: string | null;
  /** All extracted PLR properties as structured JSON for faceted filtering. */
  properties_json: Record<string, unknown> | null;
  /** Foreign key to the deck definition catalog, if this resource is also a deck. */
  deck_definition_accession_id: string | null;
  /** Foreign key to the asset requirement this resource definition satisfies. */
  asset_requirement_accession_id: string | null;
  /** Fully qualified name of the PyLabRobot class. */
  fqn: string;
  /** Human-readable name for the type definition. Not unique since fqn is the unique identifier. */
  name: string;
  /** Detailed description of the type. */
  description: string | null;
  /** Category of the type in PyLabRobot (e.g., 'Deck', 'LiquidHandler'). */
  plr_category: string | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
}

/**
 * Interface for the 'resources' table
 */
export interface Resource {
  /** Unique identifier for the resource, derived from the Asset base class. */
  accession_id: string;
  /** Foreign key to the resource definition catalog. */
  resource_definition_accession_id: string | null;
  /** Foreign key to the parent resource's accession ID, if this is a child resource. */
  parent_accession_id: string | null;
  status: ResourceStatus | null;
  /** Additional details about the current status, e.g., error message */
  status_details: string | null;
  /** Foreign key to the current protocol run this resource is used in, if applicable. */
  current_protocol_run_accession_id: string | null;
  /** Name of the deck position where the resource is currently located. */
  current_deck_position_name: string | null;
  /** Foreign key to the machine where this resource is currently located, if applicable. */
  machine_location_accession_id: string | null;
  /** Foreign key to the deck this resource is located on, if applicable. */
  deck_accession_id: string | null;
  /** Foreign key to the workcell this resource belongs to, if applicable. */
  workcell_accession_id: string | null;
}

/**
 * Interface for the 'scheduler_metrics_mv' table
 */
export interface SchedulerMetricsMv {
  metric_timestamp: string;
  protocols_scheduled: number;
  protocols_completed: number;
  protocols_failed: number;
  protocols_cancelled: number;
  avg_queue_wait_time_ms: number;
  avg_execution_time_ms: number;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
  /** Unique, human-readable name for the object. */
  name: string;
}

/**
 * Interface for the 'well_data_outputs' table
 */
export interface WellDataOutput {
  /** Foreign key to the function data output this well data output belongs to */
  function_data_output_accession_id: string;
  /** Foreign key to the plate resource this well data output belongs to */
  plate_resource_accession_id: string;
  /** Well name (e.g., 'A1', 'H12') */
  well_name: string | null;
  /** 0-based row index */
  well_row: number | null;
  /** 0-based column index */
  well_column: number | null;
  /** Linear well index (0-based) */
  well_index: number | null;
  /** Primary numeric value for this well */
  data_value: number | null;
  accession_id: string;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
  /** Unique, human-readable name for the object. */
  name: string;
}

/**
 * Interface for the 'workcells' table
 */
export interface Workcell {
  accession_id: string;
  name: string;
  /** Description of the workcell's purpose or contents */
  description: string | null;
  /** Physical location of the workcell (e.g., 'Lab 2, Room 301') */
  physical_location: string | null;
  /** JSONB representation of the latest state of the workcell */
  latest_state_json: Record<string, unknown> | null;
  /** Timestamp of the last state update */
  last_state_update_time: string | null;
  /** Current status of the workcell */
  status: string | null;
  /** Timestamp when the record was created. */
  created_at: string;
  updated_at: string;
  /** Arbitrary metadata. */
  properties_json: Record<string, unknown> | null;
}
