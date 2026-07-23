# Dependency Injection Certification

## Dependency Injection Inventory
The current DI configuration relies on `Container` within `src/infrastructure/di/container.py` and module wiring in `src/bootstrap/modules`.

| Service | Interface | Implementation | Registration Module | Lifetime | Registration Scope | Resolution Mechanism |
| ------- | --------- | -------------- | ------------------- | -------- | ------------------ | -------------------- |
| SystemSettings | `SystemSettings` | `SystemSettings` | Infrastructure | Singleton | Global | Direct |
| AsyncClient | `httpx.AsyncClient` | `httpx.AsyncClient` | Infrastructure | Singleton (Factory) | Global | Factory |
| PromptManager | `PromptManager` | `PromptManager` | Intelligence | Singleton | Global | Direct |
| ProviderFactory | `ProviderFactory` | `ProviderFactory` | Intelligence | Singleton | Global | Direct |
| AIProvider | `IAIProvider` | `OllamaProvider` | Intelligence | Singleton (Factory) | Global | Factory |
| Reason Engine | `ILLMReasoningEngine`| `AIProviderLLMEngineAdapter`| Intelligence | Transient | Global | Automatic Injection |
| AIService | `IAIService` | `DefaultAIService` | Intelligence | Transient | Global | Automatic Injection |
| Campaign Intel | `CampaignIntelligenceService`| `CampaignIntelligenceService`| Intelligence | Transient (Factory) | Global | Factory |
| Campaign Repo | `ICampaignRepository` | `CampaignRepository` | Campaign | Transient (Factory) | Global | Factory |
| DB Session | `AsyncSession` | Request DB Session | Application API | Singleton (Request) | Request scoped | Route Middleware |

## Certification
- **Duplicate registrations**: None identified.
- **Orphan registrations**: None.
- **Missing registrations**: `AsyncSession` was resolved by creating a request-scoped child container in the Presentation layer.
- **Conflicting registrations**: The DI container scoping resolution issue was fixed via runtime modification.
- **Status**: Certified. The dependency graph remains deterministic.
