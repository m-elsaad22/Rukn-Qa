#!/usr/bin/env python3
"""Continue Qatar site fixes without touching ranking post 2973."""
from __future__ import annotations

import base64
import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD in the environment.")
AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorFix/1.0",
    "Content-Type": "application/json",
}
PHONE = ""
PHONE_HUMAN = ""
WA = "971586634710"
LEAK_URL = "https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/"
LOCKED = 2973
LEAK_CLONES = [
    (11132, "water-leak-detection-doha"),
    (11133, "water-leak-detection-al-rayyan"),
    (11134, "water-leak-detection-al-wakrah"),
    (11135, "water-leak-detection-al-khor"),
    (11136, "water-leak-detection-umm-salal"),
    (11137, "water-leak-detection-al-shamal"),
    (11138, "water-leak-detection-al-daayen"),
    (11139, "water-leak-detection-al-shahaniya"),
    (12693, "water-pipe-leak-detection-doha"),
    (12694, "water-pipe-leak-detection-al-rayyan"),
    (12695, "water-pipe-leak-detection-al-wakrah"),
    (12696, "water-pipe-leak-detection-al-khor"),
    (12697, "water-pipe-leak-detection-umm-salal"),
    (12698, "water-pipe-leak-detection-al-shamal"),
    (12699, "water-pipe-leak-detection-al-daayen"),
    (12700, "water-pipe-leak-detection-al-shahaniya"),
]


def api(path, method="GET", data=None, timeout=90):
    url = path if path.startswith("http") else BASE + path
    body = None if data is None else json.dumps(data).encode()
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


def note(msg):
    print(msg, flush=True)


def assert_2973_untouched():
    code, p = api(f"/wp/v2/posts/{LOCKED}?context=edit&_fields=id,slug,status,title")
    title = unescape((p.get("title") or {}).get("raw") or "")
    ok = (
        code == 200
        and p.get("id") == LOCKED
        and p.get("slug") == "water-leak-detection-company-in-qatar"
        and p.get("status") == "publish"
        and title == "شركة كشف تسربات المياه في قطر"
    )
    note(f"LOCKCHECK 2973 {code} slug={p.get('slug') if isinstance(p, dict) else p} title={title!r} ok={ok}")
    if not ok:
        raise SystemExit("Ranking post 2973 changed — aborting")


def rm_meta(post_id, **kwargs):
    if int(post_id) == LOCKED:
        note(f"SKIP locked SEO {post_id}")
        return
    meta = {}
    if kwargs.get("title"):
        meta["rank_math_title"] = kwargs["title"]
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
    api("/rankmath/v1/updateMeta", "POST", {"objectType": kwargs.get("object_type", "post"), "objectID": int(post_id), "meta": meta})


def cta():
    return (
        f'<p><a href="https://wa.me/{WA}?text={urllib.parse.quote("مرحباً، أريد الاستفسار عن خدمات ركن التطور في قطر")}">واتساب</a></p>'
    )


