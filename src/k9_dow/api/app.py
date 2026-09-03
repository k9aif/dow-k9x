# SPDX-License-Identifier: Apache-2.0
# DAS — FastAPI App Backend
#
# Serves UI, handles uploads, routes to orchestrators via Kafka or in-process.

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from datetime import datetime, timezone

import asyncio
import os
import uuid
from collections import deque

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from k9_aif_abb.k9_utils.config_loader import load_yaml
from k9_dow.config.settings import settings
from k9_dow.utils.ids import generate_job_id
from k9_dow.utils.health_check import check_dependencies, check_ollama_reachable

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

app = FastAPI(
    title="DAS — Defense Acquisition System",
    description="JCIDS / SE / Acquisition pipeline powered by K9-AIF",
    version="0.2.0",
)

_config = load_yaml(settings.CONFIG_DIR / "config.yaml")
_job_store: dict = {}
_event_log: deque = deque(maxlen=500)
_sse_clients: list = []

# Single-flight job queue -- confirmed necessary 2026-09-03 via a real
# concurrent-job test: two browsers submitting at once caused missing
# SquadStarted events (lost/misattributed progress) and GPU contention
# that made CompletenessCheckerAgent's Ollama call return an empty
# response entirely. Jobs now queue through an ElasticMQ/SQS-compatible
# queue instead of publishing straight to the Router, and only one is
# ever in flight at a time -- deliberately kept invisible to the UI (no
# new tab, no cancel) per explicit direction to not complicate this.
_QUEUE_ENDPOINT = os.environ.get("DAS_QUEUE_ENDPOINT", "http://192.168.1.98:9324")
_QUEUE_NAME = "das-job-queue"
_dispatch_state = {"running_job_id": None}


def _get_sqs_client():
    import boto3
    return boto3.client(
        "sqs",
        endpoint_url=_QUEUE_ENDPOINT,
        region_name="elasticmq",
        aws_access_key_id="x",
        aws_secret_access_key="x",
    )


def _get_or_create_queue_url(sqs) -> str:
    try:
        return sqs.get_queue_url(QueueName=_QUEUE_NAME)["QueueUrl"]
    except sqs.exceptions.QueueDoesNotExist:
        log.info("[Dispatcher] Queue %r doesn't exist yet -- creating it.", _QUEUE_NAME)
        return sqs.create_queue(QueueName=_QUEUE_NAME)["QueueUrl"]


def _publish_to_router(event: dict) -> None:
    """The actual Router-triggering publish -- previously called directly
    from _submit_job(); now only ever called from _dispatch_queue() so
    exactly one job is in flight at a time."""
    from k9_aif_abb.k9_core.messaging.k9_event_bus import K9EventBus
    broker = _config.get("messaging", {}).get("bootstrap_servers", "localhost:9092")
    bus = K9EventBus(broker_url=broker, topic="dow.router.in", group_id="das-app")
    bus.publish(event)
    if bus._producer:
        bus._producer.flush()
    bus.close()


async def _dispatch_queue():
    """Background task: while no job is running, pull one message off the
    queue and publish it to the Router. Freed to dispatch the next job by
    _consume_results() when it observes that job's terminal result on
    das.results -- reuses that existing signal rather than inventing a
    separate completion-notification mechanism."""
    sqs = _get_sqs_client()
    queue_url = _get_or_create_queue_url(sqs)
    log.info("[Dispatcher] Watching queue: %s", queue_url)
    loop = asyncio.get_event_loop()
    while True:
        if _dispatch_state["running_job_id"] is not None:
            await asyncio.sleep(1)
            continue
        try:
            resp = await loop.run_in_executor(
                None,
                lambda: sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=10),
            )
        except Exception as exc:
            log.warning("[Dispatcher] Queue receive failed: %s", exc)
            await asyncio.sleep(5)
            continue

        messages = resp.get("Messages", [])
        if not messages:
            continue

        msg = messages[0]
        try:
            event = json.loads(msg["Body"])
        except Exception as exc:
            log.error("[Dispatcher] Bad message body, dropping: %s", exc)
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"])
            continue

        job_id = event.get("job_id")
        _dispatch_state["running_job_id"] = job_id
        if job_id in _job_store:
            _job_store[job_id]["status"] = "running"

        try:
            _publish_to_router(event)
            log.info("[Dispatcher] Dispatched job=%s to router", job_id)
        except Exception as exc:
            log.error("[Dispatcher] Publish to router failed for job=%s: %s", job_id, exc)
            if job_id in _job_store:
                _job_store[job_id]["status"] = "failed"
            _dispatch_state["running_job_id"] = None

        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"])


