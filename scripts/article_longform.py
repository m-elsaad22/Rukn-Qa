#!/usr/bin/env python3
"""Long-form Qatar national articles. Never used for post 2973."""
from __future__ import annotations

import hashlib
import re
from html import unescape

from kayan_article_builder import (
    ALL_CITIES,
    CITIES_HUB,
    LEAK,
    PACKS,
    SHORTCODES,
    _ul,
    article_image,
    build_theme_payload,
    classify,
    detect_city,
    pack_for,
    service_core,
    wa_url,
)

CITY_HUBS = {
    "الدوحة": "https://www.rukn-eltatawer.com/qa/services-in-doha-qatar/",
    "لوسيل": "https://www.rukn-eltatawer.com/qa/services-in-lusail-qatar/",
    "الريان": "https://www.rukn-eltatawer.com/qa/services-in-al-rayyan-qatar/",
    "الوكرة": "https://www.rukn-eltatawer.com/qa/services-in-al-wakrah-qatar/",
    "الخور": "https://www.rukn-eltatawer.com/qa/services-in-al-khor-qatar/",
    "أم صلال": "https://www.rukn-eltatawer.com/qa/services-in-umm-salal-qatar/",
    "الظعاين": "https://www.rukn-eltatawer.com/qa/services-in-al-daayen-qatar/",
    "الشمال": "https://www.rukn-eltatawer.com/qa/services-in-al-shamal-qatar/",
    "الشحانية": "https://www.rukn-eltatawer.com/qa/services-in-al-shahaniya-qatar/",
}

CITY_BUILDINGS = {
    "الدوحة": "أبراج الخليج الغربي واللؤلؤة تختلط بفلل السد وعين خالد؛ الوصول أحياناً يحتاج تنسيقاً مع إدارة المبنى.",
    "لوسيل": "الشقق والتكييف المركزي أكثر من الحوش؛ الزيارة تُجدول مع معرفة البرج والدور.",
    "الريان": "فلل وحوش واسعة: الوعب والغرافة ومعيذر. الخزان الأرضي ومواسير الري جزء شائع من المعاينة.",
    "الوكرة": "مناخ ساحلي يزيد الرطوبة على الجدران والعزل القديم في الوكير والمشاف.",
    "الخور": "فلل ساحلية أبعد من الدوحة؛ زمن الوصول يُذكر بعد العنوان وليس وعداً بنفس الساعة.",
    "أم صلال": "فلل ومزارع سكنية في أم صلال والخيسة؛ الخزانات والري المخفي يظهران كثيراً.",
    "الظعاين": "توسع عمراني بين الفلل والمجمعات الجديدة قرب لوسيل الشمالية.",
    "الشمال": "الرويس والشمال أبعد تغطية؛ الموعد يُثبت مسبقاً مع توضيح زمن الطريق.",
    "الشحانية": "مساحات مفتوحة وأسطح واسعة غرب الريان؛ العزل والحدائق طلب متكرر بعد الصيف.",
}

