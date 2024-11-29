import logging
from typing import Any, Final

from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions.exceptions import GatewayError


_UNAUTHENTICATED: Final[JSONResponse] = JSONResponse(
    content={"detail": "Unauthenticated"},
    status_code=401,
)
_UNAUTHORIZED: Final[JSONResponse] = JSONResponse(
    content={"detail": "Unauthorized"},
    status_code=403,
)
_NOT_FOUND: Final[JSONResponse] = JSONResponse(
    content={"detail": "Not found"},
    status_code=404,
)
_INTERNAL: Final[JSONResponse] = JSONResponse(
    content={"detail": "Internal server error"},
    status_code=500,
)


logger = logging.getLogger(__name__)


async def handle_401(request: Request, *args: Any) -> JSONResponse:
    _log_error(args)
    return _UNAUTHENTICATED


async def handle_403(request: Request, *args: Any) -> JSONResponse:
    _log_error(args)
    return _UNAUTHORIZED


async def handle_404(request: Request, *args: Any) -> JSONResponse:
    _log_error(args)
    return _NOT_FOUND


async def handle_500(request: Request, *args: Any) -> JSONResponse:
    _log_error(args, include_traceback=True)
    return _INTERNAL


def _log_error(args: tuple[Any, ...], *, include_traceback: bool = False) -> None:
    if len(args) < 1 or not isinstance(exc := args[0], GatewayError):
        return

    (logger.exception if include_traceback else logger.warning)(exc.message)
