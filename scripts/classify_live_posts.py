#!/usr/bin/env python3
"""Classify live /qa posts. Read-only. Never writes post 2973."""
from __future__ import annotations

import csv
import json
import os
import ssl
import time
import urllib.error
import urllib.request
from collections import Counter
from html import unescape
from pathlib import Path

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = __import__("base64").b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorClassify/1.0",
}

LOCKED = 2973
KEEP_SLUGS = {
    "water-leak-detection-company-in-qatar",
    "water-leak-detection-qatar-en",
    "roof-insulation-qatar-en",
    "ac-maintenance-qatar-en",
    "gas-leak-detection-doha",
    "ac-leak-detection-doha",
    "sewerage-company-in-doha",
}
CITY_SUF = (
    "-al-shahaniya",
    "-al-daayen",
    "-umm-salal",
    "-al-wakrah",
    "-al-rayyan",
    "-al-shamal",
    "-al-khor",
    "-lusail",
    "-doha",
)
CITY_AR = (
    "في الدوحة",
    "في الريان",
    "في الوكرة",
    "في الخور",
    "في أم صلال",
    "في الظعاين",
    "في الضعاين",
    "في الشمال",
    "في الشحانية",
    "في لوسيل",
    "في الخيسة",
)
HUB_SLUGS = {
    "services-in-doha-qatar",
    "services-in-al-rayyan-qatar",
    "services-in-al-wakrah-qatar",
    "services-in-al-khor-qatar",
    "services-in-umm-salal-qatar",
    "services-in-al-daayen-qatar",
    "services-in-al-shamal-qatar",
    "services-in-al-shahaniya-qatar",
    "services-in-lusail-qatar",
}


def api(path, timeout=90):
    url = path if path.startswith("http") else BASE + path
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
        return json.loads(r.read().decode() or "null"), {k.lower(): v for k, v in r.headers.items()}


def get_all(status: str):
    items = []
    page = 1
    while True:
        data, meta = api(
            f"/wp/v2/posts?per_page=100&page={page}&status={status}"
            "&context=edit&_fields=id,slug,status,title,link,date,modified"
        )
        if not data:
            break
        items.extend(data)
        pages = int(meta.get("x-wp-totalpages", 1) or 1)
        if page >= pages:
            break
        page += 1
        time.sleep(0.02)
    return items


def title_of(p):
    t = p.get("title") or {}
    return unescape(t.get("raw") or t.get("rendered") or "")


def city_suffix(slug: str) -> str | None:
    for s in CITY_SUF:
        if slug.endswith(s):
            return s[1:]
    return None


def is_leak_clone(slug: str, pid: int) -> bool:
    if pid == LOCKED or slug in KEEP_SLUGS:
        return False
    return slug.startswith("water-leak-detection-") or slug.startswith("water-pipe-leak-detection-")


def classify(p) -> str:
    pid = int(p["id"])
    slug = p.get("slug") or ""
    title = title_of(p)
    if pid == LOCKED or slug == "water-leak-detection-company-in-qatar":
        return "locked-leak"
    if slug in KEEP_SLUGS:
        return "allowlisted"
    if slug in HUB_SLUGS:
        return "city-hub"
    if is_leak_clone(slug, pid):
        return "leak-city-clone"
    if city_suffix(slug) or any(c in title for c in CITY_AR):
        return "city-template"
    if slug.endswith("-en") or slug.endswith("-qatar-en"):
        return "english"
    return "national"


def main():
    pubs = get_all("publish")
    drafts = get_all("draft")
    futures = get_all("future")
    rows = []
    counts = Counter()
    for status, bundle in (("publish", pubs), ("draft", drafts), ("future", futures)):
        for p in bundle:
            kind = classify(p)
            counts[f"{status}:{kind}"] += 1
            rows.append(
                {
                    "id": p["id"],
                    "status": status,
                    "kind": kind,
                    "slug": p.get("slug") or "",
                    "title": title_of(p),
                    "link": p.get("link") or "",
                    "date": p.get("date") or "",
                    "modified": p.get("modified") or "",
                }
            )
    out_dir = Path(__file__).resolve().parents[1] / "audit"
    out_dir.mkdir(exist_ok=True)
    csv_path = out_dir / "live-post-classification.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["id"])
        w.writeheader()
        w.writerows(rows)
    summary = {
        "publish_total": len(pubs),
        "draft_total": len(drafts),
        "future_total": len(futures),
        "counts": dict(counts),
        "publish_by_kind": dict(
            Counter(r["kind"] for r in rows if r["status"] == "publish")
        ),
        "locked_ok": any(r["id"] == LOCKED and r["kind"] == "locked-leak" for r in rows),
    }
    (out_dir / "live-post-classification.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    leftover = [r for r in rows if r["status"] == "publish" and r["kind"] == "city-template"]
    print(f"published city-template={len(leftover)} csv={csv_path}", flush=True)


if __name__ == "__main__":
    main()
