# SPDX-License-Identifier: Apache-2.0
"""docs/inputs/ keeps a browsable copy of every demo sample document. The app reads
src/k9_dow/api/static/demos/; this test fails if a copy is missing or differs from it."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMOS = ROOT / "src/k9_dow/api/static/demos"
INPUTS = ROOT / "docs/inputs"


def test_every_demo_sample_is_copied_unchanged_to_docs_inputs():
    samples = sorted(p for p in DEMOS.iterdir() if p.is_file() and p.suffix in (".md", ".txt"))
    assert samples, "no demo sample documents found"
    for src in samples:
        copy = INPUTS / src.name
        assert copy.is_file(), f"docs/inputs/{src.name} missing: copy it from {src.relative_to(ROOT)}"
        assert copy.read_bytes() == src.read_bytes(), (
            f"docs/inputs/{src.name} differs from {src.relative_to(ROOT)}: the demos folder is the source")
