import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi_csrf_protect import CsrfProtect
from src.config import settings
from src.database import Base, engine
from starlette.middleware.sessions import SessionMiddleware
from fastapi.exceptions import ResponseValidationError
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from contextlib import asynccontextmanager

logger = logging.getLogger("uvicorn.error")


class CsrfSettings(BaseSettings):
    secret_key: str = settings.csrf_secret


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


class RedirectException(Exception):
    def __init__(self, path: str, message: str|None = None):
        self.path = path
        self.message = message

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Checking tables...")

    Base.metadata.create_all(bind=engine)  # ✅ creates missing tables
    yield
    print("end")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Todo API",
        description="This is a sample FastAPI app for managing todos.",
        version="1.0.0",
        docs_url="/swagger",  # Swagger UI at /swagger
        redoc_url=None,  # Disable ReDoc
        openapi_url="/api/openapi.json",  # OpenAPI schema at /api/openapi.json
        default_response_class=JSONResponse,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1
        },  # Collapse models by default)
        lifespan=lifespan,
    )
    # Use a strong random secret key (can also load from .env)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key.get_secret_value(),
        session_cookie="session",  # optional, default "session"
        max_age=3600,  # optional, 1 hour
        same_site="lax",  # optional
    )
    @app.exception_handler(RedirectException)
    async def redirect_exception_handler(request: Request, exc: RedirectException):
        # Attach message as query parameter
        if exc.message:
            return RedirectResponse(url=f"{exc.path}?message={exc.message}", status_code=303)
        return RedirectResponse(url=exc.path, status_code=303)

    @app.get("/protected", include_in_schema=False)
    def protected():
        raise RedirectException("/login", "You must log in first!")
    # @app.exception_handler(RedirectException)
    # async def redirect_exception_handler(request: Request, exc: RedirectException):
        return RedirectResponse(exc.path, status_code=303)
    @app.exception_handler(ResponseValidationError)
    async def response_validation_exception_handler(
        request: Request, exc: ResponseValidationError
    ):
        logger.error(f"Response validation error: {exc.errors()} | Body: {exc.body}")
        return JSONResponse(
            status_code=500,
            content={"detail": exc.errors(), "body": str(exc.body)},
        )

    from src.user import users_router
    # from src.api import api_router
    from src.apiv3 import api_router
    app.include_router(users_router)
    app.include_router(api_router)

    return app
