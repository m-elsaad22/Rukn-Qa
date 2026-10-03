#!/usr/bin/env python3
"""Expand published national Qatar articles past 1000 words. Never edits post 2973."""
from __future__ import annotations

import base64
import csv
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
from article_longform import build_longform_payload, word_count

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorLongform/1.0",
    "Content-Type": "application/json",
}
LOCKED = {2973}


def api(path, method="GET", data=None, timeout=120):
    url = path if path.startswith("http") else BASE + path
    body = None if data is None else json.dumps(data).encode()
    last = None
    for attempt in range(4):
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
                return e.code, raw[:400]
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise last


def note(msg):
    print(msg, flush=True)


def lockcheck():
    st, p = api("/wp/v2/posts/2973?_fields=id,slug,status,title")
    title = unescape((p.get("title") or {}).get("rendered") or "")
    ok = st == 200 and p.get("id") == 2973 and p.get("slug") == "water-leak-detection-company-in-qatar"
    note(f"LOCK 2973 {ok} {title[:50]!r}")
    if not ok:
        raise SystemExit("ranking lock failed")


def list_posts():
    posts, page = [], 1
    while True:
        st, data = api(
            f"/wp/v2/posts?per_page=100&page={page}&status=publish&context=edit"
            "&_fields=id,slug,title,content"
        )
        if st != 200 or not data:
            break
        posts.extend(data)
        if len(data) < 100:
            break
        page += 1
        time.sleep(0.02)
    return posts


def set_terms(pid, tags):
    if int(pid) in LOCKED:
        return
    ids = []
    for name in tags:
        st, found = api(f"/wp/v2/tags?search={urllib_quote(name)}&per_page=5")
        match = None
        if st == 200 and isinstance(found, list):
            for t in found:
                if (t.get("name") or "").strip() == name:
                    match = t
                    break
        if not match:
            st, created = api("/wp/v2/tags", "POST", {"name": name})
            if st in (200, 201) and isinstance(created, dict):
                match = created
        if match:
            ids.append(int(match["id"]))
        time.sleep(0.02)
    if ids:
        api(f"/wp/v2/posts/{pid}", "POST", {"tags": ids})


def urllib_quote(s):
    import urllib.parse

    return urllib.parse.quote(s)


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


def theme_fields(meta: dict) -> dict:
    out = {}
    for key, val in meta.items():
        out[key] = json.dumps(val, ensure_ascii=False) if isinstance(val, (dict, list)) else val
    return out


def main():
    lockcheck()
    posts = list_posts()
    note(f"published {len(posts)}")
    rows = []
    ok = skip = fail = 0
    for p in posts:
        pid = int(p["id"])
        slug = p.get("slug") or ""
        title = unescape((p.get("title") or {}).get("raw") or (p.get("title") or {}).get("rendered") or "")
        if pid in LOCKED or slug == "water-leak-detection-company-in-qatar":
            skip += 1
            rows.append({"id": pid, "slug": slug, "title": title, "status": "locked", "words": ""})
            continue
        lang = "en" if slug.endswith("-en") or slug.endswith("-qatar-en") else "ar"
        try:
            payload = build_longform_payload(title, slug, lang)
            words = payload["word_count"]
            body = {
                "content": payload["html"],
                "excerpt": payload["excerpt"],
            }
            st, _ = api(f"/wp/v2/posts/{pid}", "POST", body)
            if st not in (200, 201):
                raise RuntimeError(f"update {st}")
            rm_meta(pid, title, payload["desc"], payload["keyword"])
            meta = payload.get("meta") or {}
            if meta:
                api(f"/wp/v2/posts/{pid}", "POST", {"meta": theme_fields(meta)})
            ok += 1
            rows.append({
                "id": pid, "slug": slug, "title": title, "status": "updated",
                "words": words, "ptype": payload.get("ptype"), "http": st,
            })
            if ok % 10 == 0:
                note(f"updated {ok} last={pid} {slug} words={words}")
        except Exception as e:
            fail += 1
            rows.append({"id": pid, "slug": slug, "title": title, "status": f"fail:{e}", "words": ""})
            note(f"FAIL {pid} {slug} {e}")
        time.sleep(0.05)
    lockcheck()
    out = Path(__file__).resolve().parents[1] / "audit"
    out.mkdir(exist_ok=True)
    csv_path = out / "national-longform-results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "slug", "title", "status", "words", "ptype", "http"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})
    short = [r for r in rows if r.get("status") == "updated" and int(r.get("words") or 0) < 1000]
    summary = {
        "updated": ok,
        "locked": skip,
        "failed": fail,
        "short_after": [{"id": r["id"], "slug": r["slug"], "words": r["words"]} for r in short],
    }
    (out / "national-longform-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    note(json.dumps(summary, ensure_ascii=False, indent=2))
    note("DONE expand_national_articles")


if __name__ == "__main__":
    main()
