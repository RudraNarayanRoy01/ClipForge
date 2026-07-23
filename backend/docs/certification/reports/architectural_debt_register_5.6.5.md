# Architectural Debt Register

## Architectural Debt Introduced During Batch
- **None**. The fundamental dependency injection issue was resolved immediately as part of certification.

## Operational Debt
- **Missing Telemetry**: OpenTelemetry traces and advanced logging required for production are deferred to Operational Readiness.

## Deferred Features
- Full execution pipelines for clip rendering and video extraction.

## Future Enhancements
- Support for concurrent/distributed celery workers.
- Support for multiple concurrent AI providers (fallback mechanism).
