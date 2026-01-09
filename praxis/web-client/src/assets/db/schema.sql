-- Auto-generated SQLite schema from SQLAlchemy ORM models
-- Generated at: 2026-01-09T00:43:57.670605
-- DO NOT EDIT MANUALLY - regenerate using: uv run scripts/generate_browser_schema.py

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Metadata table for schema versioning
CREATE TABLE IF NOT EXISTS _schema_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR REPLACE INTO _schema_metadata (key, value) VALUES ('generated_at', '2026-01-09T00:43:57.670613');
INSERT OR REPLACE INTO _schema_metadata (key, value) VALUES ('schema_version', '1.0.0');

-- Table: assets
CREATE TABLE assets (
	asset_type VARCHAR(16) NOT NULL, 
	name VARCHAR NOT NULL, 
	fqn VARCHAR NOT NULL, 
	location VARCHAR, 
	plr_state TEXT, 
	plr_definition TEXT, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	PRIMARY KEY (accession_id)
);

CREATE INDEX ix_assets_accession_id ON assets (accession_id);
CREATE UNIQUE INDEX ix_assets_name ON assets (name);
CREATE INDEX ix_assets_asset_type ON assets (asset_type);
CREATE INDEX ix_assets_location ON assets (location);
CREATE INDEX ix_assets_fqn ON assets (fqn);

-- Table: file_system_protocol_sources
CREATE TABLE file_system_protocol_sources (
	name VARCHAR NOT NULL, 
	base_path VARCHAR NOT NULL, 
	is_recursive INTEGER NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	PRIMARY KEY (accession_id)
);

CREATE INDEX ix_file_system_protocol_sources_accession_id ON file_system_protocol_sources (accession_id);
CREATE UNIQUE INDEX ix_file_system_protocol_sources_name ON file_system_protocol_sources (name);

-- Table: protocol_source_repositories
CREATE TABLE protocol_source_repositories (
	name VARCHAR NOT NULL, 
	git_url VARCHAR NOT NULL, 
	default_ref VARCHAR NOT NULL, 
	local_checkout_path VARCHAR, 
	last_synced_commit VARCHAR, 
	status VARCHAR(16) NOT NULL, 
	auto_sync_enabled INTEGER NOT NULL, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	PRIMARY KEY (accession_id)
);

CREATE INDEX ix_protocol_source_repositories_accession_id ON protocol_source_repositories (accession_id);
CREATE UNIQUE INDEX ix_protocol_source_repositories_name ON protocol_source_repositories (name);
CREATE INDEX ix_protocol_source_repositories_git_url ON protocol_source_repositories (git_url);

-- Table: scheduler_metrics_mv
CREATE TABLE scheduler_metrics_mv (
	metric_timestamp DATETIME NOT NULL, 
	protocols_scheduled INTEGER NOT NULL, 
	protocols_completed INTEGER NOT NULL, 
	protocols_failed INTEGER NOT NULL, 
	protocols_cancelled INTEGER NOT NULL, 
	avg_queue_wait_time_ms FLOAT NOT NULL, 
	avg_execution_time_ms FLOAT NOT NULL, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (metric_timestamp, accession_id)
);

CREATE INDEX ix_scheduler_metrics_mv_accession_id ON scheduler_metrics_mv (accession_id);
CREATE INDEX ix_scheduler_metrics_mv_name ON scheduler_metrics_mv (name);

-- EXCLUDED: users (server-only)

-- Table: workcells
CREATE TABLE workcells (
	accession_id TEXT NOT NULL, 
	name VARCHAR NOT NULL, 
	description TEXT, 
	physical_location VARCHAR, 
	latest_state_json TEXT, 
	last_state_update_time DATETIME, 
	status VARCHAR NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	PRIMARY KEY (accession_id)
);

CREATE UNIQUE INDEX ix_workcells_name ON workcells (name);
CREATE INDEX ix_workcells_accession_id ON workcells (accession_id);

