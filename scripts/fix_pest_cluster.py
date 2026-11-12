#!/usr/bin/env python3
"""Rewrite unique national pest pillars. Never writes post 2973."""
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

from kayan_article_builder import classify
from pest_unique_articles import ARTICLES, EXPECT_PTYPE, SLUGS, TITLES, payload_for

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorPest/1.0",
    "Content-Type": "application/json",
}
LOCKED = 2973
SITE = "https://www.rukn-eltatawer.com/qa"

PILLARS = {pid: (SLUGS[pid], TITLES[pid]) for pid in ARTICLES}


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


def rm_meta(pid, **kwargs):
    if int(pid) == LOCKED:
        note(f"SKIP locked SEO {pid}")
        return
    meta = {}
    if kwargs.get("title"):
        meta["rank_math_title"] = f"{kwargs['title']} | ركن التطور قطر"
    if kwargs.get("description"):
        meta["rank_math_description"] = kwargs["description"]
    if kwargs.get("keyword"):
        meta["rank_math_focus_keyword"] = kwargs["keyword"]
    if kwargs.get("robots"):
        meta["rank_math_robots"] = kwargs["robots"]
    if kwargs.get("canonical"):
        meta["rank_math_canonical_url"] = kwargs["canonical"]
    if not meta:
        return
    return api(
        "/rankmath/v1/updateMeta",
        "POST",
        {"objectType": "post", "objectID": int(pid), "meta": meta},
    )


def assert_classifier():
    cases = [
        ("شركة مكافحة حشرات في قطر", "pest-control-in-qatar", "pest"),
        ("شركة مكافحة الصراصير في قطر", "cockroach-control-in-qatar", "pest_cockroach"),
        ("شركة مكافحة النمل الأبيض في قطر", "termite-control-in-qatar", "pest_termite"),
        ("شركة مكافحة بق الفراش في قطر", "bed-bug-control-in-qatar", "pest_bedbug"),
        ("شركة مكافحة فئران وقوارض في قطر", "shrkh-mkafhh-fyran-wqward-fy-qtr", "pest_rodent"),
        ("شركة مكافحة عقارب وثعابين في قطر", "shrkh-mkafhh-aqarb-wthaabyn-fy-qtr", "pest_scorpion"),
        ("شركة مكافحة حشرات زراعية في قطر", "shrkh-mkafhh-hshrat-zraayh-fy-qtr", "pest_agri"),
        ("شركة مكافحة الصراصير في الدوحة", "cockroach-control-doha", "pest_cockroach"),
        ("شركة مكافحة النمل الأبيض (الرمة) في الريان", "termite-control-al-rayyan", "pest_termite"),
        ("شركة تنظيف منازل في قطر", "house-cleaning-in-qatar", "cleaning"),
        ("شركة عزل أسطح في قطر", "shrkh-azl-asth-fy-qtr", "insul_roof"),
        ("شركة كشف تسربات المياه في قطر", "water-leak-detection-company-in-qatar", "general"),
    ]
    for title, slug, expect in cases:
        got = classify(title, slug)
        note(f"classify {slug} -> {got} (expect {expect})")
        if got != expect:
            raise SystemExit(f"classifier mismatch {slug}: {got} != {expect}")


KEEP_SLUGS = list(SLUGS.values())


def clear_keep_source_redirects():
    rows = []
    for slug in KEEP_SLUGS:
        st, out = api("/rukn-qa/v1/redirects?q=" + slug)
        note(f"REDIRECTS {slug} http={st} rows={len(out.get('rows') or []) if isinstance(out, dict) else out}")
        st2, out2 = api("/rukn-qa/v1/redirect-delete", "POST", {"from": slug})
        note(f"DEL-SRC {slug} http={st2} {out2}")
        rows.append({"slug": slug, "list": out, "deleted": out2})
    return rows


def rewrite_pillars():
    rows = []
    for pid, (slug, title) in PILLARS.items():
        if pid == LOCKED:
            raise SystemExit("refusing to touch 2973")
        payload = payload_for(pid, title, slug)
        if payload["words"] < 1100:
            raise SystemExit(f"{pid} only {payload['words']} words")
        expect = EXPECT_PTYPE[payload["kind"]]
        if payload["ptype"] != expect:
            raise SystemExit(f"{pid} classified as {payload['ptype']} != {expect}")
        st, out = api(
            "/rukn-qa/v1/post-blocks",
            "POST",
            {
                "id": pid,
                "content": payload["html"],
                "excerpt": payload["excerpt"],
                "meta": payload.get("meta") or {},
            },
        )
        note(f"REWRITE {pid} {slug} http={st} words={payload['words']} pack={payload['ptype']}")
        if st not in (200, 201) or (isinstance(out, dict) and out.get("code") == "locked"):
            raise SystemExit(f"rewrite failed {pid}: {out}")
        rm_meta(
            pid,
            title=title,
            description=payload["desc"],
            keyword=payload["keyword"],
            robots=["index", "follow"],
            canonical=f"{SITE}/{slug}/",
        )
        rows.append(
            {
                "id": pid,
                "slug": slug,
                "words": payload["words"],
                "kind": payload["kind"],
                "ptype": payload["ptype"],
                "http": st,
                "action": "rewrite",
            }
        )
        time.sleep(0.08)
    return rows


def main():
    lockcheck()
    assert_classifier()
    lockcheck()
    cleared = clear_keep_source_redirects()
    rewrites = rewrite_pillars()
    st, purged = api("/rukn-qa/v1/purge-cache", "POST", {})
    note(f"PURGE {st} {purged}")
    lockcheck()
    summary = {
        "rewrites": rewrites,
        "cleared_keep_redirects": cleared,
        "locked": 2973,
        "min_words": min(r["words"] for r in rewrites),
        "merges": [{"id": 10357, "note": "already 301 to /cockroach-control-in-qatar/ from cleaning cluster"}],
    }
    out = Path(__file__).resolve().parents[1] / "audit" / "pest-cluster-fix.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note(json.dumps({"min_words": summary["min_words"], "rewrites": len(rewrites)}, ensure_ascii=False))
    note("DONE fix_pest_cluster")


if __name__ == "__main__":
    main()
