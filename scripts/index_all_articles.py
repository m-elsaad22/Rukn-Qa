#!/usr/bin/env python3
"""Publish every draft article on its own URL. Never writes post 2973."""
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

from city_profiles import is_leak_city_slug, slug_suffix
from city_service_articles import build_city_article
from kayan_article_builder import build_article, classify, pack_for, theme_meta

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD")
AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
SITE = "https://www.rukn-eltatawer.com/qa"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorIndexAll/1.0",
    "Content-Type": "application/json",
}
LOCKED = 2973
BATCH = 5
HOUSE = f"{SITE}/house-cleaning-in-qatar/"
COCK = f"{SITE}/cockroach-control-in-qatar/"
MOVE = f"{SITE}/shrkh-nql-athath-fy-qtr/"


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


def push_snippet():
    snippet_path = Path(__file__).with_name("snippet-rukn-qatar.php")
    code = snippet_path.read_text(encoding="utf-8")
    if "delete-post-redirects" not in code or "2973" not in code:
        raise SystemExit("snippet missing index-all routes or ranking lock")
    if "wp_safe_redirect(home_url(RUKN_QA_LEAK)" in code:
        raise SystemExit("snippet still 301s leak city posts")
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
    if "canonical" in kwargs:
        meta["rank_math_canonical_url"] = kwargs["canonical"]
    if not meta:
        return
    return api(
        "/rankmath/v1/updateMeta",
        "POST",
        {"objectType": "post", "objectID": int(pid), "meta": meta},
    )


