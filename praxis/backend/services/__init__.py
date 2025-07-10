"""Service layer for data management.

Services in this module provide an interface for managing various data entities
such as deck layouts, resource definitions, machines, and protocol runs.

These services interact with the database and provide methods for CRUD operations,
as well as specialized queries and updates. They are designed to be used by
higher-level application logic, such as API endpoints or background tasks.

They are conveniently imported and re-exported in the `__init__.py` file
to provide a single point of access for all data services.
"""

from praxis.backend.services.deck import deck_service
from praxis.backend.services.deck_type_definition import DeckTypeDefinitionService
from praxis.backend.services.discovery_service import DiscoveryService
from praxis.backend.services.outputs import (
    FunctionDataOutputCRUDService,
)
from praxis.backend.services.machine import machine_service
from praxis.backend.services.plate_viz import read_plate_data_visualization
from praxis.backend.services.praxis_orm_service import PraxisDBService
from praxis.backend.services.protocol_output_data import (
    read_protocol_run_data_summary,
)
from praxis.backend.services.protocols import protocol_run_service
from praxis.backend.services.resource import resource_service
from praxis.backend.services.resource_type_definition import ResourceTypeDefinitionService
from praxis.backend.services.workcell import workcell_service

__all__ = [
  # Deck
  "deck_service",
  # Deck Type Definition
  "DeckTypeDefinitionService",
  "DiscoveryService",
  # Function Output Data
  "FunctionDataOutputCRUDService",
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
  "ResourceTypeDefinitionService",
  # Workcell
  "workcell_service",
]