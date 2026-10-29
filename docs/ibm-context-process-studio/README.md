# DAS inputs for IBM Context Studio and Process Studio

This folder holds the inputs behind the Defense Acquisition System (DAS) application, live at
https://das.k9x.ai, packaged for IBM Context Studio and Process Studio. It lets anyone run the same
use case through those tools and compare the output with the working implementation.

The use case is **capability requirement to Milestone A**, Major Capability Acquisition pathway,
process model `mca-2026-10` (as of 2026-10-09):

Sponsor documents → normalisation and screening → Service-format requirement → Service Requirements
Validation → Joint Capability Integration review (parallel, non-blocking) → Materiel Development
Decision → Materiel Solution Analysis → Milestone A → System Requirements Review.

AI agents prepare every package; a person makes every gate decision.

Everything here is public or synthetic. The policy documents are public DoD and Joint Staff
publications. The program documents are fictional.

This folder is documentation only. The DAS application does not read it, and nothing here appears
in the das.k9x.ai document list.

## Contents

| Path | What | Use in |
|---|---|---|
| `01_context_studio/sources/` | The seven policy documents DAS is built on (table below) | Context Studio |
| `01_context_studio/schema.jsonld` | DAS domain schema: 6 entities (CapabilityRequirement, JCIReview, AcquisitionProgram, GateReview, SERequirement, DASJob) with their attributes, states, transitions and invariants | Context Studio |
| `01_context_studio/process_model.yaml` | The DAS process model the application runs: stages, gates, entry criteria and sources. Copy of `src/k9_dow/config/process_model.yaml` | Context Studio (reference) |
| `01_context_studio/corpus/` | Synthetic knowledge corpus DAS retrieves from: three prior CDDs, DoDAF view references and a review-package reference | Context Studio |
| `02_process_studio/process_sop.md` | Standard operating procedure for the same flow: steps, gates, entry criteria, controls, exceptions, KPIs, escalation | Process Studio |
| `03_sample_input/FIREBIRD_UAV_Capability_Development_Document.md` | A fictional sponsor document, one of the DAS demo inputs | Optional: simulate an intake |

### Policy sources

| Ref | Document | File |
|---|---|---|
| S1 | SecDef/DepSecDef memo, Reforming the Joint Requirements Process to Accelerate Fielding of Warfighting Capabilities (20 Aug 2025) | `SecDef_Memo_2025-08-20_requirements.pdf` |
| S2 | CJCSI 5123.01J, Charter of the JROC and the Joint Force Requirements Process, CH 1 (05 Aug 2026) | `CJCSI 5123.01J CH 1.pdf` |
| S3 | CJCSM 5123.01A, Manual for the JROC and the Joint Force Requirements Process (05 Aug 2026) | `CJCSM 5123.01A.pdf` |
| S4 | DoWI 5000.02, Operation of the Adaptive Acquisition Framework, Change 2 (08 Apr 2026) | `500002p.pdf` |
| S5 | DoDI 5000.85, Major Capability Acquisition, Change 1 (04 Nov 2021) | `500085p.pdf` |
| S6 | DoD Systems Engineering Guidebook (Feb 2022) | `SE-Guidebook-Feb2022.pdf` |
| S8 | Joint Staff briefing, Implementation of CJCSI 5123.01J and CJCSM 5123.01 (Aug 2026), cross-check only | `JFRP_overview_mhsrs.pdf` |

## How to run it

1. **Context Studio:** load `schema.jsonld`, the policy sources and the corpus. If the tool limits the
   number of documents, start with S1 (SecDef memo) and S6 (SE Guidebook); S2 and S3 carry most of
   the requirements-process detail.
2. **Process Studio:** upload `02_process_studio/process_sop.md` and run the analysis, then generate
   the blueprint and implementation artifacts.

## How to compare with DAS

- **Live application:** https://das.k9x.ai. Use the demo sign-in shown on the landing page; the
  FIREBIRD document is in the demo list.
- **Saved DAS output for FIREBIRD:**
  [`docs/process-model-2026/evidence/firebird_2026-10-15_JOB-20261015-1108EA/`](../process-model-2026/evidence/firebird_2026-10-15_JOB-20261015-1108EA/)
  (requirement package, Joint Staffing Designator recommendation, screening report, independent-model
  quality check) and
  [`docs/process-model-2026/evidence/writers_firebird_2026-10-09/`](../process-model-2026/evidence/writers_firebird_2026-10-09/)
  (MDD, MSA and SRR stage drafts).
- **Process design and sources:** [`docs/process-model-2026/`](../process-model-2026/).

Useful checks on generated output:

- Does every claim trace to these inputs?
- Are the SOP's explicit rules kept? For example, a screening warning is never a rejection, the JCI
  review never blocks, and the readiness score is computed in code.
- Is every SOP step covered?
- Are values the SOP leaves to the Service left open rather than filled in?
