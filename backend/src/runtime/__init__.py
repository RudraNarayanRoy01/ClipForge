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
from .core.provider_capability_registry import ProviderCapabilityRegistry
from .core.model_registry import ModelRegistry
from .core.model_lifecycle_manager import ModelLifecycleManager
from .core.provider_health_manager import ProviderHealthManager
from .core.provider_failover_manager import ProviderFailoverManager
from .core.runtime_retry_manager import RuntimeRetryManager
from .core.runtime_scheduling_manager import RuntimeSchedulingManager
from .core.runtime_execution_manager import RuntimeExecutionManager
from .domain.provider_registry_model import (
    ProviderType,
    ProviderStatus,
    ProviderInfo,
    ProviderRegistryResult
)
from .domain.provider_capability_model import (
    CapabilityType,
    CapabilityLimits,
    ProviderCapability,
    ProviderCapabilityResult
)
from .domain.model_registry_model import (
    ModelType,
    ModelStatus,
    ModelInfo,
    ModelRegistryResult
)
from .domain.model_lifecycle_model import (
    ModelLifecycleState,
    ModelLifecycleTransition,
    ModelLifecycleInfo,
    ModelLifecycleResult
)
from .domain.provider_health_model import (
    ProviderHealthState,
    ProviderHealthTransition,
    ProviderHealthInfo,
    ProviderHealthResult
)
from .domain.provider_failover_model import (
    ProviderFailoverState,
    ProviderFailoverTrigger,
    ProviderFailoverDecision,
    ProviderFailoverInfo,
    ProviderFailoverResult
)
from .domain.runtime_retry_model import (
    RuntimeRetryState,
    RuntimeRetryTrigger,
    RuntimeRetryDecision,
    RuntimeRetryInfo,
    RuntimeRetryResult
)
from .domain.runtime_schedule_model import (
    RuntimeScheduleState,
    RuntimeScheduleTrigger,
    RuntimeScheduleDecision,
    RuntimeScheduleInfo,
    RuntimeScheduleResult
)
from .domain.runtime_execution_model import (
    RuntimeExecutionState,
    RuntimeExecutionTrigger,
    RuntimeExecutionDecision,
    RuntimeExecutionInfo,
    RuntimeExecutionResult
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
    "ProviderCapabilityRegistry",
    "ProviderType",
    "ProviderStatus",
    "ProviderInfo",
    "ProviderRegistryResult",
    "CapabilityType",
    "CapabilityLimits",
    "ProviderCapability",
    "ProviderCapabilityResult",
    "ModelRegistry",
    "ModelType",
    "ModelStatus",
    "ModelInfo",
    "ModelRegistryResult",
    "ModelLifecycleManager",
    "ModelLifecycleState",
    "ModelLifecycleTransition",
    "ModelLifecycleInfo",
    "ModelLifecycleResult",
    "ProviderHealthManager",
    "ProviderHealthState",
    "ProviderHealthTransition",
    "ProviderHealthInfo",
    "ProviderHealthResult",
    "ProviderFailoverManager",
    "ProviderFailoverState",
    "ProviderFailoverTrigger",
    "ProviderFailoverDecision",
    "ProviderFailoverInfo",
    "ProviderFailoverResult",
    "RuntimeRetryManager",
    "RuntimeRetryState",
    "RuntimeRetryTrigger",
    "RuntimeRetryDecision",
    "RuntimeRetryInfo",
    "RuntimeRetryResult",
    "RuntimeSchedulingManager",
    "RuntimeScheduleState",
    "RuntimeScheduleTrigger",
    "RuntimeScheduleDecision",
    "RuntimeScheduleInfo",
    "RuntimeScheduleResult",
    "RuntimeExecutionManager",
    "RuntimeExecutionState",
    "RuntimeExecutionTrigger",
    "RuntimeExecutionDecision",
    "RuntimeExecutionInfo",
    "RuntimeExecutionResult",
]
