-- Auto-generated SQLite schema from SQLAlchemy ORM models
-- Generated at: 2026-01-12T15:54:02.242139
-- DO NOT EDIT MANUALLY - regenerate using: uv run scripts/generate_browser_schema.py

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Metadata table for schema versioning
CREATE TABLE IF NOT EXISTS _schema_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR REPLACE INTO _schema_metadata (key, value) VALUES ('generated_at', '2026-01-12T15:54:02.242148');
INSERT OR REPLACE INTO _schema_metadata (key, value) VALUES ('schema_version', '1.0.0');

-- Table: file_system_protocol_sources
CREATE TABLE file_system_protocol_sources (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	base_path VARCHAR NOT NULL, 
	is_recursive INTEGER NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	PRIMARY KEY (accession_id)
);

CREATE INDEX ix_file_system_protocol_sources_accession_id ON file_system_protocol_sources (accession_id);
CREATE INDEX ix_file_system_protocol_sources_name ON file_system_protocol_sources (name);

-- Table: protocol_source_repositories
CREATE TABLE protocol_source_repositories (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	git_url VARCHAR NOT NULL, 
	default_ref VARCHAR NOT NULL, 
	local_checkout_path VARCHAR, 
	last_synced_commit VARCHAR, 
	status VARCHAR(16) NOT NULL, 
	auto_sync_enabled INTEGER NOT NULL, 
	PRIMARY KEY (accession_id)
);

CREATE INDEX ix_protocol_source_repositories_accession_id ON protocol_source_repositories (accession_id);
CREATE INDEX ix_protocol_source_repositories_name ON protocol_source_repositories (name);
CREATE INDEX ix_protocol_source_repositories_git_url ON protocol_source_repositories (git_url);

-- EXCLUDED: users (server-only)

-- Table: workcells
CREATE TABLE workcells (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	description VARCHAR, 
	physical_location VARCHAR, 
	status VARCHAR NOT NULL, 
	last_state_update_time DATETIME, 
	latest_state_json TEXT, 
	PRIMARY KEY (accession_id)
);

CREATE INDEX ix_workcells_accession_id ON workcells (accession_id);
CREATE INDEX ix_workcells_name ON workcells (name);

-- Table: deck_position_definitions
CREATE TABLE deck_position_definitions (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	position_accession_id VARCHAR NOT NULL, 
	nominal_x_mm FLOAT NOT NULL, 
	nominal_y_mm FLOAT NOT NULL, 
	nominal_z_mm FLOAT NOT NULL, 
	pylabrobot_position_type_name VARCHAR, 
	accepts_tips INTEGER, 
	accepts_plates INTEGER, 
	accepts_tubes INTEGER, 
	notes VARCHAR, 
	allowed_resource_definition_names TEXT, 
	compatible_resource_fqns TEXT, 
	deck_type_id CHAR(32) NOT NULL, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(deck_type_id) REFERENCES deck_definition_catalog (accession_id)
);

CREATE INDEX ix_deck_position_definitions_accession_id ON deck_position_definitions (accession_id);
CREATE INDEX ix_deck_position_definitions_name ON deck_position_definitions (name);
CREATE INDEX ix_deck_position_definitions_deck_type_id ON deck_position_definitions (deck_type_id);
CREATE INDEX ix_deck_position_definitions_position_accession_id ON deck_position_definitions (position_accession_id);

-- Table: parameter_definitions
CREATE TABLE parameter_definitions (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	type_hint VARCHAR NOT NULL, 
	fqn VARCHAR NOT NULL, 
	is_deck_param INTEGER NOT NULL, 
	optional INTEGER NOT NULL, 
	default_value_repr VARCHAR, 
	description VARCHAR, 
	field_type VARCHAR, 
	is_itemized INTEGER NOT NULL, 
	linked_to VARCHAR, 
	constraints_json TEXT, 
	itemized_spec_json TEXT, 
	ui_hint_json TEXT, 
	protocol_definition_accession_id CHAR(32) NOT NULL, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(protocol_definition_accession_id) REFERENCES function_protocol_definitions (accession_id)
);

