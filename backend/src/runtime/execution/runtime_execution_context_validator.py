from typing import Tuple
from .runtime_execution_variable import RuntimeExecutionVariable
from .runtime_execution_binding import RuntimeExecutionBinding
from .runtime_execution_exceptions import (
    ExecutionValidationException
)

class RuntimeExecutionContextValidator:
    """
    Validates structural integrity of the Runtime Execution Context.
    
    Explicitly Validates:
    - Duplicate identifiers
    - Broken bindings
    - Lookup consistency
    - Missing variables
    - Missing references
    - Structural integrity
    
    NEVER Validates:
    - Execution
    - Scheduling
    - Planning
    - Optimization
    - Dependency Resolution
    - Provider Routing
    - Lifecycle
    - Execution Behaviour
    """
    
    @staticmethod
    def validate_variables(variables: Tuple[RuntimeExecutionVariable, ...]) -> None:
        identifiers = set()
        for variable in variables:
            if variable.identifier in identifiers:
                raise ExecutionValidationException(f"Duplicate variable identifier: {variable.identifier}")
            identifiers.add(variable.identifier)

    @staticmethod
    def validate_bindings(
        bindings: Tuple[RuntimeExecutionBinding, ...],
        variables: Tuple[RuntimeExecutionVariable, ...]
    ) -> None:
        identifiers = set()
        variable_ids = {var.identifier for var in variables}
        
        for binding in bindings:
            if binding.identifier in identifiers:
                raise ExecutionValidationException(f"Duplicate binding identifier: {binding.identifier}")
            identifiers.add(binding.identifier)
            
            if binding.source_identifier not in variable_ids:
                raise ExecutionValidationException(
                    f"Binding {binding.identifier} references missing source variable: {binding.source_identifier}"
                )
            if binding.target_identifier not in variable_ids:
                raise ExecutionValidationException(
                    f"Binding {binding.identifier} references missing target variable: {binding.target_identifier}"
                )

    @staticmethod
    def validate_context_state(
        descriptor: "RuntimeExecutionContextDescriptor",
        variables: Tuple[RuntimeExecutionVariable, ...],
        bindings: Tuple[RuntimeExecutionBinding, ...]
    ) -> None:
        if not descriptor:
            raise ExecutionValidationException("Context descriptor is missing")
        RuntimeExecutionContextValidator.validate_variables(variables)
        RuntimeExecutionContextValidator.validate_bindings(bindings, variables)
