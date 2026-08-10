import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture(scope="session")
def client():
    """
    Canonical TestClient fixture for API tests.
    Ensures the FastAPI lifespan (startup/shutdown) is executed for every test,
    properly initializing app.state.container and other resources.
    """
    with TestClient(app) as test_client:
        yield test_client
