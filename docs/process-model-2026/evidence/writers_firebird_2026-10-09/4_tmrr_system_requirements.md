# System Requirements for the SRR

## System Requirements

The following system requirements are derived from the Capability Development Document (CDD) for FIREBIRD Increment 1. Each requirement includes a unique identifier, a "shall" statement, measurable thresholds/objectives, the verification method, and the source traceability.

**SR-001: Interoperability (KPP 1)**
*   **Statement:** The system shall achieve successful electronic data exchanges with DoD Command & Control networks via Link 16.
*   **Threshold:** 98% successful exchanges.
*   **Objective:** 100% seamless integration across joint Service architectures and allied networks.
*   **Verification Method:** Test (Interoperability testing with DoD C2 networks).
*   **Source:** CDD Section 4, KPP 1.

**SR-002: System Availability (KPP 2)**
*   **Statement:** The system shall maintain access and connectivity at a specified operational availability rate over a 72-hour surge period.
*   **Threshold:** 95% operational availability.
*   **Objective:** >= 98% mission-ready operational availability under sustained field conditions.
*   **Verification Method:** Test (Sustained operations test over 72 hours).
*   **Source:** CDD Section 4, KPP 2.

**SR-003: System Reliability (KPP 3)**
*   **Statement:** The system shall achieve a Mean Time Between Critical Failure (MTBCF) during continuous operations.
*   **Threshold:** >= 150 hours.
*   **Objective:** >= 300 hours with automated failover systems.
*   **Verification Method:** Analysis (Reliability modeling) and Test (Operational reliability testing).
*   **Source:** CDD Section 4, KPP 3.

**SR-004: Timeliness / Data Latency (KPP 4)**
*   **Statement:** The system shall deliver sensor telemetry and target tracking data to the tactical web query gateway within a specified latency.
*   **Threshold:** < 3 seconds.
*   **Objective:** Full-motion video and payload target coordinates delivered to application programs in < 1 second.
*   **Verification Method:** Test (Latency measurement during live data exchange).
*   **Source:** CDD Section 4, KPP 4.

**SR-005: Payload Capacity (Attribute 5)**
*   **Statement:** The Air Vehicle (AV) shall lift a minimum payload weight consisting of optical sensors and laser designators.
*   **Threshold:** Minimum 150 lbs.
*   **Objective:** Up to 350 lbs to include dual-band synthetic aperture radar and micro-munitions.
*   **Verification Method:** Test (Payload lift test).
*   **Source:** CDD Section 4, Attribute 5.

**SR-006: Launch Environment Compatibility**
*   **Statement:** The system shall be capable of ground launch via expeditionary pneumatic catapult and deployment from U.S. Navy ship classes including CVN 68, CG 47, DDG 51, and LHD 1.
*   **Threshold:** Successful launch and recovery from specified platforms.
*   **Objective:** NOT PROVIDED IN SOURCE (Specific success rate or environmental limits for launch not quantified in CDD).
*   **Verification Method:** Demonstration (Launch and recovery trials on specified platforms).
*   **Source:** CDD Section 2.

**SR-007: Autonomous Recovery and Reuse**
*   **Statement:** Unexpended platforms shall execute a safe autonomous return and be eligible for unlimited reuse.
*   **Threshold:** Safe autonomous return executed without operator intervention for recovery.
*   **Objective:** Unlimited reuse capability demonstrated.
*   **Verification Method:** Demonstration (Autonomous recovery test).
*   **Source:** CDD Section 2.

**SR-008: System Composition and Manpower**
*   **Statement:** The system shall consist of one (1) Mobile Ground Control Station (GCS) and eight (8) Air Vehicles (AV), crewed by 4 enlisted personnel per shift.
*   **Threshold:** Configuration matches 1 GCS + 8 AVs; Manpower matches 4 personnel/shift.
*   **Objective:** NOT PROVIDED IN SOURCE (No alternative configuration or reduced manpower objective stated).
*   **Verification Method:** Inspection (Configuration audit and manpower analysis).
*   **Source:** CDD Section 3.