CREATE INDEX ix_parameter_definitions_fqn ON parameter_definitions (fqn);
CREATE INDEX ix_parameter_definitions_name ON parameter_definitions (name);
CREATE INDEX ix_parameter_definitions_type_hint ON parameter_definitions (type_hint);
CREATE INDEX ix_parameter_definitions_accession_id ON parameter_definitions (accession_id);
CREATE INDEX ix_parameter_definitions_protocol_definition_accession_id ON parameter_definitions (protocol_definition_accession_id);

-- Table: protocol_asset_requirements
CREATE TABLE protocol_asset_requirements (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	type_hint_str VARCHAR NOT NULL, 
	fqn VARCHAR, 
	actual_type_str VARCHAR, 
	optional INTEGER NOT NULL, 
	default_value_repr VARCHAR, 
	description VARCHAR, 
	required_plr_category VARCHAR, 
	constraints_json TEXT, 
	location_constraints_json TEXT, 
	protocol_definition_accession_id CHAR(32) NOT NULL, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(protocol_definition_accession_id) REFERENCES function_protocol_definitions (accession_id)
);

CREATE INDEX ix_protocol_asset_requirements_actual_type_str ON protocol_asset_requirements (actual_type_str);
CREATE INDEX ix_protocol_asset_requirements_accession_id ON protocol_asset_requirements (accession_id);
CREATE INDEX ix_protocol_asset_requirements_name ON protocol_asset_requirements (name);
CREATE INDEX ix_protocol_asset_requirements_protocol_definition_accession_id ON protocol_asset_requirements (protocol_definition_accession_id);
CREATE INDEX ix_protocol_asset_requirements_fqn ON protocol_asset_requirements (fqn);
CREATE INDEX ix_protocol_asset_requirements_required_plr_category ON protocol_asset_requirements (required_plr_category);
CREATE INDEX ix_protocol_asset_requirements_type_hint_str ON protocol_asset_requirements (type_hint_str);

-- EXCLUDED: schedule_entries (server-only)

-- EXCLUDED: schedule_history (server-only)

-- EXCLUDED: asset_reservations (server-only)

-- Table: function_protocol_definitions
CREATE TABLE function_protocol_definitions (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	fqn VARCHAR NOT NULL, 
	version VARCHAR NOT NULL, 
	description VARCHAR, 
	source_file_path VARCHAR NOT NULL, 
	module_name VARCHAR NOT NULL, 
	function_name VARCHAR NOT NULL, 
	is_top_level INTEGER NOT NULL, 
	solo_execution INTEGER NOT NULL, 
	preconfigure_deck INTEGER NOT NULL, 
	requires_deck INTEGER NOT NULL, 
	deck_param_name VARCHAR, 
	deck_construction_function_fqn VARCHAR, 
	deck_layout_path VARCHAR, 
	state_param_name VARCHAR, 
	category VARCHAR, 
	deprecated INTEGER NOT NULL, 
	source_hash VARCHAR, 
	graph_cached_at DATETIME, 
	simulation_version VARCHAR, 
	simulation_cached_at DATETIME, 
	bytecode_python_version VARCHAR, 
	bytecode_cache_version VARCHAR, 
	bytecode_cached_at DATETIME, 
	commit_hash VARCHAR, 
	tags TEXT, 
	hardware_requirements_json TEXT, 
	data_views_json TEXT, 
	computation_graph_json TEXT, 
	setup_instructions_json TEXT, 
	simulation_result_json TEXT, 
	inferred_requirements_json TEXT, 
	failure_modes_json TEXT, 
	cached_bytecode BLOB, 
	source_repository_accession_id CHAR(32), 
	file_system_source_accession_id CHAR(32), 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(source_repository_accession_id) REFERENCES protocol_source_repositories (accession_id), 
	FOREIGN KEY(file_system_source_accession_id) REFERENCES file_system_protocol_sources (accession_id)
);

