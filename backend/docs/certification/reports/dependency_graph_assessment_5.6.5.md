# Canonical Dependency Graph Assessment

## Cross-Layer Dependency Certification
The architectural dependency direction has been verified across all integration points:
Presentation → Application → Domain ← Infrastructure

## Canonical Dependency Graph
### Allowed Dependencies
- `Presentation` → `Application` (for orchestrating use cases)
- `Presentation` → `Domain` (for referencing schemas/rules/enums)
- `Application` → `Domain` (to execute business logic)
- `Infrastructure` → `Domain` (to implement ports)
- `Bootstrap` → `Infrastructure` (for DI wiring)
- `Bootstrap` → `Application` (for DI wiring)

### Discouraged Dependencies
- `Application` → `Presentation` (Data should flow upwards, not leak backwards)
- `Infrastructure` → `Application` (Except in specific wiring modules)

### Forbidden Dependencies
- `Presentation` → `Infrastructure` (Presentation must not execute raw SQL or use internal clients directly)
- `Presentation` → `Database` (No direct database connections in routes)
- `Application` → `SQLAlchemy` (Application uses Repository contracts, not ORM sessions)
- `Domain` → `FastAPI` (Domain must be framework agnostic)
- `Domain` → `FFmpeg` (Domain models abstract media properties, FFmpeg is infrastructure)
- `Domain` → `Environment Configuration` (Domain uses injected settings, not `os.getenv`)
