# DAS architecture diagrams

Drawn from the code as of 2026-10-29 (process model `mca-2026-10`, k9-aif squad layer). PlantUML
sources with rendered PNGs; to redraw: `plantuml -tpng *.puml`.

| Diagram | Shows |
|---|---|
| [01 Routing](01-routing-class-diagram.png) | `DasRouter` on the K9-AIF `BaseRouter`: event type or gate decision to run topic |
| [02 Orchestration](02-orchestration-class-diagram.png) | `ProcessStageOrchestrator` and the requirement, MSA, TMRR and traceability orchestrators; orchestrators know only squads |
| [03 Squads](03-squad-class-diagram.png) | One `DasSquad` class, nine squad YAML files and their agents |
| [04 Agents](04-agents-class-diagram.png) | The agents and their K9-AIF bases (`BaseAgent`, `K9ValidationLoopAgent`, `SectionWriterAgent`) |
| [05 Sequence](05-sequence-diagram.png) | End to end: upload, requirement run, Service validation, MDD, MSA, Milestone A, TMRR, SRR, through K9X HIL |

The process flow diagram (stages and gates) is generated from the process model:
`PYTHONPATH=src python tools/flow_diagram.py`. The deployment diagram for AWS GovCloud is in
[`deployment_guidelines/aws-govcloud/`](../../deployment_guidelines/aws-govcloud/).

The JCIDS-era diagrams (June 2026) are in the Git history before this change.
