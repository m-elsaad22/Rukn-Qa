#!/usr/bin/env python3
"""Point Qatar robots at the /qa/ sitemap and ping IndexNow. Never touches post 2973."""
from __future__ import annotations

import base64
import json
import os
import ssl
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorFix/1.0",
    "Content-Type": "application/json",
}
INDEXNOW_KEY = "a8af00632ab54314b60253cc2f140a6c"
LEAK = "https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/"


def api(path, method="GET", data=None, timeout=90, base="https://www.rukn-eltatawer.com/qa/wp-json"):
    url = path if path.startswith("http") else base + path
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw[:500]


def lockcheck():
    code, p = api("/wp/v2/posts/2973?context=edit&_fields=id,slug,status,title")
    title = unescape((p.get("title") or {}).get("raw") or "")
    ok = p.get("slug") == "water-leak-detection-company-in-qatar" and title == "شركة كشف تسربات المياه في قطر"
    print("LOCK 2973", ok, flush=True)
    if not ok:
        raise SystemExit("abort: ranking post changed")


def main():
    lockcheck()
    snippet_path = Path(__file__).with_name("snippet-rukn-qatar.php")
    code = snippet_path.read_text()
    st, sn = api("/code-snippets/v1/snippets/5")
    st, out = api("/code-snippets/v1/snippets/5", "PUT", {
        "name": "Rukn Qatar SEO and contact fix",
        "code": code,
        "scope": "global",
        "active": True,
        "priority": (sn.get("priority") if isinstance(sn, dict) else 10) or 10,
    }, timeout=120)
    print("snippet PUT", st, "err", out.get("code_error") if isinstance(out, dict) else out, flush=True)
    lockcheck()

    st, info = api("/rukn-qa/v1/robots-file")
    print("robots GET", st, {k: info.get(k) for k in ("path", "exists", "writable")} if isinstance(info, dict) else info, flush=True)
    st, info = api("/rukn-qa/v1/robots-file", "POST", {})
    print("robots POST", st, json.dumps({k: info.get(k) for k in ("wrote", "bytes", "writable", "path")} if isinstance(info, dict) else {"raw": info}, ensure_ascii=False), flush=True)
    if isinstance(info, dict):
        print("robots current:\n", info.get("current"), flush=True)
    lockcheck()

    # Collect published URLs to notify (cleaning + hubs + leak). Skip city leak clones.
    urls = [LEAK, "https://www.rukn-eltatawer.com/qa/", "https://www.rukn-eltatawer.com/qa/house-cleaning-in-qatar/", "https://www.rukn-eltatawer.com/qa/villa-cleaning-in-qatar/", "https://www.rukn-eltatawer.com/qa/apartment-cleaning-in-qatar/", "https://www.rukn-eltatawer.com/qa/home-cleaning-doha/", "https://www.rukn-eltatawer.com/qa/services-in-doha-qatar/", "https://www.rukn-eltatawer.com/qa/services-in-lusail-qatar/", "https://www.rukn-eltatawer.com/qa/as3ar/", "https://www.rukn-eltatawer.com/qa/sitemap_index.xml"]
    page = 1
    while True:
        st, posts = api(f"/wp/v2/posts?per_page=100&page={page}&status=publish&_fields=id,link,slug")
        if st != 200 or not posts:
            break
        for p in posts:
            slug = p.get("slug") or ""
            if slug.startswith("water-leak-detection-") and p.get("id") != 2973:
                continue
            if slug.startswith("water-pipe-leak-detection-"):
                continue
            link = p.get("link")
            if link:
                urls.append(link)
        if len(posts) < 100:
            break
        page += 1
    # unique, cap 200 (IndexNow limit per request often 10k but keep modest)
    seen = []
    for u in urls:
        if u not in seen:
            seen.append(u)
    urls = seen[:180]
    payload = {
        "host": "www.rukn-eltatawer.com",
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://www.rukn-eltatawer.com/qa/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "Mozilla/5.0 CursorFix/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
            print("IndexNow", r.status, r.read()[:200], "urls", len(urls), flush=True)
    except urllib.error.HTTPError as e:
        print("IndexNow err", e.code, e.read()[:300], "urls", len(urls), flush=True)
    lockcheck()
    print("DONE fix_indexing", flush=True)


if __name__ == "__main__":
    main()
