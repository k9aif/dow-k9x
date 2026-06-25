# K9-AIF Implementation Specification — DoW / DoDAF / JCIDS Architecture Workbench

## 1. Purpose

Create a complete K9-AIF-native implementation of the uploaded DoW architecture workbench. The target system must be implemented using K9-AIF framework concepts only: routers, orchestrators, squads, agents, validation loops, governance gates, persistence adapters, monitoring events, registries, model adapters, and connector adapters.

The generated code must not depend on or wrap any non-K9 orchestration framework. The old implementation should be treated only as a functional reference for business behavior, stage sequencing, agent responsibilities, and output artifacts.

## 2. Target Outcome

Claude Code must generate a clean Python application that:

1. Accepts uploaded source documents such as Markdown, TXT, PDF, DOCX, PPTX, spreadsheets, meeting notes, call reports, CONOPS, whitepapers, requirements dumps, RFI/RFP documents, and architecture material.
2. Normalizes documents into Markdown/text with metadata.
3. Routes the document into the correct analysis pipeline.
4. Executes a governed K9-AIF squad-based architecture process.
5. Produces DoDAF, JCIDS, systems-engineering, or business-development artifacts depending on routing outcome.
6. Persists job metadata, stage outputs, extracted entities, traceability, and generated reports.
7. Publishes lifecycle and monitoring events.
8. Provides an API for upload, job execution, status, report retrieval, and runtime health.
9. Supports local LLM execution through K9-AIF inference adapters, with pluggable support for enterprise LLM providers.
10. Uses K9-AIF governance controls to prevent unsupported invention, enforce evidence grounding, and capture audit events.

## 3. Architectural Principle

This is not a one-to-one code conversion. Build a clean K9-AIF implementation using these mappings:

| Current Concept | K9-AIF Target Concept |
|---|---|
| Document router | `BaseRouter` implementation |
| Pipeline controller | `BaseOrchestrator` implementation |
| Stage group | K9 Squad |
| Worker role | `BaseAgent` implementation |
| YAML stage/task config | K9-AIF squad/agent registry config |
| LLM call utility | `LLMFactory` / model adapter |
| Message bus producer/consumer | K9 connector / stream adapter |
| Persistence utility | K9 persistence adapter |
| UI console stream | K9 monitoring event stream |
| Stage verification | K9 validation loop / governance gate |
| Report generator | K9 reporting/presentation agent |

## 4. System Name

Use this working package name:

```text
k9_dow_architecture_workbench
```

Top-level runnable service name:

```text
dow_k9_service
```

CLI entrypoint:

```text
k9-dow
```

## 5. Required Repository Structure

Claude Code must generate this structure:

```text
k9_dow_architecture_workbench/
  README.md
  pyproject.toml
  .env.example
  src/
    k9_dow/
      __init__.py
      main.py
      api/
        __init__.py
        app.py
        routes_jobs.py
        routes_reports.py
        routes_health.py
        schemas.py
      config/
        __init__.py
        settings.py
        routing_rules.yaml
        stage_catalog.yaml
        agent_catalog.yaml
        prompts/
          common_grounding_rules.md
          governance_rules.md
      contracts/
        __init__.py
        events.py
        payloads.py
        artifacts.py
        stage_results.py
      routers/
        __init__.py
        dow_document_router.py
      orchestrators/
        __init__.py
        principal_orchestrator.py
        dodaf_orchestrator.py
        jcids_orchestrator.py
        se_orchestrator.py
        business_orchestrator.py
      squads/
        __init__.py
        base_stage_squad.py
        stage0_routing_squad.py
        stage1_fit_for_purpose_squad.py
        stage2_scope_icd_squad.py
        stage3_data_requirements_squad.py
        stage4_architecture_correlation_squad.py
        stage5_architecture_analysis_squad.py
        stage6_presentation_squad.py
        jcids_capability_validation_squad.py
        jcids_requirements_expansion_squad.py
        jcids_aoa_inputs_squad.py
        jcids_dotmlpfp_squad.py
        jcids_risk_acquisition_squad.py
        jcids_summary_squad.py
        business_intake_squad.py
      agents/
        __init__.py
        base_dow_agent.py
        document_normalization_agent.py
        routing_classifier_agent.py
        validation_agent.py
        governance_agent.py
        mission_assessment_agent.py
        stakeholder_extractor_agent.py
        pain_point_extractor_agent.py
        objective_extractor_agent.py
        f2p_intent_agent.py
        project_scope_agent.py
        constraint_agent.py
        operational_extractor_agent.py
        capability_extractor_agent.py
        risk_extractor_agent.py
        vocabulary_agent.py
        data_requirements_agent.py
        dm2_extractor_agent.py
        system_service_extractor_agent.py
        system_view_agent.py
        services_view_agent.py
        data_correlation_agent.py
        architecture_analyzer_agent.py
        capability_analyzer_agent.py
        operational_analyzer_agent.py
        requirement_agent.py
        verification_agent.py
        action_item_agent.py
        summarizer_agent.py
        presentation_agent.py
        report_writer_agent.py
        jcids_capability_validator_agent.py
        jcids_kpp_agent.py
        jcids_ksa_agent.py
        jcids_kur_agent.py
        jcids_aoa_agent.py
        jcids_dotmlpfp_agent.py
        jcids_risk_matrix_agent.py
        jcids_acquisition_pathway_agent.py
        business_opportunity_agent.py
        business_contracting_agent.py
      persistence/
        __init__.py
        persistence_factory.py
        postgres_repository.py
        graph_repository.py
        object_store_repository.py
        file_repository.py
      retrieval/
        __init__.py
        dow_retriever.py
        retrieval_context.py
        retrieval_policy.py
        metadata_normalizer.py
        chunking.py
        provenance.py
        knowledge_fusion.py
        vector_store_factory.py
        chroma_adapter.py
        milvus_adapter.py
        catalog_adapter.py
        null_retriever.py
      messaging/
        __init__.py
        event_publisher.py
        kafka_event_publisher.py
        in_memory_event_publisher.py
      reporting/
        __init__.py
        markdown_report_builder.py
        docx_report_builder.py
        artifact_index_builder.py
      monitoring/
        __init__.py
        k9_event_monitor.py
      utils/
        __init__.py
        file_utils.py
        markdown_utils.py
        ids.py
        time_utils.py
  tests/
    test_router.py
    test_stage1_squad.py
    test_dodaf_orchestrator.py
    test_jcids_orchestrator.py
    test_governance_rules.py
    test_api_upload.py
```

