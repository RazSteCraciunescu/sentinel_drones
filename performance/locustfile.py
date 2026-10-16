from __future__ import annotations

from locust import HttpUser, between, task


class AssuranceDashboardUser(HttpUser):
    wait_time = between(0.5, 2.0)
    host = "http://127.0.0.1:8080"

    def on_start(self) -> None:
        self.headers = {"X-Lab-Token": "observer-local-token"}

    @task(3)
    def read_fleet(self) -> None:
        with self.client.get(
            "/api/v1/fleet",
            headers=self.headers,
            name="GET /api/v1/fleet",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"unexpected status {response.status_code}")
            elif len(response.json()) != 3:
                response.failure("unexpected fleet size")

    @task(2)
    def read_metrics(self) -> None:
        self.client.get(
            "/api/v1/assurance/metrics",
            headers=self.headers,
            name="GET /api/v1/assurance/metrics",
        )

    @task(1)
    def health(self) -> None:
        self.client.get("/health", name="GET /health")
