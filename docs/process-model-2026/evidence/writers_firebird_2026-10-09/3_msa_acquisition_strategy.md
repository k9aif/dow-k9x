# Proposed Acquisition Strategy

## Recommended Pathway and Rationale

**Recommended Pathway:** Major Capability Acquisition

**Rationale for Selection:**
The requirement for FIREBIRD Group 3 UAS (Increment 1) exhibits the characteristics of a Major Capability Acquisition under DoDI 5000.85. The program involves the development of a new, complex materiel system (1 Mobile Ground Control Station + 8 Air Vehicles) with significant technical risk and joint dependencies.
*   **Complexity and New Development:** The CDD identifies a capability gap requiring a blend of prolonged endurance, zero-infrastructure deployment, and immediate kinetic response (CDD Section 1). The AoA Study Plan identifies "New Purpose-Built Unmanned Aerial System" as a primary alternative, indicating a need for significant technology maturation and risk reduction (AoA Study Plan, "Alternatives to Assess," Item 3).
*   **Joint Dependencies:** The Joint Staffing Designator (JSD) recommendation identifies this program as "FCB Interest" due to dependencies on Navy infrastructure (CVN 68, CG 47, DDG 51, LHD 1) and Link 16 interoperability (AoA Study Plan, "Joint Staffing Designator Context"). This level of cross-service integration and infrastructure compatibility typically exceeds the scope of Middle Tier or Software-only pathways.
*   **Scale and Cost:** The acquisition objective is 112 baseline systems with a unit procurement cost target of $4.5M per system (CDD Section 3, Section 6). While the total program cost is not explicitly stated as exceeding the MDAP threshold in the provided text, the complexity of the system, the requirement for autonomous recovery, and the multi-service deployment environment align with the Major Capability Acquisition framework which mandates a full Analysis of Alternatives (AoA) and Technology Maturation and Risk Reduction (TMRR) phase.

**Why Other Pathways Do Not Fit:**
*   **Middle Tier of Acquisition:** This pathway is generally for programs with lower complexity or lower cost thresholds. The FIREBIRD requirement involves complex autonomous systems, multi-service shipboard integration, and high-reliability requirements (MTBCF >= 150 hours) that suggest a higher level of technical risk and integration complexity than typical Middle Tier programs.
*   **Software Acquisition:** The requirement is for a materiel system (Air Vehicles and GCS), not just software. While software is a component, the primary deliverable is a physical platform with kinetic and sensor capabilities (CDD Section 2, Section 4).
*   **Urgent Capability Acquisition:** The CDD does not indicate an immediate, time-critical need that would preclude a standard acquisition process. The requirement is for a baseline capability with a 10-year service life (CDD Section 3), suggesting a planned, deliberate acquisition rather than an urgent stopgap.
*   **Defense Business Systems:** This pathway applies to enterprise-level business systems, not tactical combat platforms.
*   **Acquisition of Services:** The requirement is for the procurement of materiel (systems), not services.

## Business Approach and Contracting

**Business Approach:**
The business approach will follow the standard Major Capability Acquisition sequence:
1.  **Materiel Solution Analysis (MSA):** Conduct the Analysis of Alternatives (AoA) to select the preferred materiel solution. The AoA Study Plan has been approved as part of the MDD (AoA Study Plan, "Proposed Phase of Entry").
2.  **Technology Maturation and Risk Reduction (TMRR):** Upon Milestone A approval, enter TMRR to mature critical technologies and reduce risk. This phase will include competitive prototyping where planned (DoDI 5000.85).
3.  **Engineering and Manufacturing Development (EMD):** Following successful completion of TMRR and Milestone B approval, enter EMD.
4.  **Production and Deployment:** Following Milestone C approval, proceed to production and deployment of the 112 baseline systems (CDD Section 3).