## 6. Runtime Story

### 6.1 User Story

A user uploads a source document into the architecture workbench. The system validates the file, converts it into normalized Markdown/text, classifies the document, routes it into the correct governed pipeline, runs the required analysis stages, validates each output against evidence-grounding rules, persists artifacts, and returns a job identifier. The user can inspect live progress, retrieve stage outputs, and download final Markdown/DOCX report packages.

### 6.2 Main End-to-End Flow

```text
Document Upload
  -> DocumentNormalizationAgent
  -> DowDocumentRouter
  -> PrincipalOrchestrator
  -> Selected pipeline orchestrator
  -> Stage squads
  -> Governance gates after every stage
  -> Persistence and event publication
  -> Report package generation
  -> API response and downloadable artifacts
```

### 6.3 High-Level Pipeline Routing

The router must classify each input into one of these routes:

| Route | Classification | Purpose |
|---|---|---|
| `business_pipeline` | BD | Call reports, meeting notes, engagement summaries, contracting discussions, HR/workforce modernization, capture notes |
| `dodaf_pipeline` | DODAF | Mission, architecture, capability, operational, system, data-flow, interface, CONOPS, DoDAF seed documents |
| `jcids_pipeline` | JCIDS | ICD, CDD, KPP, KSA, KUR, mission need, capability gap, DOTMLPF-P, JCIDS requirements |
| `se_pipeline` | SE | Systems engineering, functional analysis, design synthesis, verification, validation, specifications, interface documents |
| `unknown_pipeline` | UNKNOWN | Fallback route with safe minimal summary and manual review recommendation |

Routing must be deterministic first, then LLM-assisted only when deterministic classification is ambiguous.

## 7. K9-AIF Core Implementation Requirements

### 7.1 Base Agent Usage

Every domain agent must extend K9-AIF `BaseAgent` or the current K9-AIF agent base class.

Required pattern:

```python
class PainPointExtractorAgent(BaseDowAgent):
    agent_name = "PainPointExtractorAgent"

    async def execute(self, payload: DowAgentPayload) -> DowAgentResult:
        ...
```

Every agent must:

1. Accept a typed payload.
2. Return a typed result.
3. Publish start/completed/failed events.
4. Use `LLMFactory` for model access.
5. Use shared governance instructions.
6. Include citations or mark unsupported content as `NOT PROVIDED IN SOURCE`.
7. Never invent stakeholders, capabilities, constraints, requirements, systems, services, or relationships.

### 7.2 Base Squad Usage

Every stage must be implemented as a K9-AIF squad. A squad is responsible for a coherent stage of work and can execute agents sequentially or in controlled parallel execution.

Required squad behavior:

1. Receive `StageExecutionContext`.
2. Execute ordered agent steps.
3. Accumulate agent outputs into `StageResult`.
4. Run `GovernanceAgent` and/or `VerificationAgent` before completing.
5. Persist stage result.
6. Publish stage lifecycle events.
7. Return `StageResult` to orchestrator.

### 7.3 Base Orchestrator Usage

The principal orchestrator must extend K9-AIF `BaseOrchestrator`.

The principal orchestrator must:

1. Receive a routed job event.
2. Resolve the selected pipeline.
3. Create job context.
4. Execute the correct pipeline orchestrator.
5. Track job state.
6. Publish lifecycle events.
7. Persist final package index.

The DoDAF orchestrator must execute:

```text
Stage 1 -> Stage 2 -> Stage 3 -> Stage 4 -> Stage 5 -> Stage 6
```

For the initial rebuild, keep this sequential. Add a config option for future parallel execution after Stage 1.

### 7.4 Base Router Usage

`DowDocumentRouter` must extend K9-AIF `BaseRouter`.

Router responsibilities:

1. Normalize raw text.
2. Apply deterministic routing rules.
3. If multiple rules match, calculate a score per route.
4. If still ambiguous, call `RoutingClassifierAgent`.
5. Return `RoutingDecision`.
6. Include classification, document type, route, eligibility flags, recommended stages, confidence, and rationale.

## 8. Contracts and Data Models

Implement these as Pydantic models or dataclasses.

### 8.1 DocumentInput

```python
class DocumentInput(BaseModel):
    job_id: str
    filename: str
    content_type: str
    raw_path: str | None = None
    text: str | None = None
    markdown: str | None = None
    metadata: dict = Field(default_factory=dict)
```

### 8.2 RoutingDecision

```python
class RoutingDecision(BaseModel):
    job_id: str
    classification: Literal["BD", "DODAF", "JCIDS", "SE", "UNKNOWN"]
    document_type: str
    route_to: str
    dodaf_eligible: bool
    jcids_eligible: bool
    se_eligible: bool
    recommended_stages: list[str | int]
    confidence: float
    rationale: str
    matched_rules: list[str] = []
```

### 8.3 StageExecutionContext

```python
class StageExecutionContext(BaseModel):
    job_id: str
    route: str
    stage_id: str
    stage_name: str
    source_document: str
    normalized_markdown: str
    prior_stage_outputs: dict[str, str] = {}
    routing_decision: RoutingDecision
    metadata: dict = {}
```

### 8.4 DowAgentResult

```python
class DowAgentResult(BaseModel):
    job_id: str
    agent_name: str
    stage_id: str
    status: Literal["completed", "failed", "skipped"]
    markdown: str = ""
    json_data: dict = {}
    citations: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []
```

### 8.5 StageResult

```python
class StageResult(BaseModel):
    job_id: str
    stage_id: str
    stage_name: str
    status: Literal["completed", "failed", "blocked", "needs_human_review"]
    agent_results: list[DowAgentResult]
    markdown_report: str
    json_bundle: dict = {}
    governance_status: str
    artifact_paths: list[str] = []
    started_at: datetime
    completed_at: datetime | None = None
```

### 8.6 GovernanceFinding

```python
class GovernanceFinding(BaseModel):
    severity: Literal["info", "warning", "error", "blocker"]
    rule_id: str
    message: str
    evidence: str | None = None
    recommended_action: str | None = None
```

