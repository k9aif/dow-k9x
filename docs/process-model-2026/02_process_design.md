# DAS process design, current as of October 2026 (for review before code)

Every stage and gate below cites `01_sources_and_findings.md` (S1-S6 = primary documents in
`data/policy/` and `data/`). Scope: the **Major Capability Acquisition (MCA)** pathway, built through
**Milestone A and the SRR**. Later phases and the other pathways are defined in the process file
but not built.

## 1. The flow (revised after the independent review, 03_independent_review.md)

```
 1  Service capability requirement document (Service format)  [agents draft]   S3 A 6.b, E 1.b
 2  Service Requirements Validation          ◆ HUMAN  Service board              S1 p.1; S2 1.b
        │
        ├──► 2J  Joint Capability Integration review   ◆ HUMAN (JROC/JCB/FCB per JSD)
        │        PARALLEL, non-blocking: "after Service/component requirements validation
        │        and in parallel with Service acquisition processes"            S3 A 6.c-d, B 2.b
        │        → JROCM: endorse (all/some/none) or reject; tripwires; critical JCRs,
        │          carried into Milestone A as evidence when available
        ▼
 3  Materiel Development Decision (MDD)      ◆ HUMAN  MDA                       S5 3.5
        inputs: validated requirement document (ICD "or equivalent"), AoA study guidance + plan
        ADM: phase of entry, initial review milestone                       S5 3.5.c
 4  MSA phase                                        [agents]               S5 3.6
        AoA summary · affordability · early SE analysis · product support planning
        SE: Alternative Systems Review (best-practice review) → draft performance spec   S6 3.1
        draft CDD-equivalent, Component-approved                        S5 3.7.a(1)
        proposed acquisition strategy matched to a pathway (PM)          S4 4.1
 5  Milestone A package                              [agents]               S5 3.7.a-b
 6  Milestone A                              ◆ HUMAN  MDA (ADM)                  S5 3.7.c
        approves the acquisition strategy (incl. pathway match), TMRR entry, RFP release
 7  TMRR phase, SE: System Requirements Review package   [agents prepare]   S6 3.2; S5 3.8
 8  SRR technical review                     ◆ HUMAN  review chair (Service-appointed);
                                                       criteria tailored by the Chief Engineer   S6 3.2
 ── designed, not built: SFR → PDR → CDD-equivalent validation → Development RFP Release →
    Milestone B (S5 3.8-3.10); MTA, Software and other pathways (S4 4.2); RRAB / Joint
    Acceleration Reserve path for joint KOP/JOP-driven needs (S1 Att. 1, 3); JCI tripwires,
    breaches and comebacks (S3 A 9); SOFCIDS/CCIDS, CCMD-derived (CDR) and JICR paths (S2, S3)
```

**Why this order** (the domain point raised by Gemini, corrected against the sources and the review):
- Requirements are validated by the **Service** (S1, S2). **Joint Capability Integration runs in parallel**
  and does not hold up acquisition (S3 A 6.d). It is an endorsement-or-reject review whose
  reviewer is set by the Joint Staffing Designator (S3).
- The **MDD** is the mandatory entry to MCA; it sets the phase of entry and the initial review milestone
  (S5 3.5.c). **The pathway is not an MDD output**: the PM matches the acquisition strategy to a
  pathway, and **the MDA approves the acquisition strategy at Milestone A** (S4 4.1; S5 3.7.c).
- **Systems engineering informs the milestone**: the ASR (a best-practice review) runs in MSA and yields
  the draft performance specification (S6 3.1). The developer **SRR follows Milestone A** in TMRR; a
  government SRR on the draft RFP may come earlier (S6 3.2).

## 2. Gates (human decisions; all through K9X HIL)

| Gate id | Who decides | Entry criteria | Decision record |
|---|---|---|---|
| `SERVICE-VALIDATION` | Service requirements board | **Service-defined** (each Service owns its criteria, S2 1.b). DAS's demo check: the document carries what the Service must later submit to JCI (S3 A 6.b): operational context; SIC/DIA threat, CIPs; capability requirements/performance attributes traceable to gaps; TRL/MRL; projected cost, schedule, quantity; joint integration. **Performance attribute certifications are Service-owned** (net-ready, intelligence supportability, sustainment, energy, survivability/cyber survivability, exportability; S3 E 2) | Service validation record |
| `JCI-REVIEW` (parallel) | JROC / JCB / FCB per JSD; "Service Information" = awareness only | JSD **recommended by the sponsor and set through the Joint Requirements Coordinator (J-8)** on the five criteria of S3 B 2.b(2); the JRC may return a document to the Service | JROCM: endorse (all/some/none) or reject; tripwires; critical JCRs; recommendations to Service boards and the RRAB (S3 A 6.c) |
| `MDD` | MDA (Service Chief concurrence for MDAPs, S5 2.3.b) | validated requirement document ("or equivalent"); AoA study guidance and study plan (S5 3.5.a) | ADM: phase of entry, initial review milestone (S5 3.5.c) |
| `MILESTONE-A` | MDA (Service Chief concurrence for MDAPs, S5 2.3.b) | S5 3.7.a-b: justification, affordability and feasibility of the preferred solution; technologies to mature; requirement trade space; technical/cost/schedule risks with funded mitigation; **acquisition strategy (pathway match, IP, program protection, exportability)**; **cybersecurity** (S4 4.1.b(3)); test strategy; mission data plan and threat; **Should Cost** targets; framing assumptions; affordability (fully funded in the FYDP); Component-approved draft CDD-equivalent; for MDAPs: ICE, ITRA, goals approved (S5 3C), and the **10 U.S.C. 2366a** technology-delay determination. ASR results as evidence (best practice, S6 3.1); JCI JROCM and tripwires when available | ADM: materiel solution, acquisition strategy, TMRR strategy, final RFP release, TMRR exit / EMD entry criteria (S5 3.7.c) |
| `SE-REVIEW-SRR` | Review chair appointed by the Service; criteria tailored by the Chief Engineer | S6 3.2 body (requirements consistent with the preferred solution and technology plans, measurable, testable, traceable) and Table 3-2 products as tailored | Review minutes, action items |

