# تدقيق ركن التطور — قطر

نتائج دخول https://www.rukn-eltatawer.com/qa بحساب `cursor` وفحص المقالات والقالب والصفحات الحية.

| الملف | المحتوى |
| --- | --- |
| [site-template-audit-2026-09.md](site-template-audit-2026-09.md) | تدقيق القالب والودجات والتواصل واللغات والسيو التقني وأخطاء الواجهة |
| [template-issues.csv](template-issues.csv) | جدول الأخطاء المستخرجة حسب الخطورة |
| [qatar-content-audit-2026-09.md](qatar-content-audit-2026-09.md) | تدقيق المقالات المنشورة والمسودات |
| [missing-articles.md](missing-articles.md) | المقالات والصفحات الناقصة تحريريًا |
| [published-articles-actions.csv](published-articles-actions.csv) | إجراء لكل مقال منشور |
| [live-fixes-2026-09.md](live-fixes-2026-09.md) | ما طُبّق على الموقع الحي: واتساب الإمارات، إخفاء الاتصال، حذف الأرقام القطرية، وإصلاح الواجهة |
| [city-grid-publish-2026-09.md](city-grid-publish-2026-09.md) | نشر تغطية 9 مدن بمحتوى مختلف لكل مقال، مع إبقاء الشحن/البيانو مسودة |
| [snippets/city-grid-publisher.php](snippets/city-grid-publisher.php) | قصاصة ووردبريس 7: توليد HTML فريد ونشر الشبكة |
| [seo_content_audit.py](seo_content_audit.py) | سكربت تدقيق سيو تقني + جودة محتوى عبر REST (بدون تخزين كلمة المرور) |
| [seo_remediation.py](seo_remediation.py) | محرّك الإصلاح: مسودة خارج التخصص، إصلاح H1/tel، شبكة روابط داخلية، هيكل LLM (dry-run افتراضي) |
| [seo-remediation.md](seo-remediation.md) | تعليمات المراجعة ثم `--apply` |

## إصلاح السيو (بعد مراجعة الخطة)

```bash
cp .env.example .env
python3 content-audit/seo_remediation.py --dry-run --tasks 1,2,3,4
python3 content-audit/seo_remediation.py --apply --tasks 1,2,3
```
| [reports/seo-technical/seo-audit-summary.md](reports/seo-technical/seo-audit-summary.md) | ملخص تدقيق 1950 URL منشوراً (17 سبتمبر 2026) |
| [reports/seo-technical/seo-audit-issues.csv](reports/seo-technical/seo-audit-issues.csv) | جدول: عنوان، رابط، كلمات، فئة المشكلة، ملاحظات |
| [reports/seo-technical/seo-audit-all.csv](reports/seo-technical/seo-audit-all.csv) | الجرد الكامل مع هياكل العناوين وRank Math والفحص الحي |

ملف `rukn-eltatawer-qatar-FULL.csv` في جذر المستودع هو مخزون قديم. النصوص المنشورة مولَّدة في القصاصة 7 وليست نسخ CSV.

## إعادة تدقيق السيو

```bash
export WP_BASE=https://www.rukn-eltatawer.com/qa
export WP_USER='your-user'
export WP_APP_PASSWORD='xxxx xxxx xxxx xxxx xxxx xxxx'
python3 content-audit/seo_content_audit.py --live-html priority --thin 1000
```

ملف `rukn-eltatawer-qatar-FULL.csv` في جذر المستودع هو مخزون قديم. النصوص المنشورة مولَّدة في القصاصة 7 وليست نسخ CSV.
