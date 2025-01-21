import os
import json
import logging
import asyncio
from typing import Dict, Any, List, cast
import aiofiles

from praxis.configure import PraxisConfiguration
from praxis.api.protocols import discover_protocols, ProtocolDirectories

# Set up logging
logger = logging.getLogger("praxis.api.initialization")
logger.setLevel(logging.DEBUG)

# Create handlers if they don't exist
if not logger.handlers:
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("logs/initialization.log", mode="a")

    # Create formatters and add it to handlers
    log_format = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Prevent the logger from propagating to the root logger
    logger.propagate = False


async def initialize_assets(config: PraxisConfiguration) -> List[Dict[str, Any]]:
    """Initialize and return the list of available assets."""
    logger.info("Initializing assets...")
    try:
        # Get the asset database path from config
        asset_db = config.asset_db
        os.makedirs(os.path.dirname(asset_db), exist_ok=True)

        # Create default assets if file doesn't exist or is empty
        if not os.path.exists(asset_db) or os.path.getsize(asset_db) == 0:
            logger.info("Creating default assets...")
            default_assets: List[Dict[str, Any]] = [
                {
                    "id": "lh1",
                    "name": "Liquid Handler 1",
                    "type": "liquid_handler",
                    "description": "Default liquid handler",
                },
                {
                    "id": "m1",
                    "name": "Machine 1",
                    "type": "machine",
                    "description": "Default machine",
                },
            ]
            async with aiofiles.open(asset_db, "w") as f:
                await f.write(json.dumps(default_assets, indent=2))
            logger.info(f"Created default assets: {default_assets}")
            return default_assets

        # Read existing assets
        logger.info("Reading existing assets...")
        async with aiofiles.open(asset_db, "r") as f:
            content = await f.read()
            assets = cast(List[Dict[str, Any]], json.loads(content))
            logger.info(f"Loaded {len(assets)} assets")
            return assets

    except Exception as e:
        logger.error(f"Error initializing assets: {e}")
        return []


async def initialize_users(config: PraxisConfiguration) -> List[Dict[str, Any]]:
    """Initialize and return the list of available users."""
    logger.info("Initializing users...")
    try:
        users_file = config.users
        os.makedirs(os.path.dirname(users_file), exist_ok=True)

        # Create default users if file doesn't exist or is empty
        if not os.path.exists(users_file) or os.path.getsize(users_file) == 0:
            logger.info("Creating default users...")
            default_users = {
                "admin": {"display_name": "Administrator", "is_admin": True},
                "user": {"display_name": "Default User", "is_admin": False},
            }
            async with aiofiles.open(users_file, "w") as f:
                await f.write(json.dumps(default_users, indent=2))

        # Read and convert users to list format
        logger.info("Reading users...")
        async with aiofiles.open(users_file, "r") as f:
            content = await f.read()
            users_dict = json.loads(content)

            users_list = []
            for username, user_data in users_dict.items():
                user_info = {
                    "username": username,
                    "display_name": user_data.get("display_name", username),
                    "is_admin": (
                        True
                        if username == "admin"
                        else user_data.get("is_admin", False)
                    ),
                }
                users_list.append(user_info)

            logger.info(f"Loaded {len(users_list)} users")
            return users_list

    except Exception as e:
        logger.error(f"Error initializing users: {e}")
        return []


async def initialize_deck_layouts(config: PraxisConfiguration) -> List[str]:
    """Initialize and return the list of available deck layouts."""
    logger.info("Initializing deck layouts...")
    try:
        deck_dir = config.deck_management.get("deck_directory", "./deck_layouts")
        os.makedirs(deck_dir, exist_ok=True)

        # Create a test deck file if none exist
        if not any(f.endswith(".json") for f in os.listdir(deck_dir)):
            logger.info("Creating test deck layout...")
            test_deck = {
                "name": "Test Deck",
                "description": "A test deck layout",
                "resources": [],
            }
            test_deck_path = os.path.join(deck_dir, "test_deck.json")
            async with aiofiles.open(test_deck_path, "w") as f:
                await f.write(json.dumps(test_deck, indent=2))

        # Get all JSON files in the deck directory
        deck_files = [f for f in os.listdir(deck_dir) if f.endswith(".json")]
        logger.info(f"Found {len(deck_files)} deck layout files")
        return deck_files

    except Exception as e:
        logger.error(f"Error initializing deck layouts: {e}")
        return []


async def initialize_protocols(config: PraxisConfiguration) -> List[Dict[str, Any]]:
    """Initialize and return the list of available protocols."""
    logger.info("Initializing protocols...")
    try:
        # Get default and configured directories
        directories = [config.default_protocol_dir]
        directories.extend(config.get_protocol_directories())

        # Create ProtocolDirectories instance
        dirs = ProtocolDirectories(directories=directories)

        # Discover protocols
        protocols = await discover_protocols(
            dirs, {"username": "system", "is_admin": True}
        )
        logger.info(f"Discovered {len(protocols)} protocols")
        return cast(List[Dict[str, Any]], protocols)

    except Exception as e:
        logger.error(f"Error initializing protocols: {e}")
        return []


async def initialize_all(config: PraxisConfiguration) -> Dict[str, Any]:
    """Initialize all resources and return their initial state."""
    logger.info("Starting initialization of all resources...")

    # Initialize all resources concurrently
    assets, users, deck_layouts, protocols = await asyncio.gather(
        initialize_assets(config),
        initialize_users(config),
        initialize_deck_layouts(config),
        initialize_protocols(config),
    )

    initialization_state = {
        "assets": assets,
        "users": users,
        "deck_layouts": deck_layouts,
        "protocols": protocols,
    }

    logger.info("Completed initialization of all resources")
    logger.debug(f"Initialization state: {initialization_state}")

    return initialization_state
