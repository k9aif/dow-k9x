# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""RequirementOrchestrator: stages NORMALIZE (input arrives as Markdown) to the requirement
gates of process model mca-2026-10 (config/process_model.yaml).

Screens the submitted Service capability requirement document, builds its architecture views,
judges it against the SERVICE-VALIDATION entry criteria, assembles the review package, and
proposes a Joint Staffing Designator. Publishes two K9X HIL tasks:

- SERVICE-VALIDATION (blocking): the Service requirements board validates; approval starts
  the MDD package run.
- JCI-REVIEW (parallel, never blocking): the joint review by the JROC, JCB or FCB the JSD
  names (CJCSM 5123.01A Encl. A 6.d); its JROCM is recorded and joins the evidence of later
  gates when it comes back.

Replaces the JCIDS-era JcidsOrchestrator (JROC-VALIDATION), retired when JCIDS was.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, Optional

from k9_dow.orchestrators.stage_base import (PACKAGE_AGENTS, READINESS_AGENTS, ProcessStageOrchestrator,
                                             das_url)

log = logging.getLogger(__name__)

GATE = "SERVICE-VALIDATION"
JOINT_GATE = "JCI-REVIEW"


def _screening_line(screening: dict) -> str:
    """One line for the HIL task: the full report is linked in its artifacts."""
    status = screening.get("status") or "not run"
    if status == "warnings":
        return f"{screening.get('warning_count')} warning(s): see the Document Screening Report; record a disposition for each"
    if status == "clean":
        return f"no warnings ({screening.get('sections_screened')} sections)"
    return "incomplete: a check did not run; see the Document Screening Report"


