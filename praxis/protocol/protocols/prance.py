# THIS WILL EVENTUALLY BE SEPARATED INTO A DIFFERENT REPO, placing here now for convenience
from os import PathLike
from asyncio import TaskGroup
from itertools import product
from abc import abstractmethod
from typing import TypeVar, Coroutine, Optional, Any
from praxis.protocol import Experiment
from praxis.commons.plate_staging import get_all_wells, split_wells_along_columns, well_to_int
from pylabrobot.plate_reading import PlateReader
from praxis.commons.commons import (
  NamedPumpArray, SampleReservoir, TipWasher, StabilizedWells, PumpManager)
from pylabrobot.liquid_handling import LiquidHandler, STAR
from pylabrobot.pumps import PumpArray
from pylabrobot.resources import Resource
from typing import cast
import warnings
import asyncio
import plotly.graph_objects as go
import plotly.express as px


from datetime import datetime as dt
from datetime import timedelta

from functools import partial

from pylabrobot.resources import (
  TipRack, TipSpot, Well, Container, Plate, ResourceStack, TipCarrier, PlateCarrier, Tip, Lid
)


needed_parameters = {"bacteria_ids": list,
                    "phage_ids": list,
                    "washer_volume": float,
                    "void_volume": float,
                    "inducer_volume": float,
                    "initial_inducer_volume": float,
                    "lagoon_volume": float,
                    "lagoon_flow_rate": float,
                    "sampling_interval": int,
                    "cycle_time": float,
                    "mixing": bool,
                    "mixing_volume": float,
                    "mixing_speed": float,
                    "mixing_cycles": int,
                    "liquid_handler": str,
                    "bacteria_pump": str,
                    "auxiliary_pump": str,
                    "pump_ids": dict,
                    "deck_layout": str,
                    "basin_refill_frequency": float,
                    "no_phage_control": int,
                    "phage_input_method": str,
                    "prefilled_basin": bool,
                    "num_plates_warning": int,
                    "tips_staged": bool,
                    "pumping_factor": float,
                    }

parameter_descriptions = {
    "bacteria_ids": "The ids of the bacteria strains to be used in the order of their pump index.",
    "phage_ids": "The ids of the phages to be used.",
    "washer_volume": "The volume of  or bleach to be used when filling tip washer (mL).",
    "void_volume": "The volume of air to be used when cleaning the sample station.",
    "inducer_volume": "The volume of inducer to be used.", #TODO: change to concentration
    "initial_inducer_volume": "The initial volume of inducer available per well.",
    "lagoon_volume": "The volume the lagoon will hold. Also sets the holding well volume.",
    "lagoon_flow_rate": "The rate at which to pipette in and out of the lagoon each cycle.",
    "sampling_interval": "The time between sampling events which are loaded to the plate reader.",
    "cycle_time": "The time between cycles.",
    "mixing": "Whether to mix the lagoon.",
    "mixing_volume": "The volume to mix.",
    "mixing_speed": "The speed of mixing.",
    "mixing_cycles": "The number of mixing cycles.",
    "bacteria_pump": "The name of the pump to use for bacteria.",
    "bacteria_index": "The index of the pump to use for bacteria.",
    "auxiliary_pump": "The name of the pump to use for water, bleach, and air.",
    "liquid_handler": "The name of the liquid handler to use.",
    "deck_layout": "Path to the deck layout to use.",
    "basin_refill_frequency": "The frequency at which to refill the tip washing basins. (hours)",
    "no_phage_control": "The number of phage control wells to use.",
    "phage_input_method": "The method to input phage. Options are 'manual' or 'automatic'.",
    "prefilled_basin": "Whether the tip washing basins are prefilled.",
    "num_plates_warning": "The number of plates to stack before warning the user.",
    "tips_staged": "Whether the tips are staged.",
    "pumping_factor": "The factor to multiply pumping volume by to ensure enough volume is pumped.",
    "other_variables": "Other variables to be used in the experiment."
  }

needed_deck_resources = {"sample_reservoir": SampleReservoir,
                          "inducer_tips": TipRack,
                          "inducer_reservoir": Plate,
                          "holding_tips": TipRack,
                          "induced_tips": TipRack,
                          "lagoon_tips_1": TipRack,
                          "lagoon_tips_2": TipRack,
                          "tip_washer": TipWasher,
                          "tip_carrier_1": TipCarrier,
                          "prance_plate_carrier": PlateCarrier,
                          "inducer_stack": StabilizedWells,
                          "inducer_reservoir": Plate,
                          "holding_plate": Plate,
                          "holding_stack": StabilizedWells,
                          "induced_stack": StabilizedWells,
                          "induced_plate": Plate,
                          "lagoon_stack": StabilizedWells,
                          "lagoon_plate": Plate,
                          "finished_plate_stack": ResourceStack,
                          "to_read_plate_stack": ResourceStack,
                          "reader_plate_stack_1": ResourceStack,
                          "reader_plate_stack_2": ResourceStack,
                          "reader_plate_stack_3": ResourceStack,
                          "reader_plate_carrier": PlateCarrier,
                          "bacteria_pump": NamedPumpArray,
                          "auxiliary_pump": NamedPumpArray,
                          "plate_reader": PlateReader
                          }

