# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""Phase and milestone facts (DoDI 5000.85 3.5-3.10) every DAS agent that drafts or judges a package
gets in its prompt. Found necessary on the real model: without them it called Milestone A the start
of EMD and spoke of "the Milestone A (MSA) phase" (a decision is not a phase)."""

PROCESS_FACTS = (
    "Process facts (Major Capability Acquisition, DoDI 5000.85):\n"
    "- Materiel Development Decision (MDD): the mandatory entry point. The MDA decides the phase of entry\n"
    "  (normally Materiel Solution Analysis, MSA) and the initial review milestone (normally Milestone A),\n"
    "  documented in an ADM with the approved AoA study guidance and study plan attached.\n"
    "- MSA: the AoA is conducted; the lead Service or Component, with the requirements and acquisition\n"
    "  communities, selects the preferred materiel solution (SE Guidebook 3.1); MSA ends at Milestone A.\n"
    "- Milestone A: approves entry into Technology Maturation and Risk Reduction (TMRR), the acquisition\n"
    "  strategy (including its pathway) and release of the final RFP for TMRR.\n"
    "- TMRR: critical technologies are matured and risk reduced here (competitive prototyping where\n"
    "  planned), with the System Requirements Review, CDD-equivalent validation and PDR. A strategy\n"
    "  approved at Milestone A plans and contracts for TMRR.\n"
    "- Development RFP Release decision point (end of TMRR, before Milestone B): approves release of the\n"
    "  solicitation for EMD. The EMD contract is awarded after Milestone B.\n"
    "- Milestone B: approves entry into Engineering and Manufacturing Development (EMD).\n"
    "  Milestone C: Production and Deployment. Never attribute EMD to Milestone A.\n"
    "- A milestone is a decision point, not a phase: say \"MSA phase\", \"at Milestone A\".\n"
)
