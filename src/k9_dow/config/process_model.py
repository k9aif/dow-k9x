# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""The DAS process model: stages, gates and sources, read from process_model.yaml.

The requirements-to-acquisition process changes with policy, so DAS keeps it in a
versioned file rather than in code. Gates, orchestrators, HIL task names and the
UI read it from here. ``load_process_model`` checks the file on load: every gate
and built stage after normalization cites a source listed in the file, and a
non-blocking gate cannot gate anything.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

PROCESS_MODEL_PATH = Path(__file__).with_name("process_model.yaml")


@dataclass(frozen=True)
class Stage:
    id: str
    title: str
    kind: str  # "agents" | "gate"
    owner: str
    sources: List[str]
    summary: str = ""
    parallel: bool = False


@dataclass(frozen=True)
class Gate:
    id: str
    title: str
    owner: str
    type: str  # PREPARE_DECIDE | REVIEW_APPROVE
    authority: str
    blocking: bool
    entry_criteria: List[str]
    decision_record: str
    sources: List[str]
    evidence: List[str] = field(default_factory=list)
    criteria_note: str = ""
    prepared_by: str = ""
    approval_starts: Optional[str] = None
    hil_queue: str = ""
    hil_application: str = ""
    hil_queue_name: str = ""

    @property
    def task_topic(self) -> str:
        return f"workflow.hil.{self.hil_queue}"

    @property
    def reply_topic(self) -> str:
        return f"{self.hil_queue}.replies"


RUNS = ("requirement", "mdd_package", "msa", "tmrr")


@dataclass(frozen=True)
class ProcessModel:
    id: str
    as_of: str
    pathway: str
    pathway_title: str
    sources: Dict[str, Dict[str, Any]]
    stages: List[Stage]
    gates: Dict[str, Gate]
    designed: List[Dict[str, Any]]

    def stage(self, stage_id: str) -> Stage:
        for s in self.stages:
            if s.id == stage_id:
                return s
        raise KeyError(stage_id)

    def gate(self, gate_id: str) -> Gate:
        return self.gates[gate_id]

    def sequence(self) -> List[Stage]:
        """The main line in order; parallel stages are left out."""
        return [s for s in self.stages if not s.parallel]

    def blocking_gates(self) -> List[str]:
        return [s.id for s in self.sequence() if s.kind == "gate" and self.gates[s.id].blocking]

    def runs(self) -> List[str]:
        """Orchestrator runs in order (the keys stage results are stored under)."""
        return list(RUNS)

    def gates_prepared_by(self, run: str) -> List[Gate]:
        return [g for g in self.gates.values() if g.prepared_by == run]

    def next_stage(self, stage_id: str) -> Optional[Stage]:
        seq = self.sequence()
        ids = [s.id for s in seq]
        i = ids.index(stage_id)
        return seq[i + 1] if i + 1 < len(seq) else None


class ProcessModelError(ValueError):
    pass


OWNERS = {"intake", "requirement", "msa", "tmrr"}
GATE_TYPES = {"PREPARE_DECIDE", "REVIEW_APPROVE"}


def _source_key(citation: str) -> str:
    return citation.split()[0]


def _validate(pm: ProcessModel) -> None:
    ids = [s.id for s in pm.stages]
    if len(ids) != len(set(ids)):
        raise ProcessModelError("duplicate stage id")
    gate_stages = {s.id for s in pm.stages if s.kind == "gate"}
    if gate_stages != set(pm.gates):
        raise ProcessModelError(f"gate stages {sorted(gate_stages)} != gates {sorted(pm.gates)}")
    for s in pm.stages:
        if s.kind not in ("agents", "gate"):
            raise ProcessModelError(f"{s.id}: unknown kind {s.kind!r}")
        if s.owner not in OWNERS:
            raise ProcessModelError(f"{s.id}: unknown owner {s.owner!r}")
        # NORMALIZE and SCREEN are DAS's own input handling, not a policy step.
        if s.id not in ("NORMALIZE", "SCREEN") and not s.sources:
            raise ProcessModelError(f"{s.id}: stage cites no source")
    citations = [c for s in pm.stages for c in s.sources]
    citations += [c for g in pm.gates.values() for c in g.sources]
    citations += [c for d in pm.designed for c in d.get("sources", [])]
    for c in citations:
        if _source_key(c) not in pm.sources:
            raise ProcessModelError(f"citation {c!r} names no listed source")
    for g in pm.gates.values():
        if g.type not in GATE_TYPES:
            raise ProcessModelError(f"{g.id}: unknown gate type {g.type!r}")
        if not g.sources or not g.entry_criteria:
            raise ProcessModelError(f"{g.id}: gate needs sources and entry criteria")
        if g.prepared_by not in RUNS:
            raise ProcessModelError(f"{g.id}: prepared_by {g.prepared_by!r} is not a run {RUNS}")
        if g.approval_starts is not None and g.approval_starts not in RUNS:
            raise ProcessModelError(f"{g.id}: approval_starts {g.approval_starts!r} is not a run")
        if g.approval_starts is not None and RUNS.index(g.approval_starts) <= RUNS.index(g.prepared_by):
            raise ProcessModelError(f"{g.id}: an approval must start a later run")
        if not g.blocking and g.approval_starts is not None:
            raise ProcessModelError(f"{g.id}: a non-blocking gate starts nothing")
        if not g.hil_queue.startswith("das."):
            raise ProcessModelError(f"{g.id}: hil_queue must start with 'das.'")
        parallel = pm.stage(g.id).parallel
        if parallel and g.blocking:
            raise ProcessModelError(f"{g.id}: a parallel gate cannot block")
        if not g.blocking and not parallel:
            raise ProcessModelError(f"{g.id}: a non-blocking gate must run in parallel")


def parse_process_model(data: Dict[str, Any]) -> ProcessModel:
    raw = data["process_model"]
    stages = [
        Stage(
            id=s["id"], title=s["title"], kind=s["kind"], owner=s.get("owner", ""),
            sources=list(s.get("sources") or []),
            summary=s.get("summary", ""), parallel=bool(s.get("parallel", False)),
        )
        for s in raw["stages"]
    ]
    titles = {s.id: s for s in stages}
    gates = {
        gid: Gate(
            id=gid, title=titles[gid].title if gid in titles else gid,
            owner=titles[gid].owner if gid in titles else "",
            type=g.get("type", "PREPARE_DECIDE"),
            authority=g["authority"], blocking=bool(g["blocking"]),
            entry_criteria=list(g["entry_criteria"]), decision_record=g["decision_record"],
            sources=list(g["sources"]), evidence=list(g.get("evidence") or []),
            criteria_note=g.get("criteria_note", ""),
            prepared_by=g.get("prepared_by", ""), approval_starts=g.get("approval_starts"),
            hil_queue=g.get("hil_queue", ""),
            hil_application=g.get("hil_application", ""), hil_queue_name=g.get("hil_queue_name", ""),
        )
        for gid, g in raw["gates"].items()
    }
    pm = ProcessModel(
        id=raw["id"], as_of=str(raw["as_of"]), pathway=raw["pathway"],
        pathway_title=raw["pathway_title"], sources=dict(raw["sources"]),
        stages=stages, gates=gates, designed=list(raw.get("designed") or []),
    )
    _validate(pm)
    return pm


@lru_cache(maxsize=4)
def load_process_model(path: str = str(PROCESS_MODEL_PATH)) -> ProcessModel:
    with open(path, "r", encoding="utf-8") as f:
        return parse_process_model(yaml.safe_load(f))
