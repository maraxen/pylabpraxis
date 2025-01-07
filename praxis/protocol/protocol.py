from __future__ import annotations
from abc import ABC, abstractmethod
import os
from os import PathLike
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.resources.deck import Deck
from pylabrobot.resources import Resource
import datetime
import logging
import json
import asyncio
from .parameter import Parameter, ProtocolParameters  # Import ProtocolParameters
from praxis.configure import LabConfiguration, ProtocolConfiguration
from praxis.utils.notify import Notifier
from praxis.utils.state import State
from praxis.operations import Operation, OperationError, OperationManager
from pylabrobot.visualizer.visualizer import Visualizer
from praxis.utils.data import Data
from typing import Optional, Coroutine, Any, Sequence, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from ..workcell import Workcell
    from ..conductor import Conductor

import warnings

class Protocol(ABC):
  """
  Protocol class to execute the protocol and store the results.

  """

  def __init__(
      self,
      protocol_configuration: ProtocolConfiguration,
      protocol_parameters: ProtocolParameters,
      needed_deck_resources: dict[str, type] | None,
      manual_check_list: list[str]):

    self.lab_configuration = LabConfiguration(lab_configuration)
    self.protocol_configuration = ProtocolConfiguration(protocol_configuration)
    self.state = State() # TODO: pull from praxis ini
    self.parameters = self.protocol_configuration.parameters
    self.uses_deck = not needed_deck_resources is None

    self.decks = self.protocol_configuration.decks
    if len(self.decks) != len(needed_deck_resources):
      raise ValueError("Number of decks and needed deck resources must be equal.")
    self.check_protocol_configuration(needed_deck_resources)
    self.parameters = self.protocol_configuration.parameters
    self.machines = self.protocol_configuration.machines
    self.directory = self.protocol_configuration.directory
    self.name = self.protocol_configuration.name
    self.user = self.protocol_configuration.user
    self.user_info = self.lab_configuration.members["users"][self.user]
    self.description = self.protocol_configuration.description
    self.data_directory = self.protocol_configuration.data_directory
    self.liquid_handler_ids = self.protocol_configuration.liquid_handler_ids
    self.decks = self.protocol_configuration.decks
    self.workcell_state_file = os.path.join(self.directory, "workcell_state.json")
    if len(self.liquid_handler_ids) != len(self.decks):
      raise ValueError("Number of liquid handlers and decks must be equal.")
    self._workcell = None
    self._start_time = datetime.datetime.now()
    self._status = "initializing"
    self._end_time = datetime.datetime.now()
    self._results = None
    self._errors: list[Exception] = []
    self._paused = False
    self._failed = False
    self._common_prompt = "Type command or press enter to resume protocol. Input 'help' to see \
                      available commands."
    self._available_commands = {
        "abort": "Abort the protocol",
        "pause": "Pause the protocol",
        "resume": "Resume the protocol",
        "save": "Save the protocol state",
        "load": "Load the protocol state",
        "status": "Get the status of the protocol",
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
  def lab(self) -> Workcell | None:
    return self._workcell

  def __getitem__(self, key: str) -> Any:
    return self.state[self.name][key]

  def __setitem__(self, key: str, value: Any) -> None:
    self.state[self.name][key] = value

  def check_list(self, check_list: list[str]):
    """
    Remind the user of protocol information before beginning the protocol.
    """
    print("Initializing protocol...")
    for item in check_list:
      print(f"- {item}")
      input = input("Press any key to continue. Otherwise, press Ctrl+C to exit.")
    print("All set to begin the protocol.")

  def check_protocol_configuration(self,
                                needed_parameters: dict[str, type],
                                needed_deck_resources: dict[str, type]):
    """
    Check the protocol configuration for required fields and validate that resources
    are available in the lab configuration.

    Args:
      needed_parameters: A dictionary of needed parameters and their types.
      needed_deck_resources: A list of dictionaries denoting needed deck resources.

    Raises:
      ValueError: If a parameter is missing or is not of the correct type.
    """
    if not self.protocol_configuration.name:
      raise ValueError("Protocol name is required.")
    if not self.protocol_configuration.description:
      raise ValueError("Protocol description is required.")
    if not self.protocol_configuration.user:
      raise ValueError("Protocol user is required.")
    if not self.protocol_configuration.directory:
      raise ValueError("Protocol directory is required.")
    if not self.protocol_configuration.data_directory:
      raise ValueError("Protocol data directory is required.")
    self.check_deck_resources(needed_deck_resources)

  def check_deck_resources(self, needed_deck_resources: dict[str | int, dict[str, type]]): #TODO: figure out best way to have which deck to check specified, probably just a dictionary
    """
    Check that the deck has all the resources needed for the protocol.

    Args:
      needed_deck_resources: A list of needed deck resources as their PLR resource names.

    Raises:
      ValueError: If a component is missing
    """

    errors: list = []
    if not all(isinstance(deck, Deck) for deck in self.decks):
      raise ValueError("All decks must be of type Deck.")
    for deck, resource_set in needed_deck_resources.items():
      for resource in resource_set:
        if not isinstance(resource, dict):
          raise ValueError("Resource must be a dictionary.")
        if not all(isinstance(key, str) for key in resource.keys()):
          raise ValueError("Resource keys must be strings.")
        if not all(isinstance(value, type) for value in resource.values()):
          raise ValueError("Resource values must be types.")
        if all(deck.has_resource(resource) for deck in self.decks):
          raise ValueError(f"All decks have resource {resource}. \
                            Please assign resources unique names to resources on different decks.")
        if not any(deck.has_resource(resource) for deck in self.decks):
          errors.append(f"No deck has needed resource {resource}.")
        deck_with_resource = [deck.has_resource(resource) for deck in self.decks].index(True)
        if not isinstance(self.decks[deck_with_resource].get_resource(resource), resource[resource]):
          errors.append(f"Resource {resource} in deck {deck_with_resource} should be of type \
            {resource[resource]}.")
      if errors:
          raise ValueError("Deck check failed with the following errors:\n" + "\n".join(errors))
      self._check_deck_resources(needed_deck_resources)

  @abstractmethod
  def _check_parameters(self, parameters: dict[str, type]):
    """
    Check the parameters for the protocol bounded by method specific constraints.
    """

  @abstractmethod
  def _check_deck_resources(self, needed_deck_resources: list[dict[str, type]]):
    """
    Check that the deck has all the resources needed for the protocol.
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
      Execute the protocol
      """
      try:
        wc: Workcell = Workcell(lab_configuration=self.lab_configuration,
                                      user=self.user,
                                      using_machines=self.machines)
        async with wc as workcell:  # ensures safety using machines
          self._workcell = workcell
          await self._setup()
          if not self.already_ran:
            for liquid_handler in self.workcell.liquid_handlers:
              for resource in liquid_handler.get_all_children():
                self[resource.name] = {}
          await self._execute()
      except KeyboardInterrupt:
        self.sync_state()
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
            print("Protocol failed.")
        else:
            print("Protocol completed.")

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
              subject=f"Error in protocol {self.name}",
              body=f"An error occurred in protocol {self.name}: {error}",
          )
      if user_email:
        self.emailer.send_email(
            sender_email=sender_email,
            recipient_email=self.user_info["notification_email"],
            subject=f"Error in protocol {self.name}",
            body=f"An error occurred in protocol {self.name}: {error}",
        )
    except Exception as e:
      self.logger.error("Error sending notification: %s", e)
      print(f"Error sending notification: {e}")


  async def stop(self):
    """
    End the protocol
    """
    self._end_time = datetime.datetime.now()
    self._status = "completed"
    self["last_status"] = "stopping"
    self["last_update"] = self.end_time
    self["end_time"] = self.end_time
    await self.sync_state()
    await self.log("Protocol ended.")
    self.update_readme("## Protocol Ends", f"- {self.end_time}")
    await self._stop()

  async def get_status(self):
      """
      Get the status of the protocol
      """
      status_message = f"Protocol Status: {self.status}"
      print(f"{status_message}")
      await self.log(status_message)

  async def _cleanup(self):
    """
    Performs cleanup operations to ensure safety.
    This method should be called if the protocol is interrupted or fails.
    """
    print("Performing cleanup operations...")
    try:
        # Example: Turn off all pumps
        if hasattr(self, "pump_manager"): # Check if it exists
            await self.pump_manager.stop_all_pumps()

        # Example: Ensure liquid handler is in a safe position
        if hasattr(self, "liquid_handler") and self.liquid_handler is not None:
            await self.liquid_handler.move_to_safe_position() # You would define this method in your LiquidHandler class

        # Add more cleanup operations as needed

    except Exception as e:
        print(f"Error during cleanup: {e}")

  async def pause(self):
    """
    Pause the protocol.
    """
    if not self.paused:
      self._paused = True
      self._status = "paused"
      self["last_status"] = self.status
      self["last_update"] = datetime.datetime.now()
      print("Protocol paused.")
      await self.log("Protocol paused.")
      self.update_readme("## Protocol Pauses", f"- {self.runtime_state['last_update']}")
      await self._pause()
    else:
        print("Protocol is already paused.")
    await self.intervene(input(self.common_prompt))

  @abstractmethod
  async def _setup(self):
      """
      Setup the protocol. This should reference the lab configuration to get the necessary
      resources and set them up the deck. You can also set up the visualizer here. You can
      set up deck layout, liquid handlers, and other resources from an existing file, but
      you should pop in the resources from the lab configuration.
      """

  @abstractmethod
  async def _pause(self):
      """
      Pause the protocol
      """

  async def intervene(self, user_input: str):
      """
      Intervene in the protocol. This function is called when the user wants to intervene in the
      protocol. The user can enter commands to pause, resume, save, load, or abort the protocol.
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
                  print("Waiting and resuming the protocol has been cancelled.")
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
    Resume the protocol
    """
    self._paused = False
    self._status = "running"
    self["last_status"] = self.status
    self["last_update"] = datetime.datetime.now()
    self.update_readme("## Protocol Resumes", f"- {self.runtime_state['last_update']}")
    print("Protocol resumed.")
    await self.log("Protocol resumed.")
    await self._resume()

  async def save_state(self):
    """
    Save the lab state
    """
    await self.workcell.save_state_to_file(self.workcell_state_file)
    await self._save_state()

  async def load_state(self):
    """
    Load the protocol state and lab state.
    """
    await self.workcell.load_state_from_file(self.workcell_state_file)
    state: DbfilenameShelf
    with DbfilenameShelf(self.state_file) as state:
      self._runtime_state.update(state)
      self._status = state["status"]
      self._start_time = state["start_time"]
    await self.log("Protocol state loaded.")
    await self._load_state()

  async def abort(self):
    """
    Abort the protocol
    """
    await self.log("Aborting protocol.")
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
    self.plr_logger.error("An protocol error occurred: %s", error)
    self.update_readme("## Protocol Errors", f"- {error}")
    self.errors.append(error)

  def start_loggers(self):
    """
    Start the loggers
    """
    logging.basicConfig(
        filename=os.path.join(self.directory, "protocol.log"),
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    self.logger = logging.getLogger(__name__)
    self.logger.info("Protocol %s.", self.name)
    self.logger.info("Protocol Directory: %s", self.directory)
    self.logger.info("Protocol State File: %s", self.state_file + ".db")
    self.logger.info("Protocol Data Directory: %s", self.data_directory)
    self.logger.info("Protocol start time: %s", self.start_time)
    self.logger.info("Protocol Name: %s", self.name)
    self.plr_logger = logging.getLogger("pylabrobot")
    self.plr_logger.info("Protocol %s started.", self.name)

  def create_readme(self):
    """
    Check if the readme file exists and create it if it does not.
    """
    self._readme_file = os.path.join(self.directory, "README.md")
    if not os.path.exists(self._readme_file):
      with open(self._readme_file, "ws") as f:
        f.write(f"# {self.name}\n\n")
        f.write(f"{self.description}\n\n")
        f.write("## Protocol Parameters\n\n")
        for key, value in self.parameters.items():
          f.write(f"- {key}: {value}\n")
        f.write("\n")
        f.write("## Protocol Results\n\n")
        f.write("No results yet.\n")
        f.write("\n")
        f.write("## Protocol Errors\n\n")
        f.write("No errors yet.\n")
        f.write("\n")
        f.write("## Protocol Starts\n\n")
        f.write("No start time yet.\n")
        f.write("\n")
        f.write("## Protocol Pauses\n\n")
        f.write("No pause times yet.\n")
        f.write("\n")
        f.write("## Protocol Resumes\n\n")
        f.write("No resume times yet.\n")
        f.write("\n")
        f.write("## Protocol Ends\n\n")
        f.write("No end time yet.\n")
        f.write("\n")
    else:
      print(f"Readme file already exists at {self._readme_file}.")
      self._check_readme_structure()
      self.update_readme("## Protocol Starts", f"- {self.start_time}")


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
          "## Protocol Parameters",
          "## Protocol Results",
          "## Protocol Errors",
          "## Protocol Starts",
          "## Protocol Pauses",
          "## Protocol Resumes",
          "## Protocol Ends",
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
      Execute the protocol
      """

  @abstractmethod
  async def _stop(self):
      """
      Stop the protocol
      """

  @abstractmethod
  async def _intervene(self, user_input: str):
      """
      Helper function for interventions in the protocol. Please override this function in the
      subclass if you want to add more interventions.
      """

  @abstractmethod
  async def _resume(self):
      """
      Resume the protocol
      """

  @abstractmethod
  async def _save_state(self):
      """
      Save the protocol state
      """

  @abstractmethod
  async def _load_state(self):
      """
      Load the protocol state
      """

  @abstractmethod
  async def _abort(self):
      """
      Abort the protocol.
      """
