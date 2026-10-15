# Joint Staffing Designator Recommendation

## Recommended Joint Staffing Designator

**JSD undetermined: ACAT needed**

The submitted Capability Development Document (CDD) for Firebird Increment 1 does not state an Acquisition Category (ACAT) level. Per the policy mapping (CJCSM 5123.01A Encl. B 2.b), the Joint Staffing Designator (JSD) is determined by the ACAT level or the ACAT level of external programs with which the capability must interoperate.

*   **If the program is designated ACAT I:** The JSD would be **JROC Interest** (CJCSM 5123.01A Encl. B 2.b(3)).
*   **If the program is designated ACAT II:** The JSD would be **JCB Interest** (CJCSM 5123.01A Encl. B 2.b(4)).
*   **If the program is designated ACAT III:** The JSD would be **FCB Interest** (CJCSM 5123.01A Encl. B 2.b(5)).
*   **If the program is inherently Service-specific with minimal joint impact and meets none of the above tiers:** The JSD would be **Service Information** (CJCSM 5123.01A Encl. B 2.b(6)).

**Note on Interoperability:** The CDD specifies a requirement for "98% successful electronic data exchanges with DoD Command & Control networks via Link 16" (CDD Section 4, KPP 1). Link 16 is a joint standard. If the external programs utilizing Link 16 in this context are ACAT I or II, this interoperability requirement could elevate the JSD to JROC Interest or JCB Interest respectively, regardless of the Firebird program's own ACAT, provided the capability is necessary to fulfill a capability gap of more than one armed force or has joint dependencies (CJCSM 5123.01A Encl. B 2.b(3)-(4)). However, the ACAT of the external Link 16 programs is NOT PROVIDED IN SOURCE.

## Assessment Against the Assignment Criteria

The following assessment judges the requirement against the five assignment criteria defined in CJCSM 5123.01A Encl. B 2.b(2).

**(a) Significant impact on Joint Force Design.**
*   **Assessment:** The CDD identifies a capability gap for "Persistent Tactical Reconnaissance and Strike" in "contested maritime and littoral environments" (CDD Section 1). The concept of operations includes launch from U.S. Navy ship classes (CVN 68, CG 47, DDG 51, LHD 1) (CDD Section 2). This indicates a joint operational environment. However, the document does not explicitly state how this impacts the overall Joint Force Design structure or doctrine.
*   **Evidence:** CDD Sections 1 and 2.

**(b) Reliance on materiel or non-materiel solutions external to the validating organization.**
*   **Assessment:** The validating organization is the Army (implied by "Army Acquisition Executive" as MDA and "Force Application Functional Capabilities Board" as validation authority, typically Army FABC). The system relies on external materiel solutions:
    1.  **U.S. Navy Ship Classes:** Launch from CVN 68, CG 47, DDG 51, and LHD 1 (CDD Section 2).
    2.  **DoD Command & Control Networks:** Interoperability via Link 16 (CDD Section 4, KPP 1).
    3.  **Spectrum Certification:** Compliance with joint frequency management policies (CDD Section 5).
*   **Conclusion:** This criterion is **met**. The system relies on Navy platforms and joint C2 networks external to the Army.

**(c) A unique DoW capability, one Service providing a capability others depend on, or insufficient resiliency or redundancy.**
*   **Assessment:** The CDD describes a capability for "immediate kinetic response" and "persistent tactical reconnaissance" (CDD Section 1). It does not explicitly state that this is a unique Department of War (DoW) capability or that other Services depend on it exclusively. It does not explicitly address resiliency or redundancy gaps beyond the general availability requirements.
*   **Conclusion:** **NOT PROVIDED IN SOURCE** as to whether it is a unique DoW capability or if other Services depend on it.

