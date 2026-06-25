# DoDAF 2.0 Architecture Development — Agent Reference

## Six-Step Architecture Development Process

### Step 1 — Determine Intended Use (Fit-for-Purpose)

**DoDAF Name:** Determine the Intended Use of the Architecture
**Purpose:** Determine WHY the architecture is being developed and HOW it will be used to support decision-making.

**Key Activities:**
- Identify the decision-makers and stakeholders
- Determine the specific decisions the architecture will support
- Identify the questions the architecture must answer
- Define success criteria for the architecture effort
- Determine the scope of the problem domain

**Outputs:**
- Fit-for-Purpose (F2P) intent statement
- Stakeholder register
- Decision context
- Architecture purpose statement
- AV-1 Overview and Summary (initial)

**DoDAF Views:** AV-1 (initial)

**Rules:**
- Architecture must be tailored to its purpose — not all views are required
- Stakeholder concerns drive view selection
- No architecture element should exist without a purpose tied to a decision

---

### Step 2 — Determine Scope of the Architecture

**DoDAF Name:** Determine the Scope of the Architecture
**Purpose:** Establish boundaries, constraints, and the level of detail for the architecture.

**Key Activities:**
- Define architecture boundaries (in-scope vs out-of-scope)
- Identify constraints (policy, technical, organizational, resource)
- Determine level of detail required
- Identify applicable standards and policies
- Define the architecture timeframe
- Identify mission context and operational environment
- Establish capability gaps and mission needs
- Create initial ICD content (mission need, capability gap)
- Build AV-2 vocabulary seed

**Outputs:**
- Architecture scope definition
- Constraint register
- ICD seed (mission need statement, capability gap analysis)
- AV-2 Integrated Dictionary (initial)
- Preliminary CV-1 Vision
- Preliminary OV-1 High-Level Operational Concept

**DoDAF Views:** AV-1, AV-2, CV-1 (initial), OV-1 (initial)

**Rules:**
- Scope must be driven by Step 1 purpose — not by available data
- Out-of-scope elements must be explicitly identified
- Constraints must cite sources (policy, directive, regulation)
- ICD content only when evidence supports it — no invention

---

### Step 3 — Identify Required Data to Support Architecture Development

**DoDAF Name:** Identify the Data Required to Support Architecture Development
**Purpose:** Identify the specific architecture data elements needed to populate the selected views.

**Key Activities:**
- Map required data to DoDAF views
- Identify DM2 entity types needed (Performer, Activity, Capability, Service, System, Resource, etc.)
- Identify data sources (documents, SMEs, databases, standards)
- Determine data quality requirements
- Map capability data requirements
- Map operational data requirements
- Map system/service data requirements
- Identify data gaps

**Outputs:**
- Required Data Register (DR-001, DR-002, ...)
- DM2 required data specification
- Data source mapping
- Data gap analysis

**DoDAF Views:** Preparation for CV, OV, SV, SvcV, DIV views

