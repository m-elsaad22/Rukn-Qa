#!/usr/bin/env python3
"""Improve then publish Qatar city×service drafts. Never writes post 2973 or leak clones."""
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

from city_profiles import SUF_ORDER, is_leak_city_slug, slug_suffix
from city_service_articles import build_city_article
from cleaning_variant_articles import VARIANTS, payload_for as variant_payload

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
SITE = "https://www.rukn-eltatawer.com/qa"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorCityPublish/1.0",
    "Content-Type": "application/json",
}
LOCKED = 2973
BATCH = 5


def api(path, method="GET", data=None, timeout=180):
    url = path if path.startswith("http") else BASE + path
    body = None if data is None else json.dumps(data).encode()
    last = None
    for attempt in range(5):
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
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise last


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


def push_snippet():
    snippet_path = Path(__file__).with_name("snippet-rukn-qatar.php")
    code = snippet_path.read_text(encoding="utf-8")
    if "bulk-publish-posts" not in code or "clear-city-hub-redirects" not in code:
        raise SystemExit("snippet missing city publish routes")
    if "2973" not in code:
        raise SystemExit("snippet missing ranking lock")
    st, sn = api("/code-snippets/v1/snippets/5")
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
        raise SystemExit("snippet update failed")


def list_drafts():
    items, page = [], 1
    while True:
        st, data = None, None
        for attempt in range(5):
            st, data = api(
                f"/wp/v2/posts?per_page=100&page={page}&status=draft&context=edit&_fields=id,slug,title"
            )
            if st == 200 and isinstance(data, list):
                break
            time.sleep(6 * (attempt + 1))
        if st != 200 or not data:
            break
        items.extend(data)
        if len(data) < 100:
            break
        page += 1
    return items


def publish_cities(drafts):
    jobs = []
    skipped = []
    for p in drafts:
        pid = int(p["id"])
        slug = p.get("slug") or ""
        title = unescape((p.get("title") or {}).get("raw") or "")
        if pid == LOCKED or is_leak_city_slug(slug):
            skipped.append({"id": pid, "slug": slug, "reason": "leak-or-lock"})
            continue
        if not slug_suffix(slug):
            continue
        try:
            html, desc, words = build_city_article(title, slug)
        except Exception as e:
            skipped.append({"id": pid, "slug": slug, "reason": str(e)})
            continue
        jobs.append(
            {
                "id": pid,
                "slug": slug,
                "title": title,
                "content": html,
                "excerpt": desc,
                "description": desc,
                "canonical": f"{SITE}/{slug}/",
                "words": words,
            }
        )
    note(f"city jobs={len(jobs)} skipped={len(skipped)}")
    updated = 0
    fails = []
    for i in range(0, len(jobs), BATCH):
        chunk = jobs[i : i + BATCH]
        payload = [{k: j[k] for k in ("id", "slug", "title", "content", "excerpt", "description", "canonical")} for j in chunk]
        st, out, n = 0, None, 0
        for attempt in range(6):
            st, out = api("/rukn-qa/v1/bulk-publish-posts", "POST", {"items": payload}, timeout=180)
            n = out.get("updated") if isinstance(out, dict) else 0
            if st in (200, 201) and n:
                break
            wait = 8 * (attempt + 1)
            note(f"RETRY {i}-{i+len(chunk)} http={st} sleep={wait}s")
            time.sleep(wait)
            if len(payload) > 1:
                payload = payload[: max(1, len(payload) // 2)]
        updated += int(n or 0)
        if st not in (200, 201) or not n:
            fails.append({"http": st, "out": str(out)[:300], "ids": [j["id"] for j in chunk]})
            note(f"BATCH FAIL {i}-{i+len(chunk)} http={st} {str(out)[:180]}")
        elif (i // BATCH) % 10 == 0:
            note(f"city published {updated}/{len(jobs)} last={chunk[-1]['slug']} words={chunk[-1]['words']}")
        time.sleep(0.4)
    return {"jobs": len(jobs), "updated": updated, "skipped": skipped[:30], "fails": fails, "min_words": min((j["words"] for j in jobs), default=0)}


def publish_variants():
    rows = []
    for pid in VARIANTS:
        if pid == LOCKED:
            continue
        payload = variant_payload(pid)
        st, out = api(
            "/rukn-qa/v1/bulk-publish-posts",
            "POST",
            {
                "items": [
                    {
                        "id": pid,
                        "slug": payload["slug"],
                        "title": payload["title"],
                        "content": payload["html"],
                        "excerpt": payload["desc"],
                        "description": payload["desc"],
                        "canonical": f"{SITE}/{payload['slug']}/",
                    }
                ]
            },
        )
        api("/rukn-qa/v1/redirect-delete", "POST", {"from": payload["slug"]})
        note(f"VARIANT {pid} {payload['slug']} http={st} words={payload['words']}")
        rows.append({"id": pid, "slug": payload["slug"], "words": payload["words"], "http": st})
        time.sleep(0.05)
    return rows


def main():
    lockcheck()
    push_snippet()
    lockcheck()
    st, cleared = api("/rukn-qa/v1/clear-city-hub-redirects", "POST", {})
    note(f"clear hub redirects {st} {cleared}")
    drafts = list_drafts()
    note(f"drafts {len(drafts)}")
    cities = publish_cities(drafts)
    variants = publish_variants()
    st, purged = api("/rukn-qa/v1/purge-cache", "POST", {})
    note(f"PURGE {st} {purged}")
    try:
        lockcheck()
    except Exception as e:
        note(f"lockcheck after 508 skipped: {e}")
    summary = {"cities": cities, "variants": variants, "locked": 2973}
    out = Path(__file__).resolve().parents[1] / "audit" / "city-coverage-publish.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note(json.dumps({"city_updated": cities.get("updated"), "city_jobs": cities.get("jobs"), "min_words": cities.get("min_words"), "variant_n": len(variants)}, ensure_ascii=False))
    note("DONE publish_city_coverage")


if __name__ == "__main__":
    main()
