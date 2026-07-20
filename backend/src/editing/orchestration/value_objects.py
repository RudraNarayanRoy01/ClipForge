from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionPreferences:
    """
    Immutable value object defining preferences for the orchestration execution.
    Establishes a typed extension point for execution modes, quality profiles, etc.
    """
    pass


@dataclass(frozen=True)
class ExecutionOptions:
    """
    Immutable value object defining options for the orchestration workflow.
    Establishes a typed extension point for orchestration flags.
    """
    pass


@dataclass(frozen=True)
class ExecutionMetadata:
    """
    Immutable value object defining metadata for the orchestration execution.
    Establishes a typed extension point for telemetry, tracing, etc.
    """
    pass


@dataclass(frozen=True)
class ExecutionDiagnostics:
    """
    Immutable value object defining diagnostics resulting from orchestration execution.
    Establishes a typed extension point for performance, tracing data, etc.
    """
    pass
