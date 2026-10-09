# DAS process design, current as of October 2026 (for review before code)

Every stage and gate below cites `01_sources_and_findings.md` (S1-S6 = primary documents in
`data/policy/` and `data/`). Scope: the **Major Capability Acquisition (MCA)** pathway, built through
**Milestone A and the SRR**. Later phases and the other pathways are defined in the process file
but not built.

## 1. The flow

```
 1  Service capability requirement document        [agents draft]      S3 Encl. A 6.b, Encl. C 3.f
 2  Service Requirements Validation          ◆ HUMAN  Service board       S1 p.1, Att.4; S2 1.b
 3  Joint review (JCI): JSD + endorsement     ◆ HUMAN  JROC/JCB/FCB by JSD S3 Encl. A 6, Encl. B 2.b
 4  Materiel Development Decision (MDD)       ◆ HUMAN  MDA                 S5 3.5
      (pathway + phase of entry; AoA study guidance/plan; ADM)        S4 4.1, S5 3.5.c
 5  MSA phase                                       [agents]          S5 3.6
      AoA summary · affordability · early SE analysis
      SE: Alternative Systems Review (ASR) → draft performance specification   S6 3.1
      draft CDD-equivalent (Service-approved)                          S5 3.7.a(1)
 6  Milestone A package                             [agents]          S5 3.7.a(2), 3.7.b
 7  Milestone A                               ◆ HUMAN  MDA (ADM)           S5 3.7.c
 8  TMRR phase, SE: System Requirements Review (SRR)  [agents prepare]  S6 3.2; S5 3.8
 9  SRR technical review                      ◆ HUMAN  chief engineer/PM   S6 3.2
 ── designed, not built: SFR → PDR → CDD-equivalent validation → Development RFP Release →
    Milestone B (S5 3.8-3.10); MTA, Software and other pathways (S4 4.2)
```

**Why this order** (the domain point Gemini raised, corrected against the sources):
- Requirements are validated by the **Service** (S1, S2). The joint step is an **endorsement review**
  sized by the JSD, not a universal JROC gate (S3).
- The **MDD** is the mandatory entry to MCA and is where the MDA sets the phase of entry (S5 3.5).
- **Systems engineering feeds the milestone**: the ASR runs in MSA and produces the draft performance
  specification behind Milestone A (S6 3.1). The **SRR follows Milestone A**, in TMRR (S6 3.2). This
  is the correction to Gemini's "SRR before the milestone", which holds only for Milestone B.

## 2. Gates (human decisions; all through K9X HIL)

| Gate id | Who decides (role) | Entry criteria (from the sources) | Decision record |
|---|---|---|---|
| `SERVICE-VALIDATION` | Service requirements board | JFRP minimum content complete: operational context (task, CONOPS); SIC/DIA threat with CIPs; capability requirements/performance attributes traceable to gaps; TRL/MRL; projected cost, schedule, quantity; joint integration (S3 A 6.b) | Service validation memo |
| `JOINT-REVIEW` | JROC / JCB / FCB per JSD; "Service Information" = no joint review | JSD assigned from ACAT and joint dependencies (S3 B 2.b); JCRs in the official format (S3 C 3.f(2)) | JROCM: endorse all / some / none; tripwires; critical JCRs (S3 A 6.c) |
| `MDD` | MDA | validated requirement document; AoA study guidance and study plan (S5 3.5.a) | ADM: phase of entry, initial review milestone (S5 3.5.c) |
| `MILESTONE-A` | MDA | ASR complete with a draft performance spec; AoA; affordability (fully funded in the FYDP); risks with funded mitigation; acquisition strategy; test strategy; Component-approved draft CDD-equivalent; ICE/ITRA for MDAPs (S5 3.6-3.7, S6 3.1) | ADM: materiel solution, TMRR strategy, RFP release, TMRR exit / EMD entry criteria (S5 3.7.c) |
| `SE-REVIEW-SRR` | Chief engineer / PM (technical review) | SRR criteria (S6 3.2, Table 3-2): requirements consistent with the preferred solution and technology plans, measurable and testable, traceable | Review minutes, action items |

`JOINT-REVIEW` is **non-blocking by design** (an endorsement, S3 A 6.c). A job proceeds when the
JROCM is recorded, whatever it endorses; its tripwires and critical JCRs carry forward as evidence.
`ACAT` and joint dependencies come from the input document.

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
| gate `JROC-VALIDATION` | `SERVICE-VALIDATION` + `JOINT-REVIEW` | Two HIL tasks; the JSD is computed and shown |
| — (new) | `MDD` gate | HIL task; ADM fields |
| `AcquisitionOrchestrator` | `MsaOrchestrator` (AoA summary, affordability, SE: ASR) + Milestone A package | The GateReadiness and PackageAssembly squads are reused; **new ASR agents** (preferred solution, draft performance spec, technical risks) |
| gate `PATHWAY-MILESTONE` | `MILESTONE-A` | Criteria from S5 3.7 / S6 3.1; the computed readiness score stays |
| `SeOrchestrator` (demo endpoint) | `TmrrOrchestrator`: SRR package + `SE-REVIEW-SRR` gate | SRR criteria from S6 Table 3-2 |
| `traceability_orchestrator` | unchanged | |

Topic and HIL plumbing (`hil_gateway`, reply topics, resume) stays; it gains stage and gate entries.
Demo-mode behaviour (shared queue, 2 jobs per visitor, own Generated Docs) is **unchanged**.

## 5. Inputs

The current demo documents (FIREBIRD, IRONCLAD, SENTINEL, F-22, Kestrel) are written as ICD/CDD-style
documents. Each stays usable: DAS treats it as a **Service capability requirement document (legacy
JCIDS format)**, which S2 Encl. A 7 explicitly allows. Optionally, new demo inputs can use the JFRP
minimum-content headings.

## 6. Verification

1. **Second-model review of this design** against the source excerpts in `01_sources_and_findings.md`
   (independent of the author model), before code.
2. Unit tests: process file loads; every stage and gate cites a source; gate order; the joint review
   is non-blocking; criteria present.
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
2. JOINT-REVIEW non-blocking (an endorsement, as the manual says)? Recommended yes.
3. Rollout via a second URL first?
