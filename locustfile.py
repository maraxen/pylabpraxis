from locust import HttpUser, task, between
import uuid
import random

class PraxisUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Assuming no auth or simple auth for now; if keycloak is strict, we'd need to fetch token.
        # For local dev testing, endpoints might be open or we use a fixed header if implemented.
        pass

    @task(3)
    def list_machines(self):
        self.client.get("/api/v1/machines")

    @task(3)
    def list_resource_definitions(self):
        self.client.get("/api/v1/resources/definitions")

    @task(1)
    def create_and_delete_machine(self):
        machine_name = f"StressTestMachine_{uuid.uuid4().hex[:8]}"
        payload = {
            "name": machine_name,
            "machine_type": "opentrons_ot2",
            "status": "AVAILABLE",
            "asset_type": "MACHINE"
        }
        # Create
        with self.client.post("/api/v1/machines", json=payload, catch_response=True) as response:
            if response.status_code == 200 or response.status_code == 201:
                machine_id = response.json().get("accession_id") or response.json().get("id")
                if machine_id:
                    # Delete
                    self.client.delete(f"/api/v1/machines/{machine_id}")
            elif response.status_code == 404:
                response.failure("Machine creation endpoint not found")

    @task(1)
    def trigger_protocol_run(self):
        # This requires a valid protocol definition ID.
        # For robust testing, we should query protocols first or use a known one.
        # Here we'll just hit the list endpoint to simulate traffic,
        # or try to run if we had a valid ID.
        # Simulating a view of protocols for now to avoid side-effects failing.
        self.client.get("/api/v1/protocols/definitions")