Requirement statements: DAS writes Service capability requirements in a **Service format**. The JCR
statement format ("The ability to … against … in order to achieve … under … in accordance with …";
S3 C 3.f(2)) belongs to **joint** documents (CRD, JDCR, CDR) and is used only where DAS drafts a joint
document. It is not a criterion for a Service requirement.

## 3. Process definition as configuration (versioned, "as of")

`src/k9_dow/config/process_model.yaml` (new; sole source for stages, gates, criteria, sources):

```yaml
process_model:
  id: mca-2026-10
  as_of: 2026-10-09
  pathway: major_capability_acquisition
  sources:                      # each maps to a file in data/policy and a section
    S1: {title: "SecDef memo, Reforming the Joint Requirements Process", date: 2025-08-20}
    S2: {title: "CJCSI 5123.01J CH 1", date: 2026-08-05}
    # ...
  stages:   [ {id, title, kind: agents|gate, squad|gate_id, after, sources: [S5 3.6, ...]} ]
  gates:    [ {id, authority_role, entry_criteria: [...], decision_record, blocking: true|false, sources} ]
  designed: [SFR, PDR, CDD-VALIDATION, DEV-RFP-RELEASE, MILESTONE-B]
```

The gate registry, the orchestrators, the HIL task titles and the UI cards **read this file**. The
next reform becomes a new `process_model` version (e.g. `mca-2027-xx`), with the old one kept for
past jobs.

## 4. Mapping onto the existing code (reuse first)

| Today | Becomes | Notes |
|---|---|---|
| `JcidsOrchestrator` (ICD + DoDAF views) | `RequirementOrchestrator` | Same squads (ViewGeneration, GateReadiness). The output is a **Service capability requirement document** with JFRP minimum content and JCR statements; DoDAF views (OV-1, etc.) stay as supporting architecture |
| gate `JROC-VALIDATION` | `SERVICE-VALIDATION` + parallel `JCI-REVIEW` | Two HIL tasks; the JCI task runs alongside the acquisition flow; DAS proposes a JSD for the reviewer to confirm |
| — (new) | `MDD` gate | HIL task; ADM fields |
| `AcquisitionOrchestrator` | `MsaOrchestrator` (AoA summary, affordability, SE: ASR) + Milestone A package | The GateReadiness and PackageAssembly squads are reused; **new ASR agents** (preferred solution, draft performance spec, technical risks) |
| gate `PATHWAY-MILESTONE` | `MILESTONE-A` | Criteria from S5 3.7 / S6 3.1; the computed readiness score stays |
| `SeOrchestrator` (demo endpoint) | `TmrrOrchestrator`: SRR package + `SE-REVIEW-SRR` gate | SRR criteria from S6 Table 3-2 |
| `traceability_orchestrator` | unchanged | |

Topic and HIL plumbing (`hil_gateway`, reply topics, resume) stays; it gains stage and gate entries.
Demo-mode behaviour (shared queue, 2 jobs per visitor, own Generated Docs) is **unchanged**.

## 5. Inputs

The current demo documents (FIREBIRD, IRONCLAD, SENTINEL, F-22, Kestrel) are written as ICD/CDD-style
documents. Each stays usable as a **Service capability requirement document**: "Services/components will use
Service/component document formats" (S3 A 6.b, E 1.b), so a legacy ICD-style layout is acceptable as
the Service's own format. (CJCSI Encl. A 7 covers documents *previously validated* under JCIDS.) Optionally, new demo inputs can use the JFRP
minimum-content headings.

## 6. Verification

1. **Second-model review of this design** against the source excerpts in `01_sources_and_findings.md`
   (independent of the author model), before code.
2. Unit tests: process file loads; every stage and gate cites a source; gate order; the JCI review
   runs in parallel and never blocks the MDD or Milestone A; criteria present.
3. `k9aif inspect`: still compliant (no new violations).
4. **Live end-to-end runs** on the deployment through all four human gates plus the SRR review,
   recorded like S15.
5. Rollout: **separate URL first** (e.g. `das-next.k9x.ai`), then replace das.k9x.ai.

## 7. Paper changes (after the code is verified)

- Section VI (DAS): stages, gates and Fig. 7 (flow) redrawn from the process file; the process is
  "current as of October 2026" with citations to CJCSI 5123.01J, CJCSM 5123.01A (Joint Staff
  library: https://www.jcs.mil/library/cjcs-manuals/), DoWI 5000.02 Ch 2, DoDI 5000.85 and the SE
  Guidebook.
- S15: new live runs. Table 9 / S5: agent, squad and orchestrator counts. S4: re-inspection.
- Response letter: answers that cite JROC-VALIDATION / PATHWAY-MILESTONE updated.
- Table 10: a new DAS release + DOI.
- Unchanged: the governance evaluation, the LangGraph comparison (it uses the GateReadiness squad,
  whose behaviour is unchanged), and the HIL experiments.

## 8. Decisions for Ravi

1. Scope: MCA through Milestone A + SRR (recommended), other pathways designed only?
2. JCI review as a **parallel**, non-blocking human review (CJCSM Encl. A 6.d: "in parallel with Service acquisition processes")? Recommended yes.
3. Rollout via a second URL first?
