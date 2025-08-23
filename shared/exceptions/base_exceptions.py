"""Base exception classes for the application."""

class BaseApplicationException(Exception):
    """Base exception for all application-specific exceptions."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationException(BaseApplicationException):
    """Raised when data validation fails."""
    pass


class AuthenticationException(BaseApplicationException):
    """Raised when authentication fails."""
    pass


class AuthorizationException(BaseApplicationException):
    """Raised when authorization fails."""
    pass


class ResourceNotFoundException(BaseApplicationException):
    """Raised when a requested resource is not found."""
    pass


class ResourceConflictException(BaseApplicationException):
    """Raised when a resource conflict occurs."""
    pass


class ExternalServiceException(BaseApplicationException):
    """Raised when an external service call fails."""
    pass