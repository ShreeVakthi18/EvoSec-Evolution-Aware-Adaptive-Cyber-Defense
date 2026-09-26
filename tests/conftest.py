import os

# Set deterministic, test-friendly configuration BEFORE importing the app,
# since pydantic-settings reads the environment at import time.
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("CORS_ALLOW_ORIGINS", "http://testserver")
os.environ.setdefault("SUSPICIOUS_RESPONSE_DELAY_SECONDS", "0")  # keep tests fast
os.environ.setdefault("LOG_JSON", "false")

import pytest
from starlette.testclient import TestClient

from app.risk_engine import store
import main


@pytest.fixture(autouse=True)
def reset_state():
    """Every test starts from a clean behavioral state so scenarios don't
    bleed into one another (mirrors restarting the process)."""
    store.endpoint_stats.clear()
    store._user_behavior.clear()
    store._last_seen.clear()
    yield


def make_client(ip: str = "10.0.0.1") -> TestClient:
    """Create a TestClient that appears to originate from a distinct source
    IP, since EAACD's behavioral tracking keys off request.client.host."""
    return TestClient(main.app, client=(ip, 12345))


@pytest.fixture
def client():
    return make_client()
