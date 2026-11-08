#!/usr/bin/env python3
"""Priority audit: service mismatch, generic template, short copy. Never writes 2973."""
from __future__ import annotations

import json
import os
import re
import ssl
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from html import unescape
from pathlib import Path

from kayan_article_builder import classify, service_core

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = __import__("base64").b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {"Authorization": f"Basic {AUTH}", "User-Agent": "Mozilla/5.0 CursorPriorityAudit/1.0"}
LOCKED = 2973
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
H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")
SHORT_RE = re.compile(r"\[[^\]]+\]")

# Words that MUST appear for the classified service (body, not title).
MUST = {
    "chimney": ["شفاط", "دهون", "عادم"],
    "chamber": ["تفتيش", "غطاء"],
    "marble": ["رخام", "جلي"],
    "ceramic": ["سيراميك"],
    "postcon": ["تشطيب"],
    "facade": ["واجهة", "واجهات"],
    "poolclean": ["مسبح", "طحالب"],
    "tankclean": ["خزان"],
    "duct": ["دكت"],
    "elevator": ["مصعد"],
    "solar": ["ألواح", "شمسية"],
    "trees": ["أشجار", "تقليم"],
    "birds": ["حمام", "طيور"],
    "insul_roof": ["سطح", "أسطح"],
    "insul_tank": ["خزان"],
    "insul_bath": ["حمام"],
    "insul_kitchen": ["مطبخ"],
    "insul_foam": ["فوم"],
    "insul_sound": ["صوت"],
    "insul_thermal": ["حرار"],
    "insul_water": ["مائي", "ماء"],
    "ac": ["تكييف", "مكيف"],
    "sewer": ["مجاري", "بيارة", "تسليك"],
    "plumbing": ["سباك", "ليّ", "سخان", "مضخة"],
    "pest_cockroach": ["صراصير", "مطبخ"],
    "pest_termite": ["خشب", "رمّة", "رمة", "نمل أبيض"],
    "pest_bedbug": ["بق", "سرير"],
    "pest_rodent": ["فئران", "قوارض"],
    "pest_scorpion": ["عقرب", "حوش"],
    "pest_agri": ["نخيل", "نبات", "شجرة"],
    "pest": ["حشرات"],
    "cleaning": ["تنظيف"],
    "garden": ["حديق", "عشب", "نخيل"],
    "paint": ["دهان", "جبس"],
    "move": ["نقل", "تغليف", "عفش", "أثاث"],
    "leak_water": ["تسرب", "رطوبة"],
    "leak_pipe": ["ماسورة", "مواسير", "ليّ"],
    "gasleak": ["غاز"],
    "acleak": ["تكييف", "فريون"],
    "poolleak": ["مسبح"],
}

# Foreign-service words that indicate the WRONG topic.
WRONG = {
    "chimney": ["غرف النوم", "كنس المنزل", "غبار المجالس"],
    "marble": ["شفاط مطعم", "دهون العادم"],
    "ceramic": ["شفاط مطعم"],
    "pest_termite": ["صراصير المطبخ", "بق الفراش"],
    "pest_bedbug": ["صراصير المطبخ", "رمّة الخشب"],
    "pest_cockroach": ["بق الفراش على المرتبة", "رمّة الباب"],
    "insul_sound": ["رش فوم سطح", "غمر الأسطح"],
    "insul_foam": ["عزل صوتي استوديو"],
    "move": ["شراء مستعمل", "سكراب"],
    "cleaning": ["شفاط مطعم", "فلاتر دهون"],
}

KAYAN_HERO = "تشخيص ثم تنفيذ مكتوب"
CITY_HERO = "نطاق مكتوب بعد فهم المبنى"
UNIQUE_MARKERS = (
    "المسار تحت الحوض",
    "فحص الخشب أولاً",
    "المأوى درز السرير",
    "ميل وصرف",
    "بيت مسكون",
    "لا رش عام بلا معرفة",
)


def api(path, timeout=90):
    url = path if path.startswith("http") else BASE + path
    last = None
    for attempt in range(5):
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
                raw = r.read().decode() or "null"
                meta = {k.lower(): v for k, v in r.headers.items()}
                return json.loads(raw), meta
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise last


def note(msg):
    print(msg, flush=True)


