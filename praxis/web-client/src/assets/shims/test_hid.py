"""Verification Script for WebHID Shim

This script is designed to run in the browser console (or Pyodide REPL) to verify
that the WebHID shim is correctly loaded and operational.

Usage:
1. Copy content to JupyterLite console or Pyodide setup.
2. Run.
"""

import sys
import asyncio
from web_hid_shim import WebHID
import pylabrobot.io.hid as plr_hid


async def verify_hid_shim():
  print("--- WebHID Shim Verification ---")

  # 1. Check Import
  print(f"1. WebHID Class: {WebHID}")

  # 2. Check Patching
  if plr_hid.HID == WebHID:
    print("2. [PASS] pylabrobot.io.hid.HID is patched to WebHID")
  else:
    print(f"2. [FAIL] pylabrobot.io.hid.HID is {plr_hid.HID}, expected WebHID")

  # 3. Check environment
  try:
    from js import navigator

    if hasattr(navigator, "hid"):
      print("3. [PASS] navigator.hid is available")
    else:
      print("3. [FAIL] navigator.hid NOT available (Browser support issue?)")
  except ImportError:
    print("3. [SKIP] Not in Pyodide environment")

  # 4. Dry Run Setup (Expected to fail without user interaction, but checking signature)
  hid = WebHID(vid=0x03EB, pid=0x2023)
  print(f"4. Instantiated WebHID: {hid._unique_id}")

  print("\n--- Verification Complete ---")


if __name__ == "__main__":
  if "pyodide" in sys.modules:
    asyncio.create_task(verify_hid_shim())
  else:
    print("Running in standard Python (dry run)...")
    if plr_hid.HID == WebHID:  # Should fail in standard python unless manually patched for test
      print("Patch active.")
    else:
      print("Patch not active (Expected in standard python).")
