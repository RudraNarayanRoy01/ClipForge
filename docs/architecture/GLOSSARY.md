---
Classification: Living Document (Continuously Updated)
Update Frequency: Continuously
Primary Owner: CTO / Principal Architect
---

# Architectural Glossary

This document serves as the canonical terminology reference for the ClipForge project. Standardized language ensures clear communication across the team and future AI agents.

## Core Terminology

- **Runtime**: The Adaptive AI Runtime subsystem responsible for orchestrating AI execution independently of providers.
- **Capability**: An abstract, generalized function that the AI can perform (e.g., "Text-to-Speech", "Vision Analysis").
- **Provider**: A specific external service or local engine that implements a Capability (e.g., Ollama, OpenAI).
- **Resource**: A physical or virtual constraint necessary for execution (e.g., GPU memory, API rate limits).
- **Planner**: A Runtime component that determines the sequence of actions needed to fulfill a Capability request.
- **Scheduler**: A Runtime component responsible for dispatching execution plans to available resources at the correct time.
- **Registry**: The catalog that maps available Capabilities to Providers.
- **Adapter**: A design pattern used to bridge abstract interfaces in the Core Domain to concrete external implementations.
- **Component**: A deployable, highly cohesive module of code that fulfills a specific domain or architectural responsibility.
- **Context**: The environmental data or state necessary for an execution or evaluation to occur.
- **Execution Plan**: The deterministic output of the Planner, detailing exactly what the Scheduler must run.
- **Timeline**: The chronological representation of video, audio, and effect layers in the Editing Engine.
- **Workspace**: The logical boundary containing project files, assets, and metadata for a specific user session or campaign.
