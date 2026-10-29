---

# Standard Operating Procedure: Capability Requirement to Milestone A (with System Requirements Review)

**Document type:** Standard Operating Procedure (SOP)  
**Organisation:** Department of War (illustrative; Defense Acquisition System demonstration)  
**Process:** Capability requirement to Milestone A, Major Capability Acquisition pathway  
**Owner:** Capability Sponsor (Service requirements office)  
**Approved by:** Service requirements board / Milestone Decision Authority  
**Process model:** mca-2026-10 (as of 09 October 2026)  
**Version:** 1.0  
**Classification:** UNCLASSIFIED  

> This SOP describes the flow the Defense Acquisition System (DAS) application runs. It is written from public DoD and Joint Staff policy and from the DAS process model; it is not an official DoD procedure. Where policy leaves a value to the Service or the decision authority (for example review timelines), this SOP says so instead of inventing one.

---

## 1. Purpose

This document defines the end-to-end procedure for taking a **Service capability requirement** from the sponsor's source documents to a **Milestone A** decision and a **System Requirements Review (SRR)**, on the Major Capability Acquisition pathway of the Adaptive Acquisition Framework.

The procedure follows the requirements reform that replaced the Joint Capabilities Integration and Development System (JCIDS): a Service validates its own requirement, a Joint Capability Integration (JCI) review runs in parallel and never blocks acquisition, and the Milestone Decision Authority (MDA) decides at the Materiel Development Decision (MDD) and Milestone A.

AI agents in DAS prepare every package: they normalise and screen documents, draft the requirement, assemble evidence and score readiness against each gate's entry criteria. **Every decision is made by a person.** No agent may make, synthesise or impersonate a decision.

Sources:

| Ref | Source | Date |
|---|---|---|
| S1 | SecDef/DepSecDef memo, Reforming the Joint Requirements Process to Accelerate Fielding of Warfighting Capabilities | 20 Aug 2025 |
| S2 | CJCSI 5123.01J, Charter of the JROC and the Joint Force Requirements Process (CH 1) | 05 Aug 2026 |
| S3 | CJCSM 5123.01A, Manual for the JROC and the Joint Force Requirements Process | 05 Aug 2026 |
| S4 | DoWI 5000.02, Operation of the Adaptive Acquisition Framework (Change 2) | 08 Apr 2026 |
| S5 | DoDI 5000.85, Major Capability Acquisition (Change 1) | 04 Nov 2021 |
| S6 | DoD Systems Engineering Guidebook | Feb 2022 |

---

## 2. Scope

This SOP applies to:

- Service capability requirements submitted to DAS for drafting and validation under the Joint Force Requirements Process (JFRP)
- The Major Capability Acquisition pathway from the Materiel Development Decision through Materiel Solution Analysis (MSA), Milestone A, and the System Requirements Review in Technology Maturation and Risk Reduction (TMRR)
- All roles listed in Section 3 and the DAS application, K9X HIL and supporting services

**Exclusions (defined in policy, not built in this version):** System Functional Review; Preliminary Design Review; CDD-equivalent validation; Development RFP Release decision point; Milestone B; the Middle Tier, Software, Urgent, Business Systems and Services pathways; the RRAB and Joint Acceleration Reserve path; JCI tripwires, breaches and comebacks; SOFCIDS, CCIDS, CCMD-derived requirements and JICR.

---

## 3. Roles and Systems

### Roles

| Role | Responsibility |
|---|---|
| Capability Sponsor | Submits the source documents (CONOPS/CONEMP, threat assessment, gap analysis and similar), answers reviewer questions, and reworks and resubmits when a package is returned. |
| Service requirements board | Validates the Service capability requirement (Service Requirements Validation). Validation criteria are Service-defined (S2 1.b). |
| Joint Requirements Coordinator (J-8) | Sets the Joint Staffing Designator from the sponsor's recommendation, using the five criteria of CJCSM 5123.01A Encl. B 2.b(2). |
| JROC / JCB / FCB | Conducts the Joint Capability Integration review by Joint Staffing Designator; issues a JROCM (endorse all, some or none, or reject). Service Information designations are for awareness only. |
| Milestone Decision Authority (MDA) | Decides at the Materiel Development Decision and Milestone A; issues the Acquisition Decision Memorandum. Service Chief concurrence is required for MDAPs. |
| Technical review chair | Chairs the System Requirements Review; appointed by the Service, with criteria tailored by the Chief Engineer. |
| DAS agents (squads) | Prepare only: normalise and screen documents, draft the requirement, assemble packages, and score readiness per criterion. Agent role: PREPARE_ONLY. |
| DAS administrator | Operates the DAS job queue; may withdraw any job. |