**SR-009: Facilities and Spatial Constraints**
*   **Statement:** System components shall fit within standard ISU-90 shipping containers and satisfy shipboard spatial constraints for CG 47 and DDG 51 hangar bays.
*   **Threshold:** Physical fit within ISU-90 and specified hangar bays.
*   **Objective:** NOT PROVIDED IN SOURCE (No alternative spatial optimization objective stated).
*   **Verification Method:** Inspection (Physical fit check and dimensional analysis).
*   **Source:** CDD Section 5.

**SR-010: Spectrum Supportability**
*   **Statement:** Transmitters shall obtain spectrum certification in compliance with joint frequency management policies to operate within standard military S-band and Ku-band ranges.
*   **Threshold:** Certification obtained for S-band and Ku-band.
*   **Objective:** NOT PROVIDED IN SOURCE (No specific spectral efficiency or interference rejection objective stated).
*   **Verification Method:** Analysis (Spectrum compliance analysis) and Inspection (Certification documentation).
*   **Source:** CDD Section 5.

**SR-011: Weapons Safety Assurance**
*   **Statement:** The platform's remote weapon release mechanism shall incorporate three distinct physical/logical inhibits requiring explicit human-in-the-loop authorization.
*   **Threshold:** Three distinct inhibits present and functional; Human-in-the-loop authorization required.
*   **Objective:** NOT PROVIDED IN SOURCE (No additional safety layer objective stated).
*   **Verification Method:** Test (Safety interlock testing) and Inspection (Design review of inhibit logic).
*   **Source:** CDD Section 5.

**SR-012: Procurement Cost**
*   **Statement:** The target unit procurement cost shall not exceed a specified amount per system (1 GCS + 8 AVs) in FY2026 dollars.
*   **Threshold:** <= $4.5M per system.
*   **Objective:** NOT PROVIDED IN SOURCE (No lower cost objective stated).
*   **Verification Method:** Analysis (Cost estimation and affordability analysis).
*   **Source:** CDD Section 6.

**SR-013: Sustainment Cost**
*   **Statement:** Operating and support costs shall remain under a specified amount per flight hour over the 10-year service life.
*   **Threshold:** < $1,200 per flight hour.
*   **Objective:** NOT PROVIDED IN SOURCE (No lower cost objective stated).
*   **Verification Method:** Analysis (Life-cycle cost analysis).
*   **Source:** CDD Section 6.

## Traceability to the Requirement Document

The following table maps each System Requirement (SR) to its specific source in the Capability Development Document (CDD) and any relevant earlier stage results.

| SR ID | Requirement Statement Summary | Source Document Section | Source Specifics |
| :--- | :--- | :--- | :--- |
| SR-001 | Interoperability via Link 16 | CDD Section 4 | KPP 1: Interoperability |
| SR-002 | System Availability (95% / 98%) | CDD Section 4 | KPP 2: System Availability |
| SR-003 | System Reliability (MTBCF) | CDD Section 4 | KPP 3: System Reliability |
| SR-004 | Data Latency (< 3s / < 1s) | CDD Section 4 | KPP 4: Timeliness |
| SR-005 | Payload Capacity (150 lbs / 350 lbs) | CDD Section 4 | Attribute 5: Payload Capacity |
| SR-006 | Launch from Catapult/Naval Vessels | CDD Section 2 | Launch Environments |
| SR-007 | Autonomous Recovery/Reuse | CDD Section 2 | Recovery |
| SR-008 | 1 GCS + 8 AVs, 4 Personnel | CDD Section 3 | System Composition |
| SR-009 | Fit in ISU-90 / Naval Hangars | CDD Section 5 | Facilities |
| SR-010 | S-band/Ku-band Spectrum Cert | CDD Section 5 | Spectrum Supportability |
| SR-011 | 3 Inhibits + Human-in-Loop | CDD Section 5 | Weapons Safety Assurance |
| SR-012 | Unit Cost <= $4.5M | CDD Section 6 | Target Unit Procurement Cost |
| SR-013 | Sustainment < $1,200/hr | CDD Section 6 | Sustainment Cost Cap |

**Note on Earlier Stage Results:** The "Alternative Systems Review" (ASR) and "AoA Summary" confirm these requirements as the validated baseline for the Materiel Solution Analysis. No deviations or waivers were recorded in the provided decision logs.