CLIMATE = {
    "insulation": "سطح فيلا في قطر يمتص حرارة عالية معظم السنة. أي ميل ضعيف يحوّل الغمر بعد المطر أو غسيل السطح إلى بقع في الغرف العلوية. الملوحة قرب الوكرة ولوسيل تسرّع تشقق الأغشية الرخيصة.",
    "ac": "حمل التبريد في الدوحة والريان لا يشبه مناخاً معتدلاً. إهمال الفلتر والكويل قبل مايو يحوّل ضعفاً بسيطاً إلى عمل طارئ في ذروة كهرماء.",
    "plumbing": "تمدد وانكماش الليّات مع الحرارة يفتح تسريباً دقيقاً تحت البلاط قبل أن يظهر بركة. عداد كهرماء الذي يدور والمحابس مغلقة إشارة أقوى من رائحة خفيفة.",
    "sewer": "الدهون في مطابخ الفلل والبيارات غير المفرّغة أشهر من «انسداد عشوائي». الكاميرا تُستخدم عند التكرار لا في أول غرغرة بسيطة.",
    "pest": "الرطوبة المخفية تجذب الصراصير والرمة. رش عام دون تحديد النوع يهدئ يوماً ويعيد المشكلة في الأسبوع التالي.",
    "cleaning": "غبار الدوحة يدخل من النوافذ والمكيف. تنظيف بعد التشطيب غير التنظيف الدوري؛ الغرف والخامات تُكتب قبل وصول الفريق.",
    "garden": "العشب الطبيعي بلا ظل وري مدروس يصفر بسرعة. العشب الصناعي والري بالتنقيط يناسبان الشحانية والريان أكثر من نسخ حديقة أوروبية.",
    "pool": "الشمس ترفع تبخّر الماء، لكن الهبوط الليلي المنتظم ليس تبحراً فقط. افصل التعويض يوماً وراقب المنسوب قبل اتهام المضخة.",
    "paint": "الدهان فوق بقعة رطبة في مناخ قطر يتقشر خلال أسابيع. عالج المصدر ثم جهّز السطح.",
    "floor": "هبوط بلاط الحوش بعد الصيف يرتبط غالباً بغسل مفرط أو ري تحت القاعدة، لا بالبلاطة وحدها.",
    "kitchen": "حمامات الفلل تفقد عزلها قبل أن يظهر الماء للجار الأسفل. التبليط التجميلي فوق تسرب يعيد العمل مرتين.",
    "build": "الشروخ الشعرية من الحرارة تختلف عن شروخ هبوط. القائمة المكتوبة تمنع «صيانة عامة» بلا نهاية.",
    "elec": "الرطوبة في العلب الخارجية قرب الساحل تسرّع القصر. زيادة حمل المكيفات صيفاً تفصل القواطع إن كانت اللوحة قديمة.",
    "gasleak": "رائحة الغاز لا تُفحص بعود ثقاب. التهوية وإغلاق المصدر ثم الكشف بالجهاز.",
    "acleak": "ماء تحت الوحدة الداخلية قد يكون صرفاً مسدوداً لا تسرب فريون. الخلط بين المصدرين يهدر شحن الغاز.",
    "poolleak": "حوض بلا عزل سليم في حرارة قطر يفقد ماءً يومياً. الخطوط تُفحص بالضغط قبل تكسير التبليط.",
    "tankclean": "خزان أرضي في فيلا الريان يجمع رواسب أسرع إن تُرك بلا غطاء محكم. الطعم المتغير إشارة للتنظيف لا لإضافة معطر.",
    "duct": "دكت غير معزول في سقف مستعار يكوّن عفناً حول المخارج. الغسيل بالماء على الكهرباء خطأ شائع.",
    "outdoor": "أشعة UV في قطر تُتلف قماش المظلة الداخلي خلال موسم واحد. الخامة الخارجية شرط لا خيار جمالي.",
    "solar": "ظلال خزان أو دكت على السطح تخفض الإنتاج أكثر مما يظهر في كتالوج اللوح. الدراسة قبل الشراء.",
    "elevator": "غبار وحرارة غرفة الماكينة يسرّعان أعطال الأبواب. التشغيل بالقوة بعد التوقف يضاعف العطل.",
    "general": "الحرارة والرطوبة والغبار عوامل ثابتة في قطر. أي خدمة تُنفَّذ دون اعتبارها تعيد العطل بسرعة.",
}


def _pick(title: str, items: list[str]) -> list[str]:
    if not items:
        return []
    h = int(hashlib.md5(title.encode("utf-8")).hexdigest(), 16)
    start = h % len(items)
    return items[start:] + items[:start]


def word_count(html: str) -> int:
    text = unescape(re.sub(r"<[^>]+>", " ", html or ""))
    text = re.sub(r"\[/?[^\]]+\]", " ", text)
    return len([w for w in re.split(r"\s+", text) if w])


