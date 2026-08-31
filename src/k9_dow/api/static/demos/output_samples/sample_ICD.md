# Initial Capabilities Document (ICD)

## DRAFT — FOR DEMONSTRATION PURPOSES ONLY

**Job ID:** JOB-20260628-DEMO01
**Date:** 28 June 2026
**Status:** Awaiting HIL Review (JROC-VALIDATION)
**Classification:** UNCLASSIFIED — PROOF OF CONCEPT
**LLM Model:** granite3-dense:2b (Proof of Concept — production deployment would use a full-scale LLM)

---

## 1. Architecture Views

### 1.1 Model Elements (Capabilities, Requirements, Systems)

**Capability Needs:**

| ID | Title | Description |
|---|---|---|
| CN-001 | Improved Maintenance Workflow | A more integrated, predictive, and digitally traceable approach to F-22 maintenance and mission readiness |
| CN-002 | Subsystem Health Monitoring | Enhanced diagnostic accuracy for hydraulic system, electronic warfare suite, and weapons interface integrity |
| CN-003 | Digital Traceability | Unified digital traceability across Maintenance_Event records to correlate subsystem failures to mission profiles |

**System Engineering Requirements:**

| ID | Shall Text | Type | Verification |
|---|---|---|---|
| SR-001 | Identify capability gaps in the maintenance and diagnostics workflow | Capability Gap Identification | Analysis |
| SR-002 | Recommended improvements to operational activities supporting aircraft readiness | Operational Improvement | Demonstration |
| SR-003 | Assessment of existing system interfaces across radar, EW suite, VMS, PTMS, and SMS | System Interface Assessment | Inspection |
| SR-004 | Suggested enhancements to data integration between MCS, System Health Monitoring service, and mission planning subsystems | Data Integration Enhancement | Test |
| SR-005 | DOTMLPF-P analysis focusing on doctrine, training, personnel skills, and facility constraints relevant to F-22 support conditions | DOTMLPF-P Analysis | Analysis |
| SR-006 | A synthesized architectural view (OV/SV/CV) to support decision-making for modernization programs | Architectural View Synthesis | Demonstration |

**Technical Baseline Items:**

| ID | Name | Subsystem |
|---|---|---|
| TBI-001 | Hydraulic System Monitoring | Hydraulic System |
| TBI-002 | Subsystem Initialization | Electronic Warfare Suite |
| TBI-003 | Data Transfer from MDF Loader | Onboard Avionics Package |
| TBI-004 | Weapons Rail Verification | Stores Management System (SMS) |
| TBI-005 | MIL-STD-1760 Compliance Check | Weapons Interface |

**Traceability:**

| Capability Need | Traced Requirements |
|---|---|
| CN-001 | SR-001, SR-002 |
| CN-002 | SR-003, SR-004 |
| CN-003 | SR-004, SR-005, SR-006 |

---

### 1.2 Operational View (OV-1)

**OV-1: High-Level Operational Concept — F-22 Raptor Maintenance & Mission Readiness**

**Operational Context:**
The 325th Maintenance Squadron operates the F-22 Raptor fleet under high-tempo training and mission scenarios. The current maintenance workflow is reactive, with inconsistent diagnostic accuracy and incomplete data traceability across subsystems.

**Operational Activities:**

| ID | Activity | Description |
|---|---|---|
| ACT-001 | Pre-Flight Diagnostics | Maintenance crews perform subsystem checks including hydraulic readings, subsystem initialization, and MDF data transfer verification |
| ACT-002 | Subsystem Health Monitoring | Continuous monitoring of radar, EW suite, VMS, PTMS, and SMS during operations |
| ACT-003 | Weapons Load Validation | MIL-STD-1760 compliance checks and torque validation for AIM-120 training rounds |
| ACT-004 | Maintenance Event Recording | Digital capture of maintenance activities with traceability to mission profiles |
| ACT-005 | Mission Planning Integration | Data exchange between MCS, System Health Monitoring, and mission planning subsystems |

**System Nodes:**

