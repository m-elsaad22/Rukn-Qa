#!/usr/bin/env python3
"""Rewrite high-intent P2 nationals with unique copy. Never writes post 2973."""
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
from p2_unique_articles import ARTICLES, EXPECT_PTYPE, SLUGS, TITLES, payload_for

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorP2Cluster/1.0",
    "Content-Type": "application/json",
}
LOCKED = 2973
SITE = "https://www.rukn-eltatawer.com/qa"

UNIQUE_H2 = {
    10387: "الكويل والغلاف لا شحن فريون من أول رسالة",
    10388: "عداد الضغط بعد التسرب لا علبة فوق وسخ",
    10285: "المخارج والراجع قبل غسيل الجداري",
    10384: "عنصر وتيرموستات لا مكيف ولا شبكة البيت كلها",
    10380: "خزان وضغط متقطع لا ري حديقة افتراضي",
    10378: "منسوب البيارة وفتحة الوصول لا سيفون مطبخ",
    10338: "قماش المجلس والجفاف لا كنب غرف النوم",
    10345: "وسائد الكنب والبخار لا سجاد الممر",
    10344: "القطعة والغرفة والجفاف لا كنب ولا مجلس وسائد",
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
    st2, p2 = api(f"/wp/v2/posts/{LOCKED}?context=edit&_fields=content")
    raw = ((p2.get("content") or {}).get("raw") or "") if isinstance(p2, dict) else ""
    if "الحل النهائي 2026" not in raw or "لماذا أصبح البحث عن شركة كشف تسربات المياه في قطر" not in raw:
        raise SystemExit("Ranking post 2973 body marker missing — aborting")
    note("LOCK 2973 body markers present")


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
        ("شركة غسيل مكيفات في قطر", "shrkh-ghsyl-mkyfat-fy-qtr", "ac"),
        ("شركة تعبئة غاز مكيفات في قطر", "shrkh-tabyh-ghaz-mkyfat-fy-qtr", "ac"),
        ("شركة تنظيف وصيانة دكتات المكيفات في قطر", "ac-duct-cleaning-and-maintenance-in-qatar", "duct"),
        ("شركة صيانة سخانات مياه في قطر", "shrkh-syanh-skhanat-myah-fy-qtr", "plumbing"),
        ("شركة تركيب مضخات مياه في قطر", "shrkh-trkyb-mdkhat-myah-fy-qtr", "plumbing"),
        ("شركة شفط بيارات في قطر", "shrkh-shft-byarat-fy-qtr", "sewer"),
        ("شركة تنظيف مجالس في قطر", "shrkh-tnzyf-mjals-fy-qtr", "cleaning"),
        ("شركة تنظيف كنب في قطر", "shrkh-tnzyf-knb-fy-qtr", "cleaning"),
        ("شركة تنظيف سجاد وموكيت في قطر", "shrkh-tnzyf-sjad-wmwkyt-fy-qtr", "cleaning"),
        ("شركة كشف تسربات المياه في قطر", "water-leak-detection-company-in-qatar", "general"),
    ]
    for title, slug, expect in cases:
        got = classify(title, slug)
        note(f"classify {slug} -> {got} (expect {expect})")
        if got != expect:
            raise SystemExit(f"classifier mismatch {slug}: {got} != {expect}")


def jobs():
    out = []
    for pid, kind in ARTICLES.items():
        if pid == LOCKED:
            raise SystemExit("locked id in jobs")
        out.append(
            {
                "id": pid,
                "slug": SLUGS[pid],
                "title": TITLES[pid],
                "kind": kind,
                "canonical": f"{SITE}/{SLUGS[pid]}/",
                "expect": EXPECT_PTYPE[kind],
            }
        )
    seen = set()
    for job in out:
        if job["id"] in seen:
            raise SystemExit(f"duplicate job id {job['id']}")
        seen.add(job["id"])
    return out


def clear_keep_source_redirects(slugs):
    rows = []
    for slug in slugs:
        st, out = api("/rukn-qa/v1/redirects?q=" + slug)
        note(f"REDIRECTS {slug} http={st} rows={len(out.get('rows') or []) if isinstance(out, dict) else out}")
        st2, out2 = api("/rukn-qa/v1/redirect-delete", "POST", {"from": slug})
        note(f"DEL-SRC {slug} http={st2} {out2}")
        rows.append({"slug": slug, "list": out, "deleted": out2})
        time.sleep(0.05)
    return rows


def rewrite_one(job):
    pid = job["id"]
    if pid == LOCKED:
        raise SystemExit("refusing to touch 2973")
    payload = payload_for(pid, job["title"], job["slug"])
    if payload["words"] < 1100:
        raise SystemExit(f"{pid} only {payload['words']} words")
    if payload["ptype"] != job["expect"]:
        raise SystemExit(f"{pid} classified as {payload['ptype']} != {job['expect']}")
    marker = UNIQUE_H2[pid]
    if marker not in payload["html"]:
        raise SystemExit(f"{pid} missing unique H2 {marker!r}")
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
    note(f"REWRITE {pid} {job['slug']} http={st} words={payload['words']} pack={payload['ptype']}")
    if st not in (200, 201) or (isinstance(out, dict) and out.get("code") == "locked"):
        raise SystemExit(f"rewrite failed {pid}: {out}")
    rm_meta(
        pid,
        title=job["title"],
        description=payload["desc"],
        keyword=payload["keyword"],
        robots=["index", "follow"],
        canonical=job["canonical"],
    )
    return {
        "id": pid,
        "slug": job["slug"],
        "words": payload["words"],
        "kind": payload["kind"],
        "ptype": payload["ptype"],
        "http": st,
        "action": "rewrite",
        "marker": marker,
    }


def main():
    lockcheck()
    assert_classifier()
    lockcheck()
    todo = jobs()
    cleared = clear_keep_source_redirects([j["slug"] for j in todo])
    rewrites = []
    for job in todo:
        rewrites.append(rewrite_one(job))
        time.sleep(0.25)
        if len(rewrites) % 5 == 0:
            lockcheck()
    st, purged = api("/rukn-qa/v1/purge-cache", "POST", {})
    note(f"PURGE {st} {purged}")
    lockcheck()
    summary = {
        "rewrites": rewrites,
        "cleared_keep_redirects": cleared,
        "locked": 2973,
        "min_words": min(r["words"] for r in rewrites),
        "count": len(rewrites),
        "merges": [],
    }
    out = Path(__file__).resolve().parents[1] / "audit" / "p2-cluster-fix.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note(json.dumps({"min_words": summary["min_words"], "rewrites": len(rewrites)}, ensure_ascii=False))
    note("DONE fix_p2_cluster")


if __name__ == "__main__":
    main()
