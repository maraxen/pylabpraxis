"""
Capability configuration templates for dynamic form generation.

Each machine type has a predefined schema that defines which capabilities
are user-configurable during machine setup. These templates are used to
generate dynamic forms in the frontend.
"""

from .models import CapabilityConfigField, MachineCapabilityConfigSchema, PLRClassType


# =============================================================================
# Liquid Handler Configuration
# =============================================================================

LIQUID_HANDLER_CONFIG = MachineCapabilityConfigSchema(
    machine_type="liquid_handler",
    config_fields=[
        CapabilityConfigField(
            field_name="num_channels",
            display_name="Number of Channels",
            field_type="select",
            default_value="8",
            options=["1", "4", "8", "12", "16"],
            help_text="Number of independent pipetting channels on the main head"
        ),
        CapabilityConfigField(
            field_name="has_iswap",
            display_name="iSWAP Plate Handler",
            field_type="boolean",
            default_value=False,
            help_text="Integrated plate transport arm for moving labware between deck positions"
        ),
        CapabilityConfigField(
            field_name="has_core96",
            display_name="CoRe 96 Head",
            field_type="boolean",
            default_value=False,
            help_text="96-channel head for parallel pipetting operations"
        ),
        CapabilityConfigField(
            field_name="has_hepa",
            display_name="HEPA Filter",
            field_type="boolean",
            default_value=False,
            help_text="Integrated HEPA filtration for sterile operations"
        ),
    ]
)


# =============================================================================
# Plate Reader Configuration
# =============================================================================

PLATE_READER_CONFIG = MachineCapabilityConfigSchema(
    machine_type="plate_reader",
    config_fields=[
        CapabilityConfigField(
            field_name="has_absorbance",
            display_name="Absorbance",
            field_type="boolean",
            default_value=True,
            help_text="Absorbance measurement capability (OD readings)"
        ),
        CapabilityConfigField(
            field_name="has_fluorescence",
            display_name="Fluorescence",
            field_type="boolean",
            default_value=False,
            help_text="Fluorescence intensity measurement capability"
        ),
        CapabilityConfigField(
            field_name="has_luminescence",
            display_name="Luminescence",
            field_type="boolean",
            default_value=False,
            help_text="Luminescence measurement capability"
        ),
        CapabilityConfigField(
            field_name="has_imaging",
            display_name="Imaging",
            field_type="boolean",
            default_value=False,
            help_text="Well imaging capability"
        ),
    ]
)


# =============================================================================
# Heater Shaker Configuration
# =============================================================================

HEATER_SHAKER_CONFIG = MachineCapabilityConfigSchema(
    machine_type="heater_shaker",
    config_fields=[
        CapabilityConfigField(
            field_name="max_temperature_c",
            display_name="Max Temperature (°C)",
            field_type="number",
            default_value=105,
            help_text="Maximum heating temperature in Celsius"
        ),
        CapabilityConfigField(
            field_name="max_speed_rpm",
            display_name="Max Speed (RPM)",
            field_type="number",
            default_value=2000,
            help_text="Maximum shaking speed in rotations per minute"
        ),
        CapabilityConfigField(
            field_name="has_cooling",
            display_name="Active Cooling",
            field_type="boolean",
            default_value=False,
            help_text="Active cooling capability below ambient temperature"
        ),
    ]
)


# =============================================================================
# Shaker Configuration (no heating)
# =============================================================================

SHAKER_CONFIG = MachineCapabilityConfigSchema(
    machine_type="shaker",
    config_fields=[
        CapabilityConfigField(
            field_name="max_speed_rpm",
            display_name="Max Speed (RPM)",
            field_type="number",
            default_value=1500,
            help_text="Maximum shaking speed in rotations per minute"
        ),
        CapabilityConfigField(
            field_name="orbit_diameter_mm",
            display_name="Orbit Diameter (mm)",
            field_type="number",
            default_value=3,
            help_text="Orbital shaking diameter in millimeters"
        ),
    ]
)


# =============================================================================
# Temperature Controller Configuration
# =============================================================================

