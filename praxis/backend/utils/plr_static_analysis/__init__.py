"""PLR Static Analysis module.

This module provides LibCST-based static analysis for PyLabRobot sources,
replacing the runtime inspection approach in plr_inspection.py.

Usage:
  from praxis.backend.utils.plr_static_analysis import PLRSourceParser, find_plr_source_root

  parser = PLRSourceParser(find_plr_source_root())
  machines = parser.discover_machine_classes()
  resources = parser.discover_resource_classes()

"""

from praxis.backend.utils.plr_static_analysis.models import (
  FRONTEND_TO_BACKEND_MAP,
  MACHINE_BACKEND_TYPES,
  MACHINE_FRONTEND_TYPES,
  CapabilityMatchResult,
  CapabilityRequirement,
  DiscoveredBackend,
  DiscoveredCapabilities,
  DiscoveredClass,
  PLRClassType,
  ProtocolRequirements,
)
from praxis.backend.utils.plr_static_analysis.parser import (
  PLRSourceParser,
  find_plr_source_root,
)

__all__ = [
  "PLRSourceParser",
  "find_plr_source_root",
  "DiscoveredClass",
  "DiscoveredBackend",
  "DiscoveredCapabilities",
  "PLRClassType",
  "MACHINE_FRONTEND_TYPES",
  "MACHINE_BACKEND_TYPES",
  "FRONTEND_TO_BACKEND_MAP",
  "CapabilityRequirement",
  "ProtocolRequirements",
  "CapabilityMatchResult",
]
