# Configuration Ownership Certification

## Configuration Flow
Environment → Settings (`SystemSettings`) → Bootstrap → Infrastructure → Application

## Validation Checklist
- **Configuration never leaks into Domain**: Domain entities accept configuration values explicitly; they do not access `os.environ` or `Settings` singletons.
- **Infrastructure owns infrastructure settings**: `AISettings` configures the LLM endpoint; Domain remains unaware of host URLs.
- **Application consumes abstractions**: Application services consume settings during initialization via DI.
- **Domain remains configuration independent**: Verified.
- **Status**: Certified.
