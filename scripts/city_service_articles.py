#!/usr/bin/env python3
"""Unique city×service articles. Never used for post 2973."""
from __future__ import annotations

import hashlib
import re

from city_profiles import PACK_CITY, PROFILES, city_from_slug_title
from kayan_article_builder import (
    ALL_CITIES,
    CITIES_HUB,
    LEAK,
    article_image,
    pack_for,
    service_core,
    wa_url,
)

KEEP_LEAK = "water-leak-detection-company-in-qatar"


def _wc(html: str) -> int:
    t = re.sub(r"\[/?[^\]]+\]", " ", html)
    t = re.sub(r"<[^>]+>", " ", t)
    return len([w for w in re.split(r"\s+", t) if w])


def _h(slug: str, n: int = 0) -> int:
    return int(hashlib.md5(f"{slug}:{n}".encode()).hexdigest(), 16)


def _pick(slug: str, items: list, k: int, salt: int = 0):
    if not items:
        return []
    start = _h(slug, salt) % len(items)
    rot = items[start:] + items[:start]
    return rot[:k]


def _faq(items):
    out = ["<h2>أسئلة عن هذه المدينة وهذه الخدمة</h2>"]
    for q, a in items:
        out.append(f'<div class="faq-item"><h3>{q}</h3><p>{a}</p></div>')
    return "\n".join(out)


def _siblings(city: str, slug: str) -> str:
    parts = []
    for name, prof in PROFILES.items():
        if name == city:
            continue
        parts.append(f'<li><a href="{prof["hub"]}">{name}</a>: {prof["buildings"]}</li>')
    return (
        "<h2>باقي مدن قطر</h2>"
        f"<p>هذه الصفحة لـ{city} فقط. الخدمة نفسها تُقدَّم في المدن التالية بمحتوى مباني مختلف، لا بنسخ الجملة نفسها.</p>"
        f"<ul>{''.join(parts)}</ul>"
        f'<p>دليل المدن: <a href="{CITIES_HUB}">المدن في قطر</a>. '
        f'كشف تسربات المياه للدولة في مقال واحد: <a href="{LEAK}">شركة كشف تسربات المياه في قطر</a>.</p>'
    )


