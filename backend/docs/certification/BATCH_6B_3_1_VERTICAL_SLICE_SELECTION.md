# Batch 6B.3.1 — Vertical Slice Selection

## 1. Batch Identity
- **Milestone:** 6B — Adaptive AI Runtime & Compute Engine
- **Sprint:** 6B.3 — Runtime Integration & Real Execution Boundary
- **Batch:** 6B.3.1
- **Batch Name:** Vertical Slice Selection
- **Batch Type:** LEVEL 0 — Architectural / Repository Analysis / Documentation

## 2. Scope
This Batch strictly performs architectural research and selection based on current repository evidence. Its goal is to identify the smallest meaningful real AI workload that can be used in future batches (Batch 6B.3.2/6B.3.3) to prove the Runtime → Provider → Real Execution architecture. This Batch involves NO source code changes, NO test changes, and NO environment modifications.

## 3. Repository Baseline
- **Branch:** `main`
- **HEAD Commit:** `e0a4ccfb06d986da0a92d9a10d8592a745a16445`
- **Working Tree:** Clean (verified via `git status --short`)

## 4. Architectural Context
The certified architecture from Sprint 6B.2 dictates that `RuntimeContext` is the provider-agnostic and hardware-agnostic Composition Root. 

**CURRENT STATE:** Application-level AI requests bypass the Runtime layer. They use `IAIService`, which resolves providers (like `OllamaProvider`) via a `ProviderFactory`.

**TARGET STATE:** Batch 6B.3.2 will design an integration boundary to route the selected workload through the `RuntimeContext` and `RuntimeExecutor`, proving the Runtime architecture without violating the 6B.2 invariants.

## 5. Selection Methodology
Candidates were evaluated based on the MINIMUM SAFE CHANGE principle. The repository was inspected using `grep` searches and file reviews to identify existing capabilities, providers, and application entries. Candidates were scored on existing infrastructure support, simplicity, real execution feasibility, and architectural risk.

## 6. Application Capability Inventory
Based on the inspected repository search, the following real AI capabilities are actively defined in `CampaignIntelligenceService` and invoked by application use cases:
- `extract_rules`: IMPLEMENTED
- `generate_summary`: IMPLEMENTED
- `calculate_worth_it_score`: IMPLEMENTED
- `generate_execution_plan`: IMPLEMENTED
- `generate_clip_strategy`: IMPLEMENTED
- `generate_prompt_template`: IMPLEMENTED
- `assess_suitability`: IMPLEMENTED

## 7. Runtime Capability Inventory
Based on the inspected repository search, the formal Runtime capability contracts are primarily interfaces and enums at present:
- `CapabilityType` (Enum): REGISTERED (e.g., `TEXT_GENERATION`, `STRUCTURED_OUTPUT`)
- `CapabilityCategory` (Enum): REGISTERED (e.g., `LANGUAGE`, `REASONING`)
- `CapabilityDescriptor`: INTERFACE ONLY. No concrete descriptors are currently registered in `RuntimeCapabilityRegistry` for the application workloads.
- Runtime Path / Executor: PLACEHOLDER ONLY. The `RuntimeExecutor` exists and returns a mock `RuntimeExecutionResult`, but its `_execute_attempt` method is explicitly defined as a placeholder (`pass`). It currently possesses NO provider selection, resolution, or invocation logic.

## 8. Provider Inventory
Based on the inspected repository search for **Ollama**:
- Provider Interface (`IAIProvider`): IMPLEMENTED
- Provider Adapter (`OllamaProvider`): IMPLEMENTED
- Provider Client (`OllamaClient`): IMPLEMENTED
- HTTP Endpoint Call (`/api/generate`): IMPLEMENTED
- JSON Schema Serialization: IMPLEMENTED (using Pydantic schema mapping)
- Timeout & Error Handling: IMPLEMENTED
- Runtime Provider Resolution: MISSING (Currently bypasses Runtime via `IAIService`)

**Execution Path Evidence:** The source code confirms an execution path from `AIRequest` → `OllamaProvider` → `OllamaClient` → HTTP POST → Pydantic Validation. While implementation is present, real end-to-end execution with a live model was not independently verified in this batch. 

## 9. Candidate Workloads
The following serious candidates were extracted from `CampaignIntelligenceService`:

