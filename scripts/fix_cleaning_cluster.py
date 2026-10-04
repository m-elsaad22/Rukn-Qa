#!/usr/bin/env python3
"""Rewrite unique cleaning pillars and 301 duplicate URLs. Never writes post 2973."""
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

from cleaning_unique_articles import ARTICLES, payload_for
from kayan_article_builder import classify

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorCleaning/1.0",
    "Content-Type": "application/json",
}
LOCKED = 2973
SITE = "https://www.rukn-eltatawer.com/qa"

PILLARS = {
    10258: ("house-cleaning-in-qatar", "شركة تنظيف منازل في قطر"),
    10264: ("villa-cleaning-in-qatar", "شركة تنظيف فلل في قطر"),
    10267: ("apartment-cleaning-in-qatar", "شركة تنظيف شقق في قطر"),
    10349: ("shrkh-tnzyf-mdakhn-mtaam-fy-qtr", "شركة تنظيف مداخن مطاعم في قطر"),
    10350: ("shrkh-tnzyf-bad-altshtyb-fy-qtr", "شركة تنظيف بعد التشطيب في قطر"),
    10351: ("shrkh-jly-rkham-fy-qtr", "شركة جلي رخام في قطر"),
    10352: ("shrkh-tlmya-syramyk-fy-qtr", "شركة تلميع سيراميك في قطر"),
    10343: ("shrkh-tnzyf-wajhat-hjryh-fy-qtr", "شركة تنظيف واجهات حجرية في قطر"),
}

# Duplicate URLs → keep URL (path on /qa)
MERGES = {
    10334: ("shrkh-tnzyf-mnazl-fy-qtr-2", "/house-cleaning-in-qatar/"),
    10338: ("shrkh-tnzyf-mjals-fy-qtr", "/house-cleaning-in-qatar/"),
    10345: ("shrkh-tnzyf-knb-fy-qtr", "/house-cleaning-in-qatar/"),
    10346: ("shrkh-tnzyf-stayr-fy-qtr", "/house-cleaning-in-qatar/"),
    10347: ("shrkh-tnzyf-mratb-fy-qtr", "/house-cleaning-in-qatar/"),
    10344: ("shrkh-tnzyf-sjad-wmwkyt-fy-qtr", "/house-cleaning-in-qatar/"),
    10339: ("shrkh-tnzyf-khyam-wbywt-shar-fy-qtr", "/house-cleaning-in-qatar/"),
    10353: ("aamlat-tnzyf-balsaah-fy-qtr", "/house-cleaning-in-qatar/"),
    10337: ("shrkh-tnzyf-qswr-fy-qtr", "/villa-cleaning-in-qatar/"),
    10379: ("shrkh-tnzyf-ghrf-tftysh-fy-qtr", "/shrkh-tslyk-mjary-fy-qtr/"),
    10357: ("shrkh-mkafhh-srasyr-fy-qtr", "/cockroach-control-in-qatar/"),
    10368: ("shrkh-tkhzyn-athath-fy-qtr", "/services/"),
    10369: ("shrkh-tkhzyn-bdaya-fy-qtr", "/services/"),
}


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


def theme_fields(meta: dict) -> dict:
    out = {}
    for key, val in meta.items():
        out[key] = json.dumps(val, ensure_ascii=False) if isinstance(val, (dict, list)) else val
    return out


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


def push_snippet():
    snippet_path = Path(__file__).with_name("snippet-rukn-qatar.php")
    code = snippet_path.read_text(encoding="utf-8")
    if "rukn_qa_cluster_redirects" not in code or "rukn-hide-fake-social" not in code:
        raise SystemExit("snippet missing cleaning redirects or rating hide")
    if "2973" not in code:
        raise SystemExit("snippet missing ranking lock")
    st, sn = api("/code-snippets/v1/snippets/5")
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
    st, out = api("/code-snippets/v1/snippets/5", "PUT", payload, timeout=180)
    err = out.get("code_error") if isinstance(out, dict) else out
    note(f"snippet PUT {st} err={err!r} len={len(code)}")
    if st not in (200, 201) or (isinstance(out, dict) and out.get("code_error")):
        raise SystemExit("snippet update failed")


