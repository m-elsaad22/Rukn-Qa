#!/usr/bin/env python3
"""Apply safe Qatar site fixes: hide call, WhatsApp 971586634710, no stored edit of 2973."""
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
    raise SystemExit("Set WP_APP_PASSWORD")

AUTH = base64.b64encode(f"{_wp_user}:{_wp_pass}".encode()).decode()
BASE = "https://www.rukn-eltatawer.com/qa/wp-json"
CTX = ssl.create_default_context()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 CursorFix/1.0",
    "Content-Type": "application/json",
}
LOCKED = 2973
WA = "971586634710"
WA_URL = f"https://wa.me/{WA}?text=" + urllib.parse.quote(
    "مرحباً، أريد الاستفسار عن خدمات ركن التطور في قطر"
)
LEAK_URL = "https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/"


def api(path, method="GET", data=None, timeout=120):
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


def assert_2973():
    code, p = api(f"/wp/v2/posts/{LOCKED}?context=edit&_fields=id,slug,status,title")
    title = unescape((p.get("title") or {}).get("raw") or "")
    ok = (
        code == 200
        and p.get("id") == LOCKED
        and p.get("slug") == "water-leak-detection-company-in-qatar"
        and p.get("status") == "publish"
        and title == "شركة كشف تسربات المياه في قطر"
    )
    note(f"LOCKCHECK 2973 ok={ok} title={title!r}")
    if not ok:
        raise SystemExit("Ranking post 2973 changed — aborting")


def wa_p():
    return (
        f'<p><a class="btn btn-wa" href="{WA_URL}" rel="nofollow noopener" target="_blank">'
        "تواصل عبر واتساب</a></p>"
    )


ABOUT = f"""
<p>ركن التطور شركة خدمات منزلية تعمل في قطر: كشف تسربات المياه، عزل الأسطح والخزانات، صيانة التكييف، السباكة، تسليك المجاري، التنظيف ومكافحة الحشرات. الفريق يعمل من الدوحة ويغطي لوسيل والريان والوكرة والخور وأم صلال والضعاين والشمال والشحانية بالتنسيق المسبق.</p>
<p>طريقة العمل ثابتة: نفهم الشكوى، نحدد المصدر قبل التكسير أو تغيير الخامة، ثم نكتب عرض السعر قبل التنفيذ. لا نبيع «حلاً جاهزاً» لكل فيلا لأن برج الخليج الغربي غير فلة معيذر.</p>
<p>تفاصيل كشف التسربات على مستوى الدولة في المقال الرئيسي:
<a href="{LEAK_URL}">شركة كشف تسربات المياه في قطر</a>.</p>
<h2>ماذا نغطي؟</h2>
<ul>
<li>كشف تسربات المياه والرطوبة وارتفاع فاتورة كهرماء.</li>
<li>عزل الأسطح والخزانات بعد فحص الميل والصرف.</li>
<li>صيانة وتركيب المكيفات وتنظيف الدكتات.</li>
<li>سباكة وتسليك وصبغ وجبس بورد حسب الحالة.</li>
</ul>
<p>للتواصل استخدم واتساب من أي صفحة في الموقع. زر الاتصال الهاتفي مخفي مؤقتاً.</p>
{wa_p()}
"""

CONTACT = f"""
<p>للتواصل مع ركن التطور في قطر استخدم واتساب. نحدد الموعد بعد العنوان ونوع الخدمة، ثم نكتب المعاينة أو العرض قبل التنفيذ.</p>
<p>التغطية: الدوحة، لوسيل، الريان، الوكرة، الخور، أم صلال، الضعاين، الشمال والشحانية.</p>
<p>البريد: info@rukn-eltatawer.com</p>
<p>كشف التسربات: <a href="{LEAK_URL}">شركة كشف تسربات المياه في قطر</a>.</p>
{wa_p()}
"""

