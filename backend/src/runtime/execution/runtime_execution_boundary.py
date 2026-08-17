from .execution_admission import ExecutionAdmission
from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.core.intent import ExecutionIntent
from .workload_normalizer import WorkloadNormalizer
from .workload_normalization_extension import WorkloadNormalizationExtensionPoint


class RuntimeExecutionBoundary:
    """
    Authoritative execution entry boundary for the Runtime.

    Responsible for accepting an ExecutionTarget and ExecutionIntent, establishing the
    execution boundary by normalizing the workload, and producing an ExecutionAdmission
    without performing provider-specific execution itself.
    """
    def __init__(self, normalizer_registry: WorkloadNormalizationExtensionPoint) -> None:
        self._normalizer_registry = normalizer_registry

    def execute(self, target: ExecutionTarget, intent: ExecutionIntent) -> ExecutionAdmission:
        """
        Accept an ExecutionTarget and ExecutionIntent and cross the execution boundary.

        Normalizes the intent payload and produces a deterministic ExecutionAdmission,
        preserving exact identity semantics without claiming execution success.
        """
        if not isinstance(target, ExecutionTarget):
            raise TypeError("Execution target must be an instance of ExecutionTarget")

        if not isinstance(intent, ExecutionIntent):
            raise TypeError("Execution intent must be an instance of ExecutionIntent")

        normalizer = self._normalizer_registry.get_normalizer(intent.capability_id)
        workload = normalizer.normalize(intent)

        return ExecutionAdmission(
            execution_target=target,
            execution_workload=workload
        )
