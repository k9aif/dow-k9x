# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""Classification screen: marked documents are refused; ordinary words are not markings."""

from pathlib import Path

import pytest

from k9_dow.security.classification_marking_check import ClassificationMarkingCheck

DEMOS = Path(__file__).resolve().parents[1] / "src" / "k9_dow" / "api" / "static" / "demos"


def outcome(text, **cfg):
    r = ClassificationMarkingCheck(cfg).check({"source_markdown": text})
    return "block" if r.blocked else "flag" if r.flagged else "pass"


@pytest.mark.parametrize("text", [
    "SECRET//NOFORN\nThe system shall ...",
    "TOP SECRET\n\nBody",
    "**CONFIDENTIAL**",
    "(S//NF) The vehicle shall operate at night.",
    "(TS) Program details follow.",
    "Distribution: REL TO USA, FVEY",
    "Handling: ORCON",
])
def test_markings_are_blocked(text):
    assert outcome(text) == "block"


@pytest.mark.parametrize("text", [
    "Protect trade secret data and confidential settlement terms.",
    "(c) 2026 Acme Corp. All rights reserved.",
    "**Document Status:** Final / Unclassified",
    "Detect, classify, and contain intrusions.",
    "The secret to success is testing.",
])
def test_ordinary_words_pass(text):
    assert outcome(text) == "pass"


def test_cui_flagged_by_default_blocked_when_configured():
    assert outcome("CUI\nProgram data") == "flag"
    assert outcome("CUI\nProgram data", block_cui=True) == "block"


def test_demo_and_other_red_team_documents_unaffected():
    docs = sorted(DEMOS.glob("*.md")) + [p for p in sorted((DEMOS / "attacks").glob("*.md"))
                                         if not p.name.startswith("08_")]
    assert docs and all(outcome(p.read_text()) == "pass" for p in docs)
