# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""Policy mappings: policy rules kept as data in config/mappings/<id>.yaml, not in agent prompts.

An agent names the mappings it needs in its YAML (``mappings: [jsd]``); the section writer
renders each one into the prompt. One file per mapping, versioned, every entry citing its
paragraph of a process model source.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml

MAPPINGS_DIR = Path(__file__).with_name("mappings")
PROCESS_MODEL = Path(__file__).with_name("process_model.yaml")


@lru_cache(maxsize=None)
def _source_name(source_id: str) -> str:
    """'S3' -> 'CJCSM 5123.01A' (the title in process_model.yaml up to its first comma)."""
    sources = (yaml.safe_load(PROCESS_MODEL.read_text(encoding="utf-8")) or {}).get("process_model", {}).get("sources", {})
    if source_id not in sources:
        raise KeyError(f"policy mapping source '{source_id}' is not a process model source")
    return sources[source_id]["title"].split(",")[0].strip()


@lru_cache(maxsize=None)
def load_mapping(mapping_id: str) -> Dict[str, Any]:
    path = MAPPINGS_DIR / f"{mapping_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"policy mapping '{mapping_id}' not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for key in ("id", "version", "title", "source", "rules"):
        if not data.get(key):
            raise ValueError(f"policy mapping {path.name} has no '{key}'")
    if data["id"] != mapping_id:
        raise ValueError(f"policy mapping {path.name} has id '{data['id']}', expected '{mapping_id}'")
    return data


def render_mapping(mapping_id: str) -> str:
    """The mapping as prompt text: criteria, tier table and rules, each with its citation."""
    m = load_mapping(mapping_id)
    src = _source_name(m["source"])
    lines = [f"Policy mapping: {m['title']} ({m['version']}; source {src}, as of {m.get('as_of', '?')})."]
    crit = m.get("criteria")
    if crit:
        lines.append(f"{crit.get('intro', 'Criteria:')} [{src} {crit['cite']}]")
        lines += [f"  ({c['id']}) {c['text']}" for c in crit["items"]]
    tiers = m.get("tiers")
    if tiers:
        if m.get("joint_condition"):
            lines.append(f"Every tier with an ACAT level requires that the capability is {m['joint_condition']}, AND:")
        lines.append("| Designator | ACAT | Condition | Review authority | Citation |")
        lines.append("|---|---|---|---|---|")
        for t in tiers:
            lines.append(f"| {t['designator']} | {t.get('acat') or '-'} | {t['condition']} | "
                         f"{t['review_authority']} | {src} {t['cite']} |")
        lines += [f"- {t['designator']}: {t['note']}" for t in tiers if t.get("note")]
    lines.append("Rules:")
    lines += [f"- {r}" for r in m["rules"]]
    return "\n".join(lines) + "\n"
