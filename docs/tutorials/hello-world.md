# Tutorial: Hello World Protocol

This tutorial will guide you through writing an advanced Praxis protocol. We will create a "Hello World" protocol that uses a liquid handler to "print" the letters **H E L L O W O R L D** onto ten separate plates using liquid transfers.

## Prerequisites

- Praxis installed and running.
- A liquid handler with 8 channels.
- 1 Tip Rack.
- 1 Trough (Source of liquid).
- 10 Plates (Destination "canvas").

## The Objective

We want to spell "HELLO WORLD" by transferring liquid from a trough to 10 destination plates. Each plate will represent one letter. We will use the 8-channel head to "paint" columns of the letter by selectively dispensing liquid into specific wells (rows A-H) of each column.

## Bitmasking Logic

Since we are using an 8-channel head, we process the plate column by column. For each column, we define a "mask" of 8 bits (0 or 1) representing the 8 rows (A-H).

- `1` (or `True`): Dispense liquid (Pixel ON).
- `0` (or `False`): Do not dispense (Pixel OFF).

## Step 1: Define the Protocol

Create a new Python file named `hello_world.py`.

```python
from praxis.backend.core.protocol_engine import protocol
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.resources import Plate, TipRack

# --- Pixel Art Definitions (8 rows x 5 columns) ---
# 1 = Fill, 0 = Empty
LETTERS = {
    'H': [
        [1,1,1,1,1,1,1,1], # Col 1
        [0,0,0,1,1,0,0,0], # Col 2
        [0,0,0,1,1,0,0,0], # Col 3
        [0,0,0,1,1,0,0,0], # Col 4
        [1,1,1,1,1,1,1,1], # Col 5
    ],
    'E': [
        [1,1,1,1,1,1,1,1],
        [1,0,0,1,1,0,0,1],
        [1,0,0,1,1,0,0,1],
        [1,0,0,1,1,0,0,1],
        [1,0,0,0,0,0,0,1],
    ],
    'L': [
        [1,1,1,1,1,1,1,1],
        [0,0,0,0,0,0,0,1],
        [0,0,0,0,0,0,0,1],
        [0,0,0,0,0,0,0,1],
        [0,0,0,0,0,0,0,1],
    ],
    'O': [
        [0,1,1,1,1,1,1,0],
        [1,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,1],
        [0,1,1,1,1,1,1,0],
    ],
    'W': [
        [1,1,1,1,1,1,0,0],
        [0,0,0,0,0,0,1,0],
        [0,0,0,0,0,0,0,1],
        [0,0,0,0,0,0,1,0],
        [1,1,1,1,1,1,0,0],
    ],
    'R': [
        [1,1,1,1,1,1,1,1],
        [1,0,0,1,0,0,0,0],
        [1,0,0,1,1,0,0,0],
        [1,0,0,0,1,1,0,0],
        [0,1,1,0,0,0,1,1],
    ],
    'D': [
        [1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,1],
        [0,1,0,0,0,0,1,0],
        [0,0,1,1,1,1,0,0],
    ]
}

@protocol(
    name="Hello World Printer",
    description="Spells HELLO WORLD on 10 plates using liquid transfers"
)
async def hello_world(
    lh: LiquidHandler, 
    tips: TipRack,
    trough: Plate, 
    h_plate: Plate,
    e_plate: Plate,
    l1_plate: Plate,
    l2_plate: Plate,
    o1_plate: Plate,
    w_plate: Plate,
    o2_plate: Plate,
    r_plate: Plate,
    l3_plate: Plate,
    d_plate: Plate,
):
    """
    Spells HELLO WORLD by transferring liquid from a trough to 10 plates.
    """
    
    TEXT = "HELLOWORLD"
    
    # Collect plates for iteration
    plates = [
        h_plate, e_plate, l1_plate, l2_plate, o1_plate,
        w_plate, o2_plate, r_plate, l3_plate, d_plate
    ]

    # Pick up tips once for the entire job (since we assume same liquid/dye)
    # Using an 8-channel range for the multichannel head
    await lh.pick_up_tips(tips["A1:H1"]) 

    try:
        # Loop through each character to print
        for letter_char, plate in zip(TEXT, plates):
            print(f"Printing '{letter_char}' on {plate.name}...")
            
            pattern = LETTERS[letter_char]
            start_col = 4 # Center character on plate
            
            for col_idx, col_pattern in enumerate(pattern):
                # Calculate volumes: 50uL for pixels, 0 for empty space
                vols = [50.0 if bit else 0.0 for bit in col_pattern]
                
                if sum(vols) == 0:
                    continue

                # Define source: Rows A-H of the trough's first column
                source_column = trough["A1":"H1"]
                
                # Define target: Rows A-H of the specific column on the plate
                target_col_num = start_col + col_idx
                target_column = plate[f"A{target_col_num}:H{target_col_num}"]
                
                # Perform the transfer using the 8-channel head
                # Since we picked up tips manually, this will use the currently attached tips
                await lh.transfer(source_column, target_column, vols=vols)

    finally:
        await lh.return_tips()
```

## Step 2: Understanding the Code

1. **Arguments**:
    - `tips: TipRack`: We explicitly request a tip rack to use.
    - `trough: Plate`: The source of our "ink".
    - `h_plate`...`d_plate`: The 10 destination plates.

2. **The Loop**:
    - We iterate through each column of the letter's design.
    - We define `vols` as a list of 8 floats, matching the 8 rows (A-H).
    - `lh.transfer` is called with:
        - `source_column`: The 8 wells of the trough (A1-H1).
        - `target_column`: The 8 wells of the current destination column.
        - `vols`: The calculated volume mask.

## Step 3: Running in Praxis

1. **Upload**: Save and upload `hello_world.py`.
2. **Setup**:
    - Add a **Tip Rack** (e.g., `TipRack_1000uL_FIT`) to the deck.
    - Add a **Trough** (e.g., `Porvair_Reservoir`) to the deck.
    - Add **10 Plates** (e.g., `Cor_96_well_plate`) to the deck.
3. **Run Protocol**:
    - Assign all resources in the wizard steps.
    - **Automatic Guidance**: Praxis will automatically guide you through placing the tip plate carrier, trough carrier, and the individual resources (tip rack, plates, and trough) onto the deck as part of the guided setup flow.
4. **Execute**: The robot will pick up tips once, then move plate by plate, column by column, transferring liquid to spell the message.
