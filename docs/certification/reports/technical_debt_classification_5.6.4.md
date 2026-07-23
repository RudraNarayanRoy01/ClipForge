# Technical Debt Classification 5.6.4

The remaining engineering tasks have been classified into the following operational categories:

## 1. Architectural Technical Debt
- **None identified in the core execution pipeline.** The dependency graph, domain boundaries, and abstractions are strict, well-maintained, and fully isolated. The architecture gracefully supports scalability without violation.

## 2. Operational Technical Debt
- **Missing Telemetry and Fine-Grained Observability**: The `ClipGenerationPipelineService` and `RenderExecutionService` use basic `logging`. Full integration with OpenTelemetry and distributed tracing is required to effectively monitor step-by-step rendering performance and isolate bottlenecks during scaling.

## 3. Deferred Features
- **Clip Retrieval and Override Endpoints**: `GET /clips/{clip_id}` and `PATCH /clips/{clip_id}` are intentionally deferred (returning `501 Not Implemented`) until the precise frontend state requirements for the "User Approval" step are finalized.
- **Video Clip Extraction List**: `GET /videos/{video_id}/clips` returns `501`. This is deferred pending database query optimizations to efficiently handle high-cardinality clips associated with long-form video files.

## 4. Future Enhancements
- **Multi-Provider Dispatcher**: Implementing a routing service that dynamically chooses between MoviePy, FFmpeg, and a Cloud Render API (e.g., AWS Elemental MediaConvert) based on payload complexity or current cluster load. *Requires zero architectural redesign, just a Strategy Router and a new implementation of `IRenderBackend`.*
- **GPU Resource Management**: Building advanced locking and queueing mechanisms for multi-tenant GPU rendering nodes to prevent Out-Of-Memory (OOM) errors during concurrent rendering tasks.
