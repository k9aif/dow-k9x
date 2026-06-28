from __future__ import annotations


def build_traceability_puml(graph_data: dict) -> str:
    """Build a PlantUML object diagram from traceability graph data."""
    lines = [
        "@startuml",
        "!theme plain",
        'title "Requirements Traceability View"',
        "",
    ]

    capabilities = graph_data.get("capabilities", [])
    for cap in capabilities:
        lines.append(f'object "{cap.get("id", "CAP")}" as {_safe_id(cap.get("id", ""))} #LightBlue {{')
        lines.append(f'  title = "{cap.get("title", "")}"')
        lines.append("}")

    requirements = graph_data.get("requirements", [])
    for req in requirements:
        lines.append(f'object "{req.get("id", "REQ")}" as {_safe_id(req.get("id", ""))} #LightGreen {{')
        lines.append(f'  shall = "{_truncate(req.get("shall_text", ""), 60)}"')
        lines.append(f'  type = "{req.get("type", "")}"')
        lines.append("}")

    test_cases = graph_data.get("test_cases", [])
    for tc in test_cases:
        lines.append(f'object "{tc.get("id", "TC")}" as {_safe_id(tc.get("id", ""))} #LightYellow {{')
        lines.append(f'  title = "{tc.get("title", "")}"')
        lines.append("}")

    links = graph_data.get("links", [])
    for link in links:
        from_id = _safe_id(link.get("from", ""))
        to_id = _safe_id(link.get("to", ""))
        rel = link.get("relationship", "traces_to")
        lines.append(f'{from_id} --> {to_id} : {rel}')

    lines.append("")
    lines.append("@enduml")
    return "\n".join(lines)


def _safe_id(text: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in text)


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."
