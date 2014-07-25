class BaseError(Exception):
    """Base class for all application errors."""
    pass


class InputFileError(BaseError):
    """Raised when there is trouble reading an input file."""
    pass


class InvalidServerError(BaseError):
    """Raised when a bad server number is given."""
    pass


class ServerStopError(BaseError):
    """Raised when a server does not stop within MAX_TRIES."""
    pass