def _city_block(ptype: str, core: str) -> str:
    lines = []
    for city, note in CITY_BUILDINGS.items():
        hub = CITY_HUBS[city]
        extra = {
            "insulation": f"أسطح {city} تُفحص للميل والصرف قبل الخامة.",
            "ac": f"في {city} نحدد إن كانت الوحدات سبليت أو مركزية قبل جدولة الفريق.",
            "sewer": f"بيارات وخطوط {city} تختلف عمقاً ووصولاً؛ الكاميرا عند التكرار.",
            "plumbing": f"ضغط الشبكة في {city} ليس واحداً بين فيلا وبرج.",
            "pest": f"نوع الحشرة في {city} يُحدد المادة؛ لا رش موحّد.",
            "cleaning": f"نطاق التنظيف في {city} يُكتب غرفة غرفة.",
        }.get(ptype, f"{core} في {city} تُجدول بعد العنوان ووصف العطل.")
        lines.append(f'<li><a href="{hub}">{city}</a>: {note} {extra}</li>')
    return (
        "<h2>التغطية في مدن قطر — بلا نسخ متطابقة</h2>"
        f"<p>لا ننشئ مقالاً مكرراً لـ«{core}» في كل مدينة. الخدمة وطنية، وصفحة المدينة تشرح المباني فقط.</p>"
        f"<ul>{''.join(lines)}</ul>"
        f'<p>دليل المدن: <a href="{CITIES_HUB}">المدن التي نغطيها في قطر</a>. '
        f'كشف تسربات المياه للدولة في مقال واحد: <a href="{LEAK}">شركة كشف تسربات المياه في قطر</a>.</p>'
    )


def _long_faq(title: str, city: str, pack: dict, core: str) -> str:
    items = [
        (f"هل {title} تشمل المعاينة؟", "نعم. لا نسعّر الحالة النهائية عبر رسالة قصيرة. المعاينة أو وصف دقيق بالصور ثم عرض مكتوب."),
        (f"هل تعملون {core} خارج الدوحة؟", f"نعم بالتنسيق في { '، '.join(ALL_CITIES) }. زمن الطريق يُذكر بعد العنوان."),
        ("هل يوجد ضمان؟", "يُذكر في العرض حسب نوع العمل والخامة. لا نكتب ضماناً عاماً في المقال."),
        ("كم المدة؟", "تُقدَّر بعد التشخيص. الزيارة القصيرة غير ترميم الحمام أو عزل سطح كامل."),
        ("هل تخترعون أسعاراً ثابتة؟", "لا. عوامل التكلفة في الجدول أدناه، والرقم يُكتب بعد فهم الموقع."),
        ("ماذا أحضّر؟", "العنوان، صور العطل، وأي وصول خاص (حارس، إدارة برج، مفتاح السطح)."),
        ("هل تفتحون الجدار مباشرة؟", "التشخيص أولاً. أي فتح يُذكر في النطاق قبل التنفيذ."),
        ("كيف التواصل؟", "واتساب من زر الصفحة. زر الاتصال الهاتفي مخفي مؤقتاً."),
        (f"هل {core} يحتاج زيارات متعددة؟", "بعض الأعمال مثل البق أو العزل المرحلي تحتاج جدولاً. ذلك يُوضح قبل البدء."),
        ("هل تنسخون نفس النص لكل خدمة؟", f"هذه الصفحة عن {title} تحديداً. باقي الخدمات لها صفحاتها الوطنية."),
    ]
    out = ["<h2>أسئلة شائعة حول هذه الخدمة</h2>"]
    for q, a in items:
        out.append(f'<div class="faq-item"><h3>{q}</h3><p>{a}</p></div>')
    return "\n".join(out)


