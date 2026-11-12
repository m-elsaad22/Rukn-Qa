# سحب قوالب المدن من الفهرسة — 3 أكتوبر 2026

المقال المتصدر (#2973) لا يُمس.

## المشكلة

بعد إعادة تشغيل مستورد CSV أو نشر جماعي، عاد ~1,761 قالباً (مدينة × خدمة) إلى حالة **منشور**، بالإضافة إلى نسخ كشف تسربات حسب المدينة. هذا يناقض نموذج التغطية المعتمد:

- صفحة خدمة واحدة على مستوى قطر
- صفحة مدينة واحدة تربط لتلك الخدمات
- مقال كشف تسربات واحد فقط: `/water-leak-detection-company-in-qatar/`

وجود القوالب المنشورة يستهلك ميزانية الزحف ويضعف المقال المتصدر.

## ما الذي يُسحب

- أي مقال slug ينتهي بـ `-doha` / `-al-rayyan` / `-al-wakrah` / `-al-khor` / `-umm-salal` / `-al-daayen` / `-al-shamal` / `-al-shahaniya` / `-lusail`
- نسخ `water-leak-detection-*` و `water-pipe-leak-detection-*` ما عدا المقال المتصدر
- تُحوَّل إلى **مسودة + noindex**
- نسخ التسرب تأخذ canonical/301 إلى المقال #2973
- قوالب المدن تُحوَّل عند الزيارة إلى صفحة المدينة المناسبة (مقتطف PHP)

## ما الذي يبقى منشوراً

- #2973 `water-leak-detection-company-in-qatar`
- `sewerage-company-in-doha`
- `gas-leak-detection-doha`
- `ac-leak-detection-doha`
- المقالات الإنجليزية `*-qatar-en`
- صفحات المدن `services-in-*-qatar` (صفحات، ليست مقالات)
- المقالات الوطنية بدون لاحقة مدينة

## التنفيذ

```bash
export WP_USER=cursor
export WP_APP_PASSWORD='…'
python3 scripts/classify_live_posts.py
python3 scripts/unpublish_city_clones.py
```

`unpublish_city_clones.py` يحدّث مقتطف Code Snippets ثم يستدعي `POST /rukn-qa/v1/unpublish-city-templates` (سحب SQL دفعي + noindex). أي بقايا تُسحب عبر REST واحدة تلو الأخرى.

لا تعِد تشغيل **Rukn CSV Importer** على ملف المدينة×الخدمة.