reminders = ["Is the robot pre-heated to 37 degrees Celsius?",
              "Is the initial tip washing basin parameter set correctly?",
              "Are the bacteria pumps set up correctly? Ensure that the pump index matches the " + \
                "order of the bacteria ids specified in the experiment configuration file.",
              "Is the water and bleach sources full and connected to the correct pumps?",
              "Are the tips staged?",
              "Are the reader plates in stacks of 5?",
              "Are the plates taped to the carrier?"
              ]

class Prance(Experiment):
  """Prance is a subclass of Experiment. It is a complex experiment that
  requires a lot of setup and teardown. It is a subclass of Experiment and
  uses the liquid handler to move liquids around, pumps to pump bacteria, water, and bleach onto the
  robot and more.
  """

  def __init__(self,
                experiment_configuration: PathLike,
                lab_configuration: PathLike,
                needed_parameters: dict[str, type],
                needed_deck_resources: dict[str, type],
                check_list: list[str]):
    super().__init__(experiment_configuration=experiment_configuration,
                      lab_configuration=lab_configuration,
                      needed_parameters=needed_parameters,
                      needed_deck_resources=needed_deck_resources,
                      check_list=check_list)

    if not self.parameters["tips_staged"]:
      raise ValueError("Tips are not staged. Run tip_staging.py with PRANCE specified.")
    self._available_commands["add_phage"] = "Add phage to the phage control wells."
    self.cycle_n = 0 if not self.already_ran else self["cycle_n"]
    self.cycle_start_time = dt.now() if not self.already_ran else self["cycle_start_time"]
    self.reader_plate_stack_in_use = self["to_read_plate_stack"] \
      if not self.already_ran else self["reader_plate_stack_in_use"]
    self.variable_combinations = list(product(self.parameters["bacteria_ids"],
                                          self.parameters["phage_ids"]))

    if len(self.variable_combinations) + \
      (self.parameters["no_phage_control"] * len(self.parameters["bacteria_ids"])) > 48:
        raise ValueError("Too many variable combinations. A maximum of 48 are supported.")

    if not self.already_ran:
      self.generate_optimal_layout()

  def generate_optimal_layout(self, n_rows: int = 8, n_columns: int = 12):
    """
    Generate the optimal layout for wells in the experiment.
    """
    if any(id in self["bacteria_ids"] for id in self["phage_ids"]):
      raise ValueError("Bacteria and phage IDs must be unique.")
    # Initialize dictionaries to store well assignments for each bacteria and phage.
    for bacteria_id in self["bacteria_ids"]:
      self[f"{bacteria_id}"] = []
    for phage_id in self["phage_ids"]:
      self[f"{phage_id}"] = []
    self["phage_control"] = []

    # Calculate the number of wells available for each bacteria.
    wells_per_bacteria = (n_rows * (n_columns / 2)) // len(self["bacteria_ids"])

    # Calculate the number of phage replicates per bacteria.
    n_phage_replicates = int((wells_per_bacteria - self["no_phage_control"])) \
      // len(self["phage_ids"])

    # Assign bacteria and phage to wells, ensuring the same bacteria is assigned
    # along each column.
    for i in range(0, n_columns-1, 2):  # Iterate over every other column from the left
      for j in range(n_rows):  # Iterate over rows within the column
        well_idx = (i * n_rows) + j
        for bacteria in self["bacteria_ids"]:
          if len(self[f"{bacteria}"]) >= wells_per_bacteria:
            continue
          self[f"{bacteria}"].append(well_idx)
          break

    for idxs in [self[f"{bacteria_id}"] for bacteria_id in self["bacteria_ids"]]:
      for i, phage_id in enumerate(self["phage_ids"]):
        for j in range(n_phage_replicates):
          well_idx = idxs[(i * n_phage_replicates) + j]
          self[f"{phage_id}"].append(well_idx)
          if i == len(self["phage_ids"]) - 1:
            if j < self["no_phage_control"]:
              self["phage_control"].append(idxs[(i * n_phage_replicates) + j + n_phage_replicates])

    # Generate a CSV report of the layout.
    with open("layout_report.csv", "w") as f:
      f.write("Well,Bacteria,Phage\n")
      for bacteria_id in self["bacteria_ids"]:
        for well_id in self[bacteria_id]:
          phage_id = self.get_phage_for_well(well_id)
          f.write(f"{well_id},{bacteria_id},{phage_id}\n")

    # Generate a visual representation of the layout (PDF or PNG).
    self.generate_layout_visualization()

  def get_phage_for_well(self, well_id: int) -> str:
      """
      Helper function to get the phage assigned to a given well.
      """
      for phage_id in self["phage_ids"]:
        if well_id in self[phage_id]:
          assert isinstance(phage_id, str), "Phage ID must be a string."
          return phage_id
      if well_id in self["phage_control"]:
        return "phage_control"
      return "unknown"

  def get_bacteria_for_well(self, well_id: int) -> str:
      """
      Helper function to get the bacteria assigned to a given well.
      """
      for bacteria_id in self["bacteria_ids"]:
        if well_id in self[bacteria_id]:
          assert isinstance(bacteria_id, str), "Bacteria ID must be a string."
          return bacteria_id
      return "none"

  def generate_layout_visualization(self):
        """
        Generate a visual representation of the layut (PNG).
        Wells are indexed from the upper right-hand corner, corresponding to A1.
        """
        import plotly.graph_objects as go
        import plotly.express as px

        # Define the color palette for phages
        phage_colors = px.colors.qualitative.Vivid
        phage_color_map = {
            phage_id: phage_colors[i % len(phage_colors)]
            for i, phage_id in enumerate(self["phage_ids"])
        }
        phage_color_map["phage_control"] = "lightgray"


        # Create a list to store the shapes (rectangles) for the wells
        shapes = []
        annotations = []

        # Draw the wells and color them according to the assigned phage
        # change edge color according to bacteria
        for i in range(96):
            row = (i) % 8  # Calculate row index (0-7)
            col = (i) // 8  # Calculate column index (0-11)
            row = 7 - row  # Invert row index to start from the top
            x0 = col * 10
            y0 = row * 10
            x1 = x0 + 10
            y1 = y0 + 10
            phage_id = self.get_phage_for_well(i)
            bacteria_id = self.get_bacteria_for_well(i)
            phage_color = phage_color_map.get(phage_id, "white")  # Default to white
            shapes.append(
                dict(
                    type="rect",
                    x0=x0,
                    y0=y0,
                    x1=x1,
                    y1=y1,
                    line=dict(color="black", width=1),
                    fillcolor=phage_color,
                )
            )
            # Annotate with bacteria name
            annotations.append(
                dict(
                    x=x0 + 5,
                    y=y0 + 5,
                    text=bacteria_id,
                    showarrow=False,
                    font=dict(size=12, color="white"),
                )
            )
            annotations.append(
                dict(
                    x=x0 + 5,
                    y=y0 + 2,  # Adjust position to avoid overlap with well ID
                    text=str(i + 1),
                    showarrow=False,
                    font=dict(size=10, color="white"),
                )
            )

        # Add letters A-H to the rows and numbers 1-12 to the columns
        for i, letter in enumerate("ABCDEFGH"):
            annotations.append(
          dict(
              x=-5,
              y=(7 - i) * 10 + 5,  # Adjust y position to match the row
              text=letter,
              showarrow=False,
              font=dict(size=12),
          )
            )
        for i in range(12):
            annotations.append(
          dict(
              x=i * 10 + 5,
              y=80 + 5,  # Adjust y position to be above the top row
              text=str(i + 1),
              showarrow=False,
              font=dict(size=12),
          )
            )

        # Create the layout for the plot
        layout = go.Layout(
            xaxis=dict(
          showgrid=False,
          zeroline=False,
          showticklabels=False,
          range=[-10, 130],  # Adjust range for better spacing
            ),
            yaxis=dict(
          showgrid=False,
          zeroline=False,
          showticklabels=False,
          range=[-10, 90],  # Adjust range for better spacing
            ),
            shapes=shapes,
            annotations=annotations,
            width=800,
            height=600,
            margin=dict(l=50, r=50, t=50, b=50),  # Adjust margins for better spacing
        )



        # Create the figure and add the shapes
        fig = go.Figure(layout=layout)

        # Add hover information for each well
        for i in range(96):
            row = (i) % 8  # Calculate row index (0-7)
            col = (i) // 8  # Calculate column index (0-11)
            well_letter = chr(65 + row)  # Convert row index to letter (A-H)
            row = 7 - row  # Invert row index to start from the top
            well_number = col + 1  # Convert column index to number (1-12)
            well_id = f"{well_letter}{well_number}"
            fig.add_trace(
          go.Scatter(
              x=[col * 10 + 5],
              y=[row * 10 + 5],
              mode="markers",
              marker=dict(size=10, color="rgba(0,0,0,0)"),  # Invisible marker
              text=well_id,
              hoverinfo="text",
              showlegend=False,
          )
            )

        # Add legend
        for phage_id, color in phage_color_map.items():
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=dict(size=10, color=color),
                    name=phage_id,
                )
            )

        # Show the plot
        fig.write_html("layout.html")


  def _check_parameters(self, parameters: dict):
    if len(parameters["bacteria_ids"]) > 6:
      raise ValueError("Too many bacteria strains. Currently, a maximum of six are supported.")


  def _check_deck(self, needed_deck_resources: list):
    """
    Check that the deck has all the resources needed for the experiment.
    """
    pass




  async def _execute(self):
    """
    Execute the experiment. This is the main function that runs the experiment. We will have tip
    washing basins filled, the function itself checks to see if the tip washing basins are full or
    need to be refilled. Then we will get samples from the sample reservoir and fill the holding
    well, inducer wells, and lagoons. If it is the first cycle, we will fill the reader plate.
    If it is not the first cycle, we will run the cycle and if the sampling interval has passed,
    we will fill the reader plate. We will then increment the cycle count and repeat the process.
    All functions rely on state data to determine what actions will be taken, and have been taken
    already this cycle.
    """


    async def empty_tip_washer():
      """
      Empty the tip washer.
      """
      await self.pump_manager.pump_volume(pump_name="auxiliary_pump",
                                                volume=self.parameters[f"washer_volume"] * self.tip_washer.num_basins,
                                                use_channels="waste",
                                                speed=0.8) # TODO: have calibrations work as functions with fit constants and parameters in PLR
      washer_state = {"is_filled": False, "last_filled": dt.now()}
      await self.update_resource_state([self.tip_washer],
                                  washer_state)
      await self.log(f"Tip washers emptied.")

    async def fill_tip_washer():
      async with TaskGroup() as tg: # need to test this
        water_in_coro = self.pump_manager.pump_volume(
          pump_name="auxiliary_pump",
          volume=self.parameters[f"washer_volume"] * 3,
          use_channels="water",
          speed=0.8
          )
        bleach_in_coro = self.pump_manager.pump_volume(
          pump_name="auxiliary_pump",
          volume=self.parameters[f"washer_volume"],
          use_channels="bleach",
          speed=0.8
          )
        tg.create_task(water_in_coro)
        tg.create_task(bleach_in_coro)
      time = dt.now()
      tip_washer_state = {"is_filled": True, "last_filled": time}
      await self.update_resource_state(self.tip_washer,
                                  tip_washer_state)
      await self.log(f"Tip washers filled.")

    async def handle_tip_washer():
      """
      Fill the tip washer with water and bleach.
      """
      if dt.now() - self[self.tip_washer.name]["last_filled"] \
        >= self.parameters["basin_refill_frequency"]: # TODO: check that this logic works with hours
          await empty_tip_washer()
          await fill_tip_washer()
      else:
        await fill_tip_washer()
      self["step"] = "transfer_samples"

    async def clean_sample_station():
      """
      Clean the sample station.
      """
      if "clean_progress" not in self[self.sample_reservoir.name]:
        self[self.sample_reservoir.name]["clean_progress"] = "unused"
      if "is_dirty" not in self[self.sample_reservoir.name]:
        self[self.sample_reservoir.name]["is_dirty"] = True # TODO: maybe have reference parameter
      #TODO: change for the use case with separate sample stations for each bacteria
      bleach_wash = self.pump_manager.pump_volume(
            pump_name=self.parameters["bacteria_pump"],
            volume=self.sample_reservoir.max_volume,
            use_channels="bleach",
            speed=0.8
            )
      water_wash = self.pump_manager.pump_volume(
            pump_name=self.parameters["bacteria_pump"],
            volume=self.sample_reservoir.max_volume,
            use_channels="water",
            speed=0.8
            )
      void = self.pump_manager.run_for_duration(
            pump_name=self.parameters["auxiliary_pump"],
            duration=self.parameters["void_volume"],
            use_channels="air",
            speed=0.8
            )
      waste = self.pump_manager.pump_volume(
            pump_name=self.parameters["auxiliary_pump"],
            volume=self.sample_reservoir.max_volume,
            use_channels="sample_waste",
            speed=0.8
            )
      if self[self.sample_reservoir.name]["is_dirty"]:
        while self[self.sample_reservoir.name]["is_dirty"]:
          match self[self.sample_reservoir.name]["clean_progress"]:
            case "unused":
              self[self.sample_reservoir.name]["clean_progress"] = "bleach_wash"
              self[self.sample_reservoir.name]["is_bleached"] = False
              #await self.sync_state()
            case "bleach_wash":
              await bleach_wash
              await void
              self[self.sample_reservoir.name]["clean_progress"] = "water_wash"
              self[self.sample_reservoir.name]["is_bleached"] = True
              #await self.sync_state()
            case "water_wash":
              await waste
              if "water_wash_substep" not in self[self.sample_reservoir.name]:
                self[self.sample_reservoir.name]["water_wash_substep"] = 0
              if self[self.sample_reservoir.name]["water_wash_substep"] == 3:
                self[self.sample_reservoir.name]["clean_progress"] = "waste"
                self[self.sample_reservoir.name]["water_wash_substep"] = 0
                self[self.sample_reservoir.name]["isQ_dirty"] = False
              else:
                await water_wash
                await void
                self[self.sample_reservoir.name]["water_wash_substep"] += 1
              #await self.sync_state()
      self[self.sample_reservoir.name]["last_cleaned"] = dt.now()
      await self.log(f"{self.sample_reservoir.name} cleaned.")
      #await self.sync_state()

    async def pump_on_bacteria(bacteria_id: str):
      """
      Get bacteria from the sample reservoir.
      """
      volume_needed = self.parameters["lagoon_flow_rate"] * \
        self[bacteria_id]["num_wells"] * \
          self["pumping_factor"]
      await self.pump_manager.pump_volume(
        pump_name=self["bacteria_pump"],
        volume=volume_needed,
        use_channels=bacteria_id,
        speed=0.8
        )
      sample_station_state = {"is_dirty": True, "has_bacteria": bacteria_id}
      await self.update_resource_state(self.sample_reservoir, sample_station_state)
      await self.log(f"{bacteria_id} bacteria added to sample reservoir.")
      #await self.sync_state()

    async def tips_okay_to_use(tips: list[TipSpot]) -> bool:
      """
      Check if the tips have been used and if they are dirty, have bleach on them, or are clean and
      ready to use.
      """
      if all("last_used" not in self[tip.name] for tip in tips):
        return True
      if any(self[tip.name]["last_bleached"] == self[tip.name]["last_used"] for tip in tips) \
          or any(self[tip.name]["is_dirty"] for tip in tips) \
            or any(self[tip.name]["is_bleached"] for tip in tips) \
              or not all(self[tip.name]["is_cleaned"] for tip in tips):
        return False
      return True

    async def transfer_and_bleach_tips(
      tips: list[TipSpot],
      source: Resource | list[Resource] | list[Well],
      target: Resource | list[Resource] | list[Well],
      volumes: list[float],
      mix_volumes: Optional[list[float]] = None,
      mix_speeds: Optional[list[float]] = None,
      mix_cycles: Optional[list[int]] = None): #TODO: state handling with match case
      assert self.liquid_handler is not None, "Liquid handler is not defined."
      if not await tips_okay_to_use(tips):
        warnings.warn("Tips are not ready to use. Skipping transfer.")
        return
      if not all(self.liquid_handler.head[i].get_tip_origin() == tip for i, tip in enumerate(tips)): # TODO: make library function
        if all(self.liquid_handler.head[i].get_tip_origin() is not None for i in \
          range(len(self.liquid_handler.head))):
          await self.log("Tips are loaded, but not correct. Raising warning and returning current tips.")
          warnings.warn("Tips are loaded, but not correct. Returning current tips.")
          await self.liquid_handler.return_tips()
        await self.liquid_handler.pick_up_tips(tips)
      await self.liquid_handler.aspirate(resources=source,
                        vols=volumes,
                        homogenization_volume=mix_volumes,
                        homogenization_speed=mix_speeds,
                        homogeneous_cycles=mix_cycles)
      await self.liquid_handler.dispense(resources=target,
                        vols=volumes,
                        mix_volume=mix_volumes,
                        mix_speed=mix_speeds,
                        mix_cycles=mix_cycles)
      bleach_time = dt.now()
      await self.liquid_handler.aspirate(resources=self.bleach_station,
                              vols=volumes)
      await self.liquid_handler.dispense(resources=self.bleach_station,
                              vols=[volume*1.1 for volume in volumes],
                              mix_volume=[volume*0.25 for volume in volumes],
                              mix_cycles=[2 for _ in volumes])
      # TODO: decide whether or not to include initial water
      tip_state = {"is_dirty": True,
                    "last_bleached": bleach_time,
                    "is_bleached": True,
                    "last_used": bleach_time}
      await self.update_resource_state(tips, tip_state)
      await self.log(f"Tips transfer complete and tips bleached.")
      #await self.sync_state()
      await self.liquid_handler.return_tips()

    async def prance_flow(bacteria_id: str):
      """
      Transfer the bacteria to the holding wells, inducer wells, and lagoons.
      """

      #TODO: figure out how to have state checking for what has already been added to each well
      #TODO: state tracking using time comparison
      if not self.parameters["mixing"]:
        mix_volumes = None
        mix_speeds = None
        mix_cycles = None
      else:
        mix_volume = self.parameters["mixing_volume"]
        mix_speed = self.parameters["mixing_speed"]
        mix_cycles = self.parameters["mixing_cycles"]
      bacteria_wells = self[bacteria_id]["wells"]
      well_sets = await split_wells_along_columns(bacteria_wells)
      if not self["transfer_substep"]:
            self["transfer_substep"] = "station_to_holding"
      for well_set in well_sets:
        if not all(self[well.name]["transfer_substep"] for well in well_set):
          await self.update_resource_state(well_set, {"transfer_substep": "station_to_holding",
                                                    "last_bacteria_added": dt.now(),
                                            "last_cycle": self["cycle_n"]})
        if all(self[well.name]["transfer_substep"] == "finished" for well in well_set):
          if all(self[well.name]["last_cycle"] == self["cycle_n"] for well in well_set):
            continue
          else:
            await self.update_resource_state(well_set, {"transfer_substep": "station_to_holding",
                                                    "last_bacteria_added": dt.now(),
                                              "last_cycle": self["cycle_n"]})
        holding_wells = well_set
        well_idx = [await well_to_int(well, self.holding) for well in well_set]
        induced_wells = self.induced[well_idx]
        lagoon_wells = self.lagoons[well_idx]
        reader_plate = cast(Plate, self.reader_plate_stack_in_use.get_top_item())
        reader_plate_wells = reader_plate[well_idx] # TODO: change to function to get the appropriate wells, it should fill the plate in order of availability
        holding_tips = self.holding_tip_rack[well_idx]
        induced_tips = self.induced_tip_rack[well_idx]
        lagoon_tips = self.lagoon_tip_rack_1[well_idx]
        volumes = [self["lagoon_flow_rate"] for _ in well_set]
        if self["mixing"]:
          mix_volumes = [mix_volume for _ in well_set]
          mix_speeds = [mix_speed for _ in well_set]
          mix_cycles = [mix_cycles for _ in well_set]
        transfer_then_bleach = partial(transfer_and_bleach_tips,
                                  volumes=volumes,
                                  mix_volumes=mix_volumes,
                                  mix_speeds=mix_speeds,
                                  mix_cycles=mix_cycles)
        while not all(self[well.name]["transfer_substep"] == "finished" \
          for well in well_set):
          match self["transfer_substep"]:
            case "station_to_holding":
              await transfer_then_bleach(tips=holding_tips,
                                    source=self.sample_reservoir,
                                    target=holding_wells)
              await self.update_resource_state(holding_wells, {"bacteria": bacteria_id,
                                                      "last_bacteria_added": dt.now(),
                                                      "transfer_substep": "holding_to_induced"})
              self["transfer_substep"] = "holding_to_induced"
              #await self.sync_state()
            case "holding_to_induced":
              await transfer_then_bleach(tips=induced_tips,
                                    source=holding_wells,
                                    target=induced_wells)
              await self.update_resource_state(induced_wells, {"bacteria": bacteria_id,
                                                      "last_bacteria_added": dt.now(),
                                                      "transfer_substep": "induced_to_lagoon"})
              self["transfer_substep"] = "induced_to_lagoon"
              #await self.sync_state()
            case "induced_to_lagoon":
              await transfer_then_bleach(tips=lagoon_tips,
                                    source=induced_wells,
                                    target=lagoon_wells)
              await self.update_resource_state(lagoon_wells, {"bacteria": bacteria_id,
                                                      "last_bacteria_added": dt.now(),
                                                      "transfer_substep": "lagoon_to_reader"})
              self["transfer_substep"] = "lagoon_to_reader"
              #await self.sync_state()
            case "lagoon_to_reader":
              assert self.liquid_handler is not None, "Liquid handler is not defined."
              # TODO: change to time based checking
              if self["cycle_n"] == 0 or \
              (self["cycle_n"] % self.parameters["sampling_interval"] == 0):
                if reader_plate.has_lid():
                  assert reader_plate.lid is not None, "Lid is not defined."
                  await self.liquid_handler.move_lid(reader_plate.lid, to=self.finished_plates_stack)
                  self[reader_plate.lid.name]["is_on"] = False # unsure if this is needed
                await transfer_then_bleach(tips=lagoon_tips,
                                      source=lagoon_wells,
                                      target=reader_plate_wells)# TODO: get the transfer to go to half of the plates
                await self.update_resource_state(reader_plate_wells, {"bacteria": bacteria_id,
                                                  "last_bacteria_added": dt.now()})
                if not reader_plate.has_lid():
                  reader_plate_lid = cast(Lid, self.liquid_handler.get_resource(f"{reader_plate.name}_lid"))
                  await self.liquid_handler.move_lid(reader_plate_lid, to=reader_plate)
              self["transfer_substep"] = "finished"
              await self.update_resource_state(well_set, {"transfer_substep": "finished"})
              #await self.sync_state()
      self["step"] = "add_inducer"
      #await self.sync_state()


    async def transfer_samples():
      """
      Pump in and get samples from the sample reservoir and transfer to holding wells, inducer
      wells, lagoons, and transfer to reader plate if indicated. Mix if indicated.
      """
      if ["last_bacteria_added"] not in self.runtime_state:
        self["last_bacteria_added"] = dt.now()
        self["last_bacteria_added_id"] = self.parameters["bacteria_ids"][0]
        #await self.sync_state()
      for bacteria_id in self.parameters["bacteria_ids"]:
        await clean_sample_station()
        await pump_on_bacteria(bacteria_id)
        await prance_flow(bacteria_id)


    async def add_inducer():
      """
      Add inducer to the inducer wells.
      """
      assert self.liquid_handler is not None, "Liquid handler is not defined."
      tips = self.inducer_tip_rack[range(96)]
      if not await tips_okay_to_use(tips):
        warnings.warn("Tips are not ready to use. Skipping transfer.")
        return
      # TODO: introduce parameter to determine if inducer is added with 8 or 96 head
      # TODO: allow for concentration to be used instead of volume
      # TODO: check if tips already loaded and add state tracking for aspirate and dispense
      await self.liquid_handler.pick_up_tips96(tip_rack=self.inducer_tip_rack)
      await self.liquid_handler.aspirate96(resource=self.inducer_reservoir,
                                            volume=self.parameters["inducer_volume"])
      await self.liquid_handler.dispense96(resource=self.induced,
                                            volume=self.parameters["inducer_volume"])
      # TODO: make this so that there is mixing by default
      # TODO: add state tracking for inducer
      await self.liquid_handler.aspirate96(resource=self.bleach_station,
                                            volume=self.parameters["inducer_volume"]*1.1,
                                            homogenization_volume=self.parameters["inducer_volume"]*0.25,
                                            homogenization_cycles=2)
      await self.liquid_handler.dispense96(resource=self.bleach_station,
                                            volume=self.parameters["inducer_volume"]*1.1,
                                            mix_volume=self.parameters["inducer_volume"]*0.25,
                                            mix_cycles=2)
      await self.liquid_handler.return_tips96()
      await self.log(f"Inducer added to inducer wells.")
      self["step"] = "read_plate"
      #await self.sync_state()


    async def read_plate():
      """
      Read the plate if indicated and log data.
      """
      assert self.plate_reader is not None, "Plate reader is not defined."
      assert self.liquid_handler is not None, "Liquid handler is not defined."
      # TODO: change sampling interval to time based
      if self["cycle_n"] == 0 or \
        (self["cycle_n"] % self.parameters["sampling_interval"] == 0):
        if self.reader_plate_stack_in_use.is_empty():
          await self.log(f"Reader plate stack is empty. Please add more plates.")
          return
        reader_plate = cast(Plate, self.reader_plate_stack_in_use.get_top_item())
        if not reader_plate.has_lid():
          reader_plate_lid = cast(Lid, self.liquid_handler.get_resource(f"{reader_plate.name}_lid"))
          await self.liquid_handler.move_lid(reader_plate_lid, to=reader_plate)
        await self.liquid_handler.move_plate(reader_plate, to=self.plate_reader) # TODO: orient grip direction
        abs_data = await self.plate_reader.read_absorbance(reader_plate)
        # TODO: find exact serial commands to send from clariostar log for abs kinetic
        await self.data.insert_data(table_name="absorbance_readings", data=abs_data)
        # TODO: add methods to experiment to get data from plate reader array to tidy format
        lum_data = await self.plate_reader.read_luminescence(reader_plate)
        await self.data.insert_data(table_name="luminescence_readings", data=lum_data)
        await self.log(f"Plate read.")
        await self.liquid_handler.move_plate(reader_plate, to=self.finished_plates_stack)
        await self.log(f"Plate added to finished stack.")
        if self.reader_plate_stack_in_use.is_empty():
          self.reader_plate_stack_in_use = self.reading_plates_stack_1
        else: # TODO: check if this code is correct
          self.reader_plate_stack_in_use = self.reader_plate_stack_in_use.get_next_item()
        #await self.sync_state()
      self["step"] = "clean_tips"
      #await self.sync_state()

    async def all_tips_clean(tip_rack: TipRack) -> bool:
      """
      Check if the tips are clean or have bleach on them.
      """
      if any(self[tip.name]["is_dirty"]for tip in tip_rack[range(tip_rack.num_items)]) or any(self[tip.name]["is_bleached"] for tip in tip_rack[range(tip_rack.num_items)]): # TODO: make independent of 96
        if not all(self[tip.name]["last_clean_cycle"] == self["cycle_n"] for tip in tip_rack[range(tip_rack.num_items)]): # TODO: make time based
          return False
      return True

    async def clean_tips():
      """
      Clean the tips.
      """
      assert self.liquid_handler is not None, "Liquid handler is not defined."
      for tip_rack in self.tip_racks:
        if not await all_tips_clean(tip_rack):
          if not all(self.liquid_handler.head96[i].get_tip_origin() == tip_rack[i] for i in range(96)): # TODO: see if there is some united way to instead check for if the tips are already loaded
            await self.liquid_handler.pick_up_tips96(tip_rack)
          tip_volume = tip_rack.get_all_tips()[0].maximal_volume * 0.75
          clean_aspirate = partial(self.liquid_handler.aspirate96,
                                  volume=tip_volume)
          clean_dispense = partial(self.liquid_handler.dispense96,
                                  volume=tip_volume,
                                  mix_volume=tip_volume*0.5,
                                  mix_cycle=10)
          clean_stations = [self.bleach_station, self.water_station_1, self.water_station_2, self.water_station_3]
          for i, station in enumerate(clean_stations):
            if self[station.name]["next_clean_station"] != station.name:
              continue
            await clean_aspirate(resource=station)
            await clean_dispense(resource=station)
            if i < len(clean_stations) - 1:
              tip_state: dict[str, Any] = {"next_clean_station": clean_stations[i+1].name}
              await self.update_resource_state(tip_rack, tip_state)
              #await self.sync_state()
          tip_state = {"is_dirty": False,
                        "is_bleached": False,
                        "is_cleaned": True,
                        "last_clean_cycle": self["cycle_n"]}
          await self.update_resource_state(tip_rack, tip_state) # TODO: check if this should be tiprack or tips/tip spots
          await self.liquid_handler.return_tips96()
          await self.log(f"{tip_rack.name} tips cleaned.")

    while True:
      match self.runtime_state["step"]:
        case "fill_tip_washer":
          await handle_tip_washer()
        case "transfer_samples":
          await transfer_samples()
        case "add_inducer":
          await add_inducer()
        case "read_plate":
          if self["cycle_n"] == 0 or \
              (self["cycle_n"] % self.parameters["sampling_interval"] == 0): # TODO: maybe change to time based, rather than cycle based
            await read_plate()
        case "clean_tips":
          await clean_tips()
        case "wait_for_next_cycle":
          if dt.now() - self.cycle_start_time >= self.cycle_time:
            self["cycle_n"] += 1
            self.runtime_state["step"] = "fill_tip_washer"
          else:
            await asyncio.sleep(10)
        case _:
          raise ValueError("Invalid step in state.")

  async def _setup(self):
    """
    Setup the experiment
    """
    assert self.lab is not None, "Lab is not defined."
    self.basin_refill_freq = timedelta(hours=self.parameters["basin_refill_frequency"])
    self.cycle_time = timedelta(minutes=self.parameters["cycle_time"])
    deck = self.lab.deck
    self.bacteria_pumps: NamedPumpArray = cast(NamedPumpArray,
                                                deck.get_resource(self.parameters["bacteria_pump"]))
    self.bacteria_pumps.channel_names = self.parameters["bacteria_index"]
    self.auxiliary_pump: NamedPumpArray = cast(NamedPumpArray, deck.get_resource(self.parameters["auxiliary_pump"]))
    self.pump_manager: PumpManager = PumpManager(pumps = [self.bacteria_pumps, self.auxiliary_pump])
    self.inducer_reservoir: Plate = cast(Plate, deck.get_resource("inducer_reservoir"))
    self.sample_reservoir: SampleReservoir = cast(SampleReservoir, deck.get_resource("sample_reservoir"))
    self.inducer_wells: list[Well] = get_all_wells(self.inducer_reservoir)
    self.holding: Plate = cast(Plate, deck.get_resource("holding_plate"))
    self.induced: Plate = cast(Plate, deck.get_resource("induced_plate"))
    self.lagoons: Plate = cast(Plate, deck.get_resource("lagoon_plate"))
    self.holding_wells: list[Well] = get_all_wells(self.holding)
    self.induced_wells: list[Well] = get_all_wells(self.induced)
    self.lagoon_wells: list[Well] = get_all_wells(self.lagoons)
    self.reading_plates_stack_1: ResourceStack = cast(ResourceStack,
                                                      deck.get_resource("reader_plate_stack_1"))
    self.reading_plates_stack_2: ResourceStack = cast(ResourceStack,
                                                      deck.get_resource("reader_plate_stack_2"))
    self.reading_plates_stack_3: ResourceStack = cast(ResourceStack,
                                                      deck.get_resource("reader_plate_stack_3"))
    self.finished_plates_stack: ResourceStack = cast(ResourceStack,
                                                      deck.get_resource("finished_plate_stack"))
    self.to_read_plates_stack: ResourceStack = cast(ResourceStack,
                                                    deck.get_resource("to_read_plate_stack"))
    self.plate_reader: PlateReader = cast(PlateReader, deck.get_resource("plate_reader"))
    self.tip_washer: TipWasher = cast(TipWasher,
                                                    deck.get_resource("bleach_water_tip_washer"))
    self.bleach_station: Container = cast(Container,deck.get_resource("bleach_station"))
    self.water_station_1: Container = cast(Container, deck.get_resource("water_station_1"))
    self.water_station_2: Container = cast(Container, deck.get_resource("water_station_2"))
    self.water_station_3: Container = cast(Container, deck.get_resource("water_station_3"))
    self.inducer_tip_rack: TipRack = cast(TipRack, deck.get_resource("inducer_tips"))
    self.holding_tip_rack: TipRack = cast(TipRack, deck.get_resource("holding_tips"))
    self.induced_tip_rack: TipRack = cast(TipRack, deck.get_resource("induced_tips"))
    self.lagoon_tip_rack_1: TipRack = cast(TipRack, deck.get_resource("lagoon_tips_1"))
    self.lagoon_tip_rack_2: TipRack = cast(TipRack, deck.get_resource("lagoon_tips_2"))
    self.tip_racks: list[TipRack] = [self.inducer_tip_rack, self.holding_tip_rack,
                                      self.induced_tip_rack, self.lagoon_tip_rack_1,
                                      self.lagoon_tip_rack_2]
    self.inducer_tips: list[Tip] = self.inducer_tip_rack.get_all_tips()
    self.holding_tips: list[Tip] = self.holding_tip_rack.get_all_tips()
    self.induced_tips: list[Tip] = self.induced_tip_rack.get_all_tips()
    self.lagoon_tips_1: list[Tip] = self.lagoon_tip_rack_1.get_all_tips()
    self.lagoon_tips_2: list[Tip] = self.lagoon_tip_rack_2.get_all_tips()
    if "step" not in self.runtime_state:
      self["step"] = "fill_tip_washer"
      if self.parameters["prefilled_basins"]:
          self[self.tip_washer.name]["is_filled"] = True
          self[self.tip_washer.name]["last_filled"] = self.start_time
    # TODO: test and if current sync_state implementation works

  async def _stop(self):
      """
      Stop the experiment
      """

  async def _intervene(self, user_input: str):
    """
    Helper function for interventions in the experiment. Please override this function in the
    subclass if you want to add more interventions.
    """
    match user_input:
      case "add_phage":
        await self.add_phage()

  async def add_phage(self):
    """
    Add phage to the phage control wells.
    """
    if self.parameters["phage_input_method"] == "manual":
      print("Please add phage to the appropriate wells.")
      print("Consult the phage_layout.png for the correct layout.")
    print("Adding phage to the appropriate wells.")


  async def _resume(self):
    """
    Resume the experiment
    """

  async def _save_state(self):
    """
    Save the experiment state
    """
    pass

  async def _load_state(self):
    """
    Load the experiment state
    """
    pass

  async def _abort(self):
    """
    Abort the experiment.
    """
    pass
