# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""A loop agent's failed model call reaches the squad (and so the stage's retry),
instead of being carried on as the agent's output."""

import os

import pytest

os.environ.setdefault("K9_ENV", "test")

from k9_aif_abb.k9_squad.base_squad import BaseSquad  # noqa: E402

from k9_dow.agents.src import drift_classifier_agent, link_proposer_agent, view_generator_agent  # noqa: E402

LOOP_AGENTS = [(view_generator_agent, "ViewGeneratorAgent"),
               (link_proposer_agent, "LinkProposerAgent"),
               (drift_classifier_agent, "DriftClassifierAgent")]


def _down(*_a, **_k):
    raise RuntimeError("LLM backend unavailable (agent=test) after 3 attempt(s)")


@pytest.mark.parametrize("module,cls", LOOP_AGENTS)
def test_failed_model_call_raises_out_of_the_loop_agent(monkeypatch, module, cls):
    monkeypatch.setattr(module, "llm_invoke", _down)
    agent = getattr(module, cls)(config={"max_iterations": 3})
    with pytest.raises(RuntimeError, match="LLM backend unavailable"):
        agent.execute({"source_markdown": "# CDD\nKPP 1", "prior_outputs": {}, "job_id": "JOB-T"})


def test_the_squad_stops_and_passes_it_up(monkeypatch):
    """The real ViewGenerationSquad: extractor succeeds, the view generator's model call
    fails; the squad raises and the consistency checker never runs on a missing view."""
    from types import SimpleNamespace
    from pathlib import Path
    import k9_dow
    from k9_dow.agents.src import model_extractor_agent, view_consistency_checker_agent
    from k9_dow.squads.das_squad import squad_layer

    ran = []
    monkeypatch.setattr(model_extractor_agent, "llm_invoke",
                        lambda *_a, **_k: SimpleNamespace(output="CAP-001 Mobility", model_alias="t"))
    monkeypatch.setattr(view_generator_agent, "llm_invoke", _down)
    monkeypatch.setattr(view_consistency_checker_agent, "llm_invoke",
                        lambda *_a, **_k: ran.append(1) or SimpleNamespace(output="ok", model_alias="t"))
    squads_dir = Path(k9_dow.__file__).parent / "squads" / "yaml"
    squad = squad_layer({}).load_one(squads_dir / "view_generation_squad.yaml", "ViewGenerationSquad")
    with pytest.raises(RuntimeError, match="DAS ViewGenerator"):
        squad.execute({"source_markdown": "# CDD\nKPP 1", "prior_outputs": {}, "job_id": "JOB-T"})
    assert ran == []
