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
| S2 | CJCSI 5123.01J, Charter of the JROC and the Joint Force Requirements Process, 15 Jan 2026 | — | PENDING |
| S3 | CJCSM 5123.01, Manual for the JROC and the JFRP, 15 Jan 2026 | — | PENDING |
| S4 | DoDI 5000.02, Operation of the Adaptive Acquisition Framework, Change 2, 8 Apr 2026 | — | PENDING |
| S5 | DoDI 5000.85, Major Capability Acquisition | — | PENDING |
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

## Open questions, to be answered from S2-S5 (do not assume)
- What does the **Joint Force Requirements Process** (S2/S3) call the requirement documents now?
  Is the ICD or CDD retained, renamed or replaced?
- The exact validation authorities and designators in the JFRP.
- **DoDI 5000.02 Change 2** (S4): are pathways, decision points and the Milestone Decision
  Authority unchanged? How do Portfolio Acquisition Executives (S7) appear in it?
- **DoDI 5000.85** (S5): current MDD, MSA, Milestone A, TMRR and Milestone B content and the
  required technical reviews.
