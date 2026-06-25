# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — CapabilityAnalyzerAgent (SBB)

from typing import Any, Dict, Optional

from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke


class CapabilityAnalyzerAgent(BaseAgent):
    layer = "DoW CapabilityAnalyzer SBB"

    def __init__(self, config: Optional[Dict[str, Any]] = None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload.get("source_markdown") or ""
        prior = payload.get("prior_outputs") or {}
        prior_text = "\n".join(prior.values()) if prior else ""

        prompt = (
            f"Role: {self.config.get('role', 'Capability Assessment Analyst')}\n"
            f"Goal: {self.config.get('goal', 'Perform capability-by-capability assessment using prior extraction data')}\n\n"
            "## Grounding Rules\n"
            "Use only the source document and approved prior-stage outputs.\n"
            "Do not invent facts. If evidence is missing, write: NOT PROVIDED IN SOURCE.\n"
            "Include short source evidence snippets. Keep tone neutral, government-review-ready.\n\n"
            "## Task\n"
            "Perform a capability-by-capability assessment using prior extraction data.\n\n"
            "Produce the following sections:\n\n"
            "## Capability Assessment Matrix\n"
            "For each identified capability, assess:\n"
            "| Capability | Maturity | Supporting Systems | Evidence Strength | Gaps |\n"
            "Maturity levels: Initial / Developing / Defined / Managed / Optimized.\n"
            "Evidence strength: Strong / Moderate / Weak / None.\n\n"
            "## Capability Gaps\n"
            "List capabilities that are:\n"
            "- Required by mission needs but not yet identified\n"
            "- Identified but insufficiently supported by systems/services\n"
            "- Identified but lacking evidence in the source\n\n"
            "## Capability Dependencies\n"
            "Map which capabilities depend on other capabilities.\n"
            "Identify critical dependency chains.\n\n"
            "## Capability Risk Assessment\n"
            "Flag capabilities with high risk due to:\n"
            "- Low maturity in critical mission areas\n"
            "- Single-system dependency\n"
            "- Missing evidence\n\n"
            "If not found: NOT PROVIDED IN SOURCE\n\n"
            f"## Source Document\n{source[:6000]}\n"
        )
        if prior_text:
            prompt += f"\n## Prior Outputs\n{prior_text[:4000]}\n"

        req = InferenceRequest(
            prompt=prompt,
            task_type=self.config.get("model", "reasoning"),
            metadata={"agent": "CapabilityAnalyzerAgent"},
        )
        resp = llm_invoke(self.config, req)
        output = resp.output.strip()

        self.publish_event({"type": "AgentCompleted", "agent": "CapabilityAnalyzerAgent"})
        return {"agent": "CapabilityAnalyzerAgent", "output": output}
