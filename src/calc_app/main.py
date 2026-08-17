"""FastAPI application factory and ASGI entrypoint."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from calc_app.api.routes import router

STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    """Build and return the calculator FastAPI application."""
    application = FastAPI(title="Calculator API")
    application.include_router(router)

    @application.get("/health")
    def health() -> dict[str, str]:
        """Liveness probe."""
        return {"status": "ok"}

    @application.get("/", include_in_schema=False)
    def index() -> FileResponse:
        """Serve the calculator browser UI."""
        return FileResponse(STATIC_DIR / "index.html")

    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    return application


app = create_app()
