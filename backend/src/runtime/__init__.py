"""
Adaptive AI Runtime

This subsystem acts as the sole orchestrator for all AI computation within the 
ClipForge platform. It abstracts away specific AI providers (Ollama, Gemini, OpenAI) 
and hardware considerations (CUDA, VRAM) from the core Application layer.

It ensures that the application only requests Capabilities (e.g. "Reasoning"), 
leaving the Runtime to determine the optimal Provider and Schedule for execution.
"""

from .core import RuntimeBootstrap, RuntimeLifecycleState, RuntimeContext, RuntimeMetadata, RuntimeLifecycle
from .core.lifecycle_model import (
    LifecycleResult,
    LifecycleState,
    LifecycleStage,
    LifecycleSummary,
    LifecycleIdentity,
    LifecycleTransition
)
from .core.provider_registry import ProviderRegistry
from .domain.provider_registry_model import (
    ProviderType,
    ProviderStatus,
    ProviderInfo,
    ProviderRegistryResult
)
from .core.execution_model import (
    ExecutionIdentity,
    ExecutionRequest,
    ExecutionPriority
)
from .core.execution_result_model import (
    ExecutionStatus,
    ExecutionOutcome,
    ExecutionSummary,
    ExecutionResult
)
from .contracts import ILifecycleAware

__all__ = [
    "RuntimeBootstrap",
    "ExecutionIdentity",
    "ExecutionRequest",
    "ExecutionPriority",
    "ExecutionStatus",
    "ExecutionOutcome",
    "ExecutionSummary",
    "ExecutionResult",
    "LifecycleResult",
    "LifecycleState",
    "LifecycleStage",
    "LifecycleSummary",
    "LifecycleIdentity",
    "LifecycleTransition",
    "RuntimeLifecycleState",
    "RuntimeLifecycle",
    "RuntimeContext",
    "RuntimeMetadata",
    "ILifecycleAware",
    "ProviderRegistry",
    "ProviderType",
    "ProviderStatus",
    "ProviderInfo",
    "ProviderRegistryResult",
]
