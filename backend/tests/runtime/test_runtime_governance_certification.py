import inspect
import dataclasses
import pytest

from src.runtime.core.runtime_planning import RuntimePlanning, PlanningDecision
from src.runtime.core.runtime_policy import RuntimePolicy, PolicyDecision
from src.runtime.core.runtime_constraint_engine import RuntimeConstraintEngine, ConstraintDecision
from src.runtime.core.runtime_budget_planner import RuntimeBudgetPlanner, BudgetDecision
from src.runtime.core.runtime_routing import RuntimeRouting, RoutingDecision
from src.runtime.core.runtime_learning import RuntimeKnowledge
from src.runtime.core.context import RuntimeContext

class TestGovernanceRules:
    """Certifies Governance Rules: Artifact immutability and Passive Context."""
    
    def test_decision_artifacts_are_immutable(self):
        artifacts = [
            PlanningDecision,
            PolicyDecision,
            ConstraintDecision,
            BudgetDecision,
            RoutingDecision
        ]
        for artifact in artifacts:
            assert dataclasses.is_dataclass(artifact), f"{artifact.__name__} must be a dataclass."
            assert artifact.__dataclass_params__.frozen is True, f"{artifact.__name__} must be frozen (immutable)."

    def test_runtime_context_remains_passive(self):
        """Certifies RuntimeContext does not have methods for execution, routing, or scheduling."""
        context_methods = [name for name, _ in inspect.getmembers(RuntimeContext, predicate=inspect.isfunction)]
        forbidden_terms = ["execute", "schedule", "route", "optimize", "retry"]
        for method in context_methods:
            if not method.startswith("_"):
                for term in forbidden_terms:
                    assert term not in method.lower(), f"RuntimeContext method '{method}' violates passive governance."


class TestOwnershipRules:
    """Certifies Ownership Rules: Components own their respective artifacts."""
    
    def test_decision_ownership_mapping(self):
        # We verify ownership by confirming the exact return type of the primary evaluation method.
        
        planning_sig = inspect.signature(RuntimePlanning.plan)
        assert planning_sig.return_annotation == PlanningDecision
        
        policy_sig = inspect.signature(RuntimePolicy.evaluate)
        assert policy_sig.return_annotation == PolicyDecision
        
        constraint_sig = inspect.signature(RuntimeConstraintEngine.evaluate)
        assert constraint_sig.return_annotation == ConstraintDecision
        
        budget_sig = inspect.signature(RuntimeBudgetPlanner.evaluate)
        assert budget_sig.return_annotation == BudgetDecision
        
        routing_sig = inspect.signature(RuntimeRouting.evaluate)
        assert routing_sig.return_annotation == RoutingDecision

    def test_context_does_not_own_decisions(self):
        """Certifies that RuntimeContext does not own or expose methods returning Decision artifacts."""
        context_methods = [method for name, method in inspect.getmembers(RuntimeContext, predicate=inspect.isfunction)]
        for method in context_methods:
            sig = inspect.signature(method)
            assert sig.return_annotation not in [PlanningDecision, PolicyDecision, ConstraintDecision, BudgetDecision, RoutingDecision], \
                "RuntimeContext must not own or expose Decision generation."


class TestDependencyRules:
    """Certifies Dependency Rules: Contracts, Flow, and Isolation."""

    def test_pipeline_contracts_consumed_artifacts(self):
        """Certifies that each subsystem strictly consumes the required artifact from the preceding step."""
        
        # Planning consumes Knowledge
        planning_sig = inspect.signature(RuntimePlanning.plan)
        assert any(param.annotation == RuntimeKnowledge for param in planning_sig.parameters.values()), \
            "RuntimePlanning must consume RuntimeKnowledge."

        # Policy consumes PlanningDecision
        policy_sig = inspect.signature(RuntimePolicy.evaluate)
        assert any(param.annotation == PlanningDecision for param in policy_sig.parameters.values()), \
            "RuntimePolicy must consume PlanningDecision."

        # Constraint consumes PolicyDecision
        constraint_sig = inspect.signature(RuntimeConstraintEngine.evaluate)
        assert any(param.annotation == PolicyDecision for param in constraint_sig.parameters.values()), \
            "RuntimeConstraintEngine must consume PolicyDecision."

        # Budget consumes ConstraintDecision
        budget_sig = inspect.signature(RuntimeBudgetPlanner.evaluate)
        assert any(param.annotation == ConstraintDecision for param in budget_sig.parameters.values()), \
            "RuntimeBudgetPlanner must consume ConstraintDecision."

        # Routing consumes BudgetDecision
        routing_sig = inspect.signature(RuntimeRouting.evaluate)
        assert any(param.annotation == BudgetDecision for param in routing_sig.parameters.values()), \
            "RuntimeRouting must consume BudgetDecision."

    def test_forbidden_dependencies(self):
        """Certifies that subsystems do not possess reverse or skipped dependencies."""
        
        routing_mod = inspect.getmodule(RuntimeRouting)
        assert 'RuntimePlanning' not in dir(routing_mod), "Routing must not depend on Planning"
        assert 'PlanningDecision' not in dir(routing_mod), "Routing must not depend on PlanningDecision"
        
        budget_mod = inspect.getmodule(RuntimeBudgetPlanner)
        assert 'RuntimePlanning' not in dir(budget_mod), "Budget must not depend on Planning"
        assert 'PlanningDecision' not in dir(budget_mod), "Budget must not depend on PlanningDecision"
        
        constraint_mod = inspect.getmodule(RuntimeConstraintEngine)
        assert 'RuntimeContext' not in dir(constraint_mod), "Constraint must not depend on RuntimeContext"
        
        policy_mod = inspect.getmodule(RuntimePolicy)
        assert 'RuntimeContext' not in dir(policy_mod), "Policy must not depend on RuntimeContext"