NATIONAL_EXTRA = {
    "shrkh-tnzyf-mnazl-fy-qtr-2": f"""
<h2>لماذا بقيت هذه الصفحة مستقلة؟</h2>
<p>السلاق العربي «تنظيف منازل» طلب يومي غير صفحة <a href="{HOUSE}">house-cleaning</a> الإنجليزية. هنا البيت المسكون: غبار تكييف، مجلس ضيافة، مطبخ مستخدم، لا شقة تسليم مطوّر ولا شفاط مطعم.</p>
<h2>البيت المسكون لا البيت الفارغ</h2>
<p>الخزائن المغلقة تبقى مغلقة. الأطباق تُرفع أو تُستثنى. غرفة نوم فيها ملابس ظاهرة تُكنس حولها لا تُفرَّغ. إن كان البيت بلا أثاث بعد التشطيب فتلك صفحة أخرى.</p>
<h2>جدول أسبوعي مقابل زيارة عميقة</h2>
<p>زيارة أسبوعية للغبار غير زيارة قبل العيد. نكتب أيهما في العرض حتى لا يُقاس العمل على بيت لم يُستخدم أسبوعاً.</p>
<h2>واتساب هذه الصفحة</h2>
<p>صور المطبخ والمجلس وعدد الغرف. لا سعر فيلا ثابت من كلمة منازل. لا زر اتصال. لا تقييمات مخترعة.</p>
""",
    "shrkh-mkafhh-srasyr-fy-qtr": f"""
<h2>لماذا بقيت هذه الصفحة مستقلة؟</h2>
<p>السلاق العربي لصراصير المطابخ غير صفحة <a href="{COCK}">cockroach-control</a>. هنا مسار تحت الحوض والبيارة في الفلل العربية، لا بق سرير ولا رمّة باب خشب.</p>
<h2>المطبخ أولاً</h2>
<p>نرفع الطعام المكشوف، نضع الطعم في المسار، لا نرش المجلس بدل الحوض. الملحق العمالي بند إن طُلب.</p>
<h2>المتابعة</h2>
<p>البيوض ليست ليلة واحدة. إن اتُفقت زيارة ثانية تُكتب. غسل الطعوم في الصباح يفسد العمل.</p>
<p>واتساب: صور تحت الحوض ووقت الرؤية الليلية. المادة تُشرح قبل الاستخدام.</p>
""",
    "shrkh-nql-athath-fy-qtr": f"""
<h2>نقل أثاث لا تخزين مستودع</h2>
<p>هذه الصفحة لنقل القطع من بيت إلى بيت داخل قطر: فك متفق، تحميل، مسار، تركيب في العنوان الجديد. ليست شراء مستعمل وليست مستودع سنة.</p>
<h2>المبنى يغيّر النقل</h2>
<p>برج لوسيل يحتاج تصريح مصعد. فيلا الريان تحتاج موقف شاحنة في الحوش. الدوحة الضيقة تحتاج وقت تحميل أطول.</p>
<p>واتساب: العنوانان، عدد الغرف، وهل يوجد بيانو أو زجاج كبير.</p>
""",
    "shrkh-nql-afsh-fy-qtr": f"""
<h2>العفش اليومي غير الأثاث الخارجي</h2>
<p>عفش الشقق: خزائن، فرش، أجهزة ظاهرة. الحديقة والجلسات الخارجية صفحة أخرى. التغليف بند يُكتب.</p>
<h2>الجرد قبل الباب</h2>
<p>قائمة غرف تمنع «نسيتم الكرسي». الغرفة المغلقة تُستثنى. المصعد الزجاجي إن مُنع نستخدم الدرج أو نؤجّل.</p>
""",
    "shrkh-tghlyf-athath-fy-qtr": """
<h2>تغليف قبل الطريق</h2>
<p>الكرتون والبطانيات للزجاج والخشب. التغليف وحده بلا نقل بند. النقل مع التغليف بند أوضح.</p>
<h2>ما لا يُغلَّف عشوائياً</h2>
<p>أجهزة بفتحات تهوية، نباتات، مواد خطرة. نكتب الاستثناء. واتساب صور القطع الحساسة.</p>
""",
    "shrkh-fk-wtrkyb-athath-fy-qtr": """
<h2>فك وتركيب في الموقع</h2>
<p>خزائن وغرف نوم تُفك بمساميرها وتُركَّب في العنوان الجديد. ليس نجارة تفصيل جديدة.</p>
<h2>الخشب الرطب</h2>
<p>إن انتفخ الضلف من رطوبة نذكره قبل الفك حتى لا يُفهم التركيب كعيب نقل.</p>
""",
    "interior-furniture-moving-in-qatar": """
<h2>نقل داخلي داخل نفس البيت</h2>
<p>تحريك المجلس من غرفة لغرفة، أو دور إلى دور، دون شاحنة بين مدينتين. الأدراج والجبس يُراعَيان.</p>
""",
    "outdoor-furniture-moving-in-qatar": """
<h2>الأثاث الخارجي</h2>
<p>جلسات الحوش والمظلات والكنب المقاوم للشمس. الرمل والملح يُذكران. ليس عفش غرف النوم.</p>
""",
    "furniture-moving-with-packing-in-qatar": f"""
<h2>نقل مع تغليف مكتوب</h2>
<p>التغليف جزء من العرض لا مفاجأة عند الباب. الزجاج يُغلَّف أولاً. راجع أيضاً <a href="{MOVE}">نقل الأثاث</a> إن كان الفك هو الطلب.</p>
""",
    "shrkh-tkhzyn-athath-fy-qtr": """
<h2>تخزين أثاث بمدة مكتوبة</h2>
<p>حفظ قطع متفق عليها بعد التغليف، لا مستودع مفتوح بلا جرد. المدة والرطوبة تُذكران. ليست شراء مستعمل.</p>
<h2>ما يُخزَّن وما لا يُخزَّن</h2>
<p>خشب وفرش جاف. طعام ونباتات ومواد خطرة خارج النطاق. الجرد عند التسليم والاستلام.</p>
""",
    "shrkh-tkhzyn-bdaya-fy-qtr": """
<h2>تخزين بضائع صغيرة لا هكتار</h2>
<p>كراتين متفق عددها، لا تخزين تجاري لمصنع. المدة تُكتب. الجمارك والشحن الدولي ليسا هذه الصفحة.</p>
""",
    "recruitment-in-qatar": """
<h2>ليست مكتب استقدام عمالة</h2>
<p>ركن التطور للصيانة المنزلية في قطر: كشف، عزل، تنظيف، مكافحة. لا نستقدم خادمات ولا نصدر تأشيرات عمل من هذه الصفحة.</p>
<h2>ماذا نفعل بدل ذلك؟</h2>
<p>إن احتجت تنظيفاً أو صيانة بعد السكن، واتساب بنطاق الغرف. صفحة الاستقدام بقيت مفهرسة حتى لا تُحوَّل إلى مقال آخر.</p>
""",
    "shra-athath-mstaml-fy-qtr": """
<h2>لا نشتري أثاثاً مستعملاً</h2>
<p>لا تقييم كنب للبيع ولا نقل مقابل الأثاث. نفكّ وننقل أثاثك إن طلبت النقل. البق في الأثاث المستعمل صفحة مكافحة لا شراء.</p>
""",
    "shra-mkyfat-mstamlh-fy-qtr": """
<h2>لا نشتري مكيفات مستعملة</h2>
<p>نصيانة وتركيب وحدات بعد المعاينة. الوحدة المستعملة بلا ضمان ليست بند شراء هنا. ضعف التبريد يُشخَّص في صفحة التكييف.</p>
""",
    "shra-ajhzh-khrbayyh-mstamlh-fy-qtr": """
<h2>لا نشتري أجهزة كهربائية مستعملة</h2>
<p>صيانة ثلاجة أو غسالة صفحة الأجهزة. الشراء من السوق المستعمل ليس نشاط هذه الصفحة.</p>
""",
    "shra-skrab-fy-qtr": """
<h2>لا نشتري سكراباً</h2>
<p>الحديد والخردة ليسا نشاط ركن التطور. حدادة الأبواب أو الألومنيوم صيانة منزلية بعد القياس، لا وزن خردة.</p>
""",
    "shra-madat-mtaam-mstamlh-fy-qtr": """
<h2>لا نشتري معدات مطاعم مستعملة</h2>
<p>تنظيف شفاط المطعم وصيانة المداخن خدمة قائمة. شراء القلايات المستعملة ليس نشاطنا. واتساب إن كان الطلب شفاطاً أو دهوناً.</p>
""",
}


