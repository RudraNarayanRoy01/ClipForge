from abc import ABC, abstractmethod


class IRuntimeExtension(ABC):
    """
    Contract for a Runtime Extension.
    
    A Runtime Extension is a module (e.g., Capability Registry, Resource Discovery)
    that implements specific functionality and plugs into the Adaptive AI Runtime.
    """

    @property
    @abstractmethod
    def extension_name(self) -> str:
        """Return the unique name of this extension."""
        pass


class IRuntimeExtensionPoint(ABC):
    """
    Contract for a Runtime Extension Point.
    
    The Runtime owns Extension Points. Future modules implement IRuntimeExtension
    and register themselves against these extension points. This ensures the
    Runtime remains open for extension but closed for modification.
    """

    @abstractmethod
    def register_extension(self, extension: IRuntimeExtension) -> None:
        """Register an extension with this extension point."""
        pass
