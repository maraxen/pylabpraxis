"""Enumerated types for various model attributes."""

from .asset import AssetReservationStatusEnum, AssetType
from .machine import MachineCategoryEnum, MachineStatusEnum
from .outputs import DataOutputTypeEnum, SpatialContextEnum
from .plr_category import PLRCategory, get_category_from_class, infer_category_from_name
from .protocol import FunctionCallStatusEnum, ProtocolRunStatusEnum, ProtocolSourceStatusEnum
from .resource import ResourceCategoryEnum, ResourceStatusEnum
from .resolution import ResolutionActionEnum, ResolutionTypeEnum
from .schedule import ScheduleHistoryEventEnum, ScheduleHistoryEventTriggerEnum, ScheduleStatusEnum
from .workcell import WorkcellStatusEnum

__all__ = [
  "AssetReservationStatusEnum",
  "AssetType",
  "DataOutputTypeEnum",
  "FunctionCallStatusEnum",
  "MachineCategoryEnum",
  "MachineStatusEnum",
  "PLRCategory",
  "ProtocolRunStatusEnum",
  "ProtocolSourceStatusEnum",
  "ResourceCategoryEnum",
  "ResourceStatusEnum",
  "ScheduleHistoryEventEnum",
  "ScheduleHistoryEventTriggerEnum",
  "ScheduleStatusEnum",
  "SpatialContextEnum",
  "WorkcellStatusEnum",
  "get_category_from_class",
  "infer_category_from_name",
  "ResolutionActionEnum",
  "ResolutionTypeEnum",
]
