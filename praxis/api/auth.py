from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional
from keycloak import KeycloakOpenID, KeycloakAdmin
import json
from pathlib import Path
import logging
from typing import Any

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
            password=form_data.password,
            grant_type="password"
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
