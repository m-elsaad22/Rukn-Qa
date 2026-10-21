# تنفيذ الموجة الأولى — مقالات قطر

**الموقع:** https://www.rukn-eltatawer.com/qa  
**التاريخ:** 21 أكتوبر 2026  
**الدخول:** حساب `cursor` عبر REST  
**السجل:** [`reports/apply-live.json`](reports/apply-live.json)

لم تُحفظ كلمة مرور التطبيقات. القصاصة 5 لم تُعدَّل. المقال `#2973` بقي بنفس البصمة بعد التنفيذ (`lock_mismatch: false`).

## ماذا طُبّق على ووردبريس

| الطبقة | النتيجة |
| --- | --- |
| صفحات أساس (خدمات، أسعار، مدن، مدونة، من نحن، أسئلة) | 6/6 |
| صفحات مدن تسع | 9/9 |
| ركائز وطنية أُعيدت كتابتها | 14/14 |
| أدلة إنجليزية ثلاثة | 3/3 |
| CPT: كشف تسربات + عازل صوت (نُشرا) | 2/2 |
| أدلة ناقصة أُنشئت | 6 مقالات جديدة |
| تحويلات Rank Math 301 | 158/158 |
| إلغاء نشر (مسودة، بلا حذف URL) | 158/158 |

## الركائز التي استُبدل محتواها

عزل أسطح، صيانة سبليت، تكييف مركزي، تسليك مجاري، سباك منازل، صيانة سباكة، صيانة كهرباء، تنظيف منازل، مكافحة حشرات، تنسيق حدائق، صيانة عامة، صيانة مباني، دهانات داخلية، طاقة شمسية.

بدون شورت كود `[post_features/steps/prices/services]`، بدون جملة «خدمة وطنية…»، بدون أرقام مخترعة. واتساب `971586634710`. لا `href="tel:"` في المحتوى.

## مقالات جديدة

- [/qa/how-to-choose-home-services-company-qatar/](https://www.rukn-eltatawer.com/qa/how-to-choose-home-services-company-qatar/)
- [/qa/qatar-home-periodic-maintenance-guide/](https://www.rukn-eltatawer.com/qa/qatar-home-periodic-maintenance-guide/)
- [/qa/how-quotes-are-calculated-qatar/](https://www.rukn-eltatawer.com/qa/how-quotes-are-calculated-qatar/)
- [/qa/photo-report-before-repair-qatar/](https://www.rukn-eltatawer.com/qa/photo-report-before-repair-qatar/)
- [/qa/doha-lusail-rayyan-neighborhoods-guide/](https://www.rukn-eltatawer.com/qa/doha-lusail-rayyan-neighborhoods-guide/)
- [/qa/ac-maintenance-before-summer-qatar/](https://www.rukn-eltatawer.com/qa/ac-maintenance-before-summer-qatar/)

## خارج التخصص والمكرر

شحن، بيانو، نقل أثاث/عفش، تخزين، تغليف، فك وتركيب — 301 إلى `/qa/services/` ثم مسودة.  
العناوين المكررة (عشب/تسليك) — 301 إلى النسخة الأطول ثم مسودة.

عيّنة حية: `/qa/shrkh-nql-athath-fy-qtr/` → 301 `/qa/services/`.

## تحقق بعد الكتابة

- `#2973` منشور كما هو، البصمة لم تتغير.
- لا 974 في الصفحات المفحوصة.
- أزرار الاتصال ما زالت مخفية (قواعد CSS `tel:` في القالب، لا روابط اتصال في المقال).
- CPT عازل الصوت يتحدث عن الصوت لا الماء.
- CPT كشف التسربات ملخص يوجّه إلى الركيزة المجمدة.

## ما لم يُنفَّذ في هذه الموجة

- تفريد 1616 صفحة مدينة×خدمة (~1000 كلمة قالبية)
- إعادة كتابة بقية الركائز الوطنية الطويلة الذيل (~100)
- التسعون صفحة المدينة الرفيعة (112–120 كلمة) ما لم تُدمج ضمن 301 المكرر
- قصاصة GSC للفهرسة (فرع مستقل)
- المساس بالقصاصة 5 أو برقم واتساب الإمارات

التشغيل لاحقاً (بدون حفظ السر في Git):

```bash
python3 content-audit/scripts/apply-article-wave.py
python3 content-audit/scripts/apply-article-wave.py --apply
```
