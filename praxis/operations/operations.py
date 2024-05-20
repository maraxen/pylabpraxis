from typing import Optional, List, Awaitable, Union, Callable, Coroutine, Literal
from os import PathLike
from pylabrobot.resources import Resource
import asyncio
import logging
import uuid
import inspect
import functools
import warnings


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
      stop_condition (Optional[Union[Callable[[],bool], bool]]): A callable or bool that indicates
      whether the operations should be executed stop_condition a certain condition is met.
      delay_time (Optional[float]): A float that indicates the delay time between operations,
      between loops, or between checking if a condition to proceed with execution is met.
    """

    def __init__(
        self,
        operations: list[Union[Callable, "Operation", Coroutine]],
        operations_args: Optional[dict] = None,
        parallel: Optional[bool] = False,
        start_condition: Optional[Union[Callable[[], bool], bool]] = None,
        stop_condition: Optional[Union[Callable[[], bool], bool]] = None,
        error_recovery_operations: Optional[Union[Callable, "Operation"]] = None,
        loop: Optional[bool] = False,
        delay_time: Optional[float] = 0.1,
        allow_errors: Optional[bool] = False,
        **kwargs,
    ):
        self.operations = operations
        self.parallel = parallel
        self.start_condition = start_condition
        self.error_recovery_operations = error_recovery_operations
        self.loop = loop
        self.stop_condition = stop_condition
        self.delay_time = delay_time
        self.allow_errors: Optional[bool] = allow_errors

        self._suboperations: Optional[bool] = None
        self._current_state: Optional[uuid.UUID] = None
        self._parent_operation: Optional["Operation"] = None
        self._unique_id = uuid.uuid4()
        self._suboperations_ids: List[uuid.UUID] = []
        self._is_base: bool = False
        self.kwargs = kwargs
        if self.resources is not None:
            self.resources = (
                [self.resources]
                if not isinstance(self.resources, list)
                else self.resources
            )
            for resource in self.resources:
                if not isinstance(resource, Resource):
                    raise OperationError("Invalid resource type.")
                resource.is_available = True
        if not self._is_base:
            if self.parallel and all(
                isinstance(operation, (Callable, Coroutine))
                for operation in self.operations
            ):
                self._is_base = True
            for operation in self.operations:
                if isinstance(operation, Operation):
                    operation._parent_operation = self
                    self._suboperations_ids.append(operation._unique_id)
                if isinstance(operation, (Callable, Coroutine)):
                    if not self.parallel and len(self.operations) > 1:
                        operation = Operation(operations=[operation], **self.kwargs)
                        operation._parent_operation = self
                        operation._is_base = True
                        self._suboperations_ids.append(operation._unique_id)
                    elif self.parallel and not all(
                        isinstance(operation, (Callable, Coroutine))
                        for operation in self.operations
                    ):
                        operation = Operation(operations=[operation], **self.kwargs)
                        operation._is_base = True
                        operation._parent_operation = self
                        self._suboperations_ids.append(operation._unique_id)

    def __len__(self) -> int:
        return len(self.operations)

    @uuid_index_checker
    def __getitem__(self, index: Union[int, uuid.UUID]) -> Union[Callable, "Operation"]:
        return self.operations[index]

    @uuid_index_checker
    def __setitem__(
        self, index: Union[int, uuid.UUID], value: Union[Callable, "Operation"]
    ):
        self.operations[index] = value

    @uuid_index_checker
    def __delitem__(self, index):
        del self.operations[index]

    def __iter__(self) -> iter:
        return iter(self.operations)

    def __slice__(
        self, start: int, stop: int, step: int
    ) -> List[Union[Callable, "Operation"]]:
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

    def __eq__(
        self, other: "Operation"
    ) -> bool:  # TODO: runtime estimate or full attribute?
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
        await self.execute(stop_condition=self._stop_condition)

    def __call__(self, **kwargs):
        self.kwargs = kwargs
        return self

    @property
    def suboperations(self) -> bool:
        if self._suboperations is None:
            self._suboperations = (
                len(isinstance(operation, Operation) for operation in self.operations)
                > 1
            )
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
        return self._is_base

    @property
    def all_tasks(self) -> List[asyncio.Task]:
        return asyncio.all_tasks()

    @property
    def current_task(self) -> asyncio.Task:
        return asyncio.current_task()

    async def execute(
        self,
        stop_condition: Optional[Union[Callable[[], bool], bool]] = None,
        loop: Optional[bool] = None,
    ):
        """
        Execute the operations. If stop_condition is not None, the operations will be executed
        stop_condition the condition is met. Includes built in handling for errors, pausing, resuming,
        stopping, and state saving. Performance: If stop_condition is None, operations will be  executed
        once or repeatedly if loop is True. If stop_condition is a callable, the operations will be
        executed stop_condition the callable returns True. If stop_condition is a bool, the operations
        will be executed stop_condition the bool is True.

        Args:
          stop_condition (Optional[Union[Callable[[],bool], bool]]): A callable or bool that indicates
          whether the operations should be executed stop_condition a certain condition is met. If
          stop_condition is None, the Operation _stop_condition attribute will be used. This allows for
          at-execution changes of stop_condition from standard library operations if needed.
          loop (Optional[bool]): A boolean that indicates whether the operations should be executed
          repeatedly. If loop is None, the Operation _loop attribute will be used. This allows for
          at-execution changes of loop from standard library operations if needed.

        """
        if stop_condition is not None:
            self.stop_condition = stop_condition
        if loop is not None:
            self.loop = loop
        try:
            await self._execute(stop_condition=self.stop_condition)
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

    async def _execute(self, stop_condition: Optional[Union[Callable[[], bool], bool]]):
        """
        Helper function to determine whether stop_condition condition has been met or if stop_condition.
        """
        logger.info("Executing operation:", extra={"operation id": self.unique_id})
        if stop_condition is None:
            await self._process_execution(stop_condition=stop_condition)
        elif isinstance(stop_condition, (Callable, bool)):
            while not stop_condition:
                await self._process_execution(stop_condition=stop_condition)
                self._current_state = None
            await self.stop()
        else:
            raise OperationError("Invalid value for stop_condition parameter.")

    async def _process_execution(
        self,
        stop_condition: Optional[Union[Callable[[], bool], bool]] = None,
        source: Optional[str] = None,
    ):
        """
        Helper function to process the execution of the operations. Ensures that the operations are
        executed in the correct order and manner.

        Args:
          stop_condition (Optional[Union[Callable[[],bool], bool]]): A callable or bool that indicates
          whether the operations should be executed stop_condition a certain condition is met.
          source (Optional[str]): A string that indicates the source of the call to
            _process_execution.
        """
        if self.is_base:
            await self._base_operation_execute()
            return
        if source is not None:
            if source != "conditional" and self.start_condition is not None:
                await self._conditional_execute(stop_condition=stop_condition)
                return
            elif source != "loop" and self.loop:
                await self._execute_continuously(stop_condition=stop_condition)
                return
        if self.parallel:
            if not self.is_mother:
                await self._parent_operation.set_current_state(self.unique_id)
            await self._parallel_execute(
                stop_condition=stop_condition, allow_errors=self.allow_errors
            )
        else:
            if not self.is_mother:
                await self._parent_operation.set_current_state(self.unique_id)
            await self._sequential_execute(stop_condition=stop_condition)

    async def _base_operation_execute(self):
        """
        Helper function to execute the operations if the operation is a base operation.
        This is where callables are actually executed. If the operation is not a base operation, the
        function will process stop_condition it reaches the base operation in it's suboperations.
        """
        if self.parallel:
            await self._base_parallel_execute(allow_errors=self.allow_errors)
            return
        for operation in self.operations:
            if isinstance(
                operation, Coroutine
            ):  # if loaded from coroutine which should already have args
                await operation
                return
            else:
                argspec = inspect.getfullargspec(operation)  # get argspec of operation
                for resource in self.resources:
                    for (
                        arg
                    ) in argspec.annotations:  # check if any of the args are resources
                        for class_type in argspec.annotations.get(
                            arg
                        ).__args__:  # TODO: make more robust
                            if isinstance(resource, class_type):
                                self.kwargs[arg] = resource
                                break
                if argspec.varkw:
                    some_args = self.kwargs
                else:
                    some_args = dict(
                        (k, self.kwargs[k]) for k in argspec.args if k in self.kwargs
                    )
                if isinstance(operation, Awaitable):
                    await operation(**some_args)
                    return
                else:
                    operation(**some_args)
                    return

    async def _conditional_execute(
        self, stop_condition: Optional[Union[Callable[[], bool], bool]] = None
    ):
        while not self.start_condition():
            await asyncio.sleep(delay=self.delay_time)
        await self._process_execution(stop_condition=stop_condition)

    async def _base_parallel_execute(self, allow_errors: Optional[bool] = False):
        """
        Helper function to execute the operations if the operation is a base operation and parallel.
        """
        if allow_errors:
            await asyncio.gather(*self.operations)
        else:
            tasks = []
            async with asyncio.TaskGroup() as tg:
                for operation in self.operations:
                    tasks.append(tg.create_task(operation))

    async def _parallel_execute(
        self,
        stop_condition: Optional[Union[Callable[[], bool], bool]] = None,
        allow_errors: Optional[bool] = False,
    ):
        """
        Helper function to execute the operations in parallel. If allow_errors is True, the operations
        will be executed even if an error occurs in one. If allow_errors is False, the operations will
        be executed stop_condition an error occurs in one or all operations are completed.
        """
        if allow_errors:
            await asyncio.gather(
                *[
                    operation.execute(stop_condition=stop_condition)
                    for operation in self.operations
                ]
            )
        else:
            tasks = []
            async with asyncio.TaskGroup() as tg:
                for operation in self.operations:
                    tasks.append(
                        tg.create_task(operation.execute(stop_condition=stop_condition))
                    )

    async def _sequential_execute(
        self, stop_condition: Optional[Union[Callable[[], bool], bool]] = None
    ):
        for operation in self.operations[self.current_state :]:
            await operation.execute(stop_condition=stop_condition)

    async def _execute_continuously(
        self, stop_condition: Optional[Union[Callable[[], bool], bool]] = None
    ):
        await self._process_execution(stop_condition=stop_condition, source="loop")
        await asyncio.sleep(delay=self.delay_time)

    async def _error_recovery(self, error: "OperationError"):
        for operation in self.operations:
            await operation.error_recovery(error=error)

    async def error_recovery(self, error: "OperationError" = None):
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
        for operation in getattr(
            self, special_operation_key, [None]
        ):  # TODO: Add error handling
            if operation is None:
                continue
            if not hasattr(self._parent_operation, special_operation_key):
                self._parent_operation.pause_operations = []
            self._parent_operation.pause_operations.append(operation)

    async def resume(self):
        """
        Resume the operation. If the operation is a suboperation, the parent operation will also be
        resumed.
        """
        await self.manage(command="resume")
        await self.execute()

    async def stop(self):
        """
        Stop the operation and perform any stop operations.
        """
        await self.manage(command="stop")

    async def save(self):
        """
        Save the current operation in it's current state. If the operation is a suboperation, the parent
        operation will also be saved.
        """
        await self.manage(command="save")
        async with open(f"{self.unique_id}.json", "wb") as f:
            f.write(self.__dict__)

    @classmethod
    async def load_from_json(cls, file_path: PathLike):
        """
        Load an operation from a JSON file.

        Args:
          file_path (PathLike): The path to the JSON file.
        """
        async with open(file_path, "rb") as f:
            operation = f.read()
        return operation

    async def reset(self):
        """
        Reset the operation to it's initial state.
        """
        self._current_state = None
        await self.manage(command="reset")

    async def _manage(self, command: str):
        """
        Manage the operation.
        """
        match command:
            case "reset":
                await self.reset()
            case "pause":
                await self.pause()
            case "resume":
                await self.resume()
            case "stop":
                await self.stop()
            case "save":
                await self.save()
            case "load":
                await self.load()
            case "abort":
                await self.abort()
            case _:
                raise OperationError("Invalid command.")

    async def manage(
        self,
        command: Literal[
            "reset", "pause", "resume", "stop", "save", "load", "abort", "wait"
        ],
    ):
        """
        Check if the operation is parallel and if so issue the command to the parallel operations.
        """
        if not self.is_mother:
            await self._assign_operation_to_parent("{command}_operations")
            await self._parent_operation.manage(command=command)
        else:
            if hasattr(self, "{command}_operations"):
                if not self.parallel:
                    for operation in self.getattr("{command}_operations"):
                        if not isinstance(operation, Operation):
                            operation = Operation(
                                operations=[operation],
                                resources=self.resources,
                                **self.kwargs,
                            )
                        await operation.execute()
                    else:
                        tasks = []
                        async with asyncio.TaskGroup() as tg:
                            for operation in self.operations:
                                if not isinstance(operation, Operation):
                                    operation = Operation(
                                        operations=[operation],
                                        resources=self.resources,
                                        **self.kwargs,
                                    )
                                tasks.append(
                                    tg.create_task(operation.manage(command=command))
                                )

    async def abort(self):
        """
        Abort the operation.
        """
        await self.manage(command="abort")


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