**(d) Significant resource impact on the DoW, including the proposed Acquisition Category (ACAT) level.**
*   **Assessment:** The CDD provides cost data:
    *   Target Unit Procurement Cost: $4.5M per system (CDD Section 6).
    *   Total Quantity: 112 systems (CDD Section 3).
    *   Sustainment Cost Cap: $1,200 per flight hour (CDD Section 6).
*   **ACAT Level:** The ACAT level is **NOT PROVIDED IN SOURCE**. Per policy, ACAT is set by statutory dollar thresholds and designation, which the source must state. It cannot be inferred from unit cost times quantity.
*   **Conclusion:** The resource impact is quantified, but the ACAT level is missing, preventing a definitive JSD assignment based on this criterion alone.

**(e) A previous JSD designation.**
*   **Assessment:** The CDD does not mention any previous Joint Staffing Designator designation for this capability or its predecessors.
*   **Conclusion:** **NOT PROVIDED IN SOURCE**.

## Recommended Lead FCB

**NOT PROVIDED IN SOURCE**

The CDD identifies the "Force Application Functional Capabilities Board" as the Validation Authority (CDD Header). It does not specify which Functional Capabilities Board (FCB) is the lead for this requirement. If the JSD is determined to be FCB Interest (ACAT III), the lead FCB would be the final review authority (CJCSM 5123.01A Encl. B 2.b(5)). If the JSD is JCB Interest or JROC Interest, the lead FCB is not the primary review authority, though the FCB may still be involved in the validation process. The specific FCB (e.g., Army FABC, Joint FABC, etc.) is not named.

## Joint Dependencies and Interoperability

The following joint dependencies and interoperability requirements are identified in the CDD:

1.  **Naval Platform Integration:**
    *   The system must be deployable from U.S. Navy ship classes: CVN 68, CG 47, DDG 51, and LHD 1 (CDD Section 2).
    *   System components must satisfy shipboard spatial constraints for CG 47 and DDG 51 hangar bays (CDD Section 5).
    *   *Implication:* This creates a direct dependency on Navy platforms and potentially Navy maintenance/support infrastructure.

2.  **Command and Control (C2) Interoperability:**
    *   The system must achieve 98% successful electronic data exchanges with DoD Command & Control networks via Link 16 (CDD Section 4, KPP 1).
    *   *Implication:* This requires compatibility with joint C2 architectures and potentially other Services' C2 systems that use Link 16.

3.  **Spectrum Management:**
    *   Transmitters must obtain spectrum certification in compliance with joint frequency management policies to operate within standard military S-band and Ku-band ranges (CDD Section 5).
    *   *Implication:* This requires coordination with the Joint Spectrum Center (JSC) or equivalent joint spectrum management authority.

4.  **Reserve and War Reserve Integration:**
    *   The acquisition objective includes 10 Reserve Force Units and 10 War Reserve stock systems (CDD Section 3).
    *   *Implication:* This requires integration with joint reserve and war reserve logistics and sustainment structures.

## Open Questions for the Joint Requirements Coordinator

1.  **ACAT Level:** What is the designated Acquisition Category (ACAT) for the Firebird Increment 1 program? (Required to determine JSD per CJCSM 5123.01A Encl. B 2.b).
2.  **External Program ACATs:** What are the ACAT levels of the external DoD Command & Control networks and Navy ship classes (CVN 68, CG 47, DDG 51, LHD 1) with which Firebird must interoperate? (Required to determine if interoperability elevates the JSD per CJCSM 5123.01A Encl. B 2.b(3)-(4)).
3.  **Lead FCB:** Which Functional Capabilities Board is designated as the lead FCB for this requirement? (Required if JSD is FCB Interest).
4.  **Joint Dependency Justification:** Is this capability necessary to fulfill a capability gap of more than one armed force, or does it have capabilities with joint dependencies? (Required for any tier with an ACAT level per CJCSM 5123.01A Encl. B 2.b).
5.  **Previous JSD:** Has this capability or a predecessor capability received a previous Joint Staffing Designator designation? (CJCSM 5123.01A Encl. B 2.b(2)(e)).