**Contracting Strategy:**
*   **TMRR Contracting:** The Milestone A decision will approve the release of the final Request for Proposal (RFP) for TMRR (DoDI 5000.85). The RFP will be structured to allow for competitive prototyping to validate the preferred solution's performance against the KPPs (CDD Section 4).
*   **EMD Contracting:** The Engineering and Manufacturing Development (EMD) contract will be awarded after Milestone B approval. The strategy will likely involve a cost-plus-incentive-fee (CPIF) or fixed-price-incentive-firm (FPIF) structure during EMD to manage development risk, transitioning to a firm fixed-price (FFP) structure for production (CDD Section 6 affordability constraints).
*   **Small Business Participation:** The strategy will include a plan to maximize small business participation in the supply chain, particularly for sub-components and sustainment services, to support the $1,200 per flight hour sustainment cost cap (CDD Section 6).

## Intellectual Property, Program Protection and Exportability

**Intellectual Property (IP):**
*   **Government Rights:** The government will retain full rights to data and IP generated under government-funded development contracts, consistent with FAR 52.227-11. This is critical for the 10-year service life and potential future upgrades (CDD Section 3).
*   **Proprietary Data:** Any proprietary data submitted by contractors must be clearly marked and justified. The program office will review all proprietary data submissions to ensure they are necessary for the performance of the contract and do not unduly restrict competition or government use.

**Program Protection:**
*   **Security Requirements:** The system will operate in contested maritime and littoral environments (CDD Section 1). Program protection measures will include secure data handling, physical security for prototypes, and access controls for sensitive technical data.
*   **Cybersecurity:** See the Cybersecurity section below.

**Exportability:**
*   **ITAR/EAR Compliance:** The system includes kinetic capabilities (micro-munitions) and advanced sensors (SAR), which are likely subject to the International Traffic in Arms Regulations (ITAR). The program office will coordinate with the Directorate of Defense Trade Controls (DDTC) to determine export control classifications.
*   **Allied Integration:** The KPP 1 objective includes "100% seamless integration across joint Service architectures and allied networks" (CDD Section 4). The strategy will include early engagement with allied partners to assess exportability and interoperability requirements, ensuring that design choices do not preclude future allied sales or integration.

## Cybersecurity

**Cybersecurity Planning:**
*   **Zero Trust Architecture:** The system will implement a Zero Trust architecture to protect against cyber threats in contested environments. This includes strict identity verification, least privilege access, and continuous monitoring.
*   **Data Link Security:** The Link 16 interoperability requirement (KPP 1) mandates secure data exchanges. The strategy will include the use of encrypted data links and robust authentication mechanisms to prevent interception or spoofing.
*   **Autonomous Systems Security:** Given the requirement for autonomous recovery and human-in-the-loop authorization for weapon release (CDD Section 2, Section 5), the cybersecurity plan will include specific protections for the autonomous decision-making algorithms to prevent manipulation or denial of service.
*   **Compliance:** The system will comply with DoD Cybersecurity Strategy and applicable NIST standards. The program office will conduct regular cybersecurity assessments and penetration testing during TMRR and EMD.

## Test Strategy

**Test Strategy Overview:**
The test strategy will be risk-based, focusing on validating the Key Performance Parameters (KPPs) and critical interfaces.

**Phased Testing:**
1.  **TMRR Testing:**
    *   **Component Testing:** Validate individual components (sensors, actuators, data links) against their specifications.
    *   **Subsystem Testing:** Integrate and test subsystems (e.g., GCS + AV communication, catapult launch interface).
    *   **Prototype Testing:** Conduct flight tests of prototypes to validate performance against KPPs (CDD Section 4). This includes testing in simulated contested maritime environments.
    *   **Interoperability Testing:** Conduct joint interoperability testing with DoD C2 networks via Link 16 (CDD Section 4, KPP 1).
    *   **Shipboard Integration Testing:** Validate deployment and recovery from representative ship models or actual ships (CVN 68, CG 47, DDG 51, LHD 1) (CDD Section 2).
