# SPDX-License-Identifier: Apache-2.0

"""Markdown report builder — assembles stage outputs into final reports."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from k9_dow.contracts.stage_results import JobResult, StageResult


class MarkdownReportBuilder:
    """Builds final architecture report from accumulated stage results."""

    def build_final_report(self, job_result: JobResult) -> str:
        sections = [
            f"# Architecture Analysis Report",
            f"",
            f"**Job ID:** {job_result.job_id}  ",
            f"**Classification:** {job_result.classification}  ",
            f"**Route:** {job_result.route}  ",
            f"**Status:** {job_result.status}  ",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            f"",
            "---",
            "",
        ]

        for stage in job_result.stage_results:
            sections.append(f"## {stage.stage_name}")
            sections.append(f"**Stage ID:** {stage.stage_id}  ")
            sections.append(f"**Status:** {stage.status}  ")
            sections.append(f"**Governance:** {stage.governance.status}")
            sections.append("")

            if stage.markdown_report:
                sections.append(stage.markdown_report)
            else:
                sections.append("_No output generated for this stage._")
            sections.append("")
            sections.append("---")
            sections.append("")

        return "\n".join(sections)

    def build_governance_signoff(self, job_result: JobResult) -> str:
        sections = [
            "# Governance Sign-off",
            "",
            f"**Job ID:** {job_result.job_id}  ",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Stage Governance Summary",
            "",
            "| Stage | Status | Governance | Findings |",
            "|---|---|---|---|",
        ]

        for stage in job_result.stage_results:
            finding_count = len(stage.governance.findings)
            sections.append(
                f"| {stage.stage_name} | {stage.status} | "
                f"{stage.governance.status} | {finding_count} |"
            )

        sections.append("")

        has_blockers = any(s.governance.status == "block" for s in job_result.stage_results)
        has_warnings = any(s.governance.status == "warn" for s in job_result.stage_results)

        if has_blockers:
            sections.append("**Overall Decision:** BLOCKED — governance blockers must be resolved.")
        elif has_warnings:
            sections.append("**Overall Decision:** CONDITIONAL PASS — review governance warnings.")
        else:
            sections.append("**Overall Decision:** PASS — all governance checks cleared.")

        return "\n".join(sections)