**DM2 Entity Types:**
- Capability (CAP-###)
- Activity (ACT-###)
- Performer (PERF-###)
- System / Node (NODE-###)
- Service (SVC-###)
- Information / Data (INFO-###)
- Resource Flow (FLOW-###)
- Interface (INT-###)
- Measure (MOE/MOP)
- Location
- Condition / Rule
- Standard

---

### Step 4 — Collect, Organize, Correlate, and Store Architecture Data

**DoDAF Name:** Collect, Organize, Correlate, and Store Architecture Data
**Purpose:** Populate the architecture with actual data, organize it into DoDAF structures, and establish cross-view traceability.

**Key Activities:**
- Collect data from identified sources
- Organize data into DM2-compliant structures
- Correlate across viewpoints:
  - Capabilities ↔ Activities (CV-6)
  - Activities ↔ Performers (OV-5)
  - Performers ↔ Systems (SV-1)
  - Systems ↔ Services (SvcV-1)
  - Resource Flows (OV-2)
- Build preliminary views:
  - OV-2 Operational Resource Flow
  - OV-5 Operational Activity Model
  - CV-2 Capability Taxonomy
  - SV-1 Systems Interface Description
  - SvcV-1 Services Context
- Store in Architecture Data Repository (ADR)

**Outputs:**
- Populated DM2 data bundle
- Architecture correlation index
- Preliminary OV-2, OV-5, CV-2, SV-1, SvcV-1
- Architecture Data Repository entries

**DoDAF Views:** OV-2, OV-5, CV-2, CV-6, SV-1, SvcV-1, DIV-1

**Rules:**
- All correlations must be evidence-based — label unconfirmed as "Candidate"
- Cross-view consistency must be maintained
- Every entity must trace to a source document or SME input

---

### Step 5 — Conduct Analyses in Support of Architecture Objectives

**DoDAF Name:** Conduct Analyses in Support of Architecture Objectives
**Purpose:** Analyze the architecture data against mission objectives, capability gaps, operational alignment, and consistency.

**Key Activities:**
- Analyze capability-by-capability assessment
- Assess operational alignment to mission
- Evaluate architecture against objectives (from Step 1/2)
- Check cross-view consistency
- Assess architecture sufficiency
- Identify remaining gaps
- Update risk register
- Consolidate requirements
- Build traceability matrix (requirements ↔ views ↔ capabilities)
- Generate action items

**Outputs:**
- Capability analysis report
- Operational analysis report
- Objective alignment matrix
- Cross-view consistency report
- Requirements register
- Traceability matrix
- Risk register (updated)
- Action items
- Architecture sufficiency assessment

**DoDAF Views:** All views refined, OV-6 (rules/state/event-trace), SV-5 (systems functionality), StdV-1/2

**Rules:**
- Analysis must be grounded in Step 4 data — not new extraction
- Gaps must reference specific missing data elements
- Recommendations must distinguish "evidence-supported" from "requires further analysis"

---

### Step 6 — Document and Present Results

**DoDAF Name:** Document Results and Present Architecture
**Purpose:** Produce decision-ready packages that present validated architecture findings to stakeholders.

**Key Activities:**
- Compile stage outputs into final report
- Build executive summary
- Build governance sign-off
- Produce viewpoint coverage matrix
- Generate final architecture report (Markdown + DOCX)
- Build artifact index
- Conduct final cross-view validation

**Outputs:**
- Final Architecture Report
- Executive Summary
- Governance Sign-off
- Artifact Index
- Viewpoint Coverage Matrix
- Presentation Package

**DoDAF Views:** AV-1 (final), AV-2 (final), all produced views

**Rules:**
- Stage 6 MUST NOT introduce new analysis
- Stage 6 ONLY compiles and presents validated prior-stage outputs
- All claims must trace to earlier stages
- Unsupported views must be explicitly noted as "Not Produced"

---

## DoDAF 2.0 Viewpoints and Views

| Viewpoint | Code | Views |
|---|---|---|
| All Viewpoint | AV | AV-1 Overview & Summary, AV-2 Integrated Dictionary |
| Capability Viewpoint | CV | CV-1 Vision, CV-2 Capability Taxonomy, CV-3 Capability Phasing, CV-4 Capability Dependencies, CV-5 Capability to Org Mapping, CV-6 Capability to Activities Mapping, CV-7 Capability to Services Mapping |
| Data & Information Viewpoint | DIV | DIV-1 Conceptual Data Model, DIV-2 Logical Data Model, DIV-3 Physical Data Model |
| Operational Viewpoint | OV | OV-1 High-Level Operational Concept, OV-2 Operational Resource Flow, OV-3 Operational Resource Flow Matrix, OV-4 Organizational Relationships, OV-5a/b Operational Activity Models, OV-6a/b/c Rules/State/Event-Trace |
| Project Viewpoint | PV | PV-1 Project Portfolio, PV-2 Project Timelines, PV-3 Project to Capability Mapping |
| Services Viewpoint | SvcV | SvcV-1 through SvcV-10c (Services Context, Resource Flows, Functionality, Behavior, etc.) |
| Standards Viewpoint | StdV | StdV-1 Standards Profile, StdV-2 Standards Forecast |
| Systems Viewpoint | SV | SV-1 through SV-10c (Systems Interface, Resource Flows, Functionality, Behavior, etc.) |

---

## DM2 Core Entity Types

| Entity | ID Format | Definition |
|---|---|---|
| Capability | CAP-### | The ability to achieve a desired effect under specified standards and conditions |
| Activity | ACT-### | An action performed by a performer in the operational or service context |
| Performer | PERF-### | Any entity (person, organization, system) that performs an activity |
| System / Node | NODE-### | A physical or logical resource that provides or supports services |
| Service | SVC-### | A mechanism to enable access to one or more capabilities |
| Information | INFO-### | Data element that is produced, consumed, or exchanged |
| Resource Flow | FLOW-### | An exchange of resources between nodes or performers |
| Interface | INT-### | A shared boundary between two systems or nodes |
| Measure | MOE/MOP-### | Measure of Effectiveness or Measure of Performance |
| Constraint | CON-### | A restriction or limitation on architecture elements |
| Standard | STD-### | A policy, guideline, or specification that applies to the architecture |
| Location | LOC-### | A geographic or logical location relevant to the architecture |
| Objective | OBJ-### | A desired state or outcome the architecture supports |
| Risk | RISK-### | A potential event or condition that could impact the architecture |

---

## Prohibited Terms in Domain Artifacts

These terms MUST NOT appear in generated DoDAF/JCIDS artifacts:

- AI, ML, machine learning, deep learning, neural network
- analytics, data science, big data
- cloud, cloud-native, serverless, microservices
- orchestration, pipeline, framework, agent
- Kafka, Redpanda, Neo4j, Watsonx, AWS, Azure, GCP
- LLM, GPT, language model, inference
- K9-AIF, K9, CrewAI, LangChain

These are implementation details — domain artifacts must use only DoDAF/JCIDS/SE vocabulary.

---

## Evidence-Grounding Rules

1. Use ONLY information explicitly present in the source document or approved prior-stage outputs
2. If a requested element is not supported → `NOT PROVIDED IN SOURCE`
3. NEVER invent stakeholders, capabilities, systems, services, interfaces, constraints, risks, requirements, KPPs, KSAs, KURs, timelines
4. Include verbatim evidence snippets where possible
5. Maintain neutral, professional, government-review-ready tone
6. Mark uncertainty explicitly
7. Preserve traceability from source text to derived output
8. Separate extracted facts from analysis
9. Every entity MUST have a supporting citation — if no citation exists, DO NOT output the entity
10. Label unconfirmed items as "Candidate" rather than asserting them as fact
