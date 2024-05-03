from praxis.configure import LabConfiguration
from abc import ABC, ABCMeta, abstractmethod
from typing import Optional
import os
from os import PathLike
import datetime
import logging
import asyncio

class Experiment(ABC):
  """
  Experiment class to execute the experiment and store the results.
  """
  def __init__(self,
                lab: LabConfiguration,
                experiment_directory: PathLike,
                experiment_parameters: dict,
                experiment_name: str,
                experiment_description: str,
                data_directory: Optional[PathLike] = None):
    self.lab = lab
    self.experiment_directory = experiment_directory
    self.experiment_parameters = experiment_parameters
    self.experiment_name = experiment_name
    self.experiment_description = experiment_description
    self.data_directory = data_directory
    self._experiment_id = None
    self._experiment_start_time = None
    self._experiment_end_time = None
    self._experiment_status = None
    self._experiment_results = None
    self._experiment_errors = None
    self._experiment_logs = None
    self._experiment_state = None
    self._experiment_state_file = None
    self._experiment_data = None
    self._readme_file = None
    self._experiment_start_time = datetime.datetime.now()
    self._plr_logger = None
    self._available_commands = {
      "abort": "Abort the experiment",
      "pause": "Pause the experiment",
      "resume": "Resume the experiment",
      "save": "Save the experiment state",
      "load": "Load the experiment state",
      "status": "Get the status of the experiment",
      "help": "Get a list of available commands"
    }


  async def start(self):
    """
    Start the experiment
    """
    await self._create_experiment_files()
    await self._start_loggers()
    await self._run_experiment()

  @abstractmethod
  async def stop(self):
    """
    End the experiment
    """

  @abstractmethod
  async def status(self):
    """
    Get the status of the experiment
    """

  @abstractmethod
  async def pause(self):
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
      case "resume":
        await self.resume()
      case "save":
        await self.save_state()
      case "load":
        await self.load_state()
      case "status":
        await self.status()
      case "help":
        print("Available commands:")
        for command, description in self._available_commands.items():
          print(f"{command}: {description}")
        new_input = input("Enter a command: ")
        await self.intervene(new_input)
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
          new_input = input("Enter a new command or press enter to resume: ")
          if new_input == "":
            await self.resume()
          else:
            await self.intervene(new_input)
        else:
          await self.intervene(confirmation)
      case _:
        await self._intervene(user_input)


  async def _intervene(self, user_input: str):
    """
    Helper function for interventions in the experiment. Please override this function in the
    subclass if you want to add more interventions.
    """
    print(f"Command {user_input} not recognized.")
    new_input = input("Enter a new command or press enter to resume experiment:")
    if new_input == "":
      await self.resume()
    else:
      await self.intervene(new_input)

  @abstractmethod
  async def resume(self):
    """
    Resume the experiment
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

  async def _create_experiment_files(self):
    """
    Create the experiment files
    """
    await self._create_needed_dirs()
    await self._create_readme()
    await self._create_needed_files()
    self._experiment_logs = os.path.join(self.experiment_directory, "logs")
    self._experiment_state = os.path.join(self.experiment_directory, "state")
    self._experiment_data = os.path.join(self.experiment_directory, "data")
    self._experiment_state_file = os.path.join(self._experiment_state, "state.json")

  async def _start_loggers(self):
    """
    Start the loggers
    """
    logging.basicConfig(filename=os.path.join(self._experiment_logs, "experiment.log"),
                        level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    self.logger = logging.getLogger(__name__)
    self.logger.info("Experiment %s.", self.experiment_name)
    self.logger.info("Experiment Directory: %s", self.experiment_directory)
    self.logger.info("Experiment State File: %s", self._experiment_state_file)
    self.logger.info("Experiment start time: %s", self._experiment_start_time)
    self.logger.info("Experiment ID: %s", self._experiment_id)
    logging.get_logger("pylabrobot").info("Experiment %s started.", self.experiment_name)

  async def _create_needed_dirs(self, directory_names: list[PathLike] = ("logs", "state", "data")):
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
    if not os.path.exists(self._experiment_state_file):
      with open(self._experiment_state_file, "wb") as f:
        f.write("{}")
    else:
      print(f"State file already exists at {self._experiment_state_file}.")
      print("Please check the file to ensure it is correct.")

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
      print("Please check the file to ensure it is correct.")


class ContinuousExperiment(Experiment, metaclass=ABCMeta):
  """
  Looping Experiment class to execute an experiment which repeatedly runs a cycle of steps until
  a condition is met or the experiment is stopped.
  """

  def __init__(self,
                lab: LabConfiguration,
                experiment_directory: PathLike,
                experiment_parameters: dict,
                experiment_name: str,
                experiment_description: str,
                cycle_time: int,
                cycle_count: Optional[int] = None,
                stop_condition: Optional[callable] = None,
                pause_condition: Optional[callable] = None,
                resume_condition: Optional[callable] = None):
    super().__init__(lab,
                      experiment_directory,
                      experiment_parameters,
                      experiment_name,
                      experiment_description)
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
  async def status(self):
    """
    Get the status of the experiment
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
