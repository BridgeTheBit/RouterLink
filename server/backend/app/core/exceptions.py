from fastapi import HTTPException, status


class RouterLinkException(Exception):
    """Base exception for RouterLink domain errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class QuotaExceededException(RouterLinkException):
    """Raised when user exceeds allocated data quota."""
    pass


class SubscriptionExpiredException(RouterLinkException):
    """Raised when user subscription has expired."""
    pass


class ConcurrentLimitException(RouterLinkException):
    """Raised when user exceeds allowed concurrent active sessions."""
    pass


class ProtocolNotAllowedException(RouterLinkException):
    """Raised when user attempts to connect using an unauthorized protocol."""
    pass


# Reusable HTTP Exceptions
class UnauthorizedHTTP(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenHTTP(HTTPException):
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class NotFoundHTTP(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class BadRequestHTTP(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

