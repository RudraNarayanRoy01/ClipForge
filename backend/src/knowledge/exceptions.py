class KnowledgeError(Exception):
    """Base exception for all knowledge-related errors."""
    pass

class KnowledgeNotFound(KnowledgeError):
    """Raised when no knowledge snapshots exist for a given video."""
    pass

class KnowledgeUnavailable(KnowledgeError):
    """Raised when knowledge exists but is in a state that cannot be consumed."""
    pass

class KnowledgeVersionNotFound(KnowledgeError):
    """Raised when a specific version of knowledge was requested but not found."""
    pass
