# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""OLLAMA_NUM_CTX (.env) reaches every agent model alias as a number."""

import importlib


def test_num_ctx_from_env_applies_to_agent_aliases_only(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "qwen3.8:27b")
    monkeypatch.setenv("OLLAMA_NUM_CTX", "65536")
    from k9_dow.config import settings as settings_mod
    importlib.reload(settings_mod)
    from k9_dow.config import runtime
    importlib.reload(runtime)
    cfg = {"inference": {"llm_factory": {"models": {
        "general": {"model": "qwen3.8:27b"},
        "package_synthesis": {"model": "qwen3.8:27b", "num_ctx": 16384},
        "judge": {"model": "deepseek-r1:32b", "num_ctx": 32768},
    }}}}
    m = runtime.apply_runtime_settings(cfg)["inference"]["llm_factory"]["models"]
    assert m["general"]["num_ctx"] == 65536 and m["package_synthesis"]["num_ctx"] == 65536
    assert isinstance(m["general"]["num_ctx"], int)
    assert m["judge"]["num_ctx"] == 32768          # the grader is another model: untouched
