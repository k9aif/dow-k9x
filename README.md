# DoW Architecture Workbench (dow-k9x)

A [K9-AIF](https://github.com/k9aif/k9-aif-framework) Solution Building Block (SBB) that automates Department of Defense architecture and acquisition document analysis: DoDAF 2.0 viewpoints, JCIDS capability documents, and Systems Engineering artifacts, produced from source documents through a governed, human-gated multi-agent pipeline.

This is not a standalone application. It extends K9-AIF's Architecture Building Blocks (ABBs) — agents, squads, orchestrators, routing, governance, and event publishing all come from the framework; this project supplies only the DoW-specific domain logic on top of them.

## What it does

Given an uploaded source document (a capability need statement, an existing architecture description, a requirements document), the pipeline produces:

- **DoDAF 2.0 views** (Phase 1) — operational, capability, and systems viewpoints derived only from evidence in the source document, with unsupported fields explicitly marked `NOT PROVIDED IN SOURCE`.
- **JCIDS capability documents** (Phase 2) — an Initial Capabilities Document (ICD) progressing to a formal ICD, Capability Development Document (CDD), and KPP/KSA set, gated by human review between stages.
- **Systems Engineering artifacts** (Phase 3) — SRD, SPS, TEMP, and a verification & validation matrix, derived from the approved formal ICD.

Every stage runs under K9-AIF's governance model (pre/post execution policy hooks) and publishes progress as Kafka events; human reviewers approve or reject at two gates before the pipeline advances.

## Architecture

Three independently deployable processes, communicating only through Kafka:

| Process | Entry point | Role |
|---|---|---|
| App backend | `runit.sh` → `k9_dow.api.app` | FastAPI + web UI. Accepts uploads, publishes to `router.in`, streams job status. |
| Router | `start_router.sh` | Classifies incoming documents, stores originals in object storage (S3-compatible), routes to the correct pipeline topic (`orchestrator.in` / `jcids.in` / `se.in`). |
| Orchestrator | `start_orchestrator.sh` | Runs the DoDAF/JCIDS/SE squads (agents → LLM → governance) for whichever phase the document was routed to. |

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
./start_orchestrator.sh  # DoDAF/JCIDS/SE orchestrator
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
