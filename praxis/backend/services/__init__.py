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
  read_deck_instance_by_id,
  read_deck_instance_by_name,
  read_deck_instance_by_parent_machine_id,
  update_deck_instance,
  delete_deck_instance,
  list_deck_instances,
)
from .deck_position import (
  create_deck_position_definitions,
  create_deck_position_item,
  read_deck_position_item,
  read_position_definitions_for_deck_type,
  update_deck_position_item,
  update_deck_position_definition,
  delete_deck_position_item,
  delete_deck_position_item,
)
from .deck_type_definition import (
  create_deck_type_definition,
  read_deck_type_definition_by_fqn,
  read_deck_type_definition_by_id,
  update_deck_type_definition,
  delete_deck_type_definition,
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
from .machine_data_service import (
  add_or_update_machine,
  delete_machine,
  get_machine_by_id,
  get_machine_by_name,
  get_machines_by_workcell_id,
  list_machines,
  update_machine_status,
)
from .praxis_orm_service import PraxisDBService
from .protocol_data_service import (
  add_or_update_file_system_protocol_source,
  add_or_update_protocol_source_repository,
  create_protocol_run,
  get_function_call_logs_for_run,
  get_protocol_definition_by_id,
  get_protocol_definition_details,
  get_protocol_run_by_guid,
  list_active_protocol_sources,
  list_protocol_definitions,
  list_protocol_runs,
  log_function_call_end,
  log_function_call_start,
  update_protocol_run_status,
)
from .protocol_data_service import (
  upsert_function_protocol_definition as upsert_function_protocol_definition,
)
from .resource_data_service import (
  add_or_update_resource_definition,
  add_resource_instance,
  delete_resource_definition,
  delete_resource_instance,
  get_resource_definition,
  get_resource_definition_by_fqn,
  get_resource_definition_by_name,
  get_resource_instance_by_id,
  get_resource_instance_by_name,
  list_resource_definitions,
  list_resource_instances,
  update_resource_instance,
  update_resource_instance_location_and_status,
)
from .workcell_data_service import (
  create_workcell,
  delete_workcell,
  get_or_create_workcell_orm,
  get_workcell_by_id,
  get_workcell_by_name,
  get_workcell_state,
  list_workcells,
  update_workcell,
  update_workcell_state,
)

__all__ = [
  "get_deck_config_by_id",
  "get_deck_config_by_name",
  "get_resource_definition",
  "get_resource_definition_by_fqn",
  "get_resource_definition_by_name",
  "get_resource_instance_by_id",
  "get_resource_instance_by_name",
  "get_machine_by_id",
  "get_machine_by_name",
  "list_deck_configs",
  "list_resource_definitions",
  "list_resource_instances",
  "list_machines",
  "add_resource_instance",
  "add_or_update_resource_definition",
  "add_or_update_machine",
  "update_resource_instance_location_and_status",
  "update_deck_config",
  "update_machine_status",
  "delete_deck_config",
  "delete_resource_definition",
  "delete_resource_instance",
  "delete_machine",
  "create_deck_config",
  "read_deck_position_item",
  "update_deck_position_item",
  "get_deck_type_definition_by_fqn",
  "list_deck_type_definitions",
  "add_or_update_deck_type_definition",
  "add_deck_position_definitions",
  "get_deck_type_definition_by_id",
  "get_position_definitions_for_deck_type",
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
  "get_function_call_logs_for_run",
  "get_protocol_definition_by_id",
  "get_protocol_definition_details",
  "get_protocol_run_by_guid",
  "add_or_update_file_system_protocol_source",
  "add_or_update_protocol_source_repository",
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
  "get_workcell_by_id",
  "get_workcell_by_name",
  "list_workcells",
  "get_machines_by_workcell_id",
  "get_deck_config_by_id",
  "get_deck_config_by_name",
  "get_deck_config_by_parent_machine_id",
  "create_deck_position_item",
  "get_or_create_workcell_orm",
  "get_workcell_state",
  "update_workcell_state",
  "update_resource_instance",
]