### Systems

| System | Purpose |
|---|---|
| DAS (Defense Acquisition System application) | Runs the requirement, MDD package, MSA and TMRR orchestrator runs; keeps results by job id; holds the requirements traceability graph. |
| K9X HIL | Human-in-the-loop case management. Each gate is a queue (for example "Requirements (JFRP) / Service Requirements Validation", "Major Capability Acquisition / Milestone A"); the decision authority approves, rejects or returns for rework there. |
| Docling | Converts PDF, Word and scanned input to Markdown (layout and OCR); the original is kept. |
| k9x Shield and IBM Granite Guardian | Screen every section of every source document; findings go to the Document Screening Report. |
| Requirements traceability graph (Neo4j) | Links capability need, capability documents, SE requirements, technical baseline items, DoDAF views, test cases, funding lines and the SEP baseline. |

---

## 4. Process Overview

**Phase 1: Intake and screening.** The sponsor uploads source documents to DAS. DAS normalises them to Markdown and screens every section. Warnings are reported, never used to reject a document.

**Phase 2: Requirement drafting and Service validation.** DAS drafts the Service-format requirement with the content the Service later submits for joint review (S3 Encl. A 6.b), scores readiness against the Service Requirements Validation criteria, and sends the package to K9X HIL. The Service requirements board decides. In parallel, the requirement goes to the JCI review, which never blocks the flow.

**Phase 3: Materiel Development Decision.** On validation, DAS prepares the MDD package (validated requirement, draft AoA study guidance, AoA study plan). The MDA decides and issues an Acquisition Decision Memorandum.

**Phase 4: Materiel Solution Analysis and Milestone A.** DAS prepares the AoA summary, affordability analysis, early systems engineering (Alternative Systems Review yielding a draft performance specification), a draft CDD-equivalent and a proposed acquisition strategy matched to a pathway, then assembles the Milestone A package. The MDA decides.

**Phase 5: TMRR System Requirements Review.** DAS prepares the SRR package. The technical review chair decides; minutes and actions are recorded.

---

## 5. Detailed Procedures

**Step 1: Submit and normalise**

**Trigger:** The Capability Sponsor uploads source documents to DAS  
**Owner:** Capability Sponsor; DAS intake  
**System:** DAS, Docling  

1. Upload the source documents (PDF, Word or scan) through DAS.
2. DAS queues a requirement job. The shared queue has a fixed maximum size and each visitor may have at most two jobs queued or running; submissions over either limit are refused, not queued.
3. DAS converts each document to Markdown with Docling and keeps the original.

**Control point:** The original document is retained alongside its Markdown form so every later statement can be traced to its source.

---

**Step 2: Screen the documents**

**Owner:** DAS requirement orchestrator  
**System:** k9x Shield, IBM Granite Guardian  

1. Screen every section for prompt injection and unsafe content.
2. Record every warning in the Document Screening Report.
3. Continue to drafting. A warning is reported, never a rejection.

**Control point:** No section reaches a drafting agent unscreened.

---

**Step 3: Draft the Service capability requirement**

**Owner:** DAS requirement squads  
**System:** DAS  
**Sources:** S3 Encl. A 6.b, S3 Encl. E 1.b  

1. Draft the Service-format requirement document, covering the content the Service later submits for joint review.
2. Record traceability from each capability requirement and performance attribute to the capability gap it addresses.
3. Identify the Service-owned performance attribute certifications (net-ready, intelligence supportability, sustainment, energy, survivability and cyber survivability, exportability).

---

**Step 4: Service Requirements Validation (gate)**

**Owner:** Service requirements board  
**System:** K9X HIL (Requirements (JFRP) / Service Requirements Validation)  
**Gate type:** Prepare / decide; blocking; non-delegable  
**Sources:** S1 p.1, S2 para 1.b, S3 Encl. A 6.b, S3 Encl. E 2  

DAS scores readiness against each entry criterion; the score is computed in code from per-criterion verdicts, never by the language model:

1. Operational context: joint and/or Service task; CONOPS or CONEMP
2. Threat: SIC/DIA-approved threat assessment; critical intelligence parameters; intelligence supportability
3. Capability requirements and/or performance attributes, traceable to capability gaps
4. Technology and manufacturing readiness levels (TRL, MRL)
5. Projected cost, schedule and quantity
6. Joint integration: force design impacts, interoperability, inter-Service dependencies, DOTmLPF-P impacts
7. Service-owned performance attribute certifications identified

The board approves, rejects or returns the package for rework.

- **Approve:** recorded as the Service validation record; DAS starts the MDD package run (Step 6).
- **Reject:** the flow stops; the decision and rationale are recorded.
- **Return for rework:** the sponsor revises and resubmits as a new DAS run; the returned run and its decision stay on record.

---

**Step 5: Joint Capability Integration review (parallel, non-blocking)**

**Owner:** JROC, JCB or FCB by Joint Staffing Designator  
**System:** K9X HIL (Requirements (JFRP) / JCI Review)  
**Sources:** S3 Encl. A 6.c-d, S3 Encl. B 2.b  

1. The Joint Requirements Coordinator (J-8) sets the Joint Staffing Designator from the sponsor's recommendation.
2. The Service-validated requirement is submitted with the joint-review minimum content.
3. The review body issues a JROCM: endorse (all, some or none) or reject; tripwires; critical joint capability requirements; recommendations to Service boards and the RRAB.

**Control point:** The JCI review never blocks the MDD or Milestone A. Its result is evidence for Milestone A when available.

---

**Step 6: Materiel Development Decision (gate)**

**Owner:** Milestone Decision Authority  
**System:** DAS (MDD package run), K9X HIL (Major Capability Acquisition / Materiel Development Decision)  
**Sources:** S5 3.5, S5 2.3.b  

DAS prepares the package; entry criteria:

1. Validated requirement document (an ICD or equivalent; under the JFRP, the Service-validated requirement)
2. AoA study guidance
3. AoA study plan

The MDA decides. **Decision record:** Acquisition Decision Memorandum, stating the phase of entry and initial review milestone, with the AoA study guidance and plan attached. Approval starts the MSA run.

---

**Step 7: Materiel Solution Analysis**

**Owner:** DAS MSA orchestrator (prepares); program office (owns content)  
**System:** DAS  
**Sources:** S5 3.6, S5 3.7.a(1), S6 3.1, S4 4.1  

1. Summarise the Analysis of Alternatives and the affordability analysis.
2. Conduct early systems engineering, including an Alternative Systems Review (best practice) yielding a draft performance specification.
3. Draft the CDD-equivalent.
4. Propose an acquisition strategy matched to a pathway.
5. Assemble the Milestone A package and send it to K9X HIL.

---

**Step 8: Milestone A (gate)**

**Owner:** Milestone Decision Authority (Service Chief concurrence for MDAPs)  
**System:** K9X HIL (Major Capability Acquisition / Milestone A)  
**Sources:** S5 3.6-3.7, S4 4.1, S6 3.1  

Entry criteria:

1. Justification for, and affordability and feasibility of, the preferred military solution
2. Technologies that must be matured in TMRR
3. Capability requirement trade space and its priorities
4. Technical, cost and schedule risks with funded mitigation plans
5. Acquisition strategy matched to a pathway, including IP, program protection and exportability
6. Cybersecurity addressed early in program planning
7. Test strategy
8. Life-cycle mission data plan and projected threat
9. Should Cost targets and framing assumptions
10. Affordability analysis: program fully funded within the FYDP
11. Draft CDD-equivalent approved by the Component
12. For MDAPs (ACAT I) only: independent cost estimate, independent technical risk assessment, program goals, 10 U.S.C. 4251 (formerly 2366a) technology determination

**Evidence:** Alternative Systems Review results; JCI JROCM, tripwires and critical joint requirements, when available.

**Decision record:** Acquisition Decision Memorandum: materiel solution, acquisition strategy, TMRR strategy, final RFP release, TMRR exit and EMD entry criteria. Approval starts the TMRR run.

---

**Step 9: System Requirements Review (gate)**

**Owner:** Technical review chair  
**System:** DAS (TMRR run), K9X HIL (Major Capability Acquisition / System Requirements Review)  
**Gate type:** Review / approve (technical review)  
**Sources:** S6 3.2, S5 3.8  

Entry criteria:

1. System requirements consistent with the preferred materiel solution and its support concept
2. Consistent with technology maturation plans
3. Maturity of interdependent systems considered
4. Requirements clearly stated, measurable and testable
5. Requirements traceable to the requirement document; prior reviews complete and their actions closed