| ID | Node | Function |
|---|---|---|
| NODE-001 | Maintenance Control System (MCS) | Central maintenance management and scheduling |
| NODE-002 | System Health Monitoring Service | Real-time subsystem health data collection |
| NODE-003 | Vehicle Management System (VMS) | Aircraft vehicle systems control |
| NODE-004 | Power Thermal Management System (PTMS) | Power and thermal management |
| NODE-005 | Stores Management System (SMS) | Weapons and stores management |
| NODE-006 | Mission Data File Loader | Mission data programming and transfer |

*Source citation: "The 325th Maintenance Squadron requests an architectural assessment and recommendation package to improve the F-22 Raptor's maintenance workflow, subsystem health monitoring, and weapons load validation processes."*

---

### 1.3 Cross-View Consistency Report

**Cross-View Consistency Analysis:**

1. **Entities in OV views appear in corresponding system descriptions:**
   - CAP-001 (F-22 Maintenance System) — Referenced in requirements SR-001 through SR-006. **CONSISTENT**
   - ACT-001 through ACT-005 — All trace to identified capability needs. **CONSISTENT**

2. **Capabilities trace to operational activities:**
   - CN-001 (Improved Maintenance Workflow) → ACT-001, ACT-004. **CONSISTENT**
   - CN-002 (Subsystem Health Monitoring) → ACT-002. **CONSISTENT**
   - CN-003 (Digital Traceability) → ACT-004, ACT-005. **CONSISTENT**

3. **System interfaces across subsystems:**
   - MCS ↔ System Health Monitoring: Data exchange defined. **CONSISTENT**
   - MCS ↔ Mission Planning: Integration gap identified. **WARNING** — SR-004 addresses this gap
   - VMS ↔ PTMS: Interface not fully specified in source. **INFO** — requires further elicitation

4. **Standards compliance:**
   - MIL-STD-1760 referenced for weapons interface. **CONSISTENT**
   - No other standards explicitly referenced in source document. **INFO** — TV-1 view requires additional standards identification

**Overall Consistency Score: 85%**
**Critical Issues: 0 | Warnings: 1 | Info: 2**

---

## 2. Gate Readiness Assessment

### 2.1 Gate Entry Criteria

Loaded 5 entry criteria for gate JROC-VALIDATION:

1. Capability need statement complete
2. Requirements traceability coverage >= 90%
3. DoDAF views generated and consistency-checked
4. No critical invariant violations
5. Evidence package assembled

### 2.2 Evidence Summary

| Criterion | Evidence | Status |
|---|---|---|
| Capability need statement | CN-001, CN-002, CN-003 identified from source document | Available |
| Requirements traceability | SR-001 through SR-006 traced to capability needs | Available |
| DoDAF views generated | OV-1 generated with 5 operational activities, 6 system nodes | Available |
| Cross-view consistency | 85% consistency score, 0 critical issues | Available |
| Evidence package | Technical baseline items TBI-001 through TBI-005 documented | Available |

**Missing Evidence:**
- SV-1 (System Interface Description) — NOT PROVIDED IN SOURCE
- CV-1 (Capability Vision) — NOT PROVIDED IN SOURCE
- TV-1 (Standards Profile) — Only MIL-STD-1760 referenced

### 2.3 Readiness Score

| Criterion | Score | Rationale |
|---|---|---|
| Capability need statement complete | MET | Three capability needs identified with clear descriptions |
| Requirements traceability >= 90% | PARTIALLY_MET | 6 requirements trace to capability needs, but SV/CV views not yet generated |
| DoDAF views generated | PARTIALLY_MET | OV-1 generated; SV-1, CV-1, TV-1 pending |
| No critical invariant violations | MET | Cross-view consistency check passed with 0 critical issues |
| Evidence package assembled | PARTIALLY_MET | Technical baseline documented; formal package pending assembly |

**Overall Readiness Score: 65/100**

**Blockers:**
- SV-1, CV-1, TV-1 views not yet generated
- Formal evidence package not assembled

**Recommendation:** Address remaining view generation before proceeding to JROC validation gate.

### 2.4 Gap Analysis

