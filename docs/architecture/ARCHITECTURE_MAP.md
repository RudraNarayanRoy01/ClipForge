---
Classification: Living Document (Continuously Updated)
Update Frequency: Continuously
Primary Owner: CTO / Principal Architect
---

# Architecture Map

This document provides a high-level navigation map of the platform's architecture.

## High-Level Topology

```mermaid
flowchart TD
    Platform[ClipForge Platform]
    
    Platform --> UI[Frontend / UI]
    Platform --> Core[Application Core]
    Platform --> Runtime[Adaptive AI Runtime]
    Platform --> Data[Data Persistence]
    
    Core --> Campaign[Campaign Intelligence]
    Core --> Editing[Editing Engine]
    Core --> Timeline[Timeline Engine]
    
    Runtime --> Registry[Capability Registry]
    Runtime --> Planner[Execution Planning]
    Runtime --> Graph[Execution Graph Builder]
    Runtime --> Sched[Scheduler]
    
    Sched --> Providers[Provider Ecosystem]
    
    Providers --> Local[Local Hardware (CUDA, CPU)]
    Providers --> Cloud[Cloud APIs (OpenAI, Gemini)]
```

## Data Flow & Dependencies

**Dependency Direction (Inversion Principle):**
Application → Runtime Contracts
Application → Runtime Bootstrap → Runtime Context → Runtime Capability Registry → Runtime Resource Discovery → Runtime Provider Registry → Runtime Hardware Discovery → Hardware Registrations → Runtime Provider Selection → Runtime Scheduler → Runtime Execution Planner → Runtime Execution Graph Builder → Runtime Resource Allocator → Future Runtime Execution Context → Future Runtime Orchestrator → Future Runtime Execution Engine → Future Runtime Optimization
Runtime → Provider Ecosystem → Hardware

**Ownership:**
- **Application Core**: Owned by Domain Logic.
- **Adaptive AI Runtime**: Owned by Platform Engineering / Architecture.
- **Data Persistence**: Owned by Infrastructure layer.

