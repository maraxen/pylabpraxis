from praxis.configure import LabConfiguration
from abc import ABC, ABCMeta, abstractmethod
from typing import Optional


class Experiment(ABC):
  """
  Experiment class to execute the experiment and store the results.
  """
  def __init__(self,
                lab: LabConfiguration,
                experiment_parameters: dict,
                experiment_name: str,
                experiment_description: str):
    self.lab = lab
    self.experiment_parameters = experiment_parameters
    self.experiment_name = experiment_name
    self.experiment_description = experiment_description
    self._experiment_id = None
    self._experiment_start_time = None
    self._experiment_end_time = None
    self._experiment_status = None
    self._experiment_results = None
    self._experiment_errors = None

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


class ContinuousExperiment(Experiment, metaclass=ABCMeta):
  """
  Looping Experiment class to execute an experiment which repeatedly runs a cycle of steps until
  a condition is met or the experiment is stopped.
  """

  def __init__(self,
                lab: LabConfiguration,
                experiment_parameters: dict,
                experiment_name: str,
                experiment_description: str,
                cycle_time: int,
                cycle_count: Optional[int] = None,
                stop_condition: Optional[callable] = None,
                pause_condition: Optional[callable] = None,
                resume_condition: Optional[callable] = None):
    super().__init__(lab, experiment_parameters, experiment_name, experiment_description)
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
