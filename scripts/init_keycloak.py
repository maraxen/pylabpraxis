from keycloak import KeycloakAdmin
import sys
from praxis.configure import PraxisConfiguration

def init_keycloak(admin_username: str, admin_password: str) -> None:
    """Initialize Keycloak with admin credentials."""
    config = PraxisConfiguration()
    keycloak_config = config.get_keycloak_config()
    server_url = keycloak_config['server_url']

    try:
        # Initialize KeycloakAdmin
        keycloak_admin = KeycloakAdmin(
            server_url=server_url,
            username=admin_username,
            password=admin_password,
            realm_name="master",
            verify=True
        )
        print("Successfully connected to Keycloak")

        # Create realm
        try:
            keycloak_admin.create_realm({
                "realm": "praxis",
                "enabled": True,
                "displayName": "Praxis Lab Manager"
            })
            print("Created realm 'praxis'")
        except Exception as e:
            if "409" in str(e):
                print("Realm 'praxis' already exists")
            else:
                raise

        # Switch to praxis realm
        keycloak_admin.realm_name = "praxis"

        # Create client using initial access token if available
        initial_token = keycloak_config.get('client_initial_access_token')
        if initial_token:
            try:
                # Create client with initial access token
                keycloak_admin.token = initial_token
                client_representation = {
                    "clientId": "praxis-client",
                    "enabled": True,
                    "protocol": "openid-connect",
                    "publicClient": False,
                    "directAccessGrantsEnabled": True,
                    "standardFlowEnabled": True,
                    "authorizationServicesEnabled": True,
                    "serviceAccountsEnabled": True,
                    "redirectUris": ["http://localhost:5173/*"],
                    "webOrigins": ["http://localhost:5173"]
                }

                client = keycloak_admin.create_client(client_representation)
                client_id = client['id']
                client_secret = keycloak_admin.get_client_secrets(client_id)

                # Save the client credentials to config
                config.save_keycloak_config("praxis-client", client_secret['value'])

                print("\nClient Configuration:")
                print(f"Client ID: praxis-client")
                print(f"Client Secret: {client_secret['value']}")
                print("\nCredentials have been saved to praxis.ini")

            except Exception as e:
                if "409" in str(e):
                    print("Client 'praxis-client' already exists")
                else:
                    print(f"Error creating client: {e}")
                    raise
        else:
            print("No initial access token found. Skipping client creation.")

        print("\nKeycloak initialization complete!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python init_keycloak.py <admin_username> <admin_password>")
        sys.exit(1)

    init_keycloak(sys.argv[1], sys.argv[2])
