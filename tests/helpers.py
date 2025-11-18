"""Async helper functions for creating test data.

These helpers work with async SQLAlchemy sessions, unlike Factory Boy which
only supports synchronous sessions. Use these for creating test data in
async tests.
"""

from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import AssetType, ResourceStatusEnum, ProtocolRunStatusEnum
from praxis.backend.models.orm.workcell import WorkcellOrm
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.orm.deck import DeckOrm, DeckDefinitionOrm
from praxis.backend.models.orm.resource import ResourceDefinitionOrm, ResourceOrm
from praxis.backend.models.orm.protocol import FunctionProtocolDefinitionOrm, ProtocolRunOrm
from praxis.backend.models.orm.outputs import FunctionDataOutputOrm, WellDataOutputOrm
from praxis.backend.utils.uuid import uuid7


async def create_workcell(
    db_session: AsyncSession,
    name: str = "test_workcell",
    **kwargs: Any
) -> WorkcellOrm:
    """Create a workcell for testing.

    Args:
        db_session: Async database session
        name: Workcell name (default: "test_workcell")
        **kwargs: Additional attributes to set on the workcell

    Returns:
        WorkcellOrm instance with generated accession_id
    """
    if 'accession_id' not in kwargs:
        kwargs['accession_id'] = uuid7()

    workcell = WorkcellOrm(name=name, **kwargs)
    db_session.add(workcell)
    await db_session.flush()
    return workcell


async def create_machine(
    db_session: AsyncSession,
    workcell: WorkcellOrm | None = None,
    name: str | None = None,
    fqn: str = "test.machine",
    **kwargs: Any
) -> MachineOrm:
    """Create a machine for testing.

    Args:
        db_session: Async database session
        workcell: Parent workcell (will create one if not provided)
        name: Machine name (default: unique generated name)
        fqn: Fully qualified name (default: "test.machine")
        **kwargs: Additional attributes to set on the machine

    Returns:
        MachineOrm instance with generated accession_id
    """
    if workcell is None:
        # Generate unique workcell name to avoid constraint violations
        unique_suffix = str(uuid7())
        workcell = await create_workcell(db_session, name=f"test_workcell_{unique_suffix}")

    if 'accession_id' not in kwargs:
        kwargs['accession_id'] = uuid7()

    # Generate unique machine name if not provided
    if name is None:
        name = f"test_machine_{str(uuid7())}"

    # Set asset_type if not provided
    if 'asset_type' not in kwargs:
        kwargs['asset_type'] = AssetType.MACHINE

    machine = MachineOrm(
        name=name,
        fqn=fqn,
        workcell_accession_id=workcell.accession_id,
        **kwargs
    )
    db_session.add(machine)
    await db_session.flush()
    return machine


async def create_resource_definition(
    db_session: AsyncSession,
    name: str = "test_resource_definition",
    fqn: str = "test.resource.definition",
    **kwargs: Any
) -> ResourceDefinitionOrm:
    """Create a resource definition for testing.

    Args:
        db_session: Async database session
        name: Resource definition name (default: "test_resource_definition")
        fqn: Fully qualified name (default: "test.resource.definition")
        **kwargs: Additional attributes to set on the resource definition

    Returns:
        ResourceDefinitionOrm instance
    """
    resource_def = ResourceDefinitionOrm(
        name=name,
        fqn=fqn,
        **kwargs
    )
    db_session.add(resource_def)
    await db_session.flush()
    return resource_def


