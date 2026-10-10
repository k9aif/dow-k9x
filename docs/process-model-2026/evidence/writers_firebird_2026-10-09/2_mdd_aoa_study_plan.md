# Draft AoA Study Guidance and Study Plan

## Purpose and Validated Requirement

**Purpose**
This document serves as the draft Analysis of Alternatives (AoA) Study Guidance and Study Plan for the FIREBIRD Group 3 UAS (Increment 1). It is prepared for the Materiel Decision Authority (MDA), the Army Acquisition Executive, to support the Materiel Development Decision (MDD). The MDD will establish the phase of entry and the initial review milestone for the program.

**Validated Requirement**
The requirement is derived from the Capability Development Document (CDD) for FIREBIRD Increment 1, validated by the Force Application Functional Capabilities Board. The core capability gap identified is the lack of a blend of prolonged endurance, zero-infrastructure deployment, and immediate kinetic response required to counter highly mobile, light-armored forces in contested maritime and littoral environments (CDD Section 1).

Key validated attributes include:
*   **Mission:** Locate, track, and destroy light-armored mobile forces (CDD Section 2).
*   **Deployment:** Ground-launched via expeditionary pneumatic catapult or from U.S. Navy ship classes (CVN 68, CG 47, DDG 51, LHD 1) (CDD Section 2).
*   **System Composition:** One Mobile Ground Control Station (GCS) and eight Air Vehicles (AV) per system, crewed by 4 enlisted personnel per shift (CDD Section 3).
*   **Quantity:** 112 baseline systems (92 Active, 10 Reserve, 10 War Reserve) (CDD Section 3).
*   **Service Life:** 10 Years (CDD Section 3).
*   **Affordability:** Unit procurement cost not to exceed $4.5M per system; sustainment cost under $1,200 per flight hour (CDD Section 6).

**Joint Staffing Designator Context**
The Joint Staffing Designator (JSD) recommendation identifies this program as "FCB Interest" due to joint dependencies on Navy infrastructure and Link 16 interoperability, despite Army validation and MDA authority (JSD Recommendation). This context informs the coalition interoperability and joint integration requirements within the AoA.

## Draft AoA Study Guidance

The AoA study shall be conducted in accordance with DoDI 5000.85 and applicable Service acquisition regulations. The study must address the following specific guidance points derived from the validated requirement:

1.  **Scope of Analysis:** The study must evaluate materiel solutions that satisfy the validated capability gap for Persistent Tactical Reconnaissance and Strike. Solutions must be capable of operating in contested maritime and littoral environments (CDD Section 1).
2.  **Deployment Constraints:** All alternatives must demonstrate compatibility with the specified launch environments: expeditionary pneumatic catapults and the flight/hangar decks of CVN 68, CG 47, DDG 51, and LHD 1 classes (CDD Section 2). Solutions must fit within standard ISU-90 shipping containers and satisfy shipboard spatial constraints for CG 47 and DDG 51 hangar bays (CDD Section 5).
3.  **Interoperability:** Alternatives must achieve at least 98% successful electronic data exchanges with DoD Command & Control networks via Link 16 (CDD Section 4, KPP 1). The study must assess the ability to integrate with allied networks as per the performance objective (CDD Section 4, KPP 1).
4.  **Sustainment and Logistics:** The study must evaluate the logistics footprint, including the requirement for 4 enlisted personnel per shift (CDD Section 3) and the sustainment cost cap of $1,200 per flight hour (CDD Section 6).
5.  **Safety and Security:** Alternatives must incorporate the required weapons safety assurance features, specifically three distinct physical/logical inhibits for remote weapon release requiring human-in-the-loop authorization (CDD Section 5).
6.  **Spectrum Management:** The study must verify that transmitter designs can obtain spectrum certification in compliance with joint frequency management policies for S-band and Ku-band operations (CDD Section 5).
7.  **Affordability:** The study must rigorously analyze life-cycle costs against the target unit procurement cost of $4.5M per system (CDD Section 6).

## Alternatives to Assess

The AoA must identify and analyze a range of alternatives, including the status quo. Alternatives must be derived strictly from the stated gaps and attributes in the CDD. No preferred solution is assumed.

1.  **Status Quo (Baseline):**
    *   Description: Continued reliance on current theater assets which lack the necessary blend of prolonged endurance, zero-infrastructure deployment, and immediate kinetic response (CDD Section 1).
    *   Analysis Focus: Quantify the operational shortfall, cost of current sustainment, and risk of mission failure in contested maritime environments.

