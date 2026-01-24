# pylint: disable=too-many-arguments,fixme
"""Manages asset reservations for protocol runs."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from praxis.backend.models.domain.schedule import AssetReservation
from praxis.backend.models.enums import AssetReservationStatusEnum, AssetType
from praxis.backend.models.pydantic_internals.runtime import RuntimeAssetRequirement
from praxis.backend.utils.errors import AssetAcquisitionError
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)


class AssetReservationManager:
  """Manages asset reservations for protocol runs."""

  def __init__(self, db_session_factory: async_sessionmaker[AsyncSession]):
    """Initialize the AssetReservationManager."""
    self.db_session_factory = db_session_factory
    self._asset_reservations_cache: dict[str, set[uuid.UUID]] = {}

  async def reserve_assets(
    self,
    requirements: list[RuntimeAssetRequirement],
    protocol_run_id: uuid.UUID,
    db_session: AsyncSession | None = None,
    schedule_entry_id: uuid.UUID | None = None,
  ) -> bool:
    """Reserve assets for a protocol run."""
    logger.info(
      "Attempting to reserve %d assets for run %s",
      len(requirements),
      protocol_run_id,
    )

    created_reservations: list[AssetReservation] = []

    async def _do_reserve(session: AsyncSession) -> bool:
      nonlocal created_reservations

      for requirement in requirements:
        asset_key = f"{requirement.asset_type}:{requirement.asset_definition.name}"

        if asset_key in self._asset_reservations_cache:
          conflicting_runs = self._asset_reservations_cache[asset_key] - {protocol_run_id}
          if conflicting_runs:
            error_msg = (
              f"Asset {asset_key} is already reserved by runs: {[str(r) for r in conflicting_runs]}"
            )
            logger.warning(error_msg)
            for res in created_reservations:
              await session.delete(res)
              res_key = res.redis_lock_key
              if res_key in self._asset_reservations_cache:
                self._asset_reservations_cache[res_key].discard(protocol_run_id)
                if not self._asset_reservations_cache[res_key]:
                  del self._asset_reservations_cache[res_key]
            raise AssetAcquisitionError(error_msg)

        existing_query = select(AssetReservation).where(
            and_(
                AssetReservation.redis_lock_key == asset_key,
                AssetReservation.status.in_([
                    AssetReservationStatusEnum.PENDING,
                    AssetReservationStatusEnum.ACTIVE,
                    AssetReservationStatusEnum.RESERVED,
                ])
            )
        )
        result = await session.execute(existing_query)
        existing_reservations = result.scalars().all()

        conflicting = [
          r for r in existing_reservations if r.protocol_run_accession_id != protocol_run_id
        ]

        if conflicting:
          conflicting_runs = [str(r.protocol_run_accession_id) for r in conflicting]
          error_msg = f"Asset {asset_key} is already reserved by runs: {conflicting_runs}"
          logger.warning(error_msg)
          for res in created_reservations:
            await session.delete(res)
            res_key = res.redis_lock_key
            if res_key in self._asset_reservations_cache:
              self._asset_reservations_cache[res_key].discard(protocol_run_id)
              if not self._asset_reservations_cache[res_key]:
                del self._asset_reservations_cache[res_key]
          raise AssetAcquisitionError(error_msg)

        reservation_id = uuid7()
        reservation = AssetReservation(
          name=f"reservation_{requirement.asset_definition.name}_{reservation_id.hex[:8]}",
          protocol_run_accession_id=protocol_run_id,
          schedule_entry_accession_id=schedule_entry_id or protocol_run_id,
          asset_type=AssetType.ASSET,
          asset_accession_id=requirement.asset_definition.accession_id,
          asset_name=requirement.asset_definition.name,
          redis_lock_key=asset_key,
          redis_lock_value=str(reservation_id),
          lock_timeout_seconds=3600,
          status=AssetReservationStatusEnum.ACTIVE,
          released_at=None,
        )
        session.add(reservation)
        created_reservations.append(reservation)
        requirement.reservation_id = reservation_id

        if asset_key not in self._asset_reservations_cache:
          self._asset_reservations_cache[asset_key] = set()
        self._asset_reservations_cache[asset_key].add(protocol_run_id)

        logger.debug(
          "Reserved asset %s for run %s (reservation: %s)",
          asset_key,
          protocol_run_id,
          reservation_id,
        )

      await session.flush()
      logger.info(
        "Successfully reserved all %d assets for run %s",
        len(requirements),
        protocol_run_id,
      )
      return True

    try:
      if db_session:
        return await _do_reserve(db_session)
      async with self.db_session_factory() as session:
        result = await _do_reserve(session)
        await session.commit()
        return result
    except AssetAcquisitionError:
      raise
    except Exception as e:
      logger.exception(
        "Error during asset reservation for run %s",
        protocol_run_id,
      )
      msg = f"Unexpected error during asset reservation: {e!s}"
      raise AssetAcquisitionError(msg) from e

  async def release_reservations(
    self,
    asset_keys: list[str],
    protocol_run_id: uuid.UUID,
    db_session: AsyncSession | None = None,
  ) -> None:
    """Release asset reservations for a protocol run."""

    async def _do_release(session: AsyncSession) -> None:
      for asset_key in asset_keys:
        query = select(AssetReservation).where(
            and_(
                AssetReservation.redis_lock_key == asset_key,
                AssetReservation.protocol_run_accession_id == protocol_run_id,
                AssetReservation.status.in_([
                    AssetReservationStatusEnum.PENDING,
                    AssetReservationStatusEnum.ACTIVE,
                    AssetReservationStatusEnum.RESERVED,
                ])
            )
        )
        result = await session.execute(query)
        reservation = result.scalar_one_or_none()

        if reservation:
          reservation.status = AssetReservationStatusEnum.RELEASED
          reservation.released_at = datetime.now(timezone.utc)
          logger.debug("Released reservation for asset %s in database", asset_key)

        if asset_key in self._asset_reservations_cache:
          self._asset_reservations_cache[asset_key].discard(protocol_run_id)
          if not self._asset_reservations_cache[asset_key]:
            del self._asset_reservations_cache[asset_key]

    if db_session:
      await _do_release(db_session)
    else:
      async with self.db_session_factory() as session:
        await _do_release(session)
        await session.commit()