-- Table: deck_definition_catalog
CREATE TABLE deck_definition_catalog (
	default_size_x_mm FLOAT, 
	default_size_y_mm FLOAT, 
	default_size_z_mm FLOAT, 
	serialized_constructor_args_json TEXT, 
	serialized_assignment_methods_json TEXT, 
	serialized_constructor_hints_json TEXT, 
	additional_properties_json TEXT, 
	positioning_config_json TEXT, 
	asset_requirement_accession_id TEXT, 
	fqn VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	description TEXT, 
	plr_category VARCHAR, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	PRIMARY KEY (accession_id), 
	CONSTRAINT uq_deck_type_definitions_fqn UNIQUE (fqn), 
	FOREIGN KEY(asset_requirement_accession_id) REFERENCES protocol_asset_requirements (accession_id)
);

CREATE UNIQUE INDEX ix_deck_definition_catalog_fqn ON deck_definition_catalog (fqn);
CREATE INDEX ix_deck_definition_catalog_accession_id ON deck_definition_catalog (accession_id);
CREATE INDEX ix_deck_definition_catalog_name ON deck_definition_catalog (name);
CREATE INDEX ix_deck_definition_catalog_asset_requirement_accession_id ON deck_definition_catalog (asset_requirement_accession_id);

-- Table: deck_position_definitions
CREATE TABLE deck_position_definitions (
	deck_type_id TEXT NOT NULL, 
	position_accession_id VARCHAR NOT NULL, 
	nominal_x_mm FLOAT NOT NULL, 
	nominal_y_mm FLOAT NOT NULL, 
	nominal_z_mm FLOAT NOT NULL, 
	pylabrobot_position_type_name VARCHAR, 
	allowed_resource_definition_names TEXT, 
	accepts_tips INTEGER, 
	accepts_plates INTEGER, 
	accepts_tubes INTEGER, 
	notes TEXT, 
	compatible_resource_fqns TEXT, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (accession_id), 
	CONSTRAINT uq_deck_position UNIQUE (deck_type_id, position_accession_id), 
	FOREIGN KEY(deck_type_id) REFERENCES deck_definition_catalog (accession_id)
);

CREATE INDEX ix_deck_position_definitions_position_accession_id ON deck_position_definitions (position_accession_id);
CREATE INDEX ix_deck_position_definitions_deck_type_id ON deck_position_definitions (deck_type_id);
CREATE INDEX ix_deck_position_definitions_name ON deck_position_definitions (name);
CREATE INDEX ix_deck_position_definitions_accession_id ON deck_position_definitions (accession_id);

-- Table: parameter_definitions
CREATE TABLE parameter_definitions (
	protocol_definition_accession_id TEXT NOT NULL, 
	name VARCHAR NOT NULL, 
	type_hint VARCHAR NOT NULL, 
	fqn VARCHAR NOT NULL, 
	is_deck_param INTEGER NOT NULL, 
	optional INTEGER NOT NULL, 
	default_value_repr VARCHAR, 
	description TEXT, 
	constraints TEXT, 
	field_type VARCHAR, 
	is_itemized INTEGER NOT NULL, 
	itemized_spec TEXT, 
	linked_to VARCHAR, 
	ui_hint TEXT, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	PRIMARY KEY (accession_id), 
	CONSTRAINT uq_param_def_name_per_protocol_v3 UNIQUE (protocol_definition_accession_id, name), 
	FOREIGN KEY(protocol_definition_accession_id) REFERENCES function_protocol_definitions (accession_id)
);

CREATE INDEX ix_parameter_definitions_fqn ON parameter_definitions (fqn);
CREATE INDEX ix_parameter_definitions_name ON parameter_definitions (name);
CREATE INDEX ix_parameter_definitions_protocol_definition_accession_id ON parameter_definitions (protocol_definition_accession_id);
CREATE INDEX ix_parameter_definitions_type_hint ON parameter_definitions (type_hint);
CREATE INDEX ix_parameter_definitions_accession_id ON parameter_definitions (accession_id);

