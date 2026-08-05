"""
Injection Validator.

Pure validation for the Runtime Injection Foundation.
Responsible only for structural correctness: duplicates, missing implementations,
circular dependencies, invalid scopes. Does NOT perform injection.
"""
from typing import Mapping, Set, Tuple

from .injection_descriptor import InjectionDescriptor
from .injection_exceptions import (
    CircularInjectionException,
    DuplicateBindingException,
    InvalidInjectionException,
    MissingImplementationException,
)
from .runtime_injection_binding import RuntimeInjectionBinding


class InjectionValidator:
    """
    Validates structural integrity of the injection blueprint.
    """

    def validate_bindings(self, bindings: Tuple[RuntimeInjectionBinding, ...]) -> None:
        """
        Validates that there are no duplicate interface implementations
        unless they are explicitly handled (e.g., via qualifiers or collections).
        For simplicity in this foundational layer, we enforce one binding per interface.
        """
        if not isinstance(bindings, tuple):
            raise InvalidInjectionException("Bindings must be a tuple.")

        seen_interfaces: Set[str] = set()
        for binding in bindings:
            if not isinstance(binding, RuntimeInjectionBinding):
                raise InvalidInjectionException("Invalid binding type detected.")
            if not binding.interface_id or not binding.implementation_id:
                raise InvalidInjectionException("Binding must have interface and implementation IDs.")
            
            # Simplified check: strictly one binding per interface for the baseline graph
            if binding.interface_id in seen_interfaces:
                raise DuplicateBindingException(f"Duplicate binding detected for interface: {binding.interface_id}")
            seen_interfaces.add(binding.interface_id)

    def validate_graph(
        self,
        bindings: Tuple[RuntimeInjectionBinding, ...],
        injection_graph: Mapping[str, Tuple[InjectionDescriptor, ...]]
    ) -> None:
        """
        Validates the dependency graph for missing implementations and circular dependencies.
        """
        if not isinstance(injection_graph, Mapping):
            raise InvalidInjectionException("Injection graph must be a Mapping.")

        available_services = {binding.interface_id for binding in bindings}

        # Validate descriptors
        for service_id, descriptors in injection_graph.items():
            if not isinstance(descriptors, tuple):
                raise InvalidInjectionException(f"Descriptors for {service_id} must be a tuple.")
            
            for descriptor in descriptors:
                if not isinstance(descriptor, InjectionDescriptor):
                    raise InvalidInjectionException("Invalid descriptor type detected.")
                
                # Check missing implementation
                if not descriptor.optional and descriptor.dependency_service not in available_services:
                    raise MissingImplementationException(
                        f"Missing required dependency: {descriptor.dependency_service} for {service_id}"
                    )

        # Validate Circular Dependencies using DFS
        self._detect_circular_dependencies(injection_graph)

    def _detect_circular_dependencies(
        self, injection_graph: Mapping[str, Tuple[InjectionDescriptor, ...]]
    ) -> None:
        """
        Performs DFS to detect cycles in the injection graph.
        """
        visited: Set[str] = set()
        recursion_stack: Set[str] = set()

        def dfs(node: str) -> None:
            visited.add(node)
            recursion_stack.add(node)

            descriptors = injection_graph.get(node, ())
            for descriptor in descriptors:
                neighbor = descriptor.dependency_service
                if neighbor not in visited:
                    if neighbor in injection_graph:
                        dfs(neighbor)
                elif neighbor in recursion_stack:
                    raise CircularInjectionException(
                        f"Circular dependency detected involving: {node} -> {neighbor}"
                    )
            
            recursion_stack.remove(node)

        for service_id in injection_graph:
            if service_id not in visited:
                dfs(service_id)
