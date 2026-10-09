# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""The package documents of the process model (mca-2026-10), one agent each.

What each writes (headings, inputs, sources) is in its YAML under agents/yaml/.
"""

from __future__ import annotations

from k9_dow.agents.src.section_writer import SectionWriterAgent


class JsdRecommenderAgent(SectionWriterAgent):
    """Requirement run: proposed Joint Staffing Designator for the JCI review (CJCSM 5123.01A Encl. B 2.b)."""
    layer = "DAS JSD Recommender"
    document_title = "Joint Staffing Designator Recommendation"


class AoaStudyPlanAgent(SectionWriterAgent):
    """MDD package: draft AoA study guidance and study plan (DoDI 5000.85 3.5)."""
    layer = "DAS AoA Study Plan Writer"
    document_title = "Draft AoA Study Guidance and Study Plan"


class AoaSummaryAgent(SectionWriterAgent):
    """MSA: analysis-of-alternatives summary and affordability (DoDI 5000.85 3.6)."""
    layer = "DAS AoA Summary Writer"
    document_title = "Analysis of Alternatives Summary"


class AlternativeSystemsReviewAgent(SectionWriterAgent):
    """MSA: Alternative Systems Review (SE Guidebook 3.1, a best-practice review)."""
    layer = "DAS Alternative Systems Review Writer"
    document_title = "Alternative Systems Review"


class AcquisitionStrategyAgent(SectionWriterAgent):
    """MSA: proposed acquisition strategy matched to a pathway (DoWI 5000.02 4.1; approved at Milestone A)."""
    layer = "DAS Acquisition Strategy Writer"
    document_title = "Proposed Acquisition Strategy"


class SystemRequirementsAgent(SectionWriterAgent):
    """TMRR: system requirements for the System Requirements Review (SE Guidebook 3.2)."""
    layer = "DAS System Requirements Writer"
    document_title = "System Requirements for the SRR"
