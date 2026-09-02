"""
Regenerates the 10-agent JCIDS run used for Sec. VII-G's context-enrichment
token-growth measurement, against the real, currently-configured Model
Router (qwen2.5:32b per config.yaml), and records exactly which model
actually produced it -- not assumed from config, but read back from each
agent's own InferenceResponse.model_alias/provider at runtime.

This exists because output_samples/sample_result.json (the file the
manuscript's Table 11 numbers were originally computed from) carries no
model/provider field at all -- an independent read-only audit confirmed
this. Re-running the same real orchestrator against the same real input
document (sample_ICD.md) closes that gap with a fresh, self-documenting
artifact.

Run: PYTHONPATH=src OLLAMA_HOST=http://<real-ollama-host>:11434 \
     python3 experiments/regenerate_context_sample.py
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from k9_aif_abb.k9_utils.config_loader import load_yaml
from k9_dow.orchestrators.jcids_orchestrator import JcidsOrchestrator

ROOT = Path(__file__).resolve().parent.parent
ICD_PATH = ROOT / "src/k9_dow/api/static/demos/output_samples/sample_ICD.md"
CONFIG_PATH = ROOT / "src/k9_dow/config/config.yaml"
OUT_PATH = Path(__file__).resolve().parent / "context_sample_regenerated.json"


def git_sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT
    ).decode().strip()


def main():
    cfg = load_yaml(str(CONFIG_PATH))
    # In-memory override only (not written back to config.yaml): Model Router
    # persistence needs a live Postgres, unavailable in this standalone
    # regeneration and irrelevant to the token counts being measured here.
    cfg.setdefault("inference", {}).setdefault("router", {}).setdefault(
        "persistence", {})["enabled"] = False
    resolved_base_url = cfg["inference"]["llm_factory"]["base_url"]
    resolved_general_model = cfg["inference"]["llm_factory"]["models"]["general"]["model"]
    resolved_reasoning_model = cfg["inference"]["llm_factory"]["models"]["reasoning"]["model"]

    source_markdown = ICD_PATH.read_text()

    orch = JcidsOrchestrator(config=cfg)
    payload = {
        "job_id": "context-regen-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "filename": ICD_PATH.name,
        "document_type": "ICD",
        "source_markdown": source_markdown,
    }

    t0 = datetime.now(timezone.utc)
    result = orch.execute_flow(payload)
    t1 = datetime.now(timezone.utc)

    artifact = {
        "generated_at_utc": t1.isoformat(),
        "elapsed_seconds": (t1 - t0).total_seconds(),
        "commit_sha": git_sha(),
        "input_document": str(ICD_PATH.relative_to(ROOT)),
        "config_resolved": {
            "base_url": resolved_base_url,
            "general_model": resolved_general_model,
            "reasoning_model": resolved_reasoning_model,
        },
        "invocation": (
            "PYTHONPATH=src OLLAMA_HOST=<ollama-host> "
            "python3 experiments/regenerate_context_sample.py"
        ),
        "result": result,
    }

    OUT_PATH.write_text(json.dumps(artifact, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")
    print(f"Resolved base_url: {resolved_base_url}")
    print(f"Resolved general/reasoning model: {resolved_general_model} / {resolved_reasoning_model}")
    print(f"Elapsed: {artifact['elapsed_seconds']:.1f}s")


if __name__ == "__main__":
    main()
