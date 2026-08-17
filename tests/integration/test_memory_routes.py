"""Integration tests for calculator memory HTTP routes."""

from fastapi.testclient import TestClient


def test_memory_starts_empty(client: TestClient) -> None:
    response = client.get("/memory")
    assert response.status_code == 200
    assert response.json() == {"register": 0.0, "history": []}


def test_successful_calculation_is_recorded(client: TestClient) -> None:
    add = client.post("/add", json={"a": 10, "b": 2})
    assert add.status_code == 200

    memory = client.get("/memory")
    assert memory.status_code == 200
    body = memory.json()
    assert len(body["history"]) == 1
    entry = body["history"][0]
    assert entry["operation"] == "add"
    assert entry["a"] == 10.0
    assert entry["b"] == 2.0
    assert entry["result"] == 12.0
    assert entry["at"]


def test_divide_by_zero_is_not_recorded(client: TestClient) -> None:
    response = client.post("/divide", json={"a": 10, "b": 0})
    assert response.status_code == 400
    memory = client.get("/memory")
    assert memory.json()["history"] == []


def test_sqrt_is_recorded(client: TestClient) -> None:
    response = client.post("/sqrt", json={"a": 16})
    assert response.status_code == 200

    memory = client.get("/memory")
    assert memory.status_code == 200
    entry = memory.json()["history"][0]
    assert entry["operation"] == "sqrt"
    assert entry["a"] == 16.0
    assert entry["b"] is None
    assert entry["result"] == 4.0


def test_sqrt_negative_is_not_recorded(client: TestClient) -> None:
    response = client.post("/sqrt", json={"a": -9})
    assert response.status_code == 400
    memory = client.get("/memory")
    assert memory.json()["history"] == []


def test_memory_plus_and_minus(client: TestClient) -> None:
    plus = client.post("/memory/plus", json={"value": 5})
    assert plus.status_code == 200
    assert plus.json()["register"] == 5.0

    minus = client.post("/memory/minus", json={"value": 2})
    assert minus.status_code == 200
    assert minus.json()["register"] == 3.0
    assert client.get("/memory").json()["register"] == 3.0


def test_clear_register(client: TestClient) -> None:
    client.post("/memory/plus", json={"value": 9})
    client.post("/add", json={"a": 1, "b": 1})
    response = client.delete("/memory/register")
    assert response.status_code == 200
    body = response.json()
    assert body["register"] == 0.0
    assert len(body["history"]) == 1


def test_clear_history(client: TestClient) -> None:
    client.post("/memory/plus", json={"value": 4})
    client.post("/multiply", json={"a": 2, "b": 3})
    response = client.delete("/memory/history")
    assert response.status_code == 200
    body = response.json()
    assert body["history"] == []
    assert body["register"] == 4.0


def test_memory_value_must_be_finite(client: TestClient) -> None:
    response = client.post("/memory/plus", json={"value": "inf"})
    assert response.status_code == 422
