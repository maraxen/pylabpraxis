import json
import os
from typing import cast, Dict, Any, List
from pylabrobot import resources, machines
from pylabrobot.resources import Resource
from pylabrobot.utils import find_subclass
from pylabrobot.machines import Machine
import aiofiles
import asyncio

class AsyncAssetDatabase:
    """
    An asynchronous database for managing assets, with each asset being an instance of
    Resource or Machine.

    The database is stored in a JSON file, with each asset being stored as a dictionary
    in the following format:

    {
        "asset_id": {
            "key1": "value1",
            "key2": "value2",
            ...
        },
        ...
    }

    The asset_id is a unique identifier for the asset, which is extracted from the asset
    using the _get_asset_id method. The asset is serialized to a dictionary using the
    _serialize_asset method before being stored in the database. The asset can be
    deserialized using the _deserialize_asset method.

    The database file is created if it does not exist. The database supports adding assets,
    getting an asset by its asset_id, and listing all asset_ids.

    The database file is locked during read and write operations to prevent concurrent
    access issues.

    Args:
        file_path (str): The path to the database file.

    Raises:
        ValueError: If the asset is not an instance of Resource or Machine.
        KeyError: If the asset with the given asset_id already exists or does not exist.
        ValueError: If the JSON format in the database file is invalid.
        ValueError: If the asset type is unknown.
        ValueError: If the asset type cannot be determined.

    Methods:
        add_asset(asset: Resource | Machine): Adds an asset to the database.
        get_asset(asset_id: str) -> Dict[str, Any]: Gets an asset by its asset_id.
        list_assets() -> List[str]: Lists all asset_ids in the database.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lock = asyncio.Lock()

    async def _ensure_file_exists(self):
        """Ensures that the database file exists."""
        if not os.path.exists(self.file_path):
            async with aiofiles.open(self.file_path, mode='w') as f:
                await f.write(json.dumps({}))

    async def add_asset(self, asset: Resource | Machine):
      """
      Adds an asset to the database.

      Args:
          asset (Resource | Machine): The asset to add to the database.

      Raises:
          ValueError: If the asset is not an instance of Resource or Machine.
          KeyError: If the asset with the given asset_id already exists.
      """
      if not isinstance(asset, (Resource, Machine)):
          raise ValueError("Asset must be an instance of Resource or Machine")

      asset_id = self._get_asset_id(asset)

      async with self.lock:
          await self._ensure_file_exists()
          async with aiofiles.open(self.file_path, mode='r+') as f:
              try:
                  data = json.loads(await f.read())
              except json.JSONDecodeError:
                  data = {}

              if asset_id in data:
                  raise KeyError(f"Asset with id {asset_id} already exists")

              data[asset_id] = self._serialize_asset(asset)
              await f.seek(0)
              await f.write(json.dumps(data, indent=4))
              await f.truncate()

    async def get_asset(self, asset_id: str) -> dict[str, Any]:
        """
        Gets an asset by its asset_id.

        Args:
            asset_id (str): The asset_id of the asset to get.

        Returns:
            Dict[str, Any]: The asset as a dictionary.

        Raises:
            KeyError: If the asset with the given asset_id does not exist.
            ValueError: If the JSON format in the database file is invalid.
            ValueError: If the asset type is unknown.
            ValueError: If the asset type cannot be determined.
        """
        await self._ensure_file_exists()
        async with aiofiles.open(self.file_path, mode='r') as f:
            try:
                data = json.loads(await f.read())
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format in database file")

            if asset_id not in data:
                raise KeyError(f"Asset with id {asset_id} not found")

            return self._deserialize_asset(data[asset_id])

    async def list_assets(self) -> list[str]:
      """
      Lists all asset_ids in the database.

      Returns:
          List[str]: A list of asset_ids in the database.

      Raises:
          ValueError: If the JSON format in the database file is invalid.
      """
      await self._ensure_file_exists()
      async with aiofiles.open(self.file_path, mode='r') as f:
          try:
              data = json.loads(await f.read())
          except json.JSONDecodeError:
              raise ValueError("Invalid JSON format in database file")

          return list(data.keys())

    async def get_all_machines(self) -> dict[str, Machine]:
      """
      Lists all asset_ids in the database.

      Returns:
          List[str]: A list of asset_ids in the database.

      Raises:
          ValueError: If the JSON format in the database file is invalid.
      """
      await self._ensure_file_exists()
      async with aiofiles.open(self.file_path, mode='r') as f:
          try:
              data = json.loads(await f.read())
          except json.JSONDecodeError:
              raise ValueError("Invalid JSON format in database file")

          machines = {}
          for asset_id, asset_data in data.items():
              asset = self._deserialize_asset(asset_data)
              if isinstance(asset, Machine):
                  machines[asset_id] = asset
          return machines


    async def get_all_resources(self) -> dict[str, Resource]:
      """
      Lists all asset_ids in the database.

      Returns:
          List[str]: A list of asset_ids in the database.

      Raises:
          ValueError: If the JSON format in the database file is invalid.
      """
      await self._ensure_file_exists()
      async with aiofiles.open(self.file_path, mode='r') as f:
          try:
              data = json.loads(await f.read())
          except json.JSONDecodeError:
              raise ValueError("Invalid JSON format in database file")

          resources = {}
          for asset_id, asset_data in data.items():
              asset = self._deserialize_asset(asset_data)
              if isinstance(asset, Resource):
                  resources[asset_id] = asset
          return resources

    async def get_resources(self, resource_ids: list[str]) -> dict[str, Resource]:
      """
      Get resources by their asset_ids.
      """
      await self._ensure_file_exists()
      async with aiofiles.open(self.file_path, mode='r') as f:
          try:
              data = json.loads(await f.read())
          except json.JSONDecodeError:
              raise ValueError("Invalid JSON format in database file")

          resources = {}
          for asset_id in resource_ids:
              if asset_id in data:
                  asset = self._deserialize_asset(data[asset_id])
                  if isinstance(asset, Resource):
                      resources[asset_id] = asset
          return resources

    async def get_machines(self, machine_ids: list[str]) -> dict[str, Machine]:
      """
      Get machines by their asset_ids.
      """
      await self._ensure_file_exists()
      async with aiofiles.open(self.file_path, mode='r') as f:
          try:
              data = json.loads(await f.read())
          except json.JSONDecodeError:
              raise ValueError("Invalid JSON format in database file")

          machines = {}
          for asset_id in machine_ids:
              if asset_id in data:
                  asset = self._deserialize_asset(data[asset_id])
                  if isinstance(asset, Machine):
                      machines[asset_id] = asset
          return machines

    def _get_asset_id(self, asset: Resource | Machine) -> str:
      """
      Extracts a unique identifier for the asset.

      For Resource, the name is used as the asset_id. For Machine, it checks for the name, device_id,
      serial_number, and port attributes to use as the asset_id in that order. It is important to ensure
      that the asset_id is unique for each asset.

      Args:
          asset (Resource | Machine): The asset to extract the asset_id from.

      Returns:
          str: The asset_id extracted from the asset.

      Raises:
          ValueError: If the asset is not an instance of Resource or Machine.
      """
      if isinstance(asset, Resource):
          return asset.name
      elif isinstance(asset, Machine):
          return cast(str, asset.get("name", asset.get("device_id", asset.get("serial_number", asset.get("port", None)))))
      else:
          raise ValueError("Asset must be an instance of Resource or Machine")

    def _serialize_asset(self, asset: Resource | Machine) -> Dict[str, Any]:
        """Serializes the asset to a dictionary.
        Args:
            asset (Resource | Machine): The asset to serialize.
        Returns:
            Dict[str, Any]: The serialized asset as a dictionary.

        Raises:
            ValueError: If the asset is not an instance of Resource or Machine.
        """
        if isinstance(asset, Resource):
            return asset.serialize()
        elif isinstance(asset, Machine):
            return asset.serialize()
        else:
            raise ValueError("Asset must be an instance of Resource or Machine")

    def _deserialize_asset(self, data: Dict[str, Any]) -> Resource | Machine:
        """Deserializes the asset from a dictionary."""
        resource_type = data.get("type", None)
        if find_subclass(Machine, resource_type) is not None:
            cls = find_subclass(Machine, resource_type)
            return cls.deserialize(data)
        if find_subclass(Resource, resource_type) is not None:
            cls = find_subclass(Resource, resource_type)
            return cls.deserialize(data)
        raise ValueError("Asset type is unknown or cannot be determined")
