"""
Runtime Dependency Exceptions.

This module defines the dedicated exception hierarchy for the Dependency Graph.
It strictly avoids reusing Registry exceptions to maintain clear ownership boundaries.
"""

class DependencyGraphException(Exception):
    """Base exception for all Dependency Graph errors."""
    pass

class DuplicateDependencyException(DependencyGraphException):
    """Raised when attempting to register a dependency that already exists."""
    pass

class DependencyCycleException(DependencyGraphException):
    """Raised when a dependency cycle is detected in the graph."""
    pass

class MissingComponentException(DependencyGraphException):
    """Raised when a required component is missing from the graph."""
    pass

class InvalidDependencyException(DependencyGraphException):
    """Raised when a dependency registration is invalid."""
    pass

class GraphFrozenException(DependencyGraphException):
    """Raised when attempting to modify a frozen graph."""
    pass

class TraversalException(DependencyGraphException):
    """Raised when an error occurs during graph traversal."""
    pass
