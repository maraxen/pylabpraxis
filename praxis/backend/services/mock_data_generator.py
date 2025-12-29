"""Mock data generator service for simulating telemetry data."""

import asyncio
import logging
import random
import uuid
from typing import Any, TYPE_CHECKING

from praxis.backend.utils.logging import get_logger
from praxis.backend.models import ProtocolRunStatusEnum
from praxis.backend.utils.db import AsyncSessionLocal

if TYPE_CHECKING:
    from praxis.backend.services.protocols import ProtocolRunService

logger = get_logger(__name__)


class MockTelemetryService:
  """Service for generating mock telemetry data for protocol runs."""

  def __init__(self, protocol_run_service: "ProtocolRunService | None" = None) -> None:
    """Initialize the mock telemetry service."""
    self._active_streams: dict[uuid.UUID, asyncio.Task] = {}
    self._current_telemetry: dict[uuid.UUID, dict[str, Any]] = {}
    self.protocol_run_service = protocol_run_service
    logger.info("MockTelemetryService initialized.")

  def start_streaming(self, run_id: uuid.UUID) -> None:
    """Start generating mock data for a specific run."""
    if run_id in self._active_streams:
      logger.warning("Streaming already active for run %s", run_id)
      return

    logger.info("Starting mock telemetry stream for run %s", run_id)
    self._active_streams[run_id] = asyncio.create_task(
      self._generate_data_loop(run_id),
    )

  def stop_streaming(self, run_id: uuid.UUID) -> None:
    """Stop generating mock data for a specific run."""
    if run_id in self._active_streams:
      logger.info("Stopping mock telemetry stream for run %s", run_id)
      self._active_streams[run_id].cancel()
      del self._active_streams[run_id]
    
    if run_id in self._current_telemetry:
        del self._current_telemetry[run_id]

  def get_latest_data(self, run_id: uuid.UUID) -> dict[str, Any] | None:
    """Get the latest telemetry data for a run."""
    return self._current_telemetry.get(run_id)

  async def _generate_data_loop(self, run_id: uuid.UUID) -> None:
    """Background loop to generate random data."""
    iteration = 0
    try:
      while True:
        # Check status every 10 iterations (5 seconds)
        if iteration % 10 == 0 and self.protocol_run_service:
             try:
                async with AsyncSessionLocal() as db_session:
                    run = await self.protocol_run_service.get(db_session, accession_id=run_id)
                    if run and run.status in [
                        ProtocolRunStatusEnum.COMPLETED,
                        ProtocolRunStatusEnum.FAILED,
                        ProtocolRunStatusEnum.CANCELLED
                    ]:
                        logger.info("Run %s finished (status: %s), stopping telemetry.", run_id, run.status.name)
                        break # Exit loop
             except Exception as e:
                logger.warning("Error checking run status for %s: %s", run_id, e)

        # Generate random data
        # Temperature: 20-40°C with some noise
        temp = 20.0 + (random.random() * 20.0)
        
        # Absorbance: 0-4.0 OD
        absorbance = random.random() * 4.0

        data = {
          "temperature": round(temp, 2),
          "absorbance": round(absorbance, 3),
          "timestamp": asyncio.get_event_loop().time(),
        }

        self._current_telemetry[run_id] = data
        
        # Update frequency (e.g., every 0.5 seconds)
        await asyncio.sleep(0.5)
        iteration += 1

    except asyncio.CancelledError:
      logger.debug("Telemetry loop cancelled for run %s", run_id)
    except Exception as e:
      logger.exception("Error in telemetry loop for run %s", run_id)
    finally:
        # Cleanup when loop exits
        if run_id in self._current_telemetry:
            del self._current_telemetry[run_id]
        if run_id in self._active_streams:
             del self._active_streams[run_id]
