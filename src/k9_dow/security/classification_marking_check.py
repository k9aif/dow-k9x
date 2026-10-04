# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""ClassificationMarkingCheck -- DAS SBB on the framework's check contract
(BaseVulnerabilityCheck), run at JCIDS stage entry before any model call.

DAS is an UNCLASSIFIED proof of concept: a document that carries a US
classification marking above UNCLASSIFIED must not enter the pipeline.
Blocks on
  * banner lines:   TOP SECRET / SECRET / CONFIDENTIAL, alone on a line or
                    followed by //controls (e.g. "SECRET//NOFORN");
  * portion marks:  (TS) (S) (C), with or without //controls, at the start
                    of a line or paragraph, e.g. "(S//NF) The vehicle ...";
  * dissemination controls that only appear on classified material:
                    NOFORN, ORCON, //SI, //TK, //HCS, "REL TO".
Controlled Unclassified Information (CUI banner or (CUI) portion) is flagged;
config ``block_cui: true`` blocks it too. Ordinary words ("trade secret",
"confidential settlement", "(c) 2026") are not markings and pass.
"""

from __future__ import annotations

import re
from typing import Any, Dict

from k9_aif_abb.k9_security.vulnerability.base_vulnerability_check import BaseVulnerabilityCheck
from k9_aif_abb.k9_security.vulnerability.models.check_result import CheckResult

_BANNER = re.compile(r"^[ \t*#>_-]*(TOP SECRET|SECRET|CONFIDENTIAL)(//[A-Z0-9 ,/-]+)?[ \t*_-]*$", re.M)
_PORTION = re.compile(r"^[ \t*#>-]*\((TS|S|C)(//[A-Z0-9 ,/-]+)?\)\s+[A-Z]", re.M)
_CONTROLS = re.compile(r"\bNOFORN\b|\bORCON\b|//(SI|TK|HCS)\b|\bREL TO (USA|FVEY)\b")
_CUI = re.compile(r"^[ \t*#>-]*CUI(//[A-Z0-9 ,/-]+)?[ \t*]*$|^[ \t*#>-]*\(CUI\)\s", re.M)
_TEXT_KEYS = ("source_markdown", "document_text", "text", "content")


class ClassificationMarkingCheck(BaseVulnerabilityCheck):

    def check(self, payload: Dict[str, Any]) -> CheckResult:
        text = "\n".join(str(payload.get(k) or "") for k in _TEXT_KEYS)
        for pattern, label in ((_BANNER, "classification banner"), (_PORTION, "portion marking"),
                               (_CONTROLS, "dissemination control")):
            m = pattern.search(text)
            if m:
                return CheckResult.block(
                    check_name=self.check_name,
                    message=f"Classified marking ({label}: '{m.group(0).strip()[:40]}'); "
                            "DAS accepts UNCLASSIFIED documents only",
                    severity="critical",
                    metadata={"marking": m.group(0).strip()[:60], "kind": label})
        m = _CUI.search(text)
        if m:
            msg = "Controlled Unclassified Information marking (CUI)"
            if self.config.get("block_cui"):
                return CheckResult.block(check_name=self.check_name, message=msg, severity="high",
                                         metadata={"marking": m.group(0).strip()[:60], "kind": "CUI"})
            return CheckResult.flag(check_name=self.check_name, message=msg, severity="medium",
                                    metadata={"marking": m.group(0).strip()[:60], "kind": "CUI"})
        return CheckResult.pass_check(self.check_name)
