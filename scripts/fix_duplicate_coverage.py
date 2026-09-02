#!/usr/bin/env python3
"""Stop city×service clones and cover Qatar via city hubs + national pillars.

Never writes post 2973.
"""
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
LEAK = "https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/"
PHONE = '<a href="tel:+97431110184"><span dir="ltr">+974 3111 0184</span></a>'
WA = '<a href="https://wa.me/97431110184">واتساب</a>'
KEEP_SLUGS = {
    "water-leak-detection-company-in-qatar",
    "water-leak-detection-qatar-en",
    "roof-insulation-qatar-en",
    "ac-maintenance-qatar-en",
    "gas-leak-detection-doha",
    "ac-leak-detection-doha",
    "sewerage-company-in-doha",
}
CITY_SUF = (
    "-doha", "-al-rayyan", "-al-wakrah", "-al-khor", "-umm-salal",
    "-al-daayen", "-al-shamal", "-al-shahaniya", "-lusail",
)
PILLARS = {
    "leak": LEAK,
    "insul": "https://www.rukn-eltatawer.com/qa/shrkh-azl-asth-fy-qtr/",
    "ac": "https://www.rukn-eltatawer.com/qa/split-ac-maintenance-in-qatar/",
    "ac_central": "https://www.rukn-eltatawer.com/qa/central-air-conditioning-maintenance-in-qatar/",
    "clean": "https://www.rukn-eltatawer.com/qa/house-cleaning-in-qatar/",
    "villa": "https://www.rukn-eltatawer.com/qa/villa-cleaning-in-qatar/",
    "tank": "https://www.rukn-eltatawer.com/qa/water-tank-cleaning-in-qatar/",
    "pest": "https://www.rukn-eltatawer.com/qa/pest-control-in-qatar/",
    "termite": "https://www.rukn-eltatawer.com/qa/termite-control-in-qatar/",
    "plumb": "https://www.rukn-eltatawer.com/qa/home-plumber-in-qatar/",
    "sewer": "https://www.rukn-eltatawer.com/qa/shrkh-tslyk-mjary-fy-qtr/",
    "sewer_doha": "https://www.rukn-eltatawer.com/qa/sewerage-company-in-doha/",
    "garden": "https://www.rukn-eltatawer.com/qa/shrkh-tnsyq-hdayq-fy-qtr/",
    "pool": "https://www.rukn-eltatawer.com/qa/shrkh-syanh-msabh-fy-qtr/",
    "gas": "https://www.rukn-eltatawer.com/qa/shrkh-kshf-tsrbat-alghaz-fy-qtr/",
    "pool_leak": "https://www.rukn-eltatawer.com/qa/shrkh-kshf-tsrbat-almsabh-fy-qtr/",
    "services": "https://www.rukn-eltatawer.com/qa/services/",
}


def api(path, method="GET", data=None, timeout=90):
    url = path if path.startswith("http") else BASE + path
    body = None if data is None else json.dumps(data).encode()
    last_err = None
    for attempt in range(5):
        req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
                return r.status, json.loads(r.read().decode() or "null"), {k.lower(): v for k, v in r.headers.items()}
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors="replace")
            try:
                return e.code, json.loads(raw), {}
            except Exception:
                return e.code, raw[:400], {}
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise last_err


def note(msg):
    print(msg, flush=True)


def lockcheck():
    code, p, _ = api(f"/wp/v2/posts/{LOCKED}?context=edit&_fields=id,slug,status,title")
    title = unescape((p.get("title") or {}).get("raw") or "")
    ok = p.get("slug") == "water-leak-detection-company-in-qatar" and title == "شركة كشف تسربات المياه في قطر"
    note(f"LOCK 2973 {ok}")
    if not ok:
        raise SystemExit("abort: ranking post changed")


def get_all(status, fields="id,slug,status,title,date"):
    items = []
    page = 1
    while True:
        code, data, meta = api(
            f"/wp/v2/posts?per_page=100&page={page}&status={status}&context=edit&_fields={fields}"
        )
        if code != 200 or not data:
            break
        items.extend(data)
        pages = int(meta.get("x-wp-totalpages", 1) or 1)
        if page >= pages:
            break
        page += 1
        time.sleep(0.02)
    return items


def cta():
    return f"<p>المعاينة في الموقع ثم عرض سعر مكتوب. {PHONE} — {WA}</p>"


