class AppException(Exception):
    """Base application exception."""


class ConfigError(AppException):
    """Raised when required application config is missing or invalid."""


class DatabaseConnectionError(AppException):
    """Raised when the database cannot be reached."""
