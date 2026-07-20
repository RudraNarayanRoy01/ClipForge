from typing import List

from src.reasoning.execution.planner.models import ExecutionPlanDraft
from src.reasoning.execution.strategy.models import ExecutionStrategyResult
from src.reasoning.execution.validation.exceptions import InvalidValidationInputException
from src.reasoning.execution.validation.interfaces import IExecutionValidation
from src.reasoning.execution.validation.models import (
    ExecutionValidationResult,
    ValidationCategory,
    ValidationIssue,
    ValidationSeverity,
)


class DefaultExecutionValidation(IExecutionValidation):
    """
    Default deterministic implementation of the Execution Validation Engine.
    Verifies that the outputs produced by previous stages are internally consistent and complete.
    """

    def validate_execution(
        self,
        draft: ExecutionPlanDraft,
        strategy: ExecutionStrategyResult
    ) -> ExecutionValidationResult:
        if not draft:
            raise InvalidValidationInputException("ExecutionPlanDraft cannot be None")
        if not strategy:
            raise InvalidValidationInputException("ExecutionStrategyResult cannot be None")

        issues: List[ValidationIssue] = []

        # Completeness & Structural Checks on Draft
        if not draft.execution_input:
            issues.append(
                ValidationIssue(
                    message="ExecutionPlanDraft is missing ExecutionInput",
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.COMPLETENESS
                )
            )
        
        if not draft.segments:
            issues.append(
                ValidationIssue(
                    message="ExecutionPlanDraft contains no segments",
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.COMPLETENESS
                )
            )
        else:
            for idx, segment in enumerate(draft.segments):
                if segment.start_time < 0 or segment.end_time < 0:
                    issues.append(
                        ValidationIssue(
                            message=f"Segment {idx} has negative timestamps",
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.STRUCTURAL
                        )
                    )
                if segment.start_time >= segment.end_time:
                    issues.append(
                        ValidationIssue(
                            message=f"Segment {idx} has invalid time range: start >= end",
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.STRUCTURAL
                        )
                    )
                if not segment.purpose:
                    issues.append(
                        ValidationIssue(
                            message=f"Segment {idx} is missing a purpose",
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.COMPLETENESS
                        )
                    )

        # Compatibility Checks between Strategy and Draft
        # The strategy should be based on the same draft (or one with the same segments)
        if strategy.execution_plan_draft != draft:
            issues.append(
                ValidationIssue(
                    message="ExecutionStrategyResult was generated for a different ExecutionPlanDraft",
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.COMPATIBILITY
                )
            )

        # Completeness Checks on Strategy
        if not strategy.editorial_intent:
            issues.append(
                ValidationIssue(
                    message="ExecutionStrategyResult is missing EditorialIntent",
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.COMPLETENESS
                )
            )
        else:
            intent = strategy.editorial_intent
            if not intent.narrative_flow:
                issues.append(
                    ValidationIssue(
                        message="EditorialIntent is missing narrative_flow",
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.COMPLETENESS
                    )
                )
            if not intent.transition_philosophy:
                issues.append(
                    ValidationIssue(
                        message="EditorialIntent is missing transition_philosophy",
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.COMPLETENESS
                    )
                )

        is_valid = not any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        
        return ExecutionValidationResult(
            is_valid=is_valid,
            issues=tuple(issues)
        )
