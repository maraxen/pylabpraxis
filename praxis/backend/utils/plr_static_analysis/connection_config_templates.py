"""Connection configuration templates for dynamic form generation.

These templates define the connection parameters (host, port, etc.) required
for different machine types. They are used to generate dynamic forms in the
frontend.
"""

from .models import CapabilityConfigField, MachineCapabilityConfigSchema, PLRClassType

# =============================================================================
# Opentrons OT-2 Configuration
# =============================================================================

OT2_CONNECTION_CONFIG = MachineCapabilityConfigSchema(
    machine_type="opentrons_ot2",
    config_fields=[
        CapabilityConfigField(
            field_name="host",
            display_name="IP Address",
            # Wait, field_type 'select' in `models` is strict.
            # I should check if 'text' is an allowed type in CapabilityConfigField.
            # The model says: Literal["boolean", "number", "select", "multiselect"]
            # It seems 'string' or 'text' is missing! I need to update the model first or use 'select' with custom input?
            # implementing this as 'select' for now would be wrong.
            # I will use "text" string here and update model next.
            field_type="text",
            default_value="169.254.122.1",
            help_text="IP address or hostname of the OT-2 robot",
            required=True
        ),
        CapabilityConfigField(
            field_name="port",
            display_name="Port",
            field_type="number",
            default_value=31950,
            help_text="Connection port (default: 31950)",
            required=True
        ),
    ],
)


# =============================================================================
# Hamilton STAR Configuration
# =============================================================================

STAR_CONNECTION_CONFIG = MachineCapabilityConfigSchema(
    machine_type="hamilton_star",
    config_fields=[
        CapabilityConfigField(
            field_name="device_address",
            display_name="Device Address / USB",
            field_type="text",
            default_value="0",
            help_text="USB device index or COM port",
            required=True
        ),
        CapabilityConfigField(
            field_name="simulation_mode",
            display_name="Simulation Mode",
            field_type="boolean",
            default_value=True,
            help_text="Run in offline simulation mode",
        ),
    ],
)

# =============================================================================
# Sealer Configuration
# =============================================================================

SEALER_CONNECTION_CONFIG = MachineCapabilityConfigSchema(
    machine_type="sealer",
    config_fields=[
        CapabilityConfigField(
            field_name="device_address",
            display_name="Serial Port",
            field_type="text",
            default_value="/dev/ttyUSB0",
            help_text="Serial port for current connection",
            required=True
        ),
    ],
)

# =============================================================================
# Generic / Default Configuration
# =============================================================================

GENERIC_CONNECTION_CONFIG = MachineCapabilityConfigSchema(
    machine_type="generic",
    config_fields=[
        CapabilityConfigField(
            field_name="host",
            display_name="Host / IP",
            field_type="text",
            default_value="127.0.0.1",
            help_text="Network address",
        ),
        CapabilityConfigField(
            field_name="port",
            display_name="Port",
            field_type="number",
            default_value=None,
            help_text="Connection port",
        ),
        CapabilityConfigField(
            field_name="backend_config",
            display_name="Backend Config",
            field_type="text",
            default_value='{"is_simulated": true}',
            help_text="Additional JSON configuration",
        ),
    ],
)

# =============================================================================
# Template Registry
# =============================================================================

def get_connection_config_template(class_type: PLRClassType, manufacturer: str | None = None) -> MachineCapabilityConfigSchema | None:
    """Get the connection config template for a given class type and manufacturer.
    
    Args:
        class_type: The PLR class type.
        manufacturer: The manufacturer name (optional, for specific matching).
        
    Returns:
        The config schema template.

    """
    # Specific Manufacturer Matching
    if manufacturer:
        m_lower = manufacturer.lower()
        if "opentrons" in m_lower and class_type == PLRClassType.LIQUID_HANDLER:
            return OT2_CONNECTION_CONFIG.model_copy(deep=True)
        if "hamilton" in m_lower and class_type == PLRClassType.LIQUID_HANDLER:
            return STAR_CONNECTION_CONFIG.model_copy(deep=True)

    # Type-based Fallbacks
    if class_type == PLRClassType.SEALER:
         return SEALER_CONNECTION_CONFIG.model_copy(deep=True)

    # Default for generic backends if nothing else matches
    if class_type in (PLRClassType.LIQUID_HANDLER, PLRClassType.PLATE_READER):
        return GENERIC_CONNECTION_CONFIG.model_copy(deep=True)

    return None
