# How the DAS knowledge corpus was built

DAS uses two kinds of knowledge, and keeps them apart on purpose:

| Layer | What | How DAS uses it | Where |
|---|---|---|---|
| **1. Policy (authoritative)** | Seven public DoD and Joint Staff documents | Read and turned into versioned, cited configuration. Gates, entry criteria and decision rules come only from here | `src/k9_dow/config/process_model.yaml`, `src/k9_dow/config/mappings/` |
| **2. Reference corpus (supplementary)** | Six synthetic reference documents | Embedded in a vector store and retrieved as background for drafting. Never treated as part of the submitted document | `data/synthetic_corpus/` → pgvector table `dow_knowledge_corpus` |

The policy documents are **not** put in the vector store. A rule that decides something (who validates,
which criteria a gate checks, which designator tier applies) must come from a cited paragraph, not from
whichever chunk a similarity search returns.

## Layer 1: policy, turned into configuration

**Sources.** S1 to S6 and S8 are listed with release statements and download links in
[`sources/README.md`](sources/README.md).

**Currency check first.** DAS was originally built on JCIDS, which the 20 Aug 2025 SecDef memo ended.
Before the current process model was written, each source was checked for date and status in the
primary document, not in secondary reporting. The findings, with page and paragraph references, are in
[`docs/process-model-2026/01_sources_and_findings.md`](../../process-model-2026/01_sources_and_findings.md).

**Process model.** The verified findings became
[`src/k9_dow/config/process_model.yaml`](../../../src/k9_dow/config/process_model.yaml) (id `mca-2026-10`, as
of 2026-10-09):

- **12 stages and gates,** from NORMALIZE through SE-REVIEW-SRR.
- **For each gate:** its entry criteria, the decision authority, whether it blocks, and the run its approval starts.
- **A source reference on every stage and gate** (for example `S3 Encl. A 6.b`, `S5 3.6`).

The application reads this file to build its gate registry, orchestrator runs, K9X HIL queues and UI.
`tests/test_process_model.py` checks that every stage and gate cites a source and that the JCI review
never blocks. A future reform becomes a new version of the file; past jobs keep the version they ran
under.

**Policy as data.** Rules that an agent applies live in mapping files, not in prompts. For example,
[`mappings/jsd.yaml`](../../../src/k9_dow/config/mappings/jsd.yaml) holds the Joint Staffing Designator
tiers from CJCSM 5123.01A Encl. B 2.b, with a paragraph citation per entry. An agent names the mapping it
needs and the text is rendered into its prompt. `tests/test_policy_mappings.py` checks the structure,
the citations and the tier-to-ACAT table against the source. Each mapping is copied from the primary
paragraph, not from a summary. An earlier summary merged three paragraphs into one sentence and lost
the ACAT-per-tier rule, which is why this rule exists.

**Design and review.** [`02_process_design.md`](../../process-model-2026/02_process_design.md) records the
design, and [`03_independent_review.md`](../../process-model-2026/03_independent_review.md) records a
review of it against the sources.

## Layer 2: the synthetic reference corpus

**Why it exists.** DAS's drafting agents can draw on retrieved reference material through the K9-AIF
`K9Retriever`. Real program documents are not available for a public demonstration, and an empty index
means retrieval returns nothing. So the index is seeded with hand-authored synthetic documents that show
real retrieval behaviour without real data.

**Contents** ([`data/synthetic_corpus/`](../../../data/synthetic_corpus/), added 2026-09-03 in commit
`58abf2e`):

| File | What | Sections (chunks) |
|---|---|---:|
| `cdd_talon_ground_sensor.md` | Prior CDD, fictional ground-sensor program | 6 |
| `cdd_meridian_comms_relay.md` | Prior CDD, fictional communications-relay program | 6 |
| `cdd_griffon_counter_uas.md` | Prior CDD, fictional counter-UAS program | 6 |
| `dodaf_reference_operational_views.md` | DoDAF 2.0 operational-view authoring reference | 3 |
| `dodaf_reference_systems_capability_views.md` | DoDAF 2.0 systems and capability-view authoring reference | 5 |
| `acquisition_review_package_reference.md` | Review-package content reference | 3 |

Every document is marked synthetic in its header. The program names (TALON, MERIDIAN, GRIFFON) are
fictional and chosen to be clearly distinct from real programs of record.

**How it is indexed.**
[`experiments/seed_synthetic_corpus.py`](../../../experiments/seed_synthetic_corpus.py):

1. Splits each document on its `## ` section headings rather than at a fixed character count, because
   the sections are meaningful units. Each chunk is prefixed with its document title.
2. Embeds each chunk with `nomic-embed-text` (768 dimensions) through Ollama.
3. Stores it in PostgreSQL with pgvector (table `dow_knowledge_corpus`), with metadata: source file,
   heading, chunk index and `synthetic: true`.
4. Runs a test retrieval to confirm the index answers.

Run: `PYTHONPATH=src python3 experiments/seed_synthetic_corpus.py` (needs the Postgres and Ollama
settings in `.env`).

**How agents use it.**

- `ViewGeneratorAgent` retrieves the top 5 chunks for DoDAF view drafting.
- `LinkProposerAgent` retrieves the top 10 for traceability links.

Retrieved text is appended after the submitted document under the label *"Supplementary reference
material… NOT part of the submitted document"*. Agents must draw program facts only from the submission
(missing facts are marked `NOT PROVIDED IN SOURCE`). If retrieval returns nothing, the agent works from
the submitted document alone. An empty retrieval is not an error.

## Loading this into Context Studio

- **Policy:** the seven documents in [`sources/README.md`](sources/README.md). If only a few documents
  can be loaded, use S1 (the reform memo) and S3 (CJCSM 5123.01A, the requirements process detail).
- **Domain model:** [`schema.jsonld`](schema.jsonld). It holds the six DAS entities (CapabilityRequirement,
  JCIReview, AcquisitionProgram, GateReview, SERequirement, DASJob) with their attributes, states,
  transitions and invariants, prepared for Context Studio from the DAS process model.
- **Reference corpus:** the six files in [`data/synthetic_corpus/`](../../../data/synthetic_corpus/).
- **Process model** (optional, for comparison):
  [`process_model.yaml`](../../../src/k9_dow/config/process_model.yaml).

DAS keeps policy and reference material separate. If Context Studio pools them, keep in mind that
gates and criteria should be grounded in the policy sources only.
