# Sample sponsor documents

The documents the DAS demo offers in its document list. All are fictional. They live in
`src/k9_dow/api/static/demos/`, the folder the application reads, and are linked here rather than copied.

| Document | Kind | Good for |
|---|---|---|
| [FIREBIRD](../../../src/k9_dow/api/static/demos/FIREBIRD_UAV_Capability_Development_Document.md) | Capability Development Document, unmanned aircraft, Increment 1 | The main walkthrough; saved run in [`docs/process-model-2026/evidence/`](../../process-model-2026/evidence/) |
| [IRONCLAD](../../../src/k9_dow/api/static/demos/IRONCLAD_Ground_Vehicle_Capability_Development_Document.md) | Capability Development Document, ground vehicle, Increment 1 | A second Service requirement (Army) |
| [SENTINEL](../../../src/k9_dow/api/static/demos/SENTINEL_Cyber_Defense_Capability_Development_Document.md) | Capability Development Document, cyber defense, Increment 2 | A joint, cyber requirement |
| [F-22 maintenance](../../../src/k9_dow/api/static/demos/F22_Maintenance_Readiness_Assessment_Request.md) | Short, informal support request | Testing a weak input: what DAS marks as not provided |

**Red-team documents:** [`demos/attacks/`](../../../src/k9_dow/api/static/demos/attacks/), with
[`manifest.json`](../../../src/k9_dow/api/static/demos/attacks/manifest.json) stating each attack and the
expected result (including one known limit: a paraphrased injection the pattern checks are not expected to
catch).