-- Table: protocol_asset_requirements
CREATE TABLE protocol_asset_requirements (
	protocol_definition_accession_id TEXT NOT NULL, 
	name VARCHAR NOT NULL, 
	type_hint_str VARCHAR NOT NULL, 
	actual_type_str VARCHAR NOT NULL, 
	fqn VARCHAR NOT NULL, 
	optional INTEGER NOT NULL, 
	default_value_repr VARCHAR, 
	description TEXT, 
	constraints TEXT, 
	location_constraints TEXT, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	PRIMARY KEY (accession_id), 
	CONSTRAINT uq_asset_def_name_per_protocol_v3 UNIQUE (protocol_definition_accession_id, name), 
	FOREIGN KEY(protocol_definition_accession_id) REFERENCES function_protocol_definitions (accession_id)
);

CREATE INDEX ix_protocol_asset_requirements_accession_id ON protocol_asset_requirements (accession_id);
CREATE INDEX ix_protocol_asset_requirements_fqn ON protocol_asset_requirements (fqn);
CREATE INDEX ix_protocol_asset_requirements_actual_type_str ON protocol_asset_requirements (actual_type_str);
CREATE INDEX ix_protocol_asset_requirements_name ON protocol_asset_requirements (name);
CREATE INDEX ix_protocol_asset_requirements_protocol_definition_accession_id ON protocol_asset_requirements (protocol_definition_accession_id);
CREATE INDEX ix_protocol_asset_requirements_type_hint_str ON protocol_asset_requirements (type_hint_str);

-- EXCLUDED: schedule_entries (server-only)

-- EXCLUDED: schedule_history (server-only)

-- Table: function_protocol_definitions
CREATE TABLE function_protocol_definitions (
	fqn VARCHAR NOT NULL, 
	version VARCHAR NOT NULL, 
	description TEXT, 
	source_file_path VARCHAR NOT NULL, 
	module_name VARCHAR NOT NULL, 
	function_name VARCHAR NOT NULL, 
	source_repository_accession_id TEXT, 
	commit_hash VARCHAR, 
	file_system_source_accession_id TEXT, 
	is_top_level INTEGER NOT NULL, 
	solo_execution INTEGER NOT NULL, 
	preconfigure_deck INTEGER NOT NULL, 
	requires_deck INTEGER NOT NULL, 
	deck_param_name VARCHAR, 
	deck_construction_function_fqn VARCHAR, 
	deck_layout_path VARCHAR, 
	state_param_name VARCHAR, 
	category VARCHAR, 
	tags TEXT, 
	deprecated INTEGER NOT NULL, 
	hardware_requirements_json TEXT, 
	data_views_json TEXT, 
	computation_graph_json TEXT, 
	source_hash VARCHAR, 
	graph_cached_at DATETIME, 
	setup_instructions_json TEXT, 
	simulation_result_json TEXT, 
	inferred_requirements_json TEXT, 
	failure_modes_json TEXT, 
	simulation_version VARCHAR(32), 
	simulation_cached_at DATETIME, 
	cached_bytecode BLOB, 
	bytecode_python_version VARCHAR(16), 
	bytecode_cache_version VARCHAR(16), 
	bytecode_cached_at DATETIME, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (accession_id), 
	CONSTRAINT uq_repo_protocol_def_version_v3 UNIQUE (name, version, source_repository_accession_id, commit_hash), 
	CONSTRAINT uq_fs_protocol_def_version_v3 UNIQUE (name, version, file_system_source_accession_id, source_file_path), 
	FOREIGN KEY(source_repository_accession_id) REFERENCES protocol_source_repositories (accession_id), 
	FOREIGN KEY(file_system_source_accession_id) REFERENCES file_system_protocol_sources (accession_id)
);