async def create_resource(
    db_session: AsyncSession,
    name: str | None = None,
    resource_definition: ResourceDefinitionOrm | None = None,
    **kwargs: Any
) -> ResourceOrm:
    """Create a resource for testing.

    Args:
        db_session: Async database session
        name: Resource name (generates unique name if not provided)
        resource_definition: Associated resource definition (creates one if not provided)
        **kwargs: Additional attributes to set on the resource

    Returns:
        ResourceOrm instance
    """
    # Generate unique name if not provided
    if name is None:
        name = f"test_resource_{str(uuid7())}"

    # Create resource definition if not provided
    if resource_definition is None:
        resource_definition = await create_resource_definition(
            db_session,
            name=f"def_{name}",
            fqn=f"test.resource.def.{str(uuid7())}"
        )

    # Set defaults
    defaults = {
        "accession_id": uuid7(),
        "name": name,
        "fqn": f"test.resource.{str(uuid7())}",
        "asset_type": AssetType.RESOURCE,
        "status": ResourceStatusEnum.AVAILABLE_IN_STORAGE,
        "resource_definition_accession_id": resource_definition.accession_id,
    }
    defaults.update(kwargs)

    resource = ResourceOrm(**defaults)
    db_session.add(resource)
    await db_session.flush()
    return resource


async def create_deck_definition(
    db_session: AsyncSession,
    resource_definition: ResourceDefinitionOrm | None = None,
    name: str = "test_deck_definition",
    fqn: str = "test.deck.definition",
    **kwargs: Any
) -> DeckDefinitionOrm:
    """Create a deck definition for testing.

    Args:
        db_session: Async database session
        resource_definition: Associated resource definition (will create one if not provided)
        name: Deck definition name (default: "test_deck_definition")
        fqn: Fully qualified name (default: "test.deck.definition")
        **kwargs: Additional attributes to set on the deck definition

    Returns:
        DeckDefinitionOrm instance with generated accession_id
    """
    if resource_definition is None:
        resource_definition = await create_resource_definition(db_session)

    deck_def = DeckDefinitionOrm(
        name=name,
        fqn=fqn,
        resource_definition=resource_definition,
        **kwargs
    )
    db_session.add(deck_def)
    await db_session.flush()
    return deck_def


async def create_deck(
    db_session: AsyncSession,
    machine: MachineOrm | None = None,
    deck_definition: DeckDefinitionOrm | None = None,
    name: str = "test_deck",
    **kwargs: Any
) -> DeckOrm:
    """Create a deck for testing.

    Args:
        db_session: Async database session
        machine: Parent machine (will create one if not provided)
        deck_definition: Deck type definition (will create one if not provided)
        name: Deck name (default: "test_deck")
        **kwargs: Additional attributes to set on the deck

    Returns:
        DeckOrm instance with generated accession_id
    """
    from praxis.backend.utils.uuid import uuid7

    if machine is None:
        machine = await create_machine(db_session)

    if deck_definition is None:
        deck_definition = await create_deck_definition(db_session)

    deck_id = uuid7()

    # Set asset_type if not provided
    if 'asset_type' not in kwargs:
        kwargs['asset_type'] = AssetType.DECK

    deck = DeckOrm(
        accession_id=deck_id,
        name=name,
        deck_type_id=deck_definition.accession_id,
        parent_machine_accession_id=machine.accession_id,
        resource_definition_accession_id=deck_definition.resource_definition.accession_id,
        **kwargs
    )
    db_session.add(deck)
    await db_session.flush()
    await db_session.refresh(deck)  # Ensure the deck is fully loaded
    print(f"DEBUG helper created deck ID: {deck.accession_id}, name: {deck.name}")
    return deck


