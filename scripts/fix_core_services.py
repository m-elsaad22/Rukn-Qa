#!/usr/bin/env python3
"""Rewrite incomplete national service pillars. Never writes post 2973."""
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

from cleaning_unique_articles import payload_for as cleaning_payload
from insulation_unique_articles import payload_for as insulation_payload
from kayan_article_builder import classify
from core_service_unique_articles import (
    ARTICLES,
    EXPECT_PTYPE,
    SLUGS,
    TITLES,
    payload_for,
)

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorCoreServices/1.0",
    "Content-Type": "application/json",
}
LOCKED = 2973
SITE = "https://www.rukn-eltatawer.com/qa"

RESTORE = [
    {
        "id": 10258,
        "slug": "house-cleaning-in-qatar",
        "title": "شركة تنظيف منازل في قطر",
        "source": "cleaning",
        "canonical": f"{SITE}/house-cleaning-in-qatar/",
        "expect": "cleaning",
    },
    {
        "id": 10324,
        "slug": "shrkh-azl-asth-fy-qtr",
        "title": "شركة عزل أسطح في قطر",
        "source": "insulation",
        "canonical": f"{SITE}/shrkh-azl-asth-fy-qtr/",
        "expect": "insul_roof",
    },
    {
        "id": 12867,
        "slug": "roof-insulation-qatar-en",
        "title": "Roof insulation in Qatar",
        "source": "insulation",
        "canonical": f"{SITE}/en/roof-insulation-qatar-en/",
        "expect": "insul_roof",
    },
]


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
        ("شركة صيانة مكيفات سبليت في قطر", "split-ac-maintenance-in-qatar", "ac"),
        ("شركة صيانة تكييف مركزي في قطر", "central-air-conditioning-maintenance-in-qatar", "ac"),
        ("صيانة التكييف قبل صيف قطر", "ac-maintenance-before-summer-qatar", "ac"),
        ("شركة صيانة سباكة في قطر", "plumbing-maintenance-in-qatar", "plumbing"),
        ("سباك منازل في قطر", "home-plumber-in-qatar", "plumbing"),
        ("شركة تسليك مجاري في قطر", "shrkh-tslyk-mjary-fy-qtr", "sewer"),
        ("شركة تنسيق حدائق في قطر", "shrkh-tnsyq-hdayq-fy-qtr", "garden"),
        ("شركة صيانة مباني في قطر", "shrkh-syanh-mbany-fy-qtr", "build"),
        ("شركة صيانة عامة في قطر", "shrkh-syanh-aamh-fy-qtr", "build"),
        ("شركة دهانات داخلية في قطر", "shrkh-dhanat-dakhlyh-fy-qtr", "paint"),
        ("شركة تركيب طاقة شمسية في قطر", "shrkh-trkyb-taqh-shmsyh-fy-qtr", "solar"),
        ("شركة صيانة كهرباء في قطر", "shrkh-syanh-khrba-fy-qtr", "elec"),
        ("شركة تنظيف منازل في قطر", "shrkh-tnzyf-mnazl-fy-qtr-2", "cleaning"),
        ("شركة مكافحة صراصير في قطر", "shrkh-mkafhh-srasyr-fy-qtr", "pest_cockroach"),
        ("AC maintenance in Doha and Qatar", "ac-maintenance-qatar-en", "ac"),
        ("Water leak detection in Qatar without breaking", "water-leak-detection-qatar-en", "general"),
        ("شركة تنظيف منازل في قطر", "house-cleaning-in-qatar", "cleaning"),
        ("شركة عزل أسطح في قطر", "shrkh-azl-asth-fy-qtr", "insul_roof"),
        ("Roof insulation in Qatar", "roof-insulation-qatar-en", "insul_roof"),
        ("شركة كشف تسربات المياه في قطر", "water-leak-detection-company-in-qatar", "general"),
    ]
    for title, slug, expect in cases:
        got = classify(title, slug)
        note(f"classify {slug} -> {got} (expect {expect})")
        if got != expect:
            raise SystemExit(f"classifier mismatch {slug}: {got} != {expect}")


def payload_job(job):
    pid, title, slug = job["id"], job["title"], job["slug"]
    if job["source"] == "cleaning":
        payload = cleaning_payload(pid, title, slug)
    elif job["source"] == "insulation":
        payload = insulation_payload(pid, title, slug)
    else:
        payload = payload_for(pid, title, slug)
    return payload


def rewrite_one(job):
    pid = job["id"]
    if pid == LOCKED:
        raise SystemExit("refusing to touch 2973")
    payload = payload_job(job)
    if payload["words"] < 1100:
        raise SystemExit(f"{pid} only {payload['words']} words")
    if payload["ptype"] != job["expect"]:
        raise SystemExit(f"{pid} classified as {payload['ptype']} != {job['expect']}")
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
        "source": job["source"],
    }


def jobs():
    out = list(RESTORE)
    for pid, kind in ARTICLES.items():
        slug = SLUGS[pid]
        title = TITLES[pid]
        en = kind in ("ac_en", "leak_en")
        out.append(
            {
                "id": pid,
                "slug": slug,
                "title": title,
                "source": "core",
                "canonical": f"{SITE}/en/{slug}/" if en else f"{SITE}/{slug}/",
                "expect": EXPECT_PTYPE[kind],
            }
        )
    seen = set()
    unique = []
    for job in out:
        if job["id"] in seen:
            raise SystemExit(f"duplicate job id {job['id']}")
        seen.add(job["id"])
        unique.append(job)
    if LOCKED in seen:
        raise SystemExit("locked id in jobs")
    return unique


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
    out = Path(__file__).resolve().parents[1] / "audit" / "core-services-fix.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note(json.dumps({"min_words": summary["min_words"], "rewrites": len(rewrites)}, ensure_ascii=False))
    note("DONE fix_core_services")


if __name__ == "__main__":
    main()