CREATE INDEX ix_function_protocol_definitions_fqn ON function_protocol_definitions (fqn);
CREATE INDEX ix_function_protocol_definitions_category ON function_protocol_definitions (category);
CREATE INDEX ix_function_protocol_definitions_name ON function_protocol_definitions (name);
CREATE INDEX ix_function_protocol_definitions_function_name ON function_protocol_definitions (function_name);
CREATE INDEX ix_function_protocol_definitions_is_top_level ON function_protocol_definitions (is_top_level);
CREATE INDEX ix_function_protocol_definitions_file_system_source_accession_id ON function_protocol_definitions (file_system_source_accession_id);
CREATE INDEX ix_function_protocol_definitions_accession_id ON function_protocol_definitions (accession_id);
CREATE INDEX ix_function_protocol_definitions_module_name ON function_protocol_definitions (module_name);
CREATE INDEX ix_function_protocol_definitions_source_file_path ON function_protocol_definitions (source_file_path);
CREATE INDEX ix_function_protocol_definitions_deprecated ON function_protocol_definitions (deprecated);
CREATE INDEX ix_function_protocol_definitions_commit_hash ON function_protocol_definitions (commit_hash);
CREATE INDEX ix_function_protocol_definitions_source_repository_accession_id ON function_protocol_definitions (source_repository_accession_id);

-- Table: protocol_runs
CREATE TABLE protocol_runs (
	top_level_protocol_definition_accession_id TEXT NOT NULL, 
	status VARCHAR(21) NOT NULL, 
	start_time DATETIME, 
	end_time DATETIME, 
	input_parameters_json TEXT, 
	resolved_assets_json TEXT, 
	output_data_json TEXT, 
	initial_state_json TEXT, 
	final_state_json TEXT, 
	data_directory_path VARCHAR, 
	created_by_user TEXT, 
	previous_accession_id TEXT, 
	duration_ms INTEGER, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(top_level_protocol_definition_accession_id) REFERENCES function_protocol_definitions (accession_id), 
	FOREIGN KEY(previous_accession_id) REFERENCES protocol_runs (accession_id)
);

CREATE INDEX ix_protocol_runs_accession_id ON protocol_runs (accession_id);
CREATE INDEX ix_protocol_runs_name ON protocol_runs (name);
CREATE INDEX ix_protocol_runs_status ON protocol_runs (status);
CREATE INDEX ix_protocol_runs_previous_accession_id ON protocol_runs (previous_accession_id);
CREATE INDEX ix_protocol_runs_top_level_protocol_definition_accession_id ON protocol_runs (top_level_protocol_definition_accession_id);

-- Table: resource_definition_catalog
CREATE TABLE resource_definition_catalog (
	resource_type VARCHAR, 
	is_consumable INTEGER NOT NULL, 
	nominal_volume_ul FLOAT, 
	material VARCHAR, 
	manufacturer VARCHAR, 
	plr_definition_details_json TEXT, 
	ordering VARCHAR, 
	size_x_mm FLOAT, 
	size_y_mm FLOAT, 
	size_z_mm FLOAT, 
	model VARCHAR, 
	rotation_json TEXT, 
	num_items INTEGER, 
	plate_type VARCHAR, 
	well_volume_ul FLOAT, 
	tip_volume_ul FLOAT, 
	vendor VARCHAR, 
	properties_json TEXT, 
	deck_definition_accession_id TEXT, 
	asset_requirement_accession_id TEXT, 
	fqn VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	description TEXT, 
	plr_category VARCHAR, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(deck_definition_accession_id) REFERENCES deck_definition_catalog (accession_id), 
	FOREIGN KEY(asset_requirement_accession_id) REFERENCES protocol_asset_requirements (accession_id)
);

