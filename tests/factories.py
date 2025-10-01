"""Model factories for the Praxis test suite."""
import factory
from factory.alchemy import SQLAlchemyModelFactory
import uuid
from datetime import datetime

from praxis.backend.models.orm.user import UserOrm
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.orm.protocol import ProtocolRunOrm, FunctionProtocolDefinitionOrm
from praxis.backend.models.enums import AssetType, ProtocolRunStatusEnum, MachineCategoryEnum, MachineStatusEnum
from tests.conftest import TestAsyncSessionLocal

class PraxisSQLAlchemyModelFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = TestAsyncSessionLocal()
        sqlalchemy_session_persistence = "commit"

class UserFactory(PraxisSQLAlchemyModelFactory):
    class Meta:
        model = UserOrm

    accession_id = factory.LazyFunction(uuid.uuid4)
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    hashed_password = factory.Faker("password")
    full_name = factory.Faker("name")
    is_active = True
    phone_number = factory.Faker("phone_number")
    phone_carrier = "verizon"
    name = factory.LazyAttribute(lambda o: o.username)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
    properties_json = {}

class MachineFactory(PraxisSQLAlchemyModelFactory):
    class Meta:
        model = MachineOrm

    accession_id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("word")
    fqn = factory.LazyAttribute(lambda o: f"praxis.machine.{o.name}")
    asset_type = AssetType.MACHINE
    location = "lab"
    machine_category = MachineCategoryEnum.LIQUID_HANDLER
    status = MachineStatusEnum.ONLINE
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
    properties_json = {}


class FunctionProtocolDefinitionFactory(PraxisSQLAlchemyModelFactory):
    class Meta:
        model = FunctionProtocolDefinitionOrm

    accession_id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("word")
    fqn = factory.LazyAttribute(lambda o: f"praxis.protocol.{o.name}")
    version = "1.0.0"
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
    properties_json = {}


class ProtocolRunFactory(PraxisSQLAlchemyModelFactory):
    class Meta:
        model = ProtocolRunOrm

    accession_id = factory.LazyFunction(uuid.uuid4)
    top_level_protocol_definition = factory.SubFactory(FunctionProtocolDefinitionFactory)
    top_level_protocol_definition_accession_id = factory.LazyAttribute(lambda o: o.top_level_protocol_definition.accession_id)
    status = ProtocolRunStatusEnum.RUNNING
    name = factory.Faker("word")
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
    properties_json = {}