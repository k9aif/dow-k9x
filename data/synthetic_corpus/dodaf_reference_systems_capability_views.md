# DoDAF 2.0 Systems and Capability View Families — Authoring Reference

**SYNTHETIC/ORIGINAL REFERENCE MATERIAL — an original explanatory synthesis
for retrieval-corpus demonstration, not a reproduction of any official
DoDAF publication text.**

## SV-1: Systems Interface Description

The SV-1 enumerates the physical and logical systems that realize the
capability described in the operational views, and the interfaces between
them. Every system named in an OV-1's capability-to-system mapping must
have a corresponding node in the SV-1 — this is the specific pairing a
cross-view consistency check tests first, because it is the most common
place a review package breaks down: capability language and systems
language are often authored by different teams at different times, and
drift apart.

## CV-1 / CV-2: Capability Taxonomy and Capability-to-Activity Mapping

The capability view family exists to keep a program honest about the
difference between a capability (an operational outcome) and a system (a
materiel solution). A CV-1 capability taxonomy should be stable even if
the systems that satisfy it change — a program that revises its CV-1 every
time it changes a technical baseline item is a sign the capability
statement was actually written as a system description in disguise.

## SvcV-1: Services Interface Description

Where a program's architecture is service-oriented rather than
platform-oriented, the SvcV-1 plays the same structural role the SV-1
plays for systems: naming the services and the interfaces between them.
Programs with both a services layer and a platform layer should expect a
consistency check between SvcV-1 and SV-1 as well as between SV-1 and
OV-1.

## TV-1: Technical Standards Profile

The TV-1 lists the technical standards (communications waveforms, data
formats, spectrum allocations, safety standards) a program's systems must
conform to. A TV-1 entry is only useful if it is traceable to the specific
system or interface it constrains — an unattributed standards list is a
common defect that produces a technically complete-looking view with no
actual enforceability, since a reviewer cannot tell which system a given
standard applies to.

## Reading Requirements Into Views

A well-extracted requirements baseline (capability needs, system
requirements with threshold/objective values, technical baseline items,
test cases, and the relationships between them) contains everything needed
to populate every DoDAF view family described above. The most frequent
process failure observed across programs is not a shortage of requirements
data — it is a hand-off gap between the team or tool that extracts the
requirements baseline and the team or tool that authors the views, where
the extracted data exists but is never actually passed into the
view-authoring step. When that hand-off breaks, every view field reads as
unavailable even though the underlying program data is complete and
well-formed — the defect is procedural, not a lack of program content.
