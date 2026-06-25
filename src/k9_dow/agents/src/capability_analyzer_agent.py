# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload


class CapabilityAnalyzerAgent(BaseDowAgent):
    layer = "DoW CapabilityAnalyzer SBB"
    agent_name = "CapabilityAnalyzerAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="Capability Assessment Analyst",
            task=(
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
                "If not found: NOT PROVIDED IN SOURCE"
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
        )