def _build_en_long(title: str, slug: str) -> tuple[str, str, str]:
    city = detect_city(title, slug)
    ptype, pack = pack_for(title, slug, "en")
    wa = wa_url(title)
    img = article_image(ptype)
    alt = f"{title} — Rukn El Tatawer Qatar"
    cities = "Doha, Lusail, Al Rayyan, Al Wakrah, Al Khor, Umm Salal, Al Daayen, Al Shamal and Al Shahaniya"
    html = f"""
<div class="rukn-article">
<p><strong>{title}</strong> is a national Qatar service page from Rukn El Tatawer — not a copied city template. We inspect the site or review a clear photo description, then send a written scope before work starts. The team is based in Doha and visits {cities} by appointment.</p>
<section class="article-hero"><div class="hero-content">
<span class="hero-label">Qatar home services</span>
<h2>{title} — inspect, then write the scope</h2>
<p>WhatsApp the area and the fault. We do not give a final villa price from a short chat. Call buttons are hidden for now.</p>
<div class="hero-buttons"><a class="cta-button whatsapp-button" href="{wa}" rel="nofollow noopener" target="_blank"><i class="fab fa-whatsapp"></i> WhatsApp</a></div>
</div></section>
<p><img src="{img}" alt="{alt}" width="800" height="450" loading="eager" decoding="async"></p>
<h2>What this service means in Qatar</h2>
<p>{pack['what']} A villa in Al Rayyan is not a tower in West Bay. Access, materials and downtime change. Heat, humidity, dust and coastal salt around Wakrah and Lusail wear insulation, AC coils and pipe fittings faster than a mild climate. That is why we refuse one material or one visit length for every building.</p>
<p>If the visit shows that this service is not the real cause, we say so in the report and we do not continue unused work. Water leak detection for the whole country stays on one ranking page: <a href="{LEAK}">water leak detection in Qatar</a>. We do not clone that article per city.</p>
[post_features]
<h2>When to book</h2>
<p>Book when a sign keeps returning, not after a rumour. Typical triggers:</p>
{_ul(pack['when'])}
<p>If the sign appeared after the first summer on new finishing, after a roof wash, or with a jump in the Kahramaa bill, do not wait until paint peels or cooling fails completely. Delay in Qatar usually widens the scope.</p>
<h2>Signs we check on site</h2>
{_ul(pack['signs'])}
<blockquote class="warning-box"><i class="fas fa-exclamation-triangle"></i> <strong>Note:</strong> Hiding the fault with paint, daily water top-up or extra AC load removes evidence and raises the later cost.</blockquote>
<h2>Common causes after inspection</h2>
{_ul(pack['causes'])}
<h2>How we work</h2>
<p>We agree a time window, review what you sent, diagnose, and explain the next step before starting. If the scope changes — a local opening or a different material — work pauses until you approve the written change. Tools: {pack['tools']}</p>
[post_steps]
<h2>Mistakes that delay the fix</h2>
{_ul(pack['mistakes'])}
[post_call]
[post_prices]
[post_services]
<h2>Cities we cover — without duplicate articles</h2>
<p>We do not publish the same {title} text for every city. City hub pages explain building types; this page stays national.</p>
<ul>
<li><a href="{CITY_HUBS['الدوحة']}">Doha</a> — towers and villas; building management access is common.</li>
<li><a href="{CITY_HUBS['لوسيل']}">Lusail</a> — apartments and central AC more than courtyards.</li>
<li><a href="{CITY_HUBS['الريان']}">Al Rayyan</a> — villas, ground tanks and irrigation lines.</li>
<li><a href="{CITY_HUBS['الوكرة']}">Al Wakrah</a> — coastal humidity on old insulation.</li>
<li><a href="{CITY_HUBS['الخور']}">Al Khor</a> — longer travel; the window is set after the address.</li>
<li><a href="{CITY_HUBS['أم صلال']}">Umm Salal</a> — villas and farms, including Al Kheesa.</li>
<li><a href="{CITY_HUBS['الظعاين']}">Al Daayen</a> — newer compounds near north Lusail.</li>
<li><a href="{CITY_HUBS['الشمال']}">Al Shamal</a> — furthest north; booked in advance.</li>
<li><a href="{CITY_HUBS['الشحانية']}">Al Shahaniya</a> — wide roofs and gardens west of Rayyan.</li>
</ul>
<p>City index: <a href="{CITIES_HUB}">Qatar cities we cover</a>.</p>
<h2>What this page does not promise</h2>
<p>No invented star ratings, no fixed price list for every villa, and no phone call button for now. WhatsApp is enough to schedule the visit.</p>
<h2>After handover</h2>
<p>We tell you if this job needs a follow-up — seasonal AC wash, a flood test on insulation, or a second pest visit. Keep the written scope. If a new symptom appears that was not in the diagnosis, send photos before assuming the first visit failed.</p>
<h2>FAQ</h2>
<div class="faq-item"><h3>Is there a site visit?</h3><p>Yes, or a detailed photo description when that is enough to write a first scope.</p></div>
<div class="faq-item"><h3>Do you work outside Doha?</h3><p>Yes, by appointment across {cities}.</p></div>
<div class="faq-item"><h3>Is there a warranty?</h3><p>It is written in the quote for that job and material. We do not invent a site-wide warranty here.</p></div>
<div class="faq-item"><h3>How long is the visit?</h3><p>It depends on access and diagnosis. A time window is shared after we have the address — we do not promise a same-hour arrival to Al Shamal.</p></div>
<div class="faq-item"><h3>Will you break walls first?</h3><p>No. Diagnosis comes first. Any opening is listed in the quote before it happens.</p></div>
<div class="faq-item"><h3>How do I contact you?</h3><p>Use WhatsApp on this page. The call button is hidden temporarily.</p></div>
<div class="faq-item"><h3>Do you publish a city copy of this article?</h3><p>No. City hubs explain buildings. This page stays the national {title} page.</p></div>
<p>Coverage: {city}, Qatar. Related leak method if water is involved: <a href="{LEAK}">water leak detection in Qatar</a>.</p>
<h2>Summary</h2>
<p>{title} starts with diagnosis in Qatar’s climate, then a written scope. Message the area and building type on WhatsApp to book the visit. The ranking Arabic leak article is not rewritten from this English page.</p>
</div>
"""
    desc = f"{title} in Qatar. Inspection then a written quote. WhatsApp for timing in Doha and other cities."
    if len(desc) > 158:
        desc = desc[:155] + "…"
    return html.strip(), desc, title


