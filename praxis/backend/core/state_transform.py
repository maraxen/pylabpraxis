"""State transformation utilities for converting PyLabRobot state to frontend format.

This module transforms the raw state from PyLabRobot's `serialize_all_state()` into the
structured format expected by the frontend StateSnapshot model.

PLR State Format:
    {
        "resource_name": {
            # TipTracker format (TipSpot, LiquidHandler channels):
            "tip": {...} | None,
            "tip_state": {...} | None,
            "pending_tip": {...} | None,

            # VolumeTracker format (Container/Well):
            "volume": float,
            "pending_volume": float,
            "thing": str,
            "max_volume": float,

            # LiquidHandler:
            "head_state": {channel_id: tip_tracker_state}
        }
    }

Frontend StateSnapshot Format:
    {
        "tips": {"tips_loaded": bool, "tips_count": int},
        "liquids": {"resource_name": {"well_id": volume}},
        "on_deck": ["resource_name", ...],
        "raw_plr_state": {...}
    }
"""

from typing import Any


def extract_tip_state(plr_state: dict[str, Any]) -> dict[str, Any]:
    """Extract tip state from PLR state.

    Searches for liquid handler state (identified by "head_state" key) and counts
    how many channels have tips loaded.

    Args:
        plr_state: Raw state from PyLabRobot serialize_all_state()

    Returns:
        Dictionary with tips_loaded (bool) and tips_count (int)
    """
    tips_loaded = False
    tips_count = 0

    for _resource_name, resource_state in plr_state.items():
        if not isinstance(resource_state, dict):
            continue

        # Check for liquid handler state (has "head_state" key)
        if "head_state" in resource_state:
            head_state = resource_state["head_state"]
            if isinstance(head_state, dict):
                for _channel_id, channel_state in head_state.items():
                    if isinstance(channel_state, dict) and channel_state.get("tip") is not None:
                        tips_count += 1

            tips_loaded = tips_count > 0
            break  # Only one liquid handler expected

    return {"tips_loaded": tips_loaded, "tips_count": tips_count}


def extract_liquid_volumes(plr_state: dict[str, Any]) -> dict[str, dict[str, float]]:
    """Extract liquid volumes from PLR state.

    Searches for resources with VolumeTracker state (identified by "volume" key)
    and organizes them by parent resource (plate) and well identifier.

    Args:
        plr_state: Raw state from PyLabRobot serialize_all_state()

    Returns:
        Dictionary mapping resource names to well volumes:
        {"plate_name": {"A1": 250.0, "A2": 100.0, ...}}
    """
    liquids: dict[str, dict[str, float]] = {}

    for resource_name, resource_state in plr_state.items():
        if not isinstance(resource_state, dict):
            continue

        # Check for volume tracker state (has "volume" key)
        if "volume" in resource_state:
            volume = resource_state.get("volume", 0.0)

            # Only include resources with non-zero volume
            if volume > 0:
                # Try to extract parent plate name from resource name
                # Well names typically follow patterns like "plate_name_A1" or just "A1"
                # For now, use flat structure with resource name as key
                parent_name = _infer_parent_name(resource_name)
                well_id = _infer_well_id(resource_name)

                if parent_name not in liquids:
                    liquids[parent_name] = {}

                liquids[parent_name][well_id] = volume

    return liquids


def _infer_parent_name(resource_name: str) -> str:
    """Infer parent plate name from well resource name.

    Common naming patterns:
    - "plate_name_A1" -> "plate_name"
    - "source_plate_well_A1" -> "source_plate"
    - "A1" -> "unknown_plate"

    Args:
        resource_name: Full resource name

    Returns:
        Inferred parent plate name
    """
    # Check for common well identifier patterns at the end
    import re

    # Pattern: anything ending in _[A-H][1-12] or _well_[A-H][1-12]
    match = re.match(r"^(.+?)(?:_well)?_([A-P]\d{1,2})$", resource_name, re.IGNORECASE)
    if match:
        return match.group(1)

    # If no pattern match, check if it looks like a standalone well ID
    if re.match(r"^[A-P]\d{1,2}$", resource_name, re.IGNORECASE):
        return "unknown_plate"

    # Otherwise, treat the whole name as the resource identifier
    return resource_name


def _infer_well_id(resource_name: str) -> str:
    """Infer well ID from resource name.

    Args:
        resource_name: Full resource name

    Returns:
        Well identifier (e.g., "A1") or the full resource name if no pattern matches
    """
    import re

    # Pattern: extract [A-H][1-12] from end of name
    match = re.search(r"([A-P]\d{1,2})$", resource_name, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    return resource_name


def get_on_deck_resources(plr_state: dict[str, Any]) -> list[str]:
    """Get list of resource names currently on deck.

    Args:
        plr_state: Raw state from PyLabRobot serialize_all_state()

    Returns:
        List of resource names
    """
    return list(plr_state.keys())


def transform_plr_state(plr_state: dict[str, Any] | None) -> dict[str, Any] | None:
    """Transform PyLabRobot state to frontend StateSnapshot format.

    This is the main entry point for state transformation.

    Args:
        plr_state: Raw state from PyLabRobot serialize_all_state(), or None

    Returns:
        Dictionary matching frontend StateSnapshot format, or None if input is None
    """
    if not plr_state:
        return None

    tip_state = extract_tip_state(plr_state)
    liquids = extract_liquid_volumes(plr_state)
    on_deck = get_on_deck_resources(plr_state)

    return {
        "tips": tip_state,
        "liquids": liquids,
        "on_deck": on_deck,
        "raw_plr_state": plr_state,
    }
