# Fixes from the FIREBIRD package review: handled

**Status: fixed.** Every defect found in the 2026-10-10 review of the FIREBIRD MDD, Milestone A and SRR
packages is fixed in the code DAS runs today (commit `fafb4cc`, 2026-10-10), with tests where the fix is
code rather than wording. The live site at das.k9x.ai runs a build that includes these fixes; the
FIREBIRD run of 2026-10-15
([`firebird_2026-10-15_JOB-20261015-1108EA/`](firebird_2026-10-15_JOB-20261015-1108EA/)) came from it.

The drafts in [`writers_firebird_2026-10-09/`](writers_firebird_2026-10-09/) were recorded before the fix
and are kept unchanged as the "before" record.

## What was found and how it was fixed

| # | Found in review | Fix | Checked by |
|---|---|---|---|
| 1 | An MDAP dollar threshold ($750M) stated and attributed to "DoDI 5000.01" | Writers are told never to state or estimate MDAP thresholds or cite an issuance for them (`agents/src/process_facts.py`) | `test_process_facts_state_mdap_and_statute` |
| 2 | The Major Capability Acquisition pathway treated as if every program on it were an MDAP | A program is an MDAP only if its ACAT makes it one; with no ACAT in the source, DAS says so. Milestone A's MDAP items apply to ACAT I only (`process_facts.py`, `process_model.yaml`) | `test_process_facts_state_mdap_and_statute` |
| 3 | 10 U.S.C. 2366a cited | Cited as 10 U.S.C. 4251 (formerly 2366a) (`process_facts.py`, `process_model.yaml`) | `test_process_facts_state_mdap_and_statute` |
| 4 | Alternative Systems Review draft cut off mid-sentence | Package writers moved to the `package_synthesis` model profile, which allows 8,192 output tokens (`config.yaml`, writer agent YAMLs) | Configuration |
| 5 | Log lines ("Loaded N criteria", "Fetched N artifacts") appeared as package sections | The package lists the criteria and shows an artifact table instead (`criteria_loader_agent.py`, `artifact_fetcher_agent.py`) | `test_criteria_loader_lists_the_criteria_not_a_count` |
| 6 | Scorer instruction text leaked into the package | Agents instructed to write only the assessment, never their instructions or role (agent YAMLs) | Instruction |
| 7 | Unbalanced bold markup | Unclosed bold is closed when the package is composed (`utils/icd_composer.py`) | `test_package_closes_an_unclosed_bold` |
| 8 | SRR described as "entering TMRR" | Process facts state that the SRR takes place during TMRR, after Milestone A (`process_facts.py`) | Process facts |
| 9 | SRR package cited only the Service validation decision | Every gate's package cites every decision recorded for the job so far, in process order: Service validation, JCI review, MDD, Milestone A (`orchestrators/stage_base.py`) | `test_srr_sees_every_earlier_decision` |

Test run, 2026-10-29: `pytest tests/test_hil_round_trip.py -k "criteria_loader_lists or unclosed_bold or process_facts_state or srr_sees"`, **4 passed**.

## Next

A fresh FIREBIRD run through MDD, Milestone A and the SRR, saved here beside the "before" drafts, will
show the fixed packages end to end.
