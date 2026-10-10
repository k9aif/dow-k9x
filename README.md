# DoW Architecture Workbench (dow-k9x)

A [K9-AIF](https://github.com/k9aif/k9-aif-framework) Solution Building Block (SBB) that takes a Service capability requirement through the Department of Defense requirements and acquisition process **as it stands today** (Joint Force Requirements Process and the Major Capability Acquisition pathway, process model `mca-2026-10`, current as of October 2026), through a governed, human-gated multi-agent pipeline.

This is not a standalone application. It extends K9-AIF's Architecture Building Blocks (ABBs) — agents, squads, orchestrators, routing, governance, document conversion and event publishing all come from the framework; this project supplies only the DoW-specific domain logic on top of them.

## What it does

```
Upload (Docling: PDF, Word, scans → Markdown)  →  Screening (Shield + Granite Guardian; warnings report)
  → Requirement package + Joint Staffing Designator proposal
  → SERVICE-VALIDATION (human)        ── JCI-REVIEW (human, parallel, never blocks)
  → MDD package (AoA study guidance and plan)          → MDD (human)
  → MSA: AoA summary, Alternative Systems Review, acquisition strategy → MILESTONE-A (human)
  → TMRR: system requirements                          → SE-REVIEW-SRR (human)
```

Every gate is a human decision in [K9X HIL](https://hil.k9x.ai). The stages, gates, entry criteria and the policy source of each live in one versioned file, [`src/k9_dow/config/process_model.yaml`](src/k9_dow/config/process_model.yaml); the gate registry, router, HIL topics, UI flow diagram (`tools/flow_diagram.py`) and job history all read it. Sources (in `data/policy/`): SecDef memo of 20 Aug 2025; CJCSI 5123.01J CH 1 and CJCSM 5123.01A (5 Aug 2026, [Joint Staff library](https://www.jcs.mil/library/cjcs-manuals/)); DoWI 5000.02 Change 2; DoDI 5000.85; DoD SE Guidebook 2022. Design and evidence: [`docs/process-model-2026/`](docs/process-model-2026/).

Designed in the process model but not built: SFR, PDR, CDD-equivalent validation, the Development RFP Release, Milestone B, and the other five Adaptive Acquisition Framework pathways. DAS before October 2026 modelled JCIDS (JROC-VALIDATION, PATHWAY-MILESTONE); jobs from that version still display.

## Architecture

Three independently deployable processes, communicating only through Kafka:

| Process | Entry point | Role |
|---|---|---|
| App backend | `runit.sh` → `k9_dow.api.app` | FastAPI + web UI. Accepts uploads, publishes to `router.in`, streams job status. |
| Router | `start_router.sh` | Classifies incoming documents, stores originals in object storage (S3-compatible), routes to the correct pipeline topic (`orchestrator.in` / `jcids.in` / `se.in`). |
| Orchestrator | `start_orchestrator.sh` | Runs the stage orchestrators (Requirement, MSA, TMRR): squads → agents → LLM, under governance. |

Domain code lives under `src/k9_dow/`:

```
src/k9_dow/
  agents/       Python agents (extend K9-AIF's BaseAgent) + their YAML configs
  squads/       Squad flow definitions (YAML — no orchestration code required)
  orchestrators/  Phase orchestrators (extend BaseOrchestrator)
  routers/      Document classification/routing (extends BaseRouter)
  config/       config.yaml, routing rules, DoDAF stage catalog, prompts
  contracts/    Pydantic request/response models
  api/          FastAPI application
  utils/        Bootstrap and agent-loading helpers
```

See `CLAUDE.md` for the full ABB-to-SBB mapping this project follows and the DoDAF agent authoring rules.

## Setup

Requires Python 3.11+ and a running Kafka broker, PostgreSQL, Neo4j, S3-compatible object store, and an Ollama (or other) LLM endpoint — see `.env.example` for every connection setting, all defaulting to `localhost`.

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[all]"
cp .env.example .env   # edit with your own connection details
```

Run the three processes (each in its own terminal):

```bash
./runit.sh               # app backend + web UI, port 8000
./start_router.sh        # document router
./start_orchestrator.sh  # Requirement / MSA / TMRR orchestrators
```

## API surface

Selected endpoints from the app backend (`src/k9_dow/api/app.py`):

- `POST /jobs/upload` — submit a document for processing
- `GET /jobs/{job_id}` — job status
- `GET /jobs/{job_id}/docs` / `GET /jobs/{job_id}/view/{doc_id}` — generated artifacts
- `POST /gates/{gate_id}/decide` — human gate approve/reject
- `GET /events/stream` — server-sent event stream of pipeline progress
- `GET /pipeline`, `GET /llm`, `GET /health` — status/diagnostics

## License

Apache License 2.0.
