# Package writers on the real model (FIREBIRD, 2026-10-09)

The six package-writer agents run through their squads (JointReview, MddPackage, MsaAnalysis,
SrrPackage) on the deployment model (qwen3.8:27b via Ollama), input = the FIREBIRD demo CDD, with
recorded approvals passed as decisions of record. Storage and HIL were not used.

Review of the first run found phase errors (Milestone A said to start EMD; technology maturation
placed in EMD; the Development RFP placed after Milestone B). Fixed by a shared block of process
facts from DoDI 5000.85 3.5-3.10 in every writer's prompt (agents/src/section_writer.py); these files
are the third run, after the fix. Grounding held throughout: figures trace to the CDD
(112 systems, $4.5M, $1,200/flight hour, KPPs), and absent data (AoA results, ACAT, lead FCB) is
marked NOT PROVIDED IN SOURCE.