## 9. Shared Governance Rules

Every stage and every agent must follow these rules:

1. Use only information explicitly present in the source document or prior approved stage outputs.
2. If a requested element is not supported, output `NOT PROVIDED IN SOURCE`.
3. Do not invent stakeholders, capabilities, systems, services, interfaces, constraints, risks, requirements, KPPs, KSAs, KURs, or timelines.
4. Include evidence snippets where possible.
5. Maintain neutral DoD/government-review-ready tone.
6. Do not mention internal implementation frameworks in generated domain reports.
7. Mark uncertainty explicitly.
8. Preserve traceability from source text to derived stage output.
9. Separate extracted facts from analysis.
10. Send outputs through governance validation before persistence.

## 10. Pipeline 0 — Document Normalization and Routing

### 10.1 DocumentNormalizationAgent

Purpose: Convert uploaded documents into normalized Markdown/text.

Inputs:

- filename
- content type
- binary file path or stream

Supported file types:

- `.md`
- `.txt`
- `.pdf`
- `.docx`
- `.pptx`
- `.xlsx`
- `.csv`

Output:

- normalized Markdown
- metadata: page count if available, file size, conversion method, warnings

Implementation rules:

1. For `.md` and `.txt`, read directly.
2. For `.docx`, use a Python document extraction utility.
3. For `.pdf`, use a local extraction utility. OCR should be optional.
4. For `.csv` and `.xlsx`, extract tabular text and preserve table boundaries.
5. Do not fail the whole job for partial extraction; return warnings and route to governance review when text quality is poor.

### 10.2 Stage0RoutingSquad

Agents:

1. `ValidationAgent`
2. `RoutingClassifierAgent`
3. `GovernanceAgent`

Tasks:

1. Validate input readability and minimum content length.
2. Apply deterministic routing rules.
3. Use LLM classification only when deterministic rules are inconclusive.
4. Emit `RoutingDecision` JSON.
5. Persist route manifest.

## 11. DoDAF Pipeline

The DoDAF pipeline is the main architecture-development path. It must produce stage-level Markdown artifacts and a final report package.

### 11.1 Stage 1 — Fit-for-Purpose / Intended Use

Squad name:

```text
Stage1FitForPurposeSquad
```

Purpose:

Determine whether the source document is valid, operationally relevant, and appropriate for architecture analysis.

Agents:

1. `ValidationAgent`
2. `StakeholderExtractorAgent`
3. `PainPointExtractorAgent`
4. `ObjectiveExtractorAgent`
5. `MissionAssessmentAgent`
6. `F2PIntentAgent`
7. `SummarizerAgent`
8. `GovernanceAgent`

Tasks:

| Task ID | Agent | Required Output |
|---|---|---|
| `validate_doc` | ValidationAgent | validation status, missing elements, evidence citations |
| `extract_stakeholders` | StakeholderExtractorAgent | stakeholder list with exact evidence |
| `extract_pain_points` | PainPointExtractorAgent | pain point list with verbatim evidence |
| `frame_operational_problem` | PainPointExtractorAgent | OV-1 style problem framing with citations |
| `extract_objectives` | ObjectiveExtractorAgent | objective register with source citations |
| `assess_mission_context` | MissionAssessmentAgent | mission context summary with citations |
| `create_f2p_statement` | F2PIntentAgent | complete Fit-for-Purpose intent statement |
| `write_stage_summary` | SummarizerAgent | Stage 1 Markdown report |
| `governance_review` | GovernanceAgent | pass/warn/block decision |

Required artifact:

```text
stage1_fit_for_purpose.md
```

### 11.2 Stage 2 — Scope / ICD Needs Analysis

Squad name:

```text
Stage2ScopeIcdSquad
```

Purpose:

Define architecture scope, boundaries, mission needs, capability gaps, early ICD content, constraints, and vocabulary seeds.

Agents:

1. `ProjectScopeAgent`
2. `ConstraintAgent`
3. `OperationalExtractorAgent`
4. `CapabilityExtractorAgent`
5. `RiskExtractorAgent`
6. `VocabularyAgent`
7. `ArchitectureAnalyzerAgent`
8. `RequirementAgent`
9. `SummarizerAgent`
10. `GovernanceAgent`

Tasks:

| Task ID | Agent | Required Output |
|---|---|---|
| `extract_scope` | ProjectScopeAgent | scope domains, problem statement, boundaries, level-of-detail hints, citations |
| `extract_constraints` | ConstraintAgent | constraint register with type, description, scope impact, evidence |
| `extract_functions_processes` | OperationalExtractorAgent | functions/processes with scope relation and evidence |
| `extract_capabilities` | CapabilityExtractorAgent | capability snippets tied to scope or `NOT PROVIDED IN SOURCE` |
| `extract_scope_risks` | RiskExtractorAgent | risk register with affected scope elements and evidence |
| `build_vocabulary_seed` | VocabularyAgent | AV-2 vocabulary seed |
| `analyze_scope` | ArchitectureAnalyzerAgent | in-scope/out-of-scope, dependencies, assumptions, gaps |
| `draft_icd_sections` | RequirementAgent | mission need, capability gap, operational context, preliminary KPP/KSA candidates where explicitly supported |
| `write_stage_summary` | SummarizerAgent | Stage 2 Markdown report |
| `governance_review` | GovernanceAgent | pass/warn/block decision |

Required artifacts:

```text
stage2_scope_icd.md
icd_seed.md
av2_vocabulary_seed.md
```

Important rule:

Stage 2 must not generate full DoDAF views. It only creates ICD and early architecture context. Full OV/SV/SvcV/CV/DIV elaboration happens after approval and in later stages.

### 11.3 Stage 3 — Required Data Identification

Squad name:

```text
Stage3DataRequirementsSquad
```

Purpose:

Identify required architecture data, DM2 concepts, capability data, operational data, system/service data, and gaps.

Agents:

1. `DataRequirementsAgent`
2. `CapabilityExtractorAgent`
3. `DM2ExtractorAgent`
4. `SystemServiceExtractorAgent`
5. `SystemViewAgent`
6. `SummarizerAgent`
7. `GovernanceAgent`

Tasks:

