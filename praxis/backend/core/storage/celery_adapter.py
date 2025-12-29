"""Celery adapter implementing the TaskQueue protocol.

Wraps the existing Celery application to conform to the TaskQueue protocol,
enabling interchangeable usage with the in-memory task queue.
"""

import asyncio
import logging
from typing import Any

from praxis.backend.core.storage.protocols import TaskQueue

logger = logging.getLogger(__name__)


class CeleryTaskQueue:
    """Celery-backed task queue.

    Wraps the Celery application to conform to the TaskQueue protocol.
    Uses asyncio to bridge sync Celery operations.
    """

    def __init__(self, celery_app: Any | None = None) -> None:
        """Initialize the Celery task queue.

        Args:
            celery_app: The Celery application instance. If None, will import
                the global celery_app from praxis.backend.core.celery.
        """
        self._celery_app = celery_app

    def _get_app(self) -> Any:
        """Get the Celery app, importing if necessary."""
        if self._celery_app is None:
            from praxis.backend.core.celery import celery_app
            self._celery_app = celery_app
        return self._celery_app

    async def send_task(
        self,
        name: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> str:
        """Dispatch a task for async execution.

        Args:
            name: The registered Celery task name.
            args: Positional arguments for the task.
            kwargs: Keyword arguments for the task.

        Returns:
            The Celery task ID.
        """
        app = self._get_app()

        # Run in thread pool since Celery operations are sync
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: app.send_task(
                name,
                args=args or [],
                kwargs=kwargs or {},
            ),
        )
        logger.debug("Sent Celery task: %s (%s)", name, result.id)
        return result.id

    async def get_result(
        self,
        task_id: str,
        timeout: float | None = None,
    ) -> Any:
        """Wait for and retrieve a task result.

        Args:
            task_id: The Celery task ID.
            timeout: Maximum seconds to wait.

        Returns:
            The task result.

        Raises:
            TimeoutError: If timeout is reached.
            Exception: If the task failed.
        """
        app = self._get_app()
        result = app.AsyncResult(task_id)

        loop = asyncio.get_event_loop()

        # Poll for result with timeout
        start_time = asyncio.get_event_loop().time()
        while True:
            ready = await loop.run_in_executor(None, lambda: result.ready())
            if ready:
                # Get the result (may raise if task failed)
                return await loop.run_in_executor(None, result.get)

            if timeout is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= timeout:
                    msg = f"Task {task_id} did not complete within {timeout}s"
                    raise TimeoutError(msg)

            await asyncio.sleep(0.5)  # Poll interval

    async def revoke(self, task_id: str) -> None:
        """Cancel a pending or running task.

        Args:
            task_id: The task ID to cancel.
        """
        app = self._get_app()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: app.control.revoke(task_id, terminate=True),
        )
        logger.info("Revoked Celery task: %s", task_id)

    async def close(self) -> None:
        """Close the Celery connection.

        Note: This doesn't actually close Celery as it's typically a global
        singleton. Just logs for protocol compliance.
        """
        logger.info("CeleryTaskQueue close called (no-op for global Celery)")