CREATE INDEX ix_function_protocol_definitions_name ON function_protocol_definitions (name);
CREATE INDEX ix_function_protocol_definitions_is_top_level ON function_protocol_definitions (is_top_level);
CREATE INDEX ix_function_protocol_definitions_source_file_path ON function_protocol_definitions (source_file_path);
CREATE INDEX ix_function_protocol_definitions_deprecated ON function_protocol_definitions (deprecated);
CREATE INDEX ix_function_protocol_definitions_function_name ON function_protocol_definitions (function_name);
CREATE INDEX ix_function_protocol_definitions_file_system_source_accession_id ON function_protocol_definitions (file_system_source_accession_id);
CREATE INDEX ix_function_protocol_definitions_fqn ON function_protocol_definitions (fqn);
CREATE INDEX ix_function_protocol_definitions_source_repository_accession_id ON function_protocol_definitions (source_repository_accession_id);
CREATE INDEX ix_function_protocol_definitions_accession_id ON function_protocol_definitions (accession_id);
CREATE INDEX ix_function_protocol_definitions_category ON function_protocol_definitions (category);
CREATE INDEX ix_function_protocol_definitions_module_name ON function_protocol_definitions (module_name);
CREATE INDEX ix_function_protocol_definitions_commit_hash ON function_protocol_definitions (commit_hash);

-- Table: protocol_runs
CREATE TABLE protocol_runs (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	status VARCHAR(21) NOT NULL, 
	start_time DATETIME, 
	end_time DATETIME, 
	data_directory_path VARCHAR, 
	duration_ms INTEGER, 
	input_parameters_json TEXT, 
	resolved_assets_json TEXT, 
	output_data_json TEXT, 
	initial_state_json TEXT, 
	final_state_json TEXT, 
	created_by_user TEXT, 
	top_level_protocol_definition_accession_id CHAR(32) NOT NULL, 
	previous_accession_id CHAR(32), 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(top_level_protocol_definition_accession_id) REFERENCES function_protocol_definitions (accession_id), 
	FOREIGN KEY(previous_accession_id) REFERENCES protocol_runs (accession_id)
);

CREATE INDEX ix_protocol_runs_name ON protocol_runs (name);
CREATE INDEX ix_protocol_runs_top_level_protocol_definition_accession_id ON protocol_runs (top_level_protocol_definition_accession_id);
CREATE INDEX ix_protocol_runs_status ON protocol_runs (status);
CREATE INDEX ix_protocol_runs_accession_id ON protocol_runs (accession_id);
CREATE INDEX ix_protocol_runs_previous_accession_id ON protocol_runs (previous_accession_id);

-- Table: resource_definitions
CREATE TABLE resource_definitions (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	fqn VARCHAR NOT NULL, 
	description VARCHAR, 
	plr_category VARCHAR, 
	resource_type VARCHAR, 
	is_consumable INTEGER NOT NULL, 
	nominal_volume_ul FLOAT, 
	material VARCHAR, 
	manufacturer VARCHAR, 
	model VARCHAR, 
	ordering VARCHAR, 
	size_x_mm FLOAT, 
	size_y_mm FLOAT, 
	size_z_mm FLOAT, 
	num_items INTEGER, 
	plate_type VARCHAR, 
	well_volume_ul FLOAT, 
	tip_volume_ul FLOAT, 
	vendor VARCHAR, 
	plr_definition_details_json TEXT, 
	rotation_json TEXT, 
	deck_definition_accession_id CHAR(32), 
	asset_requirement_accession_id CHAR(32), 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(deck_definition_accession_id) REFERENCES deck_definition_catalog (accession_id), 
	FOREIGN KEY(asset_requirement_accession_id) REFERENCES protocol_asset_requirements (accession_id)
);