2.  **Alternative 1: Incremental Upgrade of Existing Platforms**
    *   Description: Modification of existing tactical reconnaissance or strike platforms to meet the specific endurance, payload (150-350 lbs), and shipboard deployment requirements.
    *   Analysis Focus: Assess feasibility of retrofitting for Link 16 interoperability (98% threshold), MTBCF (>= 150 hours), and shipboard spatial constraints (CDD Section 4, Section 5). Evaluate cost against the $4.5M unit cost cap.

3.  **Alternative 2: New Purpose-Built Unmanned Aerial System (UAS)**
    *   Description: Development of a new UAS system specifically designed for the 1 GCS + 8 AV configuration, pneumatic catapult launch, and autonomous recovery.
    *   Analysis Focus: Assess technology maturity for the required MTBCF (>= 150 hours threshold, >= 300 hours objective), data latency (< 3 seconds threshold, < 1 second objective), and payload capacity (150-350 lbs) (CDD Section 4). Evaluate the risk of developing new shipboard integration for CVN 68, CG 47, DDG 51, and LHD 1 (CDD Section 2).

4.  **Alternative 3: Hybrid Manned-Unmanned Teaming (MUM-T) Solution**
    *   Description: A solution leveraging existing manned assets for command and control, with unmanned effectors for strike, if the "crewed by 4 enlisted personnel" requirement can be met through remote operations centers rather than onboard crew.
    *   Analysis Focus: Assess if this meets the "zero-infrastructure deployment" and "immediate kinetic response" gaps (CDD Section 1). Evaluate interoperability and latency requirements (CDD Section 4). *Note: The CDD specifies "crewed by 4 enlisted personnel per shift" (CDD Section 3), so this alternative must demonstrate how this staffing model is satisfied or if it constitutes a deviation requiring waiver.*

5.  **Alternative 4: Non-Materiel Solution (Procedural/Training)**
    *   Description: Reliance on existing assets with enhanced training and procedural changes to extend endurance or improve response times.
    *   Analysis Focus: Assess if this can close the gap in "prolonged endurance" and "immediate kinetic response" (CDD Section 1). Likely to be rejected if it cannot meet the KPPs for MTBCF and payload, but must be formally evaluated.

*Note: The specific number of alternatives to be analyzed will be determined by the study team based on the identification of viable technical approaches. The above are illustrative categories derived from the CDD gaps.*

## Measures of Effectiveness and Performance

The AoA must use the following Measures of Effectiveness (MOEs) and Measures of Performance (MOPs) derived from the CDD to evaluate alternatives.

**Measures of Effectiveness (MOEs)**
*   **Mission Success Rate:** Percentage of missions successfully completed to locate, track, and destroy light-armored mobile forces in contested maritime/littoral environments (CDD Section 1, Section 2).
*   **Response Time:** Time from detection to kinetic engagement, reflecting the "immediate kinetic response" requirement (CDD Section 1).
*   **Operational Availability:** Ability to maintain access/connectivity at a 95% operational availability rate over a 72-hour surge period (CDD Section 4, KPP 2).

**Measures of Performance (MOPs)**
*   **KPP 1: Interoperability**
    *   Threshold: 98% successful electronic data exchanges with DoD C2 networks via Link 16 (CDD Section 4).
    *   Objective: 100% seamless integration across joint Service architectures and allied networks (CDD Section 4).
*   **KPP 2: System Availability**
    *   Threshold: 95% operational availability over 72-hour surge (CDD Section 4).
    *   Objective: >= 98% mission-ready availability under sustained field conditions (CDD Section 4).
*   **KPP 3: System Reliability**
    *   Threshold: MTBCF >= 150 hours (CDD Section 4).
    *   Objective: MTBCF >= 300 hours with automated failover (CDD Section 4).
*   **KPP 4: Timeliness (Data Latency)**
    *   Threshold: Sensor telemetry/target tracking latency < 3 seconds (CDD Section 4).
    *   Objective: Full-motion video/payload coordinates < 1 second (CDD Section 4).
*   **Attribute 5: Payload Capacity**
    *   Threshold: Minimum 150 lbs (optical sensors/laser designators) (CDD Section 4).
    *   Objective: Up to 350 lbs (SAR/micro-munitions) (CDD Section 4).
*   **Deployment Compatibility**
    *   Fit within ISU-90 containers and CG 47/DDG 51 hangar bays (CDD Section 5).
    *   Launch from pneumatic catapult and CVN 68/CG 47/DDG 51/LHD 1 decks (CDD Section 2).