CREATE INDEX ix_resource_definition_catalog_plate_type ON resource_definition_catalog (plate_type);
CREATE INDEX ix_resource_definition_catalog_vendor ON resource_definition_catalog (vendor);
CREATE INDEX ix_resource_definition_catalog_tip_volume_ul ON resource_definition_catalog (tip_volume_ul);
CREATE INDEX ix_resource_definition_catalog_deck_definition_accession_id ON resource_definition_catalog (deck_definition_accession_id);
CREATE UNIQUE INDEX ix_resource_definition_catalog_fqn ON resource_definition_catalog (fqn);
CREATE INDEX ix_resource_definition_catalog_accession_id ON resource_definition_catalog (accession_id);
CREATE INDEX ix_resource_definition_catalog_name ON resource_definition_catalog (name);
CREATE INDEX ix_resource_definition_catalog_well_volume_ul ON resource_definition_catalog (well_volume_ul);
CREATE INDEX ix_resource_definition_catalog_num_items ON resource_definition_catalog (num_items);
CREATE INDEX ix_resource_definition_catalog_asset_requirement_accession_id ON resource_definition_catalog (asset_requirement_accession_id);

-- Table: state_resolution_log
CREATE TABLE state_resolution_log (
	schedule_entry_accession_id TEXT NOT NULL, 
	protocol_run_accession_id TEXT NOT NULL, 
	operation_id VARCHAR(255) NOT NULL, 
	operation_description TEXT NOT NULL, 
	error_message TEXT NOT NULL, 
	error_type VARCHAR(255), 
	uncertain_states_json TEXT NOT NULL, 
	resolution_json TEXT NOT NULL, 
	resolution_type VARCHAR(17) NOT NULL, 
	resolved_by VARCHAR(255) NOT NULL, 
	resolved_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	notes TEXT, 
	action_taken VARCHAR(6) NOT NULL, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(schedule_entry_accession_id) REFERENCES schedule_entries (accession_id), 
	FOREIGN KEY(protocol_run_accession_id) REFERENCES protocol_runs (accession_id)
);

CREATE INDEX ix_state_resolution_log_name ON state_resolution_log (name);
CREATE INDEX ix_state_resolution_log_operation_id ON state_resolution_log (operation_id);
CREATE INDEX ix_state_resolution_log_protocol_run_accession_id ON state_resolution_log (protocol_run_accession_id);
CREATE INDEX ix_state_resolution_log_schedule_entry_accession_id ON state_resolution_log (schedule_entry_accession_id);
CREATE INDEX ix_state_resolution_log_accession_id ON state_resolution_log (accession_id);
CREATE INDEX ix_state_resolution_log_action_taken ON state_resolution_log (action_taken);
CREATE INDEX ix_state_resolution_log_resolution_type ON state_resolution_log (resolution_type);

-- Table: well_data_outputs
CREATE TABLE well_data_outputs (
	function_data_output_accession_id TEXT NOT NULL, 
	plate_resource_accession_id TEXT NOT NULL, 
	well_name VARCHAR(10) NOT NULL, 
	well_row INTEGER NOT NULL, 
	well_column INTEGER NOT NULL, 
	well_index INTEGER, 
	data_value FLOAT, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(function_data_output_accession_id) REFERENCES function_data_outputs (accession_id), 
	FOREIGN KEY(plate_resource_accession_id) REFERENCES resources (accession_id)
);

CREATE INDEX ix_well_data_outputs_name ON well_data_outputs (name);
CREATE INDEX ix_well_data_outputs_accession_id ON well_data_outputs (accession_id);
CREATE INDEX ix_well_data_outputs_plate_resource_accession_id ON well_data_outputs (plate_resource_accession_id);
CREATE INDEX ix_well_data_outputs_function_data_output_accession_id ON well_data_outputs (function_data_output_accession_id);

-- Table: decks
CREATE TABLE decks (
	accession_id TEXT NOT NULL, 
	parent_machine_accession_id TEXT, 
	deck_type_id TEXT NOT NULL, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(accession_id) REFERENCES resources (accession_id), 
	CONSTRAINT fk_deck_parent_machine FOREIGN KEY(parent_machine_accession_id) REFERENCES machines (accession_id), 
	FOREIGN KEY(deck_type_id) REFERENCES deck_definition_catalog (accession_id)
);

