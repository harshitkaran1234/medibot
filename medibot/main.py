from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from medibot.client import dependency
from medibot.common import config
from medibot.common.exception_handler import (
    base_exception_handler,
    custom_http_exception,
    custom_http_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await dependency.init()
    yield

    await dependency.close()


def register_handlers(app: FastAPI) -> None:
    app.add_exception_handler(custom_http_exception, custom_http_exception_handler)
    app.add_exception_handler(Exception, base_exception_handler)


def create_app() -> FastAPI:
    current_app = FastAPI(
        title="Medibot",
        lifespan=lifespan,
    )

    current_app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ALLOWED_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    from medibot.routes import router

    current_app.include_router(router)
    register_handlers(current_app)
    return current_app


app = create_app()