CONTACT_EN = f"""
<p>Contact Rukn El Tatawer in Qatar on WhatsApp. Share the area and the service you need; we confirm timing and send a written inspection or quote before work starts.</p>
<p>Coverage: Doha, Lusail, Al Rayyan, Al Wakrah, Al Khor, Umm Salal, Al Daayen, Al Shamal and Al Shahaniya.</p>
<p>Email: info@rukn-eltatawer.com</p>
<p>National leak guide: <a href="{LEAK_URL}">Water leak detection in Qatar</a>.</p>
<p><a class="btn btn-wa" href="{WA_URL}" rel="nofollow noopener" target="_blank">WhatsApp</a></p>
"""

PRIVACY = f"""
<p>سياسة الخصوصية — ركن التطور للخدمات المنزلية في قطر. نتعامل مع بياناتك للرد على طلب الخدمة وتنسيق المعاينة فقط.</p>
<h2>ما الذي نجمعه؟</h2>
<ul>
<li>الاسم ووسيلة التواصل التي ترسلها أنت عبر واتساب أو النموذج.</li>
<li>عنوان العقار أو المنطقة إذا لزم وصول الفني.</li>
<li>وصف المشكلة والصور التي تشاركها اختيارياً.</li>
</ul>
<h2>كيف نستخدمها؟</h2>
<p>لجدولة الزيارة، تقدير العرض، وتنفيذ الخدمة. لا نبيع بياناتك لطرف ثالث للتسويق.</p>
<h2>التواصل</h2>
<p>لطلب حذف بياناتك أو الاستفسار استخدم واتساب أو البريد info@rukn-eltatawer.com. المقر التشغيلي في الدوحة، قطر.</p>
{wa_p()}
"""

FAQ = f"""
<p>أسئلة متكررة عن خدمات ركن التطور في قطر. التفاصيل الكاملة لكشف التسربات في
<a href="{LEAK_URL}">شركة كشف تسربات المياه في قطر</a>.</p>
<h2>هل تعملون خارج الدوحة؟</h2>
<p>نعم، بالتنسيق: لوسيل والريان والوكرة والخور وأم صلال والضعاين والشمال والشحانية. زمن الوصول يُذكر بعد العنوان.</p>
<h2>هل كشف التسرب يحتاج تكسير؟</h2>
<p>التشخيص أولاً بأجهزة غير متلفة قدر الإمكان. أي فتح موضعي يُذكر في العرض قبل التنفيذ.</p>
<h2>هل السعر ثابت من الرسالة؟</h2>
<p>لا. المعاينة أو وصف دقيق للحالة ثم عرض مكتوب. الصفحة <a href="/qa/as3ar/">الأسعار</a> تشرح طريقة الحساب.</p>
<h2>كيف أتواصل الآن؟</h2>
<p>واتساب من الزر العائم أو من داخل الصفحات. زر الاتصال الهاتفي مخفي مؤقتاً.</p>
{wa_p()}
"""

BLOG = """
<p>مقالات ركن التطور عن الصيانة المنزلية في قطر: تسربات، عزل، تكييف وسباكة. نكتب من واقع الزيارات لا من قوالب عامة.</p>
"""

PRICING = f"""
<p>أسعار ركن التطور في قطر تُكتب بعد معاينة الموقع أو بعد وصف دقيق للحالة. الصفحة ليست قائمة أرقام ثابتة لكل فيلا.</p>
<h2>كيف يُحسب العرض؟</h2>
<ul>
<li>نوع الخدمة: كشف تسرب، عزل، تكييف، تسليك، تنظيف أو مكافحة حشرات.</li>
<li>المساحة وسهولة الوصول.</li>
<li>إن لزم فتح موضعي بعد التقرير.</li>
</ul>
<p>منهج كشف التسربات: <a href="{LEAK_URL}">شركة كشف تسربات المياه في قطر</a>.</p>
{wa_p()}
"""