## Consistency with the Preferred Materiel Solution and Support Concept

**Status: NOT PROVIDED IN SOURCE**

The SRR criteria require consistency with the preferred materiel solution and its support concept. However, the provided inputs indicate that the selection of the preferred materiel solution is the outcome of the Materiel Solution Analysis (MSA) phase, which concludes at Milestone A.

*   **Evidence Gap:** The "AoA Summary" explicitly states: "The selection of the preferred materiel solution is the outcome of the Materiel Solution Analysis (MSA) phase... Since the AoA analysis results, cost estimates, and risk assessments are not included in the provided inputs, a preferred solution cannot be identified or justified."
*   **Implication:** While the Milestone A decision is recorded as "APPROVED," the specific *preferred solution* (e.g., whether it is the "New Purpose-Built UAS" or another alternative) and its detailed support concept are not described in the provided text. Therefore, consistency cannot be verified against a specific solution architecture.
*   **Required Evidence:** The final AoA report identifying the selected alternative and the associated support concept plan.

## Technology Maturation Dependencies

The SRR criteria require consistency with technology maturation plans. The following dependencies are identified based on the requirements and the risk categories noted in the AoA Summary.

1.  **Autonomous Recovery and Reuse (SR-007):**
    *   **Dependency:** Technology for safe autonomous return in contested environments.
    *   **Risk:** Identified in AoA Summary under "Operational Risk" as requiring a level of autonomy and human-in-the-loop control.
    *   **Maturation Status:** NOT PROVIDED IN SOURCE. Specific Technology Readiness Levels (TRLs) for autonomous recovery are not listed.

2.  **High-Reliability Systems (SR-003):**
    *   **Dependency:** Technologies to achieve MTBCF >= 150 hours (Threshold) and >= 300 hours (Objective) with automated failover.
    *   **Risk:** Identified in AoA Summary under "Technical Risk" as a maturity requirement.
    *   **Maturation Status:** NOT PROVIDED IN SOURCE. Specific TRLs for reliability-enhancing technologies are not listed.

3.  **Low-Latency Data Processing (SR-004):**
    *   **Dependency:** Technologies to process and transmit sensor telemetry with < 3 seconds latency.
    *   **Risk:** Identified in AoA Summary under "Technical Risk."
    *   **Maturation Status:** NOT PROVIDED IN SOURCE. Specific TRLs for data processing/transmission are not listed.

4.  **Shipboard Integration (SR-006, SR-009):**
    *   **Dependency:** Integration technologies for CVN 68, CG 47, DDG 51, and LHD 1, including spatial fit and launch mechanisms.
    *   **Risk:** Identified in AoA Summary under "Integration Risk."
    *   **Maturation Status:** NOT PROVIDED IN SOURCE. Specific TRLs for shipboard integration are not listed.

**Note:** The inputs do not provide a Technology Maturation Plan (TMP) or specific TRL assessments for these dependencies.

## Interdependent Systems

The SRR criteria require consideration of the maturity of interdependent systems. The following interdependencies are identified from the CDD and ASR.

1.  **DoD Command & Control Networks (Link 16):**
    *   **Dependency:** The system relies on existing DoD C2 networks for interoperability (SR-001).
    *   **Maturity:** Assumed mature as it is an existing standard, but specific interface control documents (ICDs) or network availability guarantees are NOT PROVIDED IN SOURCE.

2.  **U.S. Navy Ship Classes (CVN 68, CG 47, DDG 51, LHD 1):**
    *   **Dependency:** The system must launch from and fit within these platforms (SR-006, SR-009).
    *   **Maturity:** These are existing platforms. However, the specific modifications or interfaces required for FIREBIRD Increment 1 are NOT PROVIDED IN SOURCE. The ASR notes "Integration Risk" regarding these platforms.

3.  **Tactical Web Query Gateway:**
    *   **Dependency:** The system must deliver data to this gateway (SR-004).
    *   **Maturity:** NOT PROVIDED IN SOURCE. The status and availability of this specific gateway are not described.

