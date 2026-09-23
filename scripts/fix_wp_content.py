#!/usr/bin/env python3
"""Fix Rukn Qatar WP content, SEO meta, duplicates, and schedule drafts."""
from __future__ import annotations

import base64
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from html import unescape
from zoneinfo import ZoneInfo

import os

_wp_user = os.environ.get("WP_USER", "cursor")
_wp_pass = os.environ.get("WP_APP_PASSWORD", "")
if not _wp_pass:
    raise SystemExit("Set WP_APP_PASSWORD in the environment (WordPress application password).")
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
IMG = "https://www.rukn-eltatawer.com/qa/wp-content/uploads/2024/05/leakage.webp"
IMG_AC = "https://www.rukn-eltatawer.com/qa/wp-content/uploads/2020/07/ac-cleaning.webp"
IMG_INTRO = "https://www.rukn-eltatawer.com/qa/wp-content/uploads/2026/04/intro-1.webp"
QATAR = ZoneInfo("Asia/Qatar")

CITIES = {
    "الدوحة": "الخليج الغربي، اللؤلؤة، لقطيفية، مشيرب، الثمامة، الدفنة، عين خالد والسد",
    "الريان": "الوعب، الغرافة، الريان الجديد، معيذر، السيلية وأبو هامور",
    "الوكرة": "الوكرة، الوكير، المشاف ومنطقة الميناء",
    "الخور": "الخور والذخيرة وسميسما",
    "أم صلال": "أم صلال محمد، أم صلال علي والخيسة",
    "الشمال": "الرويس والشمال وحدود الدولة الشمالية",
    "الظعاين": "الظعاين، أم قرن ولوسيل الشمالية",
    "الشحانية": "الشحانية، الوجبة وغرب الريان",
    "لوسيل": "مارينا لوسيل، قطيفان واللؤلؤة المجاورة",
}

PRIORITY_SLUG = [
    "water-leak", "leak-detection", "تسرب",
    "roof-insulation", "insulation", "عزل",
    "ac-", "air-condition", "split", "تكييف", "مكيف",
    "pest", "cockroach", "termite", "حشرات", "صراصير", "رمة",
    "sewer", "drain", "plumb", "مجاري", "سباك",
    "home-cleaning", "villa-cleaning", "تنظيف",
    "tank", "waterproof", "خزان",
    "general-maintenance", "building-maintenance", "صيانة",
]

SKIP_DRAFT = ("شحن", "shipping", "دولي", "international-shipping", "cargo")
# Ranking page — never rewrite, retitle, reslug, or unpublish.
LOCKED_POST_IDS = {2973}
# City clones of the ranking leak URL — keep draft; never schedule/publish.
LEAK_CLONE_IDS = {
    11132, 11133, 11134, 11135, 11136, 11137, 11138, 11139,
    12693, 12694, 12695, 12696, 12697, 12698, 12699, 12700,
}


def is_water_leak_clone(title: str, slug: str, pid: int = 0) -> bool:
    if int(pid) in LOCKED_POST_IDS or int(pid) == 12866:
        return False
    slug = slug or ""
    title = title or ""
    if "qatar-en" in slug or "without breaking" in title.lower():
        return False
    blob = title + " " + slug
    if any(x in blob for x in ("الغاز", "التكييف", "المسبح", "gas-leak", "ac-leak", "pool-leak")):
        return False
    return (
        "كشف تسربات المياه في" in title
        or "كشف تسريبات مواسير" in title
        or slug.startswith("water-leak-detection-")
        or slug.startswith("water-pipe-leak-detection-")
    )

EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\u2600-\u27BF"
    "\uFE0F"
    "]+",
    flags=re.UNICODE,
)


