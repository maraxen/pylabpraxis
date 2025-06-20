from typing import Any, Dict, List

class KeycloakOpenIDConnection:
    def __init__(
        self,
        server_url: str,
        username: str,
        password: str,
        realm_name: str,
    ) -> None: ...

class KeycloakAdmin:
    def __init__(self, connection: KeycloakOpenIDConnection) -> None: ...
    def create_realm(self, payload: Dict[str, Any]) -> None: ...
    def get_clients(self) -> List[Dict[str, Any]]: ...
    def create_client(self, payload: Dict[str, Any]) -> str: ...
    def get_groups(self) -> List[Dict[str, Any]]: ...
    def create_group(self, payload: Dict[str, Any]) -> str: ...
    realm_name: str

class KeycloakOpenID:
    def __init__(
        self,
        server_url: str,
        client_id: str,
        realm_name: str,
        client_secret_key: str
    ) -> None: ...
    def introspect(self, token: str) -> Dict[str, Any]: ...
    def token(self, username: str, password: str) -> Dict[str, str]: ...

class KeycloakPostError(Exception):
    def __init__(self, error_message: str) -> None: ...
