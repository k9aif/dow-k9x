# CLAUDE.md — DoW Architecture Workbench

This is a **K9-AIF Solution Building Block (SBB)** — not a standalone application.
It extends K9-AIF ABBs via `pip install k9-aif[s3]`. Do NOT reinvent framework classes.

---

## Architecture Rule: SBB extends ABB

Every class in this project MUST extend or use a K9-AIF ABB. If the framework has an ABB for it, use it.

| Concern | K9-AIF ABB to use | DO NOT create |
|---|---|---|
| Agent | `BaseAgent` — `execute(payload) → dict` | Custom agent base class |
| Squad | `BaseSquad` via `SquadLoader.load_one(yaml, id)` | Custom squad Python class |
| Orchestrator | `BaseOrchestrator` — `execute_flow(payload) → dict` | Custom orchestrator base |
| Router | `BaseRouter` — `route(payload) → dict` | Custom router base |
| Agent registry | `AgentRegistry.register(name, factory)` | Custom registry |
| Agent config | `AgentLoader.merge_with_global(name, config)` | Custom config merging |
| LLM calls | `llm_invoke(config, InferenceRequest)` | Direct Ollama/LLM calls |
| Events | `self.publish_event(dict)` on BaseAgent | Custom EventPublisher class |
| Monitoring | `monitor` param on BaseAgent/BaseOrchestrator | Custom monitoring |
| Object storage | `ObjectStorageFactory.create(config)` | Custom file repository |
| Governance | `self.enforce_governance()` / `require_governance()` | Custom governance wrapper |

**Reference SBB:** `k9-aif-framework/examples/K9X_Enterprise_Insurance_OperationsCenter/`

---

## Project Structure

```
dow-k9-aif/
  architecture/           ← design docs, diagrams
    diagrams/             ← PlantUML class + sequence diagrams
    docs/                 ← architecture decision records
  src/k9_dow/
    agents/
      src/                ← Python agents (extend BaseAgent)
      yaml/               ← Agent YAML configs (role, goal, instructions)
    squads/
      yaml/               ← Squad YAML (flow definitions — no Python needed)
    orchestrators/        ← Orchestrators (extend BaseOrchestrator)
    routers/              ← Router (extends BaseRouter)
    config/
      config.yaml         ← K9-AIF standard config
      routing_rules.yaml  ← Deterministic routing rules
      stage_catalog.yaml  ← DoDAF stage definitions
      prompts/            ← Grounding rules, governance rules, DoDAF 2.0 ref
    contracts/            ← Domain Pydantic models (payloads, results)
    api/                  ← FastAPI endpoints
    utils/                ← bootstrap.py, agent_loader.py (from EOC pattern)
  tests/
```

---

## Pipeline Cascade Flow

```
Document Upload (user selects document type = deterministic intent)
  → DocumentNormalizationAgent (extract/OCR)
  → DasRouter (deterministic — maps type to pipeline)
  → JcidsOrchestrator (produces ICD + relevant DoDAF views)
      → Squads via SquadLoader + AgentRegistry
      → Each agent: llm_invoke + publish_event
      → Initial ICD + F2P Summary
  → HIL Gate #1 (human reviews initial ICD)
  → JcidsOrchestrator (Phase 2 — consumes approved ICD)
      → Formal ICD + CDD + KPP/KSA
  → HIL Gate #2 (human reviews formal ICD)
  → SeOrchestrator (Phase 3 — consumes formal ICD)
      → SRD, SPS, TEMP, V&V matrix
```

### Reference deployment: HIL round trip (implemented 2026-10-02)