def hub_html(city, intro, local):
    p = PILLARS
    return f"""
<p>{intro}</p>
<p>التغطية هنا ليست نسخة «شركة … في {city}» لكل خدمة. الخدمة على مستوى قطر لها صفحة واحدة، و{city} مذكورة بما يخص مبانيها ومناخها. كشف تسربات المياه للدولة كلها في مقال واحد معتمد:
<a href="{p['leak']}">شركة كشف تسربات المياه في قطر</a>.</p>
<h2>كشف التسربات في {city}</h2>
<p>{local['leak']} التفاصيل والمنهج والأجهزة على مستوى قطر — لا صفحة مدينة منفصلة لهذا الغرض:
<a href="{p['leak']}">شركة كشف تسربات المياه في قطر</a>.
تسرب الغاز: <a href="{p['gas']}">كشف تسربات الغاز في قطر</a>.
تسرب المسبح: <a href="{p['pool_leak']}">كشف تسربات المسابح</a>.</p>
<h2>العزل</h2>
<p>{local['insul']} <a href="{p['insul']}">عزل الأسطح في قطر</a>.</p>
<h2>التكييف</h2>
<p>{local['ac']} <a href="{p['ac']}">صيانة مكيفات سبليت في قطر</a>
و<a href="{p['ac_central']}">صيانة التكييف المركزي</a>.</p>
<h2>التنظيف</h2>
<p>{local['clean']} <a href="{p['clean']}">تنظيف منازل في قطر</a>،
<a href="{p['villa']}">تنظيف فلل</a>،
<a href="{p['tank']}">تنظيف خزانات</a>.</p>
<h2>السباكة والتسليك</h2>
<p>{local['plumb']} <a href="{p['plumb']}">سباك منازل في قطر</a>
و<a href="{p['sewer']}">تسليك مجاري في قطر</a>.</p>
<h2>مكافحة الحشرات</h2>
<p>{local['pest']} <a href="{p['pest']}">مكافحة حشرات في قطر</a>
و<a href="{p['termite']}">مكافحة الرمّة</a>.</p>
<h2>الحدائق والمسابح والصيانة</h2>
<p>{local['other']} <a href="{p['garden']}">تنسيق حدائق</a>،
<a href="{p['pool']}">صيانة مسابح</a>،
<a href="{p['services']}">باقي الخدمات</a>.</p>
{cta()}
"""


