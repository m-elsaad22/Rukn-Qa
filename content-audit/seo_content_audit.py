#!/usr/bin/env python3
"""
Technical SEO + content-quality auditor for a WordPress site.

Fetches published posts, pages, and `services` CPT items via the REST API,
optionally samples live HTML, then flags:

  1. Thin content (< N words, default 1000)
  2. Template / boilerplate overuse (shared heading skeleton)
  3. Duplicate / near-duplicate copy and keyword cannibalization
  4. Search-intent / relevance mismatch (title vs body, city, service family)
  5. Missing SEO elements, placeholders, structural errors

Credentials MUST come from the environment (never commit them):

  WP_BASE          default https://www.rukn-eltatawer.com/qa
  WP_USER          WordPress username
  WP_APP_PASSWORD  application password

Usage:
  WP_USER=... WP_APP_PASSWORD=... python3 content-audit/seo_content_audit.py
  python3 content-audit/seo_content_audit.py --live-html priority --thin 1000
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html as html_lib
import json
import os
import random
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_BASE = "https://www.rukn-eltatawer.com/qa"
UA = "RuknSeoAudit/1.0 (+https://www.rukn-eltatawer.com/qa)"

CITY_SLUGS = [
    "al-shahaniya",
    "al-daayen",
    "al-rayyan",
    "al-wakrah",
    "umm-salal",
    "al-shamal",
    "al-khor",
    "lusail",
    "doha",
]  # longest-first for suffix strip

CITY_AR = [
    "الشحانية",
    "الظعاين",
    "أم صلال والخيسة",
    "أم صلال",
    "الخيسة",
    "الريان",
    "الوكرة",
    "الشمال",
    "الخور",
    "لوسيل",
    "الدوحة",
    "قطر",
]

CITY_EN = [
    "al shahaniya",
    "al-shahaniya",
    "al daayen",
    "al-daayen",
    "umm salal",
    "umm-salal",
    "al rayyan",
    "al-rayyan",
    "al wakrah",
    "al-wakrah",
    "al shamal",
    "al-shamal",
    "al khor",
    "al-khor",
    "lusail",
    "doha",
    "qatar",
]

PLACEHOLDER_PATTERNS = [
    r"lorem ipsum",
    r"\bTODO\b",
    r"\bTBD\b",
    r"\bFIXME\b",
    r"\[your[^\]]*\]",
    r"\{PHONE_RUKN[^}]*\}",
    r"\{WHATSAPP_RUKN[^}]*\}",
    r"\[\[projects\]\]",
    r"\[post_(?:features|steps|prices|services|call)[^\]]*\]?",
    r"ضع النص",
    r"نص تجريبي",
    r"Coming soon",
    r"Lorem Ipsum",
    r"xxx+",
]

SHORTCODE_RE = re.compile(
    r"\[(?:post_features|post_steps|post_prices|post_services|post_call|projects)[^\]]*\]",
    re.I,
)

GRID_MARKERS = [
    "rukn-article",
    "متى تطلب الخدمة",
    "طريقة العمل",
    "التغطية المحلية",
    "لا رقم قطري منشور حالياً",
    "أزرار الاتصال مخفية",
]

# Service-family lexicons (Arabic + English slug hints)
KIND_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("sound", re.compile(r"soundproof|عازل?\s*صوت|عزل\s*صوت|مسار الصوت", re.I)),
    ("leak", re.compile(r"leak[-_ ]|humidity|waterproof|تسرب|رطوب|كشف تسرب|بدون تكسير", re.I)),
    ("insulate", re.compile(r"insulat|lining|thermal|عزل\s*(أسطح|سطح|خزان|حراري)|فوم|عازل حرار", re.I)),
    ("ac", re.compile(r"(^|[\s-])(ac|freon|cooling|split-ac)([\s-]|$) |تكييف|مكيف|فريون|\bدكت\b", re.I)),
    ("pest", re.compile(r"pest|cockroach|termite|حشرات|صراصير|بق الفراش|نمل أبيض|\bالرمة\b|قوارض|تعقيم", re.I)),
    ("clean", re.compile(r"clean|polishing|تنظيف|جلي|تلميع", re.I)),
    ("plumb", re.compile(r"plumb|drain|septic|sewerage|سباك|مجاري|صرف صحي|تسليك|سخان ماء|مضخة", re.I)),
    ("electric", re.compile(r"electric|lighting|cctv|كهرب|إنارة|كاميرات", re.I)),
    ("garden", re.compile(r"garden|grass|irrigation|landscap|حديق|عشب|ري الحد|نافورة", re.I)),
    ("paint", re.compile(r"paint|wallpaper|gypsum|دهان|صبغ|جبس|ورق جدران", re.I)),
    ("solar", re.compile(r"solar|طاقة شمسية|سخان شمسي", re.I)),
    ("renovate", re.compile(r"inspect|renovation|crack|ترميم|فحص فيلا|شقوق", re.I)),
    ("move", re.compile(r"moving|storage|furniture|نقل عفش|تخزين", re.I)),
    ("recruit", re.compile(r"recruit|استقدام|عمالة", re.I)),
    ("shipping", re.compile(r"shipping|freight|شحن", re.I)),
    ("scrap", re.compile(r"scrap|سكراب|مستعمل", re.I)),
]


def kind_scores(blob: str) -> dict[str, int]:
    s = blob or ""
    return {kind: len(rx.findall(s)) for kind, rx in KIND_RULES}


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------


class ContentParser(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip = 0
        self._h_tag: str | None = None
        self._h_parts: list[str] = []
        self.text_parts: list[str] = []
        self.headings: list[tuple[str, str]] = []
        self.h1 = self.h2 = self.h3 = 0
        self.images = 0
        self.images_no_alt = 0
        self.internal_links = 0
        self.external_links = 0
        self.wa_links = 0
        self.tel_links = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k.lower(): (v or "") for k, v in attrs}
        if tag in self.SKIP:
            self._skip += 1
            return
        if self._skip:
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._h_tag = tag
            self._h_parts = []
            if tag == "h1":
                self.h1 += 1
            elif tag == "h2":
                self.h2 += 1
            elif tag == "h3":
                self.h3 += 1
        if tag == "img":
            self.images += 1
            alt = ad.get("alt", "")
            if not alt.strip():
                self.images_no_alt += 1
        if tag == "a":
            href = ad.get("href", "").strip()
            low = href.lower()
            if low.startswith("tel:"):
                self.tel_links += 1
            elif "wa.me" in low or "whatsapp" in low:
                self.wa_links += 1
            elif low.startswith("http") and "rukn-eltatawer.com" not in low:
                self.external_links += 1
            elif href.startswith("/") or "rukn-eltatawer.com" in low or href.startswith("#"):
                if not href.startswith("#"):
                    self.internal_links += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP and self._skip:
            self._skip -= 1
            return
        if tag == self._h_tag:
            txt = re.sub(r"\s+", " ", "".join(self._h_parts)).strip()
            if txt:
                self.headings.append((tag, txt))
            self._h_tag = None
            self._h_parts = []

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        if self._h_tag is not None:
            self._h_parts.append(data)
        self.text_parts.append(data)


def parse_html(raw: str) -> ContentParser:
    p = ContentParser()
    try:
        p.feed(raw or "")
        p.close()
    except Exception:
        pass
    return p


def visible_text(raw: str) -> str:
    p = parse_html(raw)
    t = re.sub(r"\s+", " ", html_lib.unescape(" ".join(p.text_parts))).strip()
    t = re.sub(r"في هذا المقال|محتويات المقال|جدول المحتويات", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def word_count(text: str) -> int:
    if not text:
        return 0
    tokens = re.findall(r"[A-Za-z0-9\u0600-\u06FF]+", text)
    return len([t for t in tokens if len(t) > 1 or t.isdigit()])


def normalize_cities(text: str) -> str:
    t = text
    for c in CITY_AR:
        t = t.replace(c, "{CITY}")
    low = t
    for c in CITY_EN:
        low = re.sub(re.escape(c), "{CITY}", low, flags=re.I)
    low = re.sub(r"في \{CITY\}|بال\{CITY\}|ب\{CITY\}", "{CITY}", low)
    return re.sub(r"\s+", " ", low).strip()


def heading_skeleton(headings: list[tuple[str, str]]) -> str:
    parts = []
    for tag, txt in headings:
        if tag not in {"h1", "h2", "h3"}:
            continue
        n = normalize_cities(txt)
        n = re.sub(r"\d+", "N", n)
        parts.append(f"{tag}:{n}")
    return " | ".join(parts)


def simhash64(text: str) -> int:
    tokens = re.findall(r"[A-Za-z0-9\u0600-\u06FF]{2,}", (text or "").lower())
    if not tokens:
        return 0
    v = [0] * 64
    for tok in tokens:
        h = int.from_bytes(hashlib.md5(tok.encode("utf-8")).digest()[:8], "big")
        for i in range(64):
            v[i] += 1 if (h >> i) & 1 else -1
    out = 0
    for i in range(64):
        if v[i] >= 0:
            out |= 1 << i
    return out


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def city_from_slug(slug: str) -> str:
    s = slug or ""
    for c in CITY_SLUGS:
        if s == c or s.endswith("-" + c):
            return c
    return ""


def service_stem(slug: str) -> str:
    s = slug or ""
    city = city_from_slug(s)
    if city:
        s = re.sub(r"-" + re.escape(city) + r"$", "", s)
    s = re.sub(r"-in-qatar$|-qatar$|-fy-qtr$", "", s)
    return s


def detect_kind(blob: str) -> str:
    scores = kind_scores(blob)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


def is_city_grid(html: str, slug: str) -> bool:
    if city_from_slug(slug) and html and "rukn-article" in html:
        return True
    hits = sum(1 for m in GRID_MARKERS if m in (html or ""))
    return hits >= 3


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------


def _ctx() -> ssl.SSLContext:
    return ssl.create_default_context()


def request_json(url: str, auth: str | None, timeout: int = 90) -> tuple[Any, dict[str, str]]:
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if auth:
        headers["Authorization"] = f"Basic {auth}"
    req = urllib.request.Request(url, headers=headers)
    last_err: Exception | None = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as resp:
                raw = resp.read().decode("utf-8", "replace")
                return json.loads(raw), {k.lower(): v for k, v in resp.headers.items()}
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in {429, 503, 502} and attempt < 4:
                time.sleep(2 + attempt * 3)
                continue
            raise
        except Exception as e:
            last_err = e
            time.sleep(1 + attempt)
    raise RuntimeError(last_err)


def request_html(url: str, timeout: int = 25, follow: bool = False) -> tuple[int, str, str]:
    """Fetch HTML. Default does not follow redirects (SEO-accurate status)."""
    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
            raise urllib.error.HTTPError(newurl, code, msg, headers, fp)

    handlers: list[urllib.request.BaseHandler] = [urllib.request.HTTPSHandler(context=_ctx())]
    if not follow:
        handlers.insert(0, NoRedir())
    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with opener.open(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace"), resp.geturl()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace") if e.fp else ""
        loc = e.headers.get("Location", "") if e.headers else ""
        return e.code, body, loc or url
    except Exception as e:
        return 0, str(e), url


def paginate_wp(base: str, route: str, auth: str, extra: str = "") -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    page = 1
    while True:
        q = f"{base}/wp-json/wp/v2/{route}?status=publish&per_page=100&page={page}&_fields=id,slug,link,title,content,excerpt,type,status,featured_media{extra}"
        try:
            data, headers = request_json(q, auth)
        except urllib.error.HTTPError as e:
            if e.code == 400 and page > 1:
                break
            raise
        if not data:
            break
        out.extend(data)
        total_pages = int(headers.get("x-wp-totalpages") or 1)
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.05)
    return out


def paginate_rankmath(base: str, auth: str, post_type: str) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    page = 1
    while True:
        q = (
            f"{base}/wp-json/rankmath/v1/links/posts?per_page=100&page={page}"
            + "&" + urllib.parse.urlencode({"post_type[]": post_type})
        )
        data, _ = request_json(q, auth)
        posts = data.get("posts") if isinstance(data, dict) else data
        if not posts:
            break
        for row in posts:
            try:
                out[int(row["post_id"])] = row
            except Exception:
                continue
        total_pages = int((data or {}).get("pages") or 1) if isinstance(data, dict) else 1
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.05)
    return out


# ---------------------------------------------------------------------------
# Live head parse
# ---------------------------------------------------------------------------

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
META_RE = re.compile(
    r'<meta[^>]+(?:name|property)=["\']([^"\']+)["\'][^>]+content=["\']([^"\']*)["\']',
    re.I,
)
META_RE2 = re.compile(
    r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:name|property)=["\']([^"\']+)["\']',
    re.I,
)
CANON_RE = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', re.I)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html_lib.unescape(s)).strip()


def parse_live(html: str) -> dict[str, Any]:
    title_m = TITLE_RE.search(html or "")
    title = strip_tags(title_m.group(1)) if title_m else ""
    metas: dict[str, str] = {}
    for m in META_RE.finditer(html or ""):
        metas[m.group(1).lower()] = m.group(2)
    for m in META_RE2.finditer(html or ""):
        metas[m.group(2).lower()] = m.group(1)
    canon_m = CANON_RE.search(html or "")
    h1s = [strip_tags(x) for x in H1_RE.findall(html or "")]
    robots = (metas.get("robots") or "").lower()
    desc = metas.get("description") or metas.get("og:description") or ""
    return {
        "live_title": title,
        "meta_description": desc,
        "canonical": canon_m.group(1) if canon_m else "",
        "robots": robots,
        "noindex": "noindex" in robots,
        "live_h1_count": len(h1s),
        "live_h1": " | ".join(h1s[:3]),
        "og_title": metas.get("og:title") or "",
    }


# ---------------------------------------------------------------------------
# Record
# ---------------------------------------------------------------------------


@dataclass
class Doc:
    id: int
    type: str
    slug: str
    url: str
    title: str
    excerpt: str
    html: str
    text: str
    words: int
    h1: int
    h2: int
    h3: int
    headings: list[tuple[str, str]]
    skeleton: str
    skeleton_hash: str
    images: int
    images_no_alt: int
    internal_links: int
    wa_links: int
    tel_links: int
    city: str
    stem: str
    kind_title: str
    kind_body: str
    is_grid: bool
    simhash: int
    placeholders: list[str]
    shortcodes: list[str]
    unique_token_ratio: float
    issues: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    severity: str = ""
    cluster_size: int = 1
    similar_to: str = ""
    similar_hamming: str = ""
    cannibal_group_size: int = 1
    rank_seo_score: str = ""
    rank_orphan: str = ""
    rank_incoming: str = ""
    rank_internal: str = ""
    live: dict[str, Any] = field(default_factory=dict)


def rendered(block: Any) -> str:
    if isinstance(block, dict):
        return block.get("rendered") or ""
    return str(block or "")


def find_placeholders(html: str, text: str) -> list[str]:
    blob = (html or "") + "\n" + (text or "")
    found = []
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, blob, re.I):
            found.append(pat)
    if SHORTCODE_RE.search(blob):
        found.append("unexpanded_shortcode")
    if "{PHONE" in blob or "{WHATSAPP" in blob:
        found.append("csv_placeholder")
    return found


def unique_ratio(text: str) -> float:
    toks = re.findall(r"[A-Za-z0-9\u0600-\u06FF]{2,}", (text or "").lower())
    if len(toks) < 20:
        return 0.0
    return round(len(set(toks)) / len(toks), 3)


def classify_severity(issues: list[str]) -> str:
    hard = {
        "thin_content",
        "critical_thin",
        "template_boilerplate",
        "near_duplicate",
        "intent_mismatch",
        "missing_h1_live",
        "placeholder_or_shortcode",
        "noindex",
        "empty_body",
    }
    if any(i in hard for i in issues):
        if "critical_thin" in issues or "placeholder_or_shortcode" in issues or "intent_mismatch" in issues:
            return "حرجة"
        return "عالية"
    if issues:
        return "متوسطة"
    return "منخفضة"


# ---------------------------------------------------------------------------
# Build docs + analyze
# ---------------------------------------------------------------------------


def build_doc(item: dict[str, Any], ptype: str) -> Doc:
    html = rendered(item.get("content"))
    html = re.sub(r'(?is)<div[^>]*id="ez-toc-container"[^>]*>.*?</div>', " ", html)
    html = re.sub(r'(?is)<div[^>]*class="[^"]*ez-toc[^"]*"[^>]*>.*?</div>', " ", html)
    title = strip_tags(rendered(item.get("title")))
    excerpt = strip_tags(rendered(item.get("excerpt")))
    parsed = parse_html(html)
    text = visible_text(html)
    slug = item.get("slug") or ""
    city = city_from_slug(slug)
    stem = service_stem(slug)
    kind_title = detect_kind(f"{slug} {title}")
    kind_body = detect_kind(text[:1500] + " " + slug)
    skel = heading_skeleton(parsed.headings)
    sh = hashlib.sha1(skel.encode("utf-8")).hexdigest()[:12] if skel else "no-headings"
    norm = normalize_cities(text)
    placeholders = find_placeholders(html, text)
    shortcodes = SHORTCODE_RE.findall(html or "")
    return Doc(
        id=int(item.get("id") or 0),
        type=ptype,
        slug=slug,
        url=item.get("link") or "",
        title=title,
        excerpt=excerpt,
        html=html,
        text=text,
        words=word_count(text),
        h1=parsed.h1,
        h2=parsed.h2,
        h3=parsed.h3,
        headings=parsed.headings,
        skeleton=skel,
        skeleton_hash=sh,
        images=parsed.images,
        images_no_alt=parsed.images_no_alt,
        internal_links=parsed.internal_links,
        wa_links=parsed.wa_links,
        tel_links=parsed.tel_links,
        city=city,
        stem=stem,
        kind_title=kind_title,
        kind_body=kind_body,
        is_grid=is_city_grid(html, slug),
        simhash=simhash64(norm),
        placeholders=placeholders,
        shortcodes=shortcodes,
        unique_token_ratio=unique_ratio(norm),
    )


def flag_docs(docs: list[Doc], thin: int) -> None:
    skel_groups: dict[str, list[Doc]] = defaultdict(list)
    stem_groups: dict[str, list[Doc]] = defaultdict(list)
    for d in docs:
        skel_groups[d.skeleton_hash].append(d)
        if d.stem:
            stem_groups[d.stem].append(d)

    for d in docs:
        d.cluster_size = len(skel_groups[d.skeleton_hash])
        d.cannibal_group_size = len(stem_groups.get(d.stem, [d]))

    # simhash near-dup among non-identical URLs, bucketed
    buckets: dict[int, list[Doc]] = defaultdict(list)
    for d in docs:
        buckets[d.simhash >> 48].append(d)

    near: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for group in buckets.values():
        n = len(group)
        # cap comparisons inside huge identical-template buckets
        sample = group if n <= 80 else group[:40] + group[-20:]
        for i, a in enumerate(sample):
            for b in sample[i + 1 :]:
                if a.id == b.id:
                    continue
                dist = hamming(a.simhash, b.simhash)
                if dist <= 6:
                    near[a.id].append((dist, b.url))
                    near[b.id].append((dist, a.url))

    for d in docs:
        pairs = sorted(near.get(d.id, []), key=lambda x: x[0])[:5]
        if pairs:
            d.similar_hamming = str(pairs[0][0])
            d.similar_to = " ; ".join(u for _, u in pairs[:3])

        if d.words == 0:
            d.issues.append("empty_body")
            d.notes.append("الجسم فارغ بعد إزالة HTML")
        elif d.words < 300:
            d.issues.append("critical_thin")
            d.notes.append(f"محتوى هزيل جداً ({d.words} كلمة)")
        elif d.words < thin:
            d.issues.append("thin_content")
            d.notes.append(f"أقل من {thin} كلمة ({d.words})")

        if d.cluster_size >= 8:
            d.issues.append("template_boilerplate")
            d.notes.append(f"نفس الهيكل العناوين في {d.cluster_size} صفحة (hash {d.skeleton_hash})")
        elif d.unique_token_ratio and d.unique_token_ratio < 0.28 and d.words >= 80:
            d.issues.append("template_boilerplate")
            d.notes.append(f"نسبة كلمات فريدة منخفضة ({d.unique_token_ratio})")

        if d.is_grid:
            d.issues.append("local_doorway_variant")
            d.notes.append("صفحة مدينة×خدمة من مولّد الشبكة — تغطية محلية لكن خطر doorway/تكرار")

        if pairs and pairs[0][0] <= 3:
            if d.is_grid and d.cannibal_group_size <= 9:
                d.issues.append("city_variant_similar")
            else:
                d.issues.append("near_duplicate")
                d.notes.append(f"تشابه SimHash مسافة {pairs[0][0]} مع {pairs[0][1]}")
        elif pairs and pairs[0][0] <= 6 and not d.is_grid:
            d.issues.append("similar_content")
            d.notes.append(f"محتوى مشابه (hamming {pairs[0][0]})")

        if d.cannibal_group_size >= 6 and d.stem:
            d.issues.append("keyword_cannibalization")
            d.notes.append(f"نفس جذع الخدمة `{d.stem}` على {d.cannibal_group_size} URL")

        # intent
        # intent: only when the title family is absent from the body and another family dominates
        if (
            not d.is_grid
            and d.type == "post"
            and d.kind_title != "general"
            and not d.slug.startswith("services-in-")
        ):
            scores = kind_scores(d.text)
            own = scores.get(d.kind_title, 0)
            best_kind = max(scores, key=scores.get) if scores else "general"
            best_n = scores.get(best_kind, 0)
            if own == 0 and best_n >= 2 and best_kind != d.kind_title:
                d.issues.append("intent_mismatch")
                d.notes.append(f"العنوان/السلَج أسرة `{d.kind_title}` بينما النص يغلب عليه `{best_kind}` ({best_n} إشارة)")
        elif d.type == "services" and d.kind_title != "general":
            scores = kind_scores(d.text)
            if scores.get(d.kind_title, 0) == 0 and scores.get("leak", 0) >= 3:
                d.issues.append("intent_mismatch")
                d.notes.append("صفحة خدمة CPT يغلب عليها فقرة تسربات لا موضوع الخدمة")

        if d.city:
            ar_map = {
                "doha": "الدوحة",
                "lusail": "لوسيل",
                "al-rayyan": "الريان",
                "al-wakrah": "الوكرة",
                "al-khor": "الخور",
                "umm-salal": "أم صلال",
                "al-daayen": "الظعاين",
                "al-shamal": "الشمال",
                "al-shahaniya": "الشحانية",
            }
            city_ar = ar_map.get(d.city, "")
            # ignore HQ disclaimer
            body_wo_hq = d.text.replace("المقر الدوحة", " ")
            if city_ar and city_ar not in body_wo_hq and d.city not in d.slug:
                d.issues.append("intent_mismatch")
                d.notes.append("المدينة في الرابط غير مذكورة في النص")
            # other city dominating
            counts = {c: body_wo_hq.count(name) for c, name in ar_map.items()}
            if city_ar:
                own = counts.get(d.city, 0)
                other = max((n, c) for c, n in counts.items() if c != d.city)
                if other[0] >= 3 and other[0] > own + 1:
                    d.issues.append("intent_mismatch")
                    d.notes.append(f"النص يركّز على {other[1]} أكثر من {d.city}")

        if d.placeholders or d.shortcodes:
            d.issues.append("placeholder_or_shortcode")
            d.notes.append("عناصر نائبة أو شورت كود غير موسَّع: " + ",".join((d.placeholders or d.shortcodes)[:4]))

        if d.h2 + d.h3 == 0 and d.words > 80:
            d.issues.append("missing_h2_h3")
            d.notes.append("لا توجد عناوين H2/H3 داخل المحتوى")
        if d.h1 == 0:
            d.issues.append("no_h1_in_body")
            d.notes.append("لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب)")
        if d.images and d.images_no_alt:
            d.issues.append("images_missing_alt")
            d.notes.append(f"{d.images_no_alt}/{d.images} صورة بلا alt")
        if not d.excerpt:
            d.issues.append("missing_excerpt")
        if d.internal_links == 0 and d.words > 80:
            d.issues.append("no_internal_links_in_body")
            d.notes.append("لا روابط داخلية في الجسم")
        if d.tel_links:
            d.issues.append("tel_link_present")
            d.notes.append("وجود رابط tel: في المحتوى")

        # Kayan leftover / off-brand
        if re.search(r"كيان ويب|KAYAN WEB|YourColor", d.html + d.text, re.I):
            d.issues.append("brand_leak")
            d.notes.append("بقايا علامة تجارية/قالب غير ركن التطور")

        d.issues = list(dict.fromkeys(d.issues))
        d.notes = list(dict.fromkeys(d.notes))
        d.severity = classify_severity(d.issues)


def apply_live(d: Doc, status: int, html: str, final: str) -> None:
    info = parse_live(html) if html and status == 200 else {}
    info["http_status"] = status
    info["final_url"] = final
    d.live = info
    if status and status >= 400:
        d.issues.append("http_error")
        d.notes.append(f"HTTP {status}")
    if info.get("noindex"):
        d.issues.append("noindex")
        d.notes.append("robots noindex على الصفحة الحية")
    if status == 200:
        if info.get("live_h1_count", 0) == 0:
            d.issues.append("missing_h1_live")
            d.notes.append("لا وسم H1 في HTML الحي")
        elif info.get("live_h1_count", 0) > 1:
            d.issues.append("multiple_h1")
            d.notes.append(f"{info['live_h1_count']} عناوين H1")
        desc = info.get("meta_description") or ""
        if not desc.strip():
            d.issues.append("missing_meta_description")
        elif len(desc) < 50:
            d.issues.append("short_meta_description")
            d.notes.append(f"meta description {len(desc)} حرفاً")
        if not info.get("canonical"):
            d.issues.append("missing_canonical")
        live_h1 = info.get("live_h1") or ""
        if live_h1 and d.title and strip_tags(d.title) not in live_h1 and live_h1 not in d.title:
            # loose: if fewer than 8 shared words
            tset = set(re.findall(r"[\u0600-\u06FF]{3,}", d.title))
            hset = set(re.findall(r"[\u0600-\u06FF]{3,}", live_h1))
            if tset and hset and len(tset & hset) / max(1, len(tset)) < 0.4:
                d.issues.append("intent_mismatch")
                d.notes.append(f"H1 الحي لا يطابق العنوان: {live_h1[:80]}")
    d.issues = list(dict.fromkeys(d.issues))
    d.notes = list(dict.fromkeys(d.notes))
    d.severity = classify_severity(d.issues)


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

CSV_FIELDS = [
    "id",
    "type",
    "title",
    "url",
    "slug",
    "word_count",
    "severity",
    "issues",
    "notes",
    "city",
    "service_stem",
    "kind_title",
    "kind_body",
    "is_city_grid",
    "h1_in_body",
    "h2",
    "h3",
    "heading_skeleton_hash",
    "template_cluster_size",
    "cannibal_group_size",
    "unique_token_ratio",
    "similar_to",
    "similar_hamming",
    "images",
    "images_no_alt",
    "internal_links_in_body",
    "placeholders",
    "rank_seo_score",
    "rank_orphan",
    "rank_incoming_links",
    "rank_internal_links",
    "live_http",
    "live_h1_count",
    "live_h1",
    "meta_description_len",
    "canonical",
    "noindex",
]


def to_row(d: Doc) -> dict[str, Any]:
    live = d.live or {}
    return {
        "id": d.id,
        "type": d.type,
        "title": d.title,
        "url": d.url,
        "slug": d.slug,
        "word_count": d.words,
        "severity": d.severity,
        "issues": "|".join(d.issues),
        "notes": " ؛ ".join(d.notes)[:2000],
        "city": d.city,
        "service_stem": d.stem,
        "kind_title": d.kind_title,
        "kind_body": d.kind_body,
        "is_city_grid": int(d.is_grid),
        "h1_in_body": d.h1,
        "h2": d.h2,
        "h3": d.h3,
        "heading_skeleton_hash": d.skeleton_hash,
        "template_cluster_size": d.cluster_size,
        "cannibal_group_size": d.cannibal_group_size,
        "unique_token_ratio": d.unique_token_ratio,
        "similar_to": d.similar_to,
        "similar_hamming": d.similar_hamming,
        "images": d.images,
        "images_no_alt": d.images_no_alt,
        "internal_links_in_body": d.internal_links,
        "placeholders": "|".join(d.placeholders),
        "rank_seo_score": d.rank_seo_score,
        "rank_orphan": d.rank_orphan,
        "rank_incoming_links": d.rank_incoming,
        "rank_internal_links": d.rank_internal,
        "live_http": live.get("http_status", ""),
        "live_h1_count": live.get("live_h1_count", ""),
        "live_h1": (live.get("live_h1") or "")[:180],
        "meta_description_len": len(live.get("meta_description") or "") if live else "",
        "canonical": live.get("canonical", ""),
        "noindex": int(bool(live.get("noindex"))),
    }


def md_escape(s: str) -> str:
    return (s or "").replace("|", "/").replace("\n", " ").strip()


def write_summary(docs: list[Doc], out: Path, thin: int, live_mode: str, base: str) -> None:
    n = len(docs)
    grid = [d for d in docs if d.is_grid]
    other = [d for d in docs if not d.is_grid]
    thin_docs = [d for d in docs if d.words < thin]
    crit = [d for d in docs if d.words < 300]
    templ = [d for d in docs if "template_boilerplate" in d.issues]
    intent = [d for d in docs if "intent_mismatch" in d.issues]
    ph = [d for d in docs if "placeholder_or_shortcode" in d.issues]
    miss_h2 = [d for d in docs if "missing_h2_h3" in d.issues]
    cannibal = [d for d in docs if "keyword_cannibalization" in d.issues]
    orphans = [d for d in docs if str(d.rank_orphan).lower() in {"1", "true", "yes"}]
    word_ok = [d for d in docs if d.words >= thin]

    skel = Counter(d.skeleton_hash for d in docs)
    top_skel = skel.most_common(8)
    stems = Counter(d.stem for d in docs if d.cannibal_group_size >= 6)
    kinds = Counter(d.kind_title for d in docs)
    types = Counter(d.type for d in docs)

    lines = []
    a = lines.append
    a("# تدقيق سيو تقني ومحتوى — ركن التطور قطر")
    a("")
    a(f"**المصدر:** {base} عبر REST (مقالات + صفحات + CPT خدمات).")
    a(f"**التاريخ:** {time.strftime('%Y-%m-%d')}")
    a(f"**الصفحات المفحوصة:** {n} — أنواع: {dict(types)}")
    a(f"**عتبة المحتوى الضعيف:** {thin} كلمة. **فحص HTML الحي:** `{live_mode}`.")
    a("")
    a("هذا التقرير حصيلة سكربت `seo_content_audit.py`. الجدول الكامل لكل URL في `seo-audit-all.csv`.")
    a("")
    a("## الخلاصة التنفيذية")
    a("")
    a("| المؤشر | العدد | النسبة |")
    a("| --- | ---: | ---: |")
    a(f"| إجمالي المنشورات المفحوصة | {n} | 100% |")
    a(f"| محتوى ضعيف (< {thin} كلمة) | {len(thin_docs)} | {len(thin_docs)*100//max(n,1)}% |")
    a(f"| هزيل جداً (< 300 كلمة) | {len(crit)} | {len(crit)*100//max(n,1)}% |")
    a(f"| ≥ {thin} كلمة | {len(word_ok)} | {len(word_ok)*100//max(n,1)}% |")
    a(f"| قالب/نص جاهز مشترك (≥ 8 صفحات بنفس الهيكل) | {len(templ)} | {len(templ)*100//max(n,1)}% |")
    a(f"| شبكة مدينة×خدمة (مولّد) | {len(grid)} | {len(grid)*100//max(n,1)}% |")
    a(f"| تعارض كلمات مفتاحية (نفس الخدمة على ≥6 URL) | {len(cannibal)} | {len(cannibal)*100//max(n,1)}% |")
    a(f"| عدم تطابق نية/عنوان↔نص | {len(intent)} | {len(intent)*100//max(n,1)}% |")
    a(f"| شورت كود أو نص نائب | {len(ph)} | {len(ph)*100//max(n,1)}% |")
    a(f"| بلا H2/H3 في الجسم | {len(miss_h2)} | {len(miss_h2)*100//max(n,1)}% |")
    a(f"| يتيم داخلياً (Rank Math orphan) | {len(orphans)} | {len(orphans)*100//max(n,1)}% |")
    a("")
    a("### الحكم")
    a("")
    a(
        "الموقع يعتمد على طبقتين: (1) صفحات ركيزة وطنية متفاوتة الجودة، "
        "(2) شبكة محلية ضخمة مولَّدة قالبياً (~9 مدن × الخدمة). الطبقة الثانية تغطي قطر جغرافياً "
        "لكنها **محتوى ضعيف هيكلياً ومتشابه بعد تجريد اسم المدينة**، وهذا نمط doorway-page "
        "يعرّض النطاق لتخفيض جودة في البحث وليس لتفوق محلي مستدام."
    )
    a("")
    a("## 1) المحتوى الضعيف")
    a("")
    a(f"كل مقال أقل من **{thin} كلمة** يُعد ضعيفاً وفق طلب التدقيق. توزيع الأطوال:")
    a("")
    buckets = [(0, 150), (150, 300), (300, 500), (500, 800), (800, 1000), (1000, 2000), (2000, 10_000_000)]
    a("| نطاق الكلمات | العدد |")
    a("| --- | ---: |")
    for lo, hi in buckets:
        c = sum(1 for d in docs if lo <= d.words < hi)
        label = f"{lo}–{hi-1}" if hi < 10_000_000 else f"{lo}+"
        a(f"| {label} | {c} |")
    a("")
    a("عيّنة من الأضعف خارج شبكة المدن (الأولى بالأولوية):")
    a("")
    a("| العنوان | الرابط | الكلمات | فئة | ملاحظات |")
    a("| --- | --- | ---: | --- | --- |")
    weak_other = sorted(other, key=lambda d: d.words)[:40]
    if not weak_other:
        weak_other = sorted(docs, key=lambda d: d.words)[:20]
    for d in weak_other:
        cats = ",".join(d.issues[:3]) or "—"
        a(f"| {md_escape(d.title)[:80]} | {d.url} | {d.words} | {cats} | {md_escape(' ؛ '.join(d.notes)[:160])} |")
    a("")
    a(f"شبكة المدن: {len(grid)} صفحة، وسيط الكلمات ≈ {sorted(x.words for x in grid)[len(grid)//2] if grid else 0}. كلها تحت العتبة ما لم يُذكر خلاف ذلك في CSV.")
    a("")
    a("## 2) الإفراط في القوالب")
    a("")
    a("| hash الهيكل | عدد الصفحات | عيّنة عنوان |")
    a("| --- | ---: | --- |")
    by_hash = defaultdict(list)
    for d in docs:
        by_hash[d.skeleton_hash].append(d)
    for hsh, cnt in top_skel:
        sample = by_hash[hsh][0].title if by_hash[hsh] else ""
        a(f"| `{hsh}` | {cnt} | {md_escape(sample)[:70]} |")
    a("")
    if top_skel:
        top_docs = by_hash[top_skel[0][0]]
        skel_txt = top_docs[0].skeleton if top_docs else ""
        a("الهيكل الأكثر تكراراً (بعد استبدال اسم المدينة بـ `{CITY}`):")
        a("")
        a(f"`{md_escape(skel_txt)[:500]}`")
        a("")
    a("## 3) التكرار والتشابه / cannibalization")
    a("")
    a("جذوع الخدمات المكررة عبر المدن (أعلى 25):")
    a("")
    a("| جذع السلَج | عدد الـ URL | مثال |")
    a("| --- | ---: | --- |")
    for stem, _cnt in stems.most_common(25):
        grp = [d for d in docs if d.stem == stem]
        a(f"| `{stem}` | {len(grp)} | {grp[0].url if grp else ''} |")
    a("")
    a("صفحات **غير** الشبكة ومتشابهة (hamming ≤ 6):")
    a("")
    a("| العنوان | الكلمات | مشابه لـ | المسافة |")
    a("| --- | ---: | --- | ---: |")
    shown = 0
    for d in other:
        if d.similar_to and shown < 30:
            a(f"| {md_escape(d.title)[:70]} | {d.words} | {d.similar_to[:120]} | {d.similar_hamming} |")
            shown += 1
    if shown == 0:
        a("| — | — | لا أزواج غير-شبكية تحت العتبة | — |")
    a("")
    a("## 4) عدم تطابق النية")
    a("")
    a("| العنوان | الرابط | الكلمات | ملاحظة |")
    a("| --- | --- | ---: | --- |")
    intent_rows = [d for d in docs if "intent_mismatch" in d.issues]
    intent_show = [d for d in intent_rows if not d.is_grid] + [d for d in intent_rows if d.is_grid]
    for d in intent_show[:50]:
        note = next((n for n in d.notes if "أسرة" in n or "H1" in n or "المدينة" in n or "يركّز" in n), d.notes[0] if d.notes else "")
        a(f"| {md_escape(d.title)[:70]} | {d.url} | {d.words} | {md_escape(note)[:160]} |")
    if not intent_show:
        a("| — | — | — | لا حالات عنوان↔نص متعارضة بعد القواعد الحالية |")
    a("")
    a("## 5) أخطاء وعناصر مفقودة")
    a("")
    a("| العنوان | الرابط | الكلمات | الفئة | ملاحظات |")
    a("| --- | --- | ---: | --- | --- |")
    err_docs = [
        d
        for d in other
        if any(
            x in d.issues
            for x in (
                "placeholder_or_shortcode",
                "missing_h1_live",
                "missing_h2_h3",
                "missing_meta_description",
                "noindex",
                "http_error",
                "brand_leak",
                "empty_body",
            )
        )
    ]
    err_docs = sorted(err_docs, key=lambda d: (0 if d.severity == "حرجة" else 1, d.words))
    for d in err_docs[:60]:
        cats = ",".join(
            i
            for i in d.issues
            if i
            in {
                "placeholder_or_shortcode",
                "missing_h1_live",
                "missing_h2_h3",
                "missing_meta_description",
                "noindex",
                "http_error",
                "brand_leak",
                "empty_body",
                "multiple_h1",
            }
        )
        a(f"| {md_escape(d.title)[:70]} | {d.url} | {d.words} | {cats} | {md_escape(' ؛ '.join(d.notes)[:160])} |")
    a("")
    a("صفحات وCPT الخدمات (كلّها، لأنها واجهة الموقع وليست شبكة المدن):")
    a("")
    a("| النوع | العنوان | الرابط | الكلمات | المشاكل |")
    a("| --- | --- | --- | ---: | --- |")
    for d in docs:
        if d.type in {"page", "services"}:
            a(f"| {d.type} | {md_escape(d.title)[:60]} | {d.url} | {d.words} | {','.join(d.issues[:5]) or '—'} |")
    a("")
    a("## توصيات تقنية (أولوية)")
    a("")
    a("1. **لا توسّع الشبكة أكثر.** 9 نسخ لكل خدمة كافية للتجربة المحلية؛ أي خدمة جديدة تُكتب كركيزة قطر أولاً.")
    a("2. **ارفع 12–20 ركيزة** فوق 1200 كلمة أصلية (تسرب، عزل، تكييف، مجاري، حشرات، تنظيف، سباكة، كهرباء) ثم اربط الشبكة إليها.")
    a("3. **Cannibalization:** اجعل الصفحة الوطنية هي الهدف للبحث العام، وصفحات المدن لـ `[خدمة] في [مدينة]` فقط، مع canonical أو ربط عنقودي واضح.")
    a("4. **أوراق يتيمة:** Rank Math يُظهر أغلب الشبكة بدون روابط داخلة. أضف وحدات «خدمات في هذه المدينة» و«نفس الخدمة في مدن أخرى» في القالب.")
    a("5. **العنصر النائب/الشورت كود** على أي ركيزة متبقية يُحذف فوراً — Google يرى النص الحرفي.")
    a("6. **H1:** الجسم بلا H1 مقبول إن كان القالب يطبع العنوان مرة واحدة فقط؛ تحقق الحي في عمود `live_h1_count`.")
    a("")
    a("## إعادة التشغيل")
    a("")
    a("```bash")
    a("export WP_USER=... WP_APP_PASSWORD=...")
    a("python3 content-audit/seo_content_audit.py --live-html priority --thin 1000")
    a("```")
    a("")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description="WordPress technical SEO + content auditor")
    ap.add_argument("--base", default=os.environ.get("WP_BASE", DEFAULT_BASE).rstrip("/"))
    ap.add_argument("--thin", type=int, default=1000)
    ap.add_argument("--live-html", choices=["off", "priority", "all"], default="priority")
    ap.add_argument("--live-sample-grid", type=int, default=25)
    ap.add_argument("--out-dir", default="content-audit/reports/seo-technical")
    ap.add_argument("--limit", type=int, default=0, help="debug: max items per type")
    args = ap.parse_args()

    user = os.environ.get("WP_USER", "").strip()
    password = os.environ.get("WP_APP_PASSWORD", "").strip()
    if not user or not password:
        print("Set WP_USER and WP_APP_PASSWORD in the environment.", file=sys.stderr)
        return 2
    auth = base64.b64encode(f"{user}:{password}".encode()).decode()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching posts/pages/services…", flush=True)
    items: list[tuple[str, dict[str, Any]]] = []
    for route, ptype in (("posts", "post"), ("pages", "page"), ("services", "services")):
        try:
            batch = paginate_wp(args.base, route, auth)
        except urllib.error.HTTPError as e:
            print(f"skip {route}: {e}", flush=True)
            continue
        if args.limit:
            batch = batch[: args.limit]
        print(f"  {ptype}: {len(batch)}", flush=True)
        items.extend((ptype, it) for it in batch)

    print("Building documents…", flush=True)
    docs = [build_doc(it, ptype) for ptype, it in items]

    print("Rank Math link graph…", flush=True)
    rm: dict[int, dict[str, Any]] = {}
    for ptype in ("post", "page", "services"):
        try:
            rm.update(paginate_rankmath(args.base, auth, ptype))
        except Exception as e:
            print(f"  rankmath {ptype}: {e}", flush=True)
    for d in docs:
        row = rm.get(d.id)
        if not row:
            continue
        d.rank_seo_score = str(row.get("seo_score", ""))
        d.rank_orphan = str(row.get("is_orphan", ""))
        d.rank_incoming = str(row.get("incoming_link_count", ""))
        d.rank_internal = str(row.get("internal_link_count", ""))

    print("Flagging issues…", flush=True)
    flag_docs(docs, args.thin)

    if args.live_html != "off":
        targets: list[Doc] = []
        grid = [d for d in docs if d.is_grid]
        other = [d for d in docs if not d.is_grid]
        if args.live_html == "all":
            targets = docs
        else:
            targets = list(other)
            if grid:
                random.Random(42).shuffle(grid)
                targets.extend(grid[: max(0, args.live_sample_grid)])
        print(f"Live HTML fetch: {len(targets)} URLs ({args.live_html})", flush=True)

        def fetch_one(d: Doc) -> tuple[int, int, str, str]:
            st, body, final = request_html(d.url)
            return d.id, st, body, final

        done = 0
        with ThreadPoolExecutor(max_workers=6) as ex:
            futs = [ex.submit(fetch_one, d) for d in targets]
            by_id = {d.id: d for d in docs}
            for fut in as_completed(futs):
                try:
                    did, st, body, final = fut.result()
                    apply_live(by_id[did], st, body, final)
                except Exception as e:
                    print("live err", e, flush=True)
                done += 1
                if done % 25 == 0:
                    print(f"  live {done}/{len(targets)}", flush=True)

    csv_path = out_dir / "seo-audit-all.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for d in sorted(docs, key=lambda x: (0 if x.severity == "حرجة" else 1 if x.severity == "عالية" else 2, x.words)):
            w.writerow(to_row(d))

    # compact issues-only (still all rows, easier filters)
    issues_path = out_dir / "seo-audit-issues.csv"
    with issues_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["title", "url", "word_count", "problem_category", "notes"])
        w.writeheader()
        for d in docs:
            cats = ",".join(d.issues) or "ok"
            w.writerow(
                {
                    "title": d.title,
                    "url": d.url,
                    "word_count": d.words,
                    "problem_category": cats,
                    "notes": " ؛ ".join(d.notes)[:2000],
                }
            )

    md_path = out_dir / "seo-audit-summary.md"
    write_summary(docs, md_path, args.thin, args.live_html, args.base)

    index = {
        "fetched": len(docs),
        "thin": sum(1 for d in docs if d.words < args.thin),
        "grid": sum(1 for d in docs if d.is_grid),
        "intent": sum(1 for d in docs if "intent_mismatch" in d.issues),
        "template": sum(1 for d in docs if "template_boilerplate" in d.issues),
        "csv": str(csv_path),
        "summary": str(md_path),
    }
    (out_dir / "seo-audit-index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(index, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
