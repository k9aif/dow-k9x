# DAS process model, current as of October 2026: sources and verified findings

Goal: DAS models the U.S. defense requirements-to-acquisition flow **as it stands today**,
traced to primary sources. Because the process keeps changing (JCIDS ended in 2025-26), the
model will live in a versioned configuration file stamped with an "as of" date and its sources,
so the next reform is an edit, not a rewrite.

Status of each source: **VERIFIED** = read in the primary document (file in `data/policy/`);
**PENDING** = primary document not yet obtained (government sites block scripted downloads;
Ravi downloads them in a browser).

| # | Source | File | Status |
|---|---|---|---|
| S1 | SecDef/DepSecDef memo, "Reforming the Joint Requirements Process to Accelerate Fielding of Warfighting Capabilities", 20 Aug 2025 (9 pp) | `data/policy/SecDef_Memo_2025-08-20_requirements.pdf` | VERIFIED |
| S2 | CJCSI 5123.01J, Charter of the JROC and the Joint Force Requirements Process, 15 Jan 2026, **CH 1, 5 Aug 2026** | `data/policy/CJCSI 5123.01J CH 1.pdf` | VERIFIED |
| S3 | **CJCSM 5123.01A**, Manual for the JROC and the JFRP, **5 Aug 2026** (112 pp; supersedes the Jan 2026 CJCSM 5123.01) | `data/policy/CJCSM 5123.01A.pdf` | VERIFIED (Encl. A 6, B 2.b, C) |
| S4 | DoWI 5000.02, Operation of the Adaptive Acquisition Framework, 23 Jan 2020, Change 2, 8 Apr 2026 | `data/policy/500002p.pdf` | obtained |
| S5 | DoDI 5000.85, Major Capability Acquisition, 6 Aug 2020, Change 1, 4 Nov 2021 (not reissued since) | `data/policy/500085p.pdf` | obtained |
| S8 | Joint Staff briefing "Implementation of CJCSI 5123.01J & CJCSM 5123.01" (14 pp, Aug 2026) | `data/policy/JFRP_overview_mhsrs.pdf` | obtained (cross-check only) |
| S6 | DoD Systems Engineering Guidebook, Feb 2022 | `data/SE-Guidebook-Feb2022.pdf` | VERIFIED (sections 3.1, 3.2) |
| S7 | "Transforming the Warfighting Acquisition System" memo, 7 Nov 2025 | — | PENDING (secondary reports only) |

## Step 1 findings: S1, the 20 Aug 2025 memo (verified)

1. **JCIDS ends.** The VCJCS will "effective immediately, commence the disestablishment of JCIDS
   and direct the JROC to cease validating Component-level requirement documents to the
   maximum extent permitted by law. Military Service requirements determinations shall be the
   Military Services' responsibility." JCIDS instructions and manuals are to be rescinded within
   120 days. (p. 1)
2. **The JROC is re-oriented** as "the Department's single forum for identifying and annually
   ranking Joint Force Key Operational Problems (KOP) and associated capability gaps that flow
   from the National Defense Strategy, the Joint Warfighting Concept, Joint Force Design
   activities, and other strategic guidance". (pp. 1-2)
3. **The RRAB** (Requirements and Resourcing Alignment Board, co-chaired by the VCJCS and the
   DepSecDef) "each budget cycle … shall select topics from the top-ranked KOP … perform
   analysis, issue programming guidance, and recommend allocation of funding from the Joint
   Acceleration Reserve (JAR)". It is synchronized with the annual Program and Budget Review.
   It may recommend "program starts, realignments, terminations, other program changes".
   (p. 2; Att. 1)
4. **MEIA** (Mission Engineering and Integration Activity; USD(R&E) with USD(A&S)): for each
   top KOP, conducts "mission engineering activities to refine problem understanding and
   solution suitability", industry engagement and experimentation campaigns, and recommends
   solution components for JAR funding. (p. 2; Att. 2)
5. **JAR** (Joint Acceleration Reserve) is a CAPE-held portion of Fiscal Guidance from the FY2027
   budget cycle. "All other elements of the Planning, Programming, Budgeting, and Execution
   (PPBE) system shall continue." (Att. 3)
