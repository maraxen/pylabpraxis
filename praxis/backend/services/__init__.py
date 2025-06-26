"""Service layer for data management.

Services in this module provide an interface for managing various data entities
such as deck layouts, resource definitions, machines, and protocol runs.

These services interact with the database and provide methods for CRUD operations,
as well as specialized queries and updates. They are designed to be used by
higher-level application logic, such as API endpoints or background tasks.

They are conveniently imported and re-exported in the `__init__.py` file
to provide a single point of access for all data services.
"""

from .deck import (
  create_deck,
  delete_deck,
  read_deck,
  read_deck_by_name,
  read_decks,
  update_deck,
)
from .deck_type_definition import (
  create_deck_type_definition,
  delete_deck_type_definition,
  read_deck_type_definition,
  read_deck_type_definition_by_name,
  read_deck_type_definitions,
  update_deck_type_definition,
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
  read_machines_by_workcell_id,
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
  read_protocol_definition_by_name,
  read_protocol_definition_details,
  read_protocol_run,
  read_protocol_run_by_name,
  read_protocol_source_repository,
  read_protocol_source_repository_by_name,
  update_file_system_protocol_source,
  update_protocol_run_status,
  update_protocol_source_repository,
  upsert_function_protocol_definition,
)
from .resource import (
  create_resource,
  delete_resource,
  read_resource,
  read_resource_by_name,
  read_resources,
  update_resource,
)
from .resource_type_definition import (
  create_resource_definition,
  delete_resource_definition,
  read_resource_definition,
  read_resource_definition_by_fqn,
  read_resource_definitions,
  update_resource_definition,
)
from .workcell import (
  create_workcell,
  delete_workcell,
  list_workcells,
  read_workcell,
  read_workcell_by_name,
  update_workcell,
)

__all__ = [
  # Deck
  "create_deck",
  "delete_deck",
  "read_deck",
  "read_deck_by_name",
  "read_decks",
  "update_deck",
  # Deck Type Definition
  "create_deck_type_definition",
  "delete_deck_type_definition",
  "read_deck_type_definition",
  "read_deck_type_definition_by_name",
  "read_deck_type_definitions",
  "update_deck_type_definition",
  "upsert_discovered_function_protocol_definition",
  # Function Output Data
  "create_function_data_output",
  "delete_function_data_output",
  "list_function_data_outputs",
  "read_function_data_output",
  "update_function_data_output",
  # Machine
  "create_machine",
  "delete_machine",
  "list_machines",
  "read_machine",
  "read_machine_by_name",
  "read_machines_by_workcell_id",
  "update_machine",
  "update_machine_status",
  # Plate Viz
  "read_plate_data_visualization",
  # Praxis ORM Service
  "PraxisDBService",
  # Protocol Output Data
  "read_protocol_run_data_summary",
  # Protocols
  "create_file_system_protocol_source",
  "create_protocol_run",
  "create_protocol_source_repository",
  "list_active_protocol_sources",
  "list_protocol_definitions",
  "list_protocol_runs",
  "list_protocol_source_repositories",
  "log_function_call_end",
  "log_function_call_start",
  "read_function_call_logs_for_run",
  "read_protocol_definition",
  "read_protocol_definition_by_name",
  "read_protocol_definition_details",
  "read_protocol_run",
  "read_protocol_run_by_name",
  "read_protocol_source_repository",
  "read_protocol_source_repository_by_name",
  "update_file_system_protocol_source",
  "update_protocol_run_status",
  "update_protocol_source_repository",
  "upsert_function_protocol_definition",
  # Resource
  "create_resource",
  "delete_resource",
  "read_resource",
  "read_resource_by_name",
  "read_resources",
  "update_resource",
  # Resource Definition
  "create_resource_definition",
  "delete_resource_definition",
  "read_resource_definition",
  "read_resource_definition_by_fqn",
  "read_resource_definitions",
  "update_resource_definition",
  # Workcell
  "create_workcell",
  "delete_workcell",
  "list_workcells",
  "read_workcell",
  "read_workcell_by_name",
  "update_workcell",
]
