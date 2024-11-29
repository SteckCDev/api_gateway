from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response

from entities.auth import Token
from services.auth import AuthService
from services.propagator import RequestPropagationService
from settings import HTTP_METHODS_TO_ACCEPT


v1_service_router = APIRouter(prefix="")


@v1_service_router.api_route("/{target:path}", methods=HTTP_METHODS_TO_ACCEPT)
async def service_handler(
    request: Request,
    target: str,
    request_id: UUID = Depends(RequestPropagationService.get_request_id),
    token_data: Token = Depends(AuthService.authenticate),
) -> Response:
    return await RequestPropagationService.propagate(request, target, request_id, token_data)
