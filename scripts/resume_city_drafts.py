#!/usr/bin/env python3
"""Slowly publish leftover city drafts via server-side HTML. Never touches 2973."""
from __future__ import annotations

import base64
import json
import os
import ssl
import time
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorCityResume/1.0",
    "Content-Type": "application/json",
}


def api(path, method="GET", data=None, timeout=120):
    url = path if path.startswith("http") else BASE + path
    body = None if data is None else json.dumps(data).encode()
    try:
        req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
            raw = r.read().decode() or "null"
            try:
                return r.status, json.loads(raw)
            except json.JSONDecodeError:
                return r.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw[:200]


def note(msg):
    print(msg, flush=True)


def lockcheck():
    st, p = api("/wp/v2/posts/2973?context=edit&_fields=id,slug,status,title")
    if not isinstance(p, dict):
        note(f"LOCK skip {st}")
        return
    title = unescape((p.get("title") or {}).get("raw") or "")
    ok = st == 200 and p.get("id") == 2973 and p.get("status") == "publish"
    note(f"LOCK 2973 ok={ok} {title!r}")
    if st == 200 and not ok:
        raise SystemExit("lock failed")


def push_snippet():
    code = Path(__file__).with_name("snippet-rukn-qatar.php").read_text(encoding="utf-8")
    if "publish-next-city-drafts" not in code:
        raise SystemExit("missing publish-next-city-drafts")
    st, sn = api("/code-snippets/v1/snippets/5")
    if st != 200 or not isinstance(sn, dict):
        note(f"snippet GET {st} — will retry later")
        return False
    st, out = api("/code-snippets/v1/snippets/5", "PUT", {
        "name": "Rukn Qatar SEO and contact fix",
        "desc": sn.get("desc") or "",
        "code": code,
        "tags": sn.get("tags") or [],
        "scope": "global",
        "active": True,
        "priority": sn.get("priority") or 10,
    }, timeout=180)
    err = out.get("code_error") if isinstance(out, dict) else out
    note(f"snippet PUT {st} err={err!r}")
    return st in (200, 201) and not (isinstance(out, dict) and out.get("code_error"))


def main():
    lockcheck()
    for _ in range(6):
        if push_snippet():
            break
        time.sleep(15)
    total = 0
    empty = 0
    for i in range(250):
        st, out = api("/rukn-qa/v1/publish-next-city-drafts", "POST", {"limit": 2}, timeout=90)
        if st == 508:
            note(f"508 sleep 25s i={i} total={total}")
            time.sleep(25)
            continue
        n = out.get("updated") if isinstance(out, dict) else 0
        if st not in (200, 201):
            note(f"http {st} {str(out)[:120]}")
            time.sleep(10)
            continue
        if not n:
            empty += 1
            note(f"empty {empty} {out}")
            if empty >= 3:
                break
            time.sleep(4)
            continue
        empty = 0
        total += n
        last = (out.get("items") or [{}])[-1].get("slug")
        note(f"ok +{n} total={total} last={last}")
        time.sleep(2.5)
    lockcheck()
    note(f"DONE resume total={total}")


if __name__ == "__main__":
    main()
