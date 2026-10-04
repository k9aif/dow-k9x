# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""The sign-in page never shows the admin login, whatever the environment says."""

from k9_dow.api import auth


def test_admin_login_never_published(monkeypatch):
    monkeypatch.setenv("DAS_ADMIN_PASSWORD", "secret-admin-pw")
    monkeypatch.setenv("DAS_SHOW_ADMIN_LOGIN", "true")
    out = auth.public_logins()
    assert set(out) == {"demo"}
    assert "secret-admin-pw" not in str(out)
