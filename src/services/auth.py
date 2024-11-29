import uuid
from typing import Final

from fastapi import Request

from entities.auth import Token
from exceptions.exceptions import MissingTokenError


_AUTH_HEADER: Final[str] = "Authorization"
_AUTH_TOKEN_PREFIX: Final[str] = "Bearer "


class AuthService:
    @classmethod
    async def authenticate(cls, request: Request) -> Token:
        token = request.headers.get(_AUTH_HEADER)

        if token is None or not token.startswith(_AUTH_TOKEN_PREFIX):
            raise MissingTokenError()

        token.replace(_AUTH_TOKEN_PREFIX, "")

        return Token(user_id=uuid.uuid4())