@app.on_event("startup")
async def _startup_checks():
    log.info("DAS App Backend — dependency check:")
    if not check_dependencies(_config):
        log.warning("Some dependencies are unreachable — pipeline calls may fail")
    asyncio.create_task(_consume_results())
    asyncio.create_task(_dispatch_queue())


async def _consume_results():
    """Background task: consume from das.results and push to SSE clients."""
    broker = _config.get("messaging", {}).get("bootstrap_servers", "localhost:9092")
    try:
        from aiokafka import AIOKafkaConsumer
        consumer = AIOKafkaConsumer(
            "das.results",
            bootstrap_servers=[broker],
            group_id=f"das-app-sse-{uuid.uuid4()}",
            auto_offset_reset="latest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await consumer.start()
        log.info("[SSE] Listening on das.results for live events")
        async for msg in consumer:
            evt = msg.value
            _event_log.append(evt)

            # Resolve which submitted job this event belongs to for EVERY
            # event, not just final results -- session-scoped SSE delivery
            # below needs this for progress events too, not only the final
            # one. (Previously this lookup only ran inside the "final
            # result" branch, so progress events were broadcast to every
            # connected browser tab with no way to attribute them to a
            # session -- the frontend's own mySessionJobIds filter is only
            # a display-layer mitigation; the actual event still crossed
            # the wire to every visitor.)
            evt_result = evt.get("result")
            job_id = evt.get("job_id") or (evt_result.get("job_id") if isinstance(evt_result, dict) else None)
            corr_id = evt.get("correlation_id", "")
            matched_key = None
            if job_id and job_id in _job_store:
                matched_key = job_id
            else:
                for k, v in _job_store.items():
                    if isinstance(v, dict) and v.get("correlation_id") == corr_id:
                        matched_key = k
                        break

            # Only store final pipeline results (not progress events)
            if matched_key and isinstance(evt_result, dict) and evt_result.get("status"):
                # Merge, don't replace -- the submission-time entry carries
                # filename/document_type/submitted_at that evt doesn't have.
                _job_store[matched_key] = {**_job_store.get(matched_key, {}), **evt}
                # The merge above brings in evt's own top-level keys, but
                # the pipeline's success/failure verdict only ever lives
                # nested at evt["result"]["status"] (e.g. "awaiting_gate"
                # on success, "error" on failure) -- flatten it up to
                # _job_store's own top-level "status" so this entry stops
                # reading "queued"/"running" forever. Without this, every
                # completed job stayed "running" permanently in the queue
                # -- the 5-job cap would fill up after 5 jobs ever and
                # never free a slot again.
                _job_store[matched_key]["status"] = (
                    "error" if evt_result.get("status") == "error" else "complete"
                )
                log.info("[SSE] Stored result for job=%s", matched_key)
                # Terminal result for the job the dispatcher is currently
                # tracking -- free it to pull the next queued job. Reuses
                # this existing signal rather than a separate completion
                # notification path.
                if _dispatch_state["running_job_id"] == matched_key:
                    _dispatch_state["running_job_id"] = None
                    log.info("[Dispatcher] job=%s complete, freed for next dispatch", matched_key)

            event_session_id = (
                _job_store.get(matched_key, {}).get("session_id") if matched_key else None
            )
            dead = []
            for q, client_session_id in _sse_clients:
                # No session_id on the event (couldn't attribute it to a
                # known job) or no session_id on the client (older/direct
                # connection) -- fail open to "deliver it" rather than
                # silently dropping real events; this only degrades back
                # to the pre-existing global-broadcast behavior for the
                # narrow case it can't attribute, not for the common case.
                if event_session_id and client_session_id and event_session_id != client_session_id:
                    continue
                try:
                    q.put_nowait(evt)
                except asyncio.QueueFull:
                    dead.append((q, client_session_id))
            for item in dead:
                _sse_clients.remove(item)
    except Exception as exc:
        log.warning("[SSE] Results consumer failed: %s", exc)


SSE_KEEPALIVE_SECONDS = 15  # das.k9x.ai runs through a Cloudflare tunnel, which
# kills a connection to the origin after ~100s of silence (its 524 timeout).
# A real DAS run can easily go quiet that long between agent steps, so
# without this the stream dies mid-job on Cloudflare's side even though
# both the browser and the backend are still fine -- confirmed 2026-09-03
# via a live 524 in the browser console during a real stuck-job report.

@app.get("/events/stream")
async def event_stream(session_id: str = ""):
    q: asyncio.Queue = asyncio.Queue(maxsize=100)
    client = (q, session_id or None)
    _sse_clients.append(client)

    async def generate():
        try:
            while True:
                try:
                    evt = await asyncio.wait_for(q.get(), timeout=SSE_KEEPALIVE_SECONDS)
                    yield f"data: {json.dumps(evt)}\n\n"
                except asyncio.TimeoutError:
                    # SSE comment line (leading ":") -- ignored by EventSource's
                    # own parsing, but it's real bytes on the wire, which is
                    # all Cloudflare's idle-timeout cares about.
                    yield ": keep-alive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if client in _sse_clients:
                _sse_clients.remove(client)

    return StreamingResponse(generate(), media_type="text/event-stream")


_DEMOS_DIR = Path(__file__).parent / "static" / "demos"
_OUTPUT_SAMPLES_DIR = _DEMOS_DIR / "output_samples"


@app.get("/demos/sample-result")
async def sample_result():
    sample_path = _OUTPUT_SAMPLES_DIR / "sample_result.json"
    if not sample_path.exists():
        return {"error": "No sample result available"}
    with open(sample_path, encoding="utf-8") as f:
        data = json.load(f)
    _job_store[data["job_id"]] = data
    return data


DEMO_MODE = os.environ.get("DEMO_MODE", "ON").upper() == "ON"


@app.get("/config/mode")
async def get_mode():
    return {"demo_mode": DEMO_MODE}


@app.get("/demos")
async def list_demos():
    if not _DEMOS_DIR.exists():
        return {"demos": []}
    demos = []
    for f in sorted(_DEMOS_DIR.iterdir()):
        if f.is_file() and f.suffix in (".md", ".txt"):
            demos.append({"name": f.stem.replace("_", " "), "filename": f.name, "size": f.stat().st_size})
    return {"demos": demos}


def _resolve_demo_path(filename: str) -> Path:
    """Resolve filename to a real file strictly inside _DEMOS_DIR --
    Path(filename).name strips any directory components (../, absolute
    paths) before joining, so this can't be used to read arbitrary files
    on the host."""
    path = _DEMOS_DIR / Path(filename).name
    if not path.is_file() or path.parent != _DEMOS_DIR:
        raise HTTPException(status_code=404, detail="Input document not found")
    return path


@app.get("/demos/{filename}/download")
async def download_demo(filename: str):
    from fastapi.responses import Response
    path = _resolve_demo_path(filename)
    return Response(
        content=path.read_text(encoding="utf-8"),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{path.name}"'},
    )


@app.get("/demos/{filename}/view")
async def view_demo(filename: str):
    from fastapi.responses import HTMLResponse
    import html as html_lib
    path = _resolve_demo_path(filename)
    content = path.read_text(encoding="utf-8")
    return HTMLResponse(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{html_lib.escape(path.name)}</title>
<style>
  body {{ background:#0b0e14; color:#e2e8f0; font-family:-apple-system,sans-serif; margin:0; padding:32px; }}
  .doc {{ max-width:840px; margin:0 auto; }}
  h1 {{ font-size:14px; color:#8b95a5; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:24px; }}
  pre {{ white-space:pre-wrap; word-break:break-word; font-family:ui-monospace,monospace; font-size:13px; line-height:1.6; background:#141924; border:1px solid #232a3a; border-radius:8px; padding:20px; }}
</style></head>
<body><div class="doc"><h1>{html_lib.escape(path.name)}</h1><pre>{html_lib.escape(content)}</pre></div></body></html>""")


_STATIC_DIR = Path(__file__).parent / "static"
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.get("/")
async def index():
    html = _STATIC_DIR / "index.html"
    if html.exists():
        return FileResponse(html, headers={"Cache-Control": "no-cache"})
    return {"status": "ok", "message": "DAS API running. UI not yet built."}


@app.get("/health")
async def health():
    # Previously hardcoded {"status": "ok"} with no actual check --
    # the UI had no way to warn before job submission that the backend
    # LLM was unreachable; it could only find out after a job failed.
    ollama = check_ollama_reachable(_config)
    return {
        "status": "ok" if ollama["reachable"] else "degraded",
        "service": "das",
        "version": "0.2.0",
        "ollama": ollama,
    }


@app.get("/llm")
async def llm_info():
    return {
        "active_llm": settings.ACTIVE_LLM,
        "ollama_host": settings.OLLAMA_HOST,
        "ollama_model": settings.OLLAMA_MODEL,
        "ollama_display_name": settings.OLLAMA_DISPLAY_NAME,
        "data_sources": settings.KNOWLEDGE_CORPUS_LABEL,
    }


@app.get("/pipeline")
async def pipeline_info():
    from k9_dow.gates.gate_registry import DAS_GATES
    return {
        "orchestrators": ["jcids", "acquisition", "se", "traceability"],
        "gates": {gid: {"name": g.name, "non_delegable": g.non_delegable} for gid, g in DAS_GATES.items()},
        "topics": {
            "jcids": "das.jcids",
            "acquisition": "das.acquisition",
            "se": "das.se",
            "traceability": "das.traceability",
            "results": "das.results",
        },
    }


@app.post("/jobs/demo/{demo_filename}")
async def run_demo(demo_filename: str, document_type: str = "capability_gap", session_id: str = ""):
    demo_path = _DEMOS_DIR / demo_filename
    if not demo_path.exists():
        raise HTTPException(status_code=404, detail="Demo document not found")
    text = demo_path.read_text(encoding="utf-8")
    return await _submit_job(demo_filename, text, document_type, session_id)


MAX_QUEUE_SIZE = 5
_ACTIVE_JOB_STATUSES = {"queued", "running"}


def _active_jobs() -> list:
    """Jobs still queued or running, oldest first -- the actual queue
    depth/contents, not the full job history that _job_store accumulates."""
    jobs = [j for j in _job_store.values() if j.get("status") in _ACTIVE_JOB_STATUSES]
    jobs.sort(key=lambda j: j.get("submitted_at", ""))
    return jobs


@app.get("/jobs/queue")
def list_job_queue():
    """Last 5 jobs, oldest first (FIFO order) -- a new job is appended at
    the bottom, matching how the queue actually drains. A shared activity
    view, not just current queue depth: deliberately unfiltered by
    session, since a shared demo/demo login means everyone should be able
    to see what's ahead of (or has already finished before) their own job."""
    recent = sorted(_job_store.values(), key=lambda j: j.get("submitted_at", ""))[-MAX_QUEUE_SIZE:]
    return JSONResponse(content={
        "jobs": [
            {
                "job_id": j["job_id"],
                "filename": j.get("filename"),
                "document_type": j.get("document_type"),
                "status": j.get("status"),
                "submitted_at": j.get("submitted_at"),
            }
            for j in recent
        ],
        "max_queue_size": MAX_QUEUE_SIZE,
    })


async def _submit_job(filename: str, text: str, document_type: str, session_id: str = ""):
    if len(_active_jobs()) >= MAX_QUEUE_SIZE:
        return JSONResponse(status_code=429, content={
            "status": "rejected",
            "error": f"Job queue is full ({MAX_QUEUE_SIZE} max) -- try again once a running job finishes.",
        })
    job_id = generate_job_id()
    log.info("[API] Submit: %s (%d bytes) type=%s job=%s", filename, len(text), document_type, job_id)
    try:
        event = {
            "event_type": "capability_gap",
            "document_type": document_type,
            "job_id": job_id,
            "correlation_id": str(uuid.uuid4()),
            "filename": filename,
            "source_markdown": text,
            "icd_metadata": {
                "program_name": filename.rsplit(".", 1)[0].replace("_", " "),
                "date": datetime.now(timezone.utc).strftime("%d %B %Y"),
                "version": "1.0",
            },
        }
        # Enqueue rather than publish straight to the Router -- exactly one
        # job runs at a time (see _dispatch_queue()), so a second reviewer
        # opening a second tab (or one person double-clicking) can't starve
        # or corrupt an already-running job's GPU call or event stream.
        sqs = _get_sqs_client()
        queue_url = _get_or_create_queue_url(sqs)
        sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(event))
        log.info("[API] Enqueued job=%s corr=%s", job_id, event["correlation_id"])
        _job_store[job_id] = {
            "job_id": job_id, "status": "queued", "correlation_id": event["correlation_id"],
            "filename": filename, "document_type": document_type,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id or None,
        }
        return JSONResponse(content={
            "job_id": job_id, "status": "queued",
            "correlation_id": event["correlation_id"],
            "message": "Document queued for the DAS pipeline",
        })
    except Exception as exc:
        log.error("[API] Enqueue failed: %s", exc)
        return JSONResponse(status_code=500, content={"job_id": job_id, "status": "failed", "error": str(exc)})


@app.post("/jobs/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(default="capability_gap"),
    session_id: str = Form(default=""),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    return await _submit_job(file.filename, content.decode("utf-8", errors="ignore"), document_type, session_id)


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    if job_id in _job_store:
        return _job_store[job_id]
    return {"job_id": job_id, "status": "not_found"}


# ICD composition (strip_json_blocks/extract_text/compose_icd) moved to
# k9_dow.utils.icd_composer so jcids_orchestrator.py's S3 upload can produce
# the same reviewer-facing document as these on-demand endpoints, instead of
# only a raw JSON dump.
from k9_dow.utils.icd_composer import (
    compose_icd as _compose_icd,
    extract_text as _extract_text,
    strip_json_blocks as _strip_json_blocks,
)


def _input_doc_prefix(job_data: dict) -> str:
    """Short, filename-safe stem of the input document, for prefixing output
    filenames so multiple runs in one session stay distinguishable."""
    input_filename = job_data.get("filename") or ""
    stem = Path(input_filename).stem if input_filename else ""
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_")
    return stem[:40] or "input"


def _extract_docs(job_data: dict) -> list[dict]:
    """Return single consolidated ICD document."""
    result = job_data.get("result", job_data)
    if not result.get("view_generation") and not result.get("gate_readiness"):
        return []

    icd_content = _compose_icd(job_data)
    job_id = result.get("job_id", "unknown")
    date_prefix = datetime.now().strftime("%d%m%Y_%H%M%S")
    input_prefix = _input_doc_prefix(job_data)

    return [{
        "id": "icd",
        "section": "Deliverables",
        "agent": f"Initial Capabilities Document (ICD) — {input_prefix}",
        "filename": f"{date_prefix}_{input_prefix}_{job_id}_ICD.md",
        "size": len(icd_content),
    }]


@app.get("/jobs/{job_id}/docs")
async def list_docs(job_id: str):
    data = _job_store.get(job_id)
    if not data:
        log.warning("[API] /docs: job %s not found in store. Keys: %s", job_id, list(_job_store.keys()))
        raise HTTPException(status_code=404, detail="Job not found", headers={"Cache-Control": "no-store"})
    log.info("[API] /docs: composing docs for job=%s", job_id)
    try:
        docs = _extract_docs(data)
        return JSONResponse(
            content={"job_id": job_id, "docs": docs},
            headers={"Cache-Control": "no-store"},
        )
    except Exception as exc:
        log.error("[API] /docs failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/jobs/{job_id}/docs/{doc_id}")
async def download_doc(job_id: str, doc_id: str):
    from fastapi.responses import Response

    data = _job_store.get(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found", headers={"Cache-Control": "no-store"})

    if doc_id == "icd":
        # Serve static sample for demo job
        if job_id == "JOB-20260628-DEMO01":
            sample_md = _OUTPUT_SAMPLES_DIR / "sample_ICD.md"
            if sample_md.exists():
                content = sample_md.read_text(encoding="utf-8")
                return Response(
                    content=content,
                    media_type="text/markdown",
                    headers={"Content-Disposition": f'attachment; filename="{job_id}_ICD.md"'},
                )
        content = _compose_icd(data)
        date_prefix = datetime.now().strftime("%d%m%Y_%H%M%S")
        filename = f"{date_prefix}_{_input_doc_prefix(data)}_{job_id}_ICD.md"
        return Response(
            content=content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-store",
            },
        )

    raise HTTPException(status_code=404, detail="Document not found")


@app.get("/jobs/{job_id}/view/{doc_id}")
async def view_doc(job_id: str, doc_id: str):
    from fastapi.responses import HTMLResponse

    # Serve static sample for demo job
    if job_id == "JOB-20260628-DEMO01" and doc_id == "icd":
        sample_md = _OUTPUT_SAMPLES_DIR / "sample_ICD.md"
        if sample_md.exists():
            md_content = sample_md.read_text(encoding="utf-8")
            return _render_icd_html(job_id, md_content)

    data = _job_store.get(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found", headers={"Cache-Control": "no-store"})

    if doc_id != "icd":
        raise HTTPException(status_code=404, detail="Document not found")

    md_content = _compose_icd(data)
    return _render_icd_html(job_id, md_content)


def _render_icd_html(job_id: str, md_content: str):
    from fastapi.responses import HTMLResponse
    in_table = False
    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>ICD — {job_id}</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 24px;
         background: #0f172a; color: #e2e8f0; line-height: 1.7; }}
  h1 {{ color: #3b82f6; border-bottom: 2px solid #334155; padding-bottom: 8px; }}
  h2 {{ color: #3b82f6; margin-top: 32px; border-bottom: 1px solid #334155; padding-bottom: 4px; }}
  h3 {{ color: #22c55e; margin-top: 24px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }}
  th, td {{ border: 1px solid #334155; padding: 8px 12px; text-align: left; }}
  th {{ background: #1e293b; color: #94a3b8; font-weight: 600; }}
  td {{ background: #0f172a; }}
  strong {{ color: #e2e8f0; }}
  em {{ color: #94a3b8; }}
  hr {{ border: none; border-top: 1px solid #334155; margin: 24px 0; }}
  .draft {{ background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3);
            color: #f59e0b; padding: 8px 16px; border-radius: 6px; font-size: 13px; margin: 16px 0; }}
  a.dl {{ display: inline-block; background: #22c55e; color: #000; padding: 8px 20px;
          border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 13px; margin: 16px 0; }}
  a.dl:hover {{ opacity: 0.8; }}
</style>
</head><body>
<a class="dl" href="/jobs/{job_id}/docs/icd">Download as Markdown</a>
"""

    for line in md_content.split("\n"):
        if line.startswith("# "):
            if in_table: html += "</table>\n"; in_table = False
            html += f"<h1>{line[2:]}</h1>\n"
        elif line.startswith("## DRAFT"):
            html += f'<div class="draft">{line[3:]}</div>\n'
        elif line.startswith("## "):
            if in_table: html += "</table>\n"; in_table = False
            html += f"<h2>{line[3:]}</h2>\n"
        elif line.startswith("### "):
            if in_table: html += "</table>\n"; in_table = False
            html += f"<h3>{line[4:]}</h3>\n"
        elif line.startswith("---"):
            if in_table: html += "</table>\n"; in_table = False
            html += "<hr>\n"
        elif line.startswith("|"):
            if "---|" in line:
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not in_table:
                html += "<table><tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr>\n"
                in_table = True
            else:
                html += "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>\n"
        elif line.strip() == "":
            if in_table: html += "</table>\n"; in_table = False
            html += "\n"
        else:
            if in_table: html += "</table>\n"; in_table = False
            html += f"<p>{line}</p>\n"

    if in_table: html += "</table>\n"
    html += "</body></html>"
    return HTMLResponse(content=html)


@app.post("/gates/{gate_id}/decide")
async def gate_decision(gate_id: str, action: str = Form(...), decided_by: str = Form(...), rationale: str = Form(default="")):
    from k9_dow.gates.gate_registry import GateRegistry
    from k9_dow.gates.gate_model import GateDecision
    from k9_dow.graph.schema import GateAction

    registry = GateRegistry()
    try:
        registry.init_gate(gate_id)
        decision = GateDecision(
            gate_id=gate_id,
            action=GateAction(action),
            decided_by=decided_by,
            rationale=rationale,
        )
        status = registry.record_decision(gate_id, decision)
        return {"gate_id": gate_id, "state": status.state, "may_proceed": registry.may_proceed(gate_id)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/graph/invariants")
async def check_invariants():
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
        from k9_dow.graph.invariants import check_all_invariants
        results = check_all_invariants(driver)
        driver.close()
        return [{"id": r.id, "name": r.name, "passed": r.passed, "violations": r.violations} for r in results]
    except Exception as exc:
        return {"status": "unavailable", "reason": str(exc)}
