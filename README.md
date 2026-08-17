# Calculator API

FastAPI calculator with a browser UI at `/`. Five `POST` operations plus a health check. OpenAPI UI is at `/docs`.

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

```bash
curl -X POST http://127.0.0.1:8000/sqrt \
  -H "Content-Type: application/json" \
  -d '{"a": 9}'
```

```json
{"operation": "sqrt", "a": 9.0, "b": null, "result": 3.0}
```

Other binary routes: `POST /subtract`, `POST /multiply`, `POST /divide` with the same `{"a", "b"}` body. Square root is unary: `POST /sqrt` with `{"a": 9}`. `GET /health` returns `{"status": "ok"}`. Divide by zero and square root of a negative number return HTTP 400.

## Memory

Successful calculations are stored on a history tape. Classic memory keys live on the UI (`MC`, `MR`, `M+`, `M−`). Both persist in `data/memory.json` (created on first use, gitignored). Newest 100 history entries are kept.

```bash
curl http://127.0.0.1:8000/memory
curl -X POST http://127.0.0.1:8000/memory/plus \
  -H "Content-Type: application/json" \
  -d '{"value": 12}'
curl -X POST http://127.0.0.1:8000/memory/minus \
  -H "Content-Type: application/json" \
  -d '{"value": 2}'
curl -X DELETE http://127.0.0.1:8000/memory/register
curl -X DELETE http://127.0.0.1:8000/memory/history
```

`GET /memory` returns `{"register": 0.0, "history": [...]}`. Tap a history row in the UI to load that result into the display.

## Tests

```bash
uv run pytest
uv run ruff check src tests
```
