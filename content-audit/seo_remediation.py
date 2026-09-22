#!/usr/bin/env python3
"""
Rukn Qatar SEO remediation engine (WordPress REST).

Implements the four post-audit fixes. DEFAULT IS DRY-RUN (GET + plan files only).
Nothing is written until you pass --apply after reviewing the plan.

  1. Draft out-of-scope posts (recruitment / scrap / used) and thin cannibalizing
     `services` CPT items.
  2. Fix pillar HTML: downgrade in-body <h1> → <h2>, unwrap href="tel:…".
  3. Append an idempotent internal-link mesh to city×service posts (grouped in
     memory so we fetch the catalog once, then PUT each post).
  4. Architecture only: select top 15 national pillars and build LLM rewrite
     prompts. Does NOT call OpenAI/Gemini unless --execute-llm (still off).

Credentials (never commit):

  WP_BASE_URL or WP_BASE
  WP_USERNAME or WP_USER
  WP_APP_PASSWORD

    python3 content-audit/seo_remediation.py --dry-run --tasks 1,2,3,4
    python3 content-audit/seo_remediation.py --apply --tasks 1,2
    python3 content-audit/seo_remediation.py --apply --tasks 3 --resume

Post #2973 (leak pillar) is frozen by Code Snippet 5 (`wp_insert_post_data`).
Task 2 verifies after PUT; if the H1/tel still remain, the run records
BLOCKED_BY_SNIPPET5 instead of pretending it succeeded.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import logging
import os
import random
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

LOG = logging.getLogger("rukn.seo")

DEFAULT_BASE = "https://www.rukn-eltatawer.com/qa"
UA = "RuknSeoRemediation/1.0"
MESH_ID = "rukn-internal-mesh"
MESH_START = f'<!-- {MESH_ID}:start -->'
MESH_END = f'<!-- {MESH_ID}:end -->'
LOCKED_PILLAR_ID = 2973

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
]
CITY_AR = {
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
PILLAR_SLUGS = [
    "water-leak-detection-company-in-qatar",
    "shrkh-mkafhh-srasyr-fy-qtr",
    "shrkh-tnzyf-mnazl-fy-qtr-2",
]
OOS_TITLE_SLUG = [
    "استقدام",
    "سكراب",
    "مستعمل",
    "recruitment",
    "scrap",
    "mstaml",
    "skrab",
    "used-furniture",
    "used_furniture",
]
# CPT items that steal queries from a national post and are too thin to keep live.
CPT_CANNIBAL = {
    "water-leak-detection": "water-leak-detection-company-in-qatar",
    "sound-insulation-installation": "shrkh-azl-swty-fy-qtr",
}

# National home-service stems we prefer when picking the LLM-15.
NATIONAL_PRIORITY = [
    "water-leak-detection-company-in-qatar",
    "shrkh-mkafhh-srasyr-fy-qtr",
    "shrkh-tnzyf-mnazl-fy-qtr-2",
    "shrkh-azl-asth-fy-qtr",
    "central-air-conditioning-maintenance-in-qatar",
    "shrkh-azl-swty-fy-qtr",
    "home-plumber-in-qatar",
    "shrkh-maaljh-alrtwbh-fy-qtr",
    "split-ac-maintenance-in-qatar",
    "shrkh-azl-khzanat-fy-qtr",
    "cockroach-control-in-qatar",
    "house-cleaning-in-qatar",
    "sewerage-company-in-qatar",
    "pest-control-in-qatar",
    "shrkh-dhanat-dakhlyh-fy-qtr",
]


# ---------------------------------------------------------------------------
# Env / HTTP
# ---------------------------------------------------------------------------


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip("'").strip('"')
        os.environ.setdefault(key, val)


def creds() -> tuple[str, str]:
    for candidate in (
        Path.cwd() / ".env",
        Path("/workspace/.env"),
        Path(__file__).resolve().parent.parent / ".env",
    ):
        load_dotenv(candidate)
    base = (os.environ.get("WP_BASE_URL") or os.environ.get("WP_BASE") or DEFAULT_BASE).rstrip("/")
    user = (os.environ.get("WP_USERNAME") or os.environ.get("WP_USER") or "").strip()
    password = (os.environ.get("WP_APP_PASSWORD") or "").strip()
    if not user or not password:
        raise SystemExit("Missing WP_USERNAME/WP_USER or WP_APP_PASSWORD (.env or environment).")
    return base, user + ":" + password


def _ssl() -> ssl.SSLContext:
    return ssl.create_default_context()


class RateLimiter:
    def __init__(self, min_interval: float) -> None:
        self.min_interval = max(0.0, min_interval)
        self._last = 0.0

    def wait(self) -> None:
        if self.min_interval <= 0:
            return
        gap = self.min_interval - (time.monotonic() - self._last)
        if gap > 0:
            time.sleep(gap)
        self._last = time.monotonic()


class WpClient:
    def __init__(self, base: str, basic: str, min_interval: float = 0.2) -> None:
        self.base = base.rstrip("/")
        self.auth = base64.b64encode(basic.encode()).decode()
        self.writes = RateLimiter(min_interval)
        self.reads = RateLimiter(min(0.05, min_interval / 2))

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Basic {self.auth}",
            "User-Agent": UA,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None, timeout: int = 90) -> tuple[int, Any]:
        url = path if path.startswith("http") else self.base + path
        data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        limiter = self.writes if method in {"POST", "PUT", "PATCH", "DELETE"} else self.reads
        last_err: Exception | None = None
        for attempt in range(6):
            limiter.wait()
            req = urllib.request.Request(url, data=data, method=method, headers=self._headers())
            try:
                with urllib.request.urlopen(req, timeout=timeout, context=_ssl()) as resp:
                    raw = resp.read().decode("utf-8", "replace")
                    body: Any = json.loads(raw) if raw else {}
                    return resp.status, body
            except urllib.error.HTTPError as e:
                raw = e.read().decode("utf-8", "replace") if e.fp else ""
                if e.code in {429, 502, 503} and attempt < 5:
                    LOG.warning("HTTP %s on %s %s — retry %s", e.code, method, path, attempt + 1)
                    time.sleep(2 + attempt * 3)
                    last_err = e
                    continue
                try:
                    err_body = json.loads(raw) if raw else {"message": e.reason}
                except json.JSONDecodeError:
                    err_body = {"message": raw or e.reason}
                return e.code, err_body
            except Exception as e:
                last_err = e
                time.sleep(1 + attempt)
        raise RuntimeError(last_err)

    def paginate(self, route: str, extra: str = "") -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        page = 1
        while True:
            q = (
                f"/wp-json/wp/v2/{route}?context=edit&status=publish&per_page=100"
                f"&page={page}&_fields=id,slug,link,title,content,excerpt,type,status{extra}"
            )
            code, body = self.request("GET", q)
            if code == 400 and page > 1:
                break
            if code >= 400:
                raise RuntimeError(f"GET {route} page {page} failed: {code} {body}")
            if not body:
                break
            out.extend(body)
            if len(body) < 100:
                break
            page += 1
        return out

    def put_post(self, ptype: str, post_id: int, payload: dict[str, Any]) -> tuple[int, Any]:
        route = "posts" if ptype == "post" else ptype
        path = f"/wp-json/wp/v2/{route}/{post_id}"
        code, body = self.request("PUT", path, payload)
        if code == 405:
            LOG.info("PUT not allowed on %s — falling back to POST (WP REST)", path)
            code, body = self.request("POST", path, payload)
        return code, body


# ---------------------------------------------------------------------------
# Text / city helpers
# ---------------------------------------------------------------------------


class _Text(HTMLParser):
    SKIP = {"script", "style", "noscript"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.SKIP:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def visible_text(html: str) -> str:
    p = _Text()
    try:
        p.feed(html or "")
        p.close()
    except Exception:
        pass
    return re.sub(r"\s+", " ", " ".join(p.parts)).strip()


def word_count(html: str) -> int:
    toks = re.findall(r"[A-Za-z0-9\u0600-\u06FF]+", visible_text(html))
    return len([t for t in toks if len(t) > 1 or t.isdigit()])


def rendered_or_raw(block: Any) -> tuple[str, str]:
    if not isinstance(block, dict):
        s = str(block or "")
        return s, s
    return block.get("raw") or "", block.get("rendered") or ""


def title_of(item: dict[str, Any]) -> str:
    t = item.get("title")
    if isinstance(t, dict):
        return re.sub(r"<[^>]+>", "", t.get("raw") or t.get("rendered") or "").strip()
    return str(t or "")


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
    return re.sub(r"-in-qatar$|-qatar$|-fy-qtr$", "", s)


def service_label(title: str, city: str) -> str:
    t = title
    ar = CITY_AR.get(city, "")
    for w in (ar, f"في {ar}", f"ب{ar}", "بالدوحة", "قطر", "شركة"):
        if w:
            t = t.replace(w, " ")
    t = re.sub(r"\s+", " ", t).strip(" —-|")
    return t or title


def is_oos(title: str, slug: str) -> bool:
    blob = f"{title} {slug}".lower()
    title_l = title
    for term in OOS_TITLE_SLUG:
        if term.lower() in blob or term in title_l:
            return True
    return False


def strip_mesh(html: str) -> str:
    html = html or ""
    html = re.sub(
        re.escape(MESH_START) + r".*?" + re.escape(MESH_END),
        "",
        html,
        flags=re.S,
    )
    html = re.sub(
        r'<nav[^>]*id="' + re.escape(MESH_ID) + r'"[^>]*>.*?</nav>',
        "",
        html,
        flags=re.S | re.I,
    )
    return html.rstrip() + "\n"


def downgrade_h1(html: str) -> tuple[str, int]:
    n = len(re.findall(r"</?h1\b", html or "", flags=re.I))
    out = re.sub(r"<h1(\s[^>]*)?>", r"<h2\1>", html or "", flags=re.I)
    out = re.sub(r"</h1>", "</h2>", out, flags=re.I)
    return out, n // 2 if n else 0


def unwrap_tel(html: str) -> tuple[str, int]:
    count = [0]

    def repl(m: re.Match[str]) -> str:
        count[0] += 1
        return m.group(1)

    out = re.sub(
        r'<a\b[^>]*href=["\']tel:[^"\']*["\'][^>]*>(.*?)</a>',
        repl,
        html or "",
        flags=re.I | re.S,
    )
    # leftover empty tel anchors
    out2, n2 = re.subn(r'<a\b[^>]*href=["\']tel:[^"\']*["\'][^>]*>\s*</a>', "", out, flags=re.I)
    return out2, count[0] + n2


def mesh_html(city: str, label: str, city_links: list[tuple[str, str]], service_links: list[tuple[str, str]]) -> str:
    city_ar = CITY_AR.get(city, city)
    def lis(pairs: list[tuple[str, str]], icon: str) -> str:
        items = []
        for href, txt in pairs:
            items.append(
                f'<li><i class="fas {icon}" aria-hidden="true"></i> '
                f'<a href="{href}">{txt}</a></li>'
            )
        return "\n".join(items) if items else "<li>لا روابط إضافية</li>"

    return f"""{MESH_START}