| Task ID | Agent | Required Output |
|---|---|---|
| `identify_required_data` | DataRequirementsAgent | required data register with view mapping and citations |
| `identify_contextual_data_needs` | DataRequirementsAgent | contextual data needs register |
| `extract_capability_data` | CapabilityExtractorAgent | capability data extract |
| `extract_system_service_data` | SystemServiceExtractorAgent | system/service data needs extract |
| `structure_system_data` | SystemViewAgent | preliminary SV/SvcV seeds |
| `extract_dm2_required_data` | DM2ExtractorAgent | DM2 JSON bundle |
| `write_stage_summary` | SummarizerAgent | Stage 3 Markdown report |
| `governance_review` | GovernanceAgent | pass/warn/block decision |

Required artifacts:

```text
stage3_data_requirements.md
dm2_required_data.json
```

### 11.4 Stage 4 — Architecture Data Correlation

Squad name:

```text
Stage4ArchitectureCorrelationSquad
```

Purpose:

Collect and correlate architecture data into structured DoDAF model seeds, system/service relationships, DM2 bundle, and graph persistence payload.

Agents:

1. `OperationalExtractorAgent`
2. `CapabilityExtractorAgent`
3. `SystemServiceExtractorAgent`
4. `SystemViewAgent`
5. `ServicesViewAgent`
6. `DM2ExtractorAgent`
7. `DataCorrelationAgent`
8. `ReportWriterAgent`
9. `SummarizerAgent`
10. `GovernanceAgent`

Tasks:

| Task ID | Agent | Required Output |
|---|---|---|
| `collect_operational_data` | OperationalExtractorAgent | activities, performers, triggers, conditions, evidence |
| `collect_capability_data` | CapabilityExtractorAgent | capabilities, objectives, evidence |
| `collect_system_service_data` | SystemServiceExtractorAgent | system/service names, roles, relationships |
| `structure_system_views` | SystemViewAgent | systems, services, interactions, performer associations |
| `structure_service_views` | ServicesViewAgent | services, service dependencies, service interactions |
| `extract_dm2_full_bundle` | DM2ExtractorAgent | full DM2 JSON bundle |
| `correlate_architecture_data` | DataCorrelationAgent | taxonomies, cross-links, evidence mapping, explicit gaps |
| `persist_architecture_data` | ReportWriterAgent | persistence confirmation and artifact paths |
| `write_stage_summary` | SummarizerAgent | Stage 4 Markdown report |
| `governance_review` | GovernanceAgent | pass/warn/block decision |

Required artifacts:

```text
stage4_architecture_correlation.md
dm2_full_bundle.json
architecture_correlation_index.json
```

### 11.5 Stage 5 — Architecture Analysis

Squad name:

```text
Stage5ArchitectureAnalysisSquad
```

Purpose:

Analyze the architecture against objectives, capability gaps, operational alignment, risks, consistency, and sufficiency.

Agents:

1. `ValidationAgent`
2. `VerificationAgent`
3. `ArchitectureAnalyzerAgent`
4. `CapabilityAnalyzerAgent`
5. `OperationalAnalyzerAgent`
6. `RiskExtractorAgent`
7. `ActionItemAgent`
8. `RequirementAgent`
9. `SummarizerAgent`
10. `GovernanceAgent`

Tasks:

| Task ID | Agent | Required Output |
|---|---|---|
| `revalidate_architecture` | ValidationAgent | completeness/consistency status |
| `analyze_capabilities` | CapabilityAnalyzerAgent | capability-by-capability assessment, gaps |
| `analyze_operations` | OperationalAnalyzerAgent | mission alignment, strengths, weaknesses, gaps |
| `analyze_objective_alignment` | ArchitectureAnalyzerAgent | objective support matrix |
| `review_risks` | RiskExtractorAgent | updated risk register |
| `verify_consistency` | VerificationAgent | cross-view consistency report |
| `assess_sufficiency` | ArchitectureAnalyzerAgent | sufficiency rating and iteration recommendation |
| `generate_action_items` | ActionItemAgent | action item list with priorities if supported |
| `consolidate_requirements` | RequirementAgent | requirements register and verification links |
| `write_stage_report` | SummarizerAgent | Stage 5 Markdown report |
| `governance_review` | GovernanceAgent | pass/warn/block decision |

Required artifacts:

```text
stage5_architecture_analysis.md
requirements_register.md
traceability_matrix.md
risk_register.md
```

### 11.6 Stage 6 — Presentation and Reporting

Squad name:

```text
Stage6PresentationSquad
```

Purpose:

Produce final decision-ready package. Stage 6 must not introduce new analysis. It must compile and present validated prior-stage outputs only.

Agents:

1. `VerificationAgent`
2. `PresentationAgent`
3. `SummarizerAgent`
4. `GovernanceAgent`
5. `ReportWriterAgent`

Tasks:

| Task ID | Agent | Required Output |
|---|---|---|
| `final_cross_view_validation` | VerificationAgent | viewpoint coverage matrix, unsupported views, inconsistency bullets |
| `build_presentation_package` | PresentationAgent | evidence-based presentation package |
| `build_executive_summary` | SummarizerAgent | executive summary and decision-maker summary |
| `governance_signoff` | GovernanceAgent | final status matrix and readiness decision |
| `write_final_reports` | ReportWriterAgent | Markdown and DOCX package outputs |

Required artifacts:

```text
stage6_presentation.md
final_architecture_report.md
final_architecture_report.docx
artifact_index.json
governance_signoff.md
```

## 12. JCIDS Pipeline

The JCIDS pipeline must be separate from the DoDAF pipeline but able to consume ICD/F2P outputs when available.

### 12.1 JCIDS Stage 1 — Capability Validation

Squad:

```text
JcidsCapabilityValidationSquad
```

Agent:

```text
JcidsCapabilityValidatorAgent
```

Output:

```text
jcids_capability_validation.md
```

Content:

- operational need validation
- mission gap validation
- capability problem statement
- evidence-based sufficiency notes

### 12.2 JCIDS Stage 2 — Requirements Expansion

Squad:

```text
JcidsRequirementsExpansionSquad
```

Agents:

1. `JcidsKppAgent`
2. `JcidsKsaAgent`
3. `JcidsKurAgent`