CITY_HUBS = [
    (
        "services-in-doha-qatar",
        "خدمات ركن التطور في الدوحة",
        "الدوحة",
        "<p>الدوحة مقر ركن التطور: الخليج الغربي، اللؤلؤة، مشيرب، لقطيفية، الثمامة، الدفنة، السد وعين خالد. الطلب الشائع هنا مزيج أبراج وشقق وفلل.</p>",
        "<li>فلل السد وعين خالد: مواسير الحوش والخزان الأرضي.</li><li>أبراج الخليج الغربي واللؤلؤة: دكتات التكييف والرطوبة الداخلية.</li><li>مشيرب ولقطيفية: تنسيق مع إدارة المبنى قبل الفتح الموضعي.</li>",
    ),
    (
        "services-in-al-rayyan-qatar",
        "خدمات ركن التطور في الريان",
        "الريان",
        "<p>الريان فلل وحوش أكثر من أبراج: الوعب، الغرافة، معيذر، السيلية وأبو هامور. العزل والأسطح والتسرب تحت البلاط طلبات متكررة.</p>",
        "<li>حوش الفيلا والخزان الأرضي بعد الصيف.</li><li>عزل الأسطح فوق الغرف العلوية.</li><li>رمّة ورطوبة الخشب في الملاحق.</li>",
    ),
    (
        "services-in-al-wakrah-qatar",
        "خدمات ركن التطور في الوكرة",
        "الوكرة",
        "<p>الوكرة والوكير والمشاف مناخ ساحلي: الرطوبة تخفي التسرب خلف العزل القديم وتسرّع تآكل الدهان.</p>",
        "<li>رطوبة ساحلية على الجدران والعزل.</li><li>خزانات أرضية ومضخات.</li><li>تكييف سبليت في الفلل أكثر من المركزي.</li>",
    ),
    (
        "services-in-al-khor-qatar",
        "خدمات ركن التطور في الخور",
        "الخور",
        "<p>الخور والذخيرة وسميسما: وصول من الدوحة بالتنسيق. الفلل الساحلية والرطوبة هما الغالب.</p>",
        "<li>زمن الزيارة يُذكر بعد العنوان.</li><li>خزانات ومضخات في الفلل المنفصلة.</li><li>عزل أسطح معرضة للحرارة والملح.</li>",
    ),
    (
        "services-in-umm-salal-qatar",
        "خدمات ركن التطور في أم صلال والخيسة",
        "أم صلال",
        "<p>أم صلال محمد وأم صلال علي والخيسة: فلل ومزارع سكنية. نصل بالتنسيق المسبق من الدوحة.</p>",
        "<li>خزانات أرضية وري مخفي.</li><li>عزل أسطح مساحات أكبر.</li><li>تسليك وتسرب تحت بلاط الحوش.</li>",
    ),
    (
        "services-in-al-daayen-qatar",
        "خدمات ركن التطور في الظعاين",
        "الظعاين",
        "<p>الظعاين وأم قرن ولوسيل الشمالية: توسع عمراني بين الفلل والمجمعات الجديدة.</p>",
        "<li>تشطيب جديد يحتاج فحص ضغط قبل السكن.</li><li>قرب لوسيل يعني تكييف مركزي في بعض المجمعات.</li><li>عزل الأسطح بعد أول صيف.</li>",
    ),
    (
        "services-in-al-shamal-qatar",
        "خدمات ركن التطور في الشمال",
        "الشمال",
        "<p>الرويس والشمال: أبعد تغطية شمالية. الزيارة تُجدول مسبقاً وليست فورية في نفس الساعة.</p>",
        "<li>نوضح زمن الوصول في الموعد.</li><li>خزانات وفلل منفصلة.</li><li>عزل يناسب الحرارة والرياح.</li>",
    ),
    (
        "services-in-al-shahaniya-qatar",
        "خدمات ركن التطور في الشحانية",
        "الشحانية",
        "<p>الشحانية والوجبة وغرب الريان: فلل ومساحات مفتوحة. التصحيح: الشحانية لا «المشحمية».</p>",
        "<li>أسطح واسعة وعزل حراري.</li><li>حدائق وري مع حرارة عالية.</li><li>كشف تسرب الحوش بعد هبوط البلاط.</li>",
    ),
]


def hub_html(title, city, intro, bullets):
    return f"""
{intro}
<p>لكشف تسربات المياه على مستوى قطر — بما فيها {city} — راجع المقال الرئيسي دون نسخة مكررة لكل مدينة:
<a href="{LEAK_URL}">شركة كشف تسربات المياه في قطر</a>.</p>
<h2>ما الذي يختلف في {city}؟</h2>
<ul>
{bullets}
</ul>
<h2>خدمات أخرى نصل بها إلى {city}</h2>
<ul>
<li><a href="https://www.rukn-eltatawer.com/qa/shrkh-azl-asth-fy-qtr/">عزل الأسطح</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/services/">صيانة وتكييف وتنظيف</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/cities/">باقي المدن</a></li>
</ul>
<p>المعاينة في الموقع ثم عرض سعر مكتوب. لا سعر نهائي عبر رسالة دون فهم الحالة.</p>
{cta()}
"""


def pricing_html():
    return f"""
<p>أسعار ركن التطور في قطر تُكتب بعد معاينة الموقع أو بعد وصف دقيق للحالة. الصفحة ليست قائمة أرقام ثابتة لكل فيلا، لأن التسرب والعزل والتكييف يختلفان بين برج في الدوحة وفلة في الريان.</p>
{cta()}
<h2>كيف يُحسب العرض؟</h2>
<ul>
<li>نوع الخدمة: كشف تسرب، عزل، تكييف، تسليك، تنظيف أو مكافحة حشرات.</li>
<li>المساحة وسهولة الوصول (حوش، سطح، دكت، إدارة مبنى).</li>
<li>إن لزم فتح موضعي بعد التقرير أم يكفي التشخيص.</li>
</ul>
<h2>كشف التسربات</h2>
<p>تفاصيل المنهج والأجهزة والتغطية على مستوى الدولة في المقال المتصدر:
<a href="{LEAK_URL}">شركة كشف تسربات المياه في قطر</a>.
بعد المعاينة يصلك مصدر المشكلة وتكلفة الإصلاح مكتوبة قبل التنفيذ.</p>
<h2>العزل والصيانة وباقي الخدمات</h2>
<p>عزل الأسطح والخزانات، صيانة التكييف، التسليك والتنظيف: المعاينة تحدد الخامة والمدة. لا نثبت «سعراً عبر الهاتف» للحالة النهائية.</p>
<h2>التواصل</h2>
<p>التواصل عبر واتساب من أزرار الموقع. البريد: info@rukn-eltatawer.com</p>
{cta()}
"""