HUBS = [
    (
        14601,
        "خدمات ركن التطور في الدوحة",
        "الدوحة مقر الفريق: الخليج الغربي، اللؤلؤة، مشيرب، لقطيفية، الثمامة، الدفنة، السد وعين خالد. أبراج وشقق وفلل في مدينة واحدة.",
        {
            "leak": "في الأبراج يظهر التسرب غالباً من التكييف المركزي والدكتات؛ في الفلل من الحوش والخزان الأرضي.",
            "insul": "أسطح الملاحق والأبراج تحتاج ميلاً وصرفاً قبل أي طبقة فوم أو أغشية.",
            "ac": "الخليج الغربي واللؤلؤة أغلبها مركزي؛ الفلل سبليت وباكيج.",
            "clean": "شقق مفروشة تحتاج تعقيماً أضيق من فلل عين خالد والسد.",
            "plumb": "ضغط الشبكة في الأدوار العليا يختلف عن الفلل. تسليك الدوحة له صفحة محلية إن لزم.",
            "pest": "الرطوبة في الأدوار الأرضية تجذب الصراصير؛ الرمّة في الخشب الرطب بالملاحق.",
            "other": "حدائق الفلل وصيانة العقود للأبراج تُحدَّد بعد معاينة إدارة المبنى.",
        },
    ),
    (
        14599,
        "خدمات ركن التطور في لوسيل",
        "لوسيل أبراج وشقق وتكييف مركزي أكثر من فلل الحوش: المارينا، قطيفان، واللؤلؤة المجاورة.",
        {
            "leak": "الشائع تسرب الدكتات والتكييف المركزي ورطوبة الواجهات الساحلية. منهج الكشف هو نفسه المعتمد لقطر.",
            "insul": "أسطح الملاحق والأبراج معرضة للملح والحرارة؛ المعاينة قبل الخامة.",
            "ac": "المركزي والدكتات هما الغالب. السبليت أقل من فلل الريان.",
            "clean": "الشقق تحتاج تنسيقاً مع إدارة المبنى أحياناً قبل التنظيف العميق.",
            "plumb": "شبكات الأدوار العالية وضغط المضخات يختلفان عن الفلل.",
            "pest": "بق الفراش في الشقق المفروشة طلب متكرر أكثر من الرمّة.",
            "other": "المسابح المشتركة تتبع إدارة المجمع؛ المسابح الخاصة تُعاين على حدة.",
        },
    ),
    (
        14602,
        "خدمات ركن التطور في الريان",
        "الريان فلل وحوش: الوعب، الغرافة، معيذر، السيلية وأبو هامور. الوصول من الدوحة يومي.",
        {
            "leak": "الحوش والخزان الأرضي ومواسير الري المخفي أشيع من دكتات الأبراج.",
            "insul": "أسطح الفلل واسعة؛ الحرارة فوق الغرف العلوية شكوى متكررة بعد الصيف.",
            "ac": "سبليت وباكيج أكثر من مركزي أبراج.",
            "clean": "تنظيف الفلل والخزانات الأرضية أكبر حجماً من شقق الدوحة.",
            "plumb": "البيارات ومواسير الحوش تحتاج كاميرا أحياناً قبل التسليك.",
            "pest": "الرمّة في الخشب والملاحق مع الرطوبة.",
            "other": "حدائق وعشب صناعي يناسب الملوحة والحرارة.",
        },
    ),
    (
        14603,
        "خدمات ركن التطور في الوكرة",
        "الوكرة والوكير والمشاف مناخ ساحلي: رطوبة تخفي التسرب وتسرّع تلف الدهان والعزل.",
        {
            "leak": "الرطوبة الساحلية تخفي البقع؛ عداد كهرماء والرائحة أدق من انتظار التقشير.",
            "insul": "العزل القديم على الأسطح الساحلية يتشقق أسرع.",
            "ac": "سبليت في الفلل هو الغالب؛ الملح يؤثر على الوحدات الخارجية.",
            "clean": "الملح والرطوبة يزيدان حاجة الخزانات والغسيل بعد الصيف.",
            "plumb": "شبكات قديمة في بعض الأحياء؛ لا تسليك أعمى دون فحص إن تكرر الانسداد.",
            "pest": "رطوبة ساحلية وصراصير في الأدوار الأرضية.",
            "other": "حدائق تتحمل الملح؛ مسابح منزلية شائعة.",
        },
    ),
    (
        14604,
        "خدمات ركن التطور في الخور",
        "الخور والذخيرة وسميسما: وصول من الدوحة بالتنسيق. الزمن يُذكر في موعد المعاينة.",
        {
            "leak": "فلل ساحلية وخزانات؛ الكشف بنفس منهج قطر دون صفحة مدينة مكررة.",
            "insul": "أسطح معرضة للحرارة والرياح والملح.",
            "ac": "وحدات خارجية تتأثر بالملح؛ الصيانة قبل الصيف أوضح من الانتظار للعطل.",
            "clean": "الفلل المنفصلة أكبر من شقق الدوحة؛ المعاينة تحدد الطاقم.",
            "plumb": "مضخات وخزانات أرضية أكثر من شبكات أبراج.",
            "pest": "حشرات ومخازن خشب في الملاحق.",
            "other": "الزيارة تُجدول مسبقاً وليست فورية في نفس الساعة.",
        },
    ),
    (
        14605,
        "خدمات ركن التطور في أم صلال والخيسة",
        "أم صلال محمد وأم صلال علي والخيسة: فلل ومزارع سكنية. نصل بالتنسيق من الدوحة.",
        {
            "leak": "ري مخفي وخزانات أرضية أكثر من دكتات أبراج.",
            "insul": "أسطح مساحات أكبر؛ الميل والصرف قبل الخامة.",
            "ac": "سبليت للمساحات الواسعة.",
            "clean": "خزانات أرضية وتنظيف فلل بعد السكن أو الصيف.",
            "plumb": "بيارات ومضخات؛ تكرار الانسداد يستدعي فحصاً لا تسليكاً فقط.",
            "pest": "رمّة في الخشب الرطب والمزارع السكنية.",
            "other": "حدائق ومساحات مفتوحة تحتاج رياً يناسب الحرارة.",
        },
    ),
    (
        14606,
        "خدمات ركن التطور في الظعاين",
        "الظعاين وأم قرن ولوسيل الشمالية: توسع بين فلل ومجمعات جديدة.",
        {
            "leak": "التشطيب الجديد يستفيد من فحص ضغط قبل السكن؛ بعد السكن المنهج هو مقال قطر المعتمد.",
            "insul": "أسطح جديدة تفشل إن أُهمل الميل من أول صيف.",
            "ac": "مجمعات أقرب للمركزي؛ فلل سبليت.",
            "clean": "تنظيف بعد التشطيب يختلف عن التنظيف الدوري.",
            "plumb": "تأسيس جديد يُفحص قبل الإغلاق.",
            "pest": "حشرات بعد السكن الأول في الفلل الجديدة.",
            "other": "حدائق تأسيس ومسابح خاصة حسب المجمع.",
        },
    ),
    (
        14607,
        "خدمات ركن التطور في الشمال",
        "الرويس والشمال: أبعد تغطية شمالية. الزيارة تُجدول مسبقاً ويُذكر زمن الوصول بعد العنوان.",
        {
            "leak": "الفلل المنفصلة والخزانات؛ لا نعد بوصول فوري في نفس الساعة.",
            "insul": "حرارة ورياح؛ المعاينة قبل وعد العمر الافتراضي.",
            "ac": "وحدات تتحمل الغبار والحرارة؛ الصيانة الموسمية أهم.",
            "clean": "المساحة والسفر يُذكران في عرض الموعد.",
            "plumb": "مضخات وخزانات بعيدة عن شبكة كثيفة.",
            "pest": "حشرات مخازن وملاحق.",
            "other": "نوضح إمكانية الوصول إن كان الموقع خارج النطاق المعتاد.",
        },
    ),
    (
        14608,
        "خدمات ركن التطور في الشحانية",
        "الشحانية والوجبة وغرب الريان: فلل ومساحات مفتوحة. الاسم الصحيح الشحانية لا «المشحمية».",
        {
            "leak": "حوش ومساحات واسعة؛ هبوط البلاط مؤشر قبل ظهور البركة.",
            "insul": "أسطح واسعة وعزل حراري بعد الصيف.",
            "ac": "سبليت لمساحات كبيرة.",
            "clean": "فلل أكبر؛ الخزان الأرضي جزء من المعاينة.",
            "plumb": "ري وحدائق يزيدان الحمل على الشبكة.",
            "pest": "حشرات مساحات مفتوحة ورمّة في الخشب.",
            "other": "عشب صناعي يناسب الحرارة أفضل من طبيعي بلا ري مدروس.",
        },
    ),
]


