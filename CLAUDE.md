# CLAUDE.md — DoW Architecture Workbench

This is a **K9-AIF Solution Building Block (SBB)** — not a standalone application.
It extends K9-AIF ABBs via `pip install k9-aif[s3]`. Do NOT reinvent framework classes.

---

## Architecture Rule: SBB extends ABB

Every class in this project MUST extend or use a K9-AIF ABB. If the framework has an ABB for it, use it.

| Concern | K9-AIF ABB to use | DO NOT create |
|---|---|---|
| Agent | `BaseAgent` — `execute(payload) → dict` | Custom agent base class |
| Squad | YAML + the one `DasSquad(BaseSquad)` (`squads/das_squad.py`), built by the squad layer | A Python class per squad |
| Orchestrator | `BaseOrchestrator` — `execute_flow(payload) → dict` | Custom orchestrator base |
| Router | `BaseRouter` — `route(payload) → dict` | Custom router base |
| Squad layer | `squad_layer(config)` → `SquadLoader.from_agents` (k9-aif 1.18.1; backport in `das_squad.py`) | Agent lists or `AgentRegistry` in an orchestrator |
| Agent config | agent YAML `class:` + `module:`; merged by the squad layer (`AgentLoader`) | Custom config merging |
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
      yaml/               ← Squad YAML (agents + flow); no Python per squad
      das_squad.py        ← DasSquad (one class, every squad) + squad_layer()
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

## Pipeline flow (process model mca-2026-10)

The process lives in `src/k9_dow/config/process_model.yaml` (stages, gates, entry criteria, policy
sources, the run each approval starts, HIL queue). Change the process there, then run
`PYTHONPATH=src python tools/flow_diagram.py` to redraw the flow diagram. Tests check every
stage and gate cites a source and that JCI-REVIEW never blocks.

```
API upload → Docling (retrieval/normalize.py, framework DoclingParser) → job queue → dow.router.in
DasRouter → das.requirement → RequirementOrchestrator
    screening (governance/document_screening.py: Shield + Guardian, warn-only report)
    ViewGeneration → GateReadiness(SERVICE-VALIDATION) → PackageAssembly → JointReview (JSD)
    → HIL tasks: SERVICE-VALIDATION (blocking) + JCI-REVIEW (parallel, recorded only)
approval → das.mdd → MsaOrchestrator(run mdd_package): MddPackage squad → MDD task
approval → das.msa → MsaOrchestrator(run msa): MsaAnalysis squad (AoA, ASR, strategy) → MILESTONE-A task
approval → das.tmrr → TmrrOrchestrator: SrrPackage squad → SE-REVIEW-SRR task; approval ends the flow
```

- `orchestrators/stage_base.py` (`ProcessStageOrchestrator`) holds what every run shares:
  squads, `prepare_gate`, `publish_review`, `run_package`, ingress screening of the reviewer's
  HIL comment (`apply_shield`).
- `gates/hil_gateway.py`: gate topics, run chain, stage results by job id
  (`<prefix>by-job/<job>/<run>.json`), job history; JCIDS-era jobs still display.
- Only the Router process publishes to domain topics; it stamps `_topic`.
- `DAS_INSTANCE` (config/instance.py): a second DAS (das-next) on the same Kafka/MinIO/queue
  gets its own topics, groups, queue and storage prefix. Unset = unchanged names.
- Tests: `tests/test_process_model.py`, `test_hil_round_trip.py`, `test_document_screening.py`.

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
        resp = llm_invoke(self.config, req)     # raises on failure: let it propagate (below)
        self.publish_event({"type": "AgentCompleted", "agent": self.layer})
        return {"agent": self.layer, "output": resp.output}
