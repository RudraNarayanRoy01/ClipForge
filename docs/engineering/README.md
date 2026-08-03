# Engineering Manual

## Overview & Purpose
This README is the canonical entry point for the Engineering Manual. It exists to provide a single, discoverable control plane for engineering governance, workflow standards, and templates. It is the designated entry point because it centralizes navigation, ownership, and lifecycle rules, thereby improving long-term repository maintainability and preventing knowledge fragmentation.

Engineers should begin here to orient themselves before writing code, ensuring they understand the current standards and evidentiary requirements. The Engineering Manual operationalizes the immutable principles of the Engineering Constitution and fits within the delivery sequence defined by the Milestone Execution Plan. 

## Engineering Manual Organization
The Engineering Manual and broader governance ecosystem are organized into the following categories. Note that not every category is fully implemented yet.

- **Standards**: Operational guidelines for specification, implementation, verification, and certification.
- **Templates**: Controlled, reusable artifacts for creating specifications, records, and AI-assisted prompts.
- **Engineering Records**: Point-in-time evidence of execution, such as Architecture Decision Records (ADRs) and Technical Debt Registers.
- **Repository Knowledge**: Verifiable, current facts about the repository state.
- **Architecture Knowledge**: High-level structural documentation such as Architecture Maps and Identity Cards.

## Authority Hierarchy
Lower-level artifacts never override higher-level governance.

1. **Engineering Constitution**
2. **Milestone Execution Plan**
3. **Sprint Specifications**
4. **Batch Specifications**
5. **Engineering Manual**
6. **Engineering Templates**
7. **Engineering Records**
8. **Repository Knowledge**
9. **Architecture State**
10. **Architecture Map**
11. **Component Catalog**
12. **Identity Cards**
13. **ADRs**
14. **Technical Debt Register**
15. **Runtime Health Reports**
16. **Repository Snapshot**
17. **Repository Quality Dashboard**

## Repository Navigation
A new engineer orienting to the repository should navigate the governance artifacts in the following practical reading order:

1. **Engineering Constitution**
2. **Execution Plan**
3. **Sprint Specification**
4. **Batch Specification**
5. **Engineering Manual**
6. **Standards**
7. **Templates**
8. **Repository Knowledge**
9. **Engineering Records**

## Document Status Definitions
To clearly distinguish a document's repository existence from its planning status, the following lifecycle states are used:

- **Planned**: Approved for a future scoped batch but not yet created.
- **Registered Only**: Identified in the inventory/registry without operational content.
- **Draft**: File exists but is awaiting review.
- **In Review**: Draft is undergoing named review.
- **Approved**: Accepted controlled artifact.
- **Deferred**: Intentionally postponed to a named sprint because prerequisites are missing.
- **Superseded**: Historical artifact remains discoverable but no longer governs.
- **Retired**: Historical artifact remains discoverable but no longer governs.
- **Unknown**: No evidence supports a status claim.

*(Note: An item listed in the inventory must NEVER imply the file already exists unless its state is Draft, In Review, or Approved.)*

## Ownership Model
This ownership model is the canonical ownership reference for the Engineering Manual.

- **Architecture Owner**: Verifies authority hierarchy, boundary consistency, and approves batches. Resolves architecture/governance conflict and controls constitutional alignment.
- **Engineering Governance Lead**: Authors README/control model and maintains inventory. Owns operational Manual navigation and template governance.
- **Technical Program Manager**: Validates sprint ownership/dependency assignments and progress visibility. Maintains milestone execution accountability.
- **Documentation Reviewer**: Reviews clarity, consistency, metadata, status vocabulary, and link integrity. Reviews controlled documentation quality.
- **Maintainer**: Responsible for day-to-day upkeep and alignment of artifacts.
- **Author**: Implements approved scope and supplies accurate evidence references.
- **Reviewer**: Evaluates claims against evidence (e.g., change-set verifier, architecture verifier).
- **Approver**: Makes final decisions based on evidence and verdicts (e.g., Certifier).
- **Future Artifact Owner**: Accepts ownership of planned/deferred artifact upon its owning batch/sprint. Maintains document after approval.