CREATE INDEX ix_resource_definitions_name ON resource_definitions (name);
CREATE INDEX ix_resource_definitions_deck_definition_accession_id ON resource_definitions (deck_definition_accession_id);
CREATE INDEX ix_resource_definitions_tip_volume_ul ON resource_definitions (tip_volume_ul);
CREATE INDEX ix_resource_definitions_num_items ON resource_definitions (num_items);
CREATE UNIQUE INDEX ix_resource_definitions_fqn ON resource_definitions (fqn);
CREATE INDEX ix_resource_definitions_accession_id ON resource_definitions (accession_id);
CREATE INDEX ix_resource_definitions_asset_requirement_accession_id ON resource_definitions (asset_requirement_accession_id);
CREATE INDEX ix_resource_definitions_vendor ON resource_definitions (vendor);
CREATE INDEX ix_resource_definitions_well_volume_ul ON resource_definitions (well_volume_ul);
CREATE INDEX ix_resource_definitions_plate_type ON resource_definitions (plate_type);

-- Table: state_resolution_log
CREATE TABLE state_resolution_log (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	operation_id VARCHAR NOT NULL, 
	operation_description VARCHAR NOT NULL, 
	error_message VARCHAR NOT NULL, 
	error_type VARCHAR, 
	uncertain_states_json TEXT NOT NULL, 
	resolution_json TEXT NOT NULL, 
	resolution_type VARCHAR(17) NOT NULL, 
	resolved_by VARCHAR NOT NULL, 
	resolved_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	notes VARCHAR, 
	action_taken VARCHAR(6) NOT NULL, 
	schedule_entry_accession_id CHAR(32) NOT NULL, 
	protocol_run_accession_id CHAR(32) NOT NULL, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(schedule_entry_accession_id) REFERENCES schedule_entries (accession_id), 
	FOREIGN KEY(protocol_run_accession_id) REFERENCES protocol_runs (accession_id)
);

CREATE INDEX ix_state_resolution_log_accession_id ON state_resolution_log (accession_id);
CREATE INDEX ix_state_resolution_log_protocol_run_accession_id ON state_resolution_log (protocol_run_accession_id);
CREATE INDEX ix_state_resolution_log_operation_id ON state_resolution_log (operation_id);
CREATE INDEX ix_state_resolution_log_action_taken ON state_resolution_log (action_taken);
CREATE INDEX ix_state_resolution_log_name ON state_resolution_log (name);
CREATE INDEX ix_state_resolution_log_schedule_entry_accession_id ON state_resolution_log (schedule_entry_accession_id);
CREATE INDEX ix_state_resolution_log_resolution_type ON state_resolution_log (resolution_type);

-- Table: deck_definition_catalog
CREATE TABLE deck_definition_catalog (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	fqn VARCHAR NOT NULL, 
	description VARCHAR, 
	plr_category VARCHAR, 
	default_size_x_mm FLOAT, 
	default_size_y_mm FLOAT, 
	default_size_z_mm FLOAT, 
	serialized_constructor_args_json TEXT, 
	serialized_assignment_methods_json TEXT, 
	serialized_constructor_hints_json TEXT, 
	additional_properties_json TEXT, 
	positioning_config_json TEXT, 
	asset_requirement_accession_id CHAR(32), 
	resource_definition_accession_id CHAR(32), 
	parent_accession_id CHAR(32), 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(asset_requirement_accession_id) REFERENCES protocol_asset_requirements (accession_id), 
	FOREIGN KEY(resource_definition_accession_id) REFERENCES resource_definitions (accession_id), 
	FOREIGN KEY(parent_accession_id) REFERENCES deck_definition_catalog (accession_id)
);

CREATE UNIQUE INDEX ix_deck_definition_catalog_fqn ON deck_definition_catalog (fqn);
CREATE INDEX ix_deck_definition_catalog_name ON deck_definition_catalog (name);
CREATE INDEX ix_deck_definition_catalog_accession_id ON deck_definition_catalog (accession_id);

