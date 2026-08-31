from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from k9_aif_abb.k9_agents.registry.agent_registry import AgentRegistry
from k9_aif_abb.k9_core.orchestration.base_orchestrator import BaseOrchestrator
from k9_aif_abb.k9_squad.squad_loader import SquadLoader

from k9_dow.utils.agent_loader import AgentLoader
from k9_dow.agents.src.model_extractor_agent import ModelExtractorAgent
from k9_dow.agents.src.view_generator_agent import ViewGeneratorAgent
from k9_dow.agents.src.view_consistency_checker_agent import ViewConsistencyCheckerAgent
from k9_dow.agents.src.criteria_loader_agent import CriteriaLoaderAgent
from k9_dow.agents.src.evidence_collector_agent import EvidenceCollectorAgent
from k9_dow.agents.src.readiness_scorer_agent import ReadinessScorerAgent
from k9_dow.agents.src.gap_reporter_agent import GapReporterAgent
from k9_dow.agents.src.artifact_fetcher_agent import ArtifactFetcherAgent
from k9_dow.agents.src.completeness_checker_agent import CompletenessCheckerAgent
from k9_dow.agents.src.package_builder_agent import PackageBuilderAgent

log = logging.getLogger(__name__)

_JCIDS_AGENTS = {
    "ModelExtractorAgent": ModelExtractorAgent,
    "ViewGeneratorAgent": ViewGeneratorAgent,
    "ViewConsistencyCheckerAgent": ViewConsistencyCheckerAgent,
    "CriteriaLoaderAgent": CriteriaLoaderAgent,
    "EvidenceCollectorAgent": EvidenceCollectorAgent,
    "ReadinessScorerAgent": ReadinessScorerAgent,
    "GapReporterAgent": GapReporterAgent,
    "ArtifactFetcherAgent": ArtifactFetcherAgent,
    "CompletenessCheckerAgent": CompletenessCheckerAgent,
    "PackageBuilderAgent": PackageBuilderAgent,
}


class _ProgressMonitor:
    """Lightweight monitor that forwards agent events to the progress callback."""

    def __init__(self, callback):
        self._callback = callback
        self._interesting = {
            "loop_started", "hypothesis_generated", "validation_tool_invoked",
            "observation_evaluated", "loop_continued", "loop_finalized",
            "loop_escalated", "loop_failed", "AgentCompleted",
        }

    def record_event(self, event: dict):
        evt_type = event.get("type", "")
        if evt_type not in self._interesting:
            return
        agent = event.get("agent", "?")
        iteration = event.get("iteration", "")
        confidence = ""
        obs = event.get("observation", "")
        if isinstance(obs, dict):
            confidence = obs.get("confidence", "")
        elif isinstance(obs, str) and "confidence" in obs:
            try:
                import re
                m = re.search(r"'confidence':\s*([\d.]+)", obs)
                if m:
                    confidence = round(float(m.group(1)), 2)
            except Exception:
                pass

        ui_event = {"type": evt_type, "agent": agent}
        if iteration:
            ui_event["iteration"] = iteration
        if confidence:
            ui_event["confidence"] = confidence
        self._callback(ui_event)


