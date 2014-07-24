class BaseError(Exception):
    """Base class for all application errors."""
    pass


class InputFileError(BaseError):
    """Raised when there is trouble reading an input file."""
    pass