6. **Joint validation that remains is only what statute requires** (10 U.S.C. §181). "A capability
   document only qualifies as a 'joint performance requirement' upon receipt of a signed VCJCS
   memorandum citing the appropriate legal basis … All other validations devolve to the
   sponsoring Military Service." Qualifying submissions are adjudicated "within 15 days with a
   single round of comment resolution". (Att. 4)
7. **Combatant Command needs** continue to be received and prioritized by the Joint Staff; the
   urgent and emergent need process (JUON/JEON) is to be simplified. (Att. 4)
8. **The Services review their own requirements processes** to strengthen force design, engage
   industry earlier and increase agility. (Att. 5)

### What this already means for DAS
- "JCIDS" and "JROC validation" as a universal gate are **obsolete** as DAS stage names.
- **Requirements validation** = the **sponsoring Military Service** by default; a **joint performance
  requirement** only by VCJCS memorandum (statutory basis), adjudicated in 15 days.
- Upstream of a program: **KOP ranking (JROC) → RRAB resourcing → MEIA mission engineering**.
  This is the joint, top-down path, distinct from a Service's own requirement.
- PPBE continues; the RRAB and JAR integrate with it.

## Step 2 findings: S2, CJCSI 5123.01J with Change 1 (verified)

1. **The JFRP "replaces the JCIDS in its entirety"**: "In the JFRP, Service- and
   Component-specific requirement validation is the responsibility of the respective Services and
   Components." CJCSI 5123.01I and the JCIDS Manual (30 Oct 2021) are "rescinded in their
   entirety". (para 1.b, para 7)
2. **The JFRP is requirements only**: it "does not delineate actions required to satisfy acquisitions
   rules and regulations. Services and Components must ensure their programs meet and satisfy
   the statutory and regulatory requirements". So acquisition stays under the DoW 5000 series
   (S4, S5). (para 1.b)
3. **The JROC's re-oriented focus**: **Joint Force Design (JFD)**, **Joint Capability Integration (JCI)**
   and **Combatant Command (CCMD) Requirements**, "through a lens of **Joint Operational Problems
   (JOPs)** underpinned by its analytic engine, **Capability Portfolio Management (CPM)**". JOPs are
   prioritized annually. Note the term: the 2025 memo said "Key Operational Problems (KOP)";
   the 2026 instruction uses **"Joint Operational Problems (JOPs)"**. (para 1.a; Encl. D 1.a)
4. **Joint capability requirements the JROC recommends** must "describe the joint operational
   problem", "propose **nonprescriptive** solutions" and ensure interoperability. (Encl. A 1.a(6))
5. **CCMD requirements**: immediate requirements go through the **Joint Immediate Combatant
   Command Requirement (JICR)** process, which (CH 1, Aug 2026) replaces JUON/JEON. Integrated
   Priority Lists are prioritized through the Capability Gap Assessment, plus CCMD Derived
   Requirements. (CH 1 summary; Encl. D 1.a(3))
6. **Capability Portfolio Management Reviews** assess requirements, existing solutions, gaps, risks,
   COTS alternatives and trade space, and make recommendations. (Encl. D 1.a(4))
7. **Legacy JCIDS documents**: previously JROC-validated requirements "remain valid"; updates go
   "through the **solution sponsor's internal validation procedures**". (Encl. A para 7)
8. **Portfolio Acquisition Executives** are named JROC ad hoc advisors (Encl. A 2.d(5)), which
   confirms the Nov 2025 PEO-to-PAE change appears in policy.
9. **KM/DS** is "the authoritative system for processing, coordinating, tasking, and archiving all DoW
   requirements documents". (Encl. A 6.b)

### What this means for DAS
- DAS's **default path is a Service requirement validated by the Service** (the "solution sponsor").
  The joint path applies only when the requirement is a joint capability requirement (JCI or JOP
  driven) or a CCMD requirement.
- The JROC is no longer a gate on a Service program. Its recommendations reach programs through
  JCI and CPM reviews (changes, alternatives, cancellations).
- Requirement document names: **open**, to be read in the manual (S3, CJCSM 5123.01A).

## Step 3 findings: S3, CJCSM 5123.01A, 5 Aug 2026 (verified)

