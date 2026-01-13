"""Helpers to safely run async coroutines from sync code.

Provides `run_sync(coro)` which runs the coroutine using `asyncio.run` when
no event loop is running, and falls back to running the coroutine in a
separate thread with its own event loop when a loop is already running.
"""
from __future__ import annotations

import asyncio
import threading
from typing import Any


def run_sync(coro: "collections.abc.Coroutine[Any, Any, Any]") -> Any:
  """Run an async coroutine from sync code without calling `asyncio.run`.

  This helper avoids using `asyncio.run` to prevent issues when tests
  monkeypatch `asyncio.run` or when an event loop is already running.

  Behavior:
  - If no running event loop is present in the current thread, create a
    new event loop in this thread and run the coroutine to completion.
  - If a running loop is present, execute the coroutine in a separate
    thread with its own event loop and return the result.
  """
  try:
    # If a running loop exists, get_running_loop() returns it; otherwise
    # it raises RuntimeError.
    asyncio.get_running_loop()
  except RuntimeError:
    # No running loop in this thread: create one and run the coroutine.
    loop = asyncio.new_event_loop()
    try:
      asyncio.set_event_loop(loop)
      return loop.run_until_complete(coro)
    finally:
      try:
        asyncio.set_event_loop(None)
      except Exception:
        pass
      loop.close()

  # There is a running event loop in this thread; run the coroutine
  # in a new thread with its own loop.
  result: dict[str, Any] = {}

  def _runner() -> None:
    loop = asyncio.new_event_loop()
    try:
      asyncio.set_event_loop(loop)
      result["value"] = loop.run_until_complete(coro)
    finally:
      try:
        asyncio.set_event_loop(None)
      except Exception:
        pass
      loop.close()

  thread = threading.Thread(target=_runner)
  thread.start()
  thread.join()
  return result.get("value")