```
JcidsOrchestrator ─▶ JROC-VALIDATION task ─▶ workflow.hil.das.jroc ─▶ K9X HIL
K9X HIL decision ─▶ das.jroc.replies ─▶ Router process ─▶ gate_approved ─▶ das.acquisition
AcquisitionOrchestrator ─▶ PATHWAY-MILESTONE task ─▶ workflow.hil.das.pathway ─▶ K9X HIL
K9X HIL decision ─▶ das.pathway.replies ─▶ Router process ─▶ gate_approved ─▶ das.se
SeOrchestrator ─▶ demonstration endpoint (se.demo_stub: true): records next review (SRR), ends
```

- `gates/hil_gateway.py` owns gate topics, task publishing, and stage results
  stored by job id (`jcids-output/by-job/<job>/<stage>.json`).
- Only the Router process publishes to domain topics; it stamps `_topic` so the
  orchestrator process picks the right stage.
- A decision resumes a job only if the previous stage's package is stored
  (reply topics are read from the earliest offset). `DAS_HIL_APPROVERS` (optional)
  restricts whose decisions count.
- Reject / expire stops the pipeline at that gate (`stopped_at_gate`).
- Tests: `tests/test_hil_round_trip.py`.

---

## Agent Pattern (from SKILLS.md Skill 1)

Every agent MUST follow this pattern:

```python
from k9_aif_abb.k9_core.agent.base_agent import BaseAgent
from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
from k9_aif_abb.k9_utils.llm_invoke import llm_invoke

class MyAgent(BaseAgent):
    layer = "DoW MyAgent SBB"

    def __init__(self, config=None, monitor=None, **kwargs):
        super().__init__(config or {}, monitor=monitor, **kwargs)

    def execute(self, payload: dict) -> dict:
        req = InferenceRequest(
            prompt=f"Role: {self.config.get('role')}\n...",
            task_type=self.config.get("model", "reasoning"),
        )
        resp = llm_invoke(self.config, req)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": resp.output}
```

---

## Orchestrator Pattern (from EOC example)

An orchestrator module never imports agent classes. Every agent YAML carries `class:` and
`module:`; check with `k9aif inspect .` (k9-aif >= 1.15) before committing.

```python
from k9_aif_abb.k9_agents.registry.agent_registry import AgentRegistry
from k9_aif_abb.k9_core.orchestration.base_orchestrator import BaseOrchestrator
from k9_aif_abb.k9_squad.squad_loader import SquadLoader

class DodafOrchestrator(BaseOrchestrator):
    # Agents are named, never imported: each class resolves from its agent YAML's
    # class + module (k9_inspect rule K9-DEC-001, three-layer decoupling).
    def _load_squad(self, squads_yaml_path):
        agent_loader = AgentLoader(agents_yaml_dir)      # k9_dow.utils.agent_loader
        agent_registry = AgentRegistry()
        for name in ("MyAgent", ...):
            cls = agent_loader.resolve_class(name)
            agent_registry.register(
                name,
                lambda c=cls, n=name: c(config=agent_loader.merge_with_global(n, self.config)),
            )
        loader = SquadLoader(agent_registry)
        return loader.load_one(squads_yaml_path, squad_id)

    def execute_flow(self, payload):
        squad = self._load_squad(yaml_path)
        return squad.execute(payload)
```

---

## DoDAF 2.0 Agent Rules

All domain agents producing DoDAF artifacts MUST:

1. Use ONLY information from source document or approved prior-stage outputs
2. Mark missing info as `NOT PROVIDED IN SOURCE`
3. NEVER invent stakeholders, capabilities, systems, services, requirements
4. Include verbatim evidence citations
5. Use DoDAF ID formats: CAP-001, ACT-001, PERF-001, NODE-001, etc.
6. NEVER mention: AI, ML, cloud, Kafka, Neo4j, K9-AIF, pipeline, orchestrator
7. Maintain neutral DoD/government-review-ready tone

---

## Phases

- **Phase 1:** DoDAF pipeline (Stages 1-6) — current focus
- **Phase 2:** JCIDS pipeline (consumes DoDAF ICD output)
- **Phase 3:** SE pipeline (consumes JCIDS formal ICD)