**Candidate 1: Generate Summary**
- **Application Entry:** `CampaignIntelligenceService.generate_summary` (invoked via `ImportCampaignUseCase` which is exposed by `POST /api/campaigns/import/url`).
- **Input:** Raw campaign text
- **Expected Output:** `ExtractionSummarySchema` mapped to `CampaignSummary`
- **Application Blast Radius:** LOW (Earliest stage of planning, simple read-only inference)

**Candidate 2: Extract Rules**
- **Application Entry:** `CampaignIntelligenceService.extract_rules`
- **Input:** Raw campaign text
- **Expected Output:** `ExtractionRulesSchema`
- **Application Blast Radius:** LOW

**Candidate 3: Generate Execution Plan**
- **Application Entry:** `CampaignIntelligenceService.generate_execution_plan`
- **Input:** Rules and Summary text
- **Expected Output:** `ExecutionPlanSchema`
- **Application Blast Radius:** MEDIUM (Downstream impact on clip strategy)

## 10. Candidate Evaluation Matrix

| Criterion | Importance | Generate Summary | Extract Rules |
|-----------|------------|------------------|---------------|
| Production-facing entry | HIGH | PASS (`ImportCampaignUseCase`) | PASS (`ImportCampaignUseCase`) |
| Existing capability contract | HIGH | PARTIAL (Needs Descriptor) | PARTIAL (Needs Descriptor) |
| Existing provider adapter | HIGH | PASS (`OllamaProvider`) | PASS (`OllamaProvider`) |
| Observable output | CRITICAL | PASS (`CampaignSummary`) | PASS (`CampaignRules`) |
| Minimal source change | CRITICAL | HIGHEST | HIGHEST |
| Application blast radius | CRITICAL | LOW | LOW |

## 11. Candidate Execution-Path Analysis
For the selected candidate (`generate_summary`), the execution path trace is:

**CURRENT STATE:**
API Route (`POST /api/campaigns/import/url`) → IMPLEMENTED
    ↓
`ImportCampaignUseCase` → IMPLEMENTED
    ↓
`CampaignIntelligenceService.generate_summary` → IMPLEMENTED
    ↓
`IAIService` (`DefaultAIService`) → IMPLEMENTED (BYPASSES RUNTIME)
    ↓
`ProviderFactory` → IMPLEMENTED (BYPASSES RUNTIME)
    ↓
`OllamaProvider` → IMPLEMENTED
    ↓
Result (`ExtractionSummarySchema` → `CampaignSummary`) → IMPLEMENTED

**TARGET FUTURE STATE:**
`CampaignIntelligenceService` (or equivalent proxy)
    ↓
`RuntimeContext` (Capability Request)
    ↓
`RuntimeCapabilityRegistry` (Resolution)
    ↓
`RuntimeExecutor` (Invocation)
    ↓
`OllamaProvider`

## 12. Real Provider Feasibility
The provider-side feasibility is **HIGH**, as the `OllamaProvider` adapter and client are implemented to handle request translation, Pydantic schemas, and timeout errors. However, the end-to-end Runtime feasibility is **PARTIAL / MISSING**, because `RuntimeExecutor` currently contains only a placeholder `_execute_attempt` method and lacks provider invocation logic.

## 13. Result-Model Compatibility
**Classification:** INTEGRATION RISK.
**Evidence:** The target `RuntimeExecutor.execute()` returns `RuntimeExecutionResult`. However, the existing application path (`CampaignIntelligenceService.generate_summary`) expects an `AIResponse` containing a `.structured_output` property that yields an `ExtractionSummarySchema`. The integration boundary must eventually bridge this gap. Batch 6B.3.2 must account for this compatibility boundary, which is a known carry-forward risk and a downstream handoff item.

## 14. Testability Analysis
- **Current Coverage:** `test_system_e2e.py` provides UNIT/INTEGRATION COVERAGE for `generate_summary` using a mocked `MockAIService`.
- **Future Proof Requirements:** Batch 6B.3.2/6B.3.3 must implement tests to objectively prove that an application request reaches the Runtime, successfully resolves an `Ollama` provider capability, invokes the `OllamaProvider` adapter, and correctly propagates the result or failure back to the application domain.

