# Proposed plan: an SE pipeline built on K9-AIF, alongside DAS

Status: proposal for discussion (2026-10-15). Nothing here is built yet except what is marked **exists in DAS**.
Public page: das.k9x.ai/se (`src/k9_dow/api/static/se.html`).

## 1. The idea in plain words

Building a complex system (an aircraft, a radar) means passing a series of **engineering checkpoints**. At each
one, engineers show a review board that the design is ready for the next step. Each checkpoint has its own
**checklist** and its own set of **documents** to prepare.

DAS already does this for the *buying* side of defense acquisition: AI agents read the paperwork, prepare the
documents for each checkpoint, check them against their sources, and a person approves or rejects. DAS also
already handles the first engineering checkpoint, the System Requirements Review (SRR).

The SE pipeline is the same engine applied to the *engineering* checkpoints:

| | Stays the same | Changes for SE |
|---|---|---|
| Engine | K9-AIF: governance on every agent, a person approves every checkpoint (K9X HIL), outputs graded against their sources, failures recorded, everything audited | |
| Checkpoints and checklists | | The engineering reviews and their entry criteria (a data file, not code) |
| Documents (artifacts) | | Requirements, design models, interface descriptions in; review packages and test plans out |
| Agent roles | Some DAS agents carry over (below) | A few new roles for engineering work |

**One sentence for a stakeholder:** same engine and safety; new checklists, new documents, and a few new agent
roles, some of which DAS already has.

## 2. Where it lives

- **Code:** a separate solution built on K9-AIF (its own process file, squads, agents and orchestrator), so DAS
  stays stable and each can change on its own.
- **For users:** the same site. An "Engineering reviews" section of das.k9x.ai (for example `/se`) with the same
  login, program list, job list and K9X HIL review queues. A viewer sees one system following one program from
  requirement to design reviews.
- **Connection to DAS:** by events, at the points where the two meet (below). Neither knows the other's insides.

## 3. Does DAS have to be finished first?

**No.** SE needs one thing from DAS: an **approved requirements baseline**, which DAS already produces at the SRR.
The parts of DAS not yet built (Milestone B onward) are not prerequisites. A pilot can even start from an
existing approved requirements document, with no DAS run at all.

How the two exchange work:

| From | To | What | When |
|---|---|---|---|
| DAS | SE | Approved requirement + SRR package + traceability + architecture views | After the SRR decision |
| SE | DAS | Technical review results as evidence | Before the next milestone decision (for example PDR results before Milestone B) |

## 4. The engineering checkpoints (to confirm with an SE expert)

The usual sequence of technical reviews. **Confirm the current set, names and entry criteria against DoDI 5000.88
(Engineering of Defense Systems) and the DoD Systems Engineering Guidebook (2022) before building**: DAS was once
built on a process that had already been replaced, so currency is checked first.

| Checkpoint | Plain words | Status |
|---|---|---|
| SRR, System Requirements Review | Do we understand what the system must do? | **Exists in DAS** |
| SFR, System Functional Review | Are the functions defined and the requirements split into them? | New |
| PDR, Preliminary Design Review | Is the overall design ready to be detailed? | New (pilot candidate) |
| CDR, Critical Design Review | Is the detailed design ready to build? | New |
| TRR, Test Readiness Review | Are we ready to test? | New |

## 5. Agents

**Carry over from DAS (exist today):**

| Squad | Agents | SE use |
|---|---|---|
| Traceability | LinkProposer, LinkValidator, OrphanDetector, CoverageScorer | Every requirement traced to design and test; orphans found |
| Drift detection | BaselineDiffer, DriftClassifier (FundingDiffer is acquisition-only) | What changed since the last approved baseline, and does it matter |
| Gate readiness | CriteriaLoader, EvidenceCollector, ReadinessScorer, GapReporter | Readiness for each review against its entry criteria |
| Architecture views | ModelExtractor, ViewGenerator, ViewConsistencyChecker | System views kept consistent with each other |

**New roles (to build):**

| Agent | What it does |
|---|---|
| Requirements decomposer | Splits system requirements into functional and subsystem requirements |
| Interface analyst | Lists interfaces between parts and checks each side agrees |
| Verification planner | Proposes how each requirement will be tested, inspected or analyzed |
| Review package builder | Assembles the package for each review from the outputs above |

**MBSE link:** an integration adapter to read and write SysML v2 models (through the SysML v2 API), so agents
work on the engineers' models, not only documents. This is the one genuinely new kind of integration.

## 6. Documents in and out

| In | Out |
|---|---|
| Approved requirements and SRR package (from DAS or the program) | Review package per checkpoint |
| Design model (SysML v2) or design documents | Requirement decomposition and allocation |
| Interface descriptions | Interface list with mismatches flagged |
| Previous review decisions | Verification plan; traceability report; readiness score with gaps |

Every output is graded against its sources, as in DAS; where a source is silent, the agent says so.

## 7. How to start: a pilot of one checkpoint

1. **Pick one review** (PDR is a good candidate: it is the next big step after SRR) and **one program's real
   artifacts**.
2. **A systems engineering expert supplies the checklist** (entry criteria) and judges the output.
3. **Build:** the PDR process file, the four new agents, the review package template; reuse the DAS squads above.
   The SysML adapter can come second if the pilot starts from documents.
4. **Run it** end to end with the expert deciding in K9X HIL; compare against how the review was prepared by hand.
5. **Decide** on the next checkpoints from what the pilot shows.

## 8. Honest scope

- Proposed, not built (except the reused DAS squads and the SRR).
- The checkpoints and criteria must be confirmed by an SE expert against current DoD guidance.
- The pilot proves the approach on one review; it does not replace engineering judgement. People decide at every
  checkpoint.
- K9-AIF can run existing CrewAI work inside it, governed (orchestrator adapter), so earlier efforts need not be
  thrown away.