def national_html(title: str, slug: str):
    html, desc, _t = build_article(title, slug)
    extra = NATIONAL_EXTRA.get(slug, "")
    if extra:
        stripped = html.rstrip()
        if stripped.endswith("</div>"):
            html = stripped[: -len("</div>")] + extra + "\n</div>"
        else:
            html = stripped + extra
    ptype, pack = pack_for(title, slug)
    meta = theme_meta(title, "قطر", pack, desc)
    return html, desc, meta, ptype


def list_drafts():
    items, page = [], 1
    while True:
        st, data = None, None
        for attempt in range(5):
            st, data = api(
                f"/wp/v2/posts?per_page=100&page={page}&status=draft&context=edit&_fields=id,slug,title"
            )
            if st == 200 and isinstance(data, list):
                break
            time.sleep(6 * (attempt + 1))
        if st != 200 or not data:
            break
        items.extend(data)
        if len(data) < 100:
            break
        page += 1
    return items


def payload_for(p: dict):
    pid = int(p["id"])
    slug = p.get("slug") or ""
    title = unescape((p.get("title") or {}).get("raw") or "")
    if pid == LOCKED:
        raise SystemExit("refusing 2973")
    if slug_suffix(slug) or is_leak_city_slug(slug):
        html, desc, words = build_city_article(title, slug)
        return {
            "id": pid,
            "slug": slug,
            "title": title,
            "content": html,
            "excerpt": desc,
            "description": desc,
            "canonical": f"{SITE}/{slug}/",
            "words": words,
            "kind": "leak-city" if is_leak_city_slug(slug) else "city",
            "ptype": classify(title, slug),
        }
    html, desc, meta, ptype = national_html(title, slug)
    words = len([w for w in html.replace("<", " <").split() if w and not w.startswith("[")])
    return {
        "id": pid,
        "slug": slug,
        "title": title,
        "content": html,
        "excerpt": desc,
        "description": desc,
        "canonical": f"{SITE}/{slug}/",
        "words": words,
        "kind": "national",
        "ptype": ptype,
        "meta": meta,
    }