| Gap ID | Description | Impact | Remediation | Effort |
|---|---|---|---|---|
| GAP-001 | SV-1 System Interface Description not generated | Blocker | Generate SV-1 from system nodes and interface requirements | Medium (2-3 days) |
| GAP-002 | CV-1 Capability Vision not generated | Blocker | Generate CV-1 from capability needs and operational activities | Medium (2-3 days) |
| GAP-003 | TV-1 Standards Profile incomplete | Risk-acceptance | Identify applicable standards beyond MIL-STD-1760 | Low (1-2 days) |
| GAP-004 | DOTMLPF-P analysis not completed | Risk-acceptance | Conduct analysis focusing on doctrine, training, and personnel constraints | Medium (3-5 days) |
| GAP-005 | Data integration assessment incomplete | Risk-acceptance | Detailed assessment of MCS-SHM-Mission Planning data flows | Medium (2-4 days) |

**Summary:** 2 blockers require resolution before gate review. 3 items can proceed with risk-acceptance.

---

## 3. Review Package

### 3.1 Artifact Manifest

| Artifact | Type | Status | Location |
|---|---|---|---|
| Source Document | F-22 Maintenance Readiness Assessment Request | Available | Uploaded |
| Model Elements | Capabilities, Requirements, Technical Baseline | Generated | Pipeline output |
| OV-1 Operational View | DoDAF Architecture View | Generated | Pipeline output |
| Cross-View Consistency Report | Quality Assessment | Generated | Pipeline output |
| Gate Readiness Score | Assessment (65/100) | Generated | Pipeline output |
| Gap Analysis | 5 gaps identified, 2 blockers | Generated | Pipeline output |
| SV-1 System Interface Description | DoDAF Architecture View | NOT GENERATED | Pending |
| CV-1 Capability Vision | DoDAF Architecture View | NOT GENERATED | Pending |

### 3.2 Completeness Assessment

**Generated Artifacts: 6/8 (75%)**

- Source document analysis: Complete
- Model element extraction: Complete (3 capability needs, 6 requirements, 5 technical baseline items)
- OV-1 view generation: Complete (5 activities, 6 nodes)
- Cross-view consistency: Complete (85% score)
- Gate readiness scoring: Complete (65/100)
- Gap analysis: Complete (5 gaps, 2 blockers)

**Missing Artifacts:**
- SV-1 System Interface Description — Required for gate review
- CV-1 Capability Vision — Required for gate review

**Recommendation:** Package is 75% complete. Resolve 2 blocker gaps before submitting for JROC validation.

### 3.3 Package Summary

**JROC-VALIDATION Review Package**

**Program:** F-22 Raptor Maintenance & Mission Readiness Enhancement
**Requesting Organization:** 325th Maintenance Squadron
**Gate:** JROC-VALIDATION (Non-delegable)
**Readiness Score:** 65/100
**Package Completeness:** 75%

**Executive Summary:**
The 325th Maintenance Squadron has identified three core capability needs for improving F-22 maintenance workflow, subsystem health monitoring, and digital traceability. Six system engineering requirements have been derived and traced to these capability needs. An OV-1 operational view has been generated identifying 5 operational activities and 6 system nodes. Cross-view consistency analysis shows 85% consistency with no critical issues.

**Blockers (2):**
1. GAP-001: SV-1 System Interface Description not generated
2. GAP-002: CV-1 Capability Vision not generated

**Risk-Acceptance Items (3):**
3. GAP-003: TV-1 Standards Profile incomplete
4. GAP-004: DOTMLPF-P analysis not completed
5. GAP-005: Data integration assessment incomplete

**Decision Required:**
Human authority must review this package and decide whether to:
- **APPROVE** — proceed with risk-acceptance on remaining gaps
- **REMEDIATE** — address blockers before resubmission
- **REJECT** — return for fundamental rework

*This package was prepared by the DAS pipeline. The decision is non-delegable and must be made by an authorized human decision authority.*

---

*Generated by DAS (Defense Acquisition System) — Built on K9-AIF Framework*
*28 June 2026 | JOB-20260628-DEMO01*
