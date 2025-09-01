from fastapi import HTTPException, status

class DomainError(Exception):
    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.message = message
        self.code = code or status.HTTP_400_BAD_REQUEST

class NotFoundError(DomainError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class ConflictError(DomainError):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)

def to_http(exc: DomainError) -> HTTPException:
    return HTTPException(status_code=exc.code, detail=exc.message)
