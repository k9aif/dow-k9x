# Alternative Systems Review

## Refined Joint Requirements

This section refines the validated requirements from the Capability Development Document (CDD) for FIREBIRD Increment 1, incorporating the context of joint dependencies identified in the Joint Staffing Designator (JSD) recommendation. The JSD identifies this program as "FCB Interest" due to joint dependencies on Navy infrastructure and Link 16 interoperability (AoA Study Plan, "Joint Staffing Designator Context").

**1. Operational Environment and Mission**
*   **Primary Mission:** Locate, track, and destroy light-armored mobile forces in contested maritime and littoral environments (CDD Section 1, Section 2).
*   **Deployment Modes:**
    *   Ground-launched via expeditionary pneumatic catapult (CDD Section 2).
    *   Deployed from U.S. Navy ship classes: CVN 68, CG 47, DDG 51, and LHD 1 (CDD Section 2).
*   **Recovery:** Unexpended platforms must execute a safe autonomous return and be eligible for unlimited reuse (CDD Section 2).

**2. System Composition and Manpower**
*   **Configuration:** One (1) Mobile Ground Control Station (GCS) and eight (8) Air Vehicles (AV) per system (CDD Section 3).
*   **Manpower:** Crewed by 4 enlisted personnel per shift (CDD Section 3).
*   **Quantity:** 112 baseline systems (92 Active Force, 10 Reserve Force, 10 War Reserve) (CDD Section 3).
*   **Service Life:** 10 Years (CDD Section 3).

**3. Key Performance Parameters (KPPs) and Attributes**
The following parameters are derived directly from CDD Section 4 and are critical for joint interoperability and operational effectiveness:

| Parameter | Threshold (Minimum Acceptable) | Objective (Desired Optimal) | Joint/Service Relevance |
| :--- | :--- | :--- | :--- |
| **KPP 1: Interoperability** | 98% successful electronic data exchanges with DoD C2 networks via Link 16. | 100% seamless integration across joint Service architectures and allied networks. | Critical for joint C2 integration (JSD Context). |
| **KPP 2: System Availability** | 95% operational availability over a 72-hour surge period. | >= 98% mission-ready availability under sustained field conditions. | Ensures sustained joint operations. |
| **KPP 3: System Reliability** | MTBCF >= 150 hours of continuous operations. | MTBCF >= 300 hours with automated failover systems. | Reduces sustainment burden on joint logistics. |
| **KPP 4: Timeliness** | Sensor telemetry/target tracking latency < 3 seconds. | Full-motion video/payload coordinates < 1 second. | Supports immediate kinetic response in contested environments. |
| **Attribute 5: Payload** | Minimum 150 lbs (optical sensors/laser designators). | Up to 350 lbs (dual-band SAR/micro-munitions). | Enables multi-role mission sets. |

**4. Supportability and Safety Constraints**
*   **Facilities:** Components must fit within standard ISU-90 shipping containers and satisfy shipboard spatial constraints for CG 47 and DDG 51 hangar bays (CDD Section 5).
*   **Spectrum:** Transmitters must obtain spectrum certification for S-band and Ku-band operations in compliance with joint frequency management policies (CDD Section 5).
*   **Weapons Safety:** Remote weapon release mechanism must incorporate three distinct physical/logical inhibits requiring explicit human-in-the-loop authorization (CDD Section 5).

**5. Affordability**
*   **Procurement:** Unit cost shall not exceed $4.5M per system (1 GCS + 8 AVs) in FY2026 dollars (CDD Section 6).
*   **Sustainment:** Operating and support costs must remain under $1,200 per flight hour over the 10-year service life (CDD Section 6).

## Initial Architecture for the Preferred Materiel Solution

**Status: NOT PROVIDED IN SOURCE**

The provided inputs include the validated requirement (CDD), the approved AoA Study Plan, and decision records for the Materiel Development Decision (MDD) and Service Validation. However, the inputs do not contain the completed Analysis of Alternatives (AoA) report, the selection of the preferred materiel solution, or any architectural diagrams or descriptions resulting from that selection.