## 15. Application Blast Radius
**LOW.** The `generate_summary` workload operates early in the planning pipeline. The output (`CampaignSummary`) is persisted but does not directly dictate the complex clip rendering strategy in the way an Execution Plan does. Modifying its AI execution path avoids complex cascading dependencies.

## 16. Architectural Risk
**LOW.** Routing a single read-only inference request (`generate_summary`) through the new Runtime boundary limits the risk surface. It validates the core `RuntimeContext` integration without requiring state mutations or breaking the broader application lifecycle.

## 17. Candidate Classification
- `generate_summary`: **SELECTED**
- `extract_rules`: **ALTERNATE**
- `generate_execution_plan`: **DEFERRED**
- `assess_suitability`: **DEFERRED**

## 18. Selected Vertical Slice

**SELECTED VERTICAL SLICE:**
Generate Campaign Summary

**Application Workload:**
`CampaignIntelligenceService.generate_summary` (Triggered via `ImportCampaignUseCase`)

**Current Execution:**
Bypasses Runtime. Invokes `IAIService` -> `ProviderFactory` -> `OllamaProvider`.

**Target Runtime Boundary:**
Application → Runtime capability request → Runtime execution (`RuntimeExecutor`) → provider resolution → `OllamaProvider`.

**Provider:**
`OllamaProvider`

**Model:**
Configured Ollama model (`ai_settings.ollama_model`), subject to environment availability.

**Input:**
Campaign text

**Output:**
`ExtractionSummarySchema` mapped to `CampaignSummary`

**Selection Reason:**
Smallest repository-backed, production-facing workload that provides structured, observable AI output with limited downstream dependency depth, backed by an implemented (though not verified live) provider adapter.

## 19. Selection Rationale
`generate_summary` represents the smallest meaningful candidate identified in the inspected repository. It takes raw text and produces a well-defined structured output. It is genuinely invoked by the application API. The selected workload is intended to provide the smallest meaningful proof that the Runtime can eventually resolve a provider and execute a real Pydantic-schema-bound request once the integration boundary is implemented in subsequent batches. It satisfies all batch objectives with minimal downstream impact.

## 20. Alternatives Considered
`extract_rules` was considered as it is similarly simple and shares the same execution path. However, `generate_summary` provides a slightly richer output structure (about, requirements, restrictions) which makes observing the success of the AI provider's generation more observable for a proof-of-concept vertical slice.

## 21. Known Risks and Carry-Forward Issues
- **Result-Model Mismatch:** `RuntimeExecutor` returns `RuntimeExecutionResult`, while the application expects `AIResponse.structured_output`. This mapping must be resolved.
- **RenderPlan NameError:** NOT RELEVANT to this text-generation workload.

## 22. Architectural Invariant Audit
The selected vertical slice does NOT require:
- Modifying the 23 PUBLIC / 17 INTERNAL `RuntimeContext` boundary.
- Modifying the immutable `RuntimeExecutionContext`.
- Exposing provider-specific logic in `RuntimeContext`.
- Exposing hardware-specific logic.

## 23. Batch 6B.3.2 Handoff
This document serves as the authoritative selection artifact. Batch 6B.3.2 is authorized to design the integration boundary around the `generate_summary` workload using the `OllamaProvider`. 

**Batch 6B.3.2 MUST NOT assume that:**
1. A formal Runtime capability descriptor currently exists. (Batch 6B.3.2 must define and register it).
2. `RuntimeExecutor` is already capable of provider resolution or invocation. (It currently contains a placeholder `_execute_attempt` method).

## 24. Non-Goals
- Did NOT implement the Runtime integration.
- Did NOT modify `RuntimeContext` or `RuntimeExecutor`.
- Did NOT modify `OllamaProvider`.
- Did NOT fix the result-model mismatch.

## 25. Verification Evidence
All repository inspections were performed dynamically using source code views and structural analysis.

## 26. Git / Scope Verification
- Source modifications: 0
- Test modifications: 0
- Configuration modifications: 0
- Expected untracked files: 1 (`backend/docs/certification/BATCH_6B_3_1_VERTICAL_SLICE_SELECTION.md`)

## 27. Final Decision
READY FOR CHANGE SET VERIFICATION