## Document Lifecycle
Documents undergo a strict lifecycle from planning (Planned, Registered Only, Deferred) to execution (Draft, In Review) to governance (Approved) and eventual deprecation (Superseded, Retired). No document transitions to Approved without explicit evidence-backed certification.

## Versioning Philosophy
Stable governing and Manual documents use semantic versioning to reflect substantive changes. Artifacts like the manual inventory, runtime reports, architecture state, and component catalogs use continuous status, date, and revision-based versioning.

## Review Cadence
Documents are reviewed before implementation, before batch certification, and iteratively upon any evidence-driven correction or detected architecture drift.

## Contribution Guidelines
Any modification to the Engineering Manual or governing artifacts requires an approved Engineering Specification. Work must proceed sequentially through Implementation, Repository Evidence Collection, Change-Set Verification, Architecture Verification, and Certification before merge.

## Manual Artifact Inventory
This inventory is the single canonical inventory for Engineering Manual artifacts unless superseded by an approved governance document.

| Name / Path | Purpose | Lifecycle State | Owner | Owning Sprint | Dependencies | Review Cadence | Versioning Mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `README.md` | Manual entry point | Approved | Engineering Governance Lead | 6A.1 | Constitution, Execution Plan | Event-driven | Semantic |
| `01_ENGINEERING_PHILOSOPHY.md` | Philosophy foundation | Approved | Architecture Owner | 6A.1 | Constitution | Event-driven | Semantic |
| `02_DEVELOPMENT_WORKFLOW.md` | Daily engineering lifecycle | Draft | TPM / Governance Lead | 6A.1 | Workflow model | Event-driven | Semantic |
| `03_ENGINEERING_SPECIFICATION_STANDARD.md` | Future specification quality | Approved | Architecture Owner | 6A.1 | Constitution, workflow | Event-driven | Semantic |
| `04_IMPLEMENTATION_STANDARD.md` | Architecture-preserving implementation | Draft | Principal Engineering | 6A.1 | Architecture standards | Event-driven | Semantic |
| `05_CHANGESET_VERIFICATION.md` | Operational changed-file/integration verification | Approved | Change-set Verifier | 6A.1 | 6A.2 inspection | Event-driven | Semantic |
| `06_REPOSITORY_REVIEW_STANDARD.md` | Evaluates implementation against specification | Approved | Governance Lead | 6A.1 | 6A.1 Standards | Event-driven | Semantic |
| `07_ARCHITECTURE_VERIFICATION.md` | Drift, coupling, boundary review | Deferred | Architecture Owner | 6A.4 | Map/state/catalog, 6A.3 | Event-driven | Semantic |
| `08_CERTIFICATION_STANDARD.md` | Evidence matrix, verdict rules | Deferred | Certifier | 6A.5 | 6A.3–6A.4 records | Event-driven | Semantic |
| `09_REPOSITORY_INSPECTION.md` | Repeatable inspection techniques | Deferred | Governance Lead | 6A.2 | 6A.1 manual | Event-driven | Semantic |
| `10_BATCH_WORKFLOW.md` | Batch sizing, scope, evidence rules | Deferred | TPM | 6A.6 | Pilot learnings | Event-driven | Semantic |
| `11_SPRINT_WORKFLOW.md` | Sprint planning, review, certification | Deferred | TPM | 6A.6 | Sprint learnings | Event-driven | Semantic |
| `12_MILESTONE_WORKFLOW.md` | Milestone readiness, closeout | Deferred | TPM / Architecture Owner | 6A.6 | Certification strategy | Event-driven | Semantic |
| `13_ENGINEERING_CHECKLISTS.md` | Role-specific controls | Planned | Governance Lead | 6A.1 | All standards | Event-driven | Semantic |
| `templates/` (registry) | Controlled template navigation | Planned | Governance Lead | 6A.1 | Relevant standards | Event-driven | Semantic |
| `templates/ENGINEERING_DOCUMENT_TEMPLATE.md` | Controlled document metadata | Registered Only | Governance Lead | 6A.1 | Execution Plan | Event-driven | Semantic |
| `templates/ENGINEERING_SPECIFICATION_TEMPLATE.md` | Standard future specification structure | Approved | Architecture Owner | 6A.1 | 03_ENGINEERING_SPECIFICATION_STANDARD.md | Event-driven | Semantic |
| `templates/IMPLEMENTATION_PROMPT_TEMPLATE.md` | Bounded AI/human implementation instruction | Registered Only | Governance Lead | 6A.5 | Implementation standard | Event-driven | Semantic |
| `templates/REPOSITORY_EVIDENCE_TEMPLATE.md` | Capture reproducible facts | Deferred | Governance Lead | 6A.2 | 09_REPOSITORY_INSPECTION.md | Event-driven | Semantic |
| `templates/CHANGESET_VERIFICATION_TEMPLATE.md` | Record integration completeness | Deferred | Change-set Verifier | 6A.3 | 05_CHANGESET_VERIFICATION.md | Event-driven | Semantic |
| `templates/ARCHITECTURE_VERIFICATION_TEMPLATE.md` | Record dependency, runtime drift | Deferred | Architecture Owner | 6A.4 | 07_ARCHITECTURE_VERIFICATION.md | Event-driven | Semantic |
| `templates/CERTIFICATION_TEMPLATE.md` | Criterion-to-evidence record | Deferred | Certifier | 6A.5 | 08_CERTIFICATION_STANDARD.md | Event-driven | Semantic |
| `templates/REFINEMENT_TEMPLATE.md` | Focused response to finding | Deferred | Governance Lead | 6A.5 | Prompt workflow | Event-driven | Semantic |
| `templates/ACCEPTANCE_TEMPLATE.md` | Authorized decision acknowledgement | Deferred | Governance Lead | 6A.5 | Certification standard | Event-driven | Semantic |
| `templates/ADR_TEMPLATE.md` | Consequential architecture decision | Registered Only | Architecture Owner | N/A | ADR lifecycle | Event-driven | Semantic |
| `templates/IDENTITY_CARD_TEMPLATE.md` | Subsystem purpose, contracts | Registered Only | Component Owner | 6A.4 | Architecture verification | Event-driven | Semantic |