def services_page():
    cities = [
        ("الدوحة", "https://www.rukn-eltatawer.com/qa/services-in-doha-qatar/"),
        ("لوسيل", "https://www.rukn-eltatawer.com/qa/services-in-lusail-qatar/"),
        ("الريان", "https://www.rukn-eltatawer.com/qa/services-in-al-rayyan-qatar/"),
        ("الوكرة", "https://www.rukn-eltatawer.com/qa/services-in-al-wakrah-qatar/"),
        ("الخور", "https://www.rukn-eltatawer.com/qa/services-in-al-khor-qatar/"),
        ("أم صلال والخيسة", "https://www.rukn-eltatawer.com/qa/services-in-umm-salal-qatar/"),
        ("الظعاين", "https://www.rukn-eltatawer.com/qa/services-in-al-daayen-qatar/"),
        ("الشمال", "https://www.rukn-eltatawer.com/qa/services-in-al-shamal-qatar/"),
        ("الشحانية", "https://www.rukn-eltatawer.com/qa/services-in-al-shahaniya-qatar/"),
    ]
    city_lis = "\n".join(f'<li><a href="{u}">{n}</a></li>' for n, u in cities)
    return f"""
<p>ركن التطور يغطّي الخدمات المنزلية في قطر هكذا: <strong>صفحة خدمة واحدة على مستوى الدولة</strong>، و<strong>صفحة مدينة</strong> تشرح طبيعة المباني وتربط لتلك الخدمات. لا ننشر عشرات النسخ المتطابقة «شركة … في كل مدينة».</p>
<h2>الخدمات على مستوى قطر</h2>
<ul>
<li><a href="{LEAK}">كشف تسربات المياه</a> — الصفحة المعتمدة الوحيدة لهذه النية</li>
<li><a href="{PILLARS['insul']}">عزل الأسطح</a></li>
<li><a href="{PILLARS['ac']}">صيانة المكيفات</a> و<a href="{PILLARS['ac_central']}">المركزي</a></li>
<li><a href="{PILLARS['clean']}">تنظيف المنازل</a> و<a href="{PILLARS['villa']}">الفلل</a> و<a href="{PILLARS['tank']}">الخزانات</a></li>
<li><a href="{PILLARS['plumb']}">السباكة</a> و<a href="{PILLARS['sewer']}">تسليك المجاري</a></li>
<li><a href="{PILLARS['pest']}">مكافحة الحشرات</a> و<a href="{PILLARS['termite']}">الرمّة</a></li>
<li><a href="{PILLARS['garden']}">تنسيق الحدائق</a> و<a href="{PILLARS['pool']}">المسابح</a></li>
<li><a href="{PILLARS['gas']}">كشف تسربات الغاز</a> و<a href="{PILLARS['pool_leak']}">تسرب المسبح</a></li>
</ul>
<h2>المدن</h2>
<ul>
{city_lis}
</ul>
{cta()}
"""


