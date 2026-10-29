# Sample sponsor documents

The documents the DAS demo offers in its document list. All are fictional. The application reads them
from `src/k9_dow/api/static/demos/`; identical copies are in [`docs/inputs/`](../../inputs/), linked below.
`tests/test_demo_inputs_in_sync.py` fails if a copy is missing or differs.

| Document | Kind | Good for |
|---|---|---|
| [FIREBIRD](../../inputs/FIREBIRD_UAV_Capability_Development_Document.md) | Capability Development Document, unmanned aircraft, Increment 1 | The main walkthrough; saved run in [`docs/process-model-2026/evidence/`](../../process-model-2026/evidence/) |
| [IRONCLAD](../../inputs/IRONCLAD_Ground_Vehicle_Capability_Development_Document.md) | Capability Development Document, ground vehicle, Increment 1 | A second Service requirement (Army) |
| [SENTINEL](../../inputs/SENTINEL_Cyber_Defense_Capability_Development_Document.md) | Capability Development Document, cyber defense, Increment 2 | A joint, cyber requirement |
| [F-22 maintenance](../../inputs/F22_Maintenance_Readiness_Assessment_Request.md) | Short, informal support request | Testing a weak input: what DAS marks as not provided |

**Red-team documents:** [`demos/attacks/`](../../../src/k9_dow/api/static/demos/attacks/), with
[`manifest.json`](../../../src/k9_dow/api/static/demos/attacks/manifest.json) stating each attack and the
expected result (including one known limit: a paraphrased injection the pattern checks are not expected to
catch).