2.  **EMD Testing:**
    *   **System Testing:** Full system integration and performance validation.
    *   **Environmental Testing:** Validate performance in extreme environmental conditions (temperature, humidity, salt spray) relevant to maritime operations.
    *   **Reliability Testing:** Conduct Mean Time Between Critical Failure (MTBCF) testing to validate the >= 150 hours threshold and >= 300 hours objective (CDD Section 4, KPP 3).
    *   **Weapons Safety Testing:** Validate the three distinct physical/logical inhibits and human-in-the-loop authorization for weapon release (CDD Section 5).
3.  **Acceptance Testing:**
    *   **Operational Test and Evaluation (OT&E):** Conduct OT&E to validate the system's effectiveness in meeting the mission requirements (CDD Section 1, Section 2).
    *   **Sustainment Testing:** Validate the sustainment cost and logistics footprint (ISU-90 compatibility) (CDD Section 5, Section 6).

**Test Resources:**
*   **Facilities:** Access to test ranges, shipboard facilities, and simulation environments (AoA Study Plan, "Resources").
*   **Personnel:** Cross-functional team including systems engineers, test engineers, and subject matter experts from the Army and Navy (AoA Study Plan, "Study Organization").

## TMRR Plan: Technologies to Mature and Trade Space

**Technologies to Mature:**
1.  **Autonomous Recovery and Reuse:** The requirement for "safe autonomous return and be eligible for unlimited reuse" (CDD Section 2) is a critical technology. TMRR will focus on maturing the autonomous navigation, landing, and recovery algorithms to ensure reliability and safety.
2.  **High-Reliability Avionics and Propulsion:** Achieving MTBCF >= 150 hours (threshold) and >= 300 hours (objective) requires highly reliable avionics and propulsion systems. TMRR will involve maturing these components and validating their reliability through testing.
3.  **Low-Latency Data Links:** Achieving data latency < 3 seconds (threshold) and < 1 second (objective) for full-motion video requires high-bandwidth, low-latency data links. TMRR will focus on maturing the data link technology and optimizing data processing.
4.  **Shipboard Integration:** Integrating the system with multiple Navy ship classes (CVN 68, CG 47, DDG 51, LHD 1) is a significant technical challenge. TMRR will involve maturing the launch and recovery interfaces and validating compatibility with shipboard systems.

**Trade Space and Priorities:**
*   **Payload vs. Endurance:** There is a trade-off between payload capacity (150-350 lbs) and endurance (MTBCF). The strategy will prioritize meeting the threshold requirements for both, with the objective of maximizing payload capacity while maintaining the required endurance.
*   **Autonomy vs. Human-in-the-Loop:** The requirement for human-in-the-loop authorization for weapon release (CDD Section 5) may impact the speed of response. The strategy will prioritize safety and compliance with weapons safety assurance requirements while optimizing the human-in-the-loop process for efficiency.
*   **Cost vs. Performance:** The affordability constraints ($4.5M per system, $1,200 per flight hour) (CDD Section 6) will drive trade-offs in materials, components, and design complexity. The strategy will prioritize cost-effective solutions that meet the KPPs.

**Risks with Plans and Funding to Offset Them:**
*   **Risk:** Failure to achieve MTBCF >= 150 hours.
    *   **Mitigation:** Invest in high-reliability components and conduct extensive reliability testing during TMRR.
    *   **Funding:** Allocate TMRR funding for reliability testing and component upgrades.
*   **Risk:** Failure to achieve data latency < 3 seconds.
    *   **Mitigation:** Develop and test high-bandwidth data links and optimize data processing algorithms.
    *   **Funding:** Allocate TMRR funding for data link development and testing.
*   **Risk:** Incompatibility with Navy ship classes.
    *   **Mitigation:** Early engagement with Navy for shipboard integration requirements and validation on representative ship models.
    *   **Funding:** Allocate TMRR funding for shipboard integration testing and interface development.

## Risks, Mitigations and Funding

