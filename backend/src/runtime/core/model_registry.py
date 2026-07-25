from typing import Dict, List
from ..domain.model_registry_model import ModelInfo, ModelRegistryResult, ModelType

class ModelRegistry:
    """
    The canonical metadata registry for Model Identity in the AI Clipping Platform.
    
    Responsibilities:
    - register_model()
    - update_model()
    - remove_model()
    - get_model()
    - list_models()
    - model_exists()
    - list_models_for_provider()
    - list_models_by_type()
    
    Ownership:
    - Owns ModelInfo
    - Owns ModelType
    - Owns ModelStatus
    - Produces ModelRegistryResult
    
    MUST NOT:
    - Load, initialize, execute, evaluate, or compare models.
    - Rank models or select models.
    - Route requests.
    - Manage lifecycle, health, or failover.
    - Perform reasoning, scheduling, or optimization.
    
    It only answers "What models are available?". 
    It never answers "Which model should I use?".
    """
    def __init__(self) -> None:
        self._models: Dict[str, ModelInfo] = {}

    def register_model(self, model_info: ModelInfo) -> ModelRegistryResult:
        """
        Register a new model identity.
        Raises ValueError if a model with the same identity is already registered.
        """
        if model_info.model_id in self._models:
            raise ValueError(f"Model '{model_info.model_id}' is already registered.")
        
        self._models[model_info.model_id] = model_info
        
        return ModelRegistryResult(
            registered_models=[model_info],
            operation_summary=f"Successfully registered model {model_info.model_id}.",
            validation_result=True
        )

    def update_model(self, model_info: ModelInfo) -> ModelRegistryResult:
        """
        Update an existing model identity.
        Raises KeyError if the model is not registered.
        """
        if model_info.model_id not in self._models:
            raise KeyError(f"Model '{model_info.model_id}' is not registered.")
        
        self._models[model_info.model_id] = model_info
        
        return ModelRegistryResult(
            registered_models=[model_info],
            operation_summary=f"Successfully updated model {model_info.model_id}.",
            validation_result=True
        )

    def remove_model(self, model_id: str) -> ModelRegistryResult:
        """
        Remove a model's registration.
        Raises KeyError if not found.
        """
        if model_id not in self._models:
            raise KeyError(f"Model '{model_id}' is not registered.")
        
        model_info = self._models.pop(model_id)
        
        return ModelRegistryResult(
            registered_models=[model_info],
            operation_summary=f"Successfully removed model {model_id}.",
            validation_result=True
        )

    def get_model(self, model_id: str) -> ModelInfo:
        """
        Lookup a model registration by its identity.
        Raises KeyError if not found.
        """
        if model_id not in self._models:
            raise KeyError(f"Model '{model_id}' is not registered.")
        return self._models[model_id]

    def list_models(self) -> List[ModelInfo]:
        """
        Return a list of all current model identities.
        """
        return list(self._models.values())

    def model_exists(self, model_id: str) -> bool:
        """
        Check if a model identity is registered.
        """
        return model_id in self._models

    def list_models_for_provider(self, provider_id: str) -> List[ModelInfo]:
        """
        Return a list of all current model identities for a specific provider.
        """
        return [model for model in self._models.values() if model.provider_id == provider_id]
        
    def list_models_by_type(self, model_type: ModelType) -> List[ModelInfo]:
        """
        Return a list of all current model identities for a specific model type.
        """
        return [model for model in self._models.values() if model.model_type == model_type]
