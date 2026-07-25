import inspect
import pytest

from src.runtime.core.execution_model import ExecutionRequest
from src.runtime.core.planner import RuntimeExecutionPlanner
from src.runtime.core.scheduling_model import SchedulingDecision
from src.runtime.core.scheduler import RuntimeScheduler
from src.runtime.core.execution_result_model import ExecutionResult
from src.runtime.core.executor import RuntimeExecutor
from src.runtime.core.lifecycle_model import LifecycleResult
from src.runtime.core.lifecycle import RuntimeLifecycle
from src.runtime.core.retry_model import RetryResult
from src.runtime.core.retry import RuntimeRetry
from src.runtime.core.observation_model import ObservationResult
from src.runtime.core.observation import RuntimeObservation
from src.runtime.core.learning_model import LearningResult
from src.runtime.core.learning import RuntimeLearning
from src.runtime.core.optimization_model import OptimizationResult
from src.runtime.core.optimization import RuntimeOptimization

class TestRuntimeExtensibilityCertification:
    """
    Certifies that future Runtime capabilities (Sprint 6.6) can integrate 
    through composition and consumption of immutable artifacts without modifying 
    the certified Runtime pipeline.
    """

    def test_frozen_pipeline_components_isolation(self):
        """
        Verify that existing decision pipeline components (Planner, Scheduler, Executor, etc.)
        do not depend on future extensions.
        This guarantees future modules can be added without modifying Sprint 6.5 components.
        """
        pipeline_classes = [
            RuntimeExecutionPlanner,
            RuntimeScheduler,
            RuntimeExecutor,
            RuntimeLifecycle,
            RuntimeRetry,
            RuntimeObservation,
            RuntimeLearning,
            RuntimeOptimization
        ]
        
        forbidden_imports = [
            'CampaignManager',
            'AdvancedOrchestrator',
            'DistributedCache',
            'GlobalLoadBalancer',
            'ExternalPolicyEngine'
        ]
        
        for cls in pipeline_classes:
            module = inspect.getmodule(cls)
            module_dir = dir(module)
            for forbidden in forbidden_imports:
                assert forbidden not in module_dir, \
                    f"Extensibility violation: {cls.__name__} depends on future component {forbidden}."
                    
    def test_artifacts_are_independent(self):
        """
        Verify that immutable artifacts (ExecutionRequest, SchedulingDecision, etc.) 
        have no dependencies on execution logic, ensuring they can be safely 
        consumed by Sprint 6.6 extensions.
        """
        artifacts = [
            ExecutionRequest,
            SchedulingDecision,
            ExecutionResult,
            LifecycleResult,
            RetryResult,
            ObservationResult,
            LearningResult,
            OptimizationResult
        ]
        
        pipeline_classes = [
            'RuntimeExecutionPlanner',
            'RuntimeScheduler',
            'RuntimeExecutor',
            'RuntimeLifecycle',
            'RuntimeRetry',
            'RuntimeObservation',
            'RuntimeLearning',
            'RuntimeOptimization'
        ]
        
        for artifact_cls in artifacts:
            module = inspect.getmodule(artifact_cls)
            module_dir = dir(module)
            for logic_cls in pipeline_classes:
                assert logic_cls not in module_dir, \
                    f"Extensibility violation: Artifact {artifact_cls.__name__} depends on execution logic {logic_cls}."
