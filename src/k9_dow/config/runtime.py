# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""Deployment settings applied to the loaded config.yaml.

``num_ctx`` comes from ``OLLAMA_NUM_CTX`` (.env) and is written as a number
into every agent model alias -- those using the agents' model, not the grader
or Guardian -- so the window is a deployment choice, one value for all steps.
"""

from __future__ import annotations

from typing import Any, Dict

from k9_dow.config.settings import settings


def apply_runtime_settings(config: Dict[str, Any]) -> Dict[str, Any]:
    models = ((config.get("inference") or {}).get("llm_factory") or {}).get("models") or {}
    for alias in models.values():
        if isinstance(alias, dict) and alias.get("model") == settings.OLLAMA_MODEL:
            alias["num_ctx"] = settings.OLLAMA_NUM_CTX
    return config
