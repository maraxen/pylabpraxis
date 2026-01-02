"""Serial Dilution Protocol.

A demo protocol that performs serial dilution across a plate row.
Demonstrates iterative well-to-well transfers with dilution factor.
"""

from typing import Any

from pylabrobot.resources import Plate, TipRack, Trough

from praxis.backend.core.decorators import protocol_function


@protocol_function(
    name="serial_dilution",
    version="1.0.0",
    description="Perform serial dilution across a plate row",
    category="liquid_handling",
    tags=["demo", "dilution", "assay"],
    is_top_level=True,
    param_metadata={
        "plate": {
            "description": "Plate for serial dilution",
            "plr_type": "Plate",
        },
        "tip_rack": {
            "description": "Tip rack for liquid handling",
            "plr_type": "TipRack",
        },
        "diluent_trough": {
            "description": "Trough containing diluent",
            "plr_type": "Trough",
        },
        "start_row": {
            "description": "Starting row letter (A-H)",
        },
        "num_dilutions": {
            "description": "Number of dilution steps",
        },
        "sample_volume_ul": {
            "description": "Volume of sample to transfer between wells",
        },
        "diluent_volume_ul": {
            "description": "Volume of diluent to add to each well",
        },
        "dilution_factor": {
            "description": "Dilution factor per step (e.g., 2 for 1:2 dilution)",
        },
    },
)
async def serial_dilution(
    state: dict[str, Any],
    plate: Plate,
    tip_rack: TipRack,
    diluent_trough: Trough,
    start_row: str = "A",
    num_dilutions: int = 8,
    sample_volume_ul: float = 100.0,
    diluent_volume_ul: float = 100.0,
    dilution_factor: float = 2.0,
) -> dict[str, Any]:
    """Perform serial dilution across a plate row.

    This protocol:
    1. Adds diluent to all dilution wells
    2. Transfers sample from column 1 to column 2
    3. Mixes and transfers to subsequent columns
    4. Discards final transfer volume

    Args:
        state: Protocol state dictionary
        plate: Plate for the serial dilution
        tip_rack: Tip rack for transfers
        diluent_trough: Trough with diluent
        start_row: Starting row (e.g., 'A')
        num_dilutions: Number of dilution steps
        sample_volume_ul: Volume transferred between wells
        diluent_volume_ul: Volume of diluent per well
        dilution_factor: Dilution factor per step

    Returns:
        Updated state with dilution series data

    """
    row = start_row.upper()
    if len(row) != 1 or row not in "ABCDEFGH":
        msg = f"Invalid row: {row}. Must be A-H."
        raise ValueError(msg)

    if num_dilutions < 1 or num_dilutions > 12:
        msg = f"num_dilutions must be 1-12, got {num_dilutions}"
        raise ValueError(msg)

    # Generate well positions for this row
    well_positions = [f"{row}{i}" for i in range(1, num_dilutions + 2)]

    # Record operations
    dilution_steps = []

    # Step 1: Add diluent to all dilution wells (columns 2 onwards)
    for well in well_positions[1:]:
        dilution_steps.append({
            "operation": "add_diluent",
            "well": well,
            "volume_ul": diluent_volume_ul,
            "source": diluent_trough.name,
        })

    # Step 2: Serial transfer from well to well
    concentrations = [1.0]  # Starting concentration (relative)
    for i in range(num_dilutions):
        src_well = well_positions[i]
        dst_well = well_positions[i + 1]

        dilution_steps.append({
            "operation": "transfer",
            "source_well": src_well,
            "dest_well": dst_well,
            "volume_ul": sample_volume_ul,
        })

        # Calculate concentration after dilution
        new_conc = concentrations[-1] / dilution_factor
        concentrations.append(new_conc)

    # Update state
    state["dilution_steps"] = dilution_steps
    state["well_positions"] = well_positions
    state["concentrations"] = concentrations
    state["dilution_factor"] = dilution_factor
    state["plate_name"] = plate.name
    state["status"] = "completed"

    return state