<nav class="rukn-internal-mesh" id="{MESH_ID}" aria-label="روابط داخلية ذات صلة">
  <div class="rukn-mesh-block">
    <h2><i class="fas fa-map-marker-alt" aria-hidden="true"></i> خدمات أخرى في {city_ar}</h2>
    <ul>
{lis(city_links, "fa-wrench")}
    </ul>
  </div>
  <div class="rukn-mesh-block">
    <h2><i class="fas fa-city" aria-hidden="true"></i> {label} في مدن أخرى</h2>
    <ul>
{lis(service_links, "fa-location-arrow")}
    </ul>
  </div>
</nav>
{MESH_END}
"""


def pick_n(rows: list[Any], n: int, seed: str) -> list[Any]:
    if len(rows) <= n:
        return list(rows)
    rng = random.Random(hashlib.md5(seed.encode("utf-8")).hexdigest())
    clone = list(rows)
    rng.shuffle(clone)
    return clone[:n]


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


@dataclass
class Action:
    task: str
    method: str
    type: str
    id: int
    slug: str
    url: str
    reason: str
    payload: dict[str, Any] = field(default_factory=dict)
    result: str = "planned"


def catalog(wp: WpClient) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    LOG.info("Fetching published posts (context=edit)…")
    posts = wp.paginate("posts")
    LOG.info("  posts=%s", len(posts))
    LOG.info("Fetching published services CPT…")
    try:
        services = wp.paginate("services")
    except RuntimeError as e:
        LOG.warning("services CPT: %s", e)
        services = []
    LOG.info("  services=%s", len(services))
    return posts, services


def task1_draft(posts: list[dict[str, Any]], services: list[dict[str, Any]], cpt_thin: int) -> list[Action]:
    actions: list[Action] = []
    for p in posts:
        title, slug = title_of(p), p.get("slug") or ""
        if is_oos(title, slug):
            actions.append(
                Action(
                    "1_oos",
                    "PUT",
                    "post",
                    int(p["id"]),
                    slug,
                    p.get("link") or "",
                    f"out-of-scope term in title/slug ({title})",
                    {"status": "draft"},
                )
            )
    for s in services:
        raw, rend = rendered_or_raw(s.get("content"))
        words = word_count(raw or rend)
        slug = s.get("slug") or ""
        thin = words <= cpt_thin
        cannibal = slug in CPT_CANNIBAL
        if thin and cannibal or (thin and words < 80):
            reason = f"thin CPT ({words} words)"
            if cannibal:
                reason += f" cannibalizes /{CPT_CANNIBAL[slug]}/"
            actions.append(
                Action(
                    "1_cpt",
                    "PUT",
                    "services",
                    int(s["id"]),
                    slug,
                    s.get("link") or "",
                    reason,
                    {"status": "draft"},
                )
            )
        elif cannibal and words < 400:
            actions.append(
                Action(
                    "1_cpt",
                    "PUT",
                    "services",
                    int(s["id"]),
                    slug,
                    s.get("link") or "",
                    f"CPT cannibal ({words} words) vs national pillar",
                    {"status": "draft"},
                )
            )
    return actions


def task2_pillars(posts: list[dict[str, Any]]) -> list[Action]:
    by_slug = {p.get("slug"): p for p in posts}
    actions: list[Action] = []
    for slug in PILLAR_SLUGS:
        p = by_slug.get(slug)
        if not p:
            LOG.error("Pillar missing: %s", slug)
            continue
        raw, rend = rendered_or_raw(p.get("content"))
        html = raw or rend
        html2, n_h1 = downgrade_h1(html)
        html3, n_tel = unwrap_tel(html2)
        if html3 == html:
            LOG.info("Pillar %s already clean (h1=%s tel=%s)", slug, n_h1, n_tel)
            continue
        actions.append(
            Action(
                "2_pillar",
                "PUT",
                "post",
                int(p["id"]),
                slug,
                p.get("link") or "",
                f"downgrade {n_h1} H1, unwrap {n_tel} tel: links"
                + (" [LOCKED #2973]" if int(p["id"]) == LOCKED_PILLAR_ID else ""),
                {"content": html3},
            )
        )
    return actions


def task3_mesh(posts: list[dict[str, Any]], per_list: int) -> list[Action]:
    city_posts: list[dict[str, Any]] = []
    for p in posts:
        slug = p.get("slug") or ""
        city = city_from_slug(slug)
        if not city:
            continue
        if is_oos(title_of(p), slug):
            continue
        p["_city"] = city
        p["_stem"] = service_stem(slug)
        p["_label"] = service_label(title_of(p), city)
        p["_raw"], p["_rend"] = rendered_or_raw(p.get("content"))
        city_posts.append(p)

    by_city: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_stem: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for p in city_posts:
        by_city[p["_city"]].append(p)
        by_stem[p["_stem"]].append(p)

    LOG.info("City×service catalog: %s posts, %s cities, %s stems", len(city_posts), len(by_city), len(by_stem))
    actions: list[Action] = []
    for p in city_posts:
        city, stem = p["_city"], p["_stem"]
        others_city = [x for x in by_city[city] if x["id"] != p["id"]]
        others_svc = [x for x in by_stem[stem] if x["_city"] != city]
        city_links = [
            (x.get("link") or "", x.get("_label") or title_of(x))
            for x in pick_n(others_city, per_list, f"c{p['id']}")
        ]
        svc_links = [
            (x.get("link") or "", f"{p['_label']} في {CITY_AR.get(x['_city'], x['_city'])}")
            for x in pick_n(others_svc, per_list, f"s{p['id']}")
        ]
        block = mesh_html(city, p["_label"], city_links, svc_links)
        base = strip_mesh(p["_raw"] or p["_rend"])
        new_html = base + "\n" + block
        if (p["_raw"] or p["_rend"]).strip() == new_html.strip():
            continue
        actions.append(
            Action(
                "3_mesh",
                "PUT",
                "post",
                int(p["id"]),
                p.get("slug") or "",
                p.get("link") or "",
                f"mesh {len(city_links)} city-peers + {len(svc_links)} city-variants",
                {"content": new_html},
            )
        )
    return actions


def task4_llm_prep(posts: list[dict[str, Any]], out_dir: Path) -> list[dict[str, Any]]:
    """Select 15 national pages and write prompt packets. No LLM HTTP."""
    nationals = []
    for p in posts:
        slug = p.get("slug") or ""
        if city_from_slug(slug):
            continue
        if is_oos(title_of(p), slug):
            continue
        if slug.endswith("-en") or "/en/" in (p.get("link") or ""):
            continue
        raw, rend = rendered_or_raw(p.get("content"))
        nationals.append(
            {
                "id": int(p["id"]),
                "slug": slug,
                "url": p.get("link") or "",
                "title": title_of(p),
                "words": word_count(raw or rend),
            }
        )
    by_slug = {n["slug"]: n for n in nationals}
    chosen: list[dict[str, Any]] = []
    for slug in NATIONAL_PRIORITY:
        if slug in by_slug and by_slug[slug] not in chosen:
            chosen.append(by_slug[slug])
        if len(chosen) >= 15:
            break
    rest = sorted((n for n in nationals if n not in chosen), key=lambda x: -x["words"])
    for n in rest:
        if len(chosen) >= 15:
            break
        chosen.append(n)

    packets = []
    for n in chosen[:15]:
        packets.append(
            {
                "id": n["id"],
                "slug": n["slug"],
                "url": n["url"],
                "title": n["title"],
                "current_words": n["words"],
                "target_words": 1200,
                "locale": "ar-QA",
                "system": (
                    "You are a Qatari home-services copywriter. Write original Arabic for Doha/Lusail/"
                    "Al Rayyan building stock (Kahramaa bills, summer heat, villas vs towers). "
                    "No lorem, no 24/7 guarantees, no Qatar phone numbers, WhatsApp-only CTA, no H1 in body."
                ),
                "user": (
                    f"Rewrite and expand this national service page to 1200+ words.\n"
                    f"Title: {n['title']}\nURL: {n['url']}\n"
                    "Cover: when to call, inspection method, what not to do, local coverage, FAQ. "
                    "Link up to the city-grid URLs for the same service when relevant. "
                    "Return HTML fragments (h2/h3/p/ul) only."
                ),
                "provider": os.environ.get("LLM_PROVIDER", "openai"),
                "model": os.environ.get("LLM_MODEL", "gpt-4.1"),
                "execute": False,
            }
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "task4-llm-packets.json"
    path.write_text(json.dumps(packets, ensure_ascii=False, indent=2), encoding="utf-8")
    LOG.info("Task 4: wrote %s national packets to %s (LLM not called)", len(packets), path)
    return packets


class LLMExpander:
    """Stub. Wire OpenAI/Gemini later; never called unless --execute-llm."""

    def __init__(self) -> None:
        self.provider = os.environ.get("LLM_PROVIDER", "openai")
        self.model = os.environ.get("LLM_MODEL", "gpt-4.1")
        self.api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""

    def expand(self, packet: dict[str, Any]) -> str:
        raise RuntimeError(
            f"LLM execution disabled. Provider={self.provider} model={self.model} "
            "key_set=" + str(bool(self.api_key)) + ". Pass --execute-llm after review."
        )


def apply_actions(wp: WpClient, actions: list[Action], resume_after: int, apply: bool) -> list[Action]:
    done = 0
    for act in actions:
        if act.id <= resume_after and act.task == "3_mesh":
            act.result = "skipped_resume"
            continue
        # Never touch Code Snippet 5 / never PUT the frozen leak pillar.
        if act.id == LOCKED_PILLAR_ID:
            act.result = "BLOCKED_BY_SNIPPET5"
            LOG.warning("Skip PUT #%s %s — BLOCKED_BY_SNIPPET5 (snippet 5 untouched)", act.id, act.slug)
            continue
        if not apply:
            act.result = "dry-run"
            continue
        code, body = wp.put_post(act.type, act.id, act.payload)
        if code >= 400:
            msg = body.get("message", body) if isinstance(body, dict) else body
            act.result = f"HTTP_{code}:{msg}"
            LOG.error("FAIL %s %s #%s %s", act.task, act.slug, act.id, act.result)
            continue
        act.result = f"ok_{code}"
        done += 1
        if done % 25 == 0:
            LOG.info("applied %s/%s (last id=%s)", done, len(actions), act.id)
    return actions


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def setup_log(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    LOG.handlers.clear()
    LOG.addHandler(sh)
    fh = logging.FileHandler(out_dir / "seo-remediation.log", encoding="utf-8")
    fh.setFormatter(fmt)
    LOG.addHandler(fh)


def main() -> int:
    ap = argparse.ArgumentParser(description="Rukn Qatar SEO remediation (dry-run by default)")
    ap.add_argument("--apply", action="store_true", help="Write via PUT. Omit for plan-only.")
    ap.add_argument("--dry-run", action="store_true", default=False, help="Force plan-only (default if --apply absent).")
    ap.add_argument("--tasks", default="1,2,3,4", help="Comma list: 1,2,3,4")
    ap.add_argument("--cpt-thin", type=int, default=150, help="Draft services CPT at or below this word count if cannibalizing")
    ap.add_argument("--mesh-links", type=int, default=5, help="Links per mesh list (3–5 recommended)")
    ap.add_argument("--min-interval", type=float, default=0.25, help="Seconds between write requests")
    ap.add_argument("--resume-after", type=int, default=0, help="Task 3: skip post IDs <= this")
    ap.add_argument("--execute-llm", action="store_true", help="Actually call the LLM (default: architecture only)")
    ap.add_argument("--out-dir", default="content-audit/reports/seo-remediation")
    ap.add_argument("--limit-mesh", type=int, default=0, help="Debug: max Task 3 updates")
    args = ap.parse_args()
    apply = bool(args.apply) and not args.dry_run
    tasks = {t.strip() for t in args.tasks.split(",") if t.strip()}

    out_dir = Path(args.out_dir)
    setup_log(out_dir)

    if apply:
        LOG.warning("APPLY MODE — writes enabled")
    else:
        LOG.info("DRY-RUN — no PUT will be sent. Review the plan JSON, then re-run with --apply.")

    base, basic = creds()
    wp = WpClient(base, basic, min_interval=args.min_interval)
    posts, services = catalog(wp)

    actions: list[Action] = []
    packets: list[dict[str, Any]] = []
    if "1" in tasks:
        t1 = task1_draft(posts, services, args.cpt_thin)
        LOG.info("Task 1 planned: %s drafts", len(t1))
        actions.extend(t1)
    if "2" in tasks:
        t2 = task2_pillars(posts)
        LOG.info("Task 2 planned: %s pillar updates", len(t2))
        actions.extend(t2)
    if "3" in tasks:
        t3 = task3_mesh(posts, max(3, min(5, args.mesh_links)))
        if args.limit_mesh:
            t3 = t3[: args.limit_mesh]
        LOG.info("Task 3 planned: %s mesh updates", len(t3))
        actions.extend(t3)
    if "4" in tasks:
        packets = task4_llm_prep(posts, out_dir)
        if args.execute_llm:
            expander = LLMExpander()
            expander.expand(packets[0] if packets else {})

    apply_actions(wp, actions, args.resume_after, apply)

    plan = {
        "mode": "apply" if apply else "dry-run",
        "base": base,
        "counts": {
            "task1": sum(1 for a in actions if a.task.startswith("1_")),
            "task2": sum(1 for a in actions if a.task == "2_pillar"),
            "task3": sum(1 for a in actions if a.task == "3_mesh"),
            "task4_packets": len(packets),
            "ok": sum(1 for a in actions if str(a.result).startswith("ok")),
            "failed": sum(1 for a in actions if str(a.result).startswith("HTTP") or a.result == "BLOCKED_BY_SNIPPET5"),
        },
        "actions": [
            {k: v for k, v in asdict(a).items() if k != "payload" or a.task != "3_mesh"}
            for a in actions
        ],
    }
    # Task 3 payloads are huge; keep one sample mesh for review.
    sample = next((a for a in actions if a.task == "3_mesh"), None)
    if sample:
        plan["mesh_sample"] = {
            "id": sample.id,
            "slug": sample.slug,
            "html_tail": (sample.payload.get("content") or "")[-1800:],
        }
    plan_path = out_dir / "plan.json"
    # Strip full HTML from task3 rows already done; for task2 keep payload
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    csv_lines = ["task,id,type,slug,url,reason,result"]
    for a in actions:
        csv_lines.append(
            ",".join(
                json.dumps(x, ensure_ascii=False)
                for x in (a.task, a.id, a.type, a.slug, a.url, a.reason, a.result)
            )
        )
    (out_dir / "actions.csv").write_text("\n".join(csv_lines) + "\n", encoding="utf-8")
    LOG.info("Plan written to %s (%s actions)", plan_path, len(actions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
