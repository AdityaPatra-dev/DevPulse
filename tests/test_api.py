import os

# Set testing environment variables before importing application modules
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ENVIRONMENT"] = "testing"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# In-memory SQLite database dedicated to testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_database():
    """Create fresh database tables before each test and drop after."""
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Test client for invoking FastAPI endpoints."""
    with TestClient(app) as test_client:
        yield test_client


def test_healthz(client: TestClient):
    """Verify database-backed healthz endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_create_and_get_service(client: TestClient):
    """Test service registration and listing."""
    payload = {"name": "Payment Gateway", "url": "https://payment.example.com"}
    response = client.post("/services", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Payment Gateway"
    assert created["id"] is not None

    # Duplicate name should return 409
    dup_res = client.post("/services", json=payload)
    assert dup_res.status_code == 409

    # List services
    list_res = client.get("/services")
    assert list_res.status_code == 200
    services = list_res.json()
    assert len(services) == 1
    assert services[0]["name"] == "Payment Gateway"


def test_create_and_patch_incident(client: TestClient):
    """Test incident reporting and status transitions."""
    # Register service first
    srv_res = client.post("/services", json={"name": "Auth API", "url": None})
    assert srv_res.status_code == 201
    service_id = srv_res.json()["id"]

    # Create incident
    inc_payload = {
        "service_id": service_id,
        "title": "Elevated 500 error rates",
        "severity": "high",
        "status": "investigating",
    }
    inc_res = client.post("/incidents", json=inc_payload)
    assert inc_res.status_code == 201
    incident = inc_res.json()
    incident_id = incident["id"]
    assert incident["status"] == "investigating"
    assert incident["resolved_at"] is None

    # Patch incident to resolved
    patch_res = client.patch(f"/incidents/{incident_id}", json={"status": "resolved"})
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["status"] == "resolved"
    assert updated["resolved_at"] is not None


def test_prometheus_metrics_endpoint(client: TestClient):
    """Test metrics endpoint returns Prometheus formatted text."""
    # Generate some traffic
    client.get("/services")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text