def api(path, method="GET", data=None, timeout=90):
    url = path if path.startswith("http") else BASE + path
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
            raw = r.read().decode() or "null"
            try:
                return r.status, json.loads(raw), {k.lower(): v for k, v in r.headers.items()}
            except json.JSONDecodeError:
                return r.status, raw, {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = raw[:500]
        return e.code, parsed, {}


def get_all_posts(status, fields="id,slug,status,title,date,link"):
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
        time.sleep(0.05)
    return items


def rm_meta(post_id, title=None, description=None, keyword=None, robots=None, object_type="post"):
    if int(post_id) in LOCKED_POST_IDS:
        print(f"SKIP locked ranking SEO {post_id}", flush=True)
        return
    meta = {}
    if title:
        meta["rank_math_title"] = title
    if description:
        meta["rank_math_description"] = description
    if keyword:
        meta["rank_math_focus_keyword"] = keyword
    if robots:
        meta["rank_math_robots"] = robots
    if not meta:
        return
    api(
        "/rankmath/v1/updateMeta",
        "POST",
        {"objectType": object_type, "objectID": int(post_id), "meta": meta},
    )


def cta():
    return (
        f'<p><a href="https://wa.me/{WA}?text={urllib.parse.quote("مرحباً، أريد الاستفسار عن خدمات ركن التطور في قطر")}">'
        f"واتساب مباشر</a></p>"
    )


def city_block(city: str, service: str) -> str:
    areas = CITIES.get(city, "الدوحة وباقي مدن قطر")
    return (
        f"<h2>تغطية {service} في {city} وقطر</h2>"
        f"<p>فريق ركن التطور مقيم في الدوحة ويصل إلى {city} وباقي مدن الدولة. "
        f"من الأحياء التي نغطيها حول {city}: {areas}. "
        f"المناخ الحار والرطوبة في قطر يجعلان التسرب والعزل والتكييف والصيانة الدورية أكثر إلحاحاً من مناطق معتدلة، "
        f"وعداد كهرماء يكشف غالباً الاستهلاك غير المبرر قبل ظهور البقع على الجدران.</p>"
    )


def sanitize_html(html: str, title: str, city: str | None = None) -> str:
    if not html:
        return html
    html = html.replace("{PHONE_RUKN_QATAR}", PHONE)
    html = html.replace("{WHATSAPP_RUKN_QATAR}", WA)
    html = html.replace("معاينة مجانية", "معاينة ميدانية ثم عرض سعر مكتوب")
    html = html.replace("أغسطس 2026", "سبتمبر 2026")
    html = html.replace("مارس 2026", "سبتمبر 2026")
    html = html.replace("Exmaple", "مثال")
    html = html.replace("المياة", "المياه")
    html = html.replace("Tatwwar", "Tatawer")
    html = html.replace("المجموعه المتحده للخدمات المتكاملة", "شركة ركن التطور")
    html = html.replace("الخيثة", "الخيسة")
    html = html.replace("المشحمية", "الشحانية")
    html = html.replace("971586634710", WA)
    html = html.replace("201151481000", WA)
    html = re.sub(r'src="service-\d+(?:-\d+)?\.webp"', f'src="{IMG}"', html)
    html = re.sub(
        r'src="(?!https?:)([a-z0-9\-]+\.webp)"',
        f'src="{IMG}"',
        html,
        flags=re.I,
    )
    html = re.sub(r"<h1[^>]*>.*?</h1>", "", html, count=1, flags=re.I | re.S)
    def strip_heading_emoji(m):
        inner = EMOJI_RE.sub("", m.group(2))
        inner = re.sub(r"\s+", " ", inner).strip(" –-")
        return f"<h{m.group(1)}>{inner}</h{m.group(1)}>"

    html = re.sub(r"<h([1-6])[^>]*>(.*?)</h\1>", strip_heading_emoji, html, flags=re.I | re.S)
    html = html.replace("الأسرع والأكثر ضماناً في قطر", "بتشخيص قبل الإصلاح في قطر")
    html = html.replace("خدمة فورية وضمان حقيقي 2026", "عرض سعر مكتوب ومتابعة بعد التسليم")
    html = html.replace("لماذا اختيار الشركة المناسبة يصنع الفرق؟", "متى تحتاج الخدمة في قطر؟")
    html = re.sub(r"https://img\.youtube\.com/vi/[^\"']+", IMG, html)
    if city and city_block(city, title) and city not in html[:800]:
        html = city_block(city, title) + html
    if "wa.me/971586634710" not in html:
        html += cta()
    return html


def detect_city(title: str, slug: str) -> str | None:
    blob = title + " " + slug
    mapping = [
        ("لوسيل", "لوسيل"),
        ("al-daayen", "الظعاين"),
        ("الظعاين", "الظعاين"),
        ("al-shahaniya", "الشحانية"),
        ("الشحانية", "الشحانية"),
        ("al-shamal", "الشمال"),
        ("الشمال", "الشمال"),
        ("umm-salal", "أم صلال"),
        ("أم صلال", "أم صلال"),
        ("al-khor", "الخور"),
        ("الخور", "الخور"),
        ("al-wakrah", "الوكرة"),
        ("الوكرة", "الوكرة"),
        ("al-rayyan", "الريان"),
        ("الريان", "الريان"),
        ("doha", "الدوحة"),
        ("الدوحة", "الدوحة"),
    ]
    for key, city in mapping:
        if key in blob:
            return city
    if "قطر" in title:
        return "الدوحة"
    return None


def excerpt_from(title: str) -> str:
    return (
        f"{title} مع فريق ركن التطور في قطر: تشخيص قبل الإصلاح، تقرير واضح، "
        f"وعرض سعر مكتوب. نغطي الدوحة ولوسيل والريان والوكرة وباقي مدن الدولة."
    )[:160]


def leak_article_ar():
    return f"""
<p>تسرب المياه في فلل وشقق قطر غالباً لا يظهر كبركة على الأرض. يظهر أولاً كقفزة في فاتورة <strong>كهرماء</strong>، أو تزهير أبيض على السيراميك، أو رائحة رطوبة في الطابق الأرضي، أو تقشير دهان بعد الصيف. ركن التطور يكشف المصدر بأجهزة حرارية وصوتية قبل أي تكسير، ثم يصلح الموضع بعد أن ترى التقرير.</p>
{cta()}
<h2>علامات تسرب المياه في منازل قطر</h2>
<p>الحرارة والرطوبة في الدوحة ولوسيل والريان تسرّع تمدد مواسير التغذية والانكماش بعد التكييف. إذا دار العداد والمضخة تعمل وكل المحابس مغلقة، فالمشكلة في الشبكة أو الخزان أو الري المخفي وليس في «الاستهلاك الطبيعي».</p>
<ul>
<li>ارتفاع مفاجئ في فاتورة كهرماء دون تغيّر الاستخدام.</li>
<li>بقع رطوبة أو عفن أسود خلف الخزائن وفي زوايا الحمامات.</li>
<li>هبوط بلاط الحوش أو تفكك الجبس تحت دورات المياه.</li>
<li>صوت مياه داخل الجدار مع إغلاق المحابس.</li>
<li>تغير لون ماء الخزان الأرضي أو انخفاض منسوبه دون تفسير.</li>
</ul>
<h2>كيف نكشف التسرب بدون تكسير؟</h2>
<ol>
<li>عزل أجزاء الشبكة وقياس الضغط.</li>
<li>مسح حراري للجدران والأرضيات والأسقف.</li>
<li>التقاط صوت التسرب بأجهزة أكوافون عند الحاجة.</li>
<li>تحديد نقطة الإصلاح وتوثيقها بصور قبل الفتح.</li>
<li>إصلاح موضعي ثم إعادة الفحص — لا تكسير عشوائي بحثاً عن المصدر.</li>
</ol>
<img src="{IMG}" alt="كشف تسربات المياه في قطر بالكاميرا الحرارية" width="800" height="450" />
<h2>التسرب في الدوحة ولوسيل والريان والوكرة</h2>
<p>في أبراج لوسيل واللؤلؤة الشائع هو تسرب التكييف المركزي والدكتات. في فلل الريان والوعب والغرافة الشائع مواسير الحوش والخزان الأرضي. في الوكرة والوكرة الساحلية الرطوبة تخفي التسرب خلف العزل القديم. نغطي أيضاً أم صلال والخيسة والخور والظعاين والشحانية.</p>
<h2>بعد الكشف: إصلاح وعزل إن لزم</h2>
<p>الكشف وحده لا يكفي إن بقي الجدار رطباً. بعد تحديد المصدر نصلح الماسورة أو العوامة أو تسرب المسبح، ثم نعالج الرطوبة ونقترح عزل الحمام أو الخزان إذا كان هو السبب المتكرر. السعر يُكتب بعد المعاينة لأن الحالة ليست واحدة.</p>
<h2>أسئلة شائعة</h2>
<h3>هل الكشف بدون تكسير مناسب للرخام والبورسلين؟</h3>
<p>نعم. الهدف هو تحديد النقطة أولاً حتى لا يُكسر بلاط واسع. الفتح يكون موضعياً بعد التقرير.</p>
<h3>هل ارتفاع فاتورة كهرماء يعني تسرباً دائماً؟</h3>
<p>ليس دائماً. قد تكون عوامة الخزان أو سيفون المرحاض أو المكيف. الفحص يفرّق بين الأسباب قبل أي إصلاح.</p>
<h3>هل تعملون خارج الدوحة؟</h3>
<p>نعم. المقر الدوحة والتغطية تشمل لوسيل والريان والوكرة والخور وأم صلال وباقي مدن قطر.</p>
<h2>اطلب معاينة</h2>
<p>لا نسعّر عبر رسالة واحدة دون فهم الموقع. اتصل أو راسل واتساب لتحديد موعد المعاينة، واستلم مصدر المشكلة وعرض السعر مكتوباً قبل التنفيذ.</p>
{cta()}
"""


def roof_article_ar():
    return f"""
<p>عزل الأسطح في قطر ليس «طبقة إضافية للشكل». هو حماية من حرارة الصيف وتسرب الأمطار النادرة والتكثف فوق الخزانات العلوية. الرطوبة تتسرب من البلاط القديم والمفاصل، فتهبط إلى الأسقف الداخلية وتتلف الجبس والدهان. ركن التطور يعاين الميل والصرف وحالة العزل الحالي ثم يختار الفوم أو الأغشية أو الطلاء الحراري حسب السطح لا حسب عرض جاهز.</p>
{cta()}
<h2>متى يحتاج سطح الفيلا أو المبنى عزلاً جديداً؟</h2>
<ul>
<li>ارتفاع حرارة الغرف العلوية رغم عمل المكيف.</li>
<li>تقرحات أو انتفاخ في سقف الدور الأخير.</li>
<li>تجمع مياه حول عمود المكيف أو قاعدة الخزان.</li>
<li>عزل قديم متشقق بعد صيف أو اثنين في الدوحة والريان.</li>
</ul>
<img src="{IMG}" alt="عزل أسطح في قطر" width="800" height="450" />
<h2>الفوم والأغشية والطلاء الحراري</h2>
<p>الفوم البولي يوريثان يناسب الأسطح غير المنتظمة ويقلل انتقال الحرارة. الأغشية البيتومينية المعدّلة تناسب الأسطح التي تحتاج طبقة مقاومة ماء واضحة عند الصرف. الطلاء العاكس يساعد على خفض الحرارة لكنه لا يغني عن معالجة الميل والمياه الراكدة. نوضح الخيار في المعاينة لأن خلط الأنظمة دون أساس نظيف يفشل سريعاً في مناخ قطر.</p>
<h2>الأسطح في الدوحة ولوسيل مقابل الفلل</h2>
<p>أسطح الأبراج والملاحق في لوسيل تختلف عن فلل معيذر والوكرة: مساحة الصرف، وجود الألواح الشمسية، وخزانات السطح. ننسّق العمل حتى لا يُعطل التكييف أو يُحاصر العزل تحت معدات لا تُرفع.</p>
<h2>الأسئلة الشائعة</h2>
<h3>هل العزل الحراري يغني عن العزل المائي؟</h3>
<p>لا. الحرارة والماء مشكلتان مختلفتان. كثير من الأسطح في قطر يحتاج الاثنين معاً بعد إصلاح الميل.</p>
<h3>كم تدوم الطبقة؟</h3>
<p>العمر يعتمد على الخامة والصيانة ومشي العمال على السطح. نوضح ذلك في عرض السعر مكتوبًا ولا نعد بـ«مدى الحياة».</p>
{cta()}
"""


def en_leak():
    return f"""
<p>Hidden water leaks in Qatar villas and apartments often show up first as a jump on the <strong>Kahramaa</strong> bill, salt marks on tiles, or a damp smell on the ground floor — not as a visible puddle. Rukn El Tatawer locates the source with thermal and acoustic tools before any breaking, then repairs the spot after you see the report.</p>
<p><a href="https://wa.me/{WA}">WhatsApp</a></p>
<h2>Leak signs in Doha, Lusail and Al Rayyan</h2>
<ul>
<li>Meter still running with every tap closed.</li>
<li>Peeling paint or black mould in bathrooms and behind cabinets.</li>
<li>Sunken courtyard tiles or damaged gypsum under wet rooms.</li>
<li>Ground tank level dropping or water changing colour.</li>
</ul>
<h2>How we detect leaks without breaking</h2>
<p>We isolate sections, check pressure, scan walls and floors thermally, and only open a small area after the source is documented. Coastal humidity in Wakrah and high-rise AC ducts in Lusail need a different path than a villa courtyard pipe in Al Waab.</p>
<h2>Coverage</h2>
<p>Based in Doha, we cover Lusail, Al Rayyan, Al Wakrah, Al Khor, Umm Salal, Al Daayen, Al Shamal and Al Shahaniya. Pricing is written after the site visit — not guessed on the phone.</p>
"""


def services_bodies():
    return {
        1877: (
            "كشف تسربات المياه",
            f"<p>كشف تسربات المياه في قطر بدون تكسير عشوائي: كاميرا حرارية، قياس ضغط، وتقرير يوضح المصدر قبل الإصلاح. نغطي الدوحة ولوسيل والريان والوكرة وباقي المدن.</p>{cta()}",
        ),
        1879: (
            "عزل الأسطح والخزانات",
            f"<p>عزل مائي وحراري للأسطح والخزانات والحمامات بما يناسب مناخ قطر. المعاينة تحدد الفوم أو الأغشية أو معالجة الميل قبل أي طبقة جديدة.</p>{cta()}",
        ),
        1866: (
            "إنشاء وصيانة المباني",
            f"<p>صيانة عامة للمباني والفلل في قطر: شروخ، ترميم بعد الرطوبة، وعقود متابعة. التشخيص قبل الإصلاح وعرض سعر مكتوب.</p>{cta()}",
        ),
        1883: (
            "صيانة وتركيب المكيفات",
            f"<p>غسيل وصيانة سبليت ومركزي، شحن فريون وكشف أعطال الدكتات قبل صيف قطر. نعمل في الدوحة وكل المدن التي نغطيها.</p>{cta()}",
        ),
        1881: (
            "تسليك المجاري",
            f"<p>تسليك انسدادات المجاري وشفط البيارات مع فحص بالكاميرا عند الحاجة. لا نعالج العرض فقط إذا كان السبب كسر أو تكرار في الشبكة.</p>{cta()}",
        ),
        1885: (
            "تنظيف وتعقيم",
            f"<p>تنظيف منازل وفلل وخزانات وتعقيم مناسب للاستخدام السكني في قطر، بعد معاينة المساحة ونوع التشطيب.</p>{cta()}",
        ),
        1887: (
            "مكافحة الحشرات",
            f"<p>مكافحة حشرات مرخّصة في قطر: صراصير، بق فراش، رمّة وقوارض، مع توضيح المادة ومدة المتابعة قبل التنفيذ.</p>{cta()}",
        ),
        1870: (
            "تنسيق الحدائق",
            f"<p>حدائق وعشب صناعي وشبكات ري تناسب الحرارة والملوحة في قطر، لا نسخ تصميم لا يعيش في الدوحة.</p>{cta()}",
        ),
        1868: (
            "إنشاء وصيانة المسابح",
            f"<p>إنشاء وصيانة ومعالجة مياه المسابح المنزلية في قطر، مع كشف تسرب الحوض عند انخفاض المنسوب غير المبرر.</p>{cta()}",
        ),
        1874: (
            "تركيب جبس بورد",
            f"<p>جبس بورد وأسقف داخلية بعد التأكد من جفاف السطح — لا نغطي على رطوبة غير معالجة.</p>{cta()}",
        ),
        1872: (
            "تركيب الباركيه",
            f"<p>أرضيات خشب وباركيه في بيئة قطر الجافة المكيفة، مع التنبيه إذا كانت الرطوبة الأرضية غير مناسبة للتركيب.</p>{cta()}",
        ),
        1876: (
            "عازل الصوت",
            f"<p>عزل صوتي للجدران والأسقف حسب استخدام الغرفة، بعد معاينة التشطيب القائم.</p>{cta()}",
        ),
    }


def score_draft(title: str, slug: str) -> int:
    t = (title + " " + slug).lower()
    score = 0
    city_w = {
        "doha": 80, "الدوحة": 80, "al-rayyan": 50, "الريان": 50,
        "al-wakrah": 40, "الوكرة": 40, "al-khor": 30, "umm-salal": 30,
        "al-daayen": 20, "al-shamal": 15, "al-shahaniya": 15,
    }
    for k, w in city_w.items():
        if k in t:
            score += w
            break
    for i, key in enumerate(PRIORITY_SLUG):
        if key.lower() in t:
            score += 100 - i
            break
    return score


def update_post(pid, **kwargs):
    if int(pid) in LOCKED_POST_IDS:
        print(f"SKIP locked ranking post {pid}", flush=True)
        return 0, {"skipped": True}, {}
    return api(f"/wp/v2/posts/{pid}", "POST", kwargs)


def main():
    log = []
    def note(msg):
        print(msg, flush=True)
        log.append(msg)

    # Cities taxonomy
    for slug, name in [
        ("doha", "الدوحة"), ("lusail", "لوسيل"), ("al-rayyan", "الريان"),
        ("al-wakrah", "الوكرة"), ("al-khor", "الخور"), ("umm-salal", "أم صلال"),
        ("al-daayen", "الظعاين"), ("al-shamal", "الشمال"), ("al-shahaniya", "الشحانية"),
        ("al-kheesa", "الخيسة"),
    ]:
        code, data, _ = api("/wp/v2/cities", "POST", {"name": name, "slug": slug})
        note(f"city {name}: {code}")

    # Post 2973 (كشف تسربات المياه في قطر) is LOCKED — ranking page, do not rewrite.

    roof_html = roof_article_ar()
    code, data, _ = update_post(
        10324,
        content=roof_html,
        excerpt=excerpt_from("عزل أسطح في قطر"),
        comment_status="closed",
        ping_status="closed",
        featured_media=2471,
    )
    rm_meta(
        10324,
        title="عزل أسطح في قطر | فوم وحراري ومائي — ركن التطور",
        description="عزل أسطح الفلل والمباني في الدوحة وقطر: فوم، أغشية، وطلاء حراري بعد معاينة الميل والصرف. عرض سعر مكتوب.",
        keyword="عزل أسطح في قطر",
        robots=["index", "follow"],
    )
    note(f"flagship roof {code}")

    # Duplicate handling
    duplicates = [
        (10334, 10258),  # cleaning keep 10258
        (10357, 10272),  # cockroach keep older
        (10377, 3182),   # sewer: keep doha unique-ish 3182? keep qatar 10377 as national, redirect doha stays but cleaned
    ]
    # Trash off-brand
    trash_ids = [7391, 10370, 10371, 10372, 10373, 10374, 10368, 10369]
    for pid in trash_ids:
        code, data, _ = api(f"/wp/v2/posts/{pid}", "DELETE", {"force": False})
        note(f"trash {pid}: {code}")
        rm_meta(pid, robots=["noindex", "nofollow"])

    # Redirects
    redirects = [
        ("recruitment-in-qatar", "https://www.rukn-eltatawer.com/qa/"),
        ("roof-insulation", "https://www.rukn-eltatawer.com/qa/shrkh-azl-asth-fy-qtr/"),
        ("shrkh-tnzyf-mnazl-fy-qtr-2", "https://www.rukn-eltatawer.com/qa/house-cleaning-in-qatar/"),
        ("shrkh-mkafhh-srasyr-fy-qtr", "https://www.rukn-eltatawer.com/qa/cockroach-control-in-qatar/"),
        ("shra-skrab-fy-qtr", "https://www.rukn-eltatawer.com/qa/"),
    ]
    for frm, to in redirects:
        code, data, _ = api("/rukn-qa/v1/redirect", "POST", {"from": frm, "to": to})
        note(f"redirect {frm}: {code} {data}")

    # Merge cleaning: noindex duplicate if not trashed
    code, data, _ = update_post(10334, status="draft")
    note(f"unpublish dup cleaning {code}")
    code, data, _ = update_post(10357, status="draft")
    note(f"unpublish dup cockroach {code}")

    # Fix remaining sewer doha typo via sanitize later

    # Pages
    pages = {
        7465: (
            "المدن التي نغطيها في قطر",
            """
<p>مقر ركن التطور في الدوحة، والفريق يصل إلى لوسيل والريان والوكرة والخور وأم صلال والخيسة والظعاين والشمال والشحانية. الخدمة لا تتوقف على اسم المدينة في القائمة: راسلنا إذا كان موقعك في منطقة أخرى داخل قطر.</p>
<h2>الدوحة ولوسيل</h2>
<p>أبراج وشقق وفلل: كشف تسربات، تكييف مركزي، وعزل أسطح الملاحق. أحياء متكررة: الخليج الغربي، اللؤلؤة، لقطيفية، مارينا لوسيل.</p>
<h2>الريان والوكرة والخور</h2>
<p>فلل وحوش وخزانات أرضية أكثر من الأبراج. العزل والتسليك ومكافحة الرمّة طلبات شائعة.</p>
<h2>أم صلال والظعاين والشمال والشحانية</h2>
<p>نصل بالتنسيق المسبق. زمن الزيارة يُذكر في عرض الموعد بعد معرفة العنوان.</p>
""",
        ),
        7461: (
            "اتصل بنا — ركن التطور قطر",
            f"""
<p>للتواصل مع ركن التطور في قطر استخدم واتساب من أزرار الموقع. المعاينة في الموقع، ثم تقرير وعرض سعر مكتوب. لا نثبت سعراً نهائياً عبر رسالة دون فهم الحالة.</p>
<p>البريد: info@rukn-eltatawer.com</p>
<p>نطاق العمل: الدوحة وجميع المدن التي نغطيها داخل قطر.</p>
{cta()}
""",
        ),
        7460: (
            "من نحن — ركن التطور في قطر",
            """
<p>ركن التطور شركة خدمات منزلية تعمل في قطر: كشف تسربات المياه، عزل، صيانة عامة، تكييف، سباكة وتسليك، تنظيف، مكافحة حشرات، حدائق ومسابح، وطاقة شمسية. الفكرة بسيطة: نشخّص قبل أن نفتح الجدار أو نغيّر الخامة، ونكتب التكلفة قبل التنفيذ.</p>
<p>الفريق مقيم في الدوحة ويعرف طبيعة الفلل والأبراج ومناخ الدولة، لا نماذج مستوردة من سوق آخر باسم المدينة فقط.</p>
""",
        ),
        2453: (
            "مدونة ركن التطور قطر",
            "<p>نصائح عملية لكشف التسربات والعزل والصيانة والتكييف في منازل قطر — مكتوبة لسكان الدوحة وباقي المدن، لا محتوى عام منسوخ.</p>",
        ),
        7463: (
            "خدمات ركن التطور في قطر",
            """
<p>الخدمات الأساسية: كشف التسربات، العزل، الصيانة العامة، التكييف والكهرباء، السباكة والتسليك، التنظيف، مكافحة الحشرات، الحدائق والمسابح، التشطيب والدهانات، والطاقة الشمسية.</p>
<p>كل خدمة تبدأ بمعاينة أو وصف دقيق للحالة، ثم عرض مكتوب. التفاصيل في مقالات الخدمات وصفحات المدن.</p>
""",
        ),
        7467: (
            "الأسئلة الشائعة",
            f"""
<h2>هل تكشفون التسرب بدون تكسير؟</h2>
<p>نعم، بالأجهزة أولاً ثم فتح موضعي بعد التقرير.</p>
<h2>هل التسعير عبر الهاتف؟</h2>
<p>لا نثبت سعر الحالة النهائية دون معاينة أو بيانات كافية عن الموقع.</p>
<h2>كيف أتواصل؟</h2>
<p>واتساب من الزر العائم أو من داخل الصفحات. زر الاتصال مخفي مؤقتاً.</p>
""",
        ),
        8990: (
            "Contact Rukn El Tatawer in Qatar",
            f"""
<p>Contact us on WhatsApp for leak detection, insulation, AC and general maintenance in Doha and across Qatar. Site visit first, then a written quote.</p>
<p>Email: info@rukn-eltatawer.com</p>
""",
        ),
    }
    for pid, (title, content) in pages.items():
        code, data, _ = api(f"/wp/v2/pages/{pid}", "POST", {
            "title": title,
            "content": content,
            "comment_status": "closed",
            "ping_status": "closed",
        })
        rm_meta(pid, title=f"{title} | ركن التطور قطر", description=excerpt_from(title), object_type="post")
        note(f"page {pid}: {code}")

    # Service CPT
    for sid, (title, body) in services_bodies().items():
        code, data, _ = api(f"/wp/v2/services/{sid}", "POST", {
            "title": title,
            "content": body,
            "comment_status": "closed",
        })
        rm_meta(sid, title=f"{title} في قطر | ركن التطور", description=excerpt_from(title), keyword=title, object_type="post")
        note(f"service {sid}: {code}")

    # English core posts
    en_posts = [
        {
            "title": "Water leak detection in Qatar without breaking",
            "slug": "water-leak-detection-qatar-en",
            "content": en_leak(),
            "excerpt": "Thermal leak detection in Doha and Qatar without random breaking. Written quote after the visit.",
            "keyword": "water leak detection Qatar",
        },
        {
            "title": "Roof insulation in Qatar",
            "slug": "roof-insulation-qatar-en",
            "content": f"<p>Roof waterproofing and heat insulation for Qatar villas and buildings: foam, membranes or reflective coating after checking slope and drainage — not a one-product pitch.</p><p><a href='https://wa.me/{WA}'>WhatsApp</a></p>",
            "excerpt": "Roof insulation in Doha and Qatar after a site inspection. Heat and waterproofing are specified separately.",
            "keyword": "roof insulation Qatar",
        },
        {
            "title": "AC maintenance in Doha and Qatar",
            "slug": "ac-maintenance-qatar-en",
            "content": f"<p>Split and packaged AC service before the Qatar summer: coil cleaning, refrigerant check and duct issues that raise Kahramaa bills. Based in Doha, covering Lusail, Al Rayyan and Al Wakrah.</p><p><a href='https://wa.me/{WA}'>WhatsApp</a></p>",
            "excerpt": "Air conditioning maintenance in Qatar before peak summer load. Inspection then a written quote.",
            "keyword": "AC maintenance Doha",
        },
    ]
    for p in en_posts:
        code, data, _ = api("/wp/v2/posts?lang=en", "POST", {
            "title": p["title"],
            "slug": p["slug"],
            "content": p["content"],
            "excerpt": p["excerpt"],
            "status": "publish",
            "comment_status": "closed",
            "ping_status": "closed",
            "featured_media": 2471,
        })
        pid = data.get("id") if isinstance(data, dict) else None
        if pid:
            rm_meta(pid, title=f"{p['title']} | Rukn El Tatawer Qatar", description=p["excerpt"], keyword=p["keyword"])
        note(f"en post {p['slug']}: {code} id={pid}")

    # Menu: roof insulation URL
    code, data, _ = api("/wp/v2/menu-items/10511", "POST", {
        "url": "https://www.rukn-eltatawer.com/qa/shrkh-azl-asth-fy-qtr/",
        "title": "عزل الأسطح",
    })
    note(f"menu roof {code}")

    # Bulk published (except already rewritten / trashed)
    skip = set(trash_ids + [2973, 10324, 10334, 10357])
    pubs = get_all_posts("publish", "id,slug,status,title,content,featured_media")
    note(f"published count {len(pubs)}")
    n = 0
    for p in pubs:
        pid = p["id"]
        if pid in skip:
            continue
        title = unescape((p.get("title") or {}).get("raw") or (p.get("title") or {}).get("rendered") or "")
        raw = (p.get("content") or {}).get("raw") or (p.get("content") or {}).get("rendered") or ""
        city = detect_city(title, p.get("slug") or "")
        new = sanitize_html(raw, title, city)
        payload = {"content": new, "comment_status": "closed", "ping_status": "closed", "excerpt": excerpt_from(title)}
        if not p.get("featured_media"):
            payload["featured_media"] = 2471
        code, data, _ = update_post(pid, **payload)
        rm_meta(
            pid,
            title=f"{title} | ركن التطور قطر",
            description=excerpt_from(title),
            keyword=title.replace("شركة ", "").strip(),
            robots=["index", "follow"],
        )
        n += 1
        if n % 20 == 0:
            note(f"cleaned published {n}")
        time.sleep(0.08)
    note(f"published cleaned {n}")

    # Drafts: fix + schedule
    drafts = get_all_posts("draft", "id,slug,status,title,content,featured_media")
    note(f"drafts {len(drafts)}")
    scored = []
    for p in drafts:
        title = unescape((p.get("title") or {}).get("raw") or (p.get("title") or {}).get("rendered") or "")
        slug = p.get("slug") or ""
        if any(k in title or k in slug for k in SKIP_DRAFT):
            continue
        if int(p["id"]) in LEAK_CLONE_IDS or is_water_leak_clone(title, slug, p["id"]):
            continue
        if slug.endswith((
            "-doha", "-al-rayyan", "-al-wakrah", "-al-khor", "-umm-salal",
            "-al-daayen", "-al-shamal", "-al-shahaniya", "-lusail",
        )):
            continue
        scored.append((score_draft(title, slug), p, title))
    scored.sort(key=lambda x: -x[0])
    note(f"drafts to schedule {len(scored)}")

    now = datetime.now(QATAR)
    published_one = False
    scheduled = 0
    for i, (sc, p, title) in enumerate(scored):
        pid = p["id"]
        raw = (p.get("content") or {}).get("raw") or ""
        city = detect_city(title, p.get("slug") or "")
        new = sanitize_html(raw, title, city)
        payload = {
            "content": new,
            "comment_status": "closed",
            "ping_status": "closed",
            "excerpt": excerpt_from(title),
        }
        if not p.get("featured_media"):
            payload["featured_media"] = 2471
        if not published_one:
            payload["status"] = "publish"
            payload["date"] = now.strftime("%Y-%m-%dT%H:%M:%S")
            published_one = True
            which = "PUBLISH NOW"
        else:
            when = now + timedelta(minutes=10 * scheduled)
            # first scheduled is +10 min after the one we just published; scheduled starts 0 then we increment after
            when = now + timedelta(minutes=10 * (scheduled + 1))
            payload["status"] = "future"
            payload["date"] = when.strftime("%Y-%m-%dT%H:%M:%S")
            which = f"FUTURE {payload['date']}"
            scheduled += 1
        code, data, _ = update_post(pid, **payload)
        rm_meta(
            pid,
            title=f"{title} | ركن التطور قطر",
            description=excerpt_from(title),
            keyword=title,
            robots=["index", "follow"],
        )
        if i < 8 or i % 50 == 0:
            note(f"{which} #{i} score={sc} {pid} {title} -> {code}")
        time.sleep(0.08)

    note(f"DONE published_now=1 scheduled={scheduled} skipped_shipping={len(drafts)-len(scored)}")
    with open("/tmp/wp-fix-log.txt", "w") as f:
        f.write("\n".join(log))


if __name__ == "__main__":
    main()
