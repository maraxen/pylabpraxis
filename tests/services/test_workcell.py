"""Test module for workcell service functions."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import all required models
from praxis.backend.models import MachineOrm, WorkcellOrm

# Import the service functions to be tested
# Assuming the service file is praxis/backend/services/workcell_data_service.py
from praxis.backend.services import (
  create_workcell,
  delete_workcell,
  list_workcells,
  read_workcell,
  read_workcell_by_name,
  read_workcell_state,
  update_workcell,
  update_workcell_state,
)

# --- Pytest Fixtures ---


@pytest.fixture
async def existing_workcell(db: AsyncSession) -> WorkcellOrm:
  """Fixture that creates a standard workcell for testing."""
  return await create_workcell(
    db,
    name=f"TestWorkcell_{uuid.uuid4()}",
    description="A workcell for testing.",
    physical_location="Lab 1, Bench A",
    initial_state={"status": "idle"},
  )


@pytest.fixture
async def machine_in_workcell(
  db: AsyncSession,
  existing_workcell: WorkcellOrm,
) -> MachineOrm:
  """Fixture that creates a machine and assigns it to the existing_workcell."""
  machine = MachineOrm(
    name=f"MachineInWorkcell_{uuid.uuid4()}",
    fqn="machine.in.workcell.fqn",
    workcell_accession_id=existing_workcell.accession_id,
  )
  db.add(machine)
  await db.commit()
  return machine


pytestmark = pytest.mark.asyncio


class TestWorkcellService:
  """Test suite for the Workcell service layer."""

  async def test_create_and_read_workcell(self, db: AsyncSession):
    """Test creating a workcell and reading it back by ID and name."""
    name = f"MyWorkcell_{uuid.uuid4()}"
    description = "Primary liquid handling workcell."
    location = "Room 101"

    created_wc = await create_workcell(
      db,
      name=name,
      description=description,
      physical_location=location,
    )
    assert created_wc is not None
    assert created_wc.name == name
    assert created_wc.description == description
    assert created_wc.physical_location == location

    # Read back by ID
    read_by_id = await read_workcell(db, created_wc.accession_id)
    assert read_by_id is not None
    assert read_by_id.name == name

    # Read back by name
    read_by_name = await read_workcell_by_name(db, name)
    assert read_by_name is not None
    assert read_by_name.accession_id == created_wc.accession_id

  async def test_create_workcell_fails_on_duplicate_name(
    self,
    db: AsyncSession,
    existing_workcell: WorkcellOrm,
  ):
    """Test that creating a workcell with a duplicate name raises ValueError."""
    with pytest.raises(ValueError, match="already exists"):
      await create_workcell(db, name=existing_workcell.name)

  async def test_update_workcell(
    self,
    db: AsyncSession,
    existing_workcell: WorkcellOrm,
  ):
    """Test updating various fields of a workcell."""
    new_desc = "An updated description."
    new_loc = "Lab 2, Bench B"

    updated_wc = await update_workcell(
      db,
      workcell_accession_id=existing_workcell.accession_id,
      description=new_desc,
      physical_location=new_loc,
    )

    assert updated_wc is not None
    assert updated_wc.accession_id == existing_workcell.accession_id
    assert updated_wc.description == new_desc
    assert updated_wc.physical_location == new_loc

  async def test_list_workcells(self, db: AsyncSession, existing_workcell: WorkcellOrm):
    """Test listing workcells with pagination."""
    # Create a second workcell
    await create_workcell(db, name=f"AnotherWorkcell_{uuid.uuid4()}")

    all_wcs = await list_workcells(db, limit=10)
    assert len(all_wcs) >= 2

    # Test pagination
    paginated_wcs = await list_workcells(db, limit=1, offset=0)
    assert len(paginated_wcs) == 1

    next_page_wcs = await list_workcells(db, limit=1, offset=1)
    assert len(next_page_wcs) == 1
    assert paginated_wcs[0].accession_id != next_page_wcs[0].accession_id

  async def test_delete_workcell_success(self, db: AsyncSession):
    """Test successfully deleting an empty workcell."""
    wc_to_delete = await create_workcell(db, name=f"ToDelete_{uuid.uuid4()}")
    wc_id = wc_to_delete.accession_id

    result = await delete_workcell(db, wc_id)
    assert result is True

    # Verify it's gone
    assert await read_workcell(db, wc_id) is None

  async def test_delete_workcell_fails_if_in_use(
    self,
    db: AsyncSession,
    existing_workcell: WorkcellOrm,
    machine_in_workcell: MachineOrm,
  ):
    """Test that deleting a workcell with linked machines fails gracefully."""
    # The machine_in_workcell fixture links a machine to existing_workcell.
    # Attempting to delete the workcell should fail due to the FK constraint.
    result = await delete_workcell(db, existing_workcell.accession_id)
    # The service function catches the IntegrityError and returns False
    assert result is False

  async def test_read_and_update_workcell_state(
    self,
    db: AsyncSession,
    existing_workcell: WorkcellOrm,
  ):
    """Test reading and updating the JSON state of a workcell."""
    # Test reading the initial state
    initial_state = await read_workcell_state(db, existing_workcell.accession_id)
    assert initial_state == {"status": "idle"}

    # Test updating the state
    new_state = {"status": "running", "progress": 50, "last_op": "aspirate"}
    updated_wc = await update_workcell_state(
      db,
      existing_workcell.accession_id,
      new_state,
    )
    assert updated_wc is not None
    assert updated_wc.latest_state_json == new_state
    assert updated_wc.last_state_update_time is not None
    assert existing_workcell.last_state_update_time is not None
    assert updated_wc.last_state_update_time > existing_workcell.last_state_update_time

    # Test reading the new state
    read_new_state = await read_workcell_state(db, existing_workcell.accession_id)
    assert read_new_state == new_state

  async def test_update_state_fails_for_non_existent_workcell(self, db: AsyncSession):
    """Test that updating state for a non-existent workcell raises ValueError."""
    non_existent_id = uuid.uuid4()
    with pytest.raises(ValueError, match="not found for state update"):
      await update_workcell_state(db, non_existent_id, {"status": "error"})