Outputs:

```text
jcids_kpp.md
jcids_ksa.md
jcids_kur.md
```

### 12.3 JCIDS Stage 3 — AoA Inputs

Squad:

```text
JcidsAoaInputsSquad
```

Agent:

```text
JcidsAoaAgent
```

Output:

```text
aoa_inputs.md
```

Content:

- alternatives if supported
- measures of effectiveness
- measures of performance
- evaluation factors
- unsupported areas clearly marked

### 12.4 JCIDS Stage 4 — DOTMLPF-P Extension

Squad:

```text
JcidsDotmlpfpSquad
```

Agent:

```text
JcidsDotmlpfpAgent
```

Output:

```text
dotmlpfp_extension.md
```

### 12.5 JCIDS Stage 5 — Risk and Acquisition Pathway

Squad:

```text
JcidsRiskAcquisitionSquad
```

Agents:

1. `JcidsRiskMatrixAgent`
2. `JcidsAcquisitionPathwayAgent`

Outputs:

```text
jcids_risk_matrix.md
acquisition_pathway.md
```

### 12.6 JCIDS Stage 6 — Summary

Squad:

```text
JcidsSummarySquad
```

Agent:

```text
SummarizerAgent
```

Outputs:

```text
jcids_summary.md
cdd_seed.md
```

## 13. Business Pipeline

The business pipeline processes call reports, meeting notes, engagement summaries, contracting intelligence, opportunity notes, HR modernization notes, and capture documents.

Squad:

```text
BusinessIntakeSquad
```

Agents:

1. `BusinessOpportunityAgent`
2. `StakeholderExtractorAgent`
3. `PainPointExtractorAgent`
4. `BusinessContractingAgent`
5. `RiskExtractorAgent`
6. `ActionItemAgent`
7. `SummarizerAgent`
8. `GovernanceAgent`

Outputs:

```text
business_summary.md
opportunity_extract.md
stakeholder_register.md
pain_point_register.md
contracting_intelligence.md
risk_register.md
action_items.md
```

## 14. Systems Engineering Pipeline

The systems engineering pipeline handles system specifications, interface specifications, verification/validation material, functional analysis, and design synthesis.

Orchestrator:

```text
SeOrchestrator
```

Initial squads:

1. `Stage3DataRequirementsSquad`
2. `Stage4ArchitectureCorrelationSquad`
3. `Stage5ArchitectureAnalysisSquad`
4. `Stage6PresentationSquad`

Additional SE-specific agent behavior:

- Extract functional requirements.
- Extract interface candidates.
- Extract verification criteria.
- Build requirements-to-verification traceability.
- Produce system specification seed and interface control document seed.

Required outputs:

```text
se_requirements_register.md
se_functional_analysis.md
se_interface_candidates.md
se_verification_matrix.md
se_summary.md
```

## 15. Agent Prompt Requirements

Create a common prompt file:

```text
config/prompts/common_grounding_rules.md
```

Content must include:

```text
You are operating inside a governed DoD architecture and requirements analysis workflow.
Use only the source document and approved prior-stage outputs.
Do not invent facts.
Do not introduce new systems, technologies, stakeholders, capabilities, constraints, requirements, or relationships unless explicitly present in the source.
If evidence is missing, write: NOT PROVIDED IN SOURCE.
Use structured Markdown.
Include short source evidence snippets where possible.
Keep tone neutral, professional, and suitable for government review.
Do not mention internal implementation technology in generated domain artifacts.
```

Each agent must combine the common grounding rules with its role-specific prompt.

## 16. Persistence Requirements

Implement persistence through K9-AIF-style adapters, not hard-coded utilities.

### 16.1 File Repository

Store job artifacts under:

```text
output_reports/{job_id}/
  input/
  stage_outputs/
  json/
  reports/
  logs/
```

### 16.2 PostgreSQL Repository

Create tables or repository methods for:

- jobs
- routing decisions
- stage results
- agent results
- artifacts
- governance findings
- traceability items

### 16.3 Graph Repository

Create graph persistence methods for DM2/DoDAF concepts:

- Capability
- Activity
- Performer
- System
- Service
- Information
- ResourceFlow
- Requirement
- Constraint
- Risk
- Objective
- Stakeholder

Edges:

- supports
- depends_on
- performs
- produces
- consumes
- constrains
- verifies
- traces_to
- addresses

Graph persistence must be optional and controlled by config.

### 16.4 Object Store Repository

Support MinIO/S3-compatible storage for uploaded inputs and final artifacts. Credentials must be loaded from environment variables only.

## 17. DoW Retriever Requirements

Create a K9-AIF-native governed retrieval layer named `dow_retriever`. This is a first-class K9-AIF component, not a helper utility. It must provide trusted contextual knowledge to Stage 2 through Stage 5 agents and optionally to Stage 1 and Stage 6 when classification, validation, or report assembly needs additional governed context.

### 17.1 Purpose

The `dow_retriever` is responsible for retrieving, normalizing, masking, scoring, and returning mission-relevant context from governed architecture knowledge sources. Its output must be treated as supporting evidence, not as an uncontrolled generation source. Agents must always distinguish between:

1. direct source-document evidence,
2. governed retrieved enterprise context,
3. structured DM2 or ADR records, and
4. agent-derived analysis.

The retriever must support architecture, doctrine, mission, policy, historical, and reference context needed by the DoDAF pipeline.

### 17.2 Required K9-AIF Classes

Generate these files:

```text
src/k9_dow/retrieval/
  __init__.py
  dow_retriever.py
  retrieval_context.py
  retrieval_policy.py
  metadata_normalizer.py
  chunking.py
  provenance.py
  knowledge_fusion.py
  vector_store_factory.py
  chroma_adapter.py
  milvus_adapter.py
  catalog_adapter.py
  null_retriever.py
```

Required classes:

```text
DoWRetriever
RetrievalRequest
RetrievalResult
RetrievalCitation
RetrievalContextBundle
RetrievalPolicy
MetadataNormalizer
DoWChunker
ProvenanceScorer
KnowledgeFusionService
VectorStoreFactory
CatalogAdapter
ChromaRetriever
MilvusRetriever
NullRetriever
```

