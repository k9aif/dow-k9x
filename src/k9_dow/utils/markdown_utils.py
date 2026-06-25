# SPDX-License-Identifier: Apache-2.0

import re


def strip_code_fences(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"```[a-zA-Z0-9_+-]*\s*", "", text).replace("```", "").strip()


def extract_first_json(text: str) -> str | None:
    match = re.search(r"\{[\s\S]*\}", text)
    return match.group(0).strip() if match else None


def truncate(text: str, max_len: int = 500) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."
