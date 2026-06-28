# SPDX-License-Identifier: Apache-2.0
# DAS — FastAPI App Backend
#
# Serves UI, handles uploads, routes to orchestrators via Kafka or in-process.

from __future__ import annotations

import json
import logging
from pathlib import Path
from datetime import datetime, timezone

import asyncio
import uuid
from collections import deque

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from k9_aif_abb.k9_utils.config_loader import load_yaml
from k9_dow.config.settings import settings
from k9_dow.utils.ids import generate_job_id
from k9_dow.utils.health_check import check_dependencies

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


@app.on_event("startup")
async def _startup_checks():
    log.info("DAS App Backend — dependency check:")
    if not check_dependencies(_config):
        log.warning("Some dependencies are unreachable — pipeline calls may fail")
    asyncio.create_task(_consume_results())


async def _consume_results():
    """Background task: consume from das.results and push to SSE clients."""
    broker = _config.get("messaging", {}).get("bootstrap_servers", "localhost:9092")
    try:
        from aiokafka import AIOKafkaConsumer
        consumer = AIOKafkaConsumer(
            "das.results",
            bootstrap_servers=[broker],
            group_id="das-app-sse",
            auto_offset_reset="latest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await consumer.start()
        log.info("[SSE] Listening on das.results for live events")
        async for msg in consumer:
            evt = msg.value
            _event_log.append(evt)
            # Only store final pipeline results (not progress events)
            evt_result = evt.get("result")
            if isinstance(evt_result, dict) and evt_result.get("status"):
                job_id = (
                    evt.get("job_id")
                    or evt_result.get("job_id")
                )
                corr_id = evt.get("correlation_id", "")
                matched_key = None
                if job_id and job_id in _job_store:
                    matched_key = job_id
                else:
                    for k, v in _job_store.items():
                        if isinstance(v, dict) and v.get("correlation_id") == corr_id:
                            matched_key = k
                            break
                if matched_key:
                    _job_store[matched_key] = evt
                    log.info("[SSE] Stored result for job=%s", matched_key)
            dead = []
            for q in _sse_clients:
                try:
                    q.put_nowait(evt)
                except asyncio.QueueFull:
                    dead.append(q)
            for q in dead:
                _sse_clients.remove(q)
    except Exception as exc:
        log.warning("[SSE] Results consumer failed: %s", exc)


@app.get("/events/stream")
async def event_stream():
    q: asyncio.Queue = asyncio.Queue(maxsize=100)
    _sse_clients.append(q)

    async def generate():
        try:
            while True:
                evt = await q.get()
                yield f"data: {json.dumps(evt)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if q in _sse_clients:
                _sse_clients.remove(q)

    return StreamingResponse(generate(), media_type="text/event-stream")


_DEMOS_DIR = Path(__file__).parent / "static" / "demos"


@app.get("/demos")
async def list_demos():
    if not _DEMOS_DIR.exists():
        return {"demos": []}
    demos = []
    for f in sorted(_DEMOS_DIR.iterdir()):
        if f.is_file() and f.suffix in (".md", ".txt"):
            demos.append({"name": f.stem.replace("_", " "), "filename": f.name})
    return {"demos": demos}


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
    return {"status": "ok", "service": "das", "version": "0.2.0"}


@app.get("/llm")
async def llm_info():
    return {
        "active_llm": settings.ACTIVE_LLM,
        "ollama_host": settings.OLLAMA_HOST,
        "ollama_model": settings.OLLAMA_MODEL,
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
async def run_demo(demo_filename: str, document_type: str = "capability_gap"):
    demo_path = _DEMOS_DIR / demo_filename
    if not demo_path.exists():
        raise HTTPException(status_code=404, detail="Demo document not found")
    text = demo_path.read_text(encoding="utf-8")
    return await _submit_job(demo_filename, text, document_type)


async def _submit_job(filename: str, text: str, document_type: str):
    job_id = generate_job_id()
    log.info("[API] Submit: %s (%d bytes) type=%s job=%s", filename, len(text), document_type, job_id)
    try:
        from k9_aif_abb.k9_core.messaging.k9_event_bus import K9EventBus
        broker = _config.get("messaging", {}).get("bootstrap_servers", "localhost:9092")
        bus = K9EventBus(broker_url=broker, topic="dow.router.in", group_id="das-app")
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
        bus.publish(event)
        if bus._producer:
            bus._producer.flush()
        bus.close()
        log.info("[API] Published to dow.router.in job=%s corr=%s", job_id, event["correlation_id"])
        _job_store[job_id] = {"job_id": job_id, "status": "submitted", "correlation_id": event["correlation_id"]}
        return JSONResponse(content={
            "job_id": job_id, "status": "submitted",
            "correlation_id": event["correlation_id"],
            "message": "Document submitted to DAS pipeline via Kafka",
        })
    except Exception as exc:
        log.error("[API] Publish failed: %s", exc)
        return JSONResponse(status_code=500, content={"job_id": job_id, "status": "failed", "error": str(exc)})


@app.post("/jobs/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(default="capability_gap"),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    return await _submit_job(file.filename, content.decode("utf-8", errors="ignore"), document_type)


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    if job_id in _job_store:
        return _job_store[job_id]
    return {"job_id": job_id, "status": "not_found"}


def _is_garbage(s: str) -> bool:
    """Detect junk LLM output — walls of dashes, repeated chars, etc."""
    s = s.strip()
    if not s:
        return True
    if len(s) > 50 and len(set(s.replace(" ", ""))) <= 3:
        return True
    if s.count("-") > len(s) * 0.7:
        return True
    if s.count("=") > len(s) * 0.7:
        return True
    return False


def _humanize_output(text) -> str:
    """Convert JSON/dict agent output into readable markdown."""
    if isinstance(text, str) and _is_garbage(text):
        return "*Content not generated — requires a more capable LLM backend.*"
    if isinstance(text, dict):
        # If it has an "output" key, extract that first (agent result wrapper)
        if "output" in text and isinstance(text["output"], str) and len(text["output"]) > 20:
            return _humanize_output(text["output"])
        # ValidationLoopResult — extract the output from inside
        if "disposition" in text and "output" in text:
            return _humanize_output(text["output"])
        # Skip internal keys, extract readable content
        skip_keys = {"agent", "status", "squad_id", "steps", "iterations",
                     "evidence", "final_confidence", "disposition",
                     "remaining_steps", "notes"}
        lines = []
        for k, v in text.items():
            if k in skip_keys:
                continue
            if isinstance(v, str):
                if _is_garbage(v):
                    continue
                if len(v) > 10:
                    lines.append(v.strip())
                else:
                    lines.append(f"**{k}:** {v}")
            elif isinstance(v, list):
                clean_items = []
                for item in v:
                    if isinstance(item, dict):
                        clean = {ik: iv for ik, iv in item.items()
                                 if not (isinstance(iv, str) and _is_garbage(iv))}
                        if clean:
                            parts = [f"{ik}: {iv}" for ik, iv in clean.items()]
                            clean_items.append(f"- {', '.join(parts)}")
                    elif isinstance(item, str) and not _is_garbage(item):
                        clean_items.append(f"- {item}")
                if clean_items:
                    lines.append(f"**{k}:**")
                    lines.extend(clean_items)
            elif isinstance(v, dict):
                humanized = _humanize_output(v)
                if humanized and "not generated" not in humanized:
                    lines.append(f"**{k}:** {humanized}")
            elif v is not None and str(v).strip():
                lines.append(f"**{k}:** {v}")
        if not lines:
            return "*Content not generated — requires a more capable LLM backend.*"
        return "\n".join(lines)

    if isinstance(text, list):
        lines = []
        for i, item in enumerate(text, 1):
            if isinstance(item, dict):
                title = item.get("title") or item.get("name") or item.get("id") or f"Item {i}"
                desc = item.get("description") or item.get("shall_text") or ""
                item_type = item.get("type", "")
                line = f"**{i}. {title}**"
                if item_type:
                    line += f" ({item_type})"
                if desc:
                    line += f"\n   {desc}"
                vmethod = item.get("verification_method", "")
                if vmethod:
                    line += f"\n   *Verification:* {vmethod}"
                lines.append(line)
            else:
                lines.append(f"{i}. {item}")
        return "\n\n".join(lines)

    text = str(text).strip()
    # Strip markdown code fences
    import re
    fence_match = re.search(r'```(?:json)?\s*\n(.*?)```', text, re.DOTALL)
    if fence_match:
        inner = fence_match.group(1).strip()
        before = text[:fence_match.start()].strip()
        try:
            parsed = json.loads(inner)
            humanized = _humanize_output(parsed)
            return (before + "\n\n" + humanized).strip() if before else humanized
        except (json.JSONDecodeError, ValueError):
            pass
    if text.startswith("[") or text.startswith("{"):
        try:
            parsed = json.loads(text)
            return _humanize_output(parsed)
        except (json.JSONDecodeError, ValueError):
            pass
    return text


def _compose_icd(job_data: dict) -> str:
    """Compose a single ICD markdown document from all pipeline outputs."""
    result = job_data.get("result", job_data)
    job_id = result.get("job_id", "unknown")
    gate_id = result.get("gate_id", "")
    date_str = datetime.now().strftime("%d %B %Y")

    lines = []
    lines.append("# Initial Capabilities Document (ICD)")
    lines.append("")
    lines.append("## DRAFT — FOR DEMONSTRATION PURPOSES ONLY")
    lines.append("")
    lines.append(f"**Job ID:** {job_id}")
    lines.append(f"**Date:** {date_str}")
    lines.append(f"**Status:** Awaiting HIL Review ({gate_id})")
    lines.append(f"**Classification:** UNCLASSIFIED — PROOF OF CONCEPT")
    lines.append("")
    lines.append("---")
    lines.append("")

    sections = [
        ("view_generation", "1. Architecture Views", {
            "model_elements": "1.1 Model Elements (Capabilities, Requirements, Systems)",
            "generated_views": "1.2 Operational View (OV-1)",
            "consistency_report": "1.3 Cross-View Consistency Report",
        }),
        ("gate_readiness", "2. Gate Readiness Assessment", {
            "criteria": "2.1 Gate Entry Criteria",
            "evidence": "2.2 Evidence Summary",
            "readiness_score": "2.3 Readiness Score",
            "gap_report": "2.4 Gap Analysis",
        }),
        ("review_package", "3. Review Package", {
            "artifact_manifest": "3.1 Artifact Manifest",
            "completeness_check": "3.2 Completeness Assessment",
            "review_package": "3.3 Package Summary",
        }),
    ]

    for section_key, section_title, subsections in sections:
        section = result.get(section_key, {})
        if not section:
            continue
        lines.append(f"## {section_title}")
        lines.append("")

        for agent_key, subsection_title in subsections.items():
            agent_output = section.get(agent_key, {})
            if not isinstance(agent_output, dict):
                if isinstance(agent_output, str) and agent_output.strip():
                    lines.append(f"### {subsection_title}")
                    lines.append("")
                    lines.append(agent_output.strip())
                    lines.append("")
                continue
            output_text = _humanize_output(agent_output)
            lines.append(f"### {subsection_title}")
            lines.append("")
            lines.append(output_text)
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*Generated by DAS (Defense Acquisition System) — Built on K9-AIF Framework*")
    lines.append(f"*{date_str} | {job_id}*")

    return "\n".join(lines)


def _extract_docs(job_data: dict) -> list[dict]:
    """Return single consolidated ICD document."""
    result = job_data.get("result", job_data)
    if not result.get("view_generation") and not result.get("gate_readiness"):
        return []

    icd_content = _compose_icd(job_data)
    job_id = result.get("job_id", "unknown")

    return [{
        "id": "icd",
        "section": "Deliverables",
        "agent": "Initial Capabilities Document (ICD)",
        "filename": f"{job_id}_ICD.md",
        "size": len(icd_content),
    }]


@app.get("/jobs/{job_id}/docs")
async def list_docs(job_id: str):
    data = _job_store.get(job_id)
    if not data:
        log.warning("[API] /docs: job %s not found in store. Keys: %s", job_id, list(_job_store.keys()))
        raise HTTPException(status_code=404, detail="Job not found")
    log.info("[API] /docs: composing docs for job=%s", job_id)
    try:
        docs = _extract_docs(data)
        return {"job_id": job_id, "docs": docs}
    except Exception as exc:
        log.error("[API] /docs failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/jobs/{job_id}/docs/{doc_id}")
async def download_doc(job_id: str, doc_id: str):
    from fastapi.responses import Response

    data = _job_store.get(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")

    if doc_id == "icd":
        content = _compose_icd(data)
        filename = f"{job_id}_ICD.md"
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    raise HTTPException(status_code=404, detail="Document not found")


@app.get("/jobs/{job_id}/view/{doc_id}")
async def view_doc(job_id: str, doc_id: str):
    from fastapi.responses import HTMLResponse

    data = _job_store.get(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")

    if doc_id != "icd":
        raise HTTPException(status_code=404, detail="Document not found")

    md_content = _compose_icd(data)

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
            html += f"<h1>{line[2:]}</h1>\n"
        elif line.startswith("## DRAFT"):
            html += f'<div class="draft">{line[3:]}</div>\n'
        elif line.startswith("## "):
            html += f"<h2>{line[3:]}</h2>\n"
        elif line.startswith("### "):
            html += f"<h3>{line[4:]}</h3>\n"
        elif line.startswith("---"):
            html += "<hr>\n"
        elif line.startswith("**") and ":**" in line:
            html += f"<p>{line}</p>\n"
        elif line.startswith("|"):
            if "---|" in line:
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if any(c.startswith("Gap ID") or c.startswith("---") for c in cells):
                html += "<table><tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr>\n"
            else:
                html += "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>\n"
        elif line.strip() == "":
            html += "\n"
        else:
            html += f"<p>{line}</p>\n"

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
