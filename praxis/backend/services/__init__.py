"""Service layer for data management.

Services in this module provide an interface for managing various data entities
such as deck layouts, resource definitions, machines, and protocol runs.

These services interact with the database and provide methods for CRUD operations,
as well as specialized queries and updates. They are designed to be used by
higher-level application logic, such as API endpoints or background tasks.

They are conveniently imported and re-exported in the `__init__.py` file
to provide a single point of access for all data services.
"""

from .deck import deck_service
from .deck_position import (
    create_deck_position_definitions,
    delete_deck_position_definition,
    update_deck_position_definition,
    read_position_definitions_for_deck_type,
)
from .deck_type_definition import (
  create_deck_type_definition,
  delete_deck_type_definition,
  read_deck_type_definition,
  read_deck_type_definition_by_name,
  read_deck_type_definitions,
  update_deck_type_definition,
)
from .discovery_service import ProtocolDiscoveryService
from .function_output_data import (
  create_function_data_output,
  delete_function_data_output,
  list_function_data_outputs,
  read_function_data_output,
  update_function_data_output,
)
from .machine import machine_service
from .plate_viz import read_plate_data_visualization
from .praxis_orm_service import PraxisDBService
from .protocol_output_data import (
  read_protocol_run_data_summary,
)
from .protocols import protocol_run_service
from .resource import resource_service
from .resource_type_definition import (
  create_resource_definition,
  delete_resource_definition,
  read_resource_definition,
  read_resource_definition_by_fqn,
  read_resource_definitions,
  update_resource_definition,
)
from .workcell import workcell_service

__all__ = [
  # Deck
  "deck_service",
  # Deck Type Definition
  "create_deck_type_definition",
  "delete_deck_type_definition",
  "read_deck_type_definition",
  "read_deck_type_definition_by_name",
  "read_deck_type_definitions",
  "update_deck_type_definition",
  "ProtocolDiscoveryService",
  # Function Output Data
  "create_function_data_output",
  "delete_function_data_output",
  "list_function_data_outputs",
  "read_function_data_output",
  "update_function_data_output",
  # Machine
  "machine_service",
  # Plate Viz
  "read_plate_data_visualization",
  # Praxis ORM Service
  "PraxisDBService",
  # Protocol Output Data
  "read_protocol_run_data_summary",
  # Protocols
  "protocol_run_service",
  # Resource
  "resource_service",
  # Resource Definition
  "create_resource_definition",
  "delete_resource_definition",
  "read_resource_definition",
  "read_resource_definition_by_fqn",
  "read_resource_definitions",
  "update_resource_definition",
  # Workcell
  "workcell_service",
  # Deck Position
    "create_deck_position_definitions",
    "delete_deck_position_definition",
    "update_deck_position_definition",
    "read_position_definitions_for_deck_type",
]
