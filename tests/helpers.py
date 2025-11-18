"""Async helper functions for creating test data.

These helpers work with async SQLAlchemy sessions, unlike Factory Boy which
only supports synchronous sessions. Use these for creating test data in
async tests.
"""

from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import AssetType, ResourceStatusEnum
from praxis.backend.models.orm.workcell import WorkcellOrm
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.orm.deck import DeckOrm, DeckDefinitionOrm
from praxis.backend.models.orm.resource import ResourceDefinitionOrm, ResourceOrm
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