```

---

## Policy as data: mappings, not prompts

Policy rules an agent applies (tables, thresholds, who decides what) live in **mapping files**,
`src/k9_dow/config/mappings/<id>.yaml`, never written into an agent's instructions or Python. Each file
is versioned, names a process model source (`source: S3`) and cites a paragraph per entry. An agent
names what it needs in its YAML (`mappings: [jsd]`); `SectionWriterAgent` renders it into the prompt via
`config/policy_mappings.py`. Change the policy in the mapping; the agent doesn't change.
**Test: a policy change touches one mapping file and its test, no agent.** Checked by
`tests/test_policy_mappings.py` (structure, citations, and the JSD tier-to-ACAT table against CJCSM
5123.01A Encl. B 2.b(3)-(6)). When writing a mapping, copy from the primary source's paragraph, not a
summary: the 2026-10-09 JSD prompt merged three paragraphs into one sentence and lost the ACAT-per-tier rule.

## Failures propagate: Agent → Squad → Orchestrator

**Rule:** a failed agent (model call, parse, tool) fails the stage; it is never turned into output the
squad carries on with. **Test: make one agent's model call raise; the stage ends as a recorded error
with Retry, and no later agent or package writer runs.** (Framework CLAUDE.md "Failures propagate".)

| Layer | Exception handling |
|---|---|
| Agent (`agents/src/`) | No try/except around `llm_invoke`, or one that re-raises with context. Never return `[WARN]`/empty/"validation_failed" output. |
| Loop agent (`K9ValidationLoopAgent`) | The ABB swallows a `run_validation()` error into `{"reason": "validation_failed"}`. Every loop agent overrides `fail()` with `raise_if_step_failed(self.layer, loop_ctx)` (`utils/loop_errors.py`). |
| Squad (`DasSquad` / `BaseSquad`) | Logs the failed step, re-raises. |
| Stage orchestrator (`stage_base.py`) | **Required** try/except: `PermissionError` → governance hold; `JobWithdrawn` → stop; anything else → `save_stage_result(status="error")` (Jobs in Pipeline offers Retry), then re-raise. |
| Orchestrator process (`runtime/dow_orchestrator_process.py`) | **Required** try/except: publishes `status: error` to the results topic; the consumer keeps running. |

- No `except ...: pass`. Optional parts that may be down (retriever, `.docx` rendering) log a warning or
  record the error in the result (`icd_docx_error`), and the main output still exists.
- Partial results only for side reports: `quality/icd_grader.py` keeps citation/completeness when the
  judge model is down and reports faithfulness "not scored".
- Enforced by `tests/test_loop_agent_errors.py` (the real ViewGenerationSquad stops on a failed model
  call) and `tests/test_error_propagation.py` (no silent handlers in agents or squads; every loop agent
  overrides `fail()`).
- k9_inspect K9-LLM-002 ("not inside try/except") is a false positive for DAS agents: the handling is
  the squad and orchestrator above. Don't satisfy it by wrapping agents.

---

## Orchestrator Pattern: an orchestrator knows only squads

**Rule (three-layer decoupling):** an orchestrator loads a squad by YAML file and squad id. It
never names, imports, registers or builds an agent: no agent-name lists (`AGENTS = (...)`), no
`AgentRegistry` / `AgentLoader` in an orchestrator module. **Test: if a squad's agents change, no
orchestrator changes** — only the squad YAML and the agent's own YAML and class. Not "doesn't
import": registering agents *by name* in an orchestrator is the same coupling (that was this
repo's old pattern, copied from the EOC; removed 2026-10-14).

The squad layer:

- Squads are **YAML** (`squads/yaml/`); `BaseSquad` runs the `flow:`.
- **One** `DasSquad(BaseSquad)` (`squads/das_squad.py`) for every squad; the loader instantiates it
  once per squad with that squad's agents. Its DAS behaviour: `before_step` stops a withdrawn job.
- `squad_layer(config)` builds the loader **once at the entry point**
  (`runtime/dow_orchestrator_process.py`) and passes it to every orchestrator as `squads=`.

```python
# entry point
squads = squad_layer(config)
msa = MsaOrchestrator(config=config, progress_callback=cb, squads=squads)

# orchestrator: squad file + id, nothing else
squad = self.squads.load_one(self._squads_dir / "msa_analysis_squad.yaml", "MsaAnalysisSquad",
                             config=run_config, agent_kwargs={"monitor": self._monitor})
result = squad.execute(payload)
```

Adding an agent to a squad: write the agent (class + YAML with `class:` and `module:`), add it to
the squad YAML. Nothing else. Checked by `tests/test_squad_layer.py`, by k9_inspect K9-DEC-002
(k9-aif >= 1.18.1) and by the framework's `check-orchestrator-squads.sh` hook on every edit.

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
- **Requirements to acquisition** (process model mca-2026-10): Service requirement, MDD, MSA to
  Milestone A, TMRR to the SRR; see "Pipeline flow" above. (Replaced the JCIDS-era phases.)
