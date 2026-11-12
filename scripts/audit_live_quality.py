#!/usr/bin/env python3
"""Quality audit of published /qa posts. Read-only. Never writes post 2973."""
from __future__ import annotations

import csv
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kayan_article_builder import classify, service_core

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = __import__("base64").b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorAudit/1.0",
}
LOCKED = 2973

PACK_WORDS = {
    "poolleak": ["تسربات المسابح", "تسرب المسبح", "منسوب", "سكمر"],
    "acleak": ["تسرب التكييف", "صرف الوحدة", "فريون"],
    "gasleak": ["تسرب غاز", "رائحة غاز", "موقد"],
    "poolclean": ["تنظيف مسابح", "طحالب", "كلور"],
    "tankclean": ["تنظيف خزانات", "خزان", "رواسب"],
    "duct": ["دكت", "مخارج الهواء"],
    "elevator": ["مصعد", "كابينة", "أدوار"],
    "fire": ["إنذار", "كاشف حريق"],
    "coldroom": ["غرفة تبريد", "تجميد", "كومبرسور"],
    "glass": ["زجاج", "سيكوريت"],
    "solar": ["طاقة شمسية", "ألواح", "إنفرتر"],
    "trees": ["قص أشجار", "تقليم", "أغصان"],
    "birds": ["حمام", "طيور", "شبك طيور"],
    "inspect": ["فحص مباني", "قبل الشراء"],
    "disinfect": ["تعقيم", "أسطح لمس"],
    "restore": ["ترميم", "تساقط دهان"],
    "carpentry": ["نجارة", "ضلف", "مفصل"],
    "woodalt": ["بديل خشب"],
    "doors": ["باب", "موتور", "مفصلات"],
    "aluminum": ["ألومنيوم", "قطاع"],
    "pool": ["مسبح", "حوض", "فلتر المسبح"],
    "insulation": ["عزل", "سطح", "فوم", "أغشية"],
    "ac": ["تكييف", "مكيف", "كويل", "سبليت"],
    "sewer": ["مجاري", "بيارة", "تسليك", "انسداد"],
    "plumbing": ["سباكة", "ليّ", "محبس", "سخان", "مضخة"],
    "pest": ["حشرات", "صراصير", "بق", "رمة", "نمل"],
    "cleaning": ["تنظيف", "غبار", "جلي"],
    "garden": ["حديقة", "عشب", "ري", "نخيل"],
    "paint": ["دهان", "جبس", "ديكور"],
    "floor": ["سيراميك", "رخام", "باركيه", "انترلوك", "إيبوكسي"],
    "kitchen": ["مطبخ", "حمام", "عزل حمام"],
    "build": ["مقاولات", "تشطيب", "ملحق", "صيانة مباني"],
    "elec": ["كهرباء", "كاميرا", "انتركم", "لوحة"],
    "appliance": ["ثلاجة", "غسالة", "فرن"],
    "move": ["نقل عفش", "تغليف", "أثاث"],
    "outdoor": ["مظلة", "ساتر", "برجولة", "جلسة"],
}

TEMPLATE_MARKERS = [
    "rukn-article",
    "article-hero",
    "تشخيص ثم نطاق مكتوب",
    "التغطية في مدن قطر — بلا نسخ متطابقة",
    "ما الذي لا نعد به في هذه الصفحة؟",
    "لا نثبت سعراً نهائياً لكل فيلا",
    "inspect, then write the scope",
    "Cities we cover — without duplicate articles",
    "[post_features]",
    "[post_steps]",
    "[post_call]",
    "لماذا تختار ركن التطور",
    "خطوات العمل",
    "faq-item",
]

BOILERPLATE = [
    "التغطية في مدن قطر — بلا نسخ متطابقة",
    "لا ننشئ مقالاً مكرراً",
    "ما الذي لا نعد به في هذه الصفحة",
    "كشف تسربات المياه للدولة في مقال واحد",
    "الحل النهائي 2026",
    "واتساب من زر الصفحة",
    "زر الاتصال الهاتفي مخفي",
    "ركن التطور يجمع خدمات المنزل تحت مسؤولية واحدة",
    "المقر في الدوحة، والفريق يصل إلى",
    "We do not publish the same",
    "Call buttons are hidden",
    "City hub pages explain building types",
]

H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.I | re.S)
IMG_RE = re.compile(r"<img[^>]+src=['\"]([^'\"]+)['\"]", re.I)
TAG_RE = re.compile(r"<[^>]+>")
SHORT_RE = re.compile(r"\[[^\]]+\]")


def api(path, timeout=90):
    url = path if path.startswith("http") else BASE + path
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
        return json.loads(r.read().decode() or "null"), {k.lower(): v for k, v in r.headers.items()}


