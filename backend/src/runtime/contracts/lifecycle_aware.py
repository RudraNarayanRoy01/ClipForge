from abc import ABC, abstractmethod


class ILifecycleAware(ABC):
    """
    Contract for any Runtime component that needs to hook into the Runtime lifecycle.
    
    Implementing this interface ensures the component is notified during
    key phases of the Adaptive AI Runtime's lifecycle.
    """

    @abstractmethod
    def on_bootstrap(self) -> None:
        """
        Called when the Runtime is bootstrapping.
        Components should perform initial setup but should NOT execute AI workloads.
        """
        pass

    @abstractmethod
    def on_initialize(self) -> None:
        """
        Called when the Runtime has fully initialized and is ready for operation.
        """
        pass

    @abstractmethod
    def on_shutdown(self) -> None:
        """
        Called when the Runtime is gracefully shutting down.
        Components should release resources and flush any pending operations.
        """
        pass
