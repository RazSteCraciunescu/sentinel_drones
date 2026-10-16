import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.api


def test_health_is_public_and_marks_simulation_only(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Sentinel UAS Assurance Lab",
        "environment": "local-lab",
        "simulation_only": True,
    }


def test_dashboard_is_served(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Sentinel UAS Assurance Lab" in response.text
    assert "SIMULATION ONLY" in response.text


def test_fleet_returns_seeded_aircraft(
    client: TestClient,
    headers: dict[str, dict[str, str]],
) -> None:
    response = client.get("/api/v1/fleet", headers=headers["observer"])

    assert response.status_code == 200
    assert [item["drone_id"] for item in response.json()] == ["UAS-001", "UAS-002", "UAS-003"]