-- Table: decks
CREATE TABLE decks (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	asset_type VARCHAR(16) NOT NULL, 
	fqn VARCHAR, 
	location VARCHAR, 
	properties_json TEXT, 
	plr_state TEXT, 
	plr_definition TEXT, 
	status VARCHAR(20) NOT NULL, 
	status_details VARCHAR, 
	location_label VARCHAR, 
	current_deck_position_name VARCHAR, 
	parent_machine_accession_id CHAR(32), 
	deck_type_id CHAR(32), 
	resource_definition_accession_id CHAR(32), 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(parent_machine_accession_id) REFERENCES machines (accession_id), 
	FOREIGN KEY(deck_type_id) REFERENCES deck_definition_catalog (accession_id), 
	FOREIGN KEY(resource_definition_accession_id) REFERENCES resource_definitions (accession_id)
);

CREATE INDEX ix_decks_name ON decks (name);
CREATE INDEX ix_decks_location ON decks (location);
CREATE INDEX ix_decks_fqn ON decks (fqn);
CREATE INDEX ix_decks_accession_id ON decks (accession_id);

-- Table: function_call_logs
CREATE TABLE function_call_logs (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	sequence_in_run INTEGER NOT NULL, 
	status VARCHAR(11) NOT NULL, 
	start_time DATETIME NOT NULL, 
	end_time DATETIME, 
	duration_ms INTEGER, 
	error_message_text VARCHAR, 
	error_traceback_text VARCHAR, 
	input_args_json TEXT, 
	return_value_json TEXT, 
	protocol_run_accession_id CHAR(32) NOT NULL, 
	function_protocol_definition_accession_id CHAR(32) NOT NULL, 
	parent_function_call_log_accession_id CHAR(32), 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(protocol_run_accession_id) REFERENCES protocol_runs (accession_id), 
	FOREIGN KEY(function_protocol_definition_accession_id) REFERENCES function_protocol_definitions (accession_id), 
	FOREIGN KEY(parent_function_call_log_accession_id) REFERENCES function_call_logs (accession_id)
);

CREATE INDEX ix_function_call_logs_sequence_in_run ON function_call_logs (sequence_in_run);
CREATE INDEX ix_function_call_logs_accession_id ON function_call_logs (accession_id);
CREATE INDEX ix_function_call_logs_name ON function_call_logs (name);
CREATE INDEX ix_function_call_logs_parent_function_call_log_accession_id ON function_call_logs (parent_function_call_log_accession_id);
CREATE INDEX ix_function_call_logs_function_protocol_definition_accession_id ON function_call_logs (function_protocol_definition_accession_id);
CREATE INDEX ix_function_call_logs_protocol_run_accession_id ON function_call_logs (protocol_run_accession_id);

-- Table: machine_definitions
CREATE TABLE machine_definitions (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	fqn VARCHAR NOT NULL, 
	description VARCHAR, 
	plr_category VARCHAR, 
	machine_category VARCHAR(25) NOT NULL, 
	material VARCHAR, 
	manufacturer VARCHAR, 
	model VARCHAR, 
	size_x_mm FLOAT, 
	size_y_mm FLOAT, 
	size_z_mm FLOAT, 
	has_deck INTEGER NOT NULL, 
	frontend_fqn VARCHAR, 
	plr_definition_details_json TEXT, 
	rotation_json TEXT, 
	setup_method_json TEXT, 
	capabilities TEXT, 
	compatible_backends TEXT, 
	capabilities_config TEXT, 
	connection_config TEXT, 
	resource_definition_accession_id CHAR(32), 
	deck_definition_accession_id CHAR(32), 
	asset_requirement_accession_id CHAR(32), 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(resource_definition_accession_id) REFERENCES resource_definitions (accession_id), 
	FOREIGN KEY(deck_definition_accession_id) REFERENCES deck_definition_catalog (accession_id), 
	FOREIGN KEY(asset_requirement_accession_id) REFERENCES protocol_asset_requirements (accession_id)
);

CREATE UNIQUE INDEX ix_machine_definitions_fqn ON machine_definitions (fqn);
CREATE INDEX ix_machine_definitions_accession_id ON machine_definitions (accession_id);
CREATE INDEX ix_machine_definitions_name ON machine_definitions (name);

