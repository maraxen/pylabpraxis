from praxis.configure import LabConfiguration, ExperimentConfiguration
from abc import ABC, abstractmethod
import os
from os import PathLike
from shelve import DbfilenameShelf
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.resources.deck import Deck
from pylabrobot.resources import Resource
import datetime
import logging
import json
import asyncio
from praxis.utils.notify import Notifier
from praxis.operations import Operation, OperationError, OperationManager
from pylabrobot.visualizer.visualizer import Visualizer
from praxis.utils.data import Data
from typing import Optional, Coroutine, Any, Sequence

class Experiment(ABC):
  """
  Experiment class to execute the experiment and store the results.

  State variables and parameters should never have the same name.
  """

  def __init__(
      self,
      lab_configuration: PathLike,
      experiment_configuration: PathLike,
      needed_parameters: dict[str, type],
      needed_deck_resources: dict[str, type],
      check_list: list[str]
  ):
    self.lab_configuration = LabConfiguration(lab_configuration)
    self.experiment_configuration = ExperimentConfiguration(experiment_configuration)
    self.deck = self.experiment_configuration.deck
    self.check_experiment_configuration(needed_parameters, needed_deck_resources)
    self.parameters = self.experiment_configuration.parameters
    self.liquid_handler_id = self.experiment_configuration.liquid_handler
    self.machines = self.experiment_configuration.machines
    self.directory = self.experiment_configuration.directory
    self.name = self.experiment_configuration.name
    self.user = self.experiment_configuration.user
    self.user_info = self.lab_configuration.members["users"][self.user]
    self.description = self.experiment_configuration.description
    self.data_directory = self.experiment_configuration.data_directory
    self._lh_state_file = os.path.join(self.directory, self.name, "_lh_state.json")
    self._lab = None
    self._liquid_handler = None
    self._runtime_state: dict = {}
    self._state_file = os.path.join(self.directory, self.name + ".db")
    self._start_time = datetime.datetime.now()
    self._status = "initializing"
    self._end_time = datetime.datetime.now()
    self._results = None
    self._errors: list[Exception] = []
    self._paused = False
    self._failed = False
    self._common_prompt = "Type command or press enter to resume experiment. Input 'help' to see \
                      available commands."
    self._available_commands = {
        "abort": "Abort the experiment",
        "pause": "Pause the experiment",
        "resume": "Resume the experiment",
        "save": "Save the experiment state",
        "load": "Load the experiment state",
        "status": "Get the status of the experiment",
        "help": "Get a list of available commands",
    }
    self._visualizer = None
    self.check_list(check_list)
    self.start_loggers()
    self._emailer = Notifier(
      smtp_server=self.lab_configuration.smtp_server,
      smtp_port=self.lab_configuration.smtp_port,
      smtp_username=self.user_info["smtp_username"],
      smtp_password=self.user_info["smtp_password"]
    )
    self.setup_state_file()
    self.setup_data_directory()
    self.create_readme()
    self.lab_configuration.using(using=self.machines)
    self.lab_configuration.specify_deck(deck=self.deck)


  @property
  def paused(self) -> bool:
    return self._paused

  @property
  def failed(self) -> bool:
    return self._failed

  @property
  def available_commands(self) -> dict:
    return self._available_commands

  @property
  def emailer(self) -> Notifier:
    return self._emailer

  @property
  def common_prompt(self) -> str:
    return self._common_prompt

  @property
  def status(self) -> str:
    return self._status

  @property
  def results(self) -> None | str:
    return self._results

  @property
  def errors(self) -> list[Exception]:
    return self._errors

  @property
  def runtime_state(self) -> dict:
    return self._runtime_state

  @property
  def start_time(self) -> datetime.datetime:
    return self._start_time

  @property
  def end_time(self) -> datetime.datetime:
    return self._end_time

  @property
  def data(self) -> Data:
    return self._data

  @property
  def readme_file(self) -> str:
    return self._readme_file

  @property
  def visualizer(self) -> None | Visualizer:
      return self._visualizer

  @property
  def state_file(self) -> str:
    return self._state_file

  @property
  def liquid_handler(self) -> LiquidHandler | None:
    return self._liquid_handler

  @property
  def lab(self) -> LabConfiguration | None:
    return self._lab

  @property
  def lh_state_file(self) -> str:
    return self._lh_state_file

  def __getitem__(self, key: str) -> Any:
    if key in self.parameters:
      return self.parameters[key]
    if key in self.runtime_state:
      return self.runtime_state[key]
    raise KeyError(f"Key {key} not found in parameters or runtime state.")

  def __setitem__(self, key: str, value: Any) -> None:
    self.runtime_state[key] = value
    self.sync_state()

  def check_list(self, check_list: list[str]):
    """
    Remind the user of experiment information before beginning the experiment.
    """
    print("Initializing experiment...")
    for item in check_list:
      print(f"- {item}")
      input = input("Press any key to continue. Otherwise, press Ctrl+C to exit.")
    print("All set to begin the experiment.")

  def check_experiment_configuration(self,
                                      needed_parameters: dict[str, type],
                                      needed_deck_resources: dict[str, type]):
    """
    Check the experiment configuration for required fields and validate that resources
    are available in the lab configuration.

    Args:
      needed_parameters: A dictionary of needed parameters and their types.
      needed_deck_resources: A list of needed deck resources.

    Raises:
      ValueError: If a parameter is missing or is not of the correct type.
    """
    if not self.experiment_configuration.name:
      raise ValueError("Experiment name is required.")
    if not self.experiment_configuration.description:
      raise ValueError("Experiment description is required.")
    if not self.experiment_configuration.user:
      raise ValueError("Experiment user is required.")
    if not self.experiment_configuration.directory:
      raise ValueError("Experiment directory is required.")
    if not self.experiment_configuration.data_directory:
      raise ValueError("Experiment data directory is required.")
    self.check_parameters(needed_parameters)
    self.check_deck_resources(needed_deck_resources)

  def check_parameters(self, needed_parameters: dict[str, type]):
    """
    Check the experiment configuration for required fields.

    Args:
      needed_parameters: A dictionary of needed parameters and their types.

    Raises:
      ValueError: If a parameter is missing or is not of the correct type.
    """
    for parameter in needed_parameters:
      if parameter not in self.experiment_configuration.parameters:
        raise ValueError(f"Missing parameter {parameter}")
      if not isinstance(self.experiment_configuration[parameter], needed_parameters[parameter]):
        raise ValueError(f"Parameter {parameter} should be of type {needed_parameters[parameter]}")
    self._check_parameters(needed_parameters)

  def check_deck_resources(self, needed_deck_resources: dict):
    """
    Check that the deck has all the resources needed for the experiment.

    Args:
      needed_deck_resources: A list of needed deck resources as their PLR resource names.

    Raises:
      ValueError: If a component is missing
    """
    for resource in needed_deck_resources:
      if not self.deck.has_resource(resource):
        raise ValueError(f"Deck is missing {resource}")
      if not isinstance(self.deck.get_resource(resource), needed_deck_resources[resource]):
        raise ValueError(f"Resource {resource} should be of type {needed_deck_resources[resource]}")
    self._check_deck_resources(needed_deck_resources)

  @abstractmethod
  def _check_parameters(self, parameters: dict[str, type]):
    """
    Check the parameters for the experiment bounded by method specific constraints.
    """

  @abstractmethod
  def _check_deck_resources(self, needed_deck_resources: dict[str, type]):
    """
    Check that the deck has all the resources needed for the experiment.
    """

  async def update_resource_state(self,
                                  resources: str | Resource | Sequence[str | Resource],
                                  update: dict):
    """
    Update the state of a resource with the given dictionary.
    """
    if not isinstance(resources, Sequence):
      resources = [resources]
    if not all(isinstance(resource, (str, Resource)) for resource in resources):
      raise ValueError("Resources must be of type str or Resource.")
    for resource in resources:
      if isinstance(resource, Resource):
        self[resource.name].update(update)
      elif isinstance(resource, str):
        self[resource].update(update)

  def setup_state_file(self):
    """
    Check if the state file exists and create it if it does not. If the state file exists, load
    the state.
    """
    persistent_state: DbfilenameShelf = DbfilenameShelf(self.state_file)
    with persistent_state as state:
      if "name" not in state:
        state["name"] = self.name
        state["status"] = self.status
        state["start_time"] = self.start_time
      else:
        self.already_ran = True
        self.load_state()
      self._runtime_state.update(state)

  async def setup_data_directory(self):
    """
    Check if the data directory exists and create it if it does not.
    """
    if not os.path.exists(self.data_directory):
        os.makedirs(self.data_directory)
    db_file = os.path.join(self.data_directory, "data.db")
    self._data = Data(db_file)

  async def execute(self):
      """
      Execute the experiment
      """
      try:
        async with self.lab_configuration as lab:  # ensures safety using machines
          self._lab = lab
          self._liquid_handler = lab.liquid_handler
          assert self.liquid_handler is not None, "Liquid handler not set up."
          await self._setup()
          if not self.already_ran:
            for resource in self.liquid_handler.get_all_children():
              self[resource.name] = {}
            await self.sync_state()
          await self._execute()
      except KeyboardInterrupt:
        await self.sync_state()
        await self.save_lab_state()
        await self.pause()
      except Exception as e:  # pylint: disable=broad-except
        await self.save_lab_state()
        self.logger.error("An error occurred: %s", e)
        print(f"An error occurred: {e}")
        self.errors.append(e)
        await self.log_error(error=e)
        await self.notify_error(error=e)
        self._failed = True
        await self.pause()
      finally:
        await self.stop()
        if self.failed:
            print("Experiment failed.")
        else:
            print("Experiment completed.")

  async def notify_error(self, error: Exception):
    """
    Email and text user about error.
    """
    sender_email = self.user_info["sender_email"]
    user_email = self.user_info["email"]
    user_phone = self.user_info["phone"]
    user_phone_carrier = self.user_info["phone_carrier"]
    try:
      if user_phone and user_phone_carrier:
          self.emailer.send_text(
              sender_email=sender_email,
              recipient_phone=user_phone,
              carrier=user_phone_carrier,
              subject=f"Error in experiment {self.name}",
              body=f"An error occurred in experiment {self.name}: {error}",
          )
      if user_email:
        self.emailer.send_email(
            sender_email=sender_email,
            recipient_email=self.user_info["notification_email"],
            subject=f"Error in experiment {self.name}",
            body=f"An error occurred in experiment {self.name}: {error}",
        )
    except Exception as e:
      self.logger.error("Error sending notification: %s", e)
      print(f"Error sending notification: {e}")


  async def stop(self):
    """
    End the experiment
    """
    self._end_time = datetime.datetime.now()
    self._status = "completed"
    self["last_status"] = "stopping"
    self["last_update"] = self.end_time
    self["end_time"] = self.end_time
    await self.sync_state()
    await self.log("Experiment ended.")
    self.update_readme("## Experiment Ends", f"- {self.end_time}")
    await self._stop()

  def sync_state(self):
    """
    Sync the state of the experiment
    """
    state: DbfilenameShelf
    with DbfilenameShelf(self.state_file) as state:
      state.update(self.runtime_state)

  async def get_status(self):
      """
      Get the status of the experiment
      """
      status_message = f"Experiment Status: {self.status}"
      print(f"{status_message}")
      await self.log(status_message)

  async def pause(self):
    """
    Pause the experiment.
    """
    if not self.paused:
      self._paused = True
      self._status = "paused"
      self["last_status"] = self.status
      self["last_update"] = datetime.datetime.now()
      print("Experiment paused.")
      await self.log("Experiment paused.")
      self.update_readme("## Experiment Pauses", f"- {self.runtime_state['last_update']}")
      await self._pause()
    else:
        print("Experiment is already paused.")
    await self.intervene(input(self.common_prompt))

  @abstractmethod
  async def _setup(self):
      """
      Setup the experiment. This should reference the lab configuration to get the necessary
      resources and set them up the deck. You can also set up the visualizer here. You can
      set up deck layout, liquid handlers, and other resources from an existing file, but
      you should pop in the resources from the lab configuration.
      """

  @abstractmethod
  async def _pause(self):
      """
      Pause the experiment
      """

  async def intervene(self, user_input: str):
      """
      Intervene in the experiment. This function is called when the user wants to intervene in the
      experiment. The user can enter commands to pause, resume, save, load, or abort the experiment.
      Please do not override this function, which should retain united sets of possible interventions.
      Instead, override the _intervene function to add more interventions.
      """
      match user_input:
          case "abort":
              await self.abort()
          case "pause":
              await self.pause()
          case "resume" | "":
              await self.resume()
          case "save":
              await self.save_lab_state()
              await self.intervene(input(self.common_prompt))
          case "load":
              await self.load_state()
              await self.intervene(input(self.common_prompt))
          case "status":
              await self.get_status()
              await self.intervene(input(self.common_prompt))
          case "help":
              print("Available commands:")
              for command, description in self._available_commands.items():
                  print(f"{command}: {description}")
              await self.intervene(input(self.common_prompt))
          case "wait_then_resume":
              time_to_wait = input("Enter the time to wait in seconds: ")
              print(f"Waiting for {time_to_wait} seconds before resuming.")
              confirmation = input(
                  "Press Enter to confirm, 'n' to cancel waiting before resuming, or \
                            input another command: "
              )
              if confirmation == "":
                  await asyncio.sleep(int(time_to_wait))
                  await self.resume()
              elif confirmation == "n":
                  print("Waiting and resuming the experiment has been cancelled.")
                  await self.intervene(input(self.common_prompt))
              else:
                  await self.intervene(confirmation)
          case _:
              if user_input not in self.available_commands:
                  print(f"Command {user_input} not recognized.")
                  await self.intervene(input(self.common_prompt))
              else:
                  await self._intervene(user_input)

  async def resume(self):
    """
    Resume the experiment
    """
    self._paused = False
    self._status = "running"
    self["last_status"] = self.status
    self["last_update"] = datetime.datetime.now()
    self.update_readme("## Experiment Resumes", f"- {self.runtime_state['last_update']}")
    print("Experiment resumed.")
    await self.log("Experiment resumed.")
    await self._resume()

  async def save_lab_state(self):
    """
    Save the lab state
    """
    if self.liquid_handler is not None:
      self.liquid_handler.save_state_to_file(f"{self.name}_lh.json")
      await self.log("Experiment state saved.")
    await self._save_state()

  async def load_state(self):
    """
    Load the experiment state and lab state.
    """
    if self.liquid_handler is not None:
      assert self.lab is not None, "Lab not loaded."
      self.liquid_handler.load_state_from_file("{self.name}_lh.json") # should this be awaited?
      await self.lab.align_states()
    state: DbfilenameShelf
    with DbfilenameShelf(self.state_file) as state:
      self._runtime_state.update(state)
      self._status = state["status"]
      self._start_time = state["start_time"]
    await self.log("Experiment state loaded.")
    await self._load_state()

  async def abort(self):
    """
    Abort the experiment
    """
    await self.log("Aborting experiment.")
    await self._abort()

  async def log(self, message: str):
      """
      Log a message and append it to the readme file.
      """
      self.logger.info(message)
      self.plr_logger.info(message)

  async def log_error(self, error: Exception):
      """
      Log error and append it to the errors list.
      """
      self.logger.error("An error occurred: %s", error)
      self.plr_logger.error("An experiment error occurred: %s", error)
      self.update_readme("## Experiment Errors", f"- {error}")
      self.errors.append(error)

  def start_loggers(self):
    """
    Start the loggers
    """
    logging.basicConfig(
        filename=os.path.join(self.directory, "experiment.log"),
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    self.logger = logging.getLogger(__name__)
    self.logger.info("Experiment %s.", self.name)
    self.logger.info("Experiment Directory: %s", self.directory)
    self.logger.info("Experiment State File: %s", self.state_file + ".db")
    self.logger.info("Experiment Data Directory: %s", self.data_directory)
    self.logger.info("Experiment start time: %s", self.start_time)
    self.logger.info("Experiment Name: %s", self.name)
    self.plr_logger = logging.getLogger("pylabrobot")
    self.plr_logger.info("Experiment %s started.", self.name)

  def create_readme(self):
    """
    Check if the readme file exists and create it if it does not.
    """
    self._readme_file = os.path.join(self.directory, "README.md")
    if not os.path.exists(self._readme_file):
      with open(self._readme_file, "ws") as f:
        f.write(f"# {self.name}\n\n")
        f.write(f"{self.description}\n\n")
        f.write("## Experiment Parameters\n\n")
        for key, value in self.parameters.items():
          f.write(f"- {key}: {value}\n")
        f.write("\n")
        f.write("## Experiment Results\n\n")
        f.write("No results yet.\n")
        f.write("\n")
        f.write("## Experiment Errors\n\n")
        f.write("No errors yet.\n")
        f.write("\n")
        f.write("## Experiment Starts\n\n")
        f.write("No start time yet.\n")
        f.write("\n")
        f.write("## Experiment Pauses\n\n")
        f.write("No pause times yet.\n")
        f.write("\n")
        f.write("## Experiment Resumes\n\n")
        f.write("No resume times yet.\n")
        f.write("\n")
        f.write("## Experiment Ends\n\n")
        f.write("No end time yet.\n")
        f.write("\n")
    else:
      print(f"Readme file already exists at {self._readme_file}.")
      self._check_readme_structure()
      self.update_readme("## Experiment Starts", f"- {self.start_time}")


  def _check_readme_structure(self):
    """
    Check the structure of the readme file.

    Raises:
      ValueError: If the readme file is missing information or is not correctly structured.
    """
    with open(self._readme_file, "rs") as f:
      lines = f.readlines()
      if len(lines) < 10:
        print("Readme file is missing information.")
        print("Please check the file to ensure it is correct.")
      if not self._lines_exist_with_headers(
        lines=lines,
        headers=[
          f"# {self.name}",
          "## Experiment Parameters",
          "## Experiment Results",
          "## Experiment Errors",
          "## Experiment Starts",
          "## Experiment Pauses",
          "## Experiment Resumes",
          "## Experiment Ends",
        ],
      ):
        raise ValueError("Readme file is missing proper headers.")
      else:
        print("Readme file is correctly structured.")

  async def _lines_exist_with_headers(self, lines: list[str], headers: list[str]) -> bool:
    """
    Check if the lines exist with the headers

    Args:
      lines (list[str]): The lines in the file
      headers (list[str]): The headers to check for

    Returns:
      bool: True if the lines exist with the headers, False otherwise
    """
    for header in headers:
      if header not in lines:
        return False
    return True



  def update_readme(self, section: str, message: str) -> None:
    """
    Update the readme file with the given message in the given section. This should not replace
    the existing section, but append to it.

    Args:
      section (str): The section to update
      message (str): The message to append to the section

    """
    with open(self._readme_file, "r") as f:
      lines = f.readlines()
    with open(self._readme_file, "w") as f:
      found_section = False
      for line in lines:
        if line.strip() == section:
          found_section = True
          f.write(line)
          f.write(message)
        else:
          f.write(line)
        if not found_section:
          f.write(f"\n{section}\n")
          f.write(message)

  @abstractmethod
  async def _execute(self):
      """
      Execute the experiment
      """

  @abstractmethod
  async def _stop(self):
      """
      Stop the experiment
      """

  @abstractmethod
  async def _intervene(self, user_input: str):
      """
      Helper function for interventions in the experiment. Please override this function in the
      subclass if you want to add more interventions.
      """

  @abstractmethod
  async def _resume(self):
      """
      Resume the experiment
      """

  @abstractmethod
  async def _save_state(self):
      """
      Save the experiment state
      """

  @abstractmethod
  async def _load_state(self):
      """
      Load the experiment state
      """

  @abstractmethod
  async def _abort(self):
      """
      Abort the experiment.
      """
