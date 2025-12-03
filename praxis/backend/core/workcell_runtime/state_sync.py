"""State synchronization functionality for WorkcellRuntime."""

import asyncio
import contextlib
import datetime
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from praxis.backend.models.pydantic_internals.workcell import WorkcellCreate
from praxis.backend.services.workcell import WorkcellService
from praxis.backend.utils.errors import WorkcellRuntimeError
from praxis.backend.utils.logging import get_logger

if TYPE_CHECKING:
  from praxis.backend.core.protocols.workcell import IWorkcell

logger = get_logger(__name__)


class StateSyncMixin:

  """Mixin providing state synchronization capabilities for WorkcellRuntime."""

  db_session_factory: async_sessionmaker[AsyncSession]
  workcell_svc: WorkcellService
  _main_workcell: "IWorkcell"
  _workcell_db_accession_id: uuid.UUID | None
  _state_sync_task: asyncio.Task[None] | None

  async def _link_workcell_to_db(self) -> None:
    """Links the in-memory Workcell to its persistent DB entry."""
    if self._workcell_db_accession_id is None:
      async with self.db_session_factory() as db_session:
        workcell_orm = await self.workcell_svc.create(
          db=db_session,
          obj_in=WorkcellCreate(
            name=self._main_workcell.name,
            latest_state_json=self._main_workcell.serialize_all_state(),
          ),
        )
        await db_session.commit()
        self._workcell_db_accession_id = workcell_orm.accession_id
        logger.info(
          "Workcell '%s' linked to DB ID: %s",
          self._main_workcell.name,
          self._workcell_db_accession_id,
        )

        db_state = await self.workcell_svc.read_workcell_state(
          db_session,
          self._workcell_db_accession_id,
        )
        if db_state:
          self._main_workcell.load_all_state(db_state)
          logger.info(
            "Workcell '%s' state loaded from DB on startup.",
            self._main_workcell.name,
          )

  async def _continuous_state_sync_loop(self) -> None:
    """Synchronize workcell state internally and continuously (DB & Disk)."""
    if self._workcell_db_accession_id is None:
      logger.error("Cannot start state sync loop: Workcell DB ID is not set.")
      return

    logger.info(
      "Starting continuous workcell state sync loop for workcell ID: %s",
      self._workcell_db_accession_id,
    )
    last_disk_backup_time = datetime.datetime.now(datetime.timezone.utc)

    while True:
      try:
        current_state_json = self._main_workcell.serialize_all_state()

        async with self.db_session_factory() as db_session:
          await self.workcell_svc.update_workcell_state(
            db_session,
            self._workcell_db_accession_id,
            current_state_json,
          )
          await db_session.commit()
        logger.debug(
          "Workcell state for ID %s updated in DB.",
          self._workcell_db_accession_id,
        )

        now = datetime.datetime.now(datetime.timezone.utc)
        if (now - last_disk_backup_time).total_seconds() >= self._main_workcell.backup_interval:
          disk_backup_path = self._main_workcell.save_file.replace(
            ".json",
            f"_{self._main_workcell.backup_num}.json",
          )
          self._main_workcell.save_state_to_file(disk_backup_path)
          self._main_workcell.backup_num = (
            self._main_workcell.backup_num + 1
          ) % self._main_workcell.num_backups
          last_disk_backup_time = now
          logger.info(
            "Workcell state for ID %s backed up to disk: %s.",
            self._workcell_db_accession_id,
            disk_backup_path,
          )

      except asyncio.CancelledError:
        logger.info("Workcell state sync loop cancelled.")
        break
      except Exception:  # pylint: disable=broad-except
        logger.exception(
          "Error during continuous workcell state sync for ID %s",
          self._workcell_db_accession_id,
        )
      finally:
        await asyncio.sleep(5)

  async def start_workcell_state_sync(self) -> None:
    """Start the continuous workcell state synchronization task."""
    await self._link_workcell_to_db()
    if self._state_sync_task and not self._state_sync_task.done():
      logger.warning("Workcell state sync task is already running.")
      return

    self._state_sync_task = asyncio.create_task(self._continuous_state_sync_loop())
    logger.info(
      "Workcell state sync task started for ID %s.",
      self._workcell_db_accession_id,
    )

  async def stop_workcell_state_sync(self) -> None:
    """Stop the continuous workcell state synchronization task and performs final disk backup."""
    if self._state_sync_task:
      self._state_sync_task.cancel()
      with contextlib.suppress(asyncio.CancelledError):
        await self._state_sync_task
      self._state_sync_task = None
    else:
      logger.info("No active workcell state sync task to stop.")

    if self._main_workcell:
      final_backup_path = self._main_workcell.save_file.replace(
        ".json",
        "_final_exit.json",
      )
      self._main_workcell.save_state_to_file(final_backup_path)  # type: ignore[no-untyped-call]
      logger.info("Workcell state saved to disk on exit: %s", final_backup_path)

    if self._workcell_db_accession_id:
      try:
        async with self.db_session_factory() as db_session:
          await self.workcell_svc.update_workcell_state(
            db_session,
            self._workcell_db_accession_id,
            self._main_workcell.serialize_all_state(),
          )
          await db_session.commit()
          logger.info(
            "Final workcell state for ID %s committed to DB on exit.",
            self._workcell_db_accession_id,
          )
      except Exception:  # pylint: disable=broad-except
        logger.exception(
          "Failed to commit final workcell state to DB on exit for ID %s",
          self._workcell_db_accession_id,
        )

  def get_main_workcell(self) -> "IWorkcell":
    """Return the main Workcell instance managed by the runtime."""
    if self._main_workcell is None:
      msg = "Main Workcell instance is not initialized."
      raise WorkcellRuntimeError(msg)
    return self._main_workcell

  def get_state_snapshot(self) -> dict[str, Any]:
    """Capture and return the current JSON-serializable state of the workcell."""
    return self._main_workcell.serialize_all_state()

  def apply_state_snapshot(self, snapshot_json: dict[str, Any]) -> None:
    """Apply a previously captured JSON state to the workcell."""
    self._main_workcell.load_all_state(snapshot_json)
