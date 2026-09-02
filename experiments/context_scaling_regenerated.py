"""
Recomputes the context-enrichment token-growth measurement (Sec. VII-G,
Table 11) from context_sample_regenerated.json -- a freshly generated,
self-documenting run (real qwen2.5:32b inference, commit SHA, UTC
timestamp, full invocation all recorded in that file) -- rather than the
original output_samples/sample_result.json, which carries no model
attribution at all.

Uses the exact same tiktoken cl100k_base encoding and cumulative-growth
method as context_scaling.py. cl100k_base is a fixed tokenizer choice,
independent of which model generated the text being counted -- the same
encoding is used here as before, only the input text differs (freshly
generated vs. the original, unattributed sample).

Run: python3 experiments/context_scaling_regenerated.py
"""
import json
from pathlib import Path

import tiktoken

REGEN_PATH = Path(__file__).resolve().parent / "context_sample_regenerated.json"
OUT_PATH = Path(__file__).resolve().parent / "context_scaling_regenerated_counts.json"

AGENT_ORDER = [
    ("view_generation", "model_elements"),
    ("view_generation", "generated_views"),
    ("view_generation", "consistency_report"),
    ("gate_readiness", "criteria"),
    ("gate_readiness", "evidence"),
    ("gate_readiness", "readiness_score"),
    ("gate_readiness", "gap_report"),
    ("review_package", "artifact_manifest"),
    ("review_package", "completeness_check"),
    ("review_package", "review_package"),
]

CONTEXT_WINDOW_BUDGETS = [8_192, 32_768, 131_072]


def main():
    with open(REGEN_PATH) as f:
        artifact = json.load(f)
    result = artifact["result"]

    enc = tiktoken.get_encoding("cl100k_base")
    cumulative_text = ""
    rows = []
    for i, (section, key) in enumerate(AGENT_ORDER, 1):
        text = str(result[section][key])
        own_tokens = len(enc.encode(text))
        cumulative_text += text
        cum_tokens = len(enc.encode(cumulative_text))
        rows.append({"step": i, "agent_output": f"{section}.{key}",
                      "own_tokens": own_tokens, "cumulative_tokens": cum_tokens})
        print(f"{i:>4}  {section}.{key:<25} {own_tokens:>10} {cum_tokens:>18}")

    final_tokens = rows[-1]["cumulative_tokens"]
    mean_growth = final_tokens / len(rows)
    print(f"\nFinal cumulative context: {final_tokens} tokens across {len(rows)} agents.")
    print(f"Mean marginal growth per agent: {mean_growth:.1f} tokens.")

    extrapolation = {}
    for budget in CONTEXT_WINDOW_BUDGETS:
        n_agents = budget / mean_growth
        extrapolation[str(budget)] = round(n_agents)
        print(f"  {budget:,} tokens: ~{round(n_agents)} sequential agents")

    out = {
        "source_artifact": str(REGEN_PATH.name),
        "source_commit_sha": artifact["commit_sha"],
        "source_generated_at_utc": artifact["generated_at_utc"],
        "source_model": artifact["config_resolved"]["general_model"],
        "encoding": "tiktoken cl100k_base",
        "rows": rows,
        "final_cumulative_tokens": final_tokens,
        "mean_marginal_growth_per_agent": round(mean_growth, 1),
        "extrapolation_agents_at_budget": extrapolation,
        "comparison_to_manuscript": {
            "manuscript_final_cumulative_tokens": 2713,
            "manuscript_mean_marginal_growth": 271.3,
        },
    }
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
