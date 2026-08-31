# CAPABILITY DEVELOPMENT DOCUMENT (CDD) FOR SENTINEL INCREMENT 2

**Document Status:** Final / Unclassified
**Validation Authority:** Joint Requirements Oversight Council (Cyber)
**Milestone Decision Authority:** Air Force Acquisition Executive

## 1. Capability Discussion

This program addresses the capability gaps identified in the Initial
Capabilities Document (ICD) for Tactical Network Defense and Intrusion
Response. Current network defense tooling relies on manual triage and
signature-based detection, producing response times too slow to contain
lateral movement across contested tactical networks once an adversary
gains an initial foothold. Forward-deployed units lack an organic,
disconnected-operations-capable capability to detect, isolate, and
remediate intrusions without reachback to a fixed cyber operations center.

## 2. Concept of Operations (CONOPS) Summary

- **Primary Mission:** Detect, classify, and contain intrusions on
  tactical and garrison networks, including during denied, degraded,
  intermittent, or limited (DDIL) bandwidth conditions.
- **Deployment Model:** Software-defined sensor and response agents
  deployed on existing tactical network infrastructure; no new
  organic hardware fielding required beyond a ruggedized management
  appliance at the battalion S6 level.
- **Operator Force:** Operated by cyber protection team personnel
  embedded at brigade level, with autonomous baseline-anomaly
  detection continuing to function without an active operator present.

## 3. Program Summary

- **Acquisition Objective:** Fielding to 64 brigade combat team
  equivalents.
  - *Active Component:* 48 brigade sets
  - *National Guard/Reserve:* 16 brigade sets
- **System Composition:** One (1) Battalion Management Appliance and
  distributed sensor/response agent software licensed per network
  segment, administered by a 3-person cyber protection element per
  brigade.
- **Planned Service Life:** 8 Years, with a 2-year technology
  refresh cycle for detection models given the pace of adversary
  tradecraft evolution.

## 4. System Capabilities & Performance Parameters

Requirements are structured using Thresholds (T) — the minimum
acceptable operational value — and Objectives (O) — the desired
optimal capability.

| Key Performance Parameter (KPP) / Attribute | Performance Threshold (T) | Performance Objective (O) |
|---|---|---|
| **KPP 1: Detection Latency** | Identify anomalous lateral movement within 15 minutes of initial compromise. | Identify anomalous lateral movement within 2 minutes of initial compromise. |
| **KPP 2: DDIL Resilience** | Maintain full local detection and containment function with zero reachback connectivity for 72 hours. | Maintain full local detection and containment function with zero reachback connectivity indefinitely. |
| **KPP 3: False Positive Rate** | No more than 5 false-positive containment actions per 1,000 network endpoints per week. | No more than 1 false-positive containment action per 1,000 network endpoints per week. |
| **KPP 4: Interoperability** | Ingest and correlate telemetry from at least 90% of currently fielded tactical network hardware without a forklift upgrade. | Ingest and correlate telemetry from 100% of currently fielded and programmed tactical network hardware. |
| **Attribute 5: Containment Scope** | Isolate a compromised endpoint or segment within 5 minutes of confirmed detection, without operator action. | Isolate a compromised endpoint or segment within 60 seconds, with automatic rollback if isolation proves to be a false positive. |

## 5. Other DOTMLPF-P & Supportability Considerations

- **Training:** Cyber protection team personnel require a 4-week
  qualification course prior to independent operation; refresher
  certification required annually given detection-model updates.
- **Interoperability with Higher Echelon:** Alert and incident data
  must export in a format consumable by theater-level cyber
  operations centers without a bespoke translation layer.
- **Supply Chain Assurance:** All software components must pass
  supply-chain risk assessment; no component may depend on a single
  foreign-sourced code dependency without a documented waiver.

## 6. Program Affordability & Life-Cycle Cost

- **Target Unit Procurement Cost:** Shall not exceed $1.8M per
  brigade set (appliance plus 3-year software license) in FY2026
  dollars.
- **Sustainment Cost Cap:** Annual license renewal and detection-model
  update costs must remain under $250K per brigade set over the
  8-year service life.