def assert_classifier():
    cases = [
        ("شركة تنظيف منازل في قطر", "shrkh-tnzyf-mnazl-fy-qtr-2", "cleaning"),
        ("شركة تنظيف منازل في قطر", "house-cleaning-in-qatar", "cleaning"),
        ("شركة تنظيف مداخن مطاعم في قطر", "shrkh-tnzyf-mdakhn-mtaam-fy-qtr", "chimney"),
        ("شركة جلي رخام في قطر", "shrkh-jly-rkham-fy-qtr", "marble"),
        ("شركة تلميع سيراميك في قطر", "shrkh-tlmya-syramyk-fy-qtr", "ceramic"),
        ("شركة تنظيف بعد التشطيب في قطر", "shrkh-tnzyf-bad-altshtyb-fy-qtr", "postcon"),
        ("شركة تنظيف واجهات حجرية في قطر", "shrkh-tnzyf-wajhat-hjryh-fy-qtr", "facade"),
        ("شركة تنظيف غرف تفتيش في قطر", "shrkh-tnzyf-ghrf-tftysh-fy-qtr", "chamber"),
    ]
    for title, slug, expect in cases:
        got = classify(title, slug)
        note(f"classify {slug} -> {got} (expect {expect})")
        if got != expect:
            raise SystemExit(f"classifier mismatch {slug}: {got} != {expect}")


def rewrite_pillars():
    rows = []
    for pid, (slug, title) in PILLARS.items():
        if pid == LOCKED:
            raise SystemExit("refusing to touch 2973")
        payload = payload_for(pid, title, slug)
        if payload["words"] < 1100:
            raise SystemExit(f"{pid} only {payload['words']} words")
        if payload["kind"] == "chimney" and payload["ptype"] != "chimney":
            raise SystemExit(f"chimney classified as {payload['ptype']}")
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


KEEP_SLUGS = [
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
]


def clear_keep_source_redirects():
    rows = []
    for slug in KEEP_SLUGS:
        st, out = api("/rukn-qa/v1/redirects?q=" + slug)
        note(f"REDIRECTS {slug} http={st} rows={len(out.get('rows') or []) if isinstance(out, dict) else out}")
        st2, out2 = api("/rukn-qa/v1/redirect-delete", "POST", {"from": slug})
        note(f"DEL-SRC {slug} http={st2} {out2}")
        rows.append({"slug": slug, "list": out, "deleted": out2})
    return rows


def merge_clones():
    rows = []
    for pid, (slug, dest) in MERGES.items():
        if pid == LOCKED or dest.rstrip("/") == "/water-leak-detection-company-in-qatar":
            raise SystemExit("refusing merge that touches leak ranking URL")
        target = SITE + dest
        st, out = api(f"/wp/v2/posts/{pid}", "POST", {"status": "draft"})
        note(f"DRAFT {pid} {slug} http={st} -> {dest}")
        if st not in (200, 201):
            raise SystemExit(f"draft failed {pid}: {out}")
        rm_meta(pid, robots=["noindex", "nofollow"], canonical=target)
        rst, rout = api("/rukn-qa/v1/redirect", "POST", {"from": slug, "to": target})
        note(f"REDIRECT {slug} -> {target} http={rst}")
        rows.append(
            {
                "id": pid,
                "slug": slug,
                "to": dest,
                "draft_http": st,
                "redirect_http": rst,
                "action": "draft-301",
            }
        )
        time.sleep(0.05)
    return rows


def main():
    lockcheck()
    assert_classifier()
    push_snippet()
    lockcheck()
    cleared = clear_keep_source_redirects()
    rewrites = rewrite_pillars()
    merges = merge_clones()
    st, purged = api("/rukn-qa/v1/purge-cache", "POST", {})
    note(f"PURGE {st} {purged}")
    lockcheck()
    summary = {
        "rewrites": rewrites,
        "merges": merges,
        "cleared_keep_redirects": cleared,
        "locked": 2973,
        "min_words": min(r["words"] for r in rewrites),
    }
    out = Path(__file__).resolve().parents[1] / "audit" / "cleaning-cluster-fix.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note(json.dumps({"min_words": summary["min_words"], "rewrites": len(rewrites), "merges": len(merges)}, ensure_ascii=False))
    note("DONE fix_cleaning_cluster")


if __name__ == "__main__":
    main()
