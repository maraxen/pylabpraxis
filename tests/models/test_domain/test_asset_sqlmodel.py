"""Tests for unified Asset SQLModel."""
import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from praxis.backend.models.domain.asset import Asset, AssetCreate, AssetRead, AssetUpdate
from praxis.backend.models.enums import AssetType


@pytest.fixture
def engine():
    """Create in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create database session."""
    with Session(engine) as session:
        yield session


class TestAssetSQLModel:
    """Test suite for Asset SQLModel."""

    def test_asset_creation_defaults(self, session):
        """Test creating Asset with minimal fields."""
        asset = Asset(name="test_asset")
        session.add(asset)
        session.commit()
        session.refresh(asset)
        
        assert asset.accession_id is not None
        assert asset.name == "test_asset"
        assert asset.asset_type == AssetType.ASSET
        assert asset.fqn == ""
        assert asset.location is None

    def test_asset_serialization_to_read(self, session):
        """Test serializing Asset to AssetRead response."""
        asset = Asset(
            name="test_asset",
            fqn="test.Asset",
            plr_state={"key": "value"},
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        
        # Verify read model
        read_model = AssetRead.model_validate(asset)
        assert read_model.name == "test_asset"
        assert read_model.fqn == "test.Asset"
        assert read_model.plr_state == {"key": "value"}
        assert read_model.asset_type == AssetType.ASSET

    def test_asset_create_schema_validation(self):
        """Test AssetCreate schema validation."""
        create_data = AssetCreate(
            name="new_asset",
            asset_type=AssetType.MACHINE,
            fqn="machines.NewMachine",
        )
        assert create_data.name == "new_asset"
        assert create_data.asset_type == AssetType.MACHINE
        assert create_data.fqn == "machines.NewMachine"

    def test_asset_update_partial(self):
        """Test AssetUpdate allows partial updates."""
        update_data = AssetUpdate(location="Lab A")
        assert update_data.location == "Lab A"
        assert update_data.name is None  # Not provided
        
        # Verify filtering out None values works when updating
        update_dict = update_data.model_dump(exclude_unset=True)
        assert "name" not in update_dict
        assert update_dict["location"] == "Lab A"

    def test_polymorphic_identity(self, session):
        """Test that the polymorphic identity is correctly set."""
        asset = Asset(name="poly_asset")
        session.add(asset)
        session.commit()
        
        # Raw SQL check to verify the discriminator column
        statement = select(Asset).where(Asset.name == "poly_asset")
        result = session.exec(statement).first()
        assert result.asset_type == AssetType.ASSET
        
    def test_json_fields_roundtrip(self, session):
        """Test that JSON fields are correctly stored and retrieved."""
        plr_def = {"model": "Opentrons", "version": 2}
        asset = Asset(
            name="robot", 
            plr_definition=plr_def
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)
        
        assert asset.plr_definition == plr_def