TEMPERATURE_CONTROLLER_CONFIG = MachineCapabilityConfigSchema(
    machine_type="temperature_controller",
    config_fields=[
        CapabilityConfigField(
            field_name="max_temperature_c",
            display_name="Max Temperature (°C)",
            field_type="number",
            default_value=100,
            help_text="Maximum temperature in Celsius"
        ),
        CapabilityConfigField(
            field_name="min_temperature_c",
            display_name="Min Temperature (°C)",
            field_type="number",
            default_value=4,
            help_text="Minimum temperature in Celsius (if cooling available)"
        ),
        CapabilityConfigField(
            field_name="has_cooling",
            display_name="Active Cooling",
            field_type="boolean",
            default_value=False,
            help_text="Active cooling capability"
        ),
    ]
)


# =============================================================================
# Centrifuge Configuration
# =============================================================================

CENTRIFUGE_CONFIG = MachineCapabilityConfigSchema(
    machine_type="centrifuge",
    config_fields=[
        CapabilityConfigField(
            field_name="max_rpm",
            display_name="Max Speed (RPM)",
            field_type="number",
            default_value=4000,
            help_text="Maximum centrifugation speed"
        ),
        CapabilityConfigField(
            field_name="max_g",
            display_name="Max G-Force",
            field_type="number",
            default_value=3000,
            help_text="Maximum relative centrifugal force"
        ),
        CapabilityConfigField(
            field_name="temperature_controlled",
            display_name="Temperature Control",
            field_type="boolean",
            default_value=False,
            help_text="Temperature-controlled centrifugation"
        ),
    ]
)


# =============================================================================
# Thermocycler Configuration
# =============================================================================

THERMOCYCLER_CONFIG = MachineCapabilityConfigSchema(
    machine_type="thermocycler",
    config_fields=[
        CapabilityConfigField(
            field_name="max_temperature_c",
            display_name="Max Temperature (°C)",
            field_type="number",
            default_value=99,
            help_text="Maximum block temperature"
        ),
        CapabilityConfigField(
            field_name="ramp_rate_c_per_s",
            display_name="Ramp Rate (°C/s)",
            field_type="number",
            default_value=3,
            help_text="Temperature change rate"
        ),
        CapabilityConfigField(
            field_name="lid_heated",
            display_name="Heated Lid",
            field_type="boolean",
            default_value=True,
            help_text="Heated lid to prevent condensation"
        ),
    ]
)


# =============================================================================
# Pump Configuration
# =============================================================================

PUMP_CONFIG = MachineCapabilityConfigSchema(
    machine_type="pump",
    config_fields=[
        CapabilityConfigField(
            field_name="num_channels",
            display_name="Number of Channels",
            field_type="select",
            default_value="1",
            options=["1", "2", "4", "8"],
            help_text="Number of independent pump channels"
        ),
        CapabilityConfigField(
            field_name="reversible",
            display_name="Reversible Flow",
            field_type="boolean",
            default_value=False,
            help_text="Bi-directional pumping capability"
        ),
        CapabilityConfigField(
            field_name="max_flow_rate_ml_min",
            display_name="Max Flow Rate (mL/min)",
            field_type="number",
            default_value=50,
            help_text="Maximum flow rate"
        ),
    ]
)


# =============================================================================
# Incubator Configuration
# =============================================================================

INCUBATOR_CONFIG = MachineCapabilityConfigSchema(
    machine_type="incubator",
    config_fields=[
        CapabilityConfigField(
            field_name="max_temperature_c",
            display_name="Max Temperature (°C)",
            field_type="number",
            default_value=50,
            help_text="Maximum incubation temperature"
        ),
        CapabilityConfigField(
            field_name="has_co2_control",
            display_name="CO2 Control",
            field_type="boolean",
            default_value=False,
            help_text="CO2 atmosphere control for cell culture"
        ),
        CapabilityConfigField(
            field_name="has_humidity_control",
            display_name="Humidity Control",
            field_type="boolean",
            default_value=False,
            help_text="Humidity control for cell culture"
        ),
    ]
)


# =============================================================================
# Sealer Configuration
# =============================================================================

