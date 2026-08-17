"""Shared pytest fixtures."""

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from calc_app.main import create_app


@pytest.fixture
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    """Return a TestClient bound to a fresh app with isolated memory file."""
    with TestClient(create_app(memory_path=tmp_path / "memory.json")) as test_client:
        yield test_client
