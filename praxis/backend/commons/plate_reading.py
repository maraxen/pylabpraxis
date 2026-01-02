import datetime

from praxis.protocol.standalone_task import (
  StandaloneTask,
)  # Assuming it's in the same protocol submodule


class PlateReaderTask(StandaloneTask):
  def __init__(
    self,
    experiment_name,
    plate_name,
    measurement_type,
    wells,
    estimated_duration,
    registry,
    data_instance,
    config_file="config.ini",
  ):
    super().__init__(
      experiment_name, estimated_duration, registry, data_instance, config_file,
    )
    self.plate_name = plate_name
    self.measurement_type = measurement_type
    self.wells = wells

  async def _setup(self):
    # Get the estimated next plate reader use time for the main experiment
    next_use = self.registry.get_next_plate_reader_use(self.experiment_name)

    # Calculate the earliest time this task can finish
    earliest_finish_time = datetime.datetime.now() + datetime.timedelta(
      seconds=self.estimated_duration,
    )

    # Check if there's a conflict (with a buffer)
    buffer_time = self.config.get("plate_reading").get("buffer_time")
    if buffer_time is None:
      buffer_time = datetime.timedelta(minutes=5)  # 5-minute buffer
    if next_use and earliest_finish_time + buffer_time > next_use:
      msg = "Plate reader will be needed by the main experiment soon."
      raise Exception(msg)

    # Acquire the plate reader lock
    if not self.registry.acquire_lock(
      "plate_reader",
      self.experiment_name,
      self.task_accession_id,
      lock_timeout=self.estimated_duration,
      acquire_timeout=10,
    ):
      msg = "Failed to acquire lock on plate reader."
      raise Exception(msg)

  async def _execute(self):
    # Simulate performing plate reader operation
    await asyncio.sleep(self.estimated_duration)  # Simulate time taken for operation

    # Insert usage data into the database
    try:
      cursor = self._data.conn.cursor()
      cursor.execute(
        """
                INSERT INTO plate_reader_usage (experiment_name, plate_name, measurement_type, wells, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """,
        (
          self.experiment_name,
          self.plate_name,
          self.measurement_type,
          json.dumps(self.wells),
          datetime.datetime.now(),
        ),
      )
      self._data.conn.commit()
    except Exception:
      pass

  async def _stop(self):
    # Release the plate reader lock
    self.registry.release_lock(
      "plate_reader", self.experiment_name, self.task_accession_id,
    )
