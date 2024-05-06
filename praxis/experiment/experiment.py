from praxis.configure import LabConfiguration, ExperimentConfiguration
from abc import ABC, ABCMeta, abstractmethod
from typing import Optional
import os
from os import PathLike
import datetime
import logging
import asyncio
from praxis.utils.notify import Emailer

class Experiment(ABC):
  """
  Experiment class to execute the experiment and store the results.
  """
  def __init__(self,
                lab_configuration: LabConfiguration,
                experiment_configuration: ExperimentConfiguration):
    self._check_experiment_configuration(experiment_configuration)
    self.lab_configuration = lab_configuration
    self.experiment_configuration = experiment_configuration
    self._user = experiment_configuration.user
    self._directory = experiment_configuration.directory
    self._parameters = experiment_configuration.parameters
    self._name = experiment_configuration.name
    self._description = experiment_configuration.description
    self._user = experiment_configuration.user
    self._resources = experiment_configuration.resources
    self._data_directory = None
    self._lab = None
    self._id = None
    self._start_time = None
    self._end_time = None
    self._status = None
    self._results = None
    self._errors = []
    self._logger = None
    self._plr_logger = None
    self._state = None
    self._state_file = None
    self._data = None
    self._readme_file = None
    self._paused = False
    self._failed = False
    self._start_time = None
    self._plr_logger = None
    self._emailer = None
    self._common_prompt = "Type command or press enter to resume experiment. Input 'help' to see \
                          available commands."
    self._emailer = None
    self._common_prompt = "Type command or press enter to resume experiment. Input 'help' to see \
                          available commands."
    self._available_commands = {
      "abort": "Abort the experiment",
      "pause": "Pause the experiment",
      "resume": "Resume the experiment",
      "save": "Save the experiment state",
      "load": "Load the experiment state",
      "status": "Get the status of the experiment",
      "help": "Get a list of available commands"
    }

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
  def emailer(self) -> Emailer:
    return self._emailer

  @property
  def common_prompt(self) -> str:
    return self._common_prompt

  @property
  def user(self) -> str:
    return self._user

  @property
  def resources(self) -> list[str]:
    return self._resources

  @property
  def id(self) -> str:
    return self._id

  @property
  def directory(self) -> PathLike:
    return self._directory

  @property
  def parameters(self) -> dict:
    return self._parameters

  @property
  def name(self) -> str:
    return self._name

  @property
  def description(self) -> str:
    return self._description

  @property
  def data_directory(self) -> PathLike:
    return self._data_directory

  @property
  def start_time(self) -> datetime.datetime:
    return self._start_time

  @property
  def end_time(self) -> datetime.datetime:
    return self._end_time

  @property
  def status(self) -> str:
    return self._status

  @property
  def results(self) -> str:
    return self._results

  @property
  def errors(self) -> str:
    return self._errors

  @property
  def logger(self) -> logging.Logger:
    return self._logger

  @property
  def plr_logger(self) -> logging.Logger:
    return self._plr_logger

  @property
  def state(self) -> dict:
    return self._state

  @property
  def state_file(self) -> PathLike:
    return self._state_file

  @property
  def data(self) -> dict:
    return self._data

  @property
  def readme_file(self) -> PathLike:
    return self._readme_file

  @property
  def lab(self) -> LabConfiguration:
    return self._lab

  async def _check_experiment_configuration(self,
                                            experiment_configuration: ExperimentConfiguration):
    """
    Check the experiment configuration for required fields and validate that resources
    are available in the lab configuration.
    """
    if not self.lab_configuration.has_all_specified_resources(experiment_configuration.resources):
      raise ValueError("Lab configuration does not have all the specified resources.")
    if not experiment_configuration:
      raise ValueError("Experiment configuration is required.")
    if experiment_configuration.directory != os.path.dirname(self.__file__):
      raise ValueError("Experiment directory must be the same as the experiment file.")
    if not experiment_configuration.name:
      raise ValueError("Experiment name is required.")
    if not experiment_configuration.description:
      raise ValueError("Experiment description is required.")
    if experiment_configuration.data_directory not in os.path.dirname(self.__file__):
      raise ValueError("Data directory is required.")

  async def execute(self):
    """
    Execute the experiment
    """
    self.lab_configuration.specify_resources_to_use(selection = self.resources)
    try:
      async with self.lab_configuration as lab: # ensures safety using machines
        self._lab = lab
        await self.initialize()
        self.start_time = datetime.datetime.now()
        await self._execute()
    except KeyboardInterrupt:
      self._lab = None
      await self.pause()
    except Exception as e: # pylint: disable=broad-except
      self._lab = None
      self.logger.error("An error occurred: %s", e)
      print(f"An error occurred: {e}")
      self.errors.append(e)
      self.log_error(error = e)
      self.emailer.send_email(subject = f"Error in {self.name}",
                              message = f"An error occurred in the experiment {self.name}.")
      self._failed = True
      await self.pause()
    finally:
      await self.stop()
      if self.failed:
        print("Experiment failed.")
      else:
        print("Experiment completed.")

  async def initialize(self):
    """
    Start the experiment
    """
    if self._id is None:
      self._id = self._generate_experiment_id()
    if self._id is None:
      self._id = self._generate_experiment_id()
    await self._create_experiment_files()
    await self._start_loggers()

  async def stop(self):
    """
    End the experiment
    """
    self._end_time = datetime.datetime.now()
    self._status = "completed"
    self.logger.info("Experiment %s ended.", self.name)
    self.plr_logger.info("Experiment %s ended.", self.name)
    await self._stop()

  async def get_status(self):
    """
    Get the status of the experiment
    """
    print(f"Experiment Status: {self.status}")
    self.logger.info("Experiment %s status queried; status: %s", self.name, self.status)
    self.plr_logger.info("Experiment %s status queried; status: %s", self.name, self.status)

  async def pause(self):
    """
    Pause the experiment.
    Pause the experiment.
    """
    if not self.paused:
      self._paused = True
      print("Experiment paused.")
      self.logger.info("Experiment %s paused.", self.name)
      self.plr_logger.info("Experiment %s paused.", self.name)
      await self._pause()
    else:
      print("Experiment is already paused.")
    self.intervene(input(self.common_prompt))

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
        confirmation = input("Press Enter to confirm, 'n' to cancel waiting before resuming, or \
                              input another command: ")
        if confirmation == "":
          asyncio.sleep(int(time_to_wait))
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
    self.logger.info("Experiment %s resumed.", self.name)
    self.plr_logger.info("Experiment %s resumed.", self.name)
    await self._resume()

  async def save_state(self):
    """
    Save the experiment state
    """
    with open(self.state_file, "wb") as f:
      f.write(self.state)
    self.logger.info("Experiment %s state saved.", self.name)
    self.plr_logger.info("Experiment %s state saved.", self.name)
    await self._save_state()

  async def load_state(self):
    """
    Load the experiment state
    """
    with open(self.state_file, "rb") as f:
      self._state = f.read()
    self.logger.info("Experiment %s state loaded.", self.name)
    self.plr_logger.info("Experiment %s state loaded.", self.name)
    self._load_state()

  async def abort(self):
    """
    Abort the experiment
    """
    self.logger.info("Experiment %s aborted.", self.name)
    self.plr_logger.info("Experiment %s aborted.", self.name)
    await self._abort()

  async def log_error(self, error: Exception):
    """
    Log error and append it to the errors list.
    """
    self.logger.error("An error occurred: %s", error)
    self.plr_logger.error("An experiment error occurred: %s", error)
    self.errors.append(error)

  async def _create_experiment_files(self):
    """
    Create the experiment files
    """
    await self._create_needed_dirs()
    await self._create_readme()
    await self._create_needed_files()
    await self.load_state()
    await self.create_emailer()

  async def _start_loggers(self):
    """
    Start the loggers
    """
    logging.basicConfig(filename=os.path.join(self.directory, "experiment.log"),
                        level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    self.logger = logging.getLogger(__name__)
    self.logger.info("Experiment %s.", self.name)
    self.logger.info("Experiment Directory: %s", self.directory)
    self.logger.info("Experiment State File: %s", self.state_file)
    self.logger.info("Experiment start time: %s", self.start_time)
    self.logger.info("Experiment ID: %s", self.id)
    self._plr_logger = logging.get_logger("pylabrobot")
    self.plr_logger.info("Experiment %s started.", self.name)

  async def _create_needed_dirs(self,
                directory_names: list[PathLike] = ("data")): # pylint: disable=superfluous-parens
    """
    Create the needed directories
    """
    for directory_name in directory_names:
      if not os.path.exists(os.path.join(self.experiment_directory, directory_name)):
        os.makedirs(os.path.join(self.experiment_directory, directory_name))

  async def _create_needed_files(self):
    """
    Create the needed files
    """
    if not os.path.exists(self.state_file):
      with open(self._experiment_state_file, "wb") as f:
        f.write("{}")
    else:
      print(f"State file already exists at {self.state_file}.")
      print("Please check the file to ensure it is correct.")
      self.intervene(input(self.common_prompt))

  async def _create_readme(self):
    """
    Check if the readme file exists
    """
    self._readme_file = os.path.join(self.experiment_directory, "README.md")
    if not os.path.exists(self._readme_file):
      with open(self._readme_file, "wb") as f:
        f.write(f"# {self.experiment_name}\n\n")
        f.write(f"{self.experiment_description}\n\n")
        f.write("## Experiment Parameters\n\n")
        for key, value in self.experiment_parameters.items():
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
      await self._check_readme_structure()

  async def _check_readme_structure(self):
    """
    Check the structure of the readme file
    """
    with open(self._readme_file, "rb") as f:
      lines = f.readlines()
      if len(lines) < 10:
        print("Readme file is missing information.")
        print("Please check the file to ensure it is correct.")
      if not self._lines_exist_with_headers(lines = lines,
                                            headers = [f"# {self.experiment_name}",
                                                        "## Experiment Parameters",
                                                        "## Experiment Results",
                                                        "## Experiment Errors",
                                                        "## Experiment Starts",
                                                        "## Experiment Pauses",
                                                        "## Experiment Resumes",
                                                        "## Experiment Ends"]):
        raise ValueError("Readme file is missing proper headers.")
      else:
        print("Readme file is correctly structured.")

  async def _lines_exist_with_headers(self, lines: list[str], headers: list[str]) -> bool:
    """
    Check if the lines exist with the headers
    """
    for header in headers:
      if header not in lines:
        return False
    return True

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


class ContinuousExperiment(Experiment, metaclass=ABCMeta):
  """
  Looping Experiment class to execute an experiment which repeatedly runs a cycle of steps until
  a condition is met or the experiment is stopped.
  """

  def __init__(self,
                lab_configuration: LabConfiguration,
                experiment_configuration: ExperimentConfiguration,
                cycle_time: int,
                cycle_count: Optional[int] = None,
                stop_condition: Optional[callable] = None,
                pause_condition: Optional[callable] = None,
                resume_condition: Optional[callable] = None):
    super().__init__(lab_configuration, experiment_configuration)
    super().__init__(lab_configuration, experiment_configuration)
    self.cycle_time = cycle_time
    self.cycle_count = cycle_count
    self.stop_condition = stop_condition if stop_condition else self.stop_condition
    self.pause_condition = pause_condition if pause_condition else self.pause_condition
    self.resume_condition = resume_condition if resume_condition else self.resume_condition

  @abstractmethod
  async def run_cycle(self):
    """
    Run a cycle of the experiment
    """

  @abstractmethod
  async def check_stop_condition(self):
    """
    Check if the stop condition is met
    """

  @abstractmethod
  async def reset(self):
    """
    Reset the experiment
    """

  @abstractmethod
  async def check_pause_condition(self):
    """
    Check if the pause condition is met
    """

  @abstractmethod
  async def check_resume_condition(self):
    """
    Check if the resume condition is met
    """

  @abstractmethod
  async def save_state(self):
    """
    Save the experiment state
    """

  @abstractmethod
  async def load_state(self):
    """
    Load the experiment state
    """

  @abstractmethod
  async def abort(self):
    """
    Abort the experiment
    """

  @abstractmethod
  async def start(self):
    """
    Start the experiment
    """

  @abstractmethod
  async def stop(self):
    """
    End the experiment
    """

  @abstractmethod
  async def pause(self):
    """
    Pause the experiment
    """

  @abstractmethod
  async def resume(self):
    """
    Resume the experiment
    """
