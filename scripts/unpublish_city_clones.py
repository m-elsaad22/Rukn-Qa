#!/usr/bin/env python3
"""Draft city×service clones and leak-city clones. Never writes post 2973."""
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
    "User-Agent": "Mozilla/5.0 CursorUnpublish/1.0",
    "Content-Type": "application/json",
}
LOCKED = 2973
LEAK_URL = "https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/"
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


def api(path, method="GET", data=None, timeout=180):
    url = path if path.startswith("http") else BASE + path
    body = None if data is None else json.dumps(data).encode()
    last_err = None
    for attempt in range(5):
        req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
                raw = r.read().decode() or "null"
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    parsed = raw
                return r.status, parsed, {k.lower(): v for k, v in r.headers.items()}
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors="replace")
            try:
                return e.code, json.loads(raw), {}
            except Exception:
                return e.code, raw[:400], {}
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise last_err


def note(msg):
    print(msg, flush=True)


def lockcheck():
    code, p, _ = api(f"/wp/v2/posts/{LOCKED}?context=edit&_fields=id,slug,status,title")
    title = unescape((p.get("title") or {}).get("raw") or "")
    ok = (
        code == 200
        and p.get("id") == LOCKED
        and p.get("slug") == "water-leak-detection-company-in-qatar"
        and p.get("status") == "publish"
        and title == "شركة كشف تسربات المياه في قطر"
    )
    note(f"LOCK 2973 {ok} title={title!r}")
    if not ok:
        raise SystemExit("abort: ranking post changed")


def get_all(status, fields="id,slug,status,title"):
    items = []
    page = 1
    while True:
        code, data, meta = api(
            f"/wp/v2/posts?per_page=100&page={page}&status={status}&context=edit&_fields={fields}"
        )
        if code != 200 or not data:
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


def is_city_template(p) -> bool:
    slug = p.get("slug") or ""
    title = title_of(p)
    if int(p["id"]) == LOCKED or slug in KEEP_SLUGS:
        return False
    if any(slug.endswith(s) for s in CITY_SUF):
        return True
    return any(c in title for c in CITY_AR)


def is_leak_clone(p) -> bool:
    slug = p.get("slug") or ""
    if int(p["id"]) == LOCKED or slug in KEEP_SLUGS:
        return False
    return slug.startswith("water-leak-detection-") or slug.startswith("water-pipe-leak-detection-")


def update_snippet():
    snippet_path = Path(__file__).with_name("snippet-rukn-qatar.php")
    code = snippet_path.read_text(encoding="utf-8")
    if "rukn_is_city_template" not in code or "2973" not in code:
        raise SystemExit("snippet missing city-template guard or ranking lock")
    st, sn, _ = api("/code-snippets/v1/snippets/5")
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
    st, out, _ = api("/code-snippets/v1/snippets/5", "PUT", payload, timeout=180)
    err = out.get("code_error") if isinstance(out, dict) else out
    note(f"snippet PUT {st} err={err!r} len={len(code)}")
    if st not in (200, 201) or (isinstance(out, dict) and out.get("code_error")):
        raise SystemExit("snippet update failed")


def rm_meta(post_id, **kwargs):
    if int(post_id) == LOCKED:
        note(f"SKIP locked SEO {post_id}")
        return
    meta = {}
    if kwargs.get("robots"):
        meta["rank_math_robots"] = kwargs["robots"]
    if kwargs.get("canonical"):
        meta["rank_math_canonical_url"] = kwargs["canonical"]
    if not meta:
        return
    api(
        "/rankmath/v1/updateMeta",
        "POST",
        {"objectType": "post", "objectID": int(post_id), "meta": meta},
    )


def main():
    lockcheck()
    update_snippet()
    lockcheck()

    st, result, _ = api("/rukn-qa/v1/unpublish-city-templates", "POST", {}, timeout=180)
    note(f"bulk unpublish {st} {result}")
    if st != 200:
        st2, result2, _ = api("/rukn-qa/v1/draft-city-templates", "POST", {}, timeout=180)
        note(f"fallback draft-city-templates {st2} {result2}")

    pubs = get_all("publish")
    leftovers = [p for p in pubs if is_city_template(p) or is_leak_clone(p)]
    note(f"published leftover clones={len(leftovers)} publish_total={len(pubs)}")
    n = 0
    for p in leftovers:
        pid = int(p["id"])
        if pid == LOCKED:
            continue
        slug = p.get("slug") or ""
        st, _, _ = api(f"/wp/v2/posts/{pid}", "POST", {"status": "draft"})
        meta = {"robots": ["noindex", "nofollow"]}
        if is_leak_clone(p):
            meta["canonical"] = LEAK_URL
            api("/rukn-qa/v1/redirect", "POST", {"from": slug, "to": LEAK_URL})
        rm_meta(pid, **meta)
        n += 1
        if n % 50 == 0:
            note(f"drafted leftover {n}/{len(leftovers)} last={pid} {st}")
        time.sleep(0.03)
    note(f"leftover drafted {n}")
    lockcheck()

    pubs2 = get_all("publish")
    drafts = get_all("draft")
    leftover2 = [p for p in pubs2 if is_city_template(p) or is_leak_clone(p)]
    keep_ok = [p for p in pubs2 if (p.get("slug") or "") in KEEP_SLUGS or int(p["id"]) == LOCKED]
    summary = {
        "publish": len(pubs2),
        "draft": len(drafts),
        "published_clones_left": [
            {"id": p["id"], "slug": p.get("slug")} for p in leftover2
        ],
        "keep_published": [
            {"id": p["id"], "slug": p.get("slug")} for p in keep_ok
        ],
        "locked_ok": any(int(p["id"]) == LOCKED for p in pubs2),
    }
    out = Path(__file__).resolve().parents[1] / "audit" / "unpublish-city-clones.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note(json.dumps(summary, ensure_ascii=False, indent=2))
    note("DONE unpublish_city_clones")


if __name__ == "__main__":
    main()
