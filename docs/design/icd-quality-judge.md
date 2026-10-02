# ICD Quality Judge (design, not built)

Status: **designed 2026-10-02, planned for the IBM demo week (after the IEEE v8 upload)**.
Not part of DAS v1.2.x.

## Purpose

Before a human reviews the ICD at the JROC gate (flow step 2), DAS grades the
generated ICD against the submitted source document and shows the result in
the review task, so the reviewer starts from evidence of what to check.

## Who runs it

DAS, as the last step of the JCIDS stage (flow step 1), after the ICD is
assembled and **before** the JROC HIL task is published. It has to finish
first: K9X HIL stores a task's payload when the task arrives and cannot update
it afterwards, so the score must be in the task when it is sent.

```
JCIDS squads ─▶ ICD assembled ─▶ Quality Judge squad ─▶ score saved with the job
                                                     └▶ JROC HIL task (payload carries the score)
```

The same pattern can follow Acquisition (step 4) for the Milestone package.

## Scores

| Score | How |
|---|---|
| Faithfulness | Extract factual claims from the ICD (capabilities, performance values, stakeholders, systems); for each, find support in the source: supported / unsupported / contradicted. Score = supported ÷ all, with the unsupported and contradicted claims listed. |
| Completeness | Required ICD sections and DoDAF views present, or marked `NOT PROVIDED IN SOURCE` (the agents' own grounding rule). |
| Citation accuracy | Each verbatim evidence quote in the ICD appears in the source (string match first, model only for near-matches). |

Claim-by-claim in small batches, so every number is traceable to listed
claims, not a single opaque overall grade.

## Judge model

`deepseek-r1:32b` (Ollama alias, e.g. `judge`), a different model family from
the generator (`qwen3.8:27b`), so the model does not grade its own work.
Practical limits on the single RTX 5090 (32 GB): qwen3.8:27b (~17 GB) and
deepseek-r1:32b (~19 GB) do not fit together, so Ollama swaps models for each
grading run; grading runs after the stage's own model calls. R1 reasons at
length: batch size and a timeout bound the run time.

## Where it is shown

1. **K9X HIL task** (JROC Review): payload fields `quality.faithfulness`,
   `quality.unsupported_claims` (count + first few), `quality.report_url`.
2. **Jobs in Pipeline**: a score chip on the JCIDS step; **View quality report**
   next to View ICD.
3. Stored with the job: `jcids-output/by-job/<job>/quality-jcids.json`.

## Building blocks

- `QualityJudgeSquad` (squad YAML): ClaimExtractorAgent → ClaimVerifierAgent →
  CompletenessCheckerAgent (reuse) → QualityReporterAgent; all `BaseAgent`
  SBBs calling `llm_invoke` with the judge alias.
- Context enrichment as in the other squads (each step reads the previous
  step's result key).

## Caveats

- An LLM judge needs calibration against human judgment before its scores
  are used as evidence (e.g. in a paper). In the demo it is an aid to the
  reviewer, labelled as such, not a verdict.
- Synthetic input documents: scores describe agreement with the source, not
  real-world correctness.
