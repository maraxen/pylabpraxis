from os import PathLike
import json
import inspect

from pylabrobot.utils.object_parsing import find_subclass

class Configuration:
  """
  Base for configuration objects.

  Attributes:
    configuration_file (PathLike): The path to the configuration json file.
    configuration (dict): The  configuration dictionary.
  """
  def __init__(self, configuration_file: PathLike):
    if not isinstance(configuration_file, PathLike):
      raise ValueError(f"configuration_file must be a PathLike object, \
                        not {type(configuration_file)}")
    if not configuration_file.exists():
      raise FileNotFoundError(f"configuration_file {configuration_file} does not exist")
    if configuration_file.is_dir():
      raise IsADirectoryError(f"configuration_file {configuration_file} is a directory")
    if configuration_file.suffix != ".json":
      raise ValueError(f"configuration_file {configuration_file} must be a .json file")
    self.configuration_file = configuration_file
    with open(self.configuration_file, "rb") as f:
      self.configuration = json.load(f)

  def __getitem__(self, key):
    return self.configuration[key]


class LabConfiguration(Configuration):
  """
  Lab configuration denoting specific set-  up for a lab.

  Attributes:
    configuration_file (PathLike): The path to the configuration json file.
    configuration (dict): The  configuration dictionary.
  """
  def __init__(self, configuration_file: PathLike):
    super().__init__(configuration_file)
    self.configuration = self.configuration["lab_configuration"]
    self.resources = self.configuration["resources"]
    self.unpack_resources()

  def unpack_resources(self):
    """
    Unpacks the resources in the configuration file.
    """
    for resource in self.resources:
      resource_mro = inspect.getmro(resource.__class__)
      for cls in resource_mro:
        if cls.__name__ == "Machine":
          self.machines.append(resource)
          break

      resource_path = resource["resource_path"]
      setattr(self, resource_name, resource_path)




class TaskConfiguration(Configuration):
  """
  Task configuration denoting specific settings for a task.

  Attributes:
    configuration_file (PathLike): The path to the configuration json file.
    configuration (dict): The  configuration dictionary.
  """
  def __init__(self, configuration_file: PathLike):
    super().__init__(configuration_file)
    self.configuration = self.configuration["task_configuration"]



class ExperimentConfiguration(Configuration):
  """
  Exeriment configuration denoting specific settings for an experiment.
  """
  def __init__(self, configuration_file: PathLike):
    super().__init__(configuration_file)
    self.configuration = self.configuration["experiment_configuration"]