def get_all():
    items, page = [], 1
    while True:
        data, meta = api(
            f"/wp/v2/posts?per_page=100&page={page}&status=publish&context=edit"
            "&_fields=id,slug,status,title,link,date,modified,content,excerpt"
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


def text_of(html: str) -> str:
    t = unescape(html or "")
    t = SHORT_RE.sub(" ", t)
    t = TAG_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def words_of(text: str) -> list[str]:
    return [w for w in re.split(r"\s+", text) if w]


def h2s(html: str) -> list[str]:
    out = []
    for m in H2_RE.findall(html or ""):
        out.append(re.sub(r"\s+", " ", TAG_RE.sub("", unescape(m))).strip())
    return out


def strip_boilerplate(text: str) -> str:
    t = text
    for b in BOILERPLATE:
        t = t.replace(b, " ")
    return re.sub(r"\s+", " ", t).strip()


def shingles(text: str, n: int = 4) -> set[str]:
    toks = words_of(re.sub(r"[^\w\u0600-\u06FF]+", " ", text.lower()))
    if len(toks) < n:
        return set(toks)
    return {" ".join(toks[i : i + n]) for i in range(len(toks) - n + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    uni = len(a | b)
    return inter / uni if uni else 0.0


def content_pack_scores(text: str) -> Counter:
    scores = Counter()
    for pack, kws in PACK_WORDS.items():
        for kw in kws:
            if kw.lower() in text.lower() if kw.isascii() else kw in text:
                scores[pack] += text.count(kw) if not kw.isascii() else text.lower().count(kw.lower())
    return scores


def template_hits(html: str) -> list[str]:
    return [m for m in TEMPLATE_MARKERS if m.lower() in html.lower()]


def find_errors(html: str, title: str, slug: str, text: str, pid: int = 0) -> list[str]:
    errs = []
    if re.search(r"\{[A-Z0-9_]+\}", html or ""):
        errs.append("placeholder")
    if any(x in text for x in ("أبوظبي", "الإمارات", "Mazid", "إمارة", "الإمارة")):
        errs.append("عبارات-إمارات")
    if re.search(r"tel:\+?\d", html or ""):
        errs.append("رابط-اتصال")
    if re.search(r"97431110184|3111 0184|\+974", html or ""):
        errs.append("هاتف-قطر-قديم")
    if pid != LOCKED and slug != "water-leak-detection-company-in-qatar":
        if "wa.me/" in (html or "") and "971586634710" not in (html or ""):
            errs.append("واتساب-غير-المعتمد")
    if "اتصل الآن" in text:
        errs.append("زر-اتصل-ظاهر")
    imgs = IMG_RE.findall(html or "")
    if not imgs:
        errs.append("بدون-صورة")
    rel = [s for s in imgs if not s.startswith(("http://", "https://", "data:"))]
    if rel:
        errs.append("صور-نسبية")
    if "معاينة مجانية" in text:
        errs.append("وعد-معاينة-مجانية")
    if title.count("💧") + title.count("🔥") + title.count("⭐") >= 1:
        errs.append("إيموجي-في-العنوان")
    if not any(x in (html or "") for x in ("faq-item", "أسئلة شائعة", "FAQ")):
        errs.append("بدون-أسئلة")
    if "wa.me" not in (html or "") and "واتساب" not in text and "WhatsApp" not in text:
        errs.append("بدون-واتساب")
    if "[post_" in (html or "") and html.count("[post_") >= 3:
        # shortcodes present is OK if theme expands them; flag only if nothing else
        pass
    if any(x in title.lower() for x in ("exmaple", "example.com", "lorem")):
        errs.append("نص-تجريبي")
    if any(x in slug for x in ("skrabb", "skrab", "recruitment", "athath-mstaml")):
        errs.append("خارج-النشاط")
    return errs


def title_of(p) -> str:
    t = p.get("title") or {}
    return unescape(t.get("raw") or t.get("rendered") or "")


def html_of(p) -> str:
    c = p.get("content") or {}
    return c.get("raw") or c.get("rendered") or ""


def main():
    posts = get_all()
    rows = []
    shingle_map = {}
    outline_groups = defaultdict(list)
    template_groups = defaultdict(list)

    for p in posts:
        pid = int(p["id"])
        slug = p.get("slug") or ""
        title = title_of(p)
        html = html_of(p)
        text = text_of(html)
        words = words_of(text)
        wc = len(words)
        hs = h2s(html)
        outline = " | ".join(hs)
        hits = template_hits(html)
        ptype = classify(title, slug)
        core = service_core(title)
        body = strip_boilerplate(text)
        scores = content_pack_scores(body)
        top_content = scores.most_common(2)
        top1 = top_content[0][0] if top_content else ""
        top1n = top_content[0][1] if top_content else 0
        title_score = scores.get(ptype, 0)
        mismatch = False
        mismatch_why = ""
        if top1 and ptype not in ("general",) and top1 != ptype and top1n >= 8 and title_score <= top1n * 0.35:
            mismatch = True
            mismatch_why = f"العنوان={ptype} والمحتوى يميل إلى {top1} ({top1n} مقابل {title_score})"
        if core and core not in body and pid != LOCKED and len(core) > 4:
            # title core missing from body after boilerplate strip — weak signal
            if core not in text:
                mismatch = True
                mismatch_why = (mismatch_why + "؛ " if mismatch_why else "") + f"عبارة الخدمة «{core}» غير موجودة في النص"
        errs = find_errors(html, title, slug, text, pid)
        if pid == LOCKED:
            kind = "locked-leak"
        elif slug.endswith("-en") or slug.endswith("-qatar-en"):
            kind = "english"
        else:
            kind = "national"
        if len(hits) >= 6:
            tmpl = "longform-2026-10"
        elif "article-hero" in (html or "") and "[post_features]" in (html or ""):
            tmpl = "kayan-visual"
        elif pid == LOCKED:
            tmpl = "ranking-original"
        else:
            tmpl = "other"
        rec = {
            "id": pid,
            "slug": slug,
            "title": title,
            "link": p.get("link") or "",
            "kind": kind,
            "ptype": ptype,
            "words": wc,
            "h2_count": len(hs),
            "outline": outline,
            "template": tmpl,
            "template_hits": len(hits),
            "mismatch": mismatch,
            "mismatch_why": mismatch_why,
            "content_top": top1,
            "content_top_n": top1n,
            "title_score": title_score,
            "errors": "|".join(errs),
            "short": wc < 1000,
            "locked": pid == LOCKED,
        }
        rows.append(rec)
        shingle_map[pid] = shingles(body if body else text, 4)
        outline_groups[outline].append(pid)
        template_groups[tmpl].append(pid)

    # similarity pairs
    pairs = []
    by_type = defaultdict(list)
    for r in rows:
        if r["id"] == LOCKED:
            continue
        by_type[r["ptype"]].append(r["id"])
    id_row = {r["id"]: r for r in rows}
    for ptype, ids in by_type.items():
        for i, a in enumerate(ids):
            for b in ids[i + 1 :]:
                sim = jaccard(shingle_map[a], shingle_map[b])
                if sim >= 0.55:
                    pairs.append((round(sim, 3), a, b, ptype))
    pairs.sort(reverse=True)

    # same outline groups (ignore empty)
    same_outline = {
        k: v for k, v in outline_groups.items() if k and len(v) >= 3
    }

    short = [r for r in rows if r["short"] and r["id"] != LOCKED]
    mismatches = [r for r in rows if r["mismatch"] and r["id"] != LOCKED]
    errored = [r for r in rows if r["errors"] and r["id"] != LOCKED]
    same_tmpl = [r for r in rows if r["template"] == "longform-2026-10"]

    summary = {
        "published": len(rows),
        "locked_ok": any(r["id"] == LOCKED for r in rows),
        "under_1000": len(short),
        "under_1000_ids": [{"id": r["id"], "slug": r["slug"], "words": r["words"], "title": r["title"]} for r in sorted(short, key=lambda x: x["words"])],
        "template_counts": {k: len(v) for k, v in template_groups.items()},
        "same_template_longform": len(same_tmpl),
        "same_outline_groups": [
            {"count": len(v), "sample_h2": k[:180], "ids": v[:12]}
            for k, v in sorted(same_outline.items(), key=lambda kv: -len(kv[1]))[:8]
        ],
        "similar_pairs_ge_0.55": [
            {
                "sim": sim,
                "a": id_row[a]["slug"],
                "b": id_row[b]["slug"],
                "ptype": ptype,
                "a_id": a,
                "b_id": b,
            }
            for sim, a, b, ptype in pairs[:40]
        ],
        "similar_pair_count": len(pairs),
        "mismatches": [
            {"id": r["id"], "slug": r["slug"], "title": r["title"], "why": r["mismatch_why"]}
            for r in mismatches
        ],
        "errors": [
            {"id": r["id"], "slug": r["slug"], "title": r["title"], "errors": r["errors"]}
            for r in errored
        ],
        "word_stats": {
            "min": min(r["words"] for r in rows),
            "max": max(r["words"] for r in rows),
            "median": sorted(r["words"] for r in rows)[len(rows) // 2],
            "locked_words": next(r["words"] for r in rows if r["id"] == LOCKED),
        },
    }

    out = Path(__file__).resolve().parents[1] / "audit"
    out.mkdir(exist_ok=True)
    csv_path = out / "quality-audit-live.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (out / "quality-audit-live.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "published": summary["published"],
        "under_1000": summary["under_1000"],
        "same_template_longform": summary["same_template_longform"],
        "similar_pair_count": summary["similar_pair_count"],
        "mismatches": len(summary["mismatches"]),
        "errors": len(summary["errors"]),
        "locked_words": summary["word_stats"]["locked_words"],
    }, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
