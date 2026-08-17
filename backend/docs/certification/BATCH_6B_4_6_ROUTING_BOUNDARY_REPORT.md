# BATCH 6B.4.6 ROUTING BOUNDARY REPORT

## 1. Batch Objective
Establish the clean abstract routing boundary immediately downstream of the certified Policy layer. The objective is to define the boundary that answers: *"Given an approved policy decision, what abstract execution class should this workload be routed toward?"* without continuing into provider, hardware, or scheduling selection.

## 2. Repository Discovery
- Executed repository-wide discovery in `backend/src/runtime/` looking for routing and targeting concepts.
- Discovered legacy abstractions `RuntimeRouting` and `RoutingDecision` in `backend/src/runtime/core/runtime_routing.py` that rely on a `BudgetDecision` instead of a `PolicyDecision`.
- Discovered downstream `RuntimeProviderSelection` in `selection.py` which handles provider discovery (outside this batch's scope).
- Verified that `PolicyDecision` (certified in 6B.4.5) is the authoritative policy boundary.

## 3. Existing Abstractions
- **Existing Routing:** `RuntimeRouting` / `RoutingDecision` (Legacy, coupled to budget, does not consume Policy).
- **Existing Provider Selection:** `ProviderSelectionResult` (Targeted at selecting an implementation, not an abstract execution class).
- **Existing Target:** No abstract target existed that consumed `PolicyDecision`.

## 4. REUSE / EXTEND / CREATE Decision
**CREATE**.
The existing `RoutingDecision` in `runtime_routing.py` is a parallel/legacy concept based on `BudgetDecision`. Extending it would violate the requirement to not contaminate certified architecture and would cause semantic confusion. A clean boundary called `RouteDecision` was created to cleanly map `PolicyDecision` to an abstract execution class.

## 5. Exact Routing Contract
```python
@dataclass(frozen=True)
class RouteDecision:
    policy_decision: PolicyDecision
    execution_class: str
    is_routed: bool
    fallback_allowed: bool
```

## 6. Field Semantics
- `policy_decision`: The immutable instance of the input policy decision.
- `execution_class`: The determined abstract destination (e.g., `abstract_local`, `abstract_remote`, `abstract_balanced`, `none`).
- `is_routed`: A boolean indicating if a valid route was established (respects policy rejection).
- `fallback_allowed`: Pass-through of the policy's fallback permission.

## 7. Abstract Target Semantics
The execution class represents an abstract classification, mapped deterministically from the `policy_mode`. It does not dictate implementations like CUDA or OpenAI.

## 8. Policy Gate Semantics
`RoutingEngine.evaluate` strictly consumes a `PolicyDecision`. It cannot operate on a `PlanningResult` alone.

## 9. Rejection Behavior
If `policy_decision.is_approved is False`, `is_routed` is set to `False` and the execution class defaults to `none`. The rejected state is strictly preserved.

## 10. Fallback Behavior
`fallback_allowed` is passed through from the `PolicyDecision` without instantiating concrete fallback implementations.

## 11. Payload Opacity
The `ExecutionIntent.payload` remains completely untouched.

## 12. Neutrality Validation
- **Provider-neutral:** YES
- **Model-neutral:** YES
- **Hardware-neutral:** YES
- **Scheduling-neutral:** YES
- **Execution-neutral:** YES
- **Telemetry-neutral:** YES
- **Payload-opaque:** YES
- **Deterministic:** YES

## 13. Tests
Unit tests created:
- `test_routing_valid_approval`
- `test_routing_policy_rejection`
- `test_routing_determinism`
- `test_routing_immutability`
- `test_payload_opacity_and_neutrality`

Architecture tests created:
- `test_routing_boundary_neutrality` (AST validation ensuring no providers, models, hardware, scheduling, execution, or telemetry imports).

## 14. Architecture Changes
```text
┌──────────────────────────┐
│     PolicyDecision       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│   RoutingBoundary        │
│    (RoutingEngine)       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     RouteDecision        │
└────────────┬─────────────┘
             │
             X
       STOP — 6B.4.6
```

## 15. Regression Results & Carry-Forward Failures
- The new tests passed.
- General backend test execution confirmed no pre-existing carry-forward failures related to the new abstract routing code.

## 16. Git Integrity
No history mutations, tags, merges, or rebases were performed. Only the exact budget items were generated.

## 17. 6B.4.7 Handoff
This boundary explicitly leaves provider, model, hardware, and scheduling selection to Batch 6B.4.7 and later iterations. The Runtime now transitions from `PolicyDecision` safely into the abstract routing phase.
