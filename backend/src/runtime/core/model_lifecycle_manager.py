from typing import Dict, List, Optional
from datetime import datetime

from ..domain.model_lifecycle_model import (
    ModelLifecycleState,
    ModelLifecycleTransition,
    ModelLifecycleInfo,
    ModelLifecycleResult,
    MODEL_LIFECYCLE_TRANSITION_POLICY
)


class ModelLifecycleManager:
    """
    The purely declarative Model Lifecycle Manager for the AI Clipping Platform.
    
    Responsibilities:
    - Manage lifecycle state transitions for models
    - Validate transitions structurally against the immutable Transition Policy
    - Maintain canonical lifecycle history
    
    Ownership:
    - Owns Lifecycle State
    - Owns Lifecycle Transition
    - Owns Lifecycle Validation
    - Owns Lifecycle History
    
    MUST NOT:
    - Load or execute models
    - Schedule resources (GPU, CPU, Memory)
    - Perform failover or retry
    - Inspect ProviderHealth or RuntimeHealth
    - Define transition rules itself (consumes MODEL_LIFECYCLE_TRANSITION_POLICY)
    """

    def __init__(self) -> None:
        self._lifecycles: Dict[str, ModelLifecycleInfo] = {}

    def _validate_transition(self, current_state: ModelLifecycleState, next_state: ModelLifecycleState) -> bool:
        """
        Validate transition structurally using the centralized transition policy.
        """
        allowed_transitions = MODEL_LIFECYCLE_TRANSITION_POLICY.get(current_state, [])
        return next_state in allowed_transitions

    def register_model(self, model_id: str) -> ModelLifecycleResult:
        """
        Register a new model into the lifecycle tracking system.
        """
        if model_id in self._lifecycles:
            raise ValueError(f"Model lifecycle for '{model_id}' is already registered.")
        
        info = ModelLifecycleInfo(
            model_id=model_id,
            current_state=ModelLifecycleState.REGISTERED
        )
        self._lifecycles[model_id] = info
        
        return ModelLifecycleResult(
            lifecycle_info=info,
            operation_summary=f"Successfully registered model lifecycle for {model_id}.",
            validation_result=True
        )

    def get_lifecycle(self, model_id: str) -> ModelLifecycleInfo:
        """
        Retrieve the canonical lifecycle info.
        """
        if model_id not in self._lifecycles:
            raise KeyError(f"Lifecycle for model '{model_id}' not found.")
        return self._lifecycles[model_id]

    def get_state(self, model_id: str) -> ModelLifecycleState:
        """
        Retrieve just the current lifecycle state.
        """
        return self.get_lifecycle(model_id).current_state

    def transition_state(self, model_id: str, next_state: ModelLifecycleState, reason: str = "") -> ModelLifecycleResult:
        """
        Core transition logic. Applies the policy to determine if valid.
        """
        info = self.get_lifecycle(model_id)
        current_state = info.current_state
        
        if not self._validate_transition(current_state, next_state):
            raise ValueError(f"Invalid transition from {current_state.name} to {next_state.name} for model {model_id}.")
        
        transition = ModelLifecycleTransition(
            from_state=current_state,
            to_state=next_state,
            transition_reason=reason
        )
        
        updated_info = ModelLifecycleInfo(
            model_id=model_id,
            current_state=next_state,
            previous_state=current_state,
            last_transition=transition,
            transition_reason=reason,
            created_at=info.created_at,
            updated_at=datetime.utcnow()
        )
        
        self._lifecycles[model_id] = updated_info
        
        return ModelLifecycleResult(
            lifecycle_info=updated_info,
            operation_summary=f"Successfully transitioned model {model_id} to {next_state.name}.",
            validation_result=True
        )

    def initialize_model(self, model_id: str, reason: str = "Initializing model") -> ModelLifecycleResult:
        return self.transition_state(model_id, ModelLifecycleState.INITIALIZING, reason)

    def mark_ready(self, model_id: str, reason: str = "Model is ready") -> ModelLifecycleResult:
        return self.transition_state(model_id, ModelLifecycleState.READY, reason)

    def mark_busy(self, model_id: str, reason: str = "Model is busy executing") -> ModelLifecycleResult:
        return self.transition_state(model_id, ModelLifecycleState.BUSY, reason)

    def mark_idle(self, model_id: str, reason: str = "Model is idle") -> ModelLifecycleResult:
        return self.transition_state(model_id, ModelLifecycleState.IDLE, reason)

    def start_update(self, model_id: str, reason: str = "Model updating") -> ModelLifecycleResult:
        return self.transition_state(model_id, ModelLifecycleState.UPDATING, reason)

    def finish_update(self, model_id: str, reason: str = "Update complete, returning to ready") -> ModelLifecycleResult:
        return self.transition_state(model_id, ModelLifecycleState.READY, reason)

    def deprecate_model(self, model_id: str, reason: str = "Model deprecated") -> ModelLifecycleResult:
        return self.transition_state(model_id, ModelLifecycleState.DEPRECATED, reason)

    def disable_model(self, model_id: str, reason: str = "Model disabled") -> ModelLifecycleResult:
        return self.transition_state(model_id, ModelLifecycleState.DISABLED, reason)

    def remove_model(self, model_id: str, reason: str = "Model removed") -> ModelLifecycleResult:
        return self.transition_state(model_id, ModelLifecycleState.REMOVED, reason)
