"""Capability extraction visitor for PLR static analysis."""

from typing import Any

import libcst as cst

from praxis.backend.utils.plr_static_analysis.capability_config_templates import (
  get_config_template,
)
from praxis.backend.utils.plr_static_analysis.models import (
  CentrifugeCapabilities,
  DiscoveredCapabilities,
  FanCapabilities,
  GenericMachineCapabilities,
  HeaterShakerCapabilities,
  IncubatorCapabilities,
  LiquidHandlerCapabilities,
  MachineCapabilities,
  MachineCapabilityConfigSchema,
  PeelerCapabilities,
  PlateReaderCapabilities,
  PLRClassType,
  PowderDispenserCapabilities,
  PumpCapabilities,
  ScaraCapabilities,
  SealerCapabilities,
  ShakerCapabilities,
  TemperatureControllerCapabilities,
  ThermocyclerCapabilities,
)


class CapabilityExtractorVisitor(cst.CSTVisitor):
  """Extracts capabilities from a PLR class definition."""

  def __init__(self, class_type: PLRClassType | None = None) -> None:
    """Initialize the capability extractor.

    Args:
      class_type: The type of machine class being analyzed. Used to determine
        which type-specific capability schema to populate.

    """
    self.class_type = class_type
    self.capabilities = DiscoveredCapabilities()
    self.num_channels_default: int | None = None
    self.has_num_channels_property: bool = False
    self.has_abstract_methods: bool = False
    self._in_init = False
    self._found_modules: set[str] = set()
    # Type-specific capability signals
    self._signals: dict[str, Any] = {}

  def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:  # noqa: N802
    """Visit function definitions to extract capabilities.

    Args:
      node: The function definition node.

    Returns:
      True to continue visiting the function body.

    """
    func_name = node.name.value

    # Check for abstract methods
    for decorator in node.decorators:
      dec_name = self._get_decorator_name(decorator)
      if dec_name in ("abstractmethod", "abc.abstractmethod"):
        self.has_abstract_methods = True

      # Check for num_channels property
      if func_name == "num_channels" and dec_name == "property":
        self.has_num_channels_property = True

    # Detect __init__ for constructor defaults
    if func_name == "__init__":
      self._in_init = True
      self._extract_init_defaults(node)

    # Detect module presence via method naming patterns
    self._detect_capabilities_from_method_name(func_name)

    return True

  def leave_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
    """Leave function definition.

    Args:
      node: The function definition node.

    """
    if node.name.value == "__init__":
      self._in_init = False

  def visit_Assign(self, node: cst.Assign) -> bool:  # noqa: N802
    """Detect instance attribute assignments for capability detection.

    Args:
      node: The assignment node.

    Returns:
      True to continue visiting.

    """
    if self._in_init:
      for target in node.targets:
        if isinstance(target.target, cst.Attribute):
          attr = target.target
          if isinstance(attr.value, cst.Name) and attr.value.value == "self":
            attr_name = attr.attr.value
            attr_value = self._extract_literal_value(node.value)
            self._detect_capability_from_attribute(attr_name, attr_value)
    return True

  def visit_AnnAssign(self, node: cst.AnnAssign) -> bool:  # noqa: N802
    """Detect annotated assignments for capability detection.

    Args:
      node: The annotated assignment node.

    Returns:
      True to continue visiting.

    """
    if self._in_init and isinstance(node.target, cst.Attribute):
      attr = node.target
      if isinstance(attr.value, cst.Name) and attr.value.value == "self":
        attr_name = attr.attr.value
        attr_value = self._extract_literal_value(node.value) if node.value else None
        self._detect_capability_from_attribute(attr_name, attr_value)
    return True

  def _extract_literal_value(self, node: cst.BaseExpression | None) -> Any:
    """Extract a literal value from a CST expression.

    Args:
      node: The expression node.

    Returns:
      The Python value, or None if not a literal.

    """
    if node is None:
      return None
    if isinstance(node, cst.Integer):
      # Use base=0 to auto-detect hex (0x), octal (0o), binary (0b) prefixes
      return int(node.value, 0)
    if isinstance(node, cst.Float):
      return float(node.value)
    if isinstance(node, (cst.SimpleString, cst.FormattedString, cst.ConcatenatedString)):
      # Extract string value (simplified)
      try:
        return eval(node.evaluated_value) if hasattr(node, "evaluated_value") else None
      except Exception:
        return None
    if isinstance(node, cst.Name):
      if node.value == "True":
        return True
      if node.value == "False":
        return False
      if node.value == "None":
        return None
    if isinstance(node, cst.UnaryOperation) and isinstance(node.operator, cst.Minus):
      inner = self._extract_literal_value(node.expression)
      if inner is not None:
        return -inner
    return None

  def _get_decorator_name(self, decorator: cst.Decorator) -> str | None:
    """Get the name of a decorator.

    Args:
      decorator: The decorator node.

    Returns:
      The decorator name as a string.

    """
    if isinstance(decorator.decorator, cst.Name):
      return decorator.decorator.value
    if isinstance(decorator.decorator, cst.Attribute):
      return self._attribute_to_string(decorator.decorator)
    if isinstance(decorator.decorator, cst.Call):
      if isinstance(decorator.decorator.func, cst.Name):
        return decorator.decorator.func.value
      if isinstance(decorator.decorator.func, cst.Attribute):
        return self._attribute_to_string(decorator.decorator.func)
    return None

  def _attribute_to_string(self, node: cst.Attribute) -> str:
    """Convert an Attribute node to a dotted string.

    Args:
      node: An Attribute node.

    Returns:
      The dotted string representation.

    """
    parts = []
    current: cst.BaseExpression = node
    while isinstance(current, cst.Attribute):
      parts.append(current.attr.value)
      current = current.value
    if isinstance(current, cst.Name):
      parts.append(current.value)
    return ".".join(reversed(parts))

  def _extract_init_defaults(self, node: cst.FunctionDef) -> None:
    """Extract default values from __init__ parameters.

    Args:
      node: The __init__ function definition node.

    """
    all_params = list(node.params.params) + list(node.params.kwonly_params)

    for param in all_params:
      param_name = param.name.value
      param_value = self._extract_literal_value(param.default) if param.default else None

      # Channel count extraction
      if param_name == "num_channels" and param_value is not None:
        self.num_channels_default = int(param_value)

      # Type-specific parameter extraction
      self._extract_typed_param(param_name, param_value)

  def _extract_typed_param(self, param_name: str, param_value: Any) -> None:
    """Extract type-specific parameters from __init__ defaults.

    Args:
      param_name: The parameter name.
      param_value: The default value (if any).

    """
    name_lower = param_name.lower()

    # Temperature-related
    if "max_temp" in name_lower or param_name == "max_temperature_c":
      self._signals["max_temperature_c"] = param_value
    elif "min_temp" in name_lower or param_name == "min_temperature_c":
      self._signals["min_temperature_c"] = param_value

    # Speed-related (rpm)
    elif "max_speed" in name_lower or "max_rpm" in name_lower:
      self._signals["max_speed_rpm"] = param_value

    # Flow rate
    elif "max_flow" in name_lower:
      self._signals["max_flow_rate_ml_min"] = param_value
    elif "min_flow" in name_lower:
      self._signals["min_flow_rate_ml_min"] = param_value

    # Centrifuge
    elif param_name == "max_g" or "max_rcf" in name_lower:
      self._signals["max_g"] = param_value

  def _detect_capabilities_from_method_name(self, func_name: str) -> None:
    """Detect capabilities from method names.

    Args:
      func_name: The function name.

    """
    func_lower = func_name.lower()

    # === Liquid Handler specific ===
    if func_name.startswith("iswap_") or func_name == "park_iswap":
      self._found_modules.add("swap")
      self.capabilities.has_iswap = True

    if "core96" in func_lower or "core_96" in func_lower:
      self.capabilities.has_core96 = True
      if 96 not in self.capabilities.channels:
        self.capabilities.channels.append(96)

    if "384" in func_name and 384 not in self.capabilities.channels:
      self.capabilities.channels.append(384)

    if (
      "pick_up_tips96" in func_lower or "drop_tips96" in func_lower
    ) and 96 not in self.capabilities.channels:
      self.capabilities.channels.append(96)

    if (
      "pick_up_tips384" in func_lower or "drop_tips384" in func_lower
    ) and 384 not in self.capabilities.channels:
      self.capabilities.channels.append(384)

    if "hepa" in func_lower:
      self._found_modules.add("hepa")

    # === Plate Reader specific ===
    if "absorbance" in func_lower or "read_abs" in func_lower:
      self._signals["absorbance"] = True
    if "fluorescence" in func_lower or "read_fl" in func_lower:
      self._signals["fluorescence"] = True
    if "luminescence" in func_lower or "read_lum" in func_lower:
      self._signals["luminescence"] = True
    if "imaging" in func_lower or "capture_image" in func_lower:
      self._signals["imaging"] = True

    # === HeaterShaker / TemperatureController ===
    if func_name == "cool" or "set_cooling" in func_lower:
      self._signals["has_cooling"] = True

    # === Pump ===
    if "reverse" in func_lower or "backward" in func_lower:
      self._signals["reversible"] = True

    # === Incubator ===
    if "set_co2" in func_lower or "co2_control" in func_lower:
      self._signals["has_co2_control"] = True
    if "set_humidity" in func_lower or "humidity_control" in func_lower:
      self._signals["has_humidity_control"] = True

    # === Thermocycler ===
    if "lid_temp" in func_lower or "heated_lid" in func_lower:
      self._signals["lid_heated"] = True

    # === Fan ===
    if "set_speed" in func_lower or "variable_speed" in func_lower:
      self._signals["variable_speed"] = True

  def _detect_capability_from_attribute(self, attr_name: str, attr_value: Any = None) -> None:
    """Detect capabilities from instance attributes.

    Args:
      attr_name: The attribute name.
      attr_value: The attribute value (if available).

    """
    attr_lower = attr_name.lower()

    # === Liquid Handler ===
    if attr_name == "iswap_installed" or "iswap" in attr_lower:
      self._found_modules.add("swap")
      self.capabilities.has_iswap = True

    if attr_name == "core96_head_installed" or "core96" in attr_lower or "core_96" in attr_lower:
      self.capabilities.has_core96 = True
      if 96 not in self.capabilities.channels:
        self.capabilities.channels.append(96)

    if "hepa" in attr_lower:
      self._found_modules.add("hepa")

    # === Temperature attributes ===
    if "max_temp" in attr_lower and attr_value is not None:
      self._signals["max_temperature_c"] = attr_value
    if "min_temp" in attr_lower and attr_value is not None:
      self._signals["min_temperature_c"] = attr_value

    # === Speed attributes ===
    if ("max_speed" in attr_lower or "max_rpm" in attr_lower) and attr_value is not None:
      self._signals["max_speed_rpm"] = attr_value

    # === Centrifuge ===
    if attr_name == "temperature_controlled" and attr_value is True:
      self._signals["temperature_controlled"] = True

    # === Itemized Resource dimensions (plates, tip racks, etc.) ===
    if attr_name == "num_items_x" and attr_value is not None:
      self.capabilities.num_items_x = int(attr_value)
    if attr_name == "num_items_y" and attr_value is not None:
      self.capabilities.num_items_y = int(attr_value)

  def finalize(self) -> DiscoveredCapabilities:
    """Finalize and return the discovered capabilities.

    Returns:
      The discovered capabilities.

    """
    # Add modules from detected patterns
    self.capabilities.modules = list(self._found_modules)

    # If we found num_channels default, add it
    if (
      self.num_channels_default is not None
      and self.num_channels_default not in self.capabilities.channels
    ):
      self.capabilities.channels.append(self.num_channels_default)

    return self.capabilities

  def build_machine_capabilities(self) -> MachineCapabilities | None:
    """Build type-specific machine capabilities from detected signals.

    Returns:
      The appropriate MachineCapabilities subtype, or None for non-machine types.

    """
    if self.class_type is None:
      return None

    # Map class types to capability builders
    if self.class_type in (PLRClassType.LIQUID_HANDLER, PLRClassType.LH_BACKEND):
      return LiquidHandlerCapabilities(
        channels=self.capabilities.channels,
        has_iswap=self.capabilities.has_iswap,
        has_core96=self.capabilities.has_core96,
        has_hepa="hepa" in self._found_modules,
      )

    if self.class_type in (PLRClassType.PLATE_READER, PLRClassType.PR_BACKEND):
      return PlateReaderCapabilities(
        absorbance=self._signals.get("absorbance", False),
        fluorescence=self._signals.get("fluorescence", False),
        luminescence=self._signals.get("luminescence", False),
        imaging=self._signals.get("imaging", False),
      )

    if self.class_type in (PLRClassType.HEATER_SHAKER, PLRClassType.HS_BACKEND):
      return HeaterShakerCapabilities(
        max_temperature_c=self._signals.get("max_temperature_c"),
        min_temperature_c=self._signals.get("min_temperature_c"),
        max_speed_rpm=self._signals.get("max_speed_rpm"),
        has_cooling=self._signals.get("has_cooling", False),
      )

    if self.class_type in (PLRClassType.SHAKER, PLRClassType.SHAKER_BACKEND):
      return ShakerCapabilities(
        max_speed_rpm=self._signals.get("max_speed_rpm"),
      )

    if self.class_type in (
      PLRClassType.TEMPERATURE_CONTROLLER,
      PLRClassType.TEMP_BACKEND,
    ):
      return TemperatureControllerCapabilities(
        max_temperature_c=self._signals.get("max_temperature_c"),
        min_temperature_c=self._signals.get("min_temperature_c"),
        has_cooling=self._signals.get("has_cooling", False),
      )

    if self.class_type in (PLRClassType.CENTRIFUGE, PLRClassType.CENTRIFUGE_BACKEND):
      return CentrifugeCapabilities(
        max_rpm=self._signals.get("max_speed_rpm"),
        max_g=self._signals.get("max_g"),
        temperature_controlled=self._signals.get("temperature_controlled", False),
      )

    if self.class_type in (PLRClassType.THERMOCYCLER, PLRClassType.THERMOCYCLER_BACKEND):
      return ThermocyclerCapabilities(
        max_temperature_c=self._signals.get("max_temperature_c"),
        min_temperature_c=self._signals.get("min_temperature_c"),
        lid_heated=self._signals.get("lid_heated", False),
      )

    if self.class_type in (PLRClassType.PUMP, PLRClassType.PUMP_BACKEND):
      return PumpCapabilities(
        max_flow_rate_ml_min=self._signals.get("max_flow_rate_ml_min"),
        min_flow_rate_ml_min=self._signals.get("min_flow_rate_ml_min"),
        reversible=self._signals.get("reversible", False),
        num_channels=self.num_channels_default or 1,
      )

    if self.class_type in (PLRClassType.FAN, PLRClassType.FAN_BACKEND):
      return FanCapabilities(
        max_speed_rpm=self._signals.get("max_speed_rpm"),
        variable_speed=self._signals.get("variable_speed", False),
      )

    if self.class_type in (PLRClassType.SEALER, PLRClassType.SEALER_BACKEND):
      return SealerCapabilities(
        max_temperature_c=self._signals.get("max_temperature_c"),
      )

    if self.class_type in (PLRClassType.PEELER, PLRClassType.PEELER_BACKEND):
      return PeelerCapabilities()

    if self.class_type in (
      PLRClassType.POWDER_DISPENSER,
      PLRClassType.POWDER_DISPENSER_BACKEND,
    ):
      return PowderDispenserCapabilities()

    if self.class_type in (PLRClassType.INCUBATOR, PLRClassType.INCUBATOR_BACKEND):
      return IncubatorCapabilities(
        max_temperature_c=self._signals.get("max_temperature_c"),
        min_temperature_c=self._signals.get("min_temperature_c"),
        has_co2_control=self._signals.get("has_co2_control", False),
        has_humidity_control=self._signals.get("has_humidity_control", False),
      )

    if self.class_type in (PLRClassType.SCARA, PLRClassType.SCARA_BACKEND):
      return ScaraCapabilities()

    # Fallback for unknown machine types
    if self._signals:
      return GenericMachineCapabilities(raw_capabilities=self._signals)

    return None

  def build_capabilities_config(self) -> MachineCapabilityConfigSchema | None:
    """Generate config schema based on machine type and detected signals.

    This creates a user-configurable capability schema for dynamic form
    generation in the frontend. Templates are customized with detected
    capability signals pre-filled as defaults.

    Returns:
      The config schema with defaults pre-filled, or None for non-machine types.

    """
    if self.class_type is None:
      return None

    # Get the template for this machine type
    template = get_config_template(self.class_type)
    if template is None:
      return None

    # Pre-fill defaults based on what we detected in the source
    for field in template.config_fields:
      # Map detected signals to config field defaults
      if field.field_name in self._signals:
        field.default_value = self._signals[field.field_name]

      # Special handling for liquid handler capabilities
      if (
        (field.field_name == "has_iswap" and self.capabilities.has_iswap)
        or (field.field_name == "has_core96" and self.capabilities.has_core96)
        or (field.field_name == "has_hepa" and "hepa" in self._found_modules)
      ):
        field.default_value = True
      elif field.field_name == "num_channels" and self.capabilities.channels:
        # Use the primary channel count
        field.default_value = str(max(self.capabilities.channels))

    return template
