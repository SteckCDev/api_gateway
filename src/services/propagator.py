import json
import logging
import uuid
from typing import Final

import httpx
from fastapi import Request, Response
from fastapi.datastructures import Headers

from entities.auth import Token
from exceptions.exceptions import InvalidUrlError, ServiceUnavailableError, UnexpectedRequestFailError
from settings import config


logger = logging.getLogger(__name__)


SERVICE_ROUTES: Final[dict[str, str]] = {
    "check": "http://localhost:8080",
    "users": config.proxy.user_service_url,
    "events": config.proxy.event_service_url,
    "resumes": config.proxy.resume_service_url,
}


class RequestPropagationService:
    @staticmethod
    def get_request_id() -> uuid.UUID:
        return uuid.uuid4()

    @classmethod
    async def propagate(cls, request: Request, target_path: str, request_id: uuid.UUID, token_data: Token) -> Response:
        body = await request.body()
        origin_url = str(request.url)
        target_url = cls.__build_target_url(origin_url, target_path, request_id)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=cls.__get_updated_headers(request.headers, token_data.user_id, request_id),
                    params=request.query_params,
                    data=json.loads(body) if body else None,
                )
        except httpx.ConnectError as e:
            raise ServiceUnavailableError(target_url, request_id) from e
        except Exception as e:
            raise UnexpectedRequestFailError(request_id) from e

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response.headers,
        )

    @staticmethod
    def __build_target_url(origin: str, target_path: str, request_id: uuid.UUID) -> str:
        if len(protocol_separated := origin.split("://")) < 2:
            raise InvalidUrlError(origin, request_id)

        if len(host_separated := protocol_separated[1].split("/")) < 2:
            raise InvalidUrlError(origin, request_id)

        tag = host_separated[1]

        if (target_host := SERVICE_ROUTES.get(tag)) is None:
            raise InvalidUrlError(origin, request_id)

        return f"{target_host}/api/v1/{target_path.replace(f"{tag}/", "")}"

    @staticmethod
    def __get_updated_headers(headers: Headers, user_id: uuid.UUID, request_id: uuid.UUID) -> dict[str, str]:
        return {
            # CAUTION: unpack request headers first, otherwise x-headers may be overwritten by client which is
            # major security problem
            **dict(headers),
            "x-request-id": str(request_id),
            "x-user-id": str(user_id),
        }
