"""Run control utilities for orchestrator."""

import uuid

import redis
from redis.exceptions import RedisError

from praxis.backend.configure import PraxisConfiguration

SETTINGS = PraxisConfiguration()

ALLOWED_COMMANDS: list[str] = ["PAUSE", "RESUME", "CANCEL"]
COMMAND_KEY_PREFIX = "orchestrator:control"


def _get_redis_client() -> redis.Redis:
  redis_url = f"redis://{SETTINGS.redis_host}:{SETTINGS.redis_port}/0"
  return redis.Redis.from_url(redis_url, decode_responses=True)


def _get_command_key(run_accession_id: uuid.UUID) -> str:
  return f"{COMMAND_KEY_PREFIX}:{run_accession_id}"


async def send_control_command(
  run_accession_id: uuid.UUID,
  command: str,
  ttl_seconds: int = 3600,
) -> bool:
  """Send a control command to the orchestrator for a specific run.

  Args:
    run_accession_id: The unique identifier for the run.
    command: The control command to send. Must be one of ALLOWED_COMMANDS.
    ttl_seconds: Time-to-live for the command in Redis, default is 3600 seconds
    (1 hour).

  """
  if command not in ALLOWED_COMMANDS:
    msg = f"Invalid command: {command}. Allowed commands are: {ALLOWED_COMMANDS}"
    raise ValueError(
      msg,
    )
  try:
    r = _get_redis_client()
    key = _get_command_key(run_accession_id)
    await r.set(key, command, ex=ttl_seconds)
  except RedisError:
    # In a real application, use a proper logger
    return False
  else:
    return True


async def get_control_command(run_accession_id: uuid.UUID) -> str | None:
  """Get the control command for a specific run.

  Args:
    run_accession_id: The unique identifier for the run.

  Returns:
    The control command if it exists, otherwise None.

  """
  try:
    r = _get_redis_client()
    key = _get_command_key(run_accession_id)
    return await r.get(key)
  except RedisError:
    return None


async def clear_control_command(run_accession_id: uuid.UUID) -> bool:
  """Clear the control command for a specific run.

  Args:
    run_accession_id: The unique identifier for the run.

  Returns:
    True if the command was cleared, False if it didn't exist or an error occurred.

  """
  try:
    r = _get_redis_client()
    key = _get_command_key(run_accession_id)
    deleted_count = await r.delete(key)
  except RedisError:
    return False
  else:
    return deleted_count > 0
