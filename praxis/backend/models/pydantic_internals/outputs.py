"""Compatibility shim: re-export domain outputs as pydantic internals.

Some tests and import sites expect `praxis.backend.models.pydantic_internals.outputs`.
This module re-exports the domain models to preserve the import surface.
"""
from praxis.backend.models.domain.outputs import (
  DataExportRequest,
  FunctionDataOutputBase,
  FunctionDataOutputCreate,
  FunctionDataOutputFilters,
  FunctionDataOutputRead,
  FunctionDataOutputUpdate,
  PlateDataVisualization,
  ProtocolRunDataSummary,
  WellDataOutputBase,
  WellDataOutputCreate,
  WellDataOutputFilters,
  WellDataOutputRead,
  WellDataOutputUpdate,
)

__all__ = [
  "DataExportRequest",
  "FunctionDataOutputBase",
  "FunctionDataOutputCreate",
  "FunctionDataOutputFilters",
  "FunctionDataOutputRead",
  "FunctionDataOutputUpdate",
  "PlateDataVisualization",
  "ProtocolRunDataSummary",
  "WellDataOutputBase",
  "WellDataOutputCreate",
  "WellDataOutputFilters",
  "WellDataOutputRead",
  "WellDataOutputUpdate",
]
