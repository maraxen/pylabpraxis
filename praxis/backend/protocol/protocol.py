from __future__ import annotations
from abc import abstractmethod
import os
from pylabrobot.resources import Resource
import datetime
import logging
import json
import asyncio
from .config import ProtocolConfiguration
from .required_assets import WorkcellAssets
from ..configure import PraxisConfiguration
from ..utils import Notifier, DEFAULT_NOTIFIER, State, db
from typing import Optional, Any, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import DeckManager, Workcell

from ..interfaces import ProtocolInterface, WorkcellInterface, WorkcellAssetsInterface


class Protocol(ProtocolInterface):
    """
    Protocol class to execute the protocol and store the results.

    Args:
      protocol_configuration: The protocol configuration
      state: The state of the protocol
      manual_check_list: A list of manual checks to perform before starting the protocol
      orchestrator: The orchestrator
      deck: The deck to use
      user_info: The user information

    Methods:
      check_list: Remind the user of protocol information before beginning the protocol.
      check_protocol_configuration: Check the protocol configuration for required fields and validate that resources are available in the lab configuration.
      check_deck_resources: Check that the deck has all the resources needed for the protocol.
      update_resource_state: Update the state of a resource with the given dictionary.
      setup_data_directory: Check if the data directory exists and create it if it does not.
      execute: Execute the protocol
      notify_error: Email and text user about error.
      stop: End the protocol
      get_status: Get the status of the protocol
      results: Get the results of the protocol
      errors: Get the errors of the protocol
      runtime_state: Get the runtime state of the protocol
      start_time: Get the start time of the protocol
      end_time: Get the end time of the protocol
      data: Get the data of the protocol
      readme_file: Get the readme file of the protocol
      visualizer: Get the visualizer of the protocol
      lab: Get the lab of the protocol
      paused: Get the paused status of the protocol
      failed: Get the failed status of the protocol
      available_commands: Get the available commands of the protocol
      emailer: Get the emailer of the protocol
      common_prompt: Get the common prompt of the protocol
      status: Get the status of the protocol
      start_loggers: Start the loggers
      create_readme: Create the readme file
      update_readme: Update the readme file
      log: Log a message and append it to the readme file
      log_error: Log error and append it to the errors list
      start_loggers: Start the loggers
      create_readme: Create the readme file
      update_readme: Update the readme file
      update_readme: Update the readme file
      _check_readme_structure: Check the structure of the readme file
      _lines_exist_with_headers: Check if the lines exist with the headers

    """

    def __init__(
        self,
        config: Union[ProtocolConfiguration, dict, str],
        praxis_config: Optional[PraxisConfiguration] = None,
    ):
        """Initialize Protocol with flexible configuration inputs.

        Args:
            config: Can be:
              - ProtocolConfiguration object
              - Configuration dictionary
              - Path to JSON config file
            praxis_config: Optional PraxisConfiguration (required if config is dict/path)
        """
        if isinstance(config, str):
            with open(config, "r") as f:
                config = json.load(f)

        if isinstance(config, dict):
            from .jsonschema_utils import validate_protocol_config

            validate_protocol_config(config)
            self.protocol_configuration = ProtocolConfiguration(config, praxis_config)
        else:
            self.protocol_configuration = config

        if config is None:
            raise ValueError("")

        self.praxis_config = self.protocol_configuration.praxis_config

        # Basic configuration setup
        self.machines = self.protocol_configuration.machines
        self.directory = self.protocol_configuration.directory
        self._name = self.protocol_configuration.name
        self.users = self.protocol_configuration.users
        self.parameters = self.protocol_configuration.parameters
        self.description = self.protocol_configuration.description

        # Get required assets from configuration
        self._required_assets = self.protocol_configuration.required_assets
        self._validate_and_setup_assets()
        self._validate_and_setup_assets()

        # Initialize state management
        self._workcell: Optional[WorkcellInterface] = None
        self.state: State = State(
            redis_host=self.praxis_config.redis_host,
            redis_port=self.praxis_config.redis_port,
            redis_db=self.praxis_config.redis_db,
        )
        self.data_directory = os.path.join(self.directory, "data")
        self.workcell_state_file = os.path.join(self.directory, "workcell_state.json")

        # Status tracking
        self._start_time = datetime.datetime.now()
        self._status = "initializing"
        self._end_time = datetime.datetime.now()
        self._results = None
        self._errors: list[Exception] = []
        self._paused = False
        self._failed = False
        self._common_prompt = (
            "Type command or press enter to resume protocol. Input 'help' to see "
            "available commands."
        )
        self._available_commands = {
            "abort": "Abort the protocol",
            "pause": "Pause the protocol",
            "resume": "Resume the protocol",
            "status": "Get the status of the protocol",
            "help": "Get a list of available commands",
        }
        self._visualizer = None
        self.start_loggers()
        self.already_ran = self.state.get(self.name, {}).get("already_ran", False)
        self.workcell_saves_dir = os.path.join(self.directory, "workcell_saves")
        self.data_backups_dir = os.path.join(self.directory, "data_backups")
        os.makedirs(self.workcell_saves_dir, exist_ok=True)
        os.makedirs(self.data_backups_dir, exist_ok=True)
        smtp_details = self.protocol_configuration.config_data.get("smtp_details", None)
        expected_keys = ["smtp_server", "smtp_port", "smtp_username", "smtp_password"]
        if (smtp_details is None) or not all(
            key in smtp_details for key in expected_keys
        ):
            raise ValueError(
                "SMTP server detail overrides not properly included. Structure should"
                "be 'smtp_server': SMTP_SERVER, 'smtp_port': SMTP_PORT, 'smtp_username': SMTP_USERNAME,"
                "'smtp_password': SMTP_PASSWORD' Current structure is: {smtp_details}"
            )
        self._notifier = (
            DEFAULT_NOTIFIER
            if smtp_details is None
            else Notifier(**smtp_details)  # TODO: check structure
        )
        del expected_keys
        del smtp_details
        expected_keys = [
            "sender_email",
            "email",
            "phone",
            "phone_carrier",
        ]  # TODO: maybe get rid of sender email and just have a default
        self._user_info = self.protocol_configuration.user_info
        if not all(key in self.user_info for key in expected_keys):
            raise ValueError("Needed details missing from user info.")
        self.db = db

        # Start logging and readme
        self.start_loggers()
        self.create_readme()

    async def initialize(self, workcell: Optional[WorkcellInterface] = None):
        """Initialize protocol with optional orchestrator integration."""
        if workcell:
            # Create workcell view if using orchestrator
            self._workcell = workcell
        else:
            # Create standalone workcell if no orchestrator
            self._workcell = await self._create_workcell_from_config()

    async def _load_workcell_from_file(
        self, filepath: str
    ) -> WorkcellInterface:  # TODO: figure out how to coordinate with orchestrator
        """Load workcell from a saved state file."""
        if self.praxis_config is None:
            raise RuntimeError("Protocol configuration not initialized")

        workcell = Workcell(
            config=self.praxis_config, save_file=self.workcell_state_file
        )
        await workcell.initialize_dependencies()
        await workcell.load_state_from_file(filepath)
        return workcell

    async def _create_workcell_from_config(self) -> WorkcellInterface:
        """Create new workcell from protocol configuration."""
        if self.protocol_configuration is None:
            raise RuntimeError("Protocol configuration not initialized")

        workcell = Workcell(
            config=self.protocol_configuration.praxis_config,
            save_file=self.workcell_state_file,
            user=self.users[0] if isinstance(self.users, list) else self.users,
            using_machines=[str(m) for m in self.machines],
        )

        await workcell.initialize_dependencies()

        # Configure deck layouts if specified
        if not self.protocol_configuration.decks_unspecified:
            for liquid_handler_id in self.protocol_configuration.liquid_handler_ids:
                deck_manager = DeckManager(self.praxis_config)
                deck = await deck_manager.get_deck(
                    self.protocol_configuration.decks[liquid_handler_id]
                )
                workcell.specify_deck(
                    liquid_handler_id=liquid_handler_id,
                    deck=deck,
                )

        # Validate required assets match workcell capabilities
        if self._required_assets:
            self._required_assets.validate(workcell)

        return workcell

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
    def notifier(self) -> Notifier:
        return self._notifier

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
    def start_time(self) -> datetime.datetime:
        return self._start_time

    @property
    def end_time(self) -> datetime.datetime:
        return self._end_time

    @property
    def readme_file(self) -> str:
        return self._readme_file

    @property
    def workcell(self) -> Optional[WorkcellInterface]:
        return self._workcell

    @property
    def user_info(self) -> dict[str, dict[str, Any]]:
        return self._user_info

    @property
    def name(self) -> str:
        return self._name

    @property
    def required_assets(self) -> WorkcellAssetsInterface:
        return self._required_assets

    def _validate_and_setup_assets(self) -> None:
        """Validate asset requirements and configure deck through workcell."""
        if not self._required_assets:
            return

        # Check for 96-channel head requirement
        if self._required_assets.get("needs_96_head"):
            if not hasattr(self.workcell, 'has_96_channel_head') or \
               not self.workcell.has_96_channel_head():
                raise ValueError("Protocol requires 96-channel head but none available")
            self._configure_96_head()

        # Validate asset placement considering existing deck state
        for asset_name, asset in self._required_assets.items():
            # Check carrier compatibility if specified
            if 'carrier_compatibility' in asset:
                if not self._check_carrier_compatibility(asset_name, asset):
                    raise ValueError(
                        f"No compatible carrier available for {asset_name}"
                    )

            # Check stackable flag and slot requirements
            if not asset.get('stackable', False):
                if not self._check_single_slot_available(asset_name, asset):
                    raise ValueError(
                        f"No available slot for non-stackable asset {asset_name}"
                    )

    def _configure_96_head(self) -> None:
        """Configure liquid handler for 96-channel head if possible."""
        if hasattr(self.workcell, 'liquid_handler') and \
           hasattr(self.workcell.liquid_handler, 'configure_for_96_head'):
            self.workcell.liquid_handler.configure_for_96_head()

    def _check_carrier_compatibility(self, asset_name: str, asset: dict) -> bool:
        """Check if compatible carriers are available with enough slots."""
        if not hasattr(self.workcell, 'deck'):
            return True  # Skip check if no deck

        required_slots = asset.get('min_slots', 1)
        compatible_carriers = asset.get('carrier_compatibility', [])

        # Check each compatible carrier type
        for carrier_type in compatible_carriers:
            # Get all carriers of this type on deck
            carriers = [
                r for r in self.workcell.deck.get_all_children()
                if r.__class__.__name__ == carrier_type
            ]

            # Check each carrier for available slots
            for carrier in carriers:
                available_slots = len([
                    s for s in carrier.get_all_children()
                    if not s.has_children()  # Empty slot
                ])
                if available_slots >= required_slots:
                    return True
        return False

    def _check_single_slot_available(self, asset_name: str, asset: dict) -> bool:
        """Check if at least one slot is available for non-stackable assets."""
        if not hasattr(self.workcell, 'deck'):
            return True  # Skip check if no deck

        # Check deck position if specified
        if 'deck_position' in asset:
            position = asset['deck_position']
            if not self.workcell.deck.is_position_available(position):
                return False

        # Count available slots
        available_slots = len([
            r for r in self.workcell.deck.get_all_children()
            if not r.has_children()  # Empty slot
        ])
        return available_slots > 0

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

    @abstractmethod
    def _check_workcell_assets(self, workcell_assets: WorkcellAssets) -> None:
        """Check that the deck has all the resources needed for the protocol.

        This method should be implemented by subclasses to perform protocol-specific
        resource validation.

        Args:
            deck_assets: DeckAssets object specifying required resources and machines.
        """
        pass

    @abstractmethod
    def _check_parameters(self, parameters: dict[str, type]) -> None:
        """Check the parameters for the protocol bounded by method specific constraints."""
        pass

    async def update_resource_state(
        self, resources: str | Resource | Sequence[str | Resource], update: dict
    ):
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

    async def execute(self):
        """
        Execute the protocol
        """
        try:
            # No need to create new workcell - use the view we already have
            if not self.workcell:
                raise ValueError("Workcell not initialized")

            async with self.workcell:  # This will handle resource access coordination
                if not self.already_ran:
                    self["already_ran"] = True
                await self._setup()
                await self._execute()
        except KeyboardInterrupt:
            await self.pause()
        except Exception as e:  # pylint: disable=broad-except
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
        for user in self.users:
            user_info = self.user_info[user]
            sender_email = user_info.get("sender_email", False)
            user_email = user_info.get("email", False)
            user_phone = user_info.get("phone", False)
            user_phone_carrier = user_info.get("phone_carrier", False)
            try:
                if user_phone and user_phone_carrier:
                    self.notifier.send_text(
                        sender_email=str(sender_email),
                        recipient_phone=str(user_phone),
                        carrier=str(user_phone_carrier),
                        subject=f"Error in protocol {self.name}",
                        body=f"An error occurred in protocol {self.name}: {error}",
                    )
                if user_email:
                    self.notifier.send_email(
                        sender_email=str(sender_email),
                        recipient_email=str(user_email),
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
            # Example: Ensure liquid handler is in a safe position
            if hasattr(self, "liquid_handler") and self.liquid_handler is not None:
                await self.liquid_handler.move_to_safe_position()  # TODO: find some way to implement this

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
            self.update_readme("## Protocol Pauses", f"- {self['last_update']}")
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
                await self.save_state()
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
        self.update_readme("## Protocol Resumes", f"- {self['last_update']}")
        print("Protocol resumed.")
        await self.log("Protocol resumed.")
        await self._resume()

    async def save_state(self):
        """Save the lab state"""
        if self.workcell:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(
                self.workcell_saves_dir, f"workcell_state_{timestamp}.json"
            )
            await self.workcell.save_state_to_file(save_path)
        await self._save_state()

    async def load_state(self):
        """Load the protocol state and lab state."""
        if self.workcell:
            await self.workcell.load_state_from_file(self.workcell_state_file)
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

        Args:
          message: The message to log
        """
        self.logger.info(message)
        self.plr_logger.info(message)

    async def log_error(self, error: Exception):
        """
        Log error and append it to the errors list.

        Args:
          error: The error to log
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
        self.logger.info("Protocol State File: %s", self.workcell_state_file)
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

    async def _lines_exist_with_headers(
        self, lines: list[str], headers: list[str]
    ) -> bool:
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

    async def save_output(self, config: PraxisConfiguration) -> None:
        """Save protocol output files."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save readme in protocol directory
        readme_path = os.path.join(self.directory, "README.md")
        with open(readme_path, "w") as f:
            f.write(self.create_readme())

        # Save workcell state in protocol's workcell_saves directory
        workcell_path = os.path.join(
            self.workcell_saves_dir, f"workcell_state_{timestamp}.json"
        )
        if self.workcell:
            await self.workcell.save_state_to_file(workcell_path)

    async def backup_data(self, config: PraxisConfiguration) -> None:
        """Backup protocol data during takedown or periodically."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.data_backups_dir, timestamp)
            os.makedirs(backup_dir, exist_ok=True)

            # Backup file path
            backup_file = os.path.join(backup_dir, f"{self.name}_data.sqlite")

            # Export protocol data to SQLite backup
            await self.db.export_protocol_data(self.name, backup_file)

            # Also backup the workcell state if available
            if self.workcell:
                workcell_backup = os.path.join(backup_dir, "workcell_state.json")
                await self.workcell.save_state_to_file(workcell_backup)

            self.logger.info(f"Created backup at {backup_dir}")

            # Clean up old backups (keep last 5)
            backups = sorted(
                [
                    d
                    for d in os.listdir(self.data_backups_dir)
                    if os.path.isdir(os.path.join(self.data_backups_dir, d))
                ]
            )
            while len(backups) > 5:
                oldest = backups.pop(0)
                import shutil

                shutil.rmtree(os.path.join(self.data_backups_dir, oldest))

        except Exception as e:
            self.logger.error(f"Failed to backup data: {str(e)}")
            await self.log_error(error=e)
            self.errors.append(e)
