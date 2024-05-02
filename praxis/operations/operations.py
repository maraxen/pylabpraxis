from typing import Optional, List, Awaitable, Union, Callable, Coroutine
from pylabrobot import Resource # pyright: ignore
import asyncio
import logging
import uuid
import inspect
import functools

def uuid_index_checker(func):
  @functools.wraps(func)
  def wrapper(self, index, *args, **kwargs):
    if isinstance(index, uuid.UUID):
      index = self.suboperation_ids.index(index)
    return func(self, index, *args, **kwargs)
  return wrapper

logger = logging.getLogger("pylabrobot")

class Operation:
  """
  Operation is used to define operations that can be executed by PyLabRobot resources.

  Mother operations should be called with asyncio.run(mother_operation.execute()) to execute the
  operations.

  Args:
    operations (List[Union[Callable, "Operation"]]): A list of operations to be executed.
    resources (Union[Resource, List[Resource]]): A list of resources that the operations depend on.
    parallel (Optional[bool]): A boolean that indicates whether the operations should be executed in
    parallel.
    condition (Optional[Callable[[], bool]]): A callable that indicates whether the operations
    should be executed.
    error_recovery_operations (Optional[Union[Callable, "Operation"]]): A list of operations to be
    executed in case of an error.
    loop (Optional[bool]): A boolean that indicates whether the operations should be executed
    repeatedly.
    until (Optional[Union[Callable[[],bool], bool]]): A callable or bool that indicates whether the
    operations should be executed until a certain condition is met.
    delay_time (Optional[float]): A float that indicates the delay time between operations,
    between loops, or between checking if a condition to proceed with execution is met.
  """
  def __init__(self,
              operations: list[Union[Callable, "Operation", Coroutine]],
              resources: Union[Resource, list[Resource]],
              parallel: Optional[bool]=False,
              condition: Optional[Callable[[], bool]]=None,
              error_recovery_operations: Optional[Union[Callable, "Operation"]]=None,
              loop: Optional[bool]=False,
              until: Optional[Union[Callable[[],bool], bool]]=None,
              delay_time: Optional[float]=0.1,
              allow_errors: Optional[bool]=False,
              **kwargs):
    self.operations = operations
    self.resources = resources
    self.parallel = parallel
    self.condition = condition
    self.error_recovery_operations = error_recovery_operations
    self.loop = loop
    self.until = until
    self.delay_time = delay_time
    self.allow_errors: Optional[bool] = allow_errors
    self._suboperations: Optional[bool] = None
    self._current_state: Optional[uuid.UUID] = None
    self._parent_operation: Optional["Operation"] = None
    self._unique_id = uuid.uuid4()
    self._suboperations_ids: List[uuid.UUID] = []
    self.kwargs = kwargs
    if self.resources is not None:
      self.resources = [self.resources] if not isinstance(self.resources, list) else self.resources
      for resource in self.resources:
        if not isinstance(resource, Resource):
          raise OperationError("Invalid resource type.")
        resource.is_available = True
    for operation in self.operations:
      if isinstance(operation, Operation):
        operation._parent_operation = self
        self._suboperations_ids.append(operation._unique_id)
      if isinstance(operation, (Callable, Coroutine)):
        if not self.parallel and len(self.operations) > 1:
          operation = Operation(operations=[operation], resources=self.resources, **self.kwargs)
          operation._parent_operation = self
          self._suboperations_ids.append(operation._unique_id)
        elif self.parallel and not all(isinstance(operation, (Callable, Coroutine))
                                        for operation in self.operations):
          operation = Operation(operations=[operation], resources=self.resources, **self.kwargs)
          operation._parent_operation = self
          self._suboperations_ids.append(operation._unique_id)

  def __len__(self) -> int:
    return len(self.operations)

  @uuid_index_checker
  def __getitem__(self, index: Union[int, uuid.UUID]) -> Union[Callable, "Operation"]:
    return self.operations[index]

  @uuid_index_checker
  def __setitem__(self, index: Union[int, uuid.UUID], value: Union[Callable, "Operation"]):
    self.operations[index] = value

  @uuid_index_checker
  def __delitem__(self, index):
    del self.operations[index]

  def __iter__(self) -> iter:
    return iter(self.operations)

  def __slice__(self, start: int, stop: int, step: int) -> List[Union[Callable, "Operation"]]:
    return self.operations[start:stop:step]

  def __next__(self) -> Union[Callable, "Operation"]:
    return next(self.operations)

  def __reversed__(self) -> List[Union[Callable, "Operation"]]:
    return reversed(self.operations)

  def __contains__(self, item) -> bool:
    return item in self.operations

  def __add__(self, other: Union[Callable, "Operation"]) -> "Operation":
    return self.operations + other

  def __iadd__(self, other: Union[Callable, "Operation"]) -> "Operation":
    self.operations += other
    return self

  def __eq__(self, other: "Operation") -> bool:  # TODO: runtime estimate or full attribute?
    return self.operations == other.operations

  def __ne__(self, other: "Operation") -> bool:
    return self.operations != other.operations

  def __lt__(self, other: "Operation") -> bool:
    return len(self.operations) < len(other.operations)

  def __le__(self, other: "Operation") -> bool:
    return len(self.operations) <= len(other.operations)

  def __gt__(self, other: "Operation") -> bool:
    return len(self.operations) > len(other.operations)

  def __ge__(self, other: "Operation") -> bool:
    return len(self.operations) >= len(other.operations)

  async def __await__(self):
    await self.execute(until=self._until)

  def __call__(self, **kwargs):
    self.kwargs = kwargs
    return self

  @property
  def until(self) -> Optional[Union[Callable[[],bool], bool]]:
    return self._until

  @property
  def suboperations(self) -> bool:
    if self._suboperations is None:
      self._suboperations = len(isinstance(operation, Operation) \
                                for operation in self.operations) > 1
    return self._suboperations

  @property
  def current_state(self) -> int:
    if self._current_state is None:
      return 0
    if self.parallel:
      return self.suboperations_ids
    self._current_state = self._suboperations_ids.index(self._current_state)
    return self._current_state

  @property
  def parent_operation(self) -> "Operation":
    return self._parent_operation

  @property
  def unique_id(self) -> uuid.UUID:
    return self._unique_id

  @property
  def suboperations_ids(self) -> List[uuid.UUID]:
    return self._suboperations_ids

  @property
  def is_mother(self) -> bool:
    return self._parent_operation is None

  @property
  def is_base(self) -> bool:
    if self.parallel:
      return all(isinstance(operation, (Callable, Coroutine)) for operation in self.operations)
    else:
      return len(self.operations) == 1 and isinstance(self.operations[0], (Callable, Coroutine))

  @property
  def all_tasks(self) -> List[asyncio.Task]:
    return asyncio.all_tasks()

  @property
  def current_task(self) -> asyncio.Task:
    return asyncio.current_task()

  async def execute(self,
                    until: Optional[Union[Callable[[],bool], bool]]=None,
                    loop: Optional[bool]=None):
    """
    Execute the operations. If until is not None, the operations will be executed until the
    condition is met. Includes built in handling for errors, pausing, resuming, stopping, and
    state saving. Performance: If until is None, operations will be  executed once or repeatedly if
    loop is True. If until is a callable, the operations will be executed until the callable returns
    True. If until is a bool, the operations will be executed until the bool is True.

    Args:
      until (Optional[Union[Callable[[],bool], bool]]): A callable or bool that indicates whether
      the operations should be executed until a certain condition is met. If until is None, the
      Operation _until attribute will be used. This allows for at-execution changes of until from
      standard library operations if needed.
      loop (Optional[bool]): A boolean that indicates whether the operations should be executed
      repeatedly. If loop is None, the Operation _loop attribute will be used. This allows for
      at-execution changes of loop from standard library operations if needed.
      overide (bool):

    """
    if until is not None:
      self._until = until
    if loop is not None:
      self.loop = loop
    try:
      await self._execute(until=self.until)
    except OperationError as e:
      await self._error_recovery(error=e)
      raise e
    except KeyboardInterrupt:
      await self.pause()
    except asyncio.CancelledError:
      await self.abort()
    finally:
      await self.save()
      await self.stop()

  async def _execute(self, until: Optional[Union[Callable[[],bool], bool]]):
    """
    Helper function to determine whether until condition has been met or if until.
    """
    logger.info("Executing operation:", extra={"operation id": self.unique_id})
    match until:
      case callable(until):
        while not until():
          await self._execute_continuously()
          self._current_state = None
        await self.stop()
      case bool():
        while not until:
          await self._execute_continuously()
          self._current_state = None
        await self.stop()
      case None:
        await self._process_execution(until=until)
      case _:
        raise OperationError("Invalid value for until parameter.")
    pass

  async def _process_execution(self,
                              until: Optional[Union[Callable[[],bool], bool]]=None,
                              source: Optional[str]=None):
    """
    Helper function to process the execution of the operations. Ensures that the operations are
    executed in the correct order and manner.

    Args:
      until (Optional[Union[Callable[[],bool], bool]]): A callable or bool that indicates whether
        the operations should be executed until a certain condition is met.
      source (Optional[str]): A string that indicates the source of the call to
        _process_execution.
    """
    if self.is_base:
      self._base_operation_execute()
      return
    if source is not None:
      if source != "conditional" and self.condition is not None:
        await self._conditional_execute(until=until)
        return
      elif source != "loop" and self.loop:
        await self._execute_continuously(until=until)
        return
    if self.parallel:
      if not self.is_mother:
        self._parent_operation.set_current_state(self.unique_id)
      await self._parallel_execute(until=until, allow_errors=self.allow_errors)
    else:
      if not self.is_mother:
        self._parent_operation.set_current_state(self.unique_id)
      await self._sequential_execute(until=until)

  async def _base_operation_execute(self):
    """
    Helper function to execute the operations if the operation is a base operation.
    This is where callables are actually executed. If the operation is not a base operation, the
    function will process until it reaches the base operation in it's suboperations.
    """
    for operation in self.operations:
      if isinstance(operation, Coroutine): # if loaded from coroutine which should already have args
        await operation
      else:
        argspec = inspect.getfullargspec(operation) # get argspec of operation
        for resource in self.resources:
          for arg in argspec.annotations: # check if any of the args are resources
            for class_type in argspec.annotations.get(arg).__args__: # TODO: make more robust
              if isinstance(resource, class_type):
                self.kwargs[arg] = resource
                break
        if argspec.varkw:
          some_args = self.kwargs
        else:
          some_args = dict((k,self.kwargs[k]) for k in argspec.args if k in self.kwargs)
        if isinstance(operation, Awaitable):
          await operation(**some_args)
        else:
          operation(**some_args)

  async def _conditional_execute(self, until: Optional[Union[Callable[[],bool], bool]]=None):
    while not self.condition():
      await asyncio.sleep(delay=self.delay_time)
    await self._process_execution(until=until)

  async def _parallel_execute(self,
                              until: Optional[Union[Callable[[],bool], bool]]=None,
                              allow_errors: Optional[bool]=False):
    """
    Helper function to execute the operations in parallel. If allow_errors is True, the operations
    will be executed even if an error occurs in one. If allow_errors is False, the operations will
    be executed until an error occurs in one or all operations are completed.
    """
    if allow_errors:
      await asyncio.gather(*[operation.execute(until=until) for operation in self.operations])
    else:
      tasks =[]
      async with asyncio.TaskGroup() as tg:
        for operation in self.operations:
          tasks.append(tg.create_task(operation.execute(until=until)))

  async def _sequential_execute(self, until: Optional[Union[Callable[[],bool], bool]]=None):
    for operation in self.operations[self.current_state:]:
      await operation.execute(until=until)

  async def _execute_continuously(self, until: Optional[Union[Callable[[],bool], bool]]=None):
    await self._process_execution(until=until, source="loop")
    await asyncio.sleep(delay=self.delay_time)

  async def _error_recovery(self, error: "OperationError"):
    for operation in self.operations:
      await operation.error_recovery(error=error)

  async def error_recovery(self, error: "OperationError"=None):
    for error_recovery_operation in self.error_recovery_operations:
      await error_recovery_operation.execute(error=error)

  async def set_current_state(self, state: uuid.UUID):
    self._current_state = state

  async def check(self):
    pass

  async def pause(self):
    """
    Pause the operations. If the operation is a suboperation, the parent operation will also be
    paused. If the operation is the mother operation, the pause will be called on the current
    suboperation. The user will be prompted to continue. If the operation is the mother operation
    and has pause_operations, the pause_operations will be executed before the user is prompted to
    continue. If the operation is the mother operation and has resume_operations, the
    resume_operations will be executed after the user is prompted to continue.

    """
    if not self.is_mother:
      await self._assign_operation_to_parent("pause_operations")
      await self._assign_operation_to_parent("resume_operations")
      await self._parent_operation.pause()
    else:
      if hasattr(self, "pause_operations"):
        for operation in self.pause_operations:
          await operation.execute()
      input("Press enter to continue...")
      await self.resume()

  async def _assign_operation_to_parent(self, special_operation_key: str):
    for operation in getattr(self, special_operation_key, [None]):  # TODO: Add error handling
      if operation is None:
        continue
      if not hasattr(self._parent_operation, special_operation_key):
        self._parent_operation.pause_operations = []
      self._parent_operation.pause_operations.append(operation)

  async def resume(self):
    if not self.is_mother:
      raise OperationError("Cannot resume from suboperation.")
    if hasattr(self, "resume_operations"):
      for operation in self.resume_operations:
        await operation.execute()
    await self.execute()

  async def _safe_parallel_stop(self):
    if not self.parallel:
      raise OperationError("Operation is not parallel.")
    tasks = []
    async with asyncio.TaskGroup() as tg:
      for operation in self.operations:
        tasks.append(tg.create_task(operation.stop()))

  async def stop(self):
    if self.is_mother and self.parallel:
      await self._safe_parallel_stop()
    if self.parallel:
      tasks = []
      async with asyncio.TaskGroup() as tg:
        for operation in self.operations:
          tasks.append(tg.create_task(operation.stop()))
    if hasattr(self, "stop_operations"):
      for operation in self.stop_operations:
        await operation.execute()
    if not self.is_mother:
      await self._parent_operation.stop()

  async def reset(self):
    pass

  async def abort(self):
    pass

  async def wait(self):
    pass

  async def save(self):
    """
    Save the current state of the operation. If the operation is a suboperation, the parent
    operation will also be saved. If the operation is the mother operation, the save will be called
    on the current suboperation. If the operation is the mother operation and has save_operations,
    the save_operations will be executed before the user is prompted to continue. If the operation
    is the mother operation and has resume_operations, the resume_operations will be executed after
    the user is prompted to continue.
    """

  @classmethod
  async def load(cls):
    pass

class OperationManager:
  """
  OperationManager is a class that can be used to manage operations.
  """

class OperationError(Exception):
  """
  OperationError is an exception class that can be used to handle errors in operations.
  """
  def __init__(self, message: str):
    self.message = message
    super().__init__(self.message)

  def __str__(self):
    return f"{self.message}"