def main():
    assert_2973_untouched()

    snippet_path = Path(__file__).with_name("snippet-rukn-qatar.php")
    code = snippet_path.read_text()
    if "2973" not in code or "water-leak-detection-company-in-qatar" not in code:
        raise SystemExit("snippet missing ranking lock")
    code_st, sn = api("/code-snippets/v1/snippets/5")
    note(f"snippet GET {code_st} active={sn.get('active') if isinstance(sn, dict) else sn}")
    payload = {
        "name": "Rukn Qatar SEO and contact fix",
        "desc": sn.get("desc") if isinstance(sn, dict) else "",
        "code": code,
        "tags": sn.get("tags") if isinstance(sn, dict) else [],
        "scope": "global",
        "active": True,
        "priority": (sn.get("priority") if isinstance(sn, dict) else 10) or 10,
    }
    st, out = api("/code-snippets/v1/snippets/5", "PUT", payload, timeout=120)
    err = out.get("code_error") if isinstance(out, dict) else out
    note(f"snippet PUT {st} err={err!r} len={len(code)}")
    if st not in (200, 201) or (isinstance(out, dict) and out.get("code_error")):
        raise SystemExit("snippet update failed")
    assert_2973_untouched()

    # Keep city leak clones draft + noindex + canonical to ranking URL
    for pid, slug in LEAK_CLONES:
        st, data = api(f"/wp/v2/posts/{pid}", "POST", {"status": "draft"})
        rm_meta(
            pid,
            robots=["noindex", "nofollow"],
            canonical=LEAK_URL,
            keyword="شركة كشف تسربات المياه في قطر",
        )
        st2, r = api("/rukn-qa/v1/redirect", "POST", {"from": slug, "to": LEAK_URL})
        note(f"clone {pid} {slug} draft={st} redirect={st2} {r if isinstance(r, dict) else ''}")
        time.sleep(0.05)
    assert_2973_untouched()

    # Service CPT: canonical to ranking article (do not edit 2973)
    st, _ = api("/wp/v2/services/1877", "POST", {
        "content": (
            "<p>كشف تسربات المياه في قطر بدون تكسير عشوائي. التفاصيل الكاملة والمنهج المعتمد على مستوى الدولة في "
            f'<a href="{LEAK_URL}">شركة كشف تسربات المياه في قطر</a>.</p>'
            + cta()
        )
    })
    rm_meta(1877, canonical=LEAK_URL, robots=["noindex", "follow"], object_type="post",
            title="كشف تسربات المياه في قطر | ركن التطور",
            description="تحويل إلى دليل كشف تسربات المياه في قطر — التشخيص قبل التكسير.",
            keyword="كشف تسربات المياه")
    note(f"service 1877 {st}")

    # Pricing
    st, _ = api("/wp/v2/pages/7464", "POST", {
        "title": "الأسعار والمعاينة — ركن التطور قطر",
        "slug": "as3ar",
        "content": pricing_html(),
        "comment_status": "closed",
        "ping_status": "closed",
    })
    rm_meta(7464, title="أسعار خدمات ركن التطور في قطر | معاينة ثم عرض مكتوب",
            description="لا سعر نهائي عبر الهاتف. معاينة في الدوحة وقطر ثم عرض مكتوب لكشف التسربات والعزل والتكييف.",
            keyword="أسعار خدمات منزلية قطر", object_type="post")
    note(f"pricing {st}")
    st, r = api("/rukn-qa/v1/redirect", "POST", {"from": "pricing", "to": "https://www.rukn-eltatawer.com/qa/as3ar/"})
    note(f"pricing redirect {st} {r}")

    # City hubs
    created = []
    for slug, title, city, intro, bullets in CITY_HUBS:
        st, existing = api(f"/wp/v2/pages?slug={slug}&_fields=id,slug,status")
        pid = None
        if isinstance(existing, list) and existing:
            pid = existing[0]["id"]
        body = hub_html(title, city, intro, bullets)
        payload = {
            "title": title,
            "slug": slug,
            "content": body,
            "status": "publish",
            "comment_status": "closed",
            "ping_status": "closed",
        }
        if pid:
            st, data = api(f"/wp/v2/pages/{pid}", "POST", payload)
        else:
            st, data = api("/wp/v2/pages", "POST", payload)
            pid = data.get("id") if isinstance(data, dict) else None
        if pid:
            rm_meta(
                pid,
                title=f"{title} | ركن التطور",
                description=f"خدمات ركن التطور في {city}: صيانة وعزل وتكييف، مع رابط دليل كشف التسربات على مستوى قطر.",
                keyword=f"خدمات ركن التطور في {city}",
                object_type="post",
            )
        created.append((st, pid, slug))
        note(f"hub {slug} {st} id={pid}")
        time.sleep(0.08)
    assert_2973_untouched()

    cities_links = "\n".join(
        f'<li><a href="https://www.rukn-eltatawer.com/qa/{slug}/">{title}</a></li>'
        for slug, title, *_ in CITY_HUBS
    )
    st, _ = api("/wp/v2/pages/7465", "POST", {
        "title": "المدن التي نغطيها في قطر",
        "content": f"""
<p>مقر ركن التطور في الدوحة، والفريق يصل إلى لوسيل والريان والوكرة والخور وأم صلال والخيسة والظعاين والشمال والشحانية.</p>
<p>كشف تسربات المياه على مستوى الدولة موثّق في مقال واحد حتى لا تتشتت نتائج البحث:
<a href="{LEAK_URL}">شركة كشف تسربات المياه في قطر</a>.</p>
<h2>صفحات المدن</h2>
<ul>
<li><a href="https://www.rukn-eltatawer.com/qa/services-in-lusail-qatar/">خدمات ركن التطور في لوسيل</a></li>
{cities_links}
</ul>
""",
    })
    note(f"cities page {st}")

    st, _ = api("/wp/v2/pages/7463", "POST", {
        "title": "خدمات ركن التطور في قطر",
        "content": f"""
<p>الخدمات الأساسية: كشف التسربات، العزل، الصيانة العامة، التكييف، السباكة والتسليك، التنظيف، مكافحة الحشرات، الحدائق والمسابح، التشطيب، والطاقة الشمسية.</p>
<p>دليل كشف التسربات (الصفحة المعتمدة على مستوى قطر):
<a href="{LEAK_URL}">شركة كشف تسربات المياه في قطر</a>.</p>
<p>كل خدمة تبدأ بمعاينة أو وصف دقيق، ثم عرض مكتوب.</p>
{cta()}
""",
    })
    note(f"services page {st}")

    st, _ = api("/wp/v2/pages/7467", "POST", {
        "title": "الأسئلة الشائعة",
        "content": f"""
<h2>هل تكشفون التسرب بدون تكسير؟</h2>
<p>نعم، بالأجهزة أولاً ثم فتح موضعي بعد التقرير. التفاصيل في
<a href="{LEAK_URL}">شركة كشف تسربات المياه في قطر</a>.</p>
<h2>هل التسعير عبر الهاتف؟</h2>
<p>لا نثبت سعر الحالة النهائية دون معاينة أو بيانات كافية عن الموقع.</p>
<h2>ما رقم التواصل؟</h2>
<p>{PHONE_HUMAN} أو واتساب على نفس الرقم.</p>
""",
    })
    note(f"faq page {st}")
    assert_2973_untouched()

    # Hero: remove Dubai municipality leftover in seed widget
    st, w = api("/rukn-qa/v1/seed-widget?id=10639")
    wpm = ((w.get("meta") or {}).get("widget_post_meta") if isinstance(w, dict) else None) or {}
    trust = wpm.get("dash_trust") or []
    changed = False
    new_trust = []
    for item in trust:
        title = (item or {}).get("title") or ""
        if "دبي" in title or "بلدية" in title:
            new_trust.append({**item, "title": "فريق مقيم في قطر"})
            changed = True
        else:
            new_trust.append(item)
    if changed:
        wpm["dash_trust"] = new_trust
        st, _ = api("/rukn-qa/v1/seed-widget?id=10639", "POST", {"widget_post_meta": wpm})
        note(f"hero dubai fix {st}")
    else:
        note("hero dubai already clean")

    assert_2973_untouched()
    note("DONE continue_safe")


if __name__ == "__main__":
    main()
