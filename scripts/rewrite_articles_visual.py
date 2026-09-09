#!/usr/bin/env python3
"""Rewrite published Qatar articles with visual KAYAN blocks. Never edits post 2973."""
from __future__ import annotations

import base64
import json
import os
import ssl
import time
import urllib.error
import urllib.request
from html import unescape
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kayan_article_builder import build_article

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


def api(path, method="GET", data=None, timeout=120):
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
            return e.code, raw[:500]


def note(msg):
    print(msg, flush=True)


def assert_lock():
    st, p = api("/wp/v2/posts/2973?_fields=id,slug,status,title")
    title = unescape((p.get("title") or {}).get("rendered") or (p.get("title") or {}).get("raw") or "")
    ok = st == 200 and p.get("slug") == "water-leak-detection-company-in-qatar" and p.get("status") == "publish"
    note(f"LOCK 2973 ok={ok} title={title[:60]!r}")
    if not ok:
        raise SystemExit("ranking post lock failed")


def push_snippet():
    code = Path(__file__).with_name("snippet-rukn-qatar.php").read_text()
    if "rukn-article-ui" not in code:
        raise SystemExit("snippet missing article CSS")
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


def list_posts():
    posts = []
    page = 1
    while True:
        st, data = api(f"/wp/v2/posts?per_page=100&page={page}&status=publish&_fields=id,slug,title")
        if st != 200 or not data:
            break
        posts.extend(data)
        if len(data) < 100:
            break
        page += 1
    return posts


def rm_meta(pid, title, desc, keyword):
    if int(pid) in LOCKED:
        return
    api("/rankmath/v1/updateMeta", "POST", {
        "objectType": "post",
        "objectID": int(pid),
        "meta": {
            "rank_math_title": f"{title} | ركن التطور قطر",
            "rank_math_description": desc,
            "rank_math_focus_keyword": keyword,
        },
    })


def rewrite_posts():
    posts = list_posts()
    note(f"published {len(posts)}")
    ok = skip = fail = 0
    for p in posts:
        pid = int(p["id"])
        slug = p.get("slug") or ""
        title = unescape((p.get("title") or {}).get("rendered") or "")
        if pid in LOCKED:
            note(f"SKIP locked {pid} {slug}")
            skip += 1
            continue
        lang = "en" if slug.endswith("-en") or slug.endswith("qatar-en") else "ar"
        html, desc, kw = build_article(title, slug, lang)
        st, out = api(f"/wp/v2/posts/{pid}", "POST", {"content": html})
        if st not in (200, 201):
            note(f"FAIL post {pid} {slug} {st} {str(out)[:120]}")
            fail += 1
            continue
        rm_meta(pid, title, desc, kw)
        ok += 1
        if ok % 10 == 0:
            note(f"progress posts {ok}")
            assert_lock()
        time.sleep(0.08)
    return ok, skip, fail


def rewrite_services():
    st, items = api("/wp/v2/services?per_page=50&status=publish&_fields=id,slug,title")
    if st != 200 or not isinstance(items, list):
        note(f"services list {st}")
        return 0
    n = 0
    for p in items:
        if pid == 1877:
            note("SKIP service 1877 leak CPT")
            continue
        slug = p.get("slug") or ""
        html, desc, kw = build_article(title, slug, "ar")
        st, _ = api(f"/wp/v2/services/{pid}", "POST", {"content": html})
        note(f"service {pid} {st}")
        if pid != 1877:
            api("/rankmath/v1/updateMeta", "POST", {
                "objectType": "post",
                "objectID": pid,
                "meta": {
                    "rank_math_title": f"{title} | ركن التطور قطر",
                    "rank_math_description": desc,
                    "rank_math_focus_keyword": kw,
                },
            })
        n += 1
        time.sleep(0.08)
    return n


def main():
    os.chdir(Path(__file__).resolve().parent)
    assert_lock()
    push_snippet()
    assert_lock()
    ok, skip, fail = rewrite_posts()
    ns = rewrite_services()
    assert_lock()
    note(f"DONE posts_ok={ok} skipped={skip} fail={fail} services={ns}")
    if fail:
        raise SystemExit(f"{fail} posts failed")


if __name__ == "__main__":
    main()
