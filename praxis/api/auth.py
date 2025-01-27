from fastapi import APIRouter, HTTPException, Depends, status, Body, Request, Response, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
from keycloak import KeycloakOpenID
import json
from pathlib import Path
import logging
from typing import Any
from urllib.parse import quote

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Load Keycloak configuration
try:
    with open(Path(__file__).parent.parent.parent / "keycloak.json") as f:
        keycloak_config = json.load(f)
        logger.info("Loaded Keycloak configuration")
except Exception as e:
    logger.error(f"Failed to load keycloak.json: {e}")
    raise

# Initialize Keycloak client
keycloak_openid = KeycloakOpenID(
    server_url=keycloak_config["auth-server-url"].rstrip('/'),
    realm_name=keycloak_config["realm"],
    client_id=keycloak_config["resource"],
    client_secret_key=keycloak_config["credentials"]["secret"],
    verify=True
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class UserInfo(BaseModel):
    username: str
    email: Optional[str] = None
    is_admin: bool = False
    roles: List[str] = []
    picture: str

# Token and Authentication endpoints
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        token = await keycloak_openid.a_token(
            username=form_data.username,
            password=form_data.password
        )
        return {
            "access_token": token["access_token"],
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(refresh_token: str):
    try:
        token = await keycloak_openid.a_refresh_token(refresh_token)
        return {
            "access_token": token["access_token"],
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

# User Info and Management
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    try:
        token_info = await keycloak_openid.a_decode_token(token)
        return {
            "username": token_info.get("preferred_username"),
            "email": token_info.get("email"),
            "is_admin": "admin" in token_info.get("realm_access", {}).get("roles", []),
            "roles": token_info.get("realm_access", {}).get("roles", [])
        }
    except Exception as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/users/me", response_model=UserInfo)
async def read_users_me(current_user: Dict = Depends(get_current_user)):
    return current_user

@router.get("/login-user", response_model=UserInfo)
async def get_login_user(token: str = Depends(oauth2_scheme)) -> Dict:
    try:
        token_info = await keycloak_openid.a_decode_token(token)
        return {
            "username": token_info.get("preferred_username"),
            "email": token_info.get("email"),
            "is_admin": "admin" in token_info.get("realm_access", {}).get("roles", []),
            "roles": token_info.get("realm_access", {}).get("roles", []),
            "picture": token_info.get("picture")
        }
    except Exception as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/userinfo")
async def get_userinfo(token: str = Depends(oauth2_scheme)):
    try:
        return await keycloak_openid.a_userinfo(token)
    except Exception as e:
        logger.error(f"Userinfo fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not retrieve user information"
        )


# Auth flow endpoints
@router.get("/login-uri")
async def get_login_uri(redirect_uri: str, state: Optional[str] = None):
    return {"uri": await keycloak_openid.a_auth_url(redirect_uri, state=state)}

@router.post("/logout")
async def logout(refresh_token: str):
    try:
        await keycloak_openid.a_logout(refresh_token)
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )

# Token verification and introspection
@router.post("/verify-token")
async def verify_token(token: str):
    try:
        token_info = await keycloak_openid.a_introspect(token)
        return token_info
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# --- Auth flow endpoints ---

@router.get("/register-uri")
async def get_register_uri(redirect_uri: str = "http://localhost:5173/"):
    """
    Returns the Keycloak registration URI.
    """
    register_url = keycloak_config["auth-server-url"] + f"/realms/{keycloak_openid.realm_name}/login-actions/registration"
    register_url += f"?client_id={keycloak_config['resource']}"
    register_url += f"&redirect_uri={quote(redirect_uri, safe='')}"
    register_url += f"&response_mode=query"
    register_url += f"&response_type=code"
    register_url += f"&scope=openid+email+profile"
    try:
        return {"uri": register_url}
    except Exception as e:
        logger.error(f"Error generating registration URI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating registration URI"
        )

@router.post("/create-user")
async def create_user(request: Request, response: Response):
    """
    Handles user creation by redirecting to the Keycloak registration page.
    """
    redirect_uri = request.url_for("get_register_uri")
    return RedirectResponse(url=redirect_uri)

@router.get("/forgot-password-uri")
async def get_forgot_password_uri(redirect_uri: str = "http://localhost:8000/static/index.html"):
    """
    Returns the Keycloak forgot password URI.
    """
    forgot_password_url = keycloak_openid.server_url + f"realms/{keycloak_openid.realm_name}/login-actions/reset-credentials"
    forgot_password_url += f"?client_id={keycloak_openid.client_id}"
    forgot_password_url += f"&redirect_uri={quote(redirect_uri, safe='')}"
    try:
        return {"uri": forgot_password_url}
    except Exception as e:
        logger.error(f"Error generating forgot password URI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating forgot password URI"
        )

@router.post("/forgot-password")
async def forgot_password(request: Request, response: Response):
    """
    Handles forgot password requests by redirecting to the Keycloak forgot password page.
    """
    redirect_uri = request.url_for("get_forgot_password_uri")
    return RedirectResponse(url=redirect_uri)

@router.get("/update-password-uri")
async def get_update_password_uri(redirect_uri: str = "http://localhost:8000/static/index.html"):
    """
    Returns the Keycloak update password URI.
    """
    update_password_url = keycloak_openid.server_url + f"realms/{keycloak_openid.realm_name}/login-actions/action-token"
    update_password_url += f"?client_id={keycloak_openid.client_id}"
    update_password_url += f"&redirect_uri={quote(redirect_uri, safe='')}"
    update_password_url += f"&execution=execute-actions"
    update_password_url += f"&key=UPDATE_PASSWORD"
    try:
        return {"uri": update_password_url}
    except Exception as e:
        logger.error(f"Error generating update password URI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating update password URI"
        )

@router.put("/update-password")
async def update_password(
    request: Request,
    response: Response
):
    """
    Handles password updates by redirecting to the Keycloak update password page.
    """
    redirect_uri = request.url_for("get_update_password_uri")
    return RedirectResponse(url=redirect_uri)
