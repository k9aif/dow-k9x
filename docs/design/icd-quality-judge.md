# ICD Quality Judge (design)

Status: designed 2026-10-02; **built 2026-10-03** as `src/k9_dow/quality/icd_grader.py`. Example output:
`docs/process-model-2026/evidence/firebird_2026-10-15_JOB-20261015-1108EA/JOB-20261015-1108EA-ICD-Quality.md`.

## As built (updated 2026-10-29)

The build kept the three scores and the independent judge model, and simplified how grading is run.
Where this section and the original design below differ, this section and the code are current.

| | Original design (below) | As built |
|---|---|---|
| When it runs | Automatically, as the last step of the stage, before the HIL task is sent | **On demand:** a signed-in user clicks the grader in the Generated Docs panel (`POST /jobs/{job_id}/grade`); it runs in the background and takes about a minute |
| Score in the HIL task | Yes (`quality.*` payload fields) | No. The report is a job document beside the package: `<job>-ICD-Quality.md` |
| Implementation | `QualityJudgeSquad` with four agents | A plain module, `quality/icd_grader.py`, called by the API (`_grade_job` in `api/app.py`) |
| Faithfulness | Claims extracted from the ICD | The package's typed model elements (capability needs, SE requirements, baseline items), each judged supported / unsupported / contradicted by the `judge` model alias |
| Completeness, citation accuracy | Code and model | **Code only:** required sections present; verbatim quotes of 20+ characters found in the source (architecture views only) |
| Overall score | Not specified | Mean of the three. When the judge model is down, citation and completeness are kept and faithfulness is reported as "not evaluated", with no overall score |
| Judge model | `deepseek-r1:32b` | Same default, set by `GRADER_MODEL`. The judge is loaded for the run and the generator model reloaded afterwards (one GPU) |
| Stored | `jcids-output/by-job/<job>/quality-jcids.json` | Stage result `quality-jcids` for the job (same by-job storage) |

The terms below (JCIDS, ICD, JROC gate) come from the JCIDS-era flow. Under process model `mca-2026-10`
the graded document is the Service requirement package, and the review it supports is Service
Requirements Validation.

## Original design (2026-10-02)

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
