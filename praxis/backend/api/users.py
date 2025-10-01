"""API endpoints for user management."""
from datetime import datetime
from fastapi import APIRouter, Depends
import uuid

from praxis.backend.models.pydantic_internals.user import UserResponse

router = APIRouter()

def get_current_user() -> UserResponse:
    """
    A dependency that returns a hardcoded user.
    In a real application, this would be replaced with a proper
    authentication and user lookup mechanism.
    """
    now = datetime.now()
    return UserResponse(
        accession_id=uuid.uuid4(),
        username="testuser",
        email="testuser@example.com",
        full_name="Test User",
        is_active=True,
        created_at=now,
        updated_at=now,
        properties_json={},
        name="testuser"
    )

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    """
    An endpoint to get the current user.
    """
    return current_user