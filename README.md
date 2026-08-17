# Calculator API

FastAPI calculator with a browser UI at `/`. Four `POST` operations plus a health check. OpenAPI UI is at `/docs`.

## Install

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Run

```bash
uv run uvicorn calc_app.main:app --reload
```

Then open http://127.0.0.1:8000/ for the calculator UI, or http://127.0.0.1:8000/docs for OpenAPI.

## Example

```bash
curl -X POST http://127.0.0.1:8000/add \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 2}'
```

```json
{"operation": "add", "a": 10.0, "b": 2.0, "result": 12.0}
```

Other routes: `POST /subtract`, `POST /multiply`, `POST /divide` with the same `{"a", "b"}` body. `GET /health` returns `{"status": "ok"}`. Divide by zero returns HTTP 400.

## Tests

```bash
uv run pytest
uv run ruff check src tests
```