CREATE INDEX ix_decks_parent_machine_accession_id ON decks (parent_machine_accession_id);
CREATE INDEX ix_decks_accession_id ON decks (accession_id);
CREATE INDEX ix_decks_deck_type_id ON decks (deck_type_id);

-- Table: function_call_logs
CREATE TABLE function_call_logs (
	protocol_run_accession_id TEXT NOT NULL, 
	sequence_in_run INTEGER NOT NULL, 
	function_protocol_definition_accession_id TEXT NOT NULL, 
	parent_function_call_log_accession_id TEXT, 
	start_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	end_time DATETIME, 
	duration_ms INTEGER, 
	input_args_json TEXT, 
	return_value_json TEXT, 
	status VARCHAR(11) NOT NULL, 
	error_message_text TEXT, 
	error_traceback_text TEXT, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(protocol_run_accession_id) REFERENCES protocol_runs (accession_id), 
	FOREIGN KEY(function_protocol_definition_accession_id) REFERENCES function_protocol_definitions (accession_id), 
	FOREIGN KEY(parent_function_call_log_accession_id) REFERENCES function_call_logs (accession_id)
);

CREATE INDEX ix_function_call_logs_function_protocol_definition_accession_id ON function_call_logs (function_protocol_definition_accession_id);
CREATE INDEX ix_function_call_logs_sequence_in_run ON function_call_logs (sequence_in_run);
CREATE INDEX ix_function_call_logs_name ON function_call_logs (name);
CREATE INDEX ix_function_call_logs_protocol_run_accession_id ON function_call_logs (protocol_run_accession_id);
CREATE INDEX ix_function_call_logs_parent_function_call_log_accession_id ON function_call_logs (parent_function_call_log_accession_id);
CREATE INDEX ix_function_call_logs_accession_id ON function_call_logs (accession_id);

-- Table: machine_definition_catalog
CREATE TABLE machine_definition_catalog (
	machine_category VARCHAR(25) NOT NULL, 
	material VARCHAR, 
	manufacturer VARCHAR, 
	plr_definition_details_json TEXT, 
	size_x_mm FLOAT, 
	size_y_mm FLOAT, 
	size_z_mm FLOAT, 
	model VARCHAR, 
	rotation_json TEXT, 
	resource_definition_accession_id TEXT, 
	has_deck INTEGER NOT NULL, 
	deck_definition_accession_id TEXT, 
	setup_method_json TEXT, 
	capabilities TEXT, 
	compatible_backends TEXT, 
	capabilities_config TEXT, 
	connection_config TEXT, 
	frontend_fqn VARCHAR(512), 
	asset_requirement_accession_id TEXT, 
	fqn VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	description TEXT, 
	plr_category VARCHAR, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(resource_definition_accession_id) REFERENCES resource_definition_catalog (accession_id), 
	FOREIGN KEY(deck_definition_accession_id) REFERENCES deck_definition_catalog (accession_id), 
	FOREIGN KEY(asset_requirement_accession_id) REFERENCES protocol_asset_requirements (accession_id)
);

CREATE INDEX ix_machine_definition_catalog_asset_requirement_accession_id ON machine_definition_catalog (asset_requirement_accession_id);
CREATE INDEX ix_machine_definition_catalog_deck_definition_accession_id ON machine_definition_catalog (deck_definition_accession_id);
CREATE INDEX ix_machine_definition_catalog_machine_category ON machine_definition_catalog (machine_category);
CREATE INDEX ix_machine_definition_catalog_accession_id ON machine_definition_catalog (accession_id);
CREATE INDEX ix_machine_definition_catalog_name ON machine_definition_catalog (name);
CREATE INDEX ix_machine_definition_catalog_resource_definition_accession_id ON machine_definition_catalog (resource_definition_accession_id);
CREATE UNIQUE INDEX ix_machine_definition_catalog_fqn ON machine_definition_catalog (fqn);

