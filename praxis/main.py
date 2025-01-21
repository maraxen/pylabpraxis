
from fastapi import APIRouter, HTTPException, Depends, status, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt  # type: ignore
import json
import os
from praxis.configure import PraxisConfiguration

router = APIRouter()

# Load configuration from praxis.ini
config = (
    PraxisConfiguration()
)  # Assuming you initialize Configuration with "praxis.ini"
auth_config = config.get_section("auth")
admin_config = config.get_section("admin")


# --- Configuration ---
SECRET_KEY = auth_config.get("secret_key") or ""
ALGORITHM = auth_config.get("algorithm") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(auth_config.get("access_token_expire_minutes") or 30)
USER_DB_FILE = config.get_section("database").get("users", "users.json")


# --- Admin Credentials ---
ADMIN_USERNAME = admin_config.get("username")
ADMIN_PASSWORD = admin_config.get("password")


# --- User Database ---
# Placeholder for user database using JSON file
def get_user_db():
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w") as f:
            json.dump({}, f)  # Create an empty user database
    with open(USER_DB_FILE, "r") as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = {}
    return users


# --- OAuth2 ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# --- Pydantic Models ---
class Token(BaseModel):
    access_token: str
    token_type: str


# --- Helper Functions ---


def get_password_hash(password: str) -> str:
    """Hashes the password using bcrypt (replace with your actual hashing logic)."""
    # !!! In a real application, use a proper password hashing library like bcrypt !!!
    # Example (using bcrypt - install with: pip install bcrypt):
    import bcrypt

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_password.decode("utf-8")  # Store as a string


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a stored hash."""
    # !!! In a real application, use a proper password hashing library like bcrypt !!!
    # Example (using bcrypt):
    import bcrypt

    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return str(encoded_jwt)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and verifies a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return dict(payload)  # Convert to dict to match return type annotation
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- API Endpoints ---


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint for user login and token generation."""
    users_db = get_user_db()  # Load users from the JSON file

    # Check if the user is the admin user
    if form_data.username == ADMIN_USERNAME and form_data.password == ADMIN_PASSWORD:
        user = {"username": form_data.username, "is_admin": True}
    else:
        user = users_db.get(form_data.username)
        if not user or not verify_password(
            form_data.password, str(user["hashed_password"])
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current user from the JWT token."""
    try:
        print(f"Decoding token: {token}")
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            print("No username in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        print(f"Found user: {username}")
        return {"username": username, "is_admin": username == ADMIN_USERNAME}
    except Exception as e:
        print(f"Error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(current_user: Dict = Depends(get_current_user)):
    """Get the current active user."""
    try:
        print(f"Checking if user is active: {current_user}")
        return current_user
    except Exception as e:
        print(f"Error in get_current_active_user: {str(e)}")
        raise HTTPException(status_code=400, detail="Inactive user")


async def get_current_admin_user(current_user: Dict = Depends(get_current_active_user)):
    """Get the current admin user."""
    try:
        print(f"Checking if user is admin: {current_user}")
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Not an admin user")
        return current_user
    except Exception as e:
        print(f"Error in get_current_admin_user: {str(e)}")
        raise HTTPException(status_code=403, detail="Not an admin user")


@router.get("/users/me")
async def read_users_me(current_user: Dict = Depends(get_current_active_user)):
    """Protected endpoint that requires a valid JWT token."""
    return {
        "username": current_user["username"],
        "is_admin": current_user.get("is_admin", False),
    }

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/auth")