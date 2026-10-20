#!/usr/bin/env python3
"""PUT the GSC indexing snippet live. Never edits snippet 5 or post 2973."""
from __future__ import annotations

import base64
import json
import os
import ssl
import urllib.error
import urllib.request
from pathlib import Path

USER = os.environ.get("WP_USERNAME") or os.environ.get("WP_USER") or "cursor"
PW = os.environ.get("WP_APP_PASSWORD", "")
BASE = (os.environ.get("WP_BASE_URL") or "https://www.rukn-eltatawer.com/qa").rstrip("/")
if not PW:
    raise SystemExit("Set WP_APP_PASSWORD")

AUTH = base64.b64encode(f"{USER}:{PW}".encode()).decode()
CTX = ssl.create_default_context()
ROOT = Path(__file__).resolve().parents[1]


def api(method: str, path: str, data=None, timeout=120):
    url = path if path.startswith("http") else BASE + "/" + path.lstrip("/")
    headers = {
        "Authorization": f"Basic {AUTH}",
        "User-Agent": "RuknQA-GSC/1.0",
        "Accept": "application/json",
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            raw = r.read().decode()
            return r.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"raw": raw[:800]}
        print("HTTP", e.code, path, parsed)
        raise


def lock_2973():
    st, p = api("GET", "/wp-json/wp/v2/posts/2973?context=edit&_fields=id,slug,status,title")
    title = ((p.get("title") or {}).get("raw") or "")
    ok = p.get("id") == 2973 and p.get("slug") == "water-leak-detection-company-in-qatar"
    print("LOCK 2973", ok, title[:80], flush=True)
    if not ok:
        raise SystemExit("abort: ranking post changed")


def main():
    lock_2973()
    code = (ROOT / "snippets" / "gsc-indexing-fix.php").read_text()
    payload = {
        "name": "Rukn Qatar GSC indexing fix",
        "desc": "Sitemap exclusions, /qa/qa/ collapse, real EN hreflang only. Does not touch snippet 5.",
        "code": code,
        "scope": "global",
        "active": True,
        "priority": 3,
    }
    existing = None
    for sid in range(1, 40):
        try:
            st, sn = api("GET", f"/wp-json/code-snippets/v1/snippets/{sid}?t=gsc")
        except Exception:
            continue
        if isinstance(sn, dict) and sn.get("name") == "Rukn Qatar GSC indexing fix":
            existing = sn
            break
        if isinstance(sn, dict) and "gsc-indexing" in (sn.get("code") or "")[:400]:
            existing = sn
            break
    if existing:
        sid = existing["id"]
        st, out = api("PUT", f"/wp-json/code-snippets/v1/snippets/{sid}", payload)
        print("PUT snippet", sid, st, "err", out.get("code_error"), "active", out.get("active"))
    else:
        st, out = api("POST", "/wp-json/code-snippets/v1/snippets", payload)
        print("POST snippet", st, out.get("id"), "err", out.get("code_error"), "active", out.get("active"))

    s5 = api("GET", "/wp-json/code-snippets/v1/snippets/5?t=1")[1]
    print("snippet 5 still", s5.get("name"), "active", s5.get("active"))
    lock_2973()
    try:
        st, rr = api("POST", "/wp-json/rukn-qa/v1/gsc-fix", {})
        print("gsc-fix", st, rr)
    except Exception as e:
        print("gsc-fix endpoint not ready yet", e)
    lock_2973()
    print("DONE")


if __name__ == "__main__":
    main()
