# SPDX-License-Identifier: Apache-2.0
# K9-AIF Framework
"""DAS web login: two roles, checked on the server.

    viewer  DAS_DEMO_USER / DAS_DEMO_PASSWORD (default demo / demo): run jobs, view
    admin   DAS_ADMIN_USER / DAS_ADMIN_PASSWORD: also starts the next stage after
            a HIL approval (POST /jobs/{id}/advance). No admin password = no admin.

Tokens are HMAC-signed (DAS_SESSION_SECRET; a random per-process secret if
unset, which signs everyone out on restart) and expire after 12 hours.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Optional

from fastapi import Header, HTTPException

_SECRET = (os.environ.get("DAS_SESSION_SECRET") or secrets.token_hex(32)).encode()
_TTL = 12 * 3600


def _accounts() -> dict:
    accts = {os.environ.get("DAS_DEMO_USER", "demo"): (os.environ.get("DAS_DEMO_PASSWORD", "demo"), "viewer")}
    admin_pw = os.environ.get("DAS_ADMIN_PASSWORD", "")
    if admin_pw:
        accts[os.environ.get("DAS_ADMIN_USER", "admin")] = (admin_pw, "admin")
    return accts


def public_logins() -> dict:
    """Shown on the sign-in page (public demonstration deployment)."""
    out = {"demo": {"user": os.environ.get("DAS_DEMO_USER", "demo"),
                    "password": os.environ.get("DAS_DEMO_PASSWORD", "demo")}}
    if os.environ.get("DAS_ADMIN_PASSWORD") and os.environ.get("DAS_SHOW_ADMIN_LOGIN", "true").lower() == "true":
        out["admin"] = {"user": os.environ.get("DAS_ADMIN_USER", "admin"),
                        "password": os.environ["DAS_ADMIN_PASSWORD"]}
    return out


def login(username: str, password: str) -> Optional[dict]:
    rec = _accounts().get((username or "").strip())
    if not rec or not hmac.compare_digest(rec[0].encode(), (password or "").encode()):
        return None
    body = base64.urlsafe_b64encode(json.dumps(
        {"u": username.strip(), "r": rec[1], "exp": int(time.time()) + _TTL}).encode()).decode()
    sig = hmac.new(_SECRET, body.encode(), hashlib.sha256).hexdigest()
    return {"token": f"{body}.{sig}", "user": username.strip(), "role": rec[1]}


def verify(token: str) -> Optional[dict]:
    try:
        body, sig = token.rsplit(".", 1)
        if not hmac.compare_digest(sig, hmac.new(_SECRET, body.encode(), hashlib.sha256).hexdigest()):
            return None
        data = json.loads(base64.urlsafe_b64decode(body.encode()))
        return data if data.get("exp", 0) > time.time() else None
    except Exception:
        return None


def require_admin(authorization: str = Header(default="")) -> dict:
    data = verify(authorization.removeprefix("Bearer ").strip()) if authorization else None
    if not data:
        raise HTTPException(status_code=401, detail="Sign in required")
    if data.get("r") != "admin":
        raise HTTPException(status_code=403, detail="DAS admin only")
    return data
