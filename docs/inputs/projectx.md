
In the United States Department of Defense (DoD) [Defense Acquisition System (DAS)](https://www.sbir.gov/tutorials/acquisition-basics/tutorial-1), the primary requirements documents are developed under the Joint Capabilities Integration and Development System (JCIDS). The foundational document used to transition a raw military gap into a formal engineering program is the  **Capability Development Document (CDD)** . [[1](https://acqnotes.com/acqnote/tasks/capability-development-documentrequirements), [2](https://www.sbir.gov/tutorials/acquisition-basics/tutorial-1), [3](https://acqnotes.com/acqnote/tasks/step-2-write-document-requirements)]

A real-world, unclassified, structured sample based on historical JCIDS inputs for an **Unmanned Aerial Vehicle (UAV) program** outlines how operational constraints map directly to technical parameters. [[1](https://www.coursehero.com/file/101032584/Capabilities-Development-Document-CDD-Increment/)]

---

CAPABILITY DEVELOPMENT DOCUMENT (CDD) FOR FIREBIRD INCREMENT 1

**Document Status:** Final / Unclassified
**Validation Authority:** Force Application Functional Capabilities Board
**Milestone Decision Authority:** Army Acquisition Executive [[1](https://www.acqnotes.com/Attachments/System%20Requirements%20Document%20(SRD)%20Template.doc), [2](https://www.coursehero.com/file/101032584/Capabilities-Development-Document-CDD-Increment/)]

1. Capability Discussion

This program addresses the capability gaps identified in the [Initial Capabilities Document (ICD)](https://acqnotes.com/acqnote/acquisitions/initial-capabilities-document-icd) for Persistent Tactical Reconnaissance and Strike. Current theater assets lack the necessary blend of prolonged endurance, zero-infrastructure deployment, and immediate kinetic response required to counter highly mobile, light-armored forces in contested maritime and littoral environments. [[1](https://acqnotes.com/acqnote/acquisitions/initial-capabilities-document-icd), [2](https://www.acqnotes.com/Attachments/Capability%20Development%20Document%20Template%2030%20Oct%2012.doc), [3](https://www.coursehero.com/file/101032584/Capabilities-Development-Document-CDD-Increment/)]

2. Concept of Operations (CONOPS) Summary

* **Primary Mission:** Locate, track, and destroy light-armored mobile forces.
* **Recovery:** Unexpended platforms must execute a safe autonomous return and be eligible for unlimited reuse.
* **Launch Environments:** Ground-launched via expeditionary pneumatic catapult, or deployed from the flight/hangar decks of U.S. Navy ship classes including CVN 68, CG 47, DDG 51, and LHD 1. [[1](https://www.coursehero.com/file/101032584/Capabilities-Development-Document-CDD-Increment/)]

3. Program Summary

* **Acquisition Objective:** Total of 112 baseline systems.

  * *Active Force:* 92 systems
  * *Reserve Force Units:* 10 systems
  * *War Reserve stock:* 10 systems [[1](https://www.coursehero.com/file/101032584/Capabilities-Development-Document-CDD-Increment/)]
* **System Composition:** One (1) Mobile Ground Control Station (GCS) and eight (8) Air Vehicles (AV), crewed by 4 enlisted personnel per shift. [[1](https://www.coursehero.com/file/101032584/Capabilities-Development-Document-CDD-Increment/)]
* **Planned Service Life:** 10 Years. [[1](https://www.coursehero.com/file/101032584/Capabilities-Development-Document-CDD-Increment/)]

---

4. System Capabilities & Performance Parameters

Requirements are structured using  **Thresholds (T)** —the minimum acceptable operational value—and  **Objectives (O)** —the desired optimal capability. [[1](https://acqnotes.com/acqnote/tasks/step-2-write-document-requirements), [2](https://acqnotes.com/acqnote/tasks/capability-development-documentrequirements)]


| Key Performance Parameter (KPP) / Attribute | Performance Threshold (T)                                                                        | Performance Objective (O)                                                                                          |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **KPP 1: Interoperability**                 | 98% successful electronic data exchanges with DoD Command & Control networks via Link 16.        | 100% seamless integration across joint Service architectures and allied networks.                                  |
| **KPP 2: System Availability**              | Maintain access/connectivity at a 95% operational availability rate over a 72-hour surge period. | Achieve ≥ 98% mission-ready operational availability under sustained field conditions.                            |
| **KPP 3: System Reliability**               | Mean Time Between Critical Failure (MTBCF) of ≥ 150 hours of continuous operations.             | Mean Time Between Critical Failure (MTBCF) of ≥ 300 hours with automated failover systems.                        |
| **KPP 4: Timeliness (Data Latency)**        | Sensor telemetry and target tracking data latency < 3 seconds to the tactical web query gateway. | Full-motion video and payload target coordinates delivered to application programs in near real-time (< 1 second). |
| **Attribute 5: Payload Capacity**           | Must lift a minimum of 150 lbs consisting of optical sensors and laser designators.              | Must lift up to 350 lbs to include dual-band synthetic aperture radar and micro-munitions.                         |

---

5. Other DOTMLPF-P & Supportability Considerations

* **Facilities:** System components must fit within standard standard ISU-90 shipping containers and satisfy shipboard spatial constraints for CG 47 and DDG 51 hangar bays. [[1](https://www.waru.edu/acquipedia-article/jcids-documentation-dcr-icd-cdd-jeon-juon-and-their-variants), [2](https://www.coursehero.com/file/101032584/Capabilities-Development-Document-CDD-Increment/)]
* **Spectrum Supportability:** Transmitters must obtain spectrum certification in compliance with joint frequency management policies to operate within standard military S-band and Ku-band ranges.
* **Weapons Safety Assurance:** The platform's remote weapon release mechanism must incorporate three distinct physical/logical inhibits, requiring explicit human-in-the-loop authorization. [[1](https://acqnotes.com/acqnote/acquisitions/capability-development-document-cdd)]

---

6. Program Affordability & Life-Cycle Cost

* **Target Unit Procurement Cost:** Shall not exceed $4.5M per system (1 GCS + 8 AVs) in FY2026 dollars.
* **Sustainment Cost Cap:** Operating and support costs must remain under $1,200 per flight hour over the 10-year service life. [[1](https://acqnotes.com/acqnote/acquisitions/capability-development-document-cdd), [2](https://www.coursehero.com/file/101032584/Capabilities-Development-Document-CDD-Increment/)]

---

Next Steps & Actionable Guidance

To translate this capability documentation into a developer-facing contract package, the program office typically converts these operational needs into a **System Requirements Document (SRD)** or a formal Statement of Work (SOW). [[1](https://acqnotes.com/acqnote/tasks/system-requirements-documentrequirements), [2](https://www.acqnotes.com/Attachments/System%20Requirements%20Document%20(SRD)%20Template.doc)]

If you are drafting an acquisition package, tell me:

* **What ****specific mission or equipment domain** (e.g., software, cyber, armored vehicles, sensors) your document targets?
* **Which ****milestone phase** you are preparing for (e.g., initial prototyping vs. full-rate production)? [[1](https://www.youtube.com/watch?v=EgkEGsIrcKQ&t=165), [2](https://www.sbir.gov/tutorials/acquisition-basics/tutorial-1)]

I can generate a precise, tailored clause-by-clause template for your specific defense program.

* [](https://acqnotes.com/acqnote/tasks/step-2-write-document-requirements)![]()

  AcqNotes

  Step 2: Write & Document Requirements - AcqNotes

  **Jun 11, 2021 — **The CPD identifies, in threshold/objective format, the specific attributes that contribute most significantly to the desired opera...

  ![]()
* [](https://static.e-publishing.af.mil/production/1/af_a3_5/publication/afi10-601/afi10-601.pdf)![]()

  AF.mil

  afi10-601.pdf - Air Force

  **Nov 6, 2013 — **This chapter provides an overview of the Joint Capabilities Integration and. Development System (JCIDS) requirements process and h...

  ![]()
* [](https://www.dla.mil/portals/104/documents/dlms/committees/dodaad/meetings/92606/func_requirts_doc_sept06.doc)![]()

  Defense Logistics Agency (DLA) (.mil)

  FUNCTIONAL REQUIREMENTS DOCUMENT (FRD) - DLA

  Table_content: | Key Performance Parameters | Top-Level Metrics | Threshold | | --- | --- | --- | | Interoperability | Facilitate ...

get more from:



🛠️ Systems Engineering & Functional Specs

* **Range Commanders Council (RCC) FRD:** The [RCC Signature Data Base Functional Requirements Document](https://apps.dtic.mil/sti/tr/pdf/ADA346528.pdf) acts as an excellent technical template for establishing data systems, standard data definitions, and test/evaluation requirements. [[1](https://apps.dtic.mil/sti/tr/pdf/ADA346528.pdf)]
* **System Security Engineering Requirements:** Review the [System Security Engineering Case Study Template](https://ndia.dtic.mil/wp-content/uploads/2012/systemtutorial/14762.pdf) to see how concepts of operations (CONOPS) translate into System Requirements Documents (SRD) and Statements of Work (SOW). [[1](https://ndia.dtic.mil/wp-content/uploads/2012/systemtutorial/14762.pdf)]
* **Surface Navy Systems Engineering Plan:** The [Theater Air Defense Systems Engineering Plan](https://apps.dtic.mil/sti/tr/pdf/ADA376506.pdf) outlines an exact template for a Systems Engineering Memorandum (SEM) to communicate technical baseline allocations. [[1](https://apps.dtic.mil/sti/tr/pdf/ADA376506.pdf)]
