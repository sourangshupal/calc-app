"""Shared pytest fixtures."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from calc_app.main import create_app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Return a TestClient bound to a fresh app instance."""
    with TestClient(create_app()) as test_client:
        yield test_client