`DoWRetriever` must extend or compose K9-AIF base abstractions consistently with the generated framework style. If retrieval is modeled as an agent, implement `DoWRetrieverAgent(BaseAgent)`. If retrieval is modeled as a connector/service, expose it through a K9 connector adapter and inject it into agents through the orchestrator context.

### 17.3 Inputs

`RetrievalRequest` must include:

```python
@dataclass
class RetrievalRequest:
    job_id: str
    stage_id: str
    agent_name: str
    query: str
    document_type: str | None
    mission_context: str | None
    viewpoint: str | None        # CV, OV, SV, SvcV, PV, StdV, ICD, F2P
    entities: list[str]
    required_metadata: dict[str, Any]
    top_k: int = 8
    min_confidence: float = 0.65
    include_enterprise_context: bool = True
    include_historical_context: bool = True
    include_doctrine: bool = True
    include_policy: bool = True
```

### 17.4 Outputs

`RetrievalContextBundle` must include:

```python
@dataclass
class RetrievalContextBundle:
    job_id: str
    stage_id: str
    query: str
    results: list[RetrievalResult]
    citations: list[RetrievalCitation]
    fused_summary: str
    provenance_score: float
    governance_findings: list[dict[str, Any]]
    warnings: list[str]
```

`RetrievalResult` must include source name, source type, chunk id, text, score, provenance, lineage, classification level if available, page number if available, section heading, and retrieval timestamp.

### 17.5 Knowledge Sources

The retriever must support these source categories:

1. extracted text corpora from uploaded source documents,
2. architecture reference material,
3. doctrine/manual/guidance content,
4. SME-written notes and reports,
5. historical or lessons-learned archives,
6. structured metadata from a knowledge catalog or equivalent governed catalog,
7. vector stores such as Chroma or Milvus,
8. optional relational or graph-backed lookups when a query needs DM2/ADR context.

The implementation must not hard-code a specific enterprise product. Provide a generic `CatalogAdapter` interface with environment-driven implementations. The catalog role is governance metadata, stewardship, lineage, classification, provenance, and data-source discovery.

### 17.6 Retrieval Pipeline

Implement this retrieval pipeline:

```text
1. Receive RetrievalRequest from an agent or orchestrator.
2. Normalize query and metadata filters.
3. Apply RetrievalPolicy.
4. Mask or redact restricted content before LLM exposure.
5. Query catalog metadata for governed source discovery.
6. Query vector store for semantic chunks.
7. Query optional graph/relational repositories for DM2/ADR facts.
8. Score provenance, freshness, lineage, source trust, and classification suitability.
9. Fuse compatible context from multiple sources.
10. Return RetrievalContextBundle with citations, warnings, and governance findings.
```

### 17.7 Chunking Requirements

`DoWChunker` must chunk documents with metadata preservation:

- page number,
- source filename,
- document type,
- section heading,
- paragraph index,
- table identifier,
- image reference if available,
- confidence score if OCR/layout extraction provided it,
- bounding box if available,
- classification / sensitivity metadata if available,
- source lineage id.

Chunking must preserve Markdown tables and section hierarchy. Do not flatten tables into plain text unless no better option is available.

### 17.8 Governance Rules

`RetrievalPolicy` must enforce:

1. Do not return content below the configured confidence threshold.
2. Do not mix incompatible classification levels in a single context bundle.
3. Do not expose masked fields to LLM prompts.
4. Prefer authoritative cataloged sources over uncataloged sources.
5. Prefer source-document evidence over historical examples for final claims.
6. Attach provenance to every retrieved chunk.
7. Return warnings when retrieval is weak, stale, ambiguous, or unsupported.
8. Support HIL escalation when critical ICD/F2P claims depend on low-confidence retrieval.

### 17.9 Agent Usage Pattern

Agents must call the retriever through a single interface:

```python
context_bundle = self.retriever.retrieve(
    RetrievalRequest(
        job_id=payload.job_id,
        stage_id=payload.stage_id,
        agent_name=self.name,
        query=query,
        document_type=payload.document_type,
        mission_context=payload.mission_context,
        viewpoint=payload.viewpoint,
        entities=payload.entities,
        required_metadata=filters,
        top_k=8,
    )
)
```

Agents must include retrieved context in prompts under a clearly labeled section:

```text
GOVERNED RETRIEVED CONTEXT
- Use only as supporting context.
- Do not invent facts absent from source evidence or retrieved citations.
- Cite source chunk ids when using this context.
```

### 17.10 Stage-Specific Retriever Behavior

Stage 1 may use the retriever only for classification support, known document patterns, routing hints, and policy references. Stage 1 must not rely on retrieval alone to approve F2P.

Stage 2 must use the retriever for mission context, constraints, policy/standards references, stakeholder context, capability gaps, and ICD framing.

Stage 3 must use the retriever for operational context, doctrine, mission activities, performer references, and operational terminology. Stage 3 must still write structured architectural facts separately to graph/relational persistence.

Stage 4 must use the retriever for system/service context, known interfaces, existing architecture references, and standards-linked system/service descriptions.

Stage 5 must use the retriever for performance measures, standards, compliance constraints, technical limits, and standards forecasts.

Stage 6 may use the retriever for final citation validation, missing-reference checks, and HIL-ready evidence packages. Stage 6 must not generate new architecture from retrieval; it assembles validated outputs from prior stages.

### 17.11 Vector Store Factory

Implement retrieval through `VectorStoreFactory` with these adapters:

1. `NullRetriever` for no retrieval.
2. `ChromaRetriever` for local persistent vector store.
3. `MilvusRetriever` for external vector store.
4. `CatalogAdapter` for governed metadata and lineage lookup.

All adapters must share a stable interface:

```python
class RetrieverAdapter(Protocol):
    def index(self, chunks: list[DocumentChunk]) -> list[str]: ...
    def search(self, request: RetrievalRequest) -> list[RetrievalResult]: ...
    def health(self) -> dict[str, Any]: ...
```

### 17.12 API Endpoints

Add API endpoints:

```text
POST /retrieval/index/{job_id}
POST /retrieval/query
GET  /retrieval/sources/{job_id}
GET  /retrieval/health
```

The `/retrieval/query` endpoint must return the same `RetrievalContextBundle` structure used internally by agents.

### 17.13 Tests

Generate tests:

