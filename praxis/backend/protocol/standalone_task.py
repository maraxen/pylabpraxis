from abc import ABC, abstractmethod
import asyncio
import datetime
import json
import time
import configparser

class StandaloneTask(ABC):
    def __init__(self, experiment_name, estimated_duration, registry, data_instance, config_file="config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.experiment_name = experiment_name
        self.registry = registry
        self.estimated_duration = estimated_duration
        self.lock = None
        self._data = data_instance
        self.task_id = str(int(time.time()))

    @abstractmethod
    async def _setup(self):
        """
        Acquire necessary resources. This should include acquiring locks on any
        shared resources that the task needs to use.
        """
        pass

    @abstractmethod
    async def _execute(self):
        """
        Perform the main task operation. This is where the core logic of the task
        should be implemented.
        """
        pass

    @abstractmethod
    async def _stop(self):
        """
        Release any acquired resources. This should include releasing locks on
        any shared resources that the task used.
        """
        pass

    def run_task(self):
        """
        Public method to run the task.
        """
        asyncio.run(self._run_task())

    async def _run_task(self):
        """
        Internal method to run the task steps.
        """
        try:
            await self._setup()
            await self._execute()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await self._stop()