1. **There are no ICDs or CDDs at the joint level any more.** "Initial Capabilities Document" does not
   appear in the manual. The **Joint Force Requirements (JFR) documents** are:
   - **Capstone Requirements Document (CRD)**: top-down, overarching Joint Force needs, captured as
     Joint Capability Requirements (JCRs) and prioritized within a portfolio for CPM analysis;
   - **Joint DOTmLPF-P Change Request (JDCR)**: non-materiel solutions;
   - **Combatant Command Derived Requirement (CDR)**: when a CCDR deems a gap's risk unacceptable.
     Service-, solution- and cost-agnostic. (Encl. C 1-2)
2. **JFR document format**: cover page (incl. proposed JSD and lead FCB), Executive Summary,
   1 Operational Context, 2 Threat Summary, 3 Joint Capability Requirements and Gaps,
   4 Interoperability, 5 Final Recommendations / Implementation Plans. (Encl. C 3)
3. **JCR statement format**: "The ability to [perform a task (UJT or Service Task) Operational
   Activity] against/given a [Threat] in order to achieve [Effect] in a/under [Environmental
   Conditions] in accordance with the [Standard of Performance]." It must not presuppose a
   solution. (Encl. C 3.f(2))
4. **A Service requirement**: "Services/components will use Service/component document formats."
   After **Service approval**, the sponsor submits it in **KM/DS** to the Joint Requirements
   Coordinator for **Joint Staffing Designator (JSD)** assignment and a **JCI initial review**, with a
   minimum content set:
   - operational context (task, CONOPS/CONEMP);
   - threat (SIC/DIA-approved threat assessment, Critical Intelligence Parameters, intelligence
     supportability);
   - requirements (Capability Requirements and/or Performance Attributes, traceability to gaps,
     **TRLs and MRLs**, projected cost, schedule and quantity);
   - joint integration (force design impacts, interoperability, inter-Service dependencies,
     DOTmLPF-P). (Encl. A 6.a-b)
5. **The outcome is an endorsement, not a validation**: the JROC or a subordinate board publishes a
   **JROCM** that endorses "all, some, or none" of the Service document as a JFR; identifies
   critical JCRs "to inform **Warfighting Acquisition System (WAS)** trade-space decisions";
   establishes **tripwires and comebacks**; and forwards recommendations to Service
   requirements/acquisition boards and the **RRAB**. (Encl. A 6.c)
6. **JSDs** (from highest to lowest), set "at the lowest possible level":
   - **JROC Interest**: largest/highest-risk; gaps of more than one armed force or joint
     dependencies, and projected **ACAT I** or interoperating with ACAT I;
   - **JCB Interest**: below the JROC threshold; ACAT II-level; the minimum for JDCRs and
     CCMD-sponsored documents;
   - **FCB Interest**;
   - **Service Information**.
   The JSD sets "the staffing process and final review authority". (Encl. B 2.b)
7. USSOCOM (SOFCIDS) and USCYBERCOM (CCIDS) keep their own validation authority; the JROC keeps
   awareness through JCI. (Encl. A 7)

### What this means for DAS
- The input document is a **Service capability requirement document** (Service format), *not* a
  JCIDS ICD. DAS can draft it with the JFRP **minimum content** (finding 4) and JCR statements in
  the official format (finding 3).
- **Gate 1 = Service requirements validation** (the Service's board; human).
- **Step 2 = Joint review**: JSD assignment from ACAT and joint dependencies, then a JCI initial
  review whose outcome is an endorsement JROCM ("all / some / none"). This is a human review whose
  authority follows from the JSD (JROC, JCB, FCB or Service Information). It is not a blocking
  validation, but its endorsements, tripwires and critical JCRs feed acquisition trade space.
- The term **Warfighting Acquisition System (WAS)** is official (used in the manual).

## Open questions, to be answered from S2-S5 (do not assume)
- What does the **Joint Force Requirements Process** (S2/S3) call the requirement documents now?
  Is the ICD or CDD retained, renamed or replaced?
- The exact validation authorities and designators in the JFRP.
- **DoDI 5000.02 Change 2** (S4): are pathways, decision points and the Milestone Decision
  Authority unchanged? How do Portfolio Acquisition Executives (S7) appear in it?
- **DoDI 5000.85** (S5): current MDD, MSA, Milestone A, TMRR and Milestone B content and the
  required technical reviews.
