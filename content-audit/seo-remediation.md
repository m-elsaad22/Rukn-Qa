# محرّك إصلاح السيو — ركن التطور قطر

سكربت `seo_remediation.py` ينفّذ الأربع إصلاحات بعد تدقيق 1950 URL. **الوضع الافتراضي dry-run**: يجلب البيانات ويكتب خطة، ولا يرسل `PUT` إلا مع `--apply`.

## التشغيل (بعد المراجعة)

```bash
cp .env.example .env   # ثم املأ WP_USERNAME و WP_APP_PASSWORD
python3 content-audit/seo_remediation.py --dry-run --tasks 1,2,3,4
# راجع content-audit/reports/seo-remediation/plan.json و actions.csv
python3 content-audit/seo_remediation.py --apply --tasks 1,2
python3 content-audit/seo_remediation.py --apply --tasks 3 --min-interval 0.25
```

المخرجات: `content-audit/reports/seo-remediation/`.

## المهام

| # | ماذا يفعل | ملاحظات |
| --- | --- | --- |
| 1 | `PUT status=draft` لاستقدام/سكراب/مستعمل + CPT الرفيعة التي تسرق نية الركيزة | عتبة CPT: `--cpt-thin 150` |
| 2 | داخل الركائز الثلاث: `<h1>` → `<h2>`، فك أغلفة `href="tel:"` | المقال **#2973** مجمَّد بقصاصة 5؛ السكربت يتحقق بعد الكتابة |
| 3 | كتلة روابط داخلية (3–5 خدمات في نفس المدينة + 3–5 مدن لنفس الخدمة) | تُجلب الكتالوج مرة واحدة ثم تُحدَّث المقالات. الكتلة `rukn-internal-mesh` تُستبدل لا تُضاعَف |
| 4 | 15 ركيزة قطر + حزم prompts لـ OpenAI/Gemini | **لا يُستدعى LLM** إلا `--execute-llm` |

## قفل #2973

`wp_insert_post_data` يعيد محتوى كشف التسربات ما لم يُضبط `$GLOBALS['rukn_unlock_2973']=true`. إن فشل Task 2 على هذا المقال ستظهر النتيجة `BLOCKED_BY_SNIPPET5`.