## Engineering Knowledge Ecosystem
To prevent ambiguity, it is crucial to distinguish between the following layers of the engineering knowledge ecosystem:

- **Engineering Governance**: The immutable rules of the project (Engineering Constitution) and the execution blueprints (Milestone Execution Plan).
- **Engineering Manual**: The operational standards and templates contained within this directory.
- **Repository Knowledge**: Verified, point-in-time facts about what exists in the repository.
- **Architecture Knowledge**: High-level structural documentation such as Architecture Maps, State, and Component Catalogs.
- **Engineering Records**: Point-in-time evidentiary files like ADRs, Technical Debt Registers, and Health Reports.

## Future Engineering Artifacts
The immediate repository focus involves delivering the remaining documents for Sprint 6A.1 and then moving through Sprints 6A.2 to 6A.6. 

Because we do not invent repository facts, any artifact that cannot be explicitly verified must be marked UNKNOWN. The following artifact categories have not yet been established and verified, and are therefore currently categorized as follows:

**Repository Knowledge**
- Repository Snapshot: **UNKNOWN**
- Repository Quality Dashboard: **UNKNOWN**

**Architecture Knowledge**
- Architecture State: **UNKNOWN**
- Architecture Map: **UNKNOWN**
- Component Catalog: **UNKNOWN**
- Identity Cards: **UNKNOWN**

**Engineering Records**
- ADRs: **UNKNOWN**
- Technical Debt Register: **UNKNOWN**
- Runtime Health Reports: **UNKNOWN**

*(No placeholder documents exist for these UNKNOWN artifacts. They will be created strictly in their owning batches based on repository evidence.)*
