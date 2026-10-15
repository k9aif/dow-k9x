
# K9-AIF Compliance Report

- **Source:** https://github.com/k9aif/dow-k9x/tree/main/src/k9_dow @ `4619b854bc08`
- **Inspected:** 2026-10-15T00:20:11+00:00 with k9-aif 1.15.0
- **Files:** 100 Python, 34 YAML
- **Framework:** declares `k9-aif[s3,docling]==1.15.3` (../../requirements.txt:2), latest k9-aif 1.18.1 — OUTDATED — update to the latest
- **Verdict:** COMPLIANT WITH WARNINGS — 82% of 28 rules pass
- **Findings:** 0 critical, 0 violations, 20 warnings, 2 recommendations

## WARNING (20)

- **K9-DEP-002** [Dependencies] `../../requirements.txt:2` — pins k9-aif k9-aif[s3,docling]==1.15.3 — latest is 1.18.1
  - Fix: Update the requirement to the latest k9-aif (e.g. k9-aif>=1.18.1), rebuild and re-run the tests.
- **K9-LLM-002** [LLM path] `agents/src/baseline_differ_agent.py:37` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/completeness_checker_agent.py:43` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/coverage_scorer_agent.py:38` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/drift_classifier_agent.py:57` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/evidence_collector_agent.py:41` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/funding_differ_agent.py:36` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/gap_reporter_agent.py:42` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/link_proposer_agent.py:75` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/link_validator_agent.py:38` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/model_extractor_agent.py:40` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/orphan_detector_agent.py:36` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/package_builder_agent.py:48` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/readiness_scorer_agent.py:48` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/section_writer.py:114` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/view_consistency_checker_agent.py:42` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-002** [LLM path] `agents/src/view_generator_agent.py:108` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.
- **K9-LLM-001** [LLM path] `api/app.py:603` — calls a model HTTP endpoint directly (acceptable for health checks / warm-up, not for inference)
  - Fix: Replace with: from k9_aif_abb.k9_utils.llm_invoke import llm_invoke; llm_invoke(self.config, InferenceRequest(prompt=..., task_type=...)).
- **K9-LLM-001** [LLM path] `api/app.py:1089` — calls a model HTTP endpoint directly (acceptable for health checks / warm-up, not for inference)
  - Fix: Replace with: from k9_aif_abb.k9_utils.llm_invoke import llm_invoke; llm_invoke(self.config, InferenceRequest(prompt=..., task_type=...)).
- **K9-LLM-002** [LLM path] `quality/icd_grader.py:129` — llm_invoke() not inside try/except
  - Fix: Wrap the call: try: ... except RuntimeError as exc: return a failed result with the reason.

## RECOMMENDATION (2)

- **K9-GOV-006** [Governance] `config/config.yaml:154` — egress does not run OutboundLinkCheck
  - Fix: Add PIIBoundaryCheck and OutboundLinkCheck (with allowed_domains) to security.shield.egress.checks.
- **K9-GOV-011** [Zero Trust]  — Zero Trust is not enabled (enable_zero_trust)
  - Fix: Set enable_zero_trust: true and security.identity.mode: signed (K9_IDENTITY_SECRET in .env).

## Rules

| Rule                                                            | Category         | Severity       | Result        |
| --------------------------------------------------------------- | ---------------- | -------------- | ------------- |
| K9-CFG-001 No hardcoded private IP addresses                    | Configuration    | violation      | pass          |
| K9-CFG-002 No secrets in YAML                                   | Secrets          | critical       | pass          |
| K9-CFG-003 .env is not committed                                | Secrets          | critical       | pass          |
| K9-CFG-004 Agent model aliases exist in the model catalog       | Configuration    | warning        | pass          |
| K9-CON-001 Agents extend a K9-AIF agent ABB                     | ABB contract     | violation      | pass          |
| K9-CON-002 Loop agents implement the loop hooks, not execute()  | ABB contract     | violation      | pass          |
| K9-DEC-001 Three-layer decoupling                               | Decoupling       | violation      | pass          |
| K9-DEP-001 Depends on k9-aif with governance by construction    | Dependencies     | warning        | pass          |
| K9-DEP-002 Runs the latest k9-aif                               | Dependencies     | warning        | 1 finding(s)  |
| K9-GOV-001 Shield governance is enabled                         | Governance       | violation      | pass          |
| K9-GOV-002 Shield has ingress and egress checks                 | Governance       | violation      | pass          |
| K9-GOV-003 No NoopGovernance outside tests                      | Governance       | warning        | pass          |
| K9-GOV-004 Granite Guardian (semantic screening) is configured  | Governance       | warning        | pass          |
| K9-GOV-005 Deployments run with K9_ENV=production               | Governance       | warning        | pass          |
| K9-GOV-006 Egress screens personal data and links               | Governance       | recommendation | 1 finding(s)  |
| K9-GOV-007 No agent opts out of the governance wrapper          | Governance       | critical       | pass          |
| K9-GOV-008 Orchestrators screen their own ingress               | Governance       | warning        | pass          |
| K9-GOV-009 Pre-1.15 agents call the governance hooks themselves | Governance       | violation      | pass          |
| K9-GOV-010 Guardian fails closed                                | Governance       | warning        | pass          |
| K9-GOV-011 Zero Trust enabled with signed identity              | Zero Trust       | recommendation | 1 finding(s)  |
| K9-KAF-001 Only Router and Orchestrator touch Kafka             | Kafka ownership  | violation      | pass          |
| K9-LLM-001 Model calls go through llm_invoke()                  | LLM path         | critical       | 2 finding(s)  |
| K9-LLM-002 llm_invoke() failures are handled                    | LLM path         | warning        | 17 finding(s) |
| K9-LLM-003 InferenceRequest names a task_type                   | LLM path         | recommendation | pass          |
| K9-PAT-001 Hand-written model loops use a loop ABB              | Patterns         | recommendation | pass          |
| K9-SYN-001 All Python files parse                               | Code             | violation      | pass          |
| K9-YAML-001 Squad YAML structure                                | Squad/Agent YAML | violation      | pass          |
| K9-YAML-002 Agent YAML does not name its squad or routing       | Squad/Agent YAML | violation      | pass          |
