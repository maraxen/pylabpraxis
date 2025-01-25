from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from keycloak import KeycloakOpenID
from typing import Dict
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Load Keycloak configuration from json file
try:
    with open(Path(__file__).parent.parent.parent / "keycloak.json") as f:
        keycloak_config = json.load(f)
        logger.info("Loaded Keycloak configuration from keycloak.json")
except Exception as e:
    logger.error(f"Failed to load keycloak.json: {e}")
    raise

# Clean up server URL
server_url = keycloak_config["auth-server-url"].rstrip('/')
if '/auth' not in server_url:
    server_url = f"{server_url}/auth"

logger.info(f"Initializing Keycloak with server URL: {server_url}")

# Initialize Keycloak client
keycloak_openid = KeycloakOpenID(
    server_url=server_url,
    realm_name=keycloak_config["realm"],
    client_id=keycloak_config["resource"],
    client_secret_key=keycloak_config["credentials"]["secret"],
    verify=True
)

# Test the configuration
try:
    well_known = keycloak_openid.well_known()
    logger.info("Successfully retrieved Keycloak OIDC configuration")
    logger.debug(f"OIDC Configuration: {well_known}")
except Exception as e:
    logger.error(f"Failed to retrieve Keycloak OIDC configuration: {e}")
    raise

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    try:
        # Decode token
        token_info = keycloak_openid.decode_token(
            token
        )

        return {
            "username": token_info.get("preferred_username"),
            "email": token_info.get("email"),
            "is_admin": "admin" in token_info.get("realm_access", {}).get("roles", [])
        }
    except Exception as e:
        logger.error(f"Failed to decode token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin_user(user: Dict = Depends(get_current_user)) -> Dict:
    if not user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user