def cities_page():
    return f"""
<p>المقر الدوحة، والفريق يصل إلى لوسيل والريان والوكرة والخور وأم صلال والخيسة والظعاين والشمال والشحانية. إن كان موقعك خارج القائمة راسلنا ونوضح إمكانية الوصول.</p>
<p>كشف تسربات المياه للدولة في مقال واحد:
<a href="{LEAK}">شركة كشف تسربات المياه في قطر</a>.</p>
<h2>صفحات المدن</h2>
<ul>
<li><a href="https://www.rukn-eltatawer.com/qa/services-in-doha-qatar/">الدوحة</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/services-in-lusail-qatar/">لوسيل</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/services-in-al-rayyan-qatar/">الريان</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/services-in-al-wakrah-qatar/">الوكرة</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/services-in-al-khor-qatar/">الخور</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/services-in-umm-salal-qatar/">أم صلال والخيسة</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/services-in-al-daayen-qatar/">الظعاين</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/services-in-al-shamal-qatar/">الشمال</a></li>
<li><a href="https://www.rukn-eltatawer.com/qa/services-in-al-shahaniya-qatar/">الشحانية</a></li>
</ul>
"""


def main():
    lockcheck()
    snippet = Path(__file__).with_name("snippet-rukn-qatar.php").read_text()
    if "rukn_is_city_template" not in snippet:
        raise SystemExit("snippet missing city-template guard")
    st, sn, _ = api("/code-snippets/v1/snippets/5")
    st, out, _ = api("/code-snippets/v1/snippets/5", "PUT", {
        "name": "Rukn Qatar SEO and contact fix",
        "code": snippet,
        "scope": "global",
        "active": True,
        "priority": (sn.get("priority") if isinstance(sn, dict) else 10) or 10,
    }, timeout=120)
    note(f"snippet PUT {st} err={out.get('code_error') if isinstance(out, dict) else out}")
    if isinstance(out, dict) and out.get("code_error"):
        raise SystemExit("snippet error")
    lockcheck()

    futures = get_all("future")
    pubs = get_all("publish")
    to_draft = []
    for p in futures:
        if p["id"] == LOCKED:
            continue
        to_draft.append(p)
    for p in pubs:
        slug = p.get("slug") or ""
        if p["id"] == LOCKED or slug in KEEP_SLUGS:
            continue
        if slug.endswith(CITY_SUF) or p.get("date", "") >= "2026-09-02T12:30:00":
            # keep intentional EN nationals created the same day
            if slug.endswith("-en"):
                continue
            to_draft.append(p)
    note(f"drafting {len(to_draft)} clones (future+published templates)")
    n = 0
    for p in to_draft:
        if p["id"] == LOCKED:
            continue
        st, _, _ = api(f"/wp/v2/posts/{p['id']}", "POST", {"status": "draft"})
        n += 1
        if n % 100 == 0:
            note(f"drafted {n}/{len(to_draft)} last={p['id']} {st}")
        time.sleep(0.04)
    note(f"drafted done {n}")
    lockcheck()

    city_name = {
        14601: "الدوحة", 14599: "لوسيل", 14602: "الريان", 14603: "الوكرة",
        14604: "الخور", 14605: "أم صلال", 14606: "الظعاين", 14607: "الشمال", 14608: "الشحانية",
    }
    for pid, title, intro, local in HUBS:
        st, _, _ = api(f"/wp/v2/pages/{pid}", "POST", {
            "title": title,
            "content": hub_html(city_name[pid], intro, local),
            "comment_status": "closed",
            "ping_status": "closed",
        })
        note(f"hub {pid} {city_name[pid]} {st}")
        time.sleep(0.05)
    st, _, _ = api("/wp/v2/pages/7463", "POST", {"title": "خدمات ركن التطور في قطر", "content": services_page()})
    note(f"services page {st}")
    st, _, _ = api("/wp/v2/pages/7465", "POST", {"title": "المدن التي نغطيها في قطر", "content": cities_page()})
    note(f"cities page {st}")
    lockcheck()

    pubs2 = get_all("publish")
    fut2 = get_all("future")
    note(f"remaining publish={len(pubs2)} future={len(fut2)}")
    leftover = [p for p in pubs2 if (p.get("slug") or "").endswith(CITY_SUF) and p.get("slug") not in KEEP_SLUGS]
    note(f"published city-suffix leftover {len(leftover)}")
    note("DONE fix_duplicate_coverage")


if __name__ == "__main__":
    main()
