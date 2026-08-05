"""
Dependency Type enum for the Runtime Dependency Graph.

Pure metadata representing the type of relationship between components.
"""

from enum import Enum, auto

class DependencyType(Enum):
    """
    Defines the semantics of a component dependency.
    """
    REQUIRED = auto()
    OPTIONAL = auto()
    INITIALIZATION = auto()
    STARTUP = auto()
    CONFIGURATION = auto()
    OBSERVATION = auto()
