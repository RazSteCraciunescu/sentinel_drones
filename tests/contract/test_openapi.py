import pytest
from fastapi.testclient import TestClient


@pytest.mark.contract
def test_openapi_declares_api_key_security_scheme(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    scheme = schema["components"]["securitySchemes"]["APIKeyHeader"]
    assert scheme == {"type": "apiKey", "in": "header", "name": "X-Lab-Token"}


@pytest.mark.contract
def test_openapi_exposes_only_safe_command_enum(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    actions = schema["components"]["schemas"]["SafeCommandAction"]["enum"]
    assert actions == ["hold", "return_home", "land"]


@pytest.mark.contract
def test_health_contract_requires_simulation_flag(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    health_schema = schema["components"]["schemas"]["HealthResponse"]
    assert "simulation_only" in health_schema["properties"]


@pytest.mark.contract
def test_unknown_route_is_not_masked(client: TestClient) -> None:
    response = client.get("/api/v1/flight-controller/connect")

    assert response.status_code == 404
