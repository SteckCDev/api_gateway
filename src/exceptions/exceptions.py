from uuid import UUID


class GatewayError(Exception):
    def __init__(self, message: str, request_id: UUID | None = None) -> None:
        self.message = message

        if request_id is not None:
            self.message += f" ({request_id=})"

        super().__init__(self.message)


class UnauthenticatedError(GatewayError): ...


class UnauthorizedError(GatewayError): ...


class InvalidTokenError(UnauthenticatedError):
    def __init__(self, request_id: UUID) -> None:
        self.message: str = "Authorization token is invalid"
        super().__init__(self.message)


class MissingTokenError(UnauthenticatedError):
    def __init__(self) -> None:
        self.message: str = "Authorization token is missing"
        super().__init__(self.message)


class PropagationError(GatewayError): ...


class InvalidUrlError(PropagationError):
    def __init__(self, origin_url: str, request_id: UUID) -> None:
        self.message = f"Invalid URL: {origin_url}"
        super().__init__(self.message)


class ServiceRequestError(PropagationError): ...


class ServiceUnavailableError(ServiceRequestError):
    def __init__(self, target_url: str, request_id: UUID) -> None:
        self.message = f"Requested service is unavailable: {target_url}"
        super().__init__(self.message)


class UnexpectedRequestFailError(ServiceRequestError):
    def __init__(self, request_id: UUID) -> None:
        self.message = "Request failed for not known reason"
        super().__init__(self.message)
