from .auth import login_for_access_token, read_users_me
from .keycloak_auth import get_current_user, get_current_admin_user
from praxis.api import assets

__all__ = [
    'login_for_access_token',
    'read_users_me',
    'get_current_user',
    'get_current_admin_user'
]

app.include_router(assets.router, prefix="/assets", tags=["assets"])