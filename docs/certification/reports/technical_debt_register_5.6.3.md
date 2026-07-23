# Technical Debt Register 5.6.3

This register aggregates all non-blocking technical debt identified during the Sprint 5.6.3 architectural certification. None of these items represent a violation of current architectural rules; they are legacy artifacts isolated from the core execution path.

## 1. Architectural Technical Debt
- **Legacy Modality Interfaces (`capabilities.py`):** The existence of legacy protocols (`IReasoning`, `IStructuredOutput`, `IVision`, `IToolCalling`) conflicts conceptually with the new unified `IAIProvider` contract, though they do not actively interfere with modern execution.
- **Legacy Prompt Infrastructure:** A legacy `PromptCompiler` (utilizing `.format()`) and an older in-memory `PromptRegistry` remain in the codebase alongside the modern, certified `PromptManager`.

## 2. Operational Technical Debt
- **Legacy Provider Routing (`CapabilityRouter`):** The `router.py` module contains a `CapabilityRouter` that explicitly instantiates a legacy `Gemma4LocalProvider` to maintain backward compatibility. This bypasses the modern `ProviderFactory` DI pattern.
- **Settings Consolidation (`AISettings`):** Current configuration models merge runtime execution settings (e.g., timeout, retries) with provider-specific connection settings (e.g., Ollama host URLs). 

## 3. Future Modernization Opportunities
- **Deprecate Legacy Components:** Systematically remove `CapabilityRouter`, legacy modality interfaces, `PromptCompiler`, and `PromptRegistry`.
- **Configuration Decoupling:** Split `AISettings` into distinct, provider-specific configuration models (e.g., `OllamaConfig`, `OpenAIConfig`).
- **Execution Policy Layer:** Introduce dynamic routing, load balancing, or fallback mechanisms as a dedicated Execution Policy layer or middleware, preserving the integrity of `DefaultAIService`.
- **Streaming Abstractions:** Should streaming inference become a requirement, implement dedicated asynchronous generator protocols alongside the existing `execute` signatures.
