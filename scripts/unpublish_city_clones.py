#!/usr/bin/env python3
"""Return doorway city×service pages and leak clones to draft. Never touches 2973 or allowlisted city pages."""
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
from post_policy import should_unpublish, PILLAR_LEAK

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
LEAK_URL = "https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/"


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


def list_published():
    items, page = [], 1
    while True:
        st, data = api(f"/wp/v2/posts?per_page=100&page={page}&status=publish&_fields=id,slug,title,status")
        if st != 200 or not data:
            break
        items.extend(data)
        if len(data) < 100:
            break
        page += 1
        time.sleep(0.04)
    return items


def main():
    dry = "--apply" not in sys.argv
    st, p = api("/wp/v2/posts/2973?_fields=id,slug,status")
    if st != 200 or (p or {}).get("slug") != "water-leak-detection-company-in-qatar":
        raise SystemExit("ranking post lock failed")
    posts = list_published()
    targets = []
    for p in posts:
        pid = int(p["id"])
        slug = p.get("slug") or ""
        title = unescape((p.get("title") or {}).get("rendered") or "")
        if should_unpublish(pid, title, slug):
            targets.append((pid, slug, title))
    print(f"published={len(posts)} to_draft={len(targets)} dry={dry}", flush=True)
    for pid, slug, title in targets[:12]:
        print(f"TARGET {pid} {slug} {title[:50]}", flush=True)
    if dry:
        print("Re-run with --apply to set status=draft + noindex on these doorway pages.", flush=True)
        return
    ok = fail = 0
    for i, (pid, slug, title) in enumerate(targets, 1):
        payload = {"status": "draft"}
        st, out = api(f"/wp/v2/posts/{pid}", "POST", payload)
        if st not in (200, 201):
            fail += 1
            print(f"FAIL draft {pid} {slug} {st} {str(out)[:120]}", flush=True)
            continue
        leakish = any(m in f"{title} {slug}".lower() for m in ("كشف تسربات المياه", "water-leak", "water leak"))
        meta = {
            "rank_math_robots": ["noindex", "nofollow"],
        }
        if leakish and slug not in PILLAR_LEAK:
            meta["rank_math_canonical_url"] = LEAK_URL
        api("/rankmath/v1/updateMeta", "POST", {
            "objectType": "post",
            "objectID": pid,
            "meta": meta,
        })
        ok += 1
        if i % 50 == 0:
            print(f"progress {i}/{len(targets)} ok={ok} fail={fail}", flush=True)
        time.sleep(0.05)
    print(f"DONE drafted={ok} fail={fail}", flush=True)
    if fail:
        raise SystemExit(f"{fail} failed")


if __name__ == "__main__":
    main()