The AoA Summary explicitly states: "The selection of the preferred materiel solution is the outcome of the Materiel Solution Analysis (MSA) phase... Since the AoA analysis results, cost estimates, and risk assessments are not included in the provided inputs, a preferred solution cannot be identified or justified" (AoA Summary, "Preferred Military Solution and Justification").

**Evidence Needed:**
To populate this section, the following evidence is required:
1.  The final AoA report identifying the selected preferred materiel solution (e.g., Alternative 2: New Purpose-Built UAS, or another variant).
2.  System architecture diagrams or descriptions detailing the integration of the 1 GCS and 8 AVs.
3.  Interface control documents or high-level interface descriptions for the Link 16, shipboard integration (CVN 68, CG 47, DDG 51, LHD 1), and pneumatic catapult launch systems.
4.  Technology maturity assessments for the selected solution's critical technologies.

## Draft System Performance Specification

This section drafts performance specification requirements based on the validated requirements in the CDD. These requirements are traceable to the CDD attributes and are stated conservatively to allow for design trade space during Technology Maturation and Risk Reduction (TMRR).

**1. General System Requirements**
*   **REQ-GEN-001:** The system shall consist of one (1) Mobile Ground Control Station (GCS) and eight (8) Air Vehicles (AV) per baseline system. *(Source: CDD Section 3)*
*   **REQ-GEN-002:** The system shall support a planned service life of 10 years. *(Source: CDD Section 3)*
*   **REQ-GEN-003:** The system shall be operable by 4 enlisted personnel per shift. *(Source: CDD Section 3)*

**2. Launch and Recovery**
*   **REQ-LR-001:** The Air Vehicles shall be capable of launch via expeditionary pneumatic catapult. *(Source: CDD Section 2)*
*   **REQ-LR-002:** The Air Vehicles shall be capable of deployment from the flight/hangar decks of U.S. Navy ship classes including CVN 68, CG 47, DDG 51, and LHD 1. *(Source: CDD Section 2)*
*   **REQ-LR-003:** Unexpended Air Vehicles shall execute a safe autonomous return and be eligible for unlimited reuse. *(Source: CDD Section 2)*

**3. Interoperability (KPP 1)**
*   **REQ-INT-001:** The system shall achieve a minimum of 98% successful electronic data exchanges with DoD Command & Control networks via Link 16. *(Source: CDD Section 4, KPP 1 Threshold)*
*   **REQ-INT-002:** The system shall support integration across joint Service architectures and allied networks to achieve seamless data exchange. *(Source: CDD Section 4, KPP 1 Objective)*

**4. Availability and Reliability (KPP 2 & 3)**
*   **REQ-AVL-001:** The system shall maintain access/connectivity at a 95% operational availability rate over a 72-hour surge period. *(Source: CDD Section 4, KPP 2 Threshold)*
*   **REQ-AVL-002:** The system shall achieve a mission-ready operational availability of >= 98% under sustained field conditions. *(Source: CDD Section 4, KPP 2 Objective)*
*   **REQ-RLB-001:** The system shall achieve a Mean Time Between Critical Failure (MTBCF) of >= 150 hours of continuous operations. *(Source: CDD Section 4, KPP 3 Threshold)*
*   **REQ-RLB-002:** The system shall achieve a Mean Time Between Critical Failure (MTBCF) of >= 300 hours with automated failover systems. *(Source: CDD Section 4, KPP 3 Objective)*

**5. Timeliness (KPP 4)**
*   **REQ-TML-001:** Sensor telemetry and target tracking data latency shall be < 3 seconds to the tactical web query gateway. *(Source: CDD Section 4, KPP 4 Threshold)*
*   **REQ-TML-002:** Full-motion video and payload target coordinates shall be delivered to application programs in near real-time (< 1 second). *(Source: CDD Section 4, KPP 4 Objective)*

**6. Payload Capacity (Attribute 5)**
*   **REQ-PLD-001:** The Air Vehicles shall lift a minimum of 150 lbs consisting of optical sensors and laser designators. *(Source: CDD Section 4, Attribute 5 Threshold)*
*   **REQ-PLD-002:** The Air Vehicles shall lift up to 350 lbs to include dual-band synthetic aperture radar and micro-munitions. *(Source: CDD Section 4, Attribute 5 Objective)*