class JcidsOrchestrator(BaseOrchestrator):
    """JCIDS Orchestrator — requirements process.

    Owns: View Generation Squad, Gate Readiness Squad, Package Assembly Squad.
    Produces: DoDAF views, JROC-ready packages.
    Gate: JROC-VALIDATION (non-delegable).
    """

    layer = "DAS JCIDS Orchestrator"

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 progress_callback: Optional[Callable[[dict], None]] = None, **kwargs) -> None:
        super().__init__(config=config or {}, **kwargs)
        self._squads_dir = Path(__file__).resolve().parent.parent / "squads" / "yaml"
        self._agents_dir = Path(__file__).resolve().parent.parent / "agents" / "yaml"
        self._progress = progress_callback or (lambda e: None)
        self._monitor = _ProgressMonitor(self._progress) if progress_callback else None

    def _load_squad(self, yaml_filename: str, squad_id: str):
        agent_loader = AgentLoader(self._agents_dir)
        registry = AgentRegistry()
        for name, cls in _JCIDS_AGENTS.items():
            registry.register(
                name,
                lambda c=cls, n=name: c(
                    config=agent_loader.merge_with_global(n, self.config),
                    monitor=self._monitor,
                ),
            )
        loader = SquadLoader(registry)
        return loader.load_one(str(self._squads_dir / yaml_filename), squad_id)

    def _emit(self, event_type: str, **kwargs):
        evt = {"type": event_type, "orchestrator": "JcidsOrchestrator", **kwargs}
        self._progress(evt)

    def _run_squad(self, squad, squad_name: str, payload: dict) -> dict:
        flow = getattr(squad, "flow", [])
        total = len(flow)
        agents = [s.get("agent", "?") for s in flow]
        print(f"\n  ▶ Squad: {squad_name}  ({total} agents)", flush=True)
        self._emit("SquadStarted", squad=squad_name, agents=agents, total=total)
        t0 = time.monotonic()
        result = squad.execute(payload)
        elapsed = time.monotonic() - t0
        print(f"  ✓ Squad: {squad_name}  done ({elapsed:.1f}s)\n", flush=True)
        self._emit("SquadCompleted", squad=squad_name, elapsed_s=round(elapsed, 1))
        return result

    def execute_flow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job_id = payload.get("job_id", "unknown")
        filename = payload.get("filename", "?")
        doc_type = payload.get("document_type", "?")

        print(flush=True)
        print("━" * 60, flush=True)
        print(f"  DAS — JCIDS Orchestrator", flush=True)
        print(f"  Job:      {job_id}", flush=True)
        print(f"  Document: {filename}", flush=True)
        print(f"  Type:     {doc_type}", flush=True)
        print(f"  Gate:     JROC-VALIDATION", flush=True)
        print("━" * 60, flush=True)

        flow_t0 = time.monotonic()
        self._emit("OrchestratorStarted", job_id=job_id, filename=filename, document_type=doc_type)

        view_gen_squad = self._load_squad("view_generation_squad.yaml", "ViewGenerationSquad")
        gate_squad = self._load_squad("gate_readiness_squad.yaml", "GateReadinessSquad")
        package_squad = self._load_squad("package_assembly_squad.yaml", "PackageAssemblySquad")

        view_result = self._run_squad(view_gen_squad, "ViewGenerationSquad", payload)

        gate_payload = {**payload, "prior_outputs": view_result, "gate_id": "JROC-VALIDATION"}
        gate_result = self._run_squad(gate_squad, "GateReadinessSquad", gate_payload)

        package_payload = {**payload, "prior_outputs": {**view_result, **gate_result}, "gate_id": "JROC-VALIDATION"}
        package_result = self._run_squad(package_squad, "PackageAssemblySquad", package_payload)

        total_elapsed = time.monotonic() - flow_t0
        print("━" * 60, flush=True)
        print(f"  ✓ JCIDS Pipeline Complete  ({total_elapsed:.1f}s)", flush=True)
        print(f"  Status: awaiting_gate (JROC-VALIDATION)", flush=True)
        print("━" * 60, flush=True)
        print(flush=True)
        self._emit("OrchestratorCompleted", job_id=job_id, elapsed_s=round(total_elapsed, 1), gate="JROC-VALIDATION")

        result = {
            "job_id": job_id,
            "orchestrator": "jcids",
            "status": "awaiting_gate",
            "gate_id": "JROC-VALIDATION",
            "view_generation": view_result,
            "gate_readiness": gate_result,
            "review_package": package_result,
        }

        s3_uri = self._store_to_s3(job_id, result)
        self._publish_hil_task(job_id, result, s3_uri)
        return result

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

            log.info("[JCIDS] Stored results to S3 bucket=%s prefix=%s/%s", bucket, date_prefix, job_id)
            print(f"  ☁ Results stored to S3: {bucket}/{date_prefix}/{job_id}/", flush=True)
            return store.get_uri(bucket, icd_key)
        except Exception as exc:
            log.warning("[JCIDS] S3 storage failed (non-fatal): %s", exc)
            return None

    def _publish_hil_task(self, job_id: str, result: dict, s3_uri: Optional[str]):
        """Publish a HIL task for the JROC-VALIDATION gate to Kafka.

        This is a fire-and-forget publish only: DAS does not consume a
        reply topic, and no downstream orchestrator resumes automatically
        on approval. That loop is a disclosed, unimplemented POC gap —
        this method's only job is to make the pending decision visible
        and actionable in K9X HIL.
        """
        try:
            from k9_aif_abb.k9_core.messaging.k9_event_bus import K9EventBus

            broker = self.config.get("messaging", {}).get("bootstrap_servers", "localhost:9092")
            # Keyed by the squad's own result_key (readiness_score/gap_report),
            # not the agent class name -- matches app.py's _compose_icd(),
            # which navigates the same gate_readiness dict the same way.
            gap_report = result.get("gate_readiness", {}).get("gap_report", {})
            readiness = result.get("gate_readiness", {}).get("readiness_score", {})

            task = {
                "title": f"JROC-VALIDATION review — {job_id}",
                "description": "DAS JCIDS pipeline complete; program manager or JROC "
                               "representative review requested before proceeding to Acquisition.",
                "source_orchestrator": "JcidsOrchestrator",
                "source_topic": "das.jcids",
                "reply_to": "das.jroc.replies",
                "correlation_id": job_id,
                "priority": "high",
                "payload": {
                    "job_id": job_id,
                    "gate_id": result.get("gate_id", "JROC-VALIDATION"),
                    "readiness_score": readiness.get("output") if isinstance(readiness, dict) else None,
                    "gap_summary": gap_report.get("output") if isinstance(gap_report, dict) else None,
                },
                # DAS's own /view/icd endpoint renders on demand from
                # _job_store, independent of whether S3 storage succeeded --
                # always include it so an approver always has something
                # clickable to actually review, even if s3_uri is None.
                "artifacts": [
                    u for u in (
                        f"{os.environ.get('DAS_PUBLIC_URL', 'https://das.k9x.ai').rstrip('/')}/jobs/{job_id}/view/icd",
                        s3_uri,
                    ) if u
                ],
                "pii": False,
                "ttl_hours": 168,
                "ttl_action": "reject",
            }

            bus = K9EventBus(broker_url=broker, topic="workflow.hil.das.jroc", group_id="das-jcids")
            bus.publish(task)
            if bus._producer:
                bus._producer.flush()
            bus.close()
            log.info("[JCIDS] Published HIL task for job=%s to workflow.hil.das.jroc", job_id)
            print(f"  → HIL task published: workflow.hil.das.jroc (job={job_id})", flush=True)
            self._emit("HilTaskPublished", job_id=job_id, topic="workflow.hil.das.jroc", artifact=s3_uri)
        except Exception as exc:
            log.warning("[JCIDS] HIL task publish failed (non-fatal): %s", exc)
