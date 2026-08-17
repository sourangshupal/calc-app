"""Integration tests for calculator HTTP routes."""


def test_add(client) -> None:
    response = client.post("/add", json={"a": 10, "b": 2})
    assert response.status_code == 200
    body = response.json()
    assert body["operation"] == "add"
    assert body["a"] == 10.0
    assert body["b"] == 2.0
    assert body["result"] == 12.0


def test_subtract(client) -> None:
    response = client.post("/subtract", json={"a": 10, "b": 2})
    assert response.status_code == 200
    body = response.json()
    assert body["operation"] == "subtract"
    assert body["result"] == 8.0


def test_multiply(client) -> None:
    response = client.post("/multiply", json={"a": 10, "b": 2})
    assert response.status_code == 200
    body = response.json()
    assert body["operation"] == "multiply"
    assert body["result"] == 20.0


def test_divide(client) -> None:
    response = client.post("/divide", json={"a": 10, "b": 4})
    assert response.status_code == 200
    body = response.json()
    assert body["operation"] == "divide"
    assert body["result"] == 2.5


def test_divide_by_zero(client) -> None:
    response = client.post("/divide", json={"a": 10, "b": 0})
    assert response.status_code == 400
    assert "Division by zero" in response.json()["detail"]


def test_non_numeric_body(client) -> None:
    response = client.post("/add", json={"a": "x", "b": 2})
    assert response.status_code == 422


def test_infinite_operands_rejected(client) -> None:
    response = client.post("/add", json={"a": "inf", "b": 1})
    assert response.status_code == 422


def test_nan_operands_rejected(client) -> None:
    response = client.post("/add", json={"a": "nan", "b": 1})
    assert response.status_code == 422


def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_html(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<title>Calculator</title>" in response.text


def test_static_assets(client) -> None:
    js_response = client.get("/static/app.js")
    css_response = client.get("/static/styles.css")
    assert js_response.status_code == 200
    assert css_response.status_code == 200