**7. Supportability and Safety**
*   **REQ-SUP-001:** System components shall fit within standard ISU-90 shipping containers. *(Source: CDD Section 5)*
*   **REQ-SUP-002:** System components shall satisfy shipboard spatial constraints for CG 47 and DDG 51 hangar bays. *(Source: CDD Section 5)*
*   **REQ-SUP-003:** Transmitters shall obtain spectrum certification in compliance with joint frequency management policies to operate within standard military S-band and Ku-band ranges. *(Source: CDD Section 5)*
*   **REQ-SAF-001:** The remote weapon release mechanism shall incorporate three distinct physical/logical inhibits. *(Source: CDD Section 5)*
*   **REQ-SAF-002:** The remote weapon release mechanism shall require explicit human-in-the-loop authorization. *(Source: CDD Section 5)*

**8. Affordability**
*   **REQ-CST-001:** The unit procurement cost shall not exceed $4.5M per system (1 GCS + 8 AVs) in FY2026 dollars. *(Source: CDD Section 6)*
*   **REQ-CST-002:** Operating and support costs shall remain under $1,200 per flight hour over the 10-year service life. *(Source: CDD Section 6)*

## Preferred Materiel Solution Rationale, Assumptions and Constraints

**Status: NOT PROVIDED IN SOURCE**

The inputs do not provide the rationale for the selection of a preferred materiel solution, as the Analysis of Alternatives (AoA) has not been completed with results. The AoA Summary states: "The selection of the preferred materiel solution is the outcome of the Materiel Solution Analysis (MSA) phase... Since the AoA analysis results, cost estimates, and risk assessments are not included in the provided inputs, a preferred solution cannot be identified or justified" (AoA Summary, "Preferred Military Solution and Justification").

**Assumptions (Derived from CDD and AoA Plan):**
*   The program will proceed through Materiel Solution Analysis (MSA) to select a preferred solution, as approved in the MDD decision of record (MDD Decision Record).
*   The preferred solution must satisfy the validated requirements in the CDD, including the specific KPPs for interoperability, availability, reliability, timeliness, and payload (CDD Section 4).
*   The solution must be compatible with the specified launch environments (pneumatic catapult, Navy ship decks) and supportability constraints (ISU-90, hangar bays) (CDD Section 2, Section 5).
*   The solution must meet the affordability caps of $4.5M per system and $1,200 per flight hour (CDD Section 6).

**Constraints:**
*   **Joint Dependencies:** The solution must integrate with Navy infrastructure and Link 16 networks, as identified in the JSD recommendation (AoA Study Plan, "Joint Staffing Designator Context").
*   **Manpower:** The solution must be operable by 4 enlisted personnel per shift (CDD Section 3).
*   **Safety:** The solution must incorporate the required weapons safety assurance features (CDD Section 5).
*   **Spectrum:** The solution must comply with joint frequency management policies for S-band and Ku-band (CDD Section 5).

**Evidence Needed:**
To populate this section, the following evidence is required:
1.  The final AoA report detailing the comparison of alternatives (Status Quo, Incremental Upgrade, New Purpose-Built UAS, MUM-T, Non-Materiel) against the MOEs and MOPs.
2.  The justification for selecting the preferred solution, including cost, schedule, and risk analysis.
3.  Any assumptions or constraints specific to the selected solution that were not present in the general CDD.

## Risk Assessment

This section identifies critical technologies and key interfaces with supporting or enabling systems, along with mitigation strategies in development. While specific risk ratings are NOT PROVIDED IN SOURCE, the following risks are identified based on the CDD requirements and the AoA Study Plan's risk analysis approach.

**1. Critical Technology Risks**

