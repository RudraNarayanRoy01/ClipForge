# Technical Debt Register Standard

## 1 Purpose

The Technical Debt Register Standard answers ONE question and ONLY ONE question:

"What known engineering debt exists, why does it exist, and what Repository Evidence supports its existence?"

It NEVER answers "How should it be fixed?", "When should it be fixed?", "Who should fix it?", or "Whether it should be fixed." Those decisions belong elsewhere. It ONLY defines the engineering standard governing future Technical Debt Registers.

## 2 What This Standard Is NOT

This standard aggressively forbids:
- Repository Snapshot
- Repository Inspection
- Repository Review
- Architecture Verification
- Certification
- Planning
- Roadmapping
- Sprint Planning
- Implementation
- Architecture Redesign
- Code Review
- Security Review
- Performance Review
- AI Reasoning
- Prompt Generation
- Repository Management
- Git
- Merge
- CI/CD
- Quality Assessment
- Future Recommendations
- Risk Acceptance
- Backlog Prioritization
- Task Scheduling

## 3 Engineering Principles

The following engineering principles apply identically from Sprint 6A:
- **Repository Truth**: Only verifiable facts from the repository are permitted.
- **Evidence First Engineering**: Every finding must be backed by traceable evidence.
- **Deterministic Engineering**: The snapshot process must be repeatable and objective.
- **Scope Discipline**: The snapshot must not exceed its bounded scope.
- **Documentation Synchronization**: The snapshot must accurately reflect the documented state of the repository.
- **Repository Evidence**: Only use verifiable evidence.
- **Traceability**: Every fact must trace back to its origin.

## 4 Technical Debt Authority

Authority derives ONLY from:
- Engineering Constitution
- Engineering Manual
- Approved Standards
- Repository Evidence
- Identity Cards
- Architecture State
- Architecture Map
- Component Catalog
- Approved ADRs
- Repository Quality Dashboard

Authority NEVER derives from:
- Opinion
- Memory
- AI reasoning
- Assumptions
- Guesses
- Future plans

## 5 Purpose of Technical Debt Register

The Register records ONLY:
- Known debt
- Debt rationale
- Debt source
- Debt evidence
- Debt owner
- Debt category
- Debt relationships
- Debt lifecycle
- Debt history
- Debt traceability

Nothing more.

## 6 Required Register Structure

Every Technical Debt Record MUST contain the following mandatory fields:
- Debt ID
- Title
- Debt Status
- Debt Category
- Debt Severity
- Debt Scope
- Debt Owner
- Repository Location
- Component
- Identity Card
- Related ADR
- Origin
- Discovery Date
- Last Verified
- Repository Evidence
- Evidence Source
- Evidence Method
- Affected Standards
- Affected Components
- Dependencies
- Related Debt
- Known Consequences
- Assumptions
- Unknowns
- Notes
- Revision
- Version

## 7 Debt Identifiers

Debt IDs are immutable and never reused.
Example taxonomy:
- CF-DEBT-0001
- CF-DEBT-0002
- CF-DEBT-0003

## 8 Debt Status

Allow ONLY the following states:
- Observed
- Verified
- Accepted
- Deferred
- Mitigated
- Resolved
- Rejected
- Archived

## 9 Debt Categories

Examples of allowable debt categories:
- Architecture
- Documentation
- Governance
- Infrastructure
- Testing
- Performance
- Maintainability
- Dependency
- Repository
- Runtime
- Security
- Unknown

## 10 Severity

Allow ONLY the following severities:
- Critical
- High
- Medium
- Low
- Unknown

Severity is descriptive only. It MUST NOT prioritize work.

## 11 Register Rules

Every debt MUST:
- Reference Repository Evidence
- Reference Identity Cards
- Reference Components
- Reference ADRs when applicable
- Reference governing Standards
- Reference authority
- Remain historically traceable
- Never invent evidence
- Never infer missing information
- Never recommend implementation

### Origin ADR

Purpose

Records the Architecture Decision Record that explicitly establishes the architectural decision responsible for the recorded Technical Debt.

Rules

• Origin ADR SHALL reference an existing ADR only when that relationship is explicitly documented by Repository Evidence.

• Logical interpretation SHALL NOT be used.

• Architectural inference SHALL NOT be used.

• Historical assumptions SHALL NOT be used.

• If Repository Evidence does not explicitly establish an Origin ADR,
Origin ADR SHALL be recorded as UNKNOWN.

Rationale

This preserves Repository Truth by ensuring that Technical Debt never invents architectural relationships not already documented by Repository Intelligence.

## 12 Repository Evidence

Every debt MUST trace back to Repository Evidence.
- Unknown evidence remains UNKNOWN.
- Missing evidence remains Missing.
- No inferred debt.

## 13 Debt Relationships

Examples of acceptable debt relationships:
- Depends On
- Blocks
- Related To
- Supersedes
- Superseded By
- Caused By
- Documents
- References
- Consumes
- Produces

## 14 Technical Debt Findings

Technical Debt Findings are strictly descriptive.
- **Allowed:** Missing Debt Record, Duplicate Debt, Broken References, Unknown Owner, Missing Evidence, Missing Identity, Missing ADR.
- **Forbidden:** Implementation criticism, Architecture criticism, Code quality review, Recommendations, Future planning.

## 15 Technical Debt Risks

Technical Debt Risks are repository-observable only.
- **Allowed:** Broken Traceability, Missing Evidence, Unknown Authority, Duplicate Debt, Missing Relationships.
- **Forbidden:** Performance analysis, Security assessment, Implementation assessment, Architecture evaluation.

## 16 Technical Debt Readiness

Readiness ends ONLY at:
- Technical Debt Ready
- Engineering Debt Ready
- Repository Debt Ready

It does NOT imply: Architecture Ready, Repository Ready, Certification Ready, Merge Ready.

## 17 Verdict

Restrict verdict vocabulary ONLY to:
- Debt Register Established
- Debt Register Established with Limitations
- Debt Register Generation Failed

Explicitly state this verdict does NOT imply:
- Repository Review
- Architecture Verification
- Certification
- Repository Truth
- Implementation Approval
- Architecture Quality
- Merge
- Git

## 18 Recommended Next Step

The ONLY allowed recommendation:
- Proceed to Runtime Health Reports.
