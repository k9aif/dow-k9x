# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""Grade a generated ICD against the submitted source document.

Three scores, each traceable to the items behind it:

- Citation accuracy (deterministic): every verbatim quote in the ICD that is
  20+ characters is looked up in the source (whitespace/case normalised).
- Completeness (deterministic): the ICD's required sections are present.
- Faithfulness (independent model, the ``judge`` alias, deepseek-r1:32b by
  default): each extracted model element (capability needs, SE requirements,
  baseline items) is judged supported / unsupported / contradicted by the
  source; score = supported / judged.

The overall score is the mean of the three. An aid for the human reviewer,
not a verdict: an LLM judge is not calibrated against human graders here.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List

REQUIRED_SECTIONS = [
    ("Model elements", r"Model Elements"),
    ("Operational view", r"Operational View|OV-1"),
    ("Cross-view consistency", r"Consistency Report"),
    ("Gate entry criteria", r"Gate Entry Criteria"),
    ("Evidence", r"Evidence Summary"),
    ("Readiness score", r"Readiness Score"),
    ("Gap analysis", r"Gap Analysis"),
    ("Review package", r"Review Package|Package Summary"),
]


def _norm(t: str) -> str:
    """Compare text, not markdown: table pipes, bold/italic markers and
    whitespace are ignored on both sides."""
    t = t.replace("’", "'").replace("“", '"').replace("”", '"')
    t = re.sub(r"[|*_`#>]", " ", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def _source_cited_part(icd: str) -> str:
    """Only the architecture views cite the source verbatim; later sections
    (gate readiness, package) quote the pipeline's own reports."""
    m = re.search(r"^##\s*2\.\s*Gate Readiness", icd, flags=re.M | re.I)
    return icd[:m.start()] if m else icd


def citation_accuracy(source: str, icd: str) -> Dict[str, Any]:
    src = _norm(source)
    quotes = []
    # A real quotation opens after start/space/bracket and closes before
    # space/punctuation, so the gap between two short quoted names is not
    # mistaken for one quotation.
    pattern = r'(?:(?<=^)|(?<=[\s(\[|:]))"([^"\n]{20,600})"(?=[\s.,;:)\]|]|$)'
    for q in re.findall(pattern, _source_cited_part(icd).replace("“", '"').replace("”", '"'), flags=re.M):
        parts = [p.strip(" .") for p in re.split(r"\.\.\.|…", q) if len(p.strip(" .")) >= 12]
        if parts:
            quotes.append((q, all(_norm(p) in src for p in parts)))
    found = sum(1 for _, ok in quotes if ok)
    return {"score": round(found / len(quotes), 3) if quotes else None, "checked": len(quotes),
            "found": found, "not_found": [q[:160] for q, ok in quotes if not ok][:10]}


def completeness(icd: str) -> Dict[str, Any]:
    present = [(name, bool(re.search(pat, icd, re.I))) for name, pat in REQUIRED_SECTIONS]
    return {"score": round(sum(ok for _, ok in present) / len(present), 3),
            "missing": [n for n, ok in present if not ok],
            "not_provided_markers": len(re.findall(r"NOT PROVIDED IN SOURCE", icd))}


def _claims(icd: str) -> List[Dict[str, str]]:
    """The ICD's extracted model elements: one claim per CN/SR/TBI line."""
    out = []
    for line in icd.splitlines():
        m = re.match(r"\s*[-*]\s*id:\s*((?:CN|SR|TBI|CAP)-\d+)\s*,\s*(.+)", line)
        if m:
            out.append({"id": m.group(1), "text": m.group(2).strip()[:400]})
    return out[:60]


def _parse_json_array(text: str) -> List[Dict[str, Any]]:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    m = re.search(r"\[[\s\S]*\]", text)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
        return [d for d in data if isinstance(d, dict) and d.get("id")]
    except json.JSONDecodeError:
        return []


def faithfulness(source: str, icd: str, config: Dict[str, Any]) -> Dict[str, Any]:
    from k9_aif_abb.k9_inference.models.inference_request import InferenceRequest
    from k9_aif_abb.k9_utils.llm_invoke import llm_invoke
    claims = _claims(icd)
    if not claims:
        return {"score": None, "judged": 0, "note": "no model elements found in the ICD"}
    listing = "\n".join(f"{c['id']}: {c['text']}" for c in claims)
    prompt = (
        "You are checking an Initial Capabilities Document (ICD) against the source document it was "
        "generated from. For EACH claim below decide whether the SOURCE supports it.\n"
        "supported = stated or directly implied by the source; unsupported = not in the source "
        "(invented or assumed); contradicted = the source says otherwise.\n"
        "Answer ONLY with a JSON array, one object per claim: "
        '[{"id": "CN-001", "verdict": "supported|unsupported|contradicted", "evidence": "short quote from the source or empty"}]\n\n'
        f"SOURCE DOCUMENT:\n{source[:24000]}\n\nCLAIMS FROM THE ICD:\n{listing}\n"
    )
    resp = llm_invoke(config, InferenceRequest(prompt=prompt, task_type="judge",
                                               metadata={"agent": "DAS ICD Grader"}))
    verdicts = {d["id"]: d for d in _parse_json_array(resp.output)}
    judged = [dict(c, **{k: verdicts[c["id"]].get(k) for k in ("verdict", "evidence")})
              for c in claims if c["id"] in verdicts]
    sup = sum(1 for j in judged if str(j.get("verdict", "")).lower() == "supported")
    return {"score": round(sup / len(judged), 3) if judged else None, "claims": len(claims),
            "judged": len(judged), "supported": sup,
            "flagged": [j for j in judged if str(j.get("verdict", "")).lower() != "supported"][:15],
            "model": getattr(resp, "model_alias", None)}


def grade(source: str, icd: str, config: Dict[str, Any], input_name: str = "", output_name: str = "") -> Dict[str, Any]:
    t0 = time.monotonic()
    cit = citation_accuracy(source, icd)
    comp = completeness(icd)
    faith = faithfulness(source, icd, config)
    parts = [x["score"] for x in (faith, comp, cit) if x.get("score") is not None]
    judge_model = ((config.get("inference") or {}).get("llm_factory", {}).get("models", {})
                   .get("judge", {}).get("model"))
    return {
        "input_document": input_name, "output_document": output_name,
        "overall": round(sum(parts) / len(parts), 3) if parts else None,
        "faithfulness": faith, "completeness": comp, "citation_accuracy": cit,
        "scored_by": judge_model, "elapsed_s": round(time.monotonic() - t0, 1),
        "note": "Aid for the human reviewer, not a verdict; the model judge is not calibrated against human graders.",
    }