| Risk Area | Description | Mitigation in Development |
| :--- | :--- | :--- |
| **Reliability (MTBCF)** | Achieving MTBCF >= 150 hours (threshold) and >= 300 hours (objective) for continuous operations in contested environments. (CDD Section 4, KPP 3) | Conduct technology maturation in TMRR to validate reliability models. Implement automated failover systems as per the objective. Perform rigorous testing and validation of critical components. |
| **Data Latency** | Achieving sensor telemetry/target tracking latency < 3 seconds (threshold) and < 1 second (objective) for full-motion video. (CDD Section 4, KPP 4) | Develop high-bandwidth, low-latency data links. Optimize data processing algorithms. Validate latency performance in simulated and live environments during TMRR. |
| **Payload Capacity** | Lifting 150 lbs (threshold) to 350 lbs (objective) including SAR and micro-munitions. (CDD Section 4, Attribute 5) | Design airframes and propulsion systems with sufficient margin. Validate payload integration and performance during prototyping. |
| **Autonomous Recovery** | Executing safe autonomous return and unlimited reuse of unexpended platforms. (CDD Section 2) | Develop and test autonomous recovery algorithms. Validate recovery procedures in various environmental conditions. |

**2. Key Interface Risks**

| Interface | Description | Mitigation in Development |
| :--- | :--- | :--- |
| **Link 16 Interoperability** | Achieving 98% successful electronic data exchanges with DoD C2 networks via Link 16. (CDD Section 4, KPP 1) | Conduct joint interoperability testing with DoD C2 networks. Validate Link 16 message formats and protocols. Engage with Joint Staff for spectrum and protocol compliance. |
| **Navy Shipboard Integration** | Deployment from CVN 68, CG 47, DDG 51, and LHD 1 decks and hangar bays. (CDD Section 2, Section 5) | Coordinate with Navy for shipboard integration requirements. Validate spatial constraints and launch/recovery procedures on representative ship models or actual ships. |
| **Pneumatic Catapult Launch** | Launch via expeditionary pneumatic catapult. (CDD Section 2) | Develop and test catapult interface and launch procedures. Validate structural integrity of AVs during catapult launch. |
| **Spectrum Certification** | Obtaining spectrum certification for S-band and Ku-band operations. (CDD Section 5) | Engage with Joint Frequency Management early in the design process. Conduct spectrum compatibility analysis and testing. |

**3. Sustainment and Logistics Risks**

| Risk Area | Description | Mitigation in Development |
| :--- | :--- | :--- |
| **Sustainment Cost** | Keeping operating and support costs under $1,200 per flight hour. (CDD Section 6) | Design for maintainability and reliability. Optimize logistics footprint (ISU-90 compatibility). Conduct life-cycle cost analysis during TMRR. |
| **Manpower Efficiency** | Operating with 4 enlisted personnel per shift. (CDD Section 3) | Design user interfaces and automation to minimize manpower requirements. Validate operational procedures with user representatives. |

**Evidence Needed:**
To complete this section with specific risk ratings and detailed mitigation plans, the following evidence is required:
1.  Technology Readiness Level (TRL) assessments for the critical technologies identified.
2.  Interface Control Documents (ICDs) for Link 16, Navy shipboard systems, and pneumatic catapult.
3.  Risk management plan detailing probability and impact assessments for each risk.
4.  Detailed mitigation strategies and verification methods for each risk.

## ASR Criteria Status

This section tracks the status of the Alternative Systems Review (ASR) criteria based on the provided inputs.

| ASR Criterion | Status | Evidence/Comment |
| :--- | :--- | :--- |
| **Validated Requirement** | **Complete** | The Capability Development Document (CDD) for FIREBIRD Increment 1 is provided and validated by the Force Application Functional Capabilities Board (CDD Header). |
| **AoA Study Plan** | **Complete** | The Draft AoA Study Guidance and Study Plan is provided and approved as part of the MDD decision (AoA Study Plan, MDD Decision Record). |
| **Preferred Materiel Solution Selection** | **Not Complete** | The AoA Summary states that the preferred solution cannot be identified because the AoA analysis results are not provided (AoA Summary, "Preferred Military Solution and Justification"). |
| **Initial Architecture** | **Not Complete** | No architectural diagrams or descriptions for the preferred solution are provided (AoA Summary, "Preferred Military Solution