*   **Sustainment Cost**
    *   Operating and support costs < $1,200 per flight hour (CDD Section 6).
*   **Procurement Cost**
    *   Unit cost <= $4.5M per system (CDD Section 6).

## Cost, Schedule and Risk Analysis Approach

**Cost Analysis**
*   **Life-Cycle Cost (LCC):** The study must develop a detailed LCC estimate for each alternative, including procurement, operation, sustainment, and disposal over the 10-year service life (CDD Section 3, Section 6).
*   **Affordability Check:** All alternatives must be evaluated against the target unit procurement cost of $4.5M per system and the sustainment cost cap of $1,200 per flight hour (CDD Section 6).
*   **Total Procurement Cost:** Estimate the total cost for 112 systems (CDD Section 3).

**Schedule Analysis**
*   **Development Timeline:** Estimate the time required to mature critical technologies and reduce risk for each alternative.
*   **Fielding Timeline:** Assess the impact of each alternative on the ability to field 112 systems within the required timeframe to address the capability gap (CDD Section 1).
*   **Milestone Alignment:** Ensure the schedule supports entry into Technology Maturation and Risk Reduction (TMRR) and subsequent milestones.

**Risk Analysis**
*   **Technical Risk:** Assess the maturity of technologies required to meet the KPPs, particularly MTBCF (>= 150 hours) and data latency (< 3 seconds) (CDD Section 4).
*   **Integration Risk:** Evaluate the risk of integrating with Navy ship classes (CVN 68, CG 47, DDG 51, LHD 1) and Link 16 networks (CDD Section 2, Section 4).
*   **Sustainment Risk:** Assess the risk of meeting the $1,200 per flight hour sustainment cap (CDD Section 6).
*   **Operational Risk:** Evaluate the risk of operating in contested maritime environments with the required level of autonomy and human-in-the-loop control (CDD Section 1, Section 5).

## Study Organization, Resources and Schedule

**Study Organization**
*   **Lead Agency:** Army (as the validating authority and MDA) (CDD Header).
*   **Participating Agencies:** Navy (for shipboard integration and launch/recovery), Joint Staff (for Link 16 and spectrum management), and other relevant DoD components.
*   **Study Team:** A cross-functional team including systems engineers, cost analysts, logistics specialists, and subject matter experts from the Army and Navy.

**Resources**
*   **Personnel:** NOT PROVIDED IN SOURCE. The specific number of personnel required for the study team is not specified in the CDD or JSD. Evidence needed: A resource estimate from the Army Program Executive Office or the designated study lead.
*   **Funding:** NOT PROVIDED IN SOURCE. The funding source and amount for the AoA study are not specified in the CDD. Evidence needed: A budget request or funding allocation document for the AoA study.
*   **Facilities:** Access to test ranges, shipboard facilities (if available), and simulation environments for evaluating deployment and interoperability.

**Schedule**
*   **Start Date:** NOT PROVIDED IN SOURCE. The start date for the AoA study is not specified. Evidence needed: A program schedule or MDD decision date.
*   **Duration:** NOT PROVIDED IN SOURCE. The duration of the AoA study is not specified. Evidence needed: A study plan with a detailed timeline.
*   **Milestones:**
    *   Study Kickoff
    *   Alternatives Identification
    *   Analysis and Modeling
    *   Draft AoA Report
    *   Final AoA Report
    *   MDD Briefing

## Proposed Phase of Entry and Initial Review Milestone

**Proposed Phase of Entry**
The Materiel Development Decision (MDD) should approve entry into **Materiel Solution Analysis (MSA)**. This is the standard phase of entry for a new capability where the Analysis of Alternatives has not yet been completed. The AoA will be conducted during MSA to select the preferred materiel solution (SE Guidebook 3.1).

**Initial Review Milestone**
The initial review milestone should be **Milestone A**. Milestone A approves entry into Technology Maturation and Risk Reduction (TMRR), the acquisition strategy, and the release of the final RFP for TMRR. This aligns with the requirement to mature critical technologies and reduce risk before proceeding to Engineering and Manufacturing Development (EMD).

**Decision Requested**
The MDA is asked to decide on the phase of entry (MSA) and the initial review milestone (Milestone A) for the FIREBIRD Group 3 UAS (Increment 1) program, based on the validated requirement and the proposed AoA study guidance and plan.