def list_published():
    items, page = [], 1
    while True:
        data, meta = api(
            f"/wp/v2/posts?per_page=100&page={page}&status=publish&context=edit&_fields=id,slug,title"
        )
        if not data:
            break
        items.extend(data)
        pages = int(meta.get("x-wp-totalpages", 1) or 1)
        note(f"list page {page}/{pages} n={len(items)}")
        if page >= pages:
            break
        page += 1
        time.sleep(0.03)
    return items


def is_city(slug: str) -> bool:
    s = slug or ""
    if s.startswith("services-in-"):
        return True
    return any(s.endswith(x) for x in CITY_SUF)


def is_leak_city(slug: str) -> bool:
    s = slug or ""
    if s in ("water-leak-detection-company-in-qatar", "water-leak-detection-qatar-en"):
        return False
    return s.startswith("water-leak-detection-") or s.startswith("water-pipe-leak-detection-")


def title_of(p):
    t = p.get("title") or {}
    return unescape(t.get("raw") or t.get("rendered") or "")


def fetch_content(ids):
    out = {}
    for i, pid in enumerate(ids):
        if pid == LOCKED:
            continue
        data, _ = api(f"/wp/v2/posts/{pid}?context=edit&_fields=id,slug,title,content,status")
        html = ((data.get("content") or {}).get("raw") or (data.get("content") or {}).get("rendered") or "")
        out[pid] = html
        if (i + 1) % 40 == 0:
            note(f"content {i+1}/{len(ids)}")
        time.sleep(0.04)
    return out


def text_of(html: str) -> str:
    t = unescape(html or "")
    t = SHORT_RE.sub(" ", t)
    t = TAG_RE.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()


def h2s(html: str):
    out = []
    for m in H2_RE.findall(html or ""):
        out.append(re.sub(r"\s+", " ", TAG_RE.sub("", unescape(m))).strip())
    return out


def analyze(pid, slug, title, html):
    ptype = classify(title, slug)
    text = text_of(html)
    wc = len([w for w in text.split() if w])
    hs = h2s(html)
    hero = hs[0] if hs else ""
    form = "other"
    if pid == LOCKED:
        form = "locked"
    elif KAYAN_HERO in (html or "") or (hero.endswith("تشخيص ثم تنفيذ مكتوب")):
        form = "kayan-generic"
    elif CITY_HERO in (html or "") or "نطاق مكتوب بعد فهم المبنى" in hero:
        form = "city-template"
    elif any(m in (html or "") for m in UNIQUE_MARKERS):
        form = "unique-cluster"
    elif "rukn-article" in (html or "") and len(hs) >= 10:
        form = "longform-shared"
    issues = []
    if wc < 700:
        issues.append("قصير جداً")
    elif wc < 1000:
        issues.append("أقل من 1000")
    must = MUST.get(ptype) or []
    if must and ptype not in ("general",) and pid != LOCKED:
        if not any(m in text for m in must):
            issues.append("نص بلا كلمات الخدمة")
    for bad in WRONG.get(ptype) or []:
        if bad in text:
            issues.append(f"خلط خدمة: {bad}")
    core = service_core(title)
    if core and len(core) > 5 and pid != LOCKED and core not in text and core not in title:
        issues.append("عنوان الخدمة غائب عن النص")
    if form == "kayan-generic" and not is_city(slug):
        issues.append("قالب كيان عام")
    if slug.startswith("shra-") or slug == "recruitment-in-qatar":
        if "تشخيص ثم تنفيذ" in (html or "") and "لا نشتري" not in text and "ليست مكتب" not in text:
            issues.append("نشاط خارج العمل بصيغة خدمة")
    if "لا نشتري" in text or "ليست مكتب استقدام" in text:
        form = "honest-out-of-scope"
    return {
        "id": pid,
        "slug": slug,
        "title": title,
        "ptype": ptype,
        "words": wc,
        "h2": len(hs),
        "hero": hero[:80],
        "form": form,
        "issues": issues,
        "link": f"https://www.rukn-eltatawer.com/qa/{slug}/",
    }


def main():
    posts = list_published()
    rows_meta = []
    for p in posts:
        pid = int(p["id"])
        slug = p.get("slug") or ""
        title = title_of(p)
        if pid == LOCKED:
            kind = "locked"
        elif is_leak_city(slug):
            kind = "leak-city"
        elif is_city(slug):
            kind = "city"
        elif slug.endswith("-en") or slug.endswith("-qatar-en"):
            kind = "english"
        else:
            kind = "national"
        rows_meta.append({"id": pid, "slug": slug, "title": title, "kind": kind, "ptype": classify(title, slug)})

    kinds = Counter(r["kind"] for r in rows_meta)
    ptypes_nat = Counter(r["ptype"] for r in rows_meta if r["kind"] == "national")
    note(f"published {len(rows_meta)} kinds={dict(kinds)}")

    nationals = [r for r in rows_meta if r["kind"] in ("national", "english", "leak-city")]
    note(f"fetching content for {len(nationals)} national/en/leak-city")
    htmls = fetch_content([r["id"] for r in nationals])

    analyzed = []
    for r in nationals:
        html = htmls.get(r["id"], "")
        analyzed.append(analyze(r["id"], r["slug"], r["title"], html))

    # sample city pages: one per ptype
    city = [r for r in rows_meta if r["kind"] == "city"]
    seen_pt = set()
    city_sample_ids = []
    for r in city:
        if r["ptype"] in seen_pt:
            continue
        seen_pt.add(r["ptype"])
        city_sample_ids.append(r["id"])
    note(f"city sample ptypes {len(city_sample_ids)}")
    city_html = fetch_content(city_sample_ids)
    city_analyzed = []
    id_city = {r["id"]: r for r in city}
    for pid in city_sample_ids:
        r = id_city[pid]
        city_analyzed.append(analyze(pid, r["slug"], r["title"], city_html.get(pid, "")))

    generic = [a for a in analyzed if a["form"] == "kayan-generic"]
    unique = [a for a in analyzed if a["form"] == "unique-cluster"]
    short = [a for a in analyzed if a["words"] < 1000]
    mismatch = [a for a in analyzed if any("خلط" in i or "بلا كلمات" in i for i in a["issues"])]
    out_of = [a for a in analyzed if a["form"] == "honest-out-of-scope" or any("خارج" in i for i in a["issues"])]
    leak_city = [a for a in analyzed if a["slug"].startswith("water-leak") or a["slug"].startswith("water-pipe")]

    # priority: national kayan-generic for real services (not out-of-scope)
    p1 = [a for a in generic if a["ptype"] not in ("general",) and a["id"] != LOCKED]
    p1.sort(key=lambda a: (0 if a["ptype"] in ("ac", "sewer", "plumbing", "garden", "paint", "build", "elec", "appliance", "outdoor", "move") else 1, a["words"]))

    summary = {
        "published": len(rows_meta),
        "kinds": dict(kinds),
        "national_ptypes": dict(ptypes_nat),
        "national_forms": dict(Counter(a["form"] for a in analyzed)),
        "city_sample_forms": dict(Counter(a["form"] for a in city_analyzed)),
        "short_national": [{"id": a["id"], "slug": a["slug"], "title": a["title"], "words": a["words"], "form": a["form"], "ptype": a["ptype"]} for a in sorted(short, key=lambda x: x["words"])],
        "mismatches": [{"id": a["id"], "slug": a["slug"], "title": a["title"], "ptype": a["ptype"], "issues": a["issues"], "hero": a["hero"], "words": a["words"]} for a in mismatch],
        "kayan_generic_national": [
            {"id": a["id"], "slug": a["slug"], "title": a["title"], "ptype": a["ptype"], "words": a["words"], "hero": a["hero"]}
            for a in p1
        ],
        "unique_cluster": [{"id": a["id"], "slug": a["slug"], "ptype": a["ptype"], "words": a["words"]} for a in unique],
        "out_of_scope": [{"id": a["id"], "slug": a["slug"], "title": a["title"], "form": a["form"], "issues": a["issues"]} for a in out_of],
        "leak_city": [{"id": a["id"], "slug": a["slug"], "words": a["words"], "form": a["form"], "ptype": a["ptype"]} for a in leak_city],
        "priority_rewrite": [
            {"id": a["id"], "slug": a["slug"], "title": a["title"], "ptype": a["ptype"], "words": a["words"], "why": "قالب كيان عام لا يخص الخدمة"}
            for a in p1[:40]
        ],
        "locked": 2973,
    }
    out = Path(__file__).resolve().parents[1] / "audit" / "content-priority.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note(json.dumps({
        "published": summary["published"],
        "kinds": summary["kinds"],
        "national_forms": summary["national_forms"],
        "short": len(short),
        "mismatch": len(mismatch),
        "kayan_generic": len(p1),
        "unique": len(unique),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
