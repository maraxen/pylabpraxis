"""Run control utilities for orchestrator."""

from typing import List, Optional

import redis
import uuid_utils as uuid
from redis.exceptions import RedisError

from praxis.backend.configure import get_settings  # To access Redis config

ALLOWED_COMMANDS: List[str] = ["PAUSE", "RESUME", "CANCEL"]
COMMAND_KEY_PREFIX = "orchestrator:control"


def _get_redis_client() -> redis.Redis:
  settings = get_settings()
  # Assuming settings.redis_host and settings.redis_port are available
  # If settings.redis_url is directly available, that would be preferred:
  # redis_url = settings.redis_url
  redis_url = f"redis://{settings.redis_host}:{settings.redis_port}/0"
  return redis.Redis.from_url(redis_url, decode_responses=True)


def _get_command_key(run_guid: uuid.UUID) -> str:
  return f"{COMMAND_KEY_PREFIX}:{run_guid}"


async def send_control_command(
  run_guid: uuid.UUID, command: str, ttl_seconds: int = 3600
) -> bool:
  """Send a control command to the orchestrator for a specific run.

  Args:
    run_guid: The unique identifier for the run.
    command: The control command to send. Must be one of ALLOWED_COMMANDS.
    ttl_seconds: Time-to-live for the command in Redis, default is 3600 seconds
    (1 hour).

  """
  if command not in ALLOWED_COMMANDS:
    raise ValueError(
      f"Invalid command: {command}. Allowed commands are: {ALLOWED_COMMANDS}"
    )
  try:
    r = _get_redis_client()
    key = _get_command_key(run_guid)
    await r.set(key, command, ex=ttl_seconds)
    return True
  except RedisError as e:
    # In a real application, use a proper logger
    print(f"RedisError sending control command for run {run_guid}: {e}")
    return False


async def get_control_command(run_guid: uuid.UUID) -> Optional[str]:
  """Get the control command for a specific run.

  Args:
    run_guid: The unique identifier for the run.

  Returns:
    The control command if it exists, otherwise None.

  """
  try:
    r = _get_redis_client()
    key = _get_command_key(run_guid)
    command = await r.get(key)
    return command  # Returns None if key doesn't exist
  except RedisError as e:
    print(f"RedisError getting control command for run {run_guid}: {e}")
    return None


async def clear_control_command(run_guid: uuid.UUID) -> bool:
  """Clear the control command for a specific run.

  Args:
    run_guid: The unique identifier for the run.

  Returns:
    True if the command was cleared, False if it didn't exist or an error occurred.

  """
  try:
    r = _get_redis_client()
    key = _get_command_key(run_guid)
    deleted_count = await r.delete(key)
    return deleted_count > 0
  except RedisError as e:
    print(f"RedisError clearing control command for run {run_guid}: {e}")
    return False