SERVICES_DIR = f"""
<p>خدمات ركن التطور في قطر من الدوحة إلى باقي المدن. اختر الخدمة ثم تواصل عبر واتساب لتحديد المعاينة.</p>
<ul>
<li><a href="{LEAK_URL}">كشف تسربات المياه</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/shrkh-azl-asth-fy-qtr/">عزل الأسطح</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/central-air-conditioning-maintenance-in-qatar/">صيانة التكييف</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/plumbing-maintenance-in-qatar/">السباكة</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/shrkh-tslyk-mjary-fy-qtr/">تسليك المجاري</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/cities/">المدن</a></li>
</ul>
{wa_p()}
"""

SERVICE_BODIES = {
    1866: "إنشاء وصيانة المباني في قطر: فحص ثم خطة عمل مكتوبة للفلل والمباني السكنية في الدوحة وباقي المدن.",
    1868: "إنشاء وصيانة المسابح في قطر: تسرب، مضخات وفلاتر بعد معاينة الموقع — بدون سعر نهائي عبر رسالة قصيرة.",
    1870: "تنسيق الحدائق في قطر يناسب الحرارة والري. نحدد النطاق بعد زيارة الفلة أو المزرعة.",
    1872: "تركيب الباركيه بعد فحص الرطوبة والقاعدة. التنفيذ بعد عرض مكتوب.",
    1874: "تركيب جبس بورد للأسقف والجدران حسب المساحة وارتفاع السقف.",
    1876: "عازل الصوت للغرف والمكاتب بعد معاينة الجدار والسقف.",
    1879: "عزل الأسطح والخزانات في قطر بعد فحص الميل والصرف. ليست خامة واحدة لكل سطح.",
    1881: "تسليك المجاري بتشخيص الانسداد قبل القص. تفاصيل وطنية لكشف التسرب في المقال الرئيسي إن كان المصدر مياهاً مخفية.",
    1883: "صيانة وتركيب المكيفات قبل الصيف: تنظيف، فريون ودكتات ترفع فاتورة كهرماء.",
    1885: "تنظيف وتعقيم للشقق والفلل بعد الاتفاق على المساحة ونوع الخدمة.",
    1887: "مكافحة الحشرات بزيارة مجدولة وشرح المادة المستخدمة قبل التنفيذ.",
}


def push_snippet():
    snippet_path = Path(__file__).with_name("snippet-rukn-qatar.php")
    code = snippet_path.read_text()
    if "971586634710" not in code or "call_show:false" not in code:
        raise SystemExit("snippet missing new WA / hide-call")
    if "2973" not in code:
        raise SystemExit("snippet missing ranking lock")
    st, sn = api("/code-snippets/v1/snippets/5")
    payload = {
        "name": "Rukn Qatar SEO and contact fix",
        "desc": sn.get("desc") if isinstance(sn, dict) else "",
        "code": code,
        "tags": sn.get("tags") if isinstance(sn, dict) else [],
        "scope": "global",
        "active": True,
        "priority": (sn.get("priority") if isinstance(sn, dict) else 10) or 10,
    }
    st, out = api("/code-snippets/v1/snippets/5", "PUT", payload)
    err = out.get("code_error") if isinstance(out, dict) else out
    note(f"snippet PUT {st} err={err!r} len={len(code)}")
    if st not in (200, 201) or (isinstance(out, dict) and out.get("code_error")):
        raise SystemExit(f"snippet update failed: {err}")


def update_pages():
    pages = {
        7460: ABOUT,
        7461: CONTACT,
        7462: PRIVACY,
        7463: SERVICES_DIR,
        7464: PRICING,
        7467: FAQ,
        2453: BLOG,
        8990: CONTACT_EN,
    }
    for pid, html in pages.items():
        st, out = api(f"/wp/v2/pages/{pid}", "POST", {"content": html})
        note(f"page {pid} {st}")
        time.sleep(0.05)


