"""FastAPI application factory."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from yojenkins import __version__
from yojenkins.api.auth import router as auth_router
from yojenkins.api.routers.builds import router as builds_router
from yojenkins.api.routers.folders import router as folders_router
from yojenkins.api.routers.jobs import router as jobs_router
from yojenkins.api.routers.server import router as server_router
from yojenkins.api.websocket import router as ws_router
from yojenkins.yo_jenkins.exceptions import (
    AuthenticationError,
    NotFoundError,
    RequestError,
    ValidationError,
    YoJenkinsException,
)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="yojenkins",
        description="Web API for managing Jenkins servers",
        version=__version__,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(server_router, prefix="/api/server", tags=["server"])
    app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])
    app.include_router(builds_router, prefix="/api/builds", tags=["builds"])
    app.include_router(folders_router, prefix="/api/folders", tags=["folders"])
    app.include_router(ws_router, prefix="/api/ws", tags=["websocket"])

    # Exception handlers
    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(RequestError)
    async def request_error_handler(request: Request, exc: RequestError):
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.exception_handler(YoJenkinsException)
    async def generic_handler(request: Request, exc: YoJenkinsException):
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    return app


# Module-level app instance for uvicorn: `uvicorn yojenkins.api.app:app`
app = create_app()
