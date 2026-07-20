class MatchingException(Exception):
    """Base exception for all matching-related errors."""
    pass


class InvalidMatchRequest(MatchingException):
    """Raised when a match request is mathematically or logically invalid."""
    pass


class InvalidMatchingScope(MatchingException):
    """Raised when an invalid matching scope is provided."""
    pass