SEALER_CONFIG = MachineCapabilityConfigSchema(
    machine_type="sealer",
    config_fields=[
        CapabilityConfigField(
            field_name="max_temperature_c",
            display_name="Seal Temperature (°C)",
            field_type="number",
            default_value=175,
            help_text="Heat sealing temperature"
        ),
        CapabilityConfigField(
            field_name="seal_time_s",
            display_name="Seal Time (s)",
            field_type="number",
            default_value=2,
            help_text="Duration of heat application"
        ),
    ]
)


# =============================================================================
# Fan Configuration
# =============================================================================

FAN_CONFIG = MachineCapabilityConfigSchema(
    machine_type="fan",
    config_fields=[
        CapabilityConfigField(
            field_name="variable_speed",
            display_name="Variable Speed",
            field_type="boolean",
            default_value=False,
            help_text="Variable speed control (vs on/off only)"
        ),
        CapabilityConfigField(
            field_name="max_speed_rpm",
            display_name="Max Speed (RPM)",
            field_type="number",
            default_value=3000,
            help_text="Maximum fan speed",
            depends_on="variable_speed"
        ),
    ]
)


# =============================================================================
# Template Registry
# =============================================================================

# Map PLRClassType to config templates
CAPABILITY_CONFIG_TEMPLATES: dict[PLRClassType, MachineCapabilityConfigSchema] = {
    PLRClassType.LIQUID_HANDLER: LIQUID_HANDLER_CONFIG,
    PLRClassType.PLATE_READER: PLATE_READER_CONFIG,
    PLRClassType.HEATER_SHAKER: HEATER_SHAKER_CONFIG,
    PLRClassType.SHAKER: SHAKER_CONFIG,
    PLRClassType.TEMPERATURE_CONTROLLER: TEMPERATURE_CONTROLLER_CONFIG,
    PLRClassType.CENTRIFUGE: CENTRIFUGE_CONFIG,
    PLRClassType.THERMOCYCLER: THERMOCYCLER_CONFIG,
    PLRClassType.PUMP: PUMP_CONFIG,
    PLRClassType.INCUBATOR: INCUBATOR_CONFIG,
    PLRClassType.SEALER: SEALER_CONFIG,
    PLRClassType.FAN: FAN_CONFIG,
}

# Also map backend types to their frontend counterparts
BACKEND_TO_FRONTEND_CONFIG: dict[PLRClassType, PLRClassType] = {
    PLRClassType.LH_BACKEND: PLRClassType.LIQUID_HANDLER,
    PLRClassType.PR_BACKEND: PLRClassType.PLATE_READER,
    PLRClassType.HS_BACKEND: PLRClassType.HEATER_SHAKER,
    PLRClassType.SHAKER_BACKEND: PLRClassType.SHAKER,
    PLRClassType.TEMP_BACKEND: PLRClassType.TEMPERATURE_CONTROLLER,
    PLRClassType.CENTRIFUGE_BACKEND: PLRClassType.CENTRIFUGE,
    PLRClassType.THERMOCYCLER_BACKEND: PLRClassType.THERMOCYCLER,
    PLRClassType.PUMP_BACKEND: PLRClassType.PUMP,
    PLRClassType.INCUBATOR_BACKEND: PLRClassType.INCUBATOR,
    PLRClassType.SEALER_BACKEND: PLRClassType.SEALER,
    PLRClassType.FAN_BACKEND: PLRClassType.FAN,
}


def get_config_template(class_type: PLRClassType) -> MachineCapabilityConfigSchema | None:
    """
    Get the capability config template for a given class type.

    Args:
        class_type: The PLR class type (frontend or backend)

    Returns:
        The config schema template, or None if no template exists
    """
    # Direct lookup for frontend types
    if class_type in CAPABILITY_CONFIG_TEMPLATES:
        return CAPABILITY_CONFIG_TEMPLATES[class_type].model_copy(deep=True)

    # Map backend types to their frontend counterpart
    frontend_type = BACKEND_TO_FRONTEND_CONFIG.get(class_type)
    if frontend_type and frontend_type in CAPABILITY_CONFIG_TEMPLATES:
        return CAPABILITY_CONFIG_TEMPLATES[frontend_type].model_copy(deep=True)

    return None