```text
tests/test_dow_retriever.py
tests/test_retrieval_policy.py
tests/test_chunking_metadata.py
tests/test_retrieval_governance.py
tests/test_retrieval_api.py
```

Minimum test cases:

1. indexes Markdown with page and heading metadata,
2. retrieves top-k chunks with citations,
3. filters low-confidence chunks,
4. masks restricted fields,
5. returns warnings for weak retrieval,
6. supports NullRetriever without failing the pipeline,
7. injects retrieved context into Stage 2 agent payload,
8. prevents Stage 6 from creating new architecture from retrieval-only context.

### 17.14 Acceptance Criteria

The retriever implementation is complete when:

1. `DoWRetriever` can index uploaded extracted artifacts.
2. Stage 2 through Stage 5 agents can request governed context.
3. Every returned result has citation and provenance metadata.
4. Governance warnings are surfaced to the stage output.
5. The pipeline works with `NullRetriever` for offline/demo mode.
6. Chroma local retrieval works with persisted collections.
7. The API exposes retrieval health and query behavior.
8. Final ICD/F2P report citations can trace retrieved context back to source chunks.

## 18. Messaging and Monitoring Requirements

Implement `EventPublisher` abstraction.

Events:

```text
DocumentUploaded
DocumentNormalized
RoutingStarted
RoutingCompleted
RoutingFailed
PipelineStarted
StageStarted
AgentStarted
AgentCompleted
AgentFailed
GovernanceReviewStarted
GovernanceReviewCompleted
StageCompleted
StageFailed
PipelineCompleted
ReportGenerated
JobFailed
```

Each event must include:

- event type
- job ID
- route
- stage ID if applicable
- agent name if applicable
- timestamp
- status
- message
- payload summary

Provide two event publishers:

1. `InMemoryEventPublisher` for tests/local dev.
2. `KafkaEventPublisher` for Redpanda/Kafka deployments.

## 19. API Requirements

Use FastAPI.

### 19.1 Endpoints

```text
GET  /health
GET  /llm
POST /jobs/upload
POST /jobs/{job_id}/run
GET  /jobs/{job_id}
GET  /jobs/{job_id}/events
GET  /jobs/{job_id}/stages
GET  /jobs/{job_id}/artifacts
GET  /reports/{job_id}/{artifact_name}
```

### 19.2 Upload Behavior

`POST /jobs/upload` must:

1. Accept a file.
2. Generate job ID.
3. Store raw file.
4. Normalize to Markdown/text.
5. Route the document.
6. Return job ID and routing decision.

### 19.3 Run Behavior

`POST /jobs/{job_id}/run` must:

1. Load normalized input and route decision.
2. Execute selected pipeline.
3. Return final job status and artifact index.

### 19.4 Event Stream

`GET /jobs/{job_id}/events` must return stored events. Optional Server-Sent Events or WebSocket can be added after core rebuild.

## 20. Configuration Requirements

Create `.env.example` with no real secrets:

```text
K9_DOW_ENV=local
K9_DOW_ACTIVE_LLM=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=granite3.3:8b
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=dow
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change-me
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=change-me
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
OBJECT_STORE_ENDPOINT=http://localhost:9000
OBJECT_STORE_ACCESS_KEY=change-me
OBJECT_STORE_SECRET_KEY=change-me
```

Never hard-code secrets. All credentials must come from environment variables.

## 21. Routing Rules

Implement routing rules in:

```text
config/routing_rules.yaml
```

Required content:

```yaml
patterns:
  - name: business_meeting_notes
    classification: BD
    document_type: meeting_notes
    contains_any:
      - call report
      - meeting notes
      - engagement
      - industry day
      - capture
      - opportunity
      - contracting officer
      - rfp
      - solicitation
      - proposal
      - market research
      - sources sought
      - military sealift command
      - recruitment
      - retention
    route_to: business_pipeline
    dodaf_eligible: false
    jcids_eligible: false
    se_eligible: false
    recommended_stages: [1]

  - name: dodaf_architecture_docs
    classification: DODAF
    document_type: architecture_document
    contains_any:
      - architecture
      - mission
      - capability
      - operational
      - system description
      - system overview
      - data flow
      - interfaces
      - conops
      - operational concept
      - ov-1
      - ov-2
      - sv-1
      - cv-1
      - dodaf
    route_to: dodaf_pipeline
    dodaf_eligible: true
    jcids_eligible: false
    se_eligible: true
    recommended_stages: [1, 2, 3, 4, 5, 6]

  - name: jcids_requirements
    classification: JCIDS
    document_type: requirements_document
    contains_any:
      - requirement
      - mission need
      - capability gap
      - initial capabilities
      - icd
      - cdd
      - kpp
      - ksa
      - kur
      - moe
      - mop
      - jcids
      - dotmlpf
    route_to: jcids_pipeline
    dodaf_eligible: true
    jcids_eligible: true
    se_eligible: true
    recommended_stages: [capability_validation, requirements_expansion, aoa, dotmlpfp, risk_acquisition, summary]

  - name: se_documents
    classification: SE
    document_type: se_document
    contains_any:
      - systems engineering
      - functional analysis
      - design synthesis
      - verification
      - validation
      - system specification
      - interface specification
      - performance specification
    route_to: se_pipeline
    dodaf_eligible: true
    jcids_eligible: false
    se_eligible: true
    recommended_stages: [requirements, functional, architecture, verification]

defaults:
  unknown:
    classification: UNKNOWN
    document_type: unknown
    route_to: unknown_pipeline
    dodaf_eligible: false
    jcids_eligible: false
    se_eligible: false
    recommended_stages: []
```

## 22. Reporting Requirements

### 22.1 Markdown Reports

All stage reports must be Markdown.

Required common report structure:

```text
# {Stage Name}

## Job Metadata

## Source Summary

## Extracted Findings

## Analysis

## Evidence / Citations

## Unsupported or Missing Information

## Governance Review

## Next Steps
```

### 22.2 DOCX Reports

DOCX generation is optional for first pass but required for complete implementation.

Implement:

```text
DocxReportBuilder
```

It must convert Markdown reports into DOCX and use templates when provided.

### 22.3 Final Report Package

Final package must include:

```text
final_architecture_report.md
final_architecture_report.docx
artifact_index.json
governance_signoff.md
traceability_matrix.md
```

