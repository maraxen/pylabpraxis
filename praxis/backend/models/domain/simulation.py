"""Pydantic models for protocol simulation and execution state history."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class TipStateSnapshot(BaseModel):
  """Snapshot of tip state."""

  tips_loaded: bool = False
  tips_count: int = 0
  tip_usage: Optional[dict[str, int]] = None


class StateSnapshot(BaseModel):
  """Complete state snapshot at a point in time."""

  tips: TipStateSnapshot = Field(default_factory=TipStateSnapshot)
  liquids: dict[str, dict[str, float]] = Field(default_factory=dict)
  on_deck: list[str] = Field(default_factory=list)
  # Allow for full raw PLR state if needed
  raw_plr_state: Optional[dict[str, Any]] = None


class OperationStateSnapshot(BaseModel):
  """State snapshot at a specific operation during execution."""

  operation_index: int
  operation_id: str
  method_name: str
  resource: Optional[str] = None
  args: Optional[dict[str, Any]] = None
  state_before: Optional[StateSnapshot] = None
  state_after: Optional[StateSnapshot] = None
  timestamp: Optional[str] = None
  duration_ms: Optional[float] = None
  status: str = "completed"  # 'completed' | 'failed' | 'skipped'
  error_message: Optional[str] = None
  state_delta: Optional[dict[str, Any]] = None


class StateHistory(BaseModel):
  """Complete state history for a protocol run."""

  run_id: str
  protocol_name: Optional[str] = None
  operations: list[OperationStateSnapshot] = Field(default_factory=list)
  final_state: Optional[StateSnapshot] = None
  total_duration_ms: Optional[float] = None
