from fastapi import HTTPException, status

class MisEventosException(HTTPException):
    """Base exception for Mis Eventos application"""
    pass

class CredentialsException(MisEventosException):
    def __init__(
        self,
        detail: str = "Could not validate credentials",
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class NotFoundException(MisEventosException):
    def __init__(
        self,
        detail: str = "Resource not found",
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )

class ForbiddenException(MisEventosException):
    def __init__(
        self,
        detail: str = "Not enough permissions",
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

class BadRequestException(MisEventosException):
    def __init__(
        self,
        detail: str = "Bad request",
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

class ConflictException(MisEventosException):
    def __init__(
        self,
        detail: str = "Conflict",
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

class EmailAlreadyRegisteredError(ConflictException):
    def __init__(self):
        super().__init__(detail="Email already registered")

class UserNotFoundError(NotFoundException):
    def __init__(self):
        super().__init__(detail="User not found")

class InvalidPasswordError(BadRequestException):
    def __init__(self):
        super().__init__(detail="Invalid password")