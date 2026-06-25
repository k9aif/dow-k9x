# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — FastAPI application

from __future__ import annotations

import logging

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from k9_dow.orchestrators.principal_orchestrator import PrincipalOrchestrator

log = logging.getLogger(__name__)

app = FastAPI(
    title="K9-AIF DoW Architecture Workbench",
    description="DoDAF 2.0 document analysis powered by K9-AIF",
    version="0.1.0",
)

_orchestrator = PrincipalOrchestrator(config={})


@app.get("/health")
async def health():
    return {"status": "ok", "service": "k9-dow", "version": "0.1.0"}


@app.post("/jobs/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    log.info("[API] Upload: %s (%d bytes)", file.filename, len(content))
    result = _orchestrator.process_upload(filename=file.filename, content=content)
    return JSONResponse(content=result)


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    return {"job_id": job_id, "message": "Job status lookup — requires persistence layer"}
