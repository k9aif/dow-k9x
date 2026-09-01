"""
Context-enrichment scaling measurement for the IEEE Access
resubmission's Sec. VII-G, quantifying the qualitative claim that
DAS's current squad depth and output verbosity keep accumulated
context well inside any modern model's context window.

Computes cumulative context size, using tiktoken's cl100k_base
encoding, across the ten real agent-output fields recorded in a real
DAS run (output_samples/sample_result.json), in the order those ten
agents actually execute across the three JCIDS squads in sequence
(ViewGenerationSquad -> GateReadinessSquad -> PackageAssemblySquad;
the JCIDS orchestrator passes each squad's full result into the next
as prior_outputs, so context accumulates across squad boundaries, not
just within one squad's own flow -- see JcidsOrchestrator.execute_flow()).

Also extrapolates the observed mean per-agent token growth linearly to
estimate the squad depth at which accumulated context alone would
reach common context-window budgets (8,192 / 32,768 / 131,072 tokens).
This extrapolation is a stated assumption, not a measurement: it holds
output length per agent constant and only varies step count. Testing
it against a real, deeper squad is future work (no such squad exists
in either reference deployment yet).

Run: python experiments/context_scaling.py
"""
import json
from pathlib import Path

import tiktoken

SAMPLE_PATH = Path(__file__).resolve().parent.parent / \
    "src/k9_dow/api/static/demos/output_samples/sample_result.json"

# Real execution order: ViewGenerationSquad (3 agents), then
# GateReadinessSquad (4 agents, receiving ViewGeneration's full result
# as prior_outputs), then PackageAssemblySquad (3 agents, receiving
# both prior squads' merged results).
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
    enc = tiktoken.get_encoding("cl100k_base")
    with open(SAMPLE_PATH) as f:
        result = json.load(f)["result"]

    cumulative_text = ""
    rows = []
    for i, (section, key) in enumerate(AGENT_ORDER, 1):
        text = str(result[section][key])
        own_tokens = len(enc.encode(text))
        cumulative_text += text
        cum_tokens = len(enc.encode(cumulative_text))
        rows.append((i, f"{section}.{key}", own_tokens, cum_tokens))

    print(f"{'Step':>4}  {'Squad.Agent Output':<38} {'Own Tokens':>10} {'Cumulative Tokens':>18}")
    for i, name, own, cum in rows:
        print(f"{i:>4}  {name:<38} {own:>10} {cum:>18}")

    final_tokens = rows[-1][3]
    mean_growth = final_tokens / len(rows)
    print(f"\nFinal cumulative context: {final_tokens} tokens "
          f"({len(cumulative_text)} characters) across {len(rows)} agents.")
    print(f"Mean marginal growth per agent: {mean_growth:.1f} tokens.")

    print("\nLinear extrapolation to common context-window budgets "
          "(assumes constant per-agent output length -- a stated "
          "assumption, not a measurement):")
    for budget in CONTEXT_WINDOW_BUDGETS:
        agents_needed = budget / mean_growth
        print(f"  {budget:>7,} tokens: ~{agents_needed:.0f} sequential agents")


if __name__ == "__main__":
    main()
