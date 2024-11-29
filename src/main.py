import logging
import logging.config
from collections.abc import AsyncGenerator, Callable, Coroutine
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
import yaml
from fastapi import FastAPI, Request, Response
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from api import service_routers
from exceptions.exceptions import (
    InvalidUrlError,
    UnauthenticatedError,
    UnauthorizedError,
    UnexpectedRequestFailError,
)
from exceptions.handlers import handle_401, handle_403, handle_404, handle_500
from settings import LOGGING_CONFIG_PATH, Config


logger = logging.getLogger(__name__)


def get_configured_fastapi_app(config: Config = Config()) -> FastAPI:
    setup_logging(config)

    app = FastAPI(
        title="Alabuga Career / API-gateway",
        description="Career's API-gateway which stand for initial handling of all requests",
        debug=config.app.debug,
        lifespan=lifespan,
        middleware=get_middleware(config),
        exception_handlers=get_exception_handlers(),
        root_path="/api/v1",
        openapi_url="/openapi.json" if config.app.enable_swagger else None,
        docs_url="/docs" if config.app.enable_swagger else None,
        redoc_url="/redoc" if config.app.enable_swagger else None,
        version=config.app.version,
    )

    include_routers(app)

    return app


def setup_logging(config: Config) -> None:
    with open(LOGGING_CONFIG_PATH) as file:
        loaded_config = yaml.safe_load(file)
        loaded_config.setdefault("root", {})["level"] = config.app.log_level
        logging.config.dictConfig(loaded_config)

    logging.basicConfig(level=config.app.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application is starting up")
    ...
    logger.info("Application started up")

    yield

    logger.info("Application is gentle-shutting down")
    ...
    logger.info("Application gentle-shuted down")


def get_middleware(config: Config) -> list[Middleware]:
    return [
        Middleware(
            cls=CORSMiddleware,
            allow_origins=config.cors.allow_origins,
            allow_credentials=config.cors.allow_credentials,
            allow_methods=config.cors.allow_methods,
            allow_headers=config.cors.allow_headers,
        )
    ]


def get_exception_handlers() -> dict[int | type[Exception], Callable[[Request, Any], Coroutine[Any, Any, Response]]]:
    return {
        UnauthenticatedError: handle_401,
        UnauthorizedError: handle_403,
        InvalidUrlError: handle_404,
        UnexpectedRequestFailError: handle_500,
    }


def include_routers(app: FastAPI) -> None:
    for router in service_routers:
        app.include_router(router)


def main() -> None:
    config = Config()

    uvicorn.run(
        app=get_configured_fastapi_app(config),
        host=config.app.host,
        port=config.app.port,
        reload=config.app.debug,
        log_level=config.app.log_level.lower(),
    )


if __name__ == "__main__":
    main()