-- EXCLUDED: asset_reservations (server-only)

-- Table: function_data_outputs
CREATE TABLE function_data_outputs (
	protocol_run_accession_id TEXT NOT NULL, 
	function_call_log_accession_id TEXT NOT NULL, 
	data_type VARCHAR(24) NOT NULL, 
	data_key VARCHAR(255) NOT NULL, 
	spatial_context VARCHAR(13) NOT NULL, 
	resource_accession_id TEXT, 
	machine_accession_id TEXT, 
	deck_accession_id TEXT, 
	spatial_coordinates_json TEXT, 
	data_value_numeric FLOAT, 
	data_value_json TEXT, 
	data_value_text TEXT, 
	data_value_binary BLOB, 
	file_path VARCHAR(500), 
	file_size_bytes INTEGER, 
	data_units VARCHAR(50), 
	data_quality_score FLOAT, 
	measurement_conditions_json TEXT, 
	measurement_timestamp DATETIME NOT NULL, 
	sequence_in_function INTEGER, 
	derived_from_data_output_accession_id TEXT, 
	processing_metadata_json TEXT, 
	accession_id TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	properties_json TEXT, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(protocol_run_accession_id) REFERENCES protocol_runs (accession_id), 
	FOREIGN KEY(function_call_log_accession_id) REFERENCES function_call_logs (accession_id), 
	FOREIGN KEY(resource_accession_id) REFERENCES resources (accession_id), 
	FOREIGN KEY(machine_accession_id) REFERENCES machines (accession_id), 
	FOREIGN KEY(deck_accession_id) REFERENCES decks (accession_id), 
	FOREIGN KEY(derived_from_data_output_accession_id) REFERENCES function_data_outputs (accession_id)
);

CREATE INDEX ix_function_data_outputs_spatial_context ON function_data_outputs (spatial_context);
CREATE INDEX ix_function_data_outputs_function_call_log_accession_id ON function_data_outputs (function_call_log_accession_id);
CREATE INDEX ix_function_data_outputs_data_type ON function_data_outputs (data_type);
CREATE INDEX ix_function_data_outputs_name ON function_data_outputs (name);
CREATE INDEX ix_function_data_outputs_resource_accession_id ON function_data_outputs (resource_accession_id);
CREATE INDEX ix_function_data_outputs_derived_from_data_output_accession_id ON function_data_outputs (derived_from_data_output_accession_id);
CREATE INDEX ix_function_data_outputs_protocol_run_accession_id ON function_data_outputs (protocol_run_accession_id);
CREATE INDEX ix_function_data_outputs_deck_accession_id ON function_data_outputs (deck_accession_id);
CREATE INDEX ix_function_data_outputs_machine_accession_id ON function_data_outputs (machine_accession_id);
CREATE INDEX ix_function_data_outputs_accession_id ON function_data_outputs (accession_id);