**Decision record:** review minutes and action items. Baselined SE requirements carry a baseline revision in the traceability graph. The flow built in this version ends here.

---

## 6. Controls

| Control ID | Control Description | Frequency | Owner | Evidence |
|---|---|---|---|---|
| DAS-CTL-001 | Every source document normalised and every section screened before drafting | Per document | DAS | Document Screening Report |
| DAS-CTL-002 | Human decision at every gate; agents prepare only and cannot make or impersonate a decision | Per gate | Decision authority | Gate decision record in K9X HIL (decider, action, rationale, evidence reference, timestamp) |
| DAS-CTL-003 | Readiness scored in code from per-criterion verdicts, never by the language model | Per gate | DAS | Readiness score and per-criterion verdicts |
| DAS-CTL-004 | Gate decisions are immutable once recorded | Per gate | DAS | Decision record |
| DAS-CTL-005 | Each run keeps the process model version it ran under | Per job | DAS | Job record (process model id) |
| DAS-CTL-006 | Requirements traceable from capability gap to SE requirement, test case and baseline | Per SRR | Technical review chair | Traceability graph |

---

## 7. Exceptions

| Exception Type | Cause | Action Required | Owner |
|---|---|---|---|
| Returned for rework | Decision authority returns a package | Sponsor revises and resubmits as a new run; the returned run stays on record | Capability Sponsor |
| Rejected at a gate | Decision authority rejects | Flow stops; decision and rationale recorded | Decision authority |
| JCI review rejects | Joint review body rejects | Recorded in the JROCM; the acquisition flow is not stopped by this decision | JROC / JCB / FCB |
| Job error | A stage raises an error (for example a failed model or tool call) | The error propagates and is recorded, never reported as a success; the queue slot is freed; the job can be resubmitted | DAS administrator |
| Job withdrawn | The submitting visitor or the DAS administrator withdraws a queued or running job | Withdrawal and requester recorded; a complete job cannot be withdrawn | DAS administrator |
| Queue full | Queue at its maximum, or the visitor already has two jobs queued or running | Submission refused with a message; resubmit when a job finishes | Capability Sponsor |

---

## 8. Key Performance Indicators

Targets are left to the Service and the decision authorities; policy does not fix them. DAS records the timestamps needed to measure each one.

| KPI | Measurement |
|---|---|
| Time from submission to Service Requirements Validation decision | DAS job and K9X HIL decision timestamps |
| Time from validation to MDD, and from MDD to Milestone A | K9X HIL decision timestamps |
| Readiness score at first submission, per gate | DAS readiness record |
| Rework rate per gate | Count of return-for-rework decisions over decisions |
| Screening warnings per document | Document Screening Report |
| Requirements traceable to a capability gap at SRR | Traceability graph |

---

## 9. Escalation

Escalation thresholds are Service-defined. The process model does not set business-day limits.

| Level | Trigger | Escalation To | Action |
|---|---|---|---|
| Level 1 | Package returned for rework, or a gate task waiting for a decision longer than the Service's review window | Capability Sponsor / gate owner | Resolve comments; confirm the decider is available |
| Level 2 | Repeated return for rework, or a JCI tripwire or critical joint requirement affecting the preferred solution | Service requirements board / Milestone Decision Authority | Direct resolution before the next gate |
| Level 3 | MDAP decision requiring Service Chief concurrence, or a rejection at MDD or Milestone A | Milestone Decision Authority / Service Chief | Decision on program continuation |

---

## Appendices

**A. Gate summary**

| Gate | Decides | Blocking | Prepared by run | Approval starts |
|---|---|---|---|---|
| Service Requirements Validation | Service requirements board | Yes | requirement | MDD package |
| JCI Review | JROC, JCB or FCB | No (parallel) | requirement | (records decision only) |
| Materiel Development Decision | Milestone Decision Authority | Yes | MDD package | MSA |
| Milestone A | Milestone Decision Authority | Yes | MSA | TMRR |
| System Requirements Review | Technical review chair | Yes | TMRR | (flow ends) |

**B. Related schema**

The entities, states and transitions in this SOP match the DAS schema loaded in Context Studio (`01_context_studio/schema.jsonld`): CapabilityRequirement, JCIReview, AcquisitionProgram, GateReview, SERequirement and DASJob.