4.  **Joint Frequency Management Policies:**
    *   **Dependency:** Spectrum certification for S-band and Ku-band (SR-010).
    *   **Maturity:** Policies are established, but the specific certification process and timeline are NOT PROVIDED IN SOURCE.

## Verification Approach

The verification methods for each requirement are summarized below. The approach aligns with the "shall" statements and measurable thresholds defined in the CDD.

| SR ID | Verification Method | Description of Verification Activity |
| :--- | :--- | :--- |
| SR-001 | Test | Conduct interoperability tests with DoD C2 networks to measure success rate of Link 16 data exchanges. |
| SR-002 | Test | Perform a 72-hour surge operation test to measure operational availability and connectivity. |
| SR-003 | Analysis/Test | Perform reliability analysis (MTBCF calculation) and operational testing to validate failure rates. |
| SR-004 | Test | Measure latency of sensor telemetry and video data from source to gateway/application. |
| SR-005 | Test | Conduct payload lift tests with specified sensor and munition weights. |
| SR-006 | Demonstration | Demonstrate launch and recovery from pneumatic catapult and specified Navy ship classes. |
| SR-007 | Demonstration | Demonstrate autonomous return and reuse of unexpended platforms. |
| SR-008 | Inspection | Inspect system configuration (1 GCS + 8 AVs) and review manpower analysis for 4 personnel/shift. |
| SR-009 | Inspection | Physically inspect components for fit within ISU-90 containers and CG 47/DDG 51 hangar bays. |
| SR-010 | Analysis/Inspection | Review spectrum certification documentation and analyze transmitter compliance with S-band/Ku-band policies. |
| SR-011 | Test/Inspection | Test weapon release inhibits and inspect design for human-in-the-loop authorization logic. |
| SR-012 | Analysis | Perform cost analysis to verify unit procurement cost does not exceed $4.5M. |
| SR-013 | Analysis | Perform life-cycle cost analysis to verify sustainment costs remain under $1,200 per flight hour. |

## Open Items for the Review

The following items are open and require resolution or clarification by the human decision authority prior to or during the SRR:

1.  **Preferred Materiel Solution Identification:**
    *   **Issue:** The specific preferred solution selected during MSA is not explicitly named in the provided inputs. The AoA Summary states it is "NOT PROVIDED IN SOURCE."
    *   **Action Required:** The review board must confirm which alternative (e.g., New Purpose-Built UAS, Incremental Upgrade, etc.) was selected as the preferred solution at Milestone A to assess consistency.

2.  **Technology Readiness Levels (TRLs):**
    *   **Issue:** Specific TRLs for critical technologies (Autonomous Recovery, High Reliability, Low Latency, Shipboard Integration) are not provided.
    *   **Action Required:** The program office must provide the current TRLs and the maturation plan to reach TRL 6 or higher by the end of TMRR.

3.  **Interdependent System Maturity:**
    *   **Issue:** The maturity and availability of interdependent systems (DoD C2 Networks, Navy Ship Classes, Tactical Web Query Gateway) are not detailed.
    *   **Action Required:** Provide status updates on the readiness of these interdependent systems to support the FIREBIRD Increment 1 requirements.

4.  **Quantitative AoA Results:**
    *   **Issue:** The AoA Summary notes that specific quantitative results, effectiveness scores, and cost estimates for the alternatives are "NOT PROVIDED IN SOURCE."
    *   **Action Required:** Provide the completed AoA report with MOE/MOP scores, LCC estimates, and risk assessments to validate the selection of the preferred solution.

5.  **Spectrum Certification Timeline:**
    *   **Issue:** The timeline and process for obtaining spectrum certification for S-band and Ku-band are not specified.
    *   **Action Required:** Provide a plan and timeline for spectrum certification to ensure it does not delay TMRR milestones.

6.  **Weapons Safety Assurance Details:**
    *   **Issue:** The specific design of the three distinct physical/logical inhibits is not detailed.
    *   **Action Required:** Provide a design description or safety analysis report detailing the inhibit mechanisms and human-in-the-loop authorization process.

**Note:** This draft is for the human decision authority's review. No decision, approval, or recommendation of the gate is made in this document.