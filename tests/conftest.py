# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""Unit tests run in the test environment (most build agents with a minimal
config on purpose). Production governance with the real DAS config is tested
explicitly in test_governance.py."""

import os

os.environ.setdefault("K9_ENV", "test")
