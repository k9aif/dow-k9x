# SPDX-License-Identifier: Apache-2.0
"""ViewGeneratorAgent records what retrieval contributed (v1.3.7): used with N passages, or unavailable with
the reason, in its output -- not only in a log line. Before 1.3.7 the hosted image lacked the `ollama`
package, retrieval fell back silently and no job record showed it."""
from types import SimpleNamespace

from k9_dow.agents.src.view_generator_agent import ViewGeneratorAgent


class _Retriever:
    def __init__(self, available, chunks):
        self._vectordb_available = available
        self._chunks = chunks

    def retrieve(self, **kwargs):
        return list(self._chunks)


def _agent(retriever, error=""):
    a = ViewGeneratorAgent.__new__(ViewGeneratorAgent)          # no governance/model needed for this unit
    a.config, a.layer = {}, "DAS ViewGenerator"
    a._retriever, a._retriever_error = retriever, error
    a._retrieval = {"status": "not_run", "passages": 0, "sources": []}
    return a


def _ctx():
    return SimpleNamespace(payload={"view_type": "OV-1", "source_markdown": "Program X needs Y."}, iteration=1)


def test_used_passages_are_recorded_and_labelled_as_guidance():
    chunks = [{"text": "guidance A", "source": "dodaf_guide.md"}, {"text": "precedent B", "source": "prior_cdd.md"}]
    a = _agent(_Retriever(True, chunks))
    h = a.generate_hypothesis(_ctx())
    assert a._retrieval == {"status": "used", "passages": 2, "sources": ["dodaf_guide.md", "prior_cdd.md"]}
    assert "Supplementary reference material" in h["context"] and "guidance A" in h["context"]


def test_unavailable_vector_store_is_recorded_not_hidden():
    a = _agent(_Retriever(False, []))
    h = a.generate_hypothesis(_ctx())
    assert a._retrieval["status"] == "unavailable" and a._retrieval["passages"] == 0
    assert "Supplementary reference material" not in h["context"]


def test_missing_retriever_is_recorded_with_reason():
    a = _agent(None, error="RuntimeError: pip install ollama required")
    a._get_retriever = lambda: None
    a.generate_hypothesis(_ctx())
    assert a._retrieval["status"] == "unavailable" and "ollama" in a._retrieval["reason"]
