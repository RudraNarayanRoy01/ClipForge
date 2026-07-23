# Repository Ownership Certification

## Application → Domain Port → Infrastructure Repository

Repositories strictly implement Domain Ports, ensuring business logic has no awareness of persistence mechanisms.

## Validation Checklist
- **Repositories never bypass interfaces**: Verified. API relies on `c.resolve(ICampaignRepository)`.
- **Application owns repository usage**: Verified. API routes and App Services orchestrate calls.
- **Infrastructure owns repository implementation**: Verified. `CampaignRepository` consumes `AsyncSession` directly in Infrastructure.
- **Domain owns repository contracts only**: Verified. `src/domain/ports.py` declares pure interfaces.

## Known Violations
- None discovered.
- **Status**: Certified.