## 23. Human-in-the-Loop Requirement

After Stage 2, support an optional HIL approval gate before full architecture elaboration.

Behavior:

1. If `require_hil_after_stage2=true`, stop after Stage 2.
2. Mark job status as `needs_human_review`.
3. Persist Stage 1 and Stage 2 outputs.
4. Provide API endpoint or method for resume.
5. Resume with Stage 3 after approval.

Config:

```text
K9_DOW_REQUIRE_HIL_AFTER_STAGE2=false
```

## 24. Error Handling

Every orchestrator, squad, and agent must handle:

- missing input
- unsupported file type
- empty normalized text
- LLM failure
- persistence failure
- governance blocker
- report generation failure

Rules:

1. Agent failure must produce a `DowAgentResult` with status `failed`.
2. Stage failure must produce a `StageResult` with status `failed` or `blocked`.
3. Governance blocker must stop downstream stage execution unless config permits warning-only mode.
4. Partial artifacts must still be persisted where possible.

## 25. Test Requirements

Claude Code must generate tests for:

1. Deterministic routing by keyword.
2. Unknown document fallback.
3. Stage 1 squad execution with mock LLM.
4. Stage 2 scope output with `NOT PROVIDED IN SOURCE` behavior.
5. Governance rule catching invented content.
6. DoDAF orchestrator stage ordering.
7. JCIDS orchestrator stage ordering.
8. API upload endpoint.
9. Artifact index generation.
10. Event publication.

Use mock LLM responses for tests. Tests must not require live Ollama, Watsonx, Postgres, Neo4j, Kafka, Chroma, Milvus, MinIO, or S3.

## 26. Acceptance Criteria

The implementation is complete when:

1. `pip install -e .` succeeds.
2. `pytest` passes.
3. `k9-dow --help` works.
4. FastAPI service starts locally.
5. A Markdown input can be uploaded and routed.
6. A DoDAF architecture input runs Stage 1 through Stage 6.
7. A JCIDS input runs the JCIDS pipeline.
8. A business meeting note runs the business pipeline.
9. All outputs are persisted under `output_reports/{job_id}`.
10. Final artifact index is generated.
11. No non-K9 orchestration dependency is imported.
12. No credentials are hard-coded.
13. All generated domain artifacts avoid internal implementation terminology.
14. Governance checks run after every stage.
15. Unsupported facts are marked `NOT PROVIDED IN SOURCE`.

## 27. Claude Code Build Instructions

Use the following implementation order:

1. Create project skeleton and `pyproject.toml`.
2. Add contracts and typed payloads.
3. Add config loader and routing rules.
4. Implement K9-AIF base integration wrappers: `BaseDowAgent`, `BaseStageSquad`, and orchestrator classes.
5. Implement `DocumentNormalizationAgent`.
6. Implement `DowDocumentRouter`.
7. Implement event publisher abstraction with in-memory implementation first.
8. Implement file repository first.
9. Implement mock LLM adapter or K9-AIF-compatible test adapter.
10. Implement Stage 1 and Stage 2 squads.
11. Add tests for router and Stage 1/2.
12. Implement Stage 3 through Stage 6 squads.
13. Implement DoDAF orchestrator.
14. Implement JCIDS squads and orchestrator.
15. Implement business pipeline.
16. Implement SE pipeline.
17. Implement Markdown report builder.
18. Implement artifact index builder.
19. Implement FastAPI routes.
20. Add optional adapters for PostgreSQL, graph DB, object store, vector store, and Kafka.
21. Add DOCX report builder.
22. Add CLI.
23. Run tests and fix issues.

## 28. Code Generation Constraints for Claude Code

Claude Code must follow these constraints:

1. Generate clean Python 3.11+ code.
2. Use async where K9-AIF execution expects async.
3. Keep all external integrations behind interfaces/adapters.
4. Use environment variables for credentials.
5. Do not import any old orchestration library.
6. Do not copy old runtime code blindly.
7. Preserve the business behavior and artifact names.
8. Prefer small classes with focused responsibilities.
9. Use typed payloads and typed results.
10. Add unit tests as code is generated.
11. Use mock implementations for tests.
12. Keep prompts in external Markdown/YAML config files.
13. Emit K9-AIF monitoring events consistently.
14. Make the first runnable path local-only: file repository, in-memory events, mock/inference adapter.
15. Add optional production integrations after local path works.

## 29. First Minimal Runnable Slice

The first working version must support this path:

```text
Markdown file upload
  -> normalize text
  -> deterministic route
  -> DoDAF Stage 1
  -> DoDAF Stage 2
  -> governance review
  -> persist Markdown artifacts
  -> return artifact index
```

After that works, add Stages 3–6, JCIDS, business, SE, streaming, graph, vector, object store, and DOCX.

## 30. Domain Artifact Naming

Use these exact output names where applicable:

```text
routing_manifest.json
stage1_fit_for_purpose.md
stage2_scope_icd.md
icd_seed.md
av2_vocabulary_seed.md
stage3_data_requirements.md
dm2_required_data.json
stage4_architecture_correlation.md
dm2_full_bundle.json
architecture_correlation_index.json
stage5_architecture_analysis.md
requirements_register.md
traceability_matrix.md
risk_register.md
stage6_presentation.md
final_architecture_report.md
final_architecture_report.docx
artifact_index.json
governance_signoff.md
jcids_capability_validation.md
jcids_kpp.md
jcids_ksa.md
jcids_kur.md
aoa_inputs.md
dotmlpfp_extension.md
jcids_risk_matrix.md
acquisition_pathway.md
jcids_summary.md
cdd_seed.md
business_summary.md
opportunity_extract.md
stakeholder_register.md
pain_point_register.md
contracting_intelligence.md
action_items.md
se_requirements_register.md
se_functional_analysis.md
se_interface_candidates.md
se_verification_matrix.md
se_summary.md
```

## 31. Final Instruction to Claude Code

Build this as a K9-AIF-native application. The reference zip defines the domain process, but the new implementation must use K9-AIF routers, orchestrators, squads, agents, validation loops, persistence adapters, monitoring events, and inference factories throughout. The generated result should feel like a clean K9-AIF solution, not a mechanical port.