def bulk_publish(jobs):
    updated = 0
    fails = []
    for i in range(0, len(jobs), BATCH):
        chunk = jobs[i : i + BATCH]
        payload = [
            {k: j[k] for k in ("id", "slug", "title", "content", "excerpt", "description", "canonical")}
            for j in chunk
        ]
        st, out, n = 0, None, 0
        for attempt in range(6):
            st, out = api("/rukn-qa/v1/bulk-publish-posts", "POST", {"items": payload}, timeout=180)
            n = out.get("updated") if isinstance(out, dict) else 0
            if st in (200, 201) and n:
                break
            wait = 8 * (attempt + 1)
            note(f"RETRY {i}-{i+len(chunk)} http={st} sleep={wait}s {str(out)[:120]}")
            time.sleep(wait)
            if len(payload) > 1:
                payload = payload[: max(1, len(payload) // 2)]
        updated += int(n or 0)
        if st not in (200, 201) or not n:
            fails.append({"http": st, "out": str(out)[:300], "ids": [j["id"] for j in chunk]})
            note(f"BATCH FAIL {i}-{i+len(chunk)} http={st} {str(out)[:180]}")
        elif (i // BATCH) % 8 == 0:
            note(f"published {updated}/{len(jobs)} last={chunk[-1]['slug']}")
        for j in chunk:
            if j["id"] != LOCKED:
                rm_meta(
                    j["id"],
                    title=j["title"],
                    description=j["description"],
                    keyword=j["title"],
                    robots=["index", "follow"],
                    canonical=j["canonical"],
                )
        time.sleep(0.35)
    return updated, fails


def assert_classifier():
    cases = [
        ("شركة كشف تسربات المياه في قطر", "water-leak-detection-company-in-qatar", "general"),
        ("شركة كشف تسربات المياه في الدوحة", "water-leak-detection-doha", "leak_water"),
        ("شركة كشف تسريبات مواسير مياه في الريان", "water-pipe-leak-detection-al-rayyan", "leak_pipe"),
        ("شركة تنظيف منازل في قطر", "house-cleaning-in-qatar", "cleaning"),
        ("شركة مكافحة الصراصير في قطر", "cockroach-control-in-qatar", "pest_cockroach"),
    ]
    for title, slug, expect in cases:
        got = classify(title, slug)
        note(f"classify {slug} -> {got} (expect {expect})")
        if got != expect:
            raise SystemExit(f"classifier mismatch {slug}: {got} != {expect}")


def main():
    lockcheck()
    assert_classifier()
    push_snippet()
    lockcheck()
    st, cleared = api("/rukn-qa/v1/delete-post-redirects", "POST", {})
    note(f"DEL-REDIRECTS {st} {json.dumps(cleared, ensure_ascii=False)[:500] if isinstance(cleared, dict) else cleared}")
    drafts = list_drafts()
    note(f"drafts {len(drafts)}")
    jobs, skipped = [], []
    for p in drafts:
        try:
            jobs.append(payload_for(p))
        except Exception as e:
            skipped.append({"id": p.get("id"), "slug": p.get("slug"), "reason": str(e)})
    note(f"jobs={len(jobs)} skipped={len(skipped)}")
    updated, fails = bulk_publish(jobs)
    st, purged = api("/rukn-qa/v1/purge-cache", "POST", {})
    note(f"PURGE {st} {purged}")
    lockcheck()
    leftover = list_drafts()
    summary = {
        "locked": 2973,
        "drafts_seen": len(drafts),
        "jobs": len(jobs),
        "updated": updated,
        "fails": fails,
        "skipped": skipped[:40],
        "drafts_left": len(leftover),
        "kinds": {
            "city": sum(1 for j in jobs if j["kind"] == "city"),
            "leak-city": sum(1 for j in jobs if j["kind"] == "leak-city"),
            "national": sum(1 for j in jobs if j["kind"] == "national"),
        },
        "redirects_deleted": cleared.get("deleted") if isinstance(cleared, dict) else None,
    }
    out = Path(__file__).resolve().parents[1] / "audit" / "index-all-articles.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note(json.dumps({k: summary[k] for k in ("updated", "jobs", "drafts_left", "kinds", "redirects_deleted")}, ensure_ascii=False))
    note("DONE index_all_articles")


if __name__ == "__main__":
    main()
