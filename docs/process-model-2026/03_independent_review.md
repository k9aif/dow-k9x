# Independent review of the DAS process design (as of 2026-10-09)

Scope: `01_sources_and_findings.md` and `02_process_design.md`, checked against the primary PDFs in `data/` (extracted with pdftotext; page labels are the documents' own, e.g. "A-10").
Abbreviations: CJCSM = CJCSM 5123.01A (5 Aug 2026); CJCSI = CJCSI 5123.01J CH 1; MEMO = 20 Aug 2025 memo (signed by the Deputy Secretary, Feinberg); 5000.85 = DoDI 5000.85 Ch 1; 5000.02 = DoWI 5000.02 Ch 2; SEG = SE Guidebook Feb 2022.

## 1. Verdict

The design is a sound and mostly accurate skeleton for a demonstration. The macro sequence is correct: Service requirement, Service validation, JCI review, MDD, MSA (AoA, ASR), Milestone A, then SRR in TMRR. The attribution of authority is also correct: the Service validates, the JROC or a subordinate board endorses and does not validate, the MDA decides at MDD and Milestone A, and a technical review chair holds the SRR. Most quotations in file 01 are verbatim and at the cited location. It should not be called "accurate" until the errors in section 2 are fixed. Five are material:

- (a) JCI is modeled as a serial step before MDD. The manual says it runs in parallel with acquisition.
- (b) The JCR statement format and the JFR document format, which govern joint documents, are applied to Service documents and used as a gate criterion.
- (c) The JFRP "minimum content" list for the JCI submission is used as the Service validation entry criterion.
- (d) The ASR is made a Milestone A entry criterion although the SE Guidebook marks it a "best practice" review.
- (e) A few notes-file claims about terminology and the manual's contents are wrong. These are "ICD does not appear in the manual", "CJCSM names PAEs", and the "KOP replaced by JOP" rename.

The Milestone A criteria are also missing several items that a DoD requirements officer or systems engineer would expect (section 3).

Counts: **14 errors (must fix)**, **14 omissions / should-consider**, **26 claims verified correct**.

## 2. Errors (must fix)

**E1. JCI is not a serial pre-MDD step.** Design section 1 puts "Joint review (JCI)" at step 3, before the MDD, and section 2 says "A job proceeds when the JROCM is recorded".
- CJCSM Encl. E para 1.d (E-1/E-2): "JCI will occur after Service/component requirements validation and in parallel with Service acquisition processes to prevent unnecessary time delays to capability development and delivery."
- CJCSM Encl. A Table 1 (A-10): "JROC only reviews Service/component documentation post-Service/component approval."
- The MDD in 5000.85 3.5.a is informed by "a validated requirements document", which is the Service-validated one. It does not depend on a JROCM.
- Fix: model JCI as a parallel track that starts after Service validation. The MDD depends only on Service validation. The JROCM (tripwires, critical JCRs) is a later input to trade-space decisions and to the RRAB. It is not a precondition for the MDD, MSA or Milestone A.
- "Non-blocking" is correct. "Proceeds when the JROCM is recorded" is not.

**E2. The JCR statement format and the JFR document format do not apply to Service documents.** Design section 2 (`JOINT-REVIEW` entry: "JCRs in the official format (S3 C 3.f(2))") and section 4 ("output is a Service capability requirement document with JFRP minimum content and JCR statements").
- CJCSM Encl. C para 1 (C-1): "CRDs, JDCRs, and CDRs are considered JFR documents." The section 1-5 format and the "ability to [perform a task…]" JCR statement (C-3 to C-4) are for those joint documents.
- CJCSM Encl. A 6.b (A-10): "Services/components will use Service/component document formats."
- CJCSM Encl. E 1.b: Services "will leverage their own Service-specific requirements documentation—such as the Air Force's Strategic Requirements Document or the Navy's Top-Level Requirements document—determining format and content that meets their needs… If desired, Services may leverage current or previous joint documentation content or formats, but they are not required to do so."
- Fix: drop the JCR format from the `JOINT-REVIEW` entry criteria. The JCR statement format is optional for a Service document. It is mandatory only if DAS later models a CRD or CDR.

**E3. The JFRP "minimum content" is a JCI submission requirement, not Service validation criteria.** Design `SERVICE-VALIDATION` entry criteria cite "JFRP minimum content complete (S3 A 6.b)".
- CJCSM Encl. A 6.a: "all approved Service/component requirements documents will be submitted in KM/DS… for JSD assignment". 6.b: "the JFRP requires Service/components to submit a minimum amount of information for JCI."
- CJCSM Encl. E 1.c: "While Service/component requirements documentation formats will not be prescribed, the JROC will review key elements for the purpose of JCI."
- The Service validation criteria are Service-owned (the Army Requirements Oversight Council, the Marine Requirements Oversight Council, the Air Force and Navy equivalents).
- Fix: label the Service gate's criteria "Service-defined (demo checklist)". Move the A 6.b list to the entry criteria of the JCI submission (the package that follows Service approval).
- Fix: file 01 Step 3 finding 4 and its "What this means" bullet ("DAS can draft it with the JFRP minimum content") are fine as a drafting aid. They must not be presented as the Service validation standard.

**E4. JSD assignment is not "computed from ACAT and joint dependencies".** Design section 2 and section 4 ("the JSD is computed and shown").
- CJCSM Encl. B 2.b(2) (B-3): JSD criteria are (a) significant impact on Joint Force Design, (b) reliance on solutions external to the validating organization, (c) a unique DoW capability, (d) significant resource impact "including proposed ACAT level", and (e) previous JSD designation. ACAT is only one factor.
- JROC/JCB/FCB Interest additionally require "a capability gap of more than one armed force or have capabilities with joint dependencies" plus the ACAT I/II/III-or-equivalent test (B-4, B-5).
- Process (B-5): the sponsor recommends the JSD; the JRC reviews; "J-8/DDRCD will review the JSD and FCB recommendations and make an initial determination"; FCB, JCB and JROC chairs may change it (B-7, B-8).
- The JRC may also decide the program "should be returned to the Service/component without further action required" (B-5).
- Fix: model JSD as sponsor-recommended and J-8 DDRCD-determined, with a demo heuristic. Do not present it as a computed value.

**E5. File 01 S4 finding 2 misattributes "Portfolio Acquisition Executives" to CJCSM 5123.01A.** The text says CJCSM "names Portfolio Acquisition Executives".
- grep of the CJCSM finds no "Portfolio Acquisition Executive", "PAE" or "PEO".
- The term is in CJCSI Encl. A 2.d(5), as an ad hoc JROC advisor ("(5) Portfolio Acquisition Executives."). S2 finding 8 cites this correctly.
- WAS is not CJCSM-only. It also appears in CJCSI Encl. B (the OSW principal advisors paragraph): "integrated into the Warfighting Acquisition System and PPBE".
- The claim that this "confirms the Nov 2025 PEO-to-PAE change appears in policy" rests on one advisor-list entry. S7, the Nov 2025 memo, is PENDING and unread, so the PEO-to-PAE rename is not verified against a primary source. Say so.

**E6. File 01 S3 finding 1 is wrong: "'Initial Capabilities Document' does not appear in the manual."** Neither exact wording does, but the manual uses both terms with "or equivalent":
- CJCSM Encl. A 12.b (A-35): the CDR is meant "to bypass writing an Initial Capability Document (or equivalent) and to link their Capability Development Document (or equivalent) to the CDR."
- Fix: replace the sentence with "the JFRP defines no joint ICD or CDD; the manual refers to Service ICD/CDD 'or equivalent' documents". The correction supports the "or equivalent" reading (section 6 below). It also means the manual itself uses ICD/CDD vocabulary for downstream Service documents.

**E7. The "KOP became JOP" statement (file 01 Step 2 finding 3) is oversimplified.**
- CJCSI para 1.a and the CJCSM use "Joint Operational Problems (JOPs)" as the JROC's ranked unit.
- But the CJCSM keeps KOPs as upstream inputs. Encl. A 1.b(6): "the responsibility of the JROC to ensure JOPs are aligned to National Defense Strategy (NDS)-directed Key Operational Problems (KOPs)". Encl. A 1.c: "top JOPs based on strategic guidance, including NDS KOPs, JWC KOPs, CCMD IPLs…". JFD step (1): "the NDS and its supporting KOPs".
- Fix: say "JOPs are the JROC-ranked unit and KOPs are NDS/JWC inputs; the Aug 2025 memo's 'ranked KOP' list is now a ranked JOP list". Do not call it a rename.
- The CJCSM glossary defines JOP by citing 10 U.S.C. 181(b).

**E8. The ASR is not a Milestone A entry criterion.** Design `MILESTONE-A` entry criteria: "ASR complete with a draft performance spec". Design section 1 lists the ASR as a standard step in MSA.
- SEG Fig. 3-1 (p. 53): ASR drawn with a dashed outline, legend "Best practice technical reviews and audits". SRR, SFR and PDR are "Mandatory technical reviews".
- SEG sec. 3.1 (p. 60): "This is a best practice review."
- SEG p. 58: ASR "occurs in the Materiel Solution Analysis phase before a development contract is awarded".
- Nothing in 5000.85 3.6-3.7 requires an ASR. The Milestone A inputs are the AoA, the draft CDD, affordability and so on.
- The SEG ASR timing text is JCIDS-era: "after a preferred materiel solution is selected… but before the FCB review". It is stale for 2026.
- Fix: "ASR (best practice; tailored in the SEP) and a draft performance specification, if the program holds one". The placement in MSA is correct. File 01's own wording, "It informs Milestone A", is fine. The design's promotion to a gate criterion is not.

**E9. The SRR gate is slightly misdescribed.** Design `SE-REVIEW-SRR`: "Chief engineer / PM"; criteria "S6 3.2, Table 3-2: requirements consistent with the preferred solution and technology plans, measurable and testable, traceable".
- Decider. SEG pp. 54-55: "For each technical review, a technical review chair is identified… The Service chooses the technical review chair, who could be the PM, Systems Engineer, or other subject matter expert". The chair "determines when the review is complete" (p. 60, in the ASR text; same role). The Chief Engineer tailors the criteria (p. 62). The PM approves, funds and staffs it.
- Criteria. "consistent with the preferred materiel solution", "consistent with technology maturation plans" and "measurable and testable" are from the sec. 3.2 body (p. 61). They are not in Table 3-2 (p. 63), which says "verifiable" and "Requirements can be met given the plans for technology maturation". Cite "3.2 and Table 3-2".
- Timing nuance. File 01 says the SRR "follows Milestone A". That is right for the mandatory developer SRR (Fig. 3-1; p. 61: "If the program's AS includes competing contractual efforts during the TMRR phase, an SRR should be held with each participating developer"). But p. 61 also says "The program office should perform an SRR to assess readiness and risks of the technical content of the draft RFP(s) before RFP release". The final TMRR RFP is released at Milestone A (5000.85 3.7.c). So a government-side pre-RFP SRR can precede Milestone A. State "the contractor-facing SRR is in TMRR" rather than an absolute rule.
- The SRR is mandatory as "SRR or SFR" under DoDI 5000.88 3.5.a (SEG p. 61). DoDI 5000.88 is not in the source set, so it is second-hand.

**E10. Pathway selection is attributed to the MDD without support.** Design step 4: "MDD (pathway + phase of entry…) S4 4.1, S5 3.5.c".
- 5000.85 3.5.c: "The MDA will determine the acquisition phase of entry and the initial review milestone." It says nothing about choosing a pathway.
- 5000.85 3.5.a: "The MDD is the mandatory entry point into the major capability acquisition process". The MDD is MCA-specific.
- 5000.02 4.1: "PMs will develop an acquisition strategy for MDA approval that matches the acquisition pathway". That is a PM strategy approved by the MDA, not an MDD output.
- 5000.85 3.2.b adds that the PM "tailor-in" information is recommended "at the MDD or program inception".
- Fix: show pathway selection as an MDA-approved acquisition-strategy decision recorded in an ADM, taken before or at the MDD for an MCA program. Allow the MDD's phase of entry to be later than MSA. Entry at Milestone B or C is possible; the design assumes MSA.

**E11. The interim joint-validation rule is presented as current (file 01 Step 1 finding 6 and its "What this already means" bullet).** MEMO Att. 4 ("Interim Joint Requirements Guidance") says a document qualifies as a "joint performance requirement" only "upon receipt of a signed VCJCS memorandum", adjudicated "within 15 days".
- The Jan 2026 CJCSI and Aug 2026 CJCSM do not carry this. grep for "joint performance requirement" finds no hits in either. The standing process is the JCI initial review, with the 55-business-day nominal timeline (CJCSM Table 1, A-10; Encl. B staffing 5 + 30 + 10 + 10).
- Fix: mark the VCJCS-memo/15-day mechanism as "interim, Aug 2025, superseded in practice by the JFRP/JCI". Keep it only as history.
- The statutory-validation point (10 U.S.C. 181) stands as background (CJCSI para 1: "implements the JROC as a statutory council"). See section 3, item 3.

**E12. The JROCM outcome omits "reject".** Design `JOINT-REVIEW` decision record: "endorse all / some / none".
- CJCSM Encl. A 6.c(1) says "Endorse all, some, or none". Encl. B 2.c(1)(b)6.a, 2.c(1)(c)4.a and 2.c(1)(d)4.a (B-7 to B-9) say "For Service/component requirements, endorse or reject the capability as addressing a JFR/JCR."
- Fix: add "reject" as a recorded outcome. Keep the process non-blocking. The Service retains approval authority; the JROCM recommends, directs analysis, and sets tripwires.

**E13. "Superseded" overstates the 5000.85 precedence claim (file 01 Step 5 heading and design assumptions).** See section 6. The documents do not formally supersede 5000.85. The accurate wording is "terminology overtaken, read through 'or equivalent'".
- File 01's statement that 5000.85 "has not been reissued" is not verifiable from the provided PDFs. The copy in `data/policy/` is Ch 1 of Nov 2021 and the file itself still names JCIDS. Record a retrieval date, and say it was checked against the DoD issuances site if that is true.

**E14. Design section 5 cites the wrong authority for accepting legacy-format inputs.** It says "S2 Encl. A 7 explicitly allows" ICD/CDD-style demo documents.
- CJCSI para 7 (Applicability of Previous JCIDS Documents) covers documents "previously validated by the JROC through the former JCIDS process", which "remain valid".
- Demo inputs are new, unvalidated Service documents. The correct basis is CJCSM Encl. A 6.b ("Services/components will use Service/component document formats") and Encl. E 1.b ("Services may leverage current or previous joint documentation content or formats").
- The CJCSM Encl. A 7 numbering ("USSOCOM (SOFCIDS)", file 01 Step 3 finding 7) is correct. The two "Encl. A 7" references are different documents.

## 3. Omissions / should-consider

1. **Service Chief concurrence for MDAPs.** 5000.85 2.3.b: the Service Chief concurs "with the need for a materiel solution as identified in the MDD review prior to entry into the MSA phase" and "with the cost, schedule, technical feasibility, and performance trade-offs… before Milestone A approval is granted pursuant to Section 2366a". 2.3.c: Service Chiefs "will advise the MDA on trade-offs before Milestones A and B". Add as a role and evidence at the MDD and `MILESTONE-A`.
2. **MDAP goals (GEM) before Milestone A.** 5000.85 3C.3.c(1): after the AoA out-brief, the Joint Staff, USW(A&S), USW(R&E) and DCAPE analyse the options matrix, and the MDA co-chairs a goal establishment meeting within 30 days. The MDA must approve cost, schedule and performance goals "before funds are obligated for technology development". This is a real Milestone A prerequisite for MDAPs and is missing from the design.
3. **10 U.S.C. 2366a at Milestone A.** 5000.85 3.7.b(3): the MDA must determine "with a high degree of confidence" that technology "will not delay the fielding target", or require separate maturation and an adoption plan. Also 3.7.c: the MDA approves "PM waiver requests".
4. **Performance attribute certifications.** CJCSM Encl. E 2 (E-2 to E-4): "the Services/components are responsible for all performance attribute certifications and endorsements". They cover net-ready/joint interoperability, intelligence supportability and threat approval, sustainment KPP (reliability and maintainability), energy, force protection/survivability (including the Cyber Survivability Endorsement), and exportability. E 2.c: for JSD of FCB Interest or higher the JROC "will review Service/component completion of these certifications". The design's JCI package and gates omit them. They are a standard systems-engineer and requirements-officer check, and they feed Milestone A and the SRR.
5. **Cybersecurity, program protection and IP in the criteria.** 5000.02 4.1.b(3): "cybersecurity… must be addressed early and continuously"; 4.1.b(4) data and license rights; 4.1.b(5) product support and affordability early. 5000.85 3.7.a(2)(e) lists IP, program protection and exportability, and (g) the life-cycle mission data plan. The design's Milestone A row names only "acquisition strategy" and "test strategy". Add the sub-items. Also add the PM-presented "Should Cost" targets and framing assumptions (3.7.b(1)), the CAE's selection of a PM and program office in MSA (3.6.b(2)), and the program office "prior to Milestone A" (3C.2.a).
6. **ICE and ITRA scope.** 5000.85 3.6.b(3): "An independent cost estimate (ICE) and independent technical risk assessment (ITRA) will be conducted before granting Milestone A approval for an MDAP." The design records this correctly for Milestone A. It should add that they repeat before Milestone B (3.8.b) and are MDAP-only. The "affordability" criterion in the design says "fully funded in the FYDP". 5000.85 3.7.b(2) calls for a "quantitatively supported affordability analysis" for MDAPs, with "similar, appropriately-scaled" analyses for other programs.
7. **RRAB and the resourcing path.** The design never mentions the RRAB, although the JROCM forwards recommendations to it (CJCSM Encl. A 6.c(7); Encl. B 2.c(1)(d)3, JROC "nominating topics to the RRAB"). MEMO Att. 1 and CJCSM Encl. E 5: the RRAB can recommend "program starts, realignments, terminations" and the JAR starts with FY2027 (MEMO Att. 3). A single optional "RRAB/JAR resourcing" annotation after the JROCM would make the model honest about how the joint path touches funding.
8. **Tripwires, breaches and comebacks.** CJCSM Encl. A 9 (A-14 to A-17): Nunn-McCurdy, Critical Intelligence Parameter breaches and JROC tripwires bring programs back to the JROC after endorsement. The design says tripwires "carry forward as evidence" but gives no re-entry path. State the re-entry rule even if it is not built.
9. **Capability Portfolio Management and JOP linkage.** CJCSI Encl. D 1.a(4): CPM Reviews assess "commercial-off-the-shelf and other alternatives… trade-space". The CJCSM FCB review criteria (B-6) include "Attributes that are critical to the Joint Force, including addressing JOPs", traceability to prioritized joint gaps, duplication and redundancy, and interoperability. The design could show that the JCI review checks those items, not just the JSD.
10. **SOFCIDS/CCIDS and the CCMD paths.** CJCSM Encl. A 7: USSOCOM and USCYBERCOM retain validation authority, and the JROC keeps awareness through JCI. The CDR path (Encl. A 12): the originating CCDR approves it, and the CDR lets Services "bypass writing an ICD (or equivalent)". The JICR path replaces JUON/JEON (CJCSM para 2.b; CJCSI CH 1). The design's non-goal statement should list these as out of scope.
11. **Pathway preference and experimentation-led acquisition.** MEMO Att. 5, items 2-3: "buy-before-build or experimentation-led approaches". CJCSM Encl. A 1.d: MEIA experimentation and industry engagement against JOPs. 5000.02 4.2.c(2): "Software-intensive components may be acquired via the software acquisition pathway". 5000.85 3.2.c covers MTA-to-MCA transition. The design scopes to MCA, which is fine. Say that the 2026 policy leans toward MTA and Software pathways and commercial solutions, so MCA is the heavyweight option.
12. **MDD decision authority depends on ACAT.** 5000.85 App. 3A: ACAT ID MDA is the DAE (USW(A&S)); ACAT IC is the CAE; ACAT II and III are the CAE or designee. DCAPE presents AoA guidance and approves the plan for MDAPs; for ACAT II and below the Component equivalent does. The design says "MDA" in each case, which is right but should reference the ACAT-driven choice, and the AoA guidance and plan owners.
13. **Later gates.** When the CDD-equivalent validation step is built, note 5000.85 2.1.b (Service Chief written determination "necessary and realistic" before Milestone B, 10 U.S.C. 2448a) and 5000.85 3.8.c ("requirements validation authority will validate the CDD (or equivalent)"). Under the 2026 regime that authority is the Service unless a statutory joint validation applies.
14. **Source hygiene.** The MEMO is signed by the Deputy Secretary of Defense (Feinberg) but is called "SecDef memo" in file names, and 5000.02 1.5.a calls it "the August 20, 2025 Secretary of Defense Memorandum". Use "OSD memo (DepSecDef)". The SE Guidebook is Feb 2022 and still says JCIDS/FCB (pp. 53-55, 58-59, 62). Mark any SEG guidance that cites them as "legacy wording, still the current SE guidance".

## 4. Verified-correct claims (brief)

Each was found in the cited location and means what the author says unless noted in section 2.

1. MEMO p. 1: "commence the disestablishment of JCIDS and direct the JROC to cease validating Component-level requirement documents to the maximum extent permitted by law. Military Service requirements determinations shall be the Military Services' responsibility." Rescission within 120 days. Verbatim.
2. MEMO pp. 1-2: JROC re-oriented as the "single forum for identifying and annually ranking Joint Force Key Operational Problems (KOP)". Verbatim.
3. MEMO p. 2 and Att. 1: the RRAB is co-chaired by the VCJCS and the Deputy Secretary and "shall select topics from the top-ranked KOP… perform analysis, issue programming guidance, and recommend allocation of funding from the Joint Acceleration Reserve (JAR)", with program starts, realignments and terminations by exception. Verbatim.
4. MEMO Att. 2: MEIA under USD(R&E) with USD(A&S) support; "mission engineering activities to refine problem understanding and solution suitability". Verbatim.
5. MEMO Att. 3: JAR from the FY2027 cycle, CAPE-held; "all other elements of the… PPBE system shall continue". Verbatim.
6. MEMO Att. 4: the "signed VCJCS memorandum", "within 15 days with a single round of comment resolution", and "All other validations devolve to the sponsoring Military Service". Verbatim, but interim (E11). The JUON/JEON simplification point is also correct.
7. CJCSI para 1.b: JFRP "replaces the JCIDS in its entirety. In the JFRP, Service- and Component-specific requirement validation is the responsibility of the respective Services and Components. The JFRP does not delineate actions required to satisfy acquisitions rules and regulations." Verbatim.
8. CJCSI para 1.a: "Joint Force Design (JFD), Joint Capability Integration (JCI), and Combatant Command (CCMD) Requirements through a lens of Joint Operational Problems (JOPs) underpinned by its analytic engine, Capability Portfolio Management (CPM)". Verbatim.
9. CJCSI para 7.a-b: previously validated documents "remain valid"; updates "through the solution sponsor's internal validation procedures". Verbatim.
10. CJCSI Encl. A 1.a(6): "(b) Propose nonprescriptive solutions to joint operational problems." Verbatim.
11. CJCSI Encl. A 2.d(5): Portfolio Acquisition Executives are ad hoc JROC advisors. Verified.
12. CJCSI Encl. A para 6.b: KM/DS is "the authoritative system for processing, coordinating, tasking, and archiving all DoW requirements documents". Verbatim.
13. CJCSI CH 1 (p. 1): "replacing all references to the legacy Joint Urgent Operational Need and Joint Emergent Operational Need pathways with the new, unified Joint Immediate Combatant Command Requirement process". CJCSM para 2.b redesignates JUON/JEON as JICR. Verified.
14. CJCSM Encl. A 6.a: "all approved Service/component requirements documents will be submitted in… KM/DS by the requirements sponsor to the Joint Requirements Coordinator (JRC) for Joint Staffing Designator (JSD) assignment". It applies to all Service documents, after Service approval.
15. CJCSM Encl. A 6.b: the minimum-content list (operational context, threat/intelligence, requirements incl. TRLs and MRLs and "Projected cost, schedule, and quantity", joint integration). Correct as listed (but see E3).
16. CJCSM Encl. A 6.c: the JROCM endorses "all, some, or none", identifies "critical Joint Capability Requirements (JCRs) to inform Warfighting Acquisition System (WAS) trade-space decisions", sets tripwires and comebacks, and forwards to Service boards "as well as the RRAB". The JCI review is an endorsement, not a validation, and happens after Service approval (Table 1, A-10).
17. CJCSM Encl. B 2.b(1) and (6): four JSDs "from highest to lowest" (JROC Interest, JCB Interest, FCB Interest, Service Information), set "at the lowest possible level". Service Information applies to "all Service-/component-approved documents that do not meet the criteria for JROC, JCB, or FCB Interest", and "no additional action will be taken as part of an initial review" (B-6). So "Service Information = no joint review" is correct.
18. CJCSM Encl. B 2.b(3)-(5): JSD thresholds (ACAT I, ACAT II, ACAT III or equivalent; JCB Interest is the minimum for JDCRs and CCMD-sponsored documents except USSOCOM and USCYBERCOM). Correct.
19. CJCSM Encl. C 3.f(2): the JCR statement format ("The ability to [perform a task…]… in accordance with the [Standard of Performance]"). Verbatim, but applies to JFR documents (E2). Encl. C 1-2 lists CRD, JDCR and CDR as the joint documents. Correct. The CDR is "Service, solution, and cost agnostic".
20. CJCSM Encl. A 7: USSOCOM and USCYBERCOM "retain validation authority for specific subsets", JROC keeps awareness through JCI. Verified.
21. 5000.02 Change 2: 1.5 (administrative; JCIDS disestablishment; Oct 10, 2025 memo), 1.1.b and 1.2 ("Defense Acquisition System (DAS)"), 3.2 (PEO), 3.1 (MDA/DA), 4.1 (strategy "for MDA approval", tailoring recorded in an "acquisition decision memorandum"), 4.1.b(7) ("systems engineering technical reviews"), 4.2 (six pathways; Urgent "in less than 2 years"; MTA 5 years / 6 months; MCA "military unique programs that provide enduring capability"), 2.2.b(2) ("validated need or capability gap"). Verbatim and correct.
22. 5000.85 3.4 (Figure 2 order: MDD, MSA, Milestone A, TMRR, CDD validation, Development RFP release, Milestone B, EMD, Milestone C, P&D, O&S). ADM documents decisions.
23. 5000.85 3.5 (MDD): "mandatory entry point", "informed by a validated requirements document (e.g., an initial capabilities document (ICD) or equivalent)", AoA study guidance and plan, DCAPE or Component equivalent presents guidance, MDA determines "acquisition phase of entry and the initial review milestone", ADM with the guidance and plan attached.
24. 5000.85 3.6-3.7 (MSA purpose; AoA; ICE and ITRA before Milestone A for MDAPs; Milestone A approves TMRR entry, the acquisition strategy and the final RFP; "A draft capability development document (CDD) approved by the DoD Component informs the acquisition strategy and the RFP for TMRR"; the principal considerations list; the affordability analysis "fully funded within the Future Years Defense Program (FYDP)"; the decisions list). Correct, with the omissions in section 3.
25. SEG 3.1 (p. 58): the ASR "leads to a draft performance specification for the preferred materiel solution" and is in MSA. SEG Fig. 3-1 puts the ASR at the end of MSA and the SRR and PDR in TMRR with the PDR before Milestone B. SEG 3.2 (p. 61): the SRR "should occur after the selection of the preferred solution and after sufficient analysis has occurred to develop a draft performance specification", with a developer SRR for competing efforts in TMRR. 5000.85 3.8.b(2): the PDR is before Milestone B "unless waived by the MDA".
26. File 01 terminology notes that hold: 5000.02 Ch 2 uses "Defense Acquisition System" and "Program Executive Officer"; CJCSM/CJCSI use "Warfighting Acquisition System (WAS)"; JICR replaces JUON/JEON (Aug 2026); JOPs are the JROC's ranked unit. The corrections are in E5-E7.

## 5. Direct answers to the specific checks

**Check 2 (flow order and attribution).**
- The sequence is correct, except that JCI is parallel to, not before, the MDD (E1).
- The JCI "initial review" is after Service approval (CJCSM Encl. A 6.a; Table 1 "post-Service/component approval") and is an endorsement, not a validation (6.c, B 2.c(1)(b)6.a).
- It applies to all approved Service requirement documents, but only JSDs of FCB Interest or higher get a staffed review. "Service Information" documents are archived in KM/DS with no further action (B-6). The JRC may also return a document with no joint equities (B-5).
- The MDD, the ASR in MSA before Milestone A, and the SRR in TMRR after Milestone A are correct (E8, E9, E10 for the caveats).
- "Draft CDD approved by the DoD Component informs Milestone A" is verbatim from 5000.85 3.7.a(1). The design's "CDD-equivalent" is consistent with the "or equivalent" wording.

**Check 3 (gate criteria).** Accurate where drawn from 5000.85 3.5 to 3.7, apart from E2 and E3. Missing items are in section 3.

**Check 4 (terminology).**
- DAS and PEO (5000.02) versus WAS (CJCSM and CJCSI): correct.
- PAE is in CJCSI Encl. A 2.d(5) only, not in the CJCSM (E5).
- KOP is NDS/JWC upstream input and JOP is the ranked unit (E7).
- JICR replaces JUON/JEON: correct.

## 6. Precedence claim: is "the 2021 DoDI 5000.85 ICD/CDD wording is superseded for requirements terminology" a fair reading?

It is a fair interpretive reading but not a formal supersession.

1. Neither the CJCSI nor the CJCSM supersedes or amends 5000.85. CJCSI para 1.b says the JFRP "does not delineate actions required to satisfy acquisitions rules and regulations. Services and Components must ensure their programs meet and satisfy the statutory and regulatory requirements". The acquisition rules therefore stay in 5000.02 and 5000.85. The MEMO directed USD(A&S) to remove JCIDS references "in DoDD 5000-series directives… and associated instructions and manuals as necessary". Only 5000.02 Change 2 (1.5.a) is shown to have done so. The 5000.85 file here is Ch 1, Nov 2021, and still cites JCIDS (3C.? international cooperative programs: "the Chairman of the Joint Chiefs of Staff Manual for the Operation of the Joint Capabilities Integration and Development System (JCIDS)") and still contains the JCIDS-era glossary entry.
2. The 5000.85 wording is built to absorb the change. Quotes:
   - 3.5.a: "informed by a validated requirements document (e.g., an initial capabilities document (ICD) or equivalent)".
   - 3.8.c: "the requirements validation authority will validate the CDD (or equivalent requirements document) for the program".
   - 3.7.a(1): "A draft capability development document (CDD) approved by the DoD Component informs…".
   - 3.8.a: "the TMRR phase is guided by the draft CDD".
   - 3.2.a: "validated capability requirements".
3. The 2026 documents use the same "or equivalent" language downstream. CJCSM Encl. A 12.b: "bypass writing an Initial Capability Document (or equivalent) and to link their Capability Development Document (or equivalent) to the CDR". 5000.02 2.2.b(2) refers to "the validated need or capability gap". CJCSM Encl. A 6.a defines the Service-approved document that gets the JSD.
4. Recommended wording: "5000.85 remains in force. Its ICD and CDD are read as 'or equivalent' Service requirement documents, and its 'requirements validation authority' is the Service (CJCSI 1.b), except where law requires joint validation." Drop "superseded". Add: "as of the retrieval date, no reissue of 5000.85 was found", with the date, only if that check is made.