def update_hubs():
    ids = [14599, 14601, 14602, 14603, 14604, 14605, 14606, 14607, 14608]
    for pid in ids:
        st, p = api(f"/wp/v2/pages/{pid}?context=edit&_fields=id,content")
        raw = ((p.get("content") or {}).get("raw") or "") if isinstance(p, dict) else ""
        raw = raw.replace('href="tel:+97431110184"', f'href="{WA_URL}"')
        raw = raw.replace("tel:+97431110184", WA_URL)
        raw = raw.replace("https://wa.me/97431110184", f"https://wa.me/{WA}")
        raw = raw.replace("+974 3111 0184", "")
        raw = raw.replace("+97431110184", "")
        if "wa.me/971586634710" not in raw:
            raw = raw.rstrip() + "\n" + wa_p()
        st, _ = api(f"/wp/v2/pages/{pid}", "POST", {"content": raw})
        note(f"hub {pid} {st}")
        time.sleep(0.05)


def update_services():
    st, _ = api("/wp/v2/services/1877", "POST", {
        "content": (
            "<p>كشف تسربات المياه في قطر بدون تكسير عشوائي. التفاصيل في "
            f'<a href="{LEAK_URL}">شركة كشف تسربات المياه في قطر</a>.</p>{wa_p()}'
        )
    })
    note(f"service 1877 {st}")
    for pid, text in SERVICE_BODIES.items():
        html = f"<p>{text}</p>{wa_p()}"
        st, _ = api(f"/wp/v2/services/{pid}", "POST", {"content": html})
        note(f"service {pid} {st}")
        time.sleep(0.04)


def update_widgets():
    patches = {
        10639: {
            "whatsapp_url": f"https://wa.me/{WA}",
            "phone_url": "",
        },
        10642: {
            "finder_wa_url": f"https://wa.me/{WA}",
        },
        10659: {
            "cta_wa_url": f"https://wa.me/{WA}",
            "cta_phone_url": "",
            "cta_quote_url": f"https://wa.me/{WA}",
        },
    }
    for wid, patch in patches.items():
        st, d = api(f"/rukn-qa/v1/seed-widget?id={wid}")
        wpm = ((d.get("meta") or {}).get("widget_post_meta") or {}) if isinstance(d, dict) else {}
        if not isinstance(wpm, dict):
            note(f"widget {wid} skip bad meta {st}")
            continue
        wpm.update(patch)
        st, out = api("/rukn-qa/v1/seed-widget", "POST", {"id": wid, "widget_post_meta": wpm})
        note(f"widget {wid} {st} {out.get('id') if isinstance(out, dict) else out}")


def add_menu_items():
    st, items = api("/wp/v2/menu-items?menus=2372&per_page=50")
    urls = set()
    if isinstance(items, list):
        urls = {i.get("url") for i in items}
    wanted = [
        ("المدن", "https://www.rukn-eltatawer.com/qa/cities/"),
        ("الأسعار", "https://www.rukn-eltatawer.com/qa/as3ar/"),
    ]
    for title, url in wanted:
        if url in urls:
            note(f"menu has {title}")
            continue
        st, out = api("/wp/v2/menu-items", "POST", {
            "title": title,
            "url": url,
            "status": "publish",
            "menus": 2372,
            "type": "custom",
        })
        note(f"menu add {title} {st} {out.get('id') if isinstance(out, dict) else out}")


def settings():
    st, out = api("/wp/v2/settings", "POST", {"page_for_posts": 2453})
    note(f"settings {st} page_for_posts={out.get('page_for_posts') if isinstance(out, dict) else out}")


def main():
    assert_2973()
    push_snippet()
    assert_2973()
    update_widgets()
    update_pages()
    update_hubs()
    update_services()
    add_menu_items()
    settings()
    assert_2973()
    note("DONE")


if __name__ == "__main__":
    main()