**Program Risks:**
1.  **Technical Risk:** High risk of failing to meet the KPPs for MTBCF, data latency, and payload capacity (CDD Section 4).
    *   **Mitigation:** Conduct rigorous technology maturation and risk reduction in TMRR. Use competitive prototyping to validate performance.
    *   **Funding:** TMRR funding will be allocated for technology development, testing, and prototyping.
2.  **Integration Risk:** Risk of integrating with Navy ship classes and Link 16 networks (CDD Section 2, Section 4).
    *   **Mitigation:** Early and continuous engagement with Navy and Joint Staff. Conduct joint interoperability testing.
    *   **Funding:** TMRR funding will be allocated for integration testing and interface development.
3.  **Sustainment Risk:** Risk of failing to meet the $1,200 per flight hour sustainment cost cap (CDD Section 6).
    *   **Mitigation:** Design for maintainability and reliability. Optimize logistics footprint. Conduct life-cycle cost analysis.
    *   **Funding:** TMRR funding will be allocated for sustainment analysis and design optimization.
4.  **Operational Risk:** Risk of operating in contested maritime environments with the required level of autonomy and human-in-the-loop control (CDD Section 1, Section 5).
    *   **Mitigation:** Conduct operational testing in simulated contested environments. Validate autonomous and human-in-the-loop procedures.
    *   **Funding:** TMRR and EMD funding will be allocated for operational testing and validation.

**Funding:**
*   **TMRR Funding:** The Milestone A decision will approve the funding for TMRR. The funding will be allocated for technology development, testing, prototyping, and integration.
*   **EMD Funding:** The Milestone B decision will approve the funding for EMD. The funding will be allocated for engineering development, manufacturing development, and testing.
*   **Production Funding:** The Milestone C decision will approve the funding for production and deployment of the 112 baseline systems (CDD Section 3).

## Should Cost Targets and Framing Assumptions

**Should Cost Targets:**
*   **Unit Procurement Cost:** The target unit procurement cost is $4.5M per system (1 GCS + 8 AVs) in FY2026 dollars (CDD Section 6). The program office will develop a Should Cost model to validate this target and identify cost drivers.
*   **Sustainment Cost:** The target sustainment cost is $1,200 per flight hour over the 10-year service life (CDD Section 6). The program office will develop a Should Cost model for sustainment to validate this target and identify cost drivers.

**Framing Assumptions:**
1.  **Technology Maturity:** The critical technologies (autonomous recovery, high-reliability avionics, low-latency data links) can be matured to the required level during TMRR.
2.  **Integration Compatibility:** The system can be successfully integrated with Navy ship classes and Link 16 networks.
3.  **Sustainment Feasibility:** The system can be designed and operated to meet the sustainment cost cap.
4.  **Regulatory Compliance:** The system can be designed to meet all applicable safety, security, and export control requirements.
5.  **Market Competition:** There is sufficient market competition to drive down costs and ensure quality.

## Initial Product Support Planning

**Initial Product Support Planning:**
*   **Logistics Footprint:** The system components must fit within standard ISU-90 shipping containers (CDD Section 5). The initial product support plan will define the logistics footprint, including packaging, storage, and transportation requirements.
*   **Sustainment Organization:** The plan will define the sustainment organization, including the roles and responsibilities of the Army, Navy, and contractor.
*   **Maintenance Strategy:** The plan will define the maintenance strategy, including preventive maintenance, corrective maintenance, and overhaul.
*   **Spare Parts:** The plan will define the spare parts strategy, including the types of spares, quantities, and storage locations.
*   **Training:** The plan will define the training strategy, including the types of training, duration, and locations.
*   **Sustainment Cost Analysis:** The plan will include a detailed sustainment cost analysis to validate the $1,200 per flight hour target (CDD Section 6).

**NOT PROVIDED IN SOURCE:**
*   Specific details of the initial product support plan, such as the maintenance strategy, spare parts strategy, and training strategy, are not provided in the source documents. Evidence needed: A draft Initial Product Support Plan (IPSP) from the program office.