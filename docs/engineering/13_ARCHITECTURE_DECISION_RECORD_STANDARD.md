# Architecture Decision Record Standard

## 1 Purpose

The Architecture Decision Record Standard answers ONE question and ONLY one question:

"What architectural decision was made, why was it made, and what repository evidence supports it?"

Architecture Decision Records capture architectural decisions. They DO NOT evaluate. They DO NOT inspect. They DO NOT review. They DO NOT certify. They DO NOT redesign architecture. They DO NOT recommend future work. They simply establish immutable records of architectural decisions.

Architecture Decision Records answer ONLY "What architectural decision exists?" and "What Repository Evidence justified it?", NOT "Is the decision correct?", NOT "Should the decision change?", NOT "How should architecture evolve?".

## 2 What This Standard Is NOT

This standard aggressively excludes:
- Repository Snapshot
- Repository Inspection
- Repository Review
- Architecture Verification
- Certification
- Implementation
- Planning
- Roadmapping
- Prompt Generation
- AI Reasoning
- Repository Management
- Git
- Merge
- CI/CD
- Quality Review
- Security Review
- Performance Review
- Technical Debt Assessment
- Future Recommendations
- Architecture Redesign

## 3 Engineering Principles

The following engineering principles apply identically from Sprint 6A:
- **Repository Truth**: Only verifiable facts from the repository are permitted.
- **Evidence First Engineering**: Every finding must be backed by traceable evidence.
- **Deterministic Engineering**: The snapshot process must be repeatable and objective.
- **Scope Discipline**: The snapshot must not exceed its bounded scope.
- **Documentation Synchronization**: The snapshot must accurately reflect the documented state of the repository.
- **Repository Evidence**: Only use verifiable evidence.
- **Traceability**: Every fact must trace back to its origin.

## 4 ADR Authority

Authority derives ONLY from:
- Engineering Constitution
- Engineering Manual
- Approved Standards
- Repository Evidence
- Approved Identity Cards
- Architecture State
- Architecture Map
- Component Catalog

Authority NEVER derives from:
- Reviewer opinion
- AI reasoning
- Memory
- Assumptions
- Inference

## 5 Purpose of ADRs

Architecture Decision Records establish:
- Architectural decision
- Decision rationale
- Decision context
- Decision evidence
- Affected identities
- Affected components
- Decision status
- Decision lifecycle
- Decision authority
- Decision traceability

Nothing beyond recording decisions.

## 6 Required ADR Structure

Every ADR MUST contain the following mandatory fields:
- ADR ID
- Title
- Decision Status
- Decision Date
- Decision Owner
- Decision Authority
- Decision Context
- Problem Statement
- Decision
- Alternatives Considered
- Decision Rationale
- Consequences
- Affected Components
- Affected Identity Cards
- Affected Standards
- Repository Evidence
- Dependencies
- Related ADRs
- Related Technical Debt
- Supersedes
- Superseded By
- Revision
- Version
- Last Verified
- Notes

## 7 ADR Identifiers

ADR identifiers are immutable. Identifiers never change. 
Example taxonomy:
- CF-ADR-0001
- CF-ADR-0002
- CF-ADR-0003

## 8 Decision Status

Allowable states only:
- Draft
- Proposed
- Accepted
- Implemented
- Superseded
- Deprecated
- Rejected
- Archived

Transition rules must strictly follow lifecycle governance documented in the Engineering Manual.

## 9 Decision Rules

Every decision must:
- Reference Repository Evidence
- Reference affected Identity Cards
- Reference affected Components
- Reference governing Standards
- Reference authority
- Be historically immutable
- Never rewrite history

Superseding creates a new ADR.

## 10 Repository Evidence

Every decision must trace to Repository Evidence.
- No speculative decisions.
- No assumed rationale.
- No undocumented architecture.

## 11 ADR Relationships

ADR relationships define relationships only.
Examples:
- Supersedes
- Depends On
- Related To
- Affects
- References
- Governed By
- Supported By
- Consumes
- Produces

## 12 ADR Findings

ADR findings are strictly descriptive.
- **Allowed:** Missing ADR, Duplicate ADR, Conflicting ADR, Unknown ADR, Broken references.
- **Forbidden:** Architecture criticism, Implementation criticism, Quality assessment.

## 13 ADR Risks

ADR risks are repository-observable only.
- **Allowed:** Missing decision history, Broken traceability, Unknown authority, Missing evidence, Duplicate decisions.
- **Forbidden:** Security risks, Performance risks, Implementation risks.

## 14 ADR Readiness

Readiness ends ONLY at:
- ADR Ready
- Decision History Ready
- Repository Decision Ready

It does NOT imply: Architecture Ready, Certification Ready, Merge Ready.

## 15 Verdict

Restrict verdict vocabulary ONLY to:
- Decision Recorded
- Decision Recorded with Limitations
- Decision Recording Failed

Explicitly state this verdict does NOT imply:
- Repository Review
- Architecture Verification
- Certification
- Repository Truth
- Merge
- Git
- Architecture Quality
- Implementation Approval

## 16 Recommended Next Step

The ONLY allowed recommendation:
- Proceed to Technical Debt Register.