-- Table: well_data_outputs
CREATE TABLE well_data_outputs (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	well_position VARCHAR, 
	measurement_type VARCHAR, 
	value FLOAT, 
	unit VARCHAR, 
	well_name VARCHAR, 
	data_value FLOAT, 
	well_row INTEGER NOT NULL, 
	well_column INTEGER NOT NULL, 
	well_index INTEGER, 
	metadata_json TEXT, 
	function_data_output_accession_id CHAR(32), 
	resource_accession_id CHAR(32), 
	plate_resource_accession_id CHAR(32), 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(function_data_output_accession_id) REFERENCES function_data_outputs (accession_id), 
	FOREIGN KEY(resource_accession_id) REFERENCES resources (accession_id), 
	FOREIGN KEY(plate_resource_accession_id) REFERENCES resources (accession_id)
);

CREATE INDEX ix_well_data_outputs_measurement_type ON well_data_outputs (measurement_type);
CREATE INDEX ix_well_data_outputs_name ON well_data_outputs (name);
CREATE INDEX ix_well_data_outputs_well_position ON well_data_outputs (well_position);
CREATE INDEX ix_well_data_outputs_accession_id ON well_data_outputs (accession_id);
CREATE INDEX ix_well_data_outputs_plate_resource_accession_id ON well_data_outputs (plate_resource_accession_id);
CREATE INDEX ix_well_data_outputs_resource_accession_id ON well_data_outputs (resource_accession_id);
CREATE INDEX ix_well_data_outputs_function_data_output_accession_id ON well_data_outputs (function_data_output_accession_id);

-- Table: function_data_outputs
CREATE TABLE function_data_outputs (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	data_type VARCHAR(24) NOT NULL, 
	data_key VARCHAR(255) NOT NULL, 
	spatial_context VARCHAR(13) NOT NULL, 
	spatial_coordinates_json TEXT, 
	data_units VARCHAR(50), 
	data_quality_score FLOAT, 
	measurement_conditions_json TEXT, 
	sequence_in_function INTEGER, 
	file_path VARCHAR, 
	file_size_bytes INTEGER, 
	mime_type VARCHAR, 
	measurement_timestamp DATETIME, 
	data_json TEXT, 
	data_value_numeric FLOAT, 
	data_value_text VARCHAR, 
	function_call_log_accession_id CHAR(32), 
	protocol_run_accession_id CHAR(32), 
	machine_accession_id CHAR(32), 
	resource_accession_id CHAR(32), 
	deck_accession_id CHAR(32), 
	derived_from_data_output_accession_id CHAR(32), 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(function_call_log_accession_id) REFERENCES function_call_logs (accession_id), 
	FOREIGN KEY(protocol_run_accession_id) REFERENCES protocol_runs (accession_id), 
	FOREIGN KEY(machine_accession_id) REFERENCES machines (accession_id), 
	FOREIGN KEY(resource_accession_id) REFERENCES resources (accession_id), 
	FOREIGN KEY(deck_accession_id) REFERENCES decks (accession_id), 
	FOREIGN KEY(derived_from_data_output_accession_id) REFERENCES function_data_outputs (accession_id)
);

CREATE INDEX ix_function_data_outputs_data_key ON function_data_outputs (data_key);
CREATE INDEX ix_function_data_outputs_data_type ON function_data_outputs (data_type);
CREATE INDEX ix_function_data_outputs_accession_id ON function_data_outputs (accession_id);
CREATE INDEX ix_function_data_outputs_function_call_log_accession_id ON function_data_outputs (function_call_log_accession_id);
CREATE INDEX ix_function_data_outputs_derived_from_data_output_accession_id ON function_data_outputs (derived_from_data_output_accession_id);
CREATE INDEX ix_function_data_outputs_machine_accession_id ON function_data_outputs (machine_accession_id);
CREATE INDEX ix_function_data_outputs_deck_accession_id ON function_data_outputs (deck_accession_id);
CREATE INDEX ix_function_data_outputs_protocol_run_accession_id ON function_data_outputs (protocol_run_accession_id);
CREATE INDEX ix_function_data_outputs_resource_accession_id ON function_data_outputs (resource_accession_id);
CREATE INDEX ix_function_data_outputs_name ON function_data_outputs (name);

