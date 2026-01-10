"""
Custom HTTP exceptions for the application.
"""
from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Raised when a resource is not found."""
    
    def __init__(self, resource_name: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name} with id '{resource_id}' not found"
        )


class ForbiddenException(HTTPException):
    """Raised when user doesn't have permission."""
    
    def __init__(self, detail: str = "You don't have permission to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class BadRequestException(HTTPException):
    """Raised when request is invalid."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class ValidationException(HTTPException):
    """Raised when data validation fails."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
