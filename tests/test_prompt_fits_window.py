# SPDX-License-Identifier: Apache-2.0
"""v1.3.8: agents send the previous stage's outputs, not whole loop records, and a prompt that would not fit
the model window is refused instead of truncated. Found on a real CDD (private run, DAS 1.3.7): the package
builder's prior_outputs came to 38,054 tokens against a 32,768-token window; Ollama dropped the oldest part
without an error. The outputs alone were 13,693 tokens."""
import pytest

from k9_dow.agents.src.squad_context import assert_fits_window, prior_text


def _loop_result(text):
    # what a validation-loop agent returns: the output plus every iteration and its evidence
    return {"agent": "DAS ViewGenerator", "output": text, "steps": [{"observation": text * 3}] * 3,
            "evidence": [text * 3] * 3}


def test_prior_text_keeps_outputs_and_drops_loop_records():
    prior = {"status": "completed", "squad_id": "ViewGenerationSquad",
             "generated_views": _loop_result("OV-1 view text. " * 200), "criteria": {"output": "C1; C2"}}
    text = prior_text(prior)
    assert "OV-1 view text." in text and "### criteria\nC1; C2" in text
    assert len(text) < len(str(prior)) / 5
    assert "squad_id" not in text


def test_a_prompt_over_the_window_is_refused(monkeypatch):
    monkeypatch.setenv("OLLAMA_NUM_CTX", "32768")
    assert_fits_window("x" * 50_000, "DAS PackageBuilder")               # ~16.7k tokens: fits
    with pytest.raises(RuntimeError, match="does not fit"):
        assert_fits_window("x" * 152_000, "DAS PackageBuilder")          # the 38k-token CDD case
