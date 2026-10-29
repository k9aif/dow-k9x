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

DAS and K9-AIF are independent, vendor-neutral open-source projects, not IBM products. IBM Context
Studio and Process Studio are named only as the tools these inputs are prepared for.

This folder is documentation only. The DAS application does not read it, and nothing here appears
in the das.k9x.ai document list.

## Contents

| Path | What | Use in |
|---|---|---|
| `01_context_studio/sources/README.md` | The seven policy documents DAS is built on: publisher pages and links to the copies in this repository (`data/policy/`, `data/`) | Context Studio |
| `01_context_studio/schema.jsonld` | DAS domain schema: 6 entities (CapabilityRequirement, JCIReview, AcquisitionProgram, GateReview, SERequirement, DASJob) with their attributes, states, transitions and invariants | Context Studio |
| `01_context_studio/knowledge-corpus.md` | How the DAS knowledge was built: policy turned into the cited process model and mappings; the synthetic reference corpus (`data/synthetic_corpus/`) seeded into pgvector | Context Studio |
| `02_process_studio/process_sop.md` | Standard operating procedure for the same flow: steps, gates, entry criteria, controls, exceptions, KPIs, escalation | Process Studio |
| `03_sample_input/FIREBIRD_UAV_Capability_Development_Document.md` | A fictional sponsor document, one of the DAS demo inputs | Optional: simulate an intake |

### Policy sources

S1 SecDef memo (20 Aug 2025); S2 CJCSI 5123.01J CH 1; S3 CJCSM 5123.01A; S4 DoWI 5000.02; S5 DoDI 5000.85;
S6 DoD SE Guidebook (Feb 2022); S8 Joint Staff JFRP implementation briefing. Download links and release
statements: [`01_context_studio/sources/README.md`](01_context_studio/sources/README.md).

## How to run it

1. **Context Studio:** load `schema.jsonld`, the policy sources (download them first; see
   `01_context_studio/sources/README.md`) and the synthetic corpus in `data/synthetic_corpus/`. See
   `01_context_studio/knowledge-corpus.md` for what each layer is. If the tool limits the number of
   documents, start with S1 (SecDef memo) and S3 (CJCSM 5123.01A).
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