-- Table: machines
CREATE TABLE machines (
	accession_id TEXT NOT NULL, 
	machine_category VARCHAR(25) NOT NULL, 
	description TEXT, 
	manufacturer VARCHAR, 
	model VARCHAR, 
	serial_number VARCHAR, 
	location_label VARCHAR, 
	maintenance_enabled INTEGER NOT NULL, 
	maintenance_schedule_json TEXT, 
	last_maintenance_json TEXT, 
	installation_date DATETIME, 
	status VARCHAR(12) NOT NULL, 
	status_details TEXT, 
	connection_info TEXT, 
	is_simulation_override INTEGER, 
	user_configured_capabilities TEXT, 
	workcell_accession_id TEXT, 
	resource_counterpart_accession_id TEXT, 
	deck_child_accession_id TEXT, 
	deck_child_definition_accession_id TEXT, 
	last_seen_online DATETIME, 
	current_protocol_run_accession_id TEXT, 
	machine_definition_accession_id TEXT, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(accession_id) REFERENCES assets (accession_id), 
	UNIQUE (serial_number), 
	FOREIGN KEY(workcell_accession_id) REFERENCES workcells (accession_id), 
	CONSTRAINT fk_machine_resource_counterpart FOREIGN KEY(resource_counterpart_accession_id) REFERENCES resources (accession_id) ON DELETE SET NULL, 
	CONSTRAINT fk_machine_deck_child FOREIGN KEY(deck_child_accession_id) REFERENCES decks (accession_id) ON DELETE SET NULL, 
	FOREIGN KEY(deck_child_definition_accession_id) REFERENCES deck_definition_catalog (accession_id) ON DELETE SET NULL, 
	FOREIGN KEY(current_protocol_run_accession_id) REFERENCES protocol_runs (accession_id) ON DELETE SET NULL, 
	FOREIGN KEY(machine_definition_accession_id) REFERENCES machine_definition_catalog (accession_id)
);

CREATE INDEX ix_machines_machine_category ON machines (machine_category);
CREATE INDEX ix_machines_workcell_accession_id ON machines (workcell_accession_id);
CREATE INDEX ix_machines_last_seen_online ON machines (last_seen_online);
CREATE INDEX ix_machines_deck_child_definition_accession_id ON machines (deck_child_definition_accession_id);
CREATE INDEX ix_machines_deck_child_accession_id ON machines (deck_child_accession_id);
CREATE INDEX ix_machines_resource_counterpart_accession_id ON machines (resource_counterpart_accession_id);
CREATE INDEX ix_machines_machine_definition_accession_id ON machines (machine_definition_accession_id);
CREATE INDEX ix_machines_current_protocol_run_accession_id ON machines (current_protocol_run_accession_id);
CREATE INDEX ix_machines_status ON machines (status);

-- Table: resources
CREATE TABLE resources (
	accession_id TEXT NOT NULL, 
	resource_definition_accession_id TEXT, 
	parent_accession_id TEXT, 
	status VARCHAR(20) NOT NULL, 
	status_details TEXT, 
	current_protocol_run_accession_id TEXT, 
	location_label VARCHAR, 
	current_deck_position_name VARCHAR, 
	machine_location_accession_id TEXT, 
	deck_accession_id TEXT, 
	workcell_accession_id TEXT, 
	PRIMARY KEY (accession_id), 
	FOREIGN KEY(accession_id) REFERENCES assets (accession_id), 
	FOREIGN KEY(resource_definition_accession_id) REFERENCES resource_definition_catalog (accession_id), 
	FOREIGN KEY(parent_accession_id) REFERENCES resources (accession_id), 
	FOREIGN KEY(current_protocol_run_accession_id) REFERENCES protocol_runs (accession_id) ON DELETE SET NULL, 
	CONSTRAINT fk_resource_machine_location FOREIGN KEY(machine_location_accession_id) REFERENCES machines (accession_id), 
	CONSTRAINT fk_resource_deck FOREIGN KEY(deck_accession_id) REFERENCES decks (accession_id) ON DELETE CASCADE, 
	FOREIGN KEY(workcell_accession_id) REFERENCES workcells (accession_id)
);

CREATE INDEX ix_resources_status ON resources (status);
CREATE INDEX ix_resources_machine_location_accession_id ON resources (machine_location_accession_id);
CREATE INDEX ix_resources_resource_definition_accession_id ON resources (resource_definition_accession_id);
CREATE INDEX ix_resources_workcell_accession_id ON resources (workcell_accession_id);
CREATE INDEX ix_resources_accession_id ON resources (accession_id);
CREATE INDEX ix_resources_deck_accession_id ON resources (deck_accession_id);
CREATE INDEX ix_resources_current_protocol_run_accession_id ON resources (current_protocol_run_accession_id);
CREATE INDEX ix_resources_parent_accession_id ON resources (parent_accession_id);
