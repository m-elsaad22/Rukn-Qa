#!/usr/bin/env python3
"""Fix GSC indexing bugs. Never rewrites post 2973 body."""
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
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorGSCFix/1.0",
    "Content-Type": "application/json",
}
LOCKED = 2973
CANON_2973 = "https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/"


def api(path, method="GET", data=None, timeout=180):
    url = path if path.startswith("http") else BASE + path
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
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
            return e.code, raw[:800]


def note(msg):
    print(msg, flush=True)


def lockcheck():
    st, p = api(f"/wp/v2/posts/{LOCKED}?context=edit&_fields=id,slug,status,title")
    title = unescape((p.get("title") or {}).get("raw") or (p.get("title") or {}).get("rendered") or "")
    ok = (
        st == 200
        and p.get("id") == LOCKED
        and p.get("slug") == "water-leak-detection-company-in-qatar"
        and p.get("status") == "publish"
        and title == "شركة كشف تسربات المياه في قطر"
    )
    note(f"LOCK 2973 ok={ok} title={title!r}")
    if not ok:
        raise SystemExit("Ranking post 2973 changed — aborting")
    st2, p2 = api(f"/wp/v2/posts/{LOCKED}?context=edit&_fields=content")
    raw = ((p2.get("content") or {}).get("raw") or "") if isinstance(p2, dict) else ""
    if "الحل النهائي 2026" not in raw or "لماذا أصبح البحث عن شركة كشف تسربات المياه في قطر" not in raw:
        raise SystemExit("Ranking post 2973 body marker missing — aborting")
    note("LOCK 2973 body markers present")


def push_snippet():
    snippet_path = Path(__file__).with_name("snippet-rukn-qatar.php")
    code = snippet_path.read_text(encoding="utf-8")
    if "rukn_qa_gsc_path_fixes" not in code:
        raise SystemExit("snippet missing gsc path fixes")
    if "wp_safe_redirect(home_url(RUKN_QA_LEAK)" in code:
        raise SystemExit("snippet still 301s leak city posts")
    st, sn = api("/code-snippets/v1/snippets/5")
    note(f"snippet GET {st} active={sn.get('active') if isinstance(sn, dict) else sn}")
    payload = {
        "name": "Rukn Qatar SEO and contact fix",
        "desc": sn.get("desc") if isinstance(sn, dict) else "",
        "code": code,
        "tags": sn.get("tags") if isinstance(sn, dict) else [],
        "scope": "global",
        "active": True,
        "priority": (sn.get("priority") if isinstance(sn, dict) else 10) or 10,
    }
    st, out = api("/code-snippets/v1/snippets/5", "PUT", payload, timeout=180)
    err = out.get("code_error") if isinstance(out, dict) else out
    note(f"snippet PUT {st} err={err!r} len={len(code)}")
    if st not in (200, 201) or (isinstance(out, dict) and out.get("code_error")):
        raise SystemExit(f"snippet update failed: {out}")


def fix_2973_canonical():
    st, out = api(
        "/rankmath/v1/updateMeta",
        "POST",
        {
            "objectType": "post",
            "objectID": LOCKED,
            "meta": {"rank_math_canonical_url": CANON_2973, "rank_math_robots": ["index", "follow"]},
        },
    )
    note(f"CANON 2973 http={st} {out if not isinstance(out, dict) else {k: out.get(k) for k in list(out)[:8]}}")
    if st not in (200, 201):
        raise SystemExit("canonical update failed")


def fix_contact_duplicate():
    st, pages = api("/wp/v2/pages?slug=contact-us-2&status=publish&_fields=id,slug,link")
    if not isinstance(pages, list) or not pages:
        note("contact-us-2 not found")
        return None
    pid = pages[0]["id"]
    st, out = api(
        "/rankmath/v1/updateMeta",
        "POST",
        {
            "objectType": "post",
            "objectID": int(pid),
            "meta": {
                "rank_math_canonical_url": "https://www.rukn-eltatawer.com/qa/contact-us/",
                "rank_math_robots": ["noindex", "follow"],
            },
        },
    )
    note(f"CONTACT-2 {pid} http={st}")
    return pid


def main():
    lockcheck()
    push_snippet()
    lockcheck()
    fix_2973_canonical()
    lockcheck()
    contact = fix_contact_duplicate()
    st, purged = api("/rukn-qa/v1/purge-cache", "POST", {})
    note(f"PURGE {st} {purged}")
    time.sleep(1)
    lockcheck()
    summary = {
        "locked": 2973,
        "canonical_2973": CANON_2973,
        "contact_us_2": contact,
        "purged": purged,
        "snippet": "rukn_qa_gsc_path_fixes",
    }
    out = Path(__file__).resolve().parents[1] / "audit" / "gsc-indexing-fix.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note("DONE apply_gsc_indexing")


if __name__ == "__main__":
    main()
