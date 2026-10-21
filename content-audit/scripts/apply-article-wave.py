#!/usr/bin/env python3
"""
Apply the first Qatar article wave to live WordPress.

Default is dry-run. Pass --apply to PUT/POST.

Never edits Code Snippet 5. Never writes post #2973.
Never deletes URLs: offtopic/duplicates get Rank Math 301 then status=draft.
Credentials stay in the environment.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from article_packets import (  # noqa: E402
    CITY_PAGES,
    CPT,
    EN_POSTS,
    HOME,
    NEW_POSTS,
    PAGES,
    PILLARS,
)
from wp_client import LOCKED_ID, WpClient  # noqa: E402

REPORTS = ROOT / "reports"
CSV_PATH = ROOT / "articles-actions-2026-10.csv"
LOCKED_SLUG = "water-leak-detection-company-in-qatar"
KEEP_FROM_REDIRECT = {
    "water-leak-detection-company-in-qatar",
    "water-leak-detection-qatar-en",
    "house-cleaning-in-qatar",
    "villa-cleaning-in-qatar",
    "apartment-cleaning-in-qatar",
    "shrkh-tnzyf-mdakhn-mtaam-fy-qtr",
    "shrkh-tnzyf-bad-altshtyb-fy-qtr",
    "shrkh-jly-rkham-fy-qtr",
    "shrkh-tlmya-syramyk-fy-qtr",
    "shrkh-tnzyf-wajhat-hjryh-fy-qtr",
    "cockroach-control-in-qatar",
    "shrkh-tslyk-mjary-fy-qtr",
    "services",
}
LEAK_DRAFT_HINT = re.compile(r"تسر[ي]?ب")
FAKE = re.compile(
    r"15\s*000|15 ألف|12 سنة|4\.9|10 سنوات|24/7|24 ساعة|971586634710|974"
)
# Fake-stat scanner should not flag the WhatsApp number in our packets.
FAKE_STATS = re.compile(r"15\s*000|15 ألف|12 سنة|تقييم\s*4\.9|ضمان\s*10|24/7")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def words(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    return len(re.findall(r"\S+", text))


def lock_check(wp: WpClient) -> dict:
    st, post = wp.get(f"/wp-json/wp/v2/posts/{LOCKED_ID}?context=edit")
    if st != 200:
        raise SystemExit(f"lock GET 2973 failed HTTP {st} {post}")
    raw = ((post.get("content") or {}).get("raw") or "")
    info = {
        "id": post.get("id"),
        "slug": post.get("slug"),
        "status": post.get("status"),
        "hash": sha(raw),
        "word_count": words(raw),
    }
    ok = info["id"] == LOCKED_ID and info["slug"] == LOCKED_SLUG
    if not ok:
        raise SystemExit(f"abort: post 2973 identity changed {info}")
    return info


def snippet5_guard(wp: WpClient) -> None:
    st, sn = wp.get("/wp-json/code-snippets/v1/snippets/5")
    if st != 200 or not isinstance(sn, dict):
        raise SystemExit(f"cannot read snippet 5: {st} {sn}")
    if "Rukn Qatar SEO and contact" not in (sn.get("name") or ""):
        raise SystemExit(f"snippet 5 name unexpected: {sn.get('name')}")
    if not sn.get("active"):
        raise SystemExit("snippet 5 is not active — abort")


def validate_html(html: str, *, allow_wa: bool = True) -> list[str]:
    errs = []
    if "tel:" in html.lower():
        errs.append("contains tel:")
    if re.search(r"(?<!\d)974(?!\d)", html):
        errs.append("contains 974")
    if FAKE_STATS.search(html):
        errs.append("possible fake stat")
    if allow_wa and "971586634710" not in html and "wa.me/" not in html:
        # pages like blog may only link internally
        pass
    if "[post_" in html:
        errs.append("contains post shortcode")
    return errs


def put_content(wp: WpClient, kind: str, item_id: int, html: str, extra: dict | None, apply: bool, log: list) -> None:
    route = {
        "post": f"/wp-json/wp/v2/posts/{item_id}",
        "page": f"/wp-json/wp/v2/pages/{item_id}",
        "services": f"/wp-json/wp/v2/services/{item_id}",
    }[kind]
    if item_id == LOCKED_ID:
        log.append({"id": item_id, "result": "BLOCKED_BY_SNIPPET5", "note": "refused before PUT"})
        return
    errs = validate_html(html)
    payload = {"content": html}
    if extra:
        payload.update(extra)
    entry = {
        "id": item_id,
        "kind": kind,
        "words": words(html),
        "apply": apply,
        "validate": errs or "ok",
    }
    if errs:
        entry["result"] = "VALIDATE_FAIL"
        log.append(entry)
        return
    if not apply:
        entry["result"] = "DRY_RUN"
        log.append(entry)
        return
    st, body = wp.put(route + "?context=edit", payload)
    entry["http"] = st
    if st in {200, 201}:
        got_id = body.get("id") if isinstance(body, dict) else None
        if got_id == LOCKED_ID:
            entry["result"] = "ABORT_LOCKED_ID"
        else:
            entry["result"] = "ok"
            entry["link"] = (body.get("link") if isinstance(body, dict) else None)
    else:
        entry["result"] = "HTTP_FAIL"
        entry["error"] = body if not isinstance(body, dict) else {
            k: body.get(k) for k in ("code", "message", "data")
        }
    log.append(entry)


def find_post_by_slug(wp: WpClient, slug: str) -> dict | None:
    st, rows = wp.get(f"/wp-json/wp/v2/posts?slug={slug}&status=any&context=edit&per_page=5")
    if st != 200 or not isinstance(rows, list) or not rows:
        return None
    return rows[0]


def create_or_update_new(wp: WpClient, packet: dict, apply: bool, log: list) -> None:
    html = packet["html"]
    errs = validate_html(html)
    entry = {"slug": packet["slug"], "title": packet["title"], "words": words(html), "apply": apply, "validate": errs or "ok"}
    if errs:
        entry["result"] = "VALIDATE_FAIL"
        log.append(entry)
        return
    existing = find_post_by_slug(wp, packet["slug"])
    if existing and existing.get("id") == LOCKED_ID:
        entry["result"] = "BLOCKED_BY_SNIPPET5"
        log.append(entry)
        return
    if not apply:
        entry["result"] = "DRY_RUN_CREATE" if not existing else f"DRY_RUN_UPDATE:{existing.get('id')}"
        log.append(entry)
        return
    payload = {
        "title": packet["title"],
        "content": html,
        "status": "publish",
        "slug": packet["slug"],
        "categories": [2457],
    }
    if existing:
        st, body = wp.put(f"/wp-json/wp/v2/posts/{existing['id']}", payload)
    else:
        st, body = wp.post("/wp-json/wp/v2/posts", payload)
    entry["http"] = st
    entry["id"] = body.get("id") if isinstance(body, dict) else None
    entry["link"] = body.get("link") if isinstance(body, dict) else None
    entry["result"] = "ok" if st in {200, 201} else "HTTP_FAIL"
    if st not in {200, 201}:
        entry["error"] = body
    log.append(entry)


def load_csv_rows() -> list[dict]:
    with CSV_PATH.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def offtopic_targets(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        if r.get("status") != "publish" or r.get("type") != "post":
            continue
        if r["action"] != "استبدال أو إلغاء نشر (مع 301)":
            continue
        pid = int(r["id"])
        if pid == LOCKED_ID:
            continue
        slug = r["slug"]
        if slug in KEEP_FROM_REDIRECT:
            continue
        out.append({"id": pid, "slug": slug, "title": r["title"], "url": r["url"]})
    return out


def duplicate_losers(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        if r.get("action") != "دمج وإعادة توجيه (301)":
            continue
        pid = int(r["id"])
        if pid == LOCKED_ID:
            continue
        m = re.search(r"الإبقاء على (\d+)", r.get("reasons") or "")
        keep_id = int(m.group(1)) if m else None
        keep_row = next((x for x in rows if x.get("id") == str(keep_id)), None) if keep_id else None
        dest = (keep_row or {}).get("url") or f"{HOME}/services/"
        out.append({"id": pid, "slug": r["slug"], "title": r["title"], "dest": dest, "keep": keep_id})
    return out


def add_redirect(wp: WpClient, slug: str, to: str, apply: bool) -> dict:
    if slug in KEEP_FROM_REDIRECT or slug == LOCKED_SLUG:
        return {"slug": slug, "result": "SKIP_KEEP"}
    if not apply:
        return {"slug": slug, "to": to, "result": "DRY_RUN"}
    st, body = wp.post("/wp-json/rukn-qa/v1/redirect", {"from": slug, "to": to})
    return {"slug": slug, "to": to, "http": st, "body": body, "result": "ok" if st in {200, 201} else "HTTP_FAIL"}


def draft_post(wp: WpClient, post_id: int, apply: bool) -> dict:
    if post_id == LOCKED_ID:
        return {"id": post_id, "result": "BLOCKED_BY_SNIPPET5"}
    if not apply:
        return {"id": post_id, "result": "DRY_RUN"}
    st, body = wp.put(f"/wp-json/wp/v2/posts/{post_id}", {"status": "draft"})
    return {"id": post_id, "http": st, "result": "ok" if st in {200, 201} else "HTTP_FAIL", "error": None if st in {200, 201} else body}


def public_get(url: str, timeout: int = 40) -> tuple[int, str]:
    import ssl
    import urllib.request

    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "RuknQA-ArticleWave/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, r.read().decode("utf-8", "replace")[:4000]
    except Exception as e:  # noqa: BLE001
        code = getattr(e, "code", None)
        return int(code or 0), str(e)[:300]


def verify_live(urls: list[str]) -> list[dict]:
    out = []
    for url in urls:
        st, body = public_get(url)
        flags = []
        if "tel:" in body.lower():
            flags.append("tel")
        if re.search(r"(?<!\d)974(?!\d)", body):
            flags.append("974")
        if "خدمة وطنية من ركن التطور" in body:
            flags.append("old_national_lead")
        if "[post_features]" in body or "[post_steps]" in body:
            flags.append("shortcode_visible")
        out.append({"url": url, "http": st, "flags": flags or "ok", "has_wa": "971586634710" in body or "wa.me/971586634710" in body})
        time.sleep(0.15)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--skip-redirects", action="store_true")
    parser.add_argument("--min-interval", type=float, default=0.25)
    args = parser.parse_args()
    apply = bool(args.apply)
    REPORTS.mkdir(parents=True, exist_ok=True)
    wp = WpClient(min_interval=args.min_interval)

    snippet5_guard(wp)
    lock_before = lock_check(wp)
    log: dict = {
        "started": datetime.now(timezone.utc).isoformat(),
        "apply": apply,
        "lock_before": lock_before,
        "pages": [],
        "city_pages": [],
        "pillars": [],
        "en": [],
        "cpt": [],
        "new_posts": [],
        "redirects": [],
        "drafts": [],
        "verify": [],
    }

    for pid, pkt in PAGES.items():
        put_content(wp, "page", pid, pkt["html"], None, apply, log["pages"])
    for pid, pkt in CITY_PAGES.items():
        put_content(wp, "page", pid, pkt["html"], None, apply, log["city_pages"])
    for pid, pkt in PILLARS.items():
        put_content(wp, "post", pid, pkt["html"], None, apply, log["pillars"])
    for pid, pkt in EN_POSTS.items():
        put_content(wp, "post", pid, pkt["html"], None, apply, log["en"])
    for pid, pkt in CPT.items():
        extra = {"status": pkt.get("status", "publish")}
        put_content(wp, "services", pid, pkt["html"], extra, apply, log["cpt"])
    for pkt in NEW_POSTS:
        create_or_update_new(wp, pkt, apply, log["new_posts"])

    rows = load_csv_rows()
    if not args.skip_redirects:
        dest_services = f"{HOME}/services/"
        for item in offtopic_targets(rows):
            red = add_redirect(wp, item["slug"], dest_services, apply)
            red["title"] = item["title"]
            log["redirects"].append(red)
            d = draft_post(wp, item["id"], apply)
            d["slug"] = item["slug"]
            d["reason"] = "offtopic"
            log["drafts"].append(d)
        for item in duplicate_losers(rows):
            if item["slug"] in KEEP_FROM_REDIRECT:
                log["redirects"].append({"slug": item["slug"], "result": "SKIP_KEEP"})
                continue
            red = add_redirect(wp, item["slug"], item["dest"], apply)
            red["title"] = item["title"]
            red["keep"] = item["keep"]
            log["redirects"].append(red)
            d = draft_post(wp, item["id"], apply)
            d["slug"] = item["slug"]
            d["reason"] = "duplicate"
            log["drafts"].append(d)

    if apply:
        try:
            wp.post("/wp-json/rukn-qa/v1/purge-cache", {})
        except Exception as e:  # noqa: BLE001
            log["purge_error"] = str(e)

    lock_after = lock_check(wp)
    log["lock_after"] = lock_after
    if lock_after["hash"] != lock_before["hash"]:
        log["lock_mismatch"] = True
        print("WARNING: post 2973 hash changed")
    else:
        log["lock_mismatch"] = False

    verify_urls = [
        f"{HOME}/services/",
        f"{HOME}/as3ar/",
        f"{HOME}/cities/",
        f"{HOME}/about/",
        f"{HOME}/faq/",
        f"{HOME}/blog/",
        f"{HOME}/shrkh-azl-asth-fy-qtr/",
        f"{HOME}/split-ac-maintenance-in-qatar/",
        f"{HOME}/house-cleaning-in-qatar/",
        f"{HOME}/pest-control-in-qatar/",
        f"{HOME}/en/water-leak-detection-qatar-en/",
        f"{HOME}/en/roof-insulation-qatar-en/",
        f"{HOME}/services/water-leak-detection/",
        f"{HOME}/services/sound-insulation-installation/",
        f"{HOME}/how-to-choose-home-services-company-qatar/",
        f"{HOME}/water-leak-detection-company-in-qatar/",
    ]
    log["verify"] = verify_live(verify_urls)
    log["finished"] = datetime.now(timezone.utc).isoformat()

    out = REPORTS / ("apply-live.json" if apply else "apply-dry-run.json")
    out.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

    def tally(items: list[dict]) -> dict:
        c: dict[str, int] = {}
        for i in items:
            c[i.get("result", "?")] = c.get(i.get("result", "?"), 0) + 1
        return c

    print("apply", apply)
    print("lock", lock_after["slug"], "hash", lock_after["hash"], "mismatch", log["lock_mismatch"])
    print("pages", tally(log["pages"]))
    print("city_pages", tally(log["city_pages"]))
    print("pillars", tally(log["pillars"]))
    print("en", tally(log["en"]))
    print("cpt", tally(log["cpt"]))
    print("new_posts", tally(log["new_posts"]))
    print("redirects", tally(log["redirects"]))
    print("drafts", tally(log["drafts"]))
    print("wrote", out)


if __name__ == "__main__":
    main()
