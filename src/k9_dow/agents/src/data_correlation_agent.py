# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — DataCorrelationAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class DataCorrelationAgent(BaseAgent):
    layer = "DoW DataCorrelation SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Architecture Data Correlation Specialist')}\n"
            f"Goal: {self.config.get('goal', 'Correlate all extracted architecture data across viewpoints')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Correlate all extracted architecture data across viewpoints.\n\n"
            "Produce the following sections:\n\n"
            "## Capability-to-Activity Traceability\n"
            "Cross-reference each capability with the operational activities it enables.\n"
            "Use a table: Capability | Operational Activity | Evidence.\n\n"
            "## System-to-Capability Mapping\n"
            "Map each system/service to the capabilities it supports.\n"
            "Use a table: System/Service | Capability | Relationship.\n\n"
            "## Mission-to-Architecture Traceability\n"
            "Trace from mission needs through capabilities to systems/services.\n"
            "Use a table: Mission Need | Capability | System/Service.\n\n"
            "## Evidence Map\n"
            "For each architecture element, list the source passages that support it.\n"
            "Flag elements with weak or missing evidence.\n\n"
            "## Taxonomy Alignment Issues\n"
            "Identify cases where the same concept appears under different names\n"
            "across viewpoints. Recommend canonical names.\n\n"
            "## Data Gaps\n"
            "List architecture elements referenced in one view but missing from others.\n"
            "Classify each gap by severity (critical/moderate/minor).\n\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "DataCorrelationAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "DataCorrelationAgent"})
        return {"agent": "DataCorrelationAgent", "output": output}
