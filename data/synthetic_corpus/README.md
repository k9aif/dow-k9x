# Synthetic DoW Knowledge Corpus

**All content in this directory is synthetic.** No real program names, real
requirements, real capability gaps, or real DoD data of any kind appear
here. Program names (TALON, MERIDIAN, GRIFFON) are fictional and chosen to
be obviously distinct from any real DoD program of record. This corpus
exists solely to demonstrate the `K9Retriever` context-enrichment pattern
described in the IEEE Access manuscript (Section VI, "Context Enrichment
and Retrieval") with real retrieval behavior instead of an empty index —
real DoW corpus data is not available for a proof-of-concept of this kind.

## Contents

- `cdd_talon_ground_sensor.md` — synthetic prior CDD (ground sensor program)
- `cdd_meridian_comms_relay.md` — synthetic prior CDD (comms relay program)
- `cdd_griffon_counter_uas.md` — synthetic prior CDD (counter-UAS program)
- `dodaf_reference_operational_views.md` — DoDAF 2.0 operational-view-family authoring reference
- `dodaf_reference_systems_capability_views.md` — DoDAF 2.0 systems/capability-view-family authoring reference
- `acquisition_review_package_reference.md` — JROC/Milestone Decision review-package content reference

Seeded into pgvector via `scripts/seed_synthetic_corpus.py`.
