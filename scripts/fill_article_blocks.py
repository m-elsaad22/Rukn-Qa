#!/usr/bin/env python3
"""Fill KAYAN theme article metaboxes and insert shortcodes. Never edits post 2973."""
from __future__ import annotations

import base64
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kayan_article_builder import WA, build_theme_payload

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorFix/1.0",
    "Content-Type": "application/json",
}
LOCKED = {2973}
SKIP_SERVICES = {1877}


def api(path, method="GET", data=None, timeout=180):
    url = path if path.startswith("http") else BASE + path
    body = None if data is None else json.dumps(data, ensure_ascii=False).encode()
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


def assert_lock():
    st, p = api("/wp/v2/posts/2973?_fields=id,slug,status,title")
    title = unescape((p.get("title") or {}).get("rendered") or "")
    ok = st == 200 and p.get("slug") == "water-leak-detection-company-in-qatar" and p.get("status") == "publish"
    note(f"LOCK 2973 ok={ok} title={title[:60]!r}")
    if not ok:
        raise SystemExit("ranking post lock failed")


def push_snippet():
    code = Path(__file__).with_name("snippet-rukn-qatar.php").read_text()
    if "/post-blocks" not in code:
        raise SystemExit("snippet missing post-blocks route")
    st, sn = api("/code-snippets/v1/snippets/5")
    st, out = api("/code-snippets/v1/snippets/5", "PUT", {
        "name": "Rukn Qatar SEO and contact fix",
        "desc": sn.get("desc") if isinstance(sn, dict) else "",
        "code": code,
        "tags": sn.get("tags") if isinstance(sn, dict) else [],
        "scope": "global",
        "active": True,
        "priority": (sn.get("priority") if isinstance(sn, dict) else 10) or 10,
    })
    err = out.get("code_error") if isinstance(out, dict) else out
    note(f"snippet PUT {st} err={err!r}")
    if st not in (200, 201) or (isinstance(out, dict) and out.get("code_error")):
        raise SystemExit("snippet failed")


def list_type(rest_base):
    items = []
    page = 1
    while True:
        st, data = api(f"/wp/v2/{rest_base}?per_page=100&page={page}&status=publish&_fields=id,slug,title,link")
        if st != 200 or not data:
            break
        items.extend(data)
        if len(data) < 100:
            break
        page += 1
    return items


def fill_one(pid, title, slug, link, lang, is_post=True):
    if pid in LOCKED:
        return "skip"
    payload = build_theme_payload(title, slug, lang)
    meta = payload["meta"]
    if isinstance(meta.get("YourColor_Service"), dict):
        meta["YourColor_Service"]["identifier"] = link or ""
    st, out = api("/rukn-qa/v1/post-blocks", "POST", {
        "id": pid,
        "content": payload["html"],
        "excerpt": payload["excerpt"],
        "tags": payload["tags"] if is_post else [],
        "cities": payload["cities"] if is_post else [],
        "meta": meta,
    })
    if st in (200, 201) and isinstance(out, dict) and "locked" not in str(out.get("code", "")):
        api("/rankmath/v1/updateMeta", "POST", {
            "objectType": "post",
            "objectID": int(pid),
            "meta": {
                "rank_math_title": f"{title} | ركن التطور قطر",
                "rank_math_description": payload["desc"],
                "rank_math_focus_keyword": payload["keyword"],
            },
        })
        return "ok"
    note(f"FAIL {pid} {slug} {st} {str(out)[:180]}")
    return "fail"


def main():
    os.chdir(Path(__file__).resolve().parent)
    assert_lock()
    push_snippet()
    assert_lock()
    posts = list_type("posts")
    services = list_type("services")
    note(f"published posts={len(posts)} services={len(services)}")
    ok = skip = fail = 0
    for p in posts:
        pid = int(p["id"])
        slug = p.get("slug") or ""
        title = unescape((p.get("title") or {}).get("rendered") or "")
        lang = "en" if slug.endswith("-en") or slug.endswith("qatar-en") else "ar"
        result = fill_one(pid, title, slug, p.get("link") or "", lang, True)
        if result == "ok":
            ok += 1
        elif result == "skip":
            skip += 1
            note(f"SKIP locked {pid} {slug}")
        else:
            fail += 1
        if (ok + skip + fail) % 10 == 0:
            note(f"progress posts ok={ok} skip={skip} fail={fail}")
            assert_lock()
        time.sleep(0.06)
    for p in services:
        pid = int(p["id"])
        if pid in SKIP_SERVICES:
            skip += 1
            note(f"SKIP service {pid}")
            continue
        slug = p.get("slug") or ""
        title = unescape((p.get("title") or {}).get("rendered") or "")
        result = fill_one(pid, title, slug, p.get("link") or "", "ar", False)
        if result == "ok":
            ok += 1
        else:
            fail += 1
            note(f"service {pid} {result}")
        time.sleep(0.06)
    assert_lock()
    api("/rukn-qa/v1/robots-file", "POST", {})
    note(f"DONE ok={ok} skipped={skip} fail={fail}")
    if fail:
        raise SystemExit(f"{fail} items failed")


if __name__ == "__main__":
    main()
