"""
Dependency Direction enum.

Defines the direction of traversal or querying within the graph.
"""

from enum import Enum, auto

class DependencyDirection(Enum):
    """
    Direction for traversal and resolution.
    """
    FORWARD = auto()  # From dependants to their dependencies (what does A depend on?)
    REVERSE = auto()  # From dependencies to their dependants (what depends on A?)