def build_city_article(title: str, slug: str) -> tuple[str, str, int]:
    city = city_from_slug_title(slug, title)
    if city == "قطر" or city not in PROFILES:
        raise ValueError(f"not a city page: {slug} {title}")
    if slug == KEEP_LEAK:
        raise ValueError("refusing ranking leak article")
    prof = PROFILES[city]
    ptype, pack = pack_for(title, slug)
    core = service_core(title)
    wa = wa_url(title)
    img = article_image(ptype)
    pack_note = (PACK_CITY.get(ptype) or {}).get(city) or prof["buildings"]
    when = _pick(slug, list(pack.get("when") or []), 4, 1)
    signs = _pick(slug, list(pack.get("signs") or []), 4, 2)
    mistakes = _pick(slug, list(pack.get("mistakes") or []), 3, 3)
    steps = list(pack.get("steps") or [])
    types = list(pack.get("types") or [])
    cost = list(pack.get("cost") or [])
    extras = _pick(
        slug,
        [
            f"في {city} نسأل عن نوع المبنى قبل أن نعد بمدة: {prof['buildings']}",
            f"الوصول هنا: {prof['access']}",
            f"المناخ المحلي: {prof['climate']}",
            f"الجدولة: {prof['schedule']}",
            f"الأحياء التي نسمعها كثيراً: {prof['areas']}.",
            "لا سعر نهائي من رسالة قصيرة بلا وصف أو صور.",
            "أي فتح أو تغيير خامة يُذكر في العرض قبل التنفيذ.",
            "إن ظهر أن الخدمة ليست المصدر نوضح ذلك ولا نكمل عملاً لا تحتاجه.",
        ],
        6,
        4,
    )
    far = (
        f"<p>لأن {city} أبعد عن مقر الفريق في الدوحة، زمن الطريق جزء من الاتفاق. "
        "نجمع البنود المتفق عليها في نفس الزيارة حين يناسب ذلك حتى لا تتكرر الرحلة بلا داع.</p>"
        if prof["far"]
        else f"<p>الوصول داخل {city} يعتمد على الزحمة والحي أكثر من اسم المدينة. العنوان الدقيق يختصر الانتظار.</p>"
    )
    coast = (
        f"<p>قرب الساحل في {city} يزيد أثر الملح والرطوبة على الحديد والعزل والوحدات الخارجية. "
        "لذلك لا ننسخ خامة أو مادة من فيلا داخلية بلا فحص.</p>"
        if prof["coast"]
        else f"<p>في {city} الغبار والحرارة أغلب من الملح البحري. الرمل عند المدخل والحوش يغيّر أسلوب التنظيف والجلي والعزل أكثر من الرذاذ.</p>"
    )
    step_html = "".join(f"<li><strong>{a}</strong> {b}</li>" for a, b in steps)
    type_html = "".join(f"<li><strong>{a}</strong> — {b} ({c})</li>" for a, b, c, *_ in types)
    cost_html = "".join(f"<li>{c}</li>" for c in cost)
    faqs = [
        (f"هل {core} في {city} بسعر ثابت؟", "لا. المعاينة أو وصف دقيق ثم عرض مكتوب. الحي والمبنى يغيّران النطاق."),
        ("هل تعملون خارج هذه المدينة؟", f"نعم في باقي مدن قطر بالتنسيق. هذه الصفحة تشرح التنفيذ في {city}."),
        ("كيف التواصل؟", "واتساب. زر الاتصال الهاتفي مخفي مؤقتاً."),
        ("هل يلزم تكسير؟", "ليس دائماً. التشخيص أولاً وأي فتح يُكتب قبل التنفيذ."),
        (f"كم تستغرق الزيارة في {city}؟", prof["schedule"]),
        ("ماذا أحضّر؟", "العنوان، صور العطل، وتصريح البرج أو مفتاح السطح إن لزم."),
        ("هل تضمنون النتيجة؟", "ما يُكتب في العرض حسب نوع العمل. لا ضمان عام في المقال."),
        (f"هل الوصول صعب في {city}؟", prof["access"]),
        ("هل هذه نسخة من صفحة قطر؟", f"لا. المباني والوصول في {city} مكتوبان هنا. صفحة قطر نية وطنية."),
        ("هل تكشفون تسرب المياه من هنا؟", f'التسرب المخفي له مقال الدولة: <a href="{LEAK}">كشف تسربات المياه في قطر</a>.'),
    ]
    more = f"""
<h2>مثال نطاق في {city}</h2>
<p>حي من {prof['areas']}، وصف العطل أو الغرف المطلوبة، وصور إن وُجدت. نكتب ما يُشمل وما يُستثنى (غرفة مغلقة، سطح بلا درج، خط مشترك في البرج). المدة تقدير بعد ذلك. هذا المثال شكل النطاق لا سعر.</p>
<p>{extras[5] if len(extras) > 5 else prof['access']}</p>
<h2>بعد التسليم في {city}</h2>
<p>نوضح إن كانت الخدمة تحتاج متابعة (عزل باختبار غمر، مكافحة بجدول، تكييف بغسيل موسمي). تحتفظ بنطاق العرض. إن ظهر عارض جديد أرسل صوراً قبل افتراض فشل العمل السابق.</p>
<p>الجيران والسيارات في الشوارع الضيقة يُراعَون عند الرذاذ أو المعدات. في الأبراج الممر ليس نطاق الشقة إلا بطلب الإدارة.</p>
<h2>علاقة هذه الصفحة بصفحة قطر</h2>
<p>صفحة {core} على مستوى الدولة تشرح الخدمة عموماً. هنا التفاصيل التي تتغيّر داخل {city}: المباني، الوصول، والمناخ. لا نكرّر فقرات الحدائق على خدمة مصعد، ولا فقرات الشفاط على تنظيف منزل.</p>
<p>{pack.get('related') or ''}</p>
<h2>ما الذي نطلبه قبل الخروج من الدوحة؟</h2>
<p>حي واضح داخل {city}، نوع المبنى (شقة، فيلا، ملحق)، وصور. إن لزم تصريح نطلبه قبل تحرك الفريق. في المدن الأبعد نثبّت اليوم لا «خلال ساعة». واتساب يكفي؛ لا نسعّر الحالة النهائية من جملة واحدة.</p>
<p>إن كانت الشكوى تسرباً مخفياً نحوّلك لمقال الكشف الوطني بدل تكرار مسح تجميلي. إن كانت شفاطاً تجارياً لا نفتحها كتنظيف غرف.</p>
"""
    desc = f"{title}: تنفيذ «{core}» في {city} بعد معاينة. واتساب لتحديد الموعد. لا سعر ثابت لكل فيلا."
    html = f"""<div class="rukn-article">
<p>{title} خدمة في {city} من ركن التطور، لا نسخة مكررة لعنوان الحي فقط. {pack['what']} في التطبيق اليومي يعني أن الفني يتعامل مع مباني {city}: {prof['buildings']}</p>
<section class="article-hero"><div class="hero-content">
<span class="hero-label">{city}</span>
<h2>{core} في {city} — نطاق مكتوب بعد فهم المبنى</h2>
<p>أرسل الحي في {city} وصور العطل. لا سعر نهائي من رسالة دون وصف كافٍ.</p>
<div class="hero-buttons"><a class="cta-button whatsapp-button" href="{wa}" rel="nofollow noopener" target="_blank"><i class="fab fa-whatsapp"></i> واتساب لتحديد المعاينة في {city}</a></div>
</div></section>
<h2>ماذا يعني {core} هنا؟</h2>
<p>{pack_note} الأحياء: {prof['areas']}.</p>
<p>{extras[0] if extras else prof['buildings']}</p>
<h2>متى تطلب الزيارة في {city}؟</h2>
<ul>{''.join(f'<li>{x}</li>' for x in when)}</ul>
<p>إن تكررت العلامة بعد «إصلاح سريع» فغالباً عُولجت النتيجة لا السبب. في مناخ {city}: {prof['climate']}</p>
<h2>علامات نراها في مباني {city}</h2>
<ul>{''.join(f'<li>{x}</li>' for x in signs)}</ul>
<blockquote class="warning-box"><i class="fas fa-exclamation-triangle"></i> إخفاء الأثر بالدهان أو بالتعطير أو بزيادة تحميل المكيف يضيّع دليل المصدر ويرفع التكلفة لاحقاً.</blockquote>
<h2>كيف نصل ونجدول في {city}؟</h2>
<p>{prof['access']}</p>
{far}
<p>{extras[1] if len(extras) > 1 else ''}</p>
<h2>المناخ والمادة</h2>
{coast}
<p>{extras[2] if len(extras) > 2 else prof['climate']}</p>
<h2>أنواع العمل داخل {core}</h2>
<ul>{type_html}</ul>
<h2>خطوات الزيارة</h2>
<ol>{step_html}</ol>
<p>الأدوات: {pack.get('tools') or 'معدات تناسب مناخ قطر بعد المعاينة.'}</p>
<h2>أخطاء تؤجّل الحل في {city}</h2>
<ul>{''.join(f'<li>{x}</li>' for x in mistakes)}</ul>
<p>{extras[3] if len(extras) > 3 else 'المقارنة على رقم واحد بلا بنود أغلى عند أول تصحيح.'}</p>
<h2>ما الذي يغيّر النطاق؟</h2>
<ul>{cost_html}</ul>
<p>لا قائمة أسعار ثابتة لكل فيلا في {city}. الرقم بعد فهم الموقع.</p>
<h2>ما لا نعد به في هذه الصفحة</h2>
<p>لا نختلق تقييماً بالنجوم، ولا نطلب اتصالاً هاتفياً. واتساب يكفي. لا ننشر قالب {core} بالحرف في كل مدينة. مقال كشف التسربات المعتمد يبقى صفحة واحدة ولا يُستبدل من هنا.</p>
<p>{extras[4] if len(extras) > 4 else ''}</p>
{more}
{_siblings(city, slug)}
{_faq(faqs)}
<h2>خلاصة {title}</h2>
<p>{desc} {prof['schedule']} التواصل واتساب.</p>
<p><img src="{img}" alt="{title} — ركن التطور في {city}" width="800" height="450" loading="eager" decoding="async"></p>
[post_call]
<p>دليل المدن: <a href="{CITIES_HUB}">المدن في قطر</a> · صفحة {city}: <a href="{prof['hub']}">{city}</a>.</p>
</div>"""
    return html.strip(), desc[:158], _wc(html)


if __name__ == "__main__":
    samples = [
        ("شركة تنظيف وتعقيم شامل في الدوحة", "deep-cleaning-doha"),
        ("شركة عزل مائي في الريان", "waterproofing-al-rayyan"),
        ("شركة صيانة تكييف مركزي في الوكرة", "central-ac-maintenance-al-wakrah"),
        ("شركة تنظيف المداخن والشفاطات في لوسيل", "chimney-cleaning-lusail"),
    ]
    for t, s in samples:
        html, desc, n = build_city_article(t, s)
        print(s, n, desc[:60])
