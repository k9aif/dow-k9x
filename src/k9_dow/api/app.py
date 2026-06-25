# SPDX-License-Identifier: Apache-2.0

"""FastAPI application for the DoW Architecture Workbench."""

from __future__ import annotations

import logging

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from k9_dow.messaging.event_publisher import InMemoryEventPublisher
from k9_dow.persistence.file_repository import FileRepository
from k9_dow.orchestrators.principal_orchestrator import PrincipalOrchestrator
from k9_dow.config.settings import settings

log = logging.getLogger(__name__)

app = FastAPI(
    title="K9-AIF DoW Architecture Workbench",
    description="DoDAF, JCIDS, SE, and Business document analysis powered by K9-AIF",
    version="0.1.0",
)

_event_publisher = InMemoryEventPublisher()
_file_repo = FileRepository(base_dir=settings.OUTPUT_DIR)
_orchestrator = PrincipalOrchestrator(
    config={},
    event_publisher=_event_publisher,
    file_repo=_file_repo,
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "k9-dow", "version": "0.1.0"}


@app.get("/llm")
async def llm_info():
    return {
        "active_llm": settings.ACTIVE_LLM,
        "ollama_host": settings.OLLAMA_HOST,
        "ollama_model": settings.OLLAMA_MODEL,
    }


@app.post("/jobs/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    log.info("[API] Upload received: %s (%d bytes)", file.filename, len(content))

    result = _orchestrator.process_upload(
        filename=file.filename,
        content=content,
    )

    return JSONResponse(content=result)


@app.post("/jobs/{job_id}/run")
async def run_job(job_id: str):
    normalized = _file_repo.load_markdown(job_id, "normalized_input.md")
    if not normalized:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found or not normalized")

    routing = _file_repo.load_json(job_id, "routing_manifest.json")

    result = _orchestrator.execute_flow({
        "job_id": job_id,
        "normalized_markdown": normalized,
        "routing_decision": routing,
    })

    return JSONResponse(content=result)


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    artifacts = _file_repo.list_artifacts(job_id)
    if not artifacts:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    routing = _file_repo.load_json(job_id, "routing_manifest.json")
    return {
        "job_id": job_id,
        "routing": routing,
        "artifacts": artifacts,
    }


@app.get("/jobs/{job_id}/events")
async def get_events(job_id: str):
    events = _event_publisher.events_for_job(job_id)
    return {"job_id": job_id, "events": [e.model_dump() for e in events]}


@app.get("/jobs/{job_id}/stages")
async def get_stages(job_id: str):
    artifacts = _file_repo.list_artifacts(job_id)
    stage_files = artifacts.get("stage_outputs", [])
    stages = {}
    for f in stage_files:
        content = _file_repo.load_markdown(job_id, f)
        stages[f] = content[:500] if content else ""
    return {"job_id": job_id, "stages": stages}


@app.get("/jobs/{job_id}/artifacts")
async def get_artifacts(job_id: str):
    index = _file_repo.build_artifact_index(job_id)
    if not index.get("artifacts"):
        raise HTTPException(status_code=404, detail=f"No artifacts for job {job_id}")
    return index


@app.get("/reports/{job_id}/{artifact_name}")
async def get_report(job_id: str, artifact_name: str):
    content = _file_repo.load_markdown(job_id, artifact_name)
    if content is None:
        json_content = _file_repo.load_json(job_id, artifact_name)
        if json_content:
            return JSONResponse(content=json_content)
        raise HTTPException(status_code=404, detail=f"Artifact {artifact_name} not found")
    return {"job_id": job_id, "artifact": artifact_name, "content": content}