def build_longform(title: str, slug: str, lang: str = "ar") -> tuple[str, str, str]:
    if lang == "en":
        return _build_en_long(title, slug)
    city = detect_city(title, slug)
    ptype, pack = pack_for(title, slug, "ar")
    core = service_core(title)
    wa = wa_url(title)
    img = article_image(ptype)
    alt = f"{title} — ركن التطور في قطر"
    climate = CLIMATE.get(ptype, CLIMATE["general"])
    focus = _pick(title, ALL_CITIES)
    focus_city = focus[0]
    rows = "".join(
        f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in pack["types"]
    )
    cmp_rows = "".join(
        f"<tr><td>{k}</td><td>{v}</td><td>عمل بلا تشخيص أو خامة لا تناسب مناخ قطر</td></tr>"
        for k, v in [
            ("التشخيص", f"نفهم مصدر مشكلة {core} قبل تغيير القطع"),
            ("النطاق", "عرض مكتوب بالبنود والمدة"),
            ("المناخ", "خامات وأدوات تحتمل الحرارة والرطوبة والغبار"),
            ("المتابعة", "نوضح ما يُراجع بعد التسليم إن لزم"),
        ]
    )
    when = _pick(title, list(pack["when"]))
    signs = _pick(title, list(pack["signs"]))
    causes = _pick(title, list(pack["causes"]))
    mistakes = _pick(title, list(pack["mistakes"]))
    loc = f" في {city}" if city and city != "قطر" and city not in title else ""
    html = f"""
<div class="rukn-article">
<p><strong>{title}</strong> خدمة وطنية من ركن التطور في قطر، لا نسخة مكررة لكل حي. {pack['what']} نبدأ بفهم العطل في الموقع أو من وصف وصور واضحة، ثم نكتب النطاق والتكلفة التقريبية قبل أي تنفيذ. المقر في الدوحة، والفريق يصل إلى { '، '.join(ALL_CITIES) } حسب الموعد. هذه الصفحة تشرح {core} كما يُنفَّذ في مباني قطر، لا كما يُنسخ من أسواق أخرى.</p>
<section class="article-hero">
<div class="hero-content">
<span class="hero-label">خدمات منزلية في قطر</span>
<h2>{title} — تشخيص ثم نطاق مكتوب</h2>
<p>صف الحي ونوع العطل على واتساب. لا سعر نهائي من رسالة دون معاينة أو وصف كافٍ.</p>
<div class="hero-buttons">
<a class="cta-button whatsapp-button" href="{wa}" rel="nofollow noopener" target="_blank"><i class="fab fa-whatsapp"></i> تواصل عبر واتساب</a>
</div></div></section>
<p><img src="{img}" alt="{alt}" width="800" height="450" loading="eager" decoding="async"></p>
<h2>ما المقصود بـ {title}؟</h2>
<p>{pack['what']} في التطبيق اليومي يعني أن الفني لا يحمل حلاً واحداً لكل فيلا. فيلا في {focus_city} غير شقة في برج الدوحة: الوصول، الخامة، ووقت التوقف عن التشغيل يختلفان. لذلك نسأل عن نوع المبنى، عمر التشطيب، وما جُرّب سابقاً. إن كان العطل يتكرر بعد «إصلاح سريع»، فغالباً عُولجت العلامة لا السبب.</p>
<p>ركن التطور يجمع خدمات المنزل تحت مسؤولية واحدة حتى لا يتنقل العميل بين سباك وعازل وفني تكييف بلا تنسيق. إن ظهر أثناء المعاينة أن {core} ليس المصدر، نوضح ذلك في التقرير ولا نكمل عملاً لا تحتاجه.</p>
[post_features]
<h2>متى تحتاج إلى {title}؟</h2>
<p>الطلب الصحيح يأتي بعد علامة ثابتة لا بعد إشاعة. راجع إن كان واحداً مما يلي يتكرر لديك:</p>
{_ul(when)}
<p>إن ظهرت العلامة بعد أول صيف على تشطيب جديد، أو بعد غسيل سطح، أو مع قفزة في فاتورة المياه أو الكهرباء، فلا تؤجل المعاينة إلى أن يتقشر الدهان أو يضعف التبريد تماماً. التأجيل في مناخ قطر يضاعف النطاق لا التكلفة فقط.</p>
<h2>علامات الفحص في مباني قطر</h2>
{_ul(signs)}
<blockquote class="warning-box"><i class="fas fa-exclamation-triangle"></i> <strong>تنبيه:</strong> إخفاء أثر {core} بالدهان أو بالتعويض اليومي للماء أو بزيادة تحميل المكيف يزيد التكلفة لاحقاً ويضيّع دليل المصدر.</blockquote>
<h2>لماذا يختلف التنفيذ في مناخ قطر؟</h2>
<p>{climate}</p>
<p>الغبار يدخل الدكتات والنوافذ. الملوحة قرب الساحل تضعف الحديد والعزل الرخيص. الحرارة تسرّع جفاف الخامات إن نُفذت في الظهيرة دون تجهيز. لذلك نرفض وعداً بـ«نفس الخامة لكل سطح» أو «نفس مدة الزيارة لكل فيلا». {CITY_BUILDINGS.get(focus_city, '')}</p>
<h2>الأسباب التي نراها بعد المعاينة</h2>
{_ul(causes)}
<p>السبب لا يُحسم من عنوان المقال. صورة واحدة تساعد، لكن قياس الرطوبة أو الضغط أو نوع الحشرة يتم في الموقع. إن طُلب منا تأكيد عبر واتساب فقط، نوضح حدود ما يمكن قوله دون زيارة.</p>
<h2>أنواع العمل داخل {core}</h2>
<div class="responsive-table"><table>
<thead><tr><th>البند</th><th>الوصف</th><th>الفائدة</th><th>متى</th></tr></thead>
<tbody>{rows}</tbody>
</table></div>
[post_steps]
<blockquote class="expert-tip"><i class="fas fa-lightbulb"></i> <strong>نصيحة:</strong> اكتب الحي واسم أقرب معلم، وأرفق صورة العداد أو موضع العطل. ذلك يختصر جدولة {title} في {focus_city} وباقي المدن.</blockquote>
<h2>كيف ننفّذ {core} خطوة بخطوة؟</h2>
<p>بعد الاتفاق على الموعد يصل الفني في النافذة المتفق عليها. يراجع ما ذكرته، يفحص المصدر، ويشرح ما سيُعمل قبل أن يبدأ. إن تغيّر النطاق — مثلاً احتاج {core} فتحاً موضعياً أو خامة مختلفة — يتوقف العمل إلى أن توافق على التعديل المكتوب. بعد التنفيذ نراجع النتيجة معك: تشغيل، جفاف موضع، أو تجربة تبريد، حسب نوع الخدمة.</p>
<p>الأدوات المستخدمة: {pack['tools']} لا نعلن جهازاً سحرياً يغني عن المعاينة. التقرير المصوّر يُقدَّم عندما يكون التشخيص هو العمل نفسه، كما في التسربات. في الخدمات التنفيذية يكفي شرح النتيجة وما يُصان لاحقاً.</p>
<h2>أخطاء تؤجّل الحل</h2>
{_ul(mistakes)}
<p>أشيع خطأ في طلب {title} هو المقارنة على رقم واحد بلا نطاق. عرض بلا بنود أرخص على الورق وأغلى عند أول زيارة تصحيح. الخطأ الثاني تجاهل المصدر إن كان تسرباً أو رطوبة؛ الدهان والتنظيف حينها مظهر فقط.</p>
[post_call]
<h2>مقارنة بين عمل منظم وعمل عشوائي</h2>
<div class="responsive-table"><table>
<thead><tr><th>المعيار</th><th>ركن التطور</th><th>شائع في السوق</th></tr></thead>
<tbody>{cmp_rows}</tbody>
</table></div>
[post_prices]
[post_services]
{_city_block(ptype, core)}
<h2>ما الذي لا نعد به في هذه الصفحة؟</h2>
<p>لا نثبت سعراً نهائياً لكل فيلا، ولا نختلق تقييماً بالنجوم، ولا نطلب اتصالاً هاتفياً الآن. واتساب يكفي لتحديد المعاينة. لا ننشر قوالب «{core} في كل مدينة» لأن جوجل والمستخدم يلتقيان بنص مكرر. المقال المعتمد لكشف تسربات المياه في قطر يبقى صفحة واحدة: <a href="{LEAK}">الحل النهائي 2026</a> — ولا نلمسه من صفحات الخدمات الأخرى إلا بالإشارة.</p>
<h2>بعد التسليم</h2>
<p>نوضح إن كانت الخدمة تحتاج متابعة (مكافحة بق، عزل يحتاج اختبار غمر، تكييف يحتاج غسيلاً موسمياً). تحتفظ بنطاق العرض للمراجعة. إن ظهر عارض جديد غير ما شُخّص، راسلنا بالصور قبل افتراض أن العمل السابق فشل.</p>
{_long_faq(title, city, pack, core)}
<p>{pack['related']}</p>
<h2>خلاصة {title}</h2>
<p>{title}{loc} تبدأ بفهم العطل في مناخ قطر لا بعرض عام. ركن التطور يزور بالتنسيق من الدوحة، يشرح التشخيص، ويكتب النطاق. إن كانت حالتك في {focus_city} أو أي مدينة أعلاه، استخدم واتساب في هذه الصفحة واذكر الحي ونوع المبنى.</p>
</div>
"""
    desc = f"{title}: تشخيص قبل التنفيذ وعرض مكتوب في قطر. تغطية الدوحة وباقي المدن. تواصل واتساب لتحديد المعاينة."
    if len(desc) > 158:
        desc = desc[:155] + "…"
    return html.strip(), desc, title


def build_longform_payload(title: str, slug: str, lang: str = "ar") -> dict:
    payload = build_theme_payload(title, slug, lang)
    html, desc, kw = build_longform(title, slug, lang)
    payload["html"] = html
    payload["desc"] = desc
    payload["keyword"] = kw
    payload["excerpt"] = desc
    payload["word_count"] = word_count(html)
    return payload
