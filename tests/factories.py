"""Factories for creating test data."""
import uuid

import factory
from factory.alchemy import SQLAlchemyModelFactory

from praxis.backend.models.orm.deck import DeckDefinitionOrm, DeckOrm
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.orm.resource import ResourceDefinitionOrm
from praxis.backend.models.orm.workcell import WorkcellOrm


class WorkcellFactory(SQLAlchemyModelFactory):
    """Factory for WorkcellOrm."""

    class Meta:
        """Meta class for WorkcellFactory."""

        model = WorkcellOrm

    accession_id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("word")


class MachineFactory(SQLAlchemyModelFactory):
    """Factory for MachineOrm."""

    class Meta:
        """Meta class for MachineFactory."""

        model = MachineOrm

    accession_id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("word")
    fqn = factory.Faker("word")
    workcell_accession_id = factory.SelfAttribute("workcell.accession_id")

    workcell = factory.SubFactory(
        "tests.factories.WorkcellFactory",
    )


class ResourceDefinitionFactory(SQLAlchemyModelFactory):
    """Factory for ResourceDefinitionOrm."""

    class Meta:
        """Meta class for ResourceDefinitionOrm."""

        model = ResourceDefinitionOrm

    name = factory.Faker("word")
    fqn = factory.Faker("word")


class DeckDefinitionFactory(SQLAlchemyModelFactory):
    """Factory for DeckDefinitionOrm."""

    class Meta:
        """Meta class for DeckDefinitionOrm."""

        model = DeckDefinitionOrm

    name = factory.Faker("word")
    fqn = factory.Faker("word")
    resource_definition = factory.SubFactory(
        "tests.factories.ResourceDefinitionFactory",
    )


class DeckFactory(SQLAlchemyModelFactory):
    """Factory for DeckOrm."""

    class Meta:
        """Meta class for DeckOrm."""

        model = DeckOrm

    accession_id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("word")
    deck_type_id = factory.SelfAttribute("deck_type.accession_id")
    parent_machine_accession_id = factory.SelfAttribute("machine.accession_id")

    deck_type = factory.SubFactory(
        "tests.factories.DeckDefinitionFactory",
    )
    machine = factory.SubFactory(
        "tests.factories.MachineFactory",
    )
