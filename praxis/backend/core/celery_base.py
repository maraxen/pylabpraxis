from __future__ import annotations

from typing import TYPE_CHECKING

from celery import Task

if TYPE_CHECKING:
  from praxis.backend.core.container import Container


class PraxisTask(Task):

  """A custom Celery Task class for Praxis that integrates with the dependency injection container."""

  @property
  def container(self) -> Container:
    """Returns the dependency injection container."""
    # The container is attached to the app instance.
    return self.app.container

  def __call__(self, *args, **kwargs):
    """Overrides the default `__call__` method to provide a DI container scope for each task execution."""
    with self.container.db_session.override(self.container.db_session_factory()):
      return super().__call__(*args, **kwargs)
