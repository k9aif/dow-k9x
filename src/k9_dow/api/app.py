# SPDX-License-Identifier: Apache-2.0
# DoW Architecture Workbench — FastAPI App Backend (Process 1 of 3)
#
# Serves UI, handles uploads, publishes events to Kafka.
# Does NOT run the pipeline — that's the router + orchestrator processes.

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from k9_dow.config.settings import settings
from k9_dow.utils.ids import generate_job_id

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

app = FastAPI(
    title="K9-AIF DoW Architecture Workbench",
    description="DoDAF 2.0 document analysis powered by K9-AIF",
    version="0.1.0",
)

_config = settings.load_yaml("config.yaml")
_kafka_producer = None


def _get_producer():
    global _kafka_producer
    if _kafka_producer is None:
        try:
            from kafka import KafkaProducer
            broker = _config.get("messaging", {}).get("bootstrap_servers", "localhost:9092")
            _kafka_producer = KafkaProducer(
                bootstrap_servers=broker,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            )
            log.info("[API] Kafka producer connected to %s", broker)
        except Exception as exc:
            log.warning("[API] Kafka not available: %s — running in local mode", exc)
    return _kafka_producer


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
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(default="architecture_document"),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    job_id = generate_job_id()
    text = content.decode("utf-8", errors="ignore")

    log.info("[API] Upload: %s (%d bytes) type=%s job=%s", file.filename, len(content), document_type, job_id)

    # Publish to Kafka router.in topic
    producer = _get_producer()
    topics = _config.get("messaging", {}).get("topics", {})
    router_topic = topics.get("router_in", "dow.router.in")

    event = {
        "job_id": job_id,
        "filename": file.filename,
        "document_type": document_type,
        "text": text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if producer:
        producer.send(router_topic, event)
        producer.flush()
        log.info("[API] Published to %s — job=%s", router_topic, job_id)
    else:
        # Local mode fallback — run in-process
        log.info("[API] No Kafka — running pipeline in-process")
        from k9_dow.orchestrators.principal_orchestrator import PrincipalOrchestrator
        orch = PrincipalOrchestrator(config=_config)
        result = orch.execute_flow({
            "job_id": job_id,
            "filename": file.filename,
            "text": text,
            "document_type": document_type,
        })
        return JSONResponse(content=result)

    return JSONResponse(content={
        "job_id": job_id,
        "status": "submitted",
        "filename": file.filename,
        "document_type": document_type,
        "route_topic": router_topic,
        "message": "Document submitted for processing. Monitor progress via /jobs/{job_id}/events",
    })


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    return {"job_id": job_id, "message": "Job status lookup — requires persistence layer"}


@app.get("/jobs/{job_id}/events")
async def get_events(job_id: str):
    return {"job_id": job_id, "message": "Event stream — SSE endpoint coming soon"}
