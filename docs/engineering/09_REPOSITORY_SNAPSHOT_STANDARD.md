# Repository Snapshot Standard

## 1 Purpose

The Repository Snapshot Standard answers ONLY:

"What objectively exists in the repository?"

Nothing more. 

It establishes the engineering standard for producing objective Repository Snapshots. It defines required structure, engineering principles, evidence requirements, lifecycle, boundaries, terminology, traceability, and verdicts. It does NOT generate snapshots.

## 2 Scope

This standard defines what repository information MAY appear inside snapshots.

Examples of permitted snapshot contents:
- Repository metadata
- Directory structure
- Technology stack
- Dependencies
- Configuration
- Statistics
- Manifest files
- Documentation inventory
- Generated metadata

Nothing evaluative is permitted in a Repository Snapshot.

## 3 What This Standard Is NOT

This standard explicitly excludes:
- Architecture State
- Architecture Map
- Component Catalog
- Identity Cards
- Repository Quality Dashboard
- Repository Review
- Changeset Verification
- Architecture Verification
- Certification
- Planning
- Roadmapping
- Implementation
- AI reasoning
- Prompt generation
- Engineering recommendations
- Quality scoring
- Health assessment
- Technical debt assessment
- Repository management
- Git operations
- Merge authorization
- Future planning
- Risk prioritization

## 4 Engineering Principles

The Repository Snapshot is descriptive, NOT interpretive. It records facts, NOT opinions. It inventories, NOT summarizes. It captures Repository Truth, NOT engineering conclusions.

The following engineering principles apply:
- **Repository Truth**: Only verifiable facts from the repository are permitted.
- **Evidence First Engineering**: Every finding must be backed by traceable evidence.
- **Scope Discipline**: The snapshot must not exceed its bounded scope.
- **Deterministic Engineering**: The snapshot process must be repeatable and objective.
- **Documentation Synchronization**: The snapshot must accurately reflect the documented state of the repository.
- **Traceability**: Every fact must trace back to its origin.

## 5 Snapshot Authority

Repository Snapshots derive authority ONLY from:
- Engineering Constitution
- Engineering Manual
- Approved Engineering Standards
- Repository Evidence
- Repository itself

Authority NEVER derives from:
- reviewer opinion
- engineering judgement
- interpretation
- memory
- assumptions

## 6 Repository Truth Rules

The following rules govern the capture of Repository Truth:
- Unknown facts remain UNKNOWN.
- Unavailable evidence is never invented.
- Incomplete evidence is explicitly marked.
- No inferred repository state.
- No estimated counts.
- No assumptions.

## 7 Repository Evidence Hierarchy

Evidence priority is strictly defined. Higher-priority evidence overrides lower-priority evidence.
1. Repository Files
2. Git Metadata
3. Build Metadata
4. Dependency Manifests
5. Configuration
6. Generated Metadata

## 8 Snapshot Scope

Future Repository Snapshots may include the following categories (this standard defines them, but does not populate them):
- Repository Metadata
- Filesystem Inventory
- Technology Inventory
- Language Inventory
- Dependency Inventory
- Repository Statistics
- Configuration Files
- Documentation Inventory
- Known Unknowns
- Generation Metadata
- Evidence Summary

## 9 Repository Evidence

Mandatory evidence sources include:
- Filesystem
- Git
- Configuration
- Package manifests
- Build configuration
- Dependency manifests
- Project metadata

Never allow memory, assumption, opinion, or speculation as evidence.

## 10 Snapshot Lifecycle

The recommended lifecycle for a Repository Snapshot is:

Draft
↓
Generated
↓
Verified
↓
Archived

## 11 Required Snapshot Structure

Every future Repository Snapshot must contain the following mandatory sections:

1. **Snapshot Metadata**: Must include Snapshot ID, Generation Timestamp, Repository Revision, Branch, Generator, Evidence Sources, Snapshot Version, Collection Method, and Repository Root.
2. **Repository Evidence**
3. **Filesystem Inventory**
4. **Technology & Dependency Inventory**
5. **Documentation Inventory**
6. **Snapshot Findings**
7. **Snapshot Risks**
8. **Snapshot Readiness Assessment**
9. **Snapshot Verdict**
10. **Recommended Next Step**

*(This standard does not generate a snapshot, only defines its structure).*

## 12 Boundary Rules

The following are explicitly forbidden within a Repository Snapshot:
- Repository Review
- Architecture Review
- Certification
- Recommendations
- Technical Debt
- Quality Judgements
- Future Planning
- Speculation
- Engineering Opinions
- Interpretation

## 13 Evidence Traceability

Every snapshot item must explicitly reference:
- Evidence Source
- Collection Method
- Timestamp
- Generator
- Repository Revision

Orphan findings without strict traceability are explicitly forbidden.

## 14 Snapshot Findings

Snapshot findings are strictly descriptive and never evaluative.

- **Allowed**: "Directory contains 42 markdown files."
- **Forbidden**: "Documentation is excessive."
- **Allowed**: "LICENSE file not found."
- **Forbidden**: "Repository licensing should be improved."

No interpretation is permitted.

## 15 Snapshot Risks

Risks are repository-observable only. Never interpret impact.

- **Allowed**: Missing LICENSE, Missing README, Missing configuration.
- **Forbidden**: Poor architecture, Bad implementation, Needs improvement, Weak testing.

Never discuss architecture quality, implementation quality, or future improvements.

## 16 Snapshot Readiness Assessment

The readiness assessment evaluates independent states. The allowed states are:
- Snapshot Ready
- Evidence Ready
- Repository Captured
- Repository Knowledge Ready
- Documentation Ready

Nothing beyond Repository Knowledge is assessed.

## 17 Snapshot Verdict

Allowed verdicts ONLY:
- Generated
- Generated with Limitations
- Generation Failed

The verdict does NOT imply:
- Repository Review
- Architecture Verification
- Certification
- Approval
- Repository Truth authorization
- Git readiness
- Merge readiness

## 18 Recommended Next Step

The only allowed recommendation is:
- Proceed to Repository Inspection.

Nothing else. No planning. No architecture. No recommendations.