async def create_protocol_definition(
    db_session: AsyncSession,
    name: str | None = None,
    **kwargs: Any
) -> FunctionProtocolDefinitionOrm:
    """Create a protocol definition for testing.

    Args:
        db_session: Async database session
        name: Protocol name (generates unique name if not provided)
        **kwargs: Additional attributes to set on the protocol definition

    Returns:
        FunctionProtocolDefinitionOrm instance
    """
    from praxis.backend.models.orm.protocol import (
        FileSystemProtocolSourceOrm,
        ProtocolSourceRepositoryOrm,
    )

    # Generate unique name if not provided
    if name is None:
        name = f"test_protocol_{str(uuid7())}"

    # Create a file system source if not provided
    if 'file_system_source' not in kwargs:
        fs_source = FileSystemProtocolSourceOrm(
            name=f"test_fs_source_{str(uuid7())}",
            base_path="/test/protocols"
        )
        db_session.add(fs_source)
        await db_session.flush()
        kwargs['file_system_source'] = fs_source

    # Create source repository if not provided (required kw_only arg)
    if 'source_repository' not in kwargs:
        repo = ProtocolSourceRepositoryOrm(
            name=f"test_repo_{str(uuid7())}",
            git_url="https://github.com/test/test.git"
        )
        db_session.add(repo)
        await db_session.flush()
        kwargs['source_repository'] = repo

    # Set required defaults
    defaults = {
        "name": name,
        "fqn": f"test.protocols.{name}",
        "source_file_path": f"/test/protocols/{name}.py",
        "module_name": f"test.protocols.{name}",
        "function_name": name,
        "version": "1.0.0",
    }
    defaults.update(kwargs)

    protocol_def = FunctionProtocolDefinitionOrm(**defaults)
    db_session.add(protocol_def)
    await db_session.flush()
    return protocol_def


async def create_protocol_run(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm | None = None,
    **kwargs: Any
) -> ProtocolRunOrm:
    """Create a protocol run for testing.

    Args:
        db_session: Async database session
        protocol_definition: Associated protocol definition (creates one if not provided)
        **kwargs: Additional attributes to set on the protocol run

    Returns:
        ProtocolRunOrm instance
    """
    # Create protocol definition if not provided
    if protocol_definition is None:
        protocol_definition = await create_protocol_definition(db_session)

    # Set defaults
    defaults = {
        "accession_id": uuid7(),
        "top_level_protocol_definition_accession_id": protocol_definition.accession_id,
        "status": ProtocolRunStatusEnum.PENDING,
    }
    defaults.update(kwargs)

    protocol_run = ProtocolRunOrm(**defaults)
    db_session.add(protocol_run)
    await db_session.flush()
    return protocol_run


async def create_function_data_output(
    db_session: AsyncSession,
    **kwargs: Any
) -> FunctionDataOutputOrm:
    """Create a function data output for testing.

    Args:
        db_session: Async database session
        **kwargs: Additional attributes to set on the data output

    Returns:
        FunctionDataOutputOrm instance
    """
    from praxis.backend.models.enums.outputs import DataOutputTypeEnum
    import datetime

    # Set defaults
    defaults = {
        "data_key": f"test_output_{str(uuid7())}",
        "data_type": DataOutputTypeEnum.SCALAR,
        "data_value_json": {"value": 42},
        "measurement_timestamp": datetime.datetime.now(datetime.timezone.utc),
    }
    defaults.update(kwargs)

    data_output = FunctionDataOutputOrm(**defaults)
    db_session.add(data_output)
    await db_session.flush()
    return data_output


async def create_well_data_output(
    db_session: AsyncSession,
    resource: ResourceOrm | None = None,
    **kwargs: Any
) -> WellDataOutputOrm:
    """Create a well data output for testing.

    Args:
        db_session: Async database session
        resource: Associated resource (creates one if not provided)
        **kwargs: Additional attributes to set on the well data output

    Returns:
        WellDataOutputOrm instance
    """
    from praxis.backend.models.enums.outputs import DataOutputTypeEnum
    import datetime

    # Create resource if not provided
    if resource is None:
        resource = await create_resource(db_session)

    # Set defaults
    defaults = {
        "data_key": f"test_well_output_{str(uuid7())}",
        "data_type": DataOutputTypeEnum.SCALAR,
        "data_value_json": {"value": 42},
        "measurement_timestamp": datetime.datetime.now(datetime.timezone.utc),
        "resource_accession_id": resource.accession_id,
        "well_position": "A1",
    }
    defaults.update(kwargs)

    well_output = WellDataOutputOrm(**defaults)
    db_session.add(well_output)
    await db_session.flush()
    return well_output
