import time
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakConnectionError
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

def init_keycloak(max_retries: int = 30, retry_delay: int = 2) -> KeycloakOpenID:
    """Initialize Keycloak with retries."""
    retries = 0
    last_error = None

    while retries < max_retries:
        try:
            keycloak_openid = KeycloakOpenID(
                server_url=server_url,
                realm_name=keycloak_config["realm"],
                client_id=keycloak_config["resource"],
                client_secret_key=keycloak_config["credentials"]["secret"],
                verify=True
            )
            # Test the connection
            keycloak_openid.well_known()
            return keycloak_openid
        except KeycloakConnectionError as e:
            last_error = e
            print(f"Attempt {retries + 1}/{max_retries}: Keycloak not ready, retrying in {retry_delay}s...")
            time.sleep(retry_delay)
            retries += 1

    raise HTTPException(
        status_code=503,
        detail=f"Failed to connect to Keycloak after {max_retries} attempts: {last_error}"
    )

# Initialize Keycloak with retry mechanism
keycloak_openid = init_keycloak()

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
