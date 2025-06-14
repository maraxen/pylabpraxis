"""Service layer for data management.

Services in this module provide an interface for managing various data entities
such as deck layouts, resource definitions, machines, and protocol runs.

These services interact with the database and provide methods for CRUD operations,
as well as specialized queries and updates. They are designed to be used by
higher-level application logic, such as API endpoints or background tasks.

They are conveniently imported and re-exported in the `__init__.py` file
to provide a single point of access for all data services.
"""

from .deck_instance import (
  create_deck_instance,
  delete_deck_instance,
  list_deck_instances,
  read_deck_instance,
  read_deck_instance_by_name,
  read_deck_instance_by_parent_machine_accession_id,
  update_deck_instance,
)
from .deck_position import (
  create_deck_position_definitions,
  create_deck_position_item,
  delete_deck_position_item,
  read_deck_position_item,
  read_position_definitions_for_deck_type,
  update_deck_position_definition,
  update_deck_position_item,
)
from .deck_type_definition import (
  create_deck_type_definition,
  delete_deck_type_definition,
  list_deck_type_definitions,
  read_deck_type_definition,
  read_deck_type_definition_by_fqn,
  update_deck_type_definition,
)
from .discovery_service import (
  get_actual_type_str_from_hint,
  get_args,
  get_origin,
  is_pylabrobot_resource,
  serialize_type_hint_str,
)
from .discovery_service import (
  upsert_function_protocol_definition as upsert_discovered_function_protocol_definition,
)
from .function_output_data import (
  create_function_data_output,
  delete_function_data_output,
  list_function_data_outputs,
  read_function_data_output,
  update_function_data_output,
)
from .machine import (
  create_machine,
  delete_machine,
  list_machines,
  read_machine,
  read_machine_by_name,
  read_machines_by_workcell_accession_id,
  update_machine,
  update_machine_status,
)
from .plate_viz import read_plate_data_visualization
from .praxis_orm_service import PraxisDBService
from .protocol_output_data import (
  read_protocol_run_data_summary,
)
from .protocols import (
  create_file_system_protocol_source,
  create_protocol_run,
  create_protocol_source_repository,
  list_active_protocol_sources,
  list_protocol_definitions,
  list_protocol_runs,
  list_protocol_source_repositories,
  log_function_call_end,
  log_function_call_start,
  read_function_call_logs_for_run,
  read_protocol_definition,
  read_protocol_definition_details,
  read_protocol_run_by_accession_id,
  update_file_system_protocol_source,
  update_protocol_run_status,
  update_protocol_source_repository,
  upsert_function_protocol_definition,
)
from .resource_instance import (
  create_resource_instance,
  delete_resource_instance,
  delete_resource_instance_by_name,
  list_resource_instances,
  read_resource_instance,
  read_resource_instance_by_name,
  update_resource_instance,
  update_resource_instance_location_and_status,
)
from .resource_type_definition import (
  create_resource_definition,
  delete_resource_definition,
  list_resource_definitions,
  read_resource_definition,
  read_resource_definition_by_fqn,
  read_resource_definition_by_name,
  update_resource_definition,
)
from .well_outputs import (
  create_well_data_output,
  create_well_data_outputs,
  create_well_data_outputs_from_flat_array,
  delete_well_data_output,
  read_well_data_output,
  read_well_data_outputs,
  update_well_data_output,
)
from .workcell import (
  create_workcell,
  delete_workcell,
  list_workcells,
  read_or_create_workcell_orm,
  read_workcell,
  read_workcell_by_name,
  read_workcell_state,
  update_workcell,
  update_workcell_state,
)

__all__ = [
  "read_deck_instance",
  "read_deck_instance_by_name",
  "read_resource_definition",
  "read_resource_definition_by_fqn",
  "read_resource_definition_by_name",
  "read_resource_instance",
  "read_resource_instance_by_name",
  "read_machine",
  "read_machine_by_name",
  "list_deck_instances",
  "list_resource_definitions",
  "list_resource_instances",
  "list_machines",
  "create_resource_instance",
  "create_resource_definition",
  "read_resource_definition",
  "read_resource_definition_by_name",
  "update_resource_definition",
  "delete_resource_definition",
  "update_resource_instance_location_and_status",
  "update_deck_instance",
  "update_machine_status",
  "delete_deck_instance",
  "delete_resource_instance",
  "delete_machine",
  "create_deck_instance",
  "read_deck_position_item",
  "update_deck_position_item",
  "read_deck_type_definition_by_fqn",
  "list_deck_type_definitions",
  "create_deck_type_definition",
  "update_deck_type_definition",
  "delete_deck_type_definition",
  "create_deck_position_definitions",
  "update_deck_position_definition",
  "delete_deck_position_item",
  "read_deck_type_definition",
  "read_position_definitions_for_deck_type",
  # Discovery service
  "is_pylabrobot_resource",
  "get_actual_type_str_from_hint",
  "get_args",
  "get_origin",
  "serialize_type_hint_str",
  "upsert_discovered_function_protocol_definition",
  # Praxis ORM service
  "PraxisDBService",
  # Protocol data service
  "read_function_call_logs_for_run",
  "read_protocol_definition",
  "read_protocol_definition_details",
  "read_protocol_run_by_accession_id",
  "list_active_protocol_sources",
  "list_protocol_definitions",
  "list_protocol_runs",
  "log_function_call_end",
  "log_function_call_start",
  "update_protocol_run_status",
  "upsert_discovered_function_protocol_definition",
  "create_protocol_run",
  # Workcell data service
  "create_workcell",
  "update_workcell",
  "delete_workcell",
  "read_workcell",
  "read_workcell_by_name",
  "list_workcells",
  "read_machines_by_workcell_accession_id",
  "read_deck_instance",
  "read_deck_instance_by_name",
  "read_deck_instance_by_parent_machine_accession_id",
  "create_deck_position_item",
  "read_or_create_workcell_orm",
  "read_workcell_state",
  "update_workcell_state",
  "update_resource_instance",
  "create_machine",
  "update_machine",
  "update_deck_position_item",
  "read_workcell_state",
  "read_workcell",
  "read_workcell_by_name",
  "create_file_system_protocol_source",
  "update_file_system_protocol_source",
  "create_protocol_source_repository",
  "update_protocol_source_repository",
  "list_protocol_source_repositories",
  "delete_resource_instance_by_name",
  "create_function_data_output",
  "delete_function_data_output",
  "list_function_data_outputs",
  "read_function_data_output",
  "update_function_data_output",
  "create_well_data_output",
  "create_well_data_outputs",
  "create_well_data_outputs_from_flat_array",
  "delete_well_data_output",
  "read_well_data_output",
  "read_well_data_outputs",
  "update_well_data_output",
  "read_plate_data_visualization",
  "read_protocol_run_data_summary",
  "upsert_function_protocol_definition",
]