class RequirementOrchestrator(ProcessStageOrchestrator):
    """Service capability requirement → SERVICE-VALIDATION (+ parallel JCI-REVIEW)."""

    layer = "DAS Requirement Orchestrator"
    AGENTS = ("ModelExtractorAgent", "ViewGeneratorAgent", "ViewConsistencyCheckerAgent",
              "JsdRecommenderAgent") + READINESS_AGENTS + PACKAGE_AGENTS

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 progress_callback: Optional[Callable[[dict], None]] = None, **kwargs) -> None:
        super().__init__(config=config, progress_callback=progress_callback, **kwargs)
        # k9x_Shield at stage entry: the submitted document is checked before any agent or
        # model sees it (security.document_screen if present, else security.shield).
        self._shield = None
        sec = self.config.get("security") or {}
        screen = sec.get("document_screen") or sec.get("shield") or {}
        if screen.get("enabled") is True:
            from k9_aif_abb.k9_security.vulnerability.shield_governance import ShieldGovernance
            self._shield = ShieldGovernance({**self.config, "security": {**sec, "shield": screen}})

        # Classification screen at stage entry: DAS is UNCLASSIFIED; marked documents never enter.
        self._classification = None
        cls_cfg = sec.get("classification") or {}
        if cls_cfg.get("enabled") is True:
            from k9_aif_abb.k9_security.vulnerability.vulnerability_chain import VulnerabilityChain
            from k9_dow.security.classification_marking_check import ClassificationMarkingCheck
            self._classification = VulnerabilityChain().add(ClassificationMarkingCheck(cls_cfg))

        # Guardian review of the assembled package (advisory; attached, never blocking).
        self._governance = None
        if self.config.get("governance", {}).get("enabled"):
            from k9_dow.governance.guardian_governance import GuardianGovernance
            self._governance = GuardianGovernance(self.config)

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = payload.get("job_id", "unknown")
        filename = payload.get("filename", "?")
        doc_type = payload.get("document_type", "?")

        print(flush=True)
        print("━" * 60, flush=True)
        print(f"  DAS — Requirement Orchestrator", flush=True)
        print(f"  Job:      {job_id}", flush=True)
        print(f"  Document: {filename}", flush=True)
        print(f"  Type:     {doc_type}", flush=True)
        print(f"  Gates:    {GATE} (+ {JOINT_GATE}, parallel)", flush=True)
        print("━" * 60, flush=True)

        flow_t0 = time.monotonic()
        self._emit("OrchestratorStarted", job_id=job_id, filename=filename, document_type=doc_type)

        if self._classification is not None:
            res = self._classification.run(payload)
            if res.blocked:
                hit = next(r for r in res.results if r.blocked)
                reason = f"k9x_Shield blocked ingress [{hit.check_name}]: {hit.message}"
                print(f"  ✋ Classification screen BLOCKED job={job_id}: {hit.message}", flush=True)
                self._emit("ShieldBlocked", job_id=job_id, check=hit.check_name, reason=reason)
                return {"job_id": job_id, "orchestrator": "requirement", "status": "blocked_by_shield",
                        "check": hit.check_name, "reason": reason, "filename": filename}

        if self._shield is not None:
            try:
                self._shield.pre_process(payload, {"layer": self.layer, "component_type": "orchestrator"})
            except PermissionError as exc:
                reason = str(exc)
                check = reason.split("[", 1)[1].split("]", 1)[0] if "[" in reason else "k9x_Shield"
                print(f"  ✋ k9x_Shield BLOCKED job={job_id}: {reason}", flush=True)
                self._emit("ShieldBlocked", job_id=job_id, check=check, reason=reason)
                return {"job_id": job_id, "orchestrator": "requirement", "status": "blocked_by_shield",
                        "check": check, "reason": reason, "filename": filename}

        # Stage SCREEN: Shield + Granite Guardian per section; warnings only, never a rejection.
        screening = self._screen_document(job_id, filename, payload)
        if screening.get("flagged_sections"):
            from k9_dow.governance.document_screening import mark_untrusted
            payload = {**payload, "source_markdown": mark_untrusted(payload.get("source_markdown", ""), screening)}

        view_result = self._run_squad(self._load_squad("view_generation_squad.yaml", "ViewGenerationSquad"),
                                      "ViewGenerationSquad", payload)
        gate_result, package_result = self.prepare_gate(GATE, payload, view_result)
        joint_result = self._run_squad(self._load_squad("joint_review_squad.yaml", "JointReviewSquad"),
                                       "JointReviewSquad", {**payload, "prior_outputs": {**view_result, **gate_result}})

        total_elapsed = time.monotonic() - flow_t0
        print("━" * 60, flush=True)
        print(f"  ✓ Requirement stage complete  ({total_elapsed:.1f}s)", flush=True)
        print(f"  Status: awaiting_gate ({GATE}; {JOINT_GATE} in parallel)", flush=True)
        print("━" * 60, flush=True)
        print(flush=True)
        self._emit("OrchestratorCompleted", job_id=job_id, elapsed_s=round(total_elapsed, 1), gate=GATE)

        from k9_dow.config.process_model import load_process_model
        from k9_dow.utils.icd_composer import extract_source_title

        result = {
            "job_id": job_id,
            "orchestrator": "requirement",
            "process_model": load_process_model().id,
            "status": "awaiting_gate",
            "gate_id": GATE,
            "parallel_gates": [JOINT_GATE],
            "document_title": extract_source_title(payload.get("source_markdown", "")),
            "filename": filename,
            "document_type": doc_type,
            "view_generation": view_result,
            "gate_readiness": gate_result,
            "review_package": package_result,
            "joint_review": joint_result,
            "screening": {k: screening.get(k) for k in
                          ("status", "warning_count", "not_screened_count", "sections_screened", "report_uri")},
        }

        # Real governance check (see __init__ + governance/guardian_governance.py)
        # -- runs before persistence so the verdict is part of the stored
        # artifact, not just an in-memory annotation. Attaches result["governance"];
        # never blocks/raises (see GuardianGovernance.post_process's own docstring
        # for why this is advisory-to-the-human-reviewer, not an auto-reject).
        if self._governance is not None:
            result = self._governance.post_process(result, {"job_id": job_id})

        from k9_dow.gates.hil_gateway import save_stage_result
        # Later runs (MDD package, MSA, TMRR) read the requirement document as screened.
        save_stage_result(self.config, job_id, "source", {"markdown": payload.get("source_markdown", ""),
                                                          "filename": filename})
        s3_uri = self._store_to_s3(job_id, result)
        self._publish_hil_tasks(job_id, result, s3_uri)
        return result

    def _screen_document(self, job_id: str, filename: str, payload: dict) -> dict:
        """Run the Document Screening Report and store it (JSON + Markdown) with the job.
        A screening failure is itself recorded, never raised: the job goes on."""
        from k9_dow.gates.hil_gateway import STAGE_BUCKET, save_stage_result
        from k9_dow.governance.document_screening import report_markdown, screen_document
        try:
            report = screen_document(self.config, payload.get("source_markdown", ""), filename)
        except Exception as exc:
            log.warning("[Requirement] document screening failed for job=%s: %s", job_id, exc)
            report = {"artifact": "Document Screening Report", "document": filename, "status": "incomplete",
                      "error": str(exc)[:400], "warning_count": 0, "not_screened_count": 1,
                      "sections_screened": 0, "flagged_sections": [], "findings": []}
        try:
            from k9_aif_abb.k9_factories.object_storage_factory import ObjectStorageFactory
            store = ObjectStorageFactory.create(self.config)
            from k9_dow.config.instance import key_prefix
            key = f"{key_prefix()}by-job/{job_id}/screening/Document_Screening_Report.md"
            if "screened_at" in report:
                store.upload(STAGE_BUCKET, key, report_markdown(report).encode("utf-8"))
                report["report_uri"] = store.get_uri(STAGE_BUCKET, key)
        except Exception as exc:
            log.warning("[Requirement] storing the screening report failed (non-fatal): %s", exc)
        save_stage_result(self.config, job_id, "screening", report)
        print(f"  🔎 Document screening: {report['status']} ({report.get('warning_count', 0)} warning(s))", flush=True)
        self._emit("DocumentScreened", job_id=job_id, status=report["status"],
                   warnings=report.get("warning_count", 0), not_screened=report.get("not_screened_count", 0))
        return report

    def _store_to_s3(self, job_id: str, result: dict) -> Optional[str]:
        """Store generated docs to S3 under DAS_results/yyyymmdd/job_id/.

        Returns the URI of the stored result.json summary, or None on failure.
        """
        try:
            import json
            from datetime import datetime
            from k9_aif_abb.k9_factories.object_storage_factory import ObjectStorageFactory

            store = ObjectStorageFactory.create(self.config)
            date_prefix = datetime.now().strftime("%Y%m%d")
            # jcids-output already exists in MinIO, provisioned for exactly
            # this purpose -- DAS-results was never actually created, so
            # every upload here was silently failing (caught below).
            bucket = "jcids-output"

            sections = {
                "view_generation": "View Generation",
                "gate_readiness": "Gate Readiness",
                "review_package": "Review Package",
            }

            for section_key, label in sections.items():
                section = result.get(section_key, {})
                for agent_key, agent_output in section.items():
                    if not isinstance(agent_output, dict):
                        continue
                    output_text = agent_output.get("output", "")
                    if not output_text:
                        continue
                    agent_name = agent_output.get("agent", agent_key)
                    key = f"{date_prefix}/{job_id}/{section_key}/{agent_key}.md"
                    content = f"# {agent_name}\n\n{output_text}"
                    store.upload(bucket, key, content.encode("utf-8"))

            summary_key = f"{date_prefix}/{job_id}/result.json"
            store.upload(bucket, summary_key, json.dumps(result, indent=2).encode("utf-8"))

            # The reviewer-facing document: same composition function app.py
            # uses for its on-demand /view and /download endpoints, so HIL
            # (which will fetch this directly from S3, not call back into
            # DAS's API) shows the identical document a human would see there.
            from k9_dow.utils.icd_composer import compose_icd
            icd_key = f"{date_prefix}/{job_id}/ICD.md"
            store.upload(bucket, icd_key, compose_icd({"result": result}).encode("utf-8"))

            log.info("[Requirement] Stored results to S3 bucket=%s prefix=%s/%s", bucket, date_prefix, job_id)
            print(f"  ☁ Results stored to S3: {bucket}/{date_prefix}/{job_id}/", flush=True)
            return store.get_uri(bucket, icd_key)
        except Exception as exc:
            log.warning("[Requirement] S3 storage failed (non-fatal): %s", exc)
            return None

    def _publish_hil_tasks(self, job_id: str, result: dict, s3_uri: Optional[str]):
        """SERVICE-VALIDATION, then the parallel JCI-REVIEW. The result is stored first: a
        decision can arrive days later, in another process (gates/hil_gateway.py)."""
        from k9_dow.gates.hil_gateway import save_stage_result
        from k9_dow.utils.icd_composer import extract_jsd

        save_stage_result(self.config, job_id, "requirement", result)
        screening_report = (result.get("screening") or {}).get("report_uri")
        self.publish_review(
            GATE, job_id, result.get("gate_readiness") or {},
            description="Service capability requirement assembled and judged against the "
                        "joint-review minimum content; the Service requirements board validates. "
                        "Approval starts the Materiel Development Decision package.",
            extra={"Document screening": _screening_line(result.get("screening") or {})},
            artifacts=[f"{das_url()}/jobs/{job_id}/view/requirement", s3_uri, screening_report],
        )
        self.publish_review(
            JOINT_GATE, job_id, {},
            description="Joint Capability Integration review of the requirement (runs in parallel with "
                        "the acquisition flow and never holds it). Record the JROCM: endorse all, some "
                        "or none of the requirement, or reject; note tripwires and critical joint "
                        "capability requirements in the comment.",
            extra={"Recommended JSD": extract_jsd(result) or "see the JSD recommendation"},
            artifacts=[f"{das_url()}/jobs/{job_id}/view/jsd", f"{das_url()}/jobs/{job_id}/view/requirement"],
        )
