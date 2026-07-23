from typing import TypeVar, Type, Callable, Dict, Any, Union, Set
import inspect

T = TypeVar('T')

class CircularDependencyError(Exception):
    pass

class Container:
    """
    Lightweight, framework-agnostic Dependency Injection Container.
    Handles Singletons, Transients, and Constructor-based resolution.
    """
    def __init__(self, parent: 'Container' = None):
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[['Container'], Any]] = {}
        self._transients: Dict[Type, Callable[['Container'], Any]] = {}
        self._resolution_stack: Set[Type] = set()
        self._parent = parent

    def create_child(self) -> 'Container':
        """Create a child container that falls back to this container."""
        return Container(parent=self)

    def register_singleton(self, interface: Type[T], implementation: Union[Type[T], T]) -> None:
        """Register a class or instance as a singleton."""
        if isinstance(implementation, type):
            self._factories[interface] = lambda c: self._build(implementation)
        else:
            self._singletons[interface] = implementation

    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a class to be instantiated freshly on every resolution."""
        self._transients[interface] = lambda c: self._build(implementation)
        
    def register_factory(self, interface: Type[T], factory: Callable[['Container'], T], singleton: bool = True) -> None:
        """Register a custom factory function."""
        if singleton:
            self._factories[interface] = factory
        else:
            self._transients[interface] = factory

    def resolve(self, interface: Type[T]) -> T:
        """Resolve a dependency by its interface/type."""
        interface_name = interface if isinstance(interface, str) else getattr(interface, '__name__', str(interface))
        
        if interface in self._resolution_stack:
            raise CircularDependencyError(f"Circular dependency detected for {interface_name}")
            
        if interface in self._singletons:
            return self._singletons[interface]
            
        self._resolution_stack.add(interface)
        
        try:
            if interface in self._factories:
                instance = self._factories[interface](self)
                self._singletons[interface] = instance
                return instance
                
            if interface in self._transients:
                return self._transients[interface](self)
                
            if self._parent is not None:
                return self._parent.resolve(interface)
                
            raise KeyError(f"No registration found for {interface_name}")
        finally:
            self._resolution_stack.remove(interface)
            
    def _build(self, implementation: Type) -> Any:
        """Automatically build an instance using constructor type hints."""
        import typing
        
        try:
            signature = inspect.signature(implementation.__init__)
        except (TypeError, ValueError):
            # Built-in or no __init__
            return implementation()
            
        try:
            # Resolve string forward references
            hints = typing.get_type_hints(implementation.__init__)
        except Exception:
            hints = {}
            
        kwargs = {}
        
        for name, param in signature.parameters.items():
            if name == 'self' or name == 'args' or name == 'kwargs':
                continue
                
            annotation = hints.get(name, param.annotation)
            
            if annotation == inspect.Parameter.empty:
                # If there's a default, skip injection
                if param.default != inspect.Parameter.empty:
                    continue
                raise ValueError(f"Cannot resolve parameter '{name}' of {implementation.__name__} without type hints")
                
            kwargs[name] = self.resolve(annotation)
            
        return implementation(**kwargs)
