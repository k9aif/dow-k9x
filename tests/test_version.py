# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""One version, in VERSION: the API, the CLI and the package all report it, and a release tag
matches it. Before v1.3.5 VERSION said 0.2.0 through every v1.x release, so the live site showed
"DAS 0.2.0" while running v1.3.4."""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _version():
    return (ROOT / "VERSION").read_text().strip()


def test_version_is_one_value_everywhere():
    v = _version()
    assert re.fullmatch(r"\d+\.\d+\.\d+", v)
    assert f'version = "{v}"' in (ROOT / "pyproject.toml").read_text()
    from k9_dow.config.settings import build_info
    assert build_info()["version"] == v


def test_no_version_number_is_written_into_the_code():
    hits = [str(p) for p in (ROOT / "src").rglob("*.py")
            # a reported version (assignment or banner); history notes such as "(v1.3.4)" are fine
            if re.search(r"""version\s*=\s*["']\d+\.\d+\.\d+["']|System v\d+\.\d+""", p.read_text())]
    assert hits == []


def test_a_tagged_commit_carries_its_tag_version():
    try:
        tags = subprocess.run(["git", "-C", str(ROOT), "tag", "--points-at", "HEAD"],
                              capture_output=True, text=True, timeout=5).stdout.split()
    except Exception:
        return                                   # not a git checkout (image build)
    releases = [t for t in tags if re.fullmatch(r"v\d+\.\d+\.\d+", t)]
    if not releases:
        return
    tagged = subprocess.run(["git", "-C", str(ROOT), "show", "HEAD:VERSION"],
                            capture_output=True, text=True, timeout=5).stdout.strip()
    for tag in releases:
        assert tag[1:] == tagged, f"{tag} is tagged on a commit whose VERSION is {tagged}"
