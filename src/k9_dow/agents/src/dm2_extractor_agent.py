# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import json
from k9_dow.agents.src.base_dow_agent import BaseDowAgent
from k9_dow.contracts.artifacts import DowAgentResult
from k9_dow.contracts.payloads import DowAgentPayload
from k9_dow.utils.markdown_utils import extract_first_json


class DM2ExtractorAgent(BaseDowAgent):
    layer = "DoW DM2Extractor SBB"
    agent_name = "DM2ExtractorAgent"

    def run_agent(self, payload: DowAgentPayload) -> DowAgentResult:
        prompt = self.build_prompt(
            role="DoDAF Meta-Model (DM2) Data Modeler",
            task=(
                "Extract DM2 entities and relationships from all available data.\n\n"
                "DM2 entity types to identify:\n"
                "- Performer (organizations, roles, systems)\n"
                "- Activity (operational activities, functions)\n"
                "- Resource (information, data, materiel)\n"
                "- Service (provided services, service descriptions)\n"
                "- Capability (mission capabilities)\n"
                "- Measure (metrics, KPIs)\n"
                "- Location (geographic, logical)\n"
                "- Condition (rules, constraints, standards)\n\n"
                "For each entity provide:\n"
                "- Entity name\n"
                "- DM2 type\n"
                "- Description\n"
                "- Verbatim evidence\n\n"
                "For relationships provide:\n"
                "- Source entity\n"
                "- Relationship type (performs, produces, consumes, supports, etc.)\n"
                "- Target entity\n\n"
                "If not found: NOT PROVIDED IN SOURCE\n\n"
                "Return Markdown report and JSON:\n"
                '{"entities": [{"name": "...", "dm2_type": "...", "description": "...", "evidence": "..."}], '
                '"relationships": [{"source": "...", "relationship": "...", "target": "..."}]}'
            ),
            source_text=payload.source_markdown,
            prior_outputs="\n".join(payload.prior_outputs.values()) if payload.prior_outputs else "",
        )

        raw = self.invoke_llm(prompt)
        json_str = extract_first_json(raw)
        json_data = json.loads(json_str) if json_str else {"entities": [], "relationships": []}
        citations = [
            e.get("evidence", "")
            for e in json_data.get("entities", [])
            if e.get("evidence")
        ]

        return DowAgentResult(
            job_id=payload.job_id,
            agent_name=self.agent_name,
            stage_id=payload.stage_id,
            status="completed",
            markdown=raw,
            json_data=json_data,
            citations=citations,
        )
