import requests
import sys

def test_auth_flow(username: str, password: str) -> None:
    """Test the complete authentication flow."""
    base_url = "http://localhost:5000"

    print("\n1. Testing login endpoint...")
    # Test login
    login_response = requests.post(
        f"{base_url}/auth/token",
        data={
            "username": username,
            "password": password,
            "grant_type": "password",
            "client_id": "praxis-client"
        }
    )

    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        sys.exit(1)

    token = login_response.json()["access_token"]
    print("✅ Login successful")

    print("\n2. Testing user info endpoint...")
    # Test getting user info
    headers = {"Authorization": f"Bearer {token}"}
    user_response = requests.get(f"{base_url}/auth/users/me", headers=headers)

    if user_response.status_code != 200:
        print(f"Getting user info failed: {user_response.text}")
        sys.exit(1)

    user_info = user_response.json()
    print("✅ Got user info:")
    print(f"Username: {user_info['username']}")
    print(f"Is Admin: {user_info['is_admin']}")
    print(f"Email: {user_info.get('email', 'Not set')}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_auth.py <username> <password>")
        sys.exit(1)

    test_auth_flow(sys.argv[1], sys.argv[2])