-- Table: machines
CREATE TABLE machines (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	asset_type VARCHAR(16) NOT NULL, 
	fqn VARCHAR, 
	location VARCHAR, 
	properties_json TEXT, 
	plr_state TEXT, 
	plr_definition TEXT, 
	machine_category VARCHAR(25) NOT NULL, 
	description VARCHAR, 
	manufacturer VARCHAR, 
	model VARCHAR, 
	serial_number VARCHAR, 
	location_label VARCHAR, 
	installation_date DATETIME, 
	status VARCHAR(12) NOT NULL, 
	status_details VARCHAR, 
	is_simulation_override INTEGER, 
	last_seen_online DATETIME, 
	maintenance_enabled INTEGER NOT NULL, 
	connection_info TEXT, 
	user_configured_capabilities TEXT, 
	maintenance_schedule_json TEXT, 
	last_maintenance_json TEXT, 
	workcell_accession_id CHAR(32), 
	resource_counterpart_accession_id CHAR(32), 
	deck_child_accession_id CHAR(32), 
	deck_child_definition_accession_id CHAR(32), 
	current_protocol_run_accession_id CHAR(32), 
	machine_definition_accession_id CHAR(32), 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(workcell_accession_id) REFERENCES workcells (accession_id), 
	FOREIGN KEY(resource_counterpart_accession_id) REFERENCES resources (accession_id), 
	FOREIGN KEY(deck_child_accession_id) REFERENCES decks (accession_id), 
	FOREIGN KEY(deck_child_definition_accession_id) REFERENCES deck_definition_catalog (accession_id), 
	FOREIGN KEY(current_protocol_run_accession_id) REFERENCES protocol_runs (accession_id), 
	FOREIGN KEY(machine_definition_accession_id) REFERENCES machine_definitions (accession_id)
);

CREATE INDEX ix_machines_name ON machines (name);
CREATE INDEX ix_machines_last_seen_online ON machines (last_seen_online);
CREATE INDEX ix_machines_location ON machines (location);
CREATE INDEX ix_machines_accession_id ON machines (accession_id);
CREATE INDEX ix_machines_fqn ON machines (fqn);

-- Table: resources
CREATE TABLE resources (
	accession_id CHAR(32) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, 
	name VARCHAR NOT NULL, 
	asset_type VARCHAR(16) NOT NULL, 
	fqn VARCHAR, 
	location VARCHAR, 
	properties_json TEXT, 
	plr_state TEXT, 
	plr_definition TEXT, 
	status VARCHAR(20) NOT NULL, 
	status_details VARCHAR, 
	location_label VARCHAR, 
	current_deck_position_name VARCHAR, 
	resource_definition_accession_id CHAR(32), 
	parent_accession_id CHAR(32), 
	current_protocol_run_accession_id CHAR(32), 
	machine_location_accession_id CHAR(32), 
	deck_location_accession_id CHAR(32), 
	workcell_accession_id CHAR(32), 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(resource_definition_accession_id) REFERENCES resource_definitions (accession_id), 
	FOREIGN KEY(parent_accession_id) REFERENCES resources (accession_id), 
	FOREIGN KEY(current_protocol_run_accession_id) REFERENCES protocol_runs (accession_id), 
	FOREIGN KEY(machine_location_accession_id) REFERENCES machines (accession_id), 
	FOREIGN KEY(deck_location_accession_id) REFERENCES decks (accession_id), 
	FOREIGN KEY(workcell_accession_id) REFERENCES workcells (accession_id)
);

CREATE INDEX ix_resources_fqn ON resources (fqn);
CREATE INDEX ix_resources_location ON resources (location);
CREATE INDEX ix_resources_name ON resources (name);
CREATE INDEX ix_resources_accession_id ON resources (accession_id);
