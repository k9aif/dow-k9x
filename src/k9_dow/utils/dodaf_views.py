# SPDX-License-Identifier: Apache-2.0
"""DoDAF 2.02 view names, and titling a generated view with its proper name."""

from __future__ import annotations

import re

# DoDAF 2.02 model names. The view's title is set from here: the model once titled OV-1
# "Capability View" (JOB-20261008-DFA941); capability content belongs in CV-1 / CV-2.
DODAF_VIEW_NAMES = {
    "AV-1": "Overview and Summary Information", "AV-2": "Integrated Dictionary",
    "CV-1": "Vision", "CV-2": "Capability Taxonomy", "CV-3": "Capability Phasing",
    "CV-4": "Capability Dependencies", "CV-5": "Capability to Organizational Development Mapping",
    "CV-6": "Capability to Operational Activities Mapping", "CV-7": "Capability to Services Mapping",
    "OV-1": "High-Level Operational Concept Graphic", "OV-2": "Operational Resource Flow Description",
    "OV-3": "Operational Resource Flow Matrix", "OV-4": "Organizational Relationships Chart",
    "OV-5a": "Operational Activity Decomposition Tree", "OV-5b": "Operational Activity Model",
    "SV-1": "Systems Interface Description", "SV-2": "Systems Resource Flow Description",
    "SvcV-1": "Services Context Description", "TV-1": "Standards Profile",
}


def label_view(output: str, view_type: str, single_view: bool = True) -> str:
    """Title the view with its DoDAF name, whatever the model called it. ``single_view``: the text
    is that one view, so its 'View Name:' line is set too."""
    name = DODAF_VIEW_NAMES.get(view_type)
    if not name:
        return output
    vt = re.escape(view_type)
    output = re.sub(rf"(?im)^(#+\s*(?:DoDAF[^:\n]*:[ \t]*){'?' if single_view else ''}{vt})[ \t]*(?:\([^)\n]*\)|[-—:][^\n]*)?[ \t]*$",
                    rf"\1 ({name})", output, count=1)
    if single_view:
        output = re.sub(r"(?im)^(\**View Name:?\**:?[ \t]*).*$", rf"\g<1>{name}", output, count=1)
    output = re.sub(rf"\b({vt}`?)\s*\((?!{re.escape(name)})[^)\n]*View\)", rf"\1 ({name})", output)
    return re.sub(rf"\b({vt}`?)\s+(?:[A-Z][a-z]+\s+)?View\b", rf"\1 ({name})", output)


def relabel_views(text: str) -> str:
    """Every 'XV-n (… View)' reference that misnames a known view gets its DoDAF name (documents
    generated before views were titled from DODAF_VIEW_NAMES)."""
    for view_type, name in DODAF_VIEW_NAMES.items():
        if view_type in text:
            text = label_view(text, view_type, single_view=False)
    return text
