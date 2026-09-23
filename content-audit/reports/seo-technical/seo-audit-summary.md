# تدقيق سيو تقني ومحتوى — ركن التطور قطر

**المصدر:** https://www.rukn-eltatawer.com/qa عبر REST (مقالات + صفحات + CPT خدمات).
**التاريخ:** 2026-09-17
**الصفحات المفحوصة:** 1950 — أنواع: {'post': 1919, 'page': 19, 'services': 12}
**عتبة المحتوى الضعيف:** 1000 كلمة. **فحص HTML الحي:** `priority`.

هذا التقرير حصيلة سكربت `seo_content_audit.py`. الجدول الكامل لكل URL في `seo-audit-all.csv`.

## الخلاصة التنفيذية

| المؤشر | العدد | النسبة |
| --- | ---: | ---: |
| إجمالي المنشورات المفحوصة | 1950 | 100% |
| محتوى ضعيف (< 1000 كلمة) | 1946 | 99% |
| هزيل جداً (< 300 كلمة) | 1797 | 92% |
| ≥ 1000 كلمة | 4 | 0% |
| قالب/نص جاهز مشترك (≥ 8 صفحات بنفس الهيكل) | 1782 | 91% |
| شبكة مدينة×خدمة (مولّد) | 1774 | 90% |
| تعارض كلمات مفتاحية (نفس الخدمة على ≥6 URL) | 1784 | 91% |
| عدم تطابق نية/عنوان↔نص | 1 | 0% |
| شورت كود أو نص نائب | 0 | 0% |
| بلا H2/H3 في الجسم | 2 | 0% |
| يتيم داخلياً (Rank Math orphan) | 1909 | 97% |

### الحكم

الموقع يعتمد على طبقتين: (1) صفحات ركيزة وطنية متفاوتة الجودة، (2) شبكة محلية ضخمة مولَّدة قالبياً (~9 مدن × الخدمة). الطبقة الثانية تغطي قطر جغرافياً لكنها **محتوى ضعيف هيكلياً ومتشابه بعد تجريد اسم المدينة**، وهذا نمط doorway-page يعرّض النطاق لتخفيض جودة في البحث وليس لتفوق محلي مستدام.

**أربع صفحات فقط من أصل 1950 تتجاوز 1000 كلمة:**

| العنوان | الرابط | الكلمات | ملاحظة تقنية |
| --- | --- | ---: | --- |
| شركة كشف تسربات المياه في قطر | https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/ | 4101 | ركيزة حقيقية؛ **H1 مزدوج** في HTML الحي + رابط `tel:` |
| شركة مكافحة الصراصير في قطر | https://www.rukn-eltatawer.com/qa/shrkh-mkafhh-srasyr-fy-qtr/ | 2644 | طويل لكن فيه `tel:` |
| شركة تنظيف منازل في قطر | https://www.rukn-eltatawer.com/qa/shrkh-tnzyf-mnazl-fy-qtr-2/ | 2641 | طويل لكن فيه `tel:` |
| مكتب استقدام في قطر | https://www.rukn-eltatawer.com/qa/recruitment-in-qatar/ | 2117 | **خارج التخصص**؛ الاستجابة الحية **301** إلى `/qa/` (ما زال منشوراً في ووردبريس) |

ملاحظات حيّة إضافية:

- أنواع CPT `/services/{slug}/` عليها `robots: noindex` (ما عدا عيّنة عازل الصوت التي فُحص هيكلها). هذا يمنع فهرسة الصفحات الرفيعة لكنه يلغيها كصفحات هبوط.
- 1909 URL يتيمة حسب Rank Math (لا روابط داخلية داخلة).
- لا نصوص `lorem ipsum` ولا شورت كود `[post_features]` متبقية في الجسم المنشور — التحسين السابق صمد.
- `no_h1_in_body` على معظم المقالات **ليس خطأ إن كان القالب يطبع العنوان مرة واحدة**. الفحص الحي للصفحات ذات الأولوية: H1 واحد صحيح، باستثناء خريطة الموقع (2) وركيزة التسربات (2).

## 1) المحتوى الضعيف

كل مقال أقل من **1000 كلمة** يُعد ضعيفاً وفق طلب التدقيق. توزيع الأطوال:

| نطاق الكلمات | العدد |
| --- | ---: |
| 0–149 | 12 |
| 150–299 | 1785 |
| 300–499 | 9 |
| 500–799 | 140 |
| 800–999 | 0 |
| 1000–1999 | 0 |
| 2000+ | 4 |

عيّنة من الأضعف خارج شبكة المدن (الأولى بالأولوية):

| العنوان | الرابط | الكلمات | فئة | ملاحظات |
| --- | --- | ---: | --- | --- |
| المدونة | https://www.rukn-eltatawer.com/qa/blog/ | 32 | critical_thin,no_h1_in_body | محتوى هزيل جداً (32 كلمة) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| كشف تسربات المياه | https://www.rukn-eltatawer.com/qa/services/water-leak-detection/ | 42 | critical_thin,keyword_cannibalization,no_h1_in_body | محتوى هزيل جداً (42 كلمة) ؛ نفس جذع الخدمة `water-leak-detection` على 10 URL ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الح |
| المدن | https://www.rukn-eltatawer.com/qa/cities/ | 55 | critical_thin,no_h1_in_body | محتوى هزيل جداً (55 كلمة) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| الخدمات | https://www.rukn-eltatawer.com/qa/services/ | 62 | critical_thin,no_h1_in_body | محتوى هزيل جداً (62 كلمة) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| سياسة الخصوصية | https://www.rukn-eltatawer.com/qa/privacy-policy/ | 88 | critical_thin,no_h1_in_body,no_internal_links_in_body | محتوى هزيل جداً (88 كلمة) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ لا روابط داخلية في الجسم |
| اتصل بنا | https://www.rukn-eltatawer.com/qa/contact-us/ | 92 | critical_thin,missing_h2_h3,no_h1_in_body | محتوى هزيل جداً (92 كلمة) ؛ لا توجد عناوين H2/H3 داخل المحتوى ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| الأسعار | https://www.rukn-eltatawer.com/qa/as3ar/ | 94 | critical_thin,no_h1_in_body | محتوى هزيل جداً (94 كلمة) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| Contact | https://www.rukn-eltatawer.com/qa/contact-us-2/ | 98 | critical_thin,missing_h2_h3,no_h1_in_body | محتوى هزيل جداً (98 كلمة) ؛ لا توجد عناوين H2/H3 داخل المحتوى ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| خريطة الموقع | https://www.rukn-eltatawer.com/qa/sitemap/ | 114 | critical_thin,multiple_h1 | محتوى هزيل جداً (114 كلمة) ؛ 2 عناوين H1 |
| الأسئلة الشائعة | https://www.rukn-eltatawer.com/qa/faq/ | 138 | critical_thin,no_h1_in_body | محتوى هزيل جداً (138 كلمة) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| من نحن | https://www.rukn-eltatawer.com/qa/about/ | 141 | critical_thin,no_h1_in_body | محتوى هزيل جداً (141 كلمة) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| AC maintenance in Doha and Qatar | https://www.rukn-eltatawer.com/qa/en/ac-maintenance-qatar-en/ | 176 | critical_thin,no_h1_in_body | محتوى هزيل جداً (176 كلمة) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| Roof insulation in Qatar | https://www.rukn-eltatawer.com/qa/en/roof-insulation-qatar-en/ | 181 | critical_thin,no_h1_in_body | محتوى هزيل جداً (181 كلمة) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| Water leak detection in Qatar without breaking | https://www.rukn-eltatawer.com/qa/en/water-leak-detection-qatar-en/ | 202 | critical_thin,no_h1_in_body | محتوى هزيل جداً (202 كلمة) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| خدمات ركن التطور في الشحانية | https://www.rukn-eltatawer.com/qa/services-in-al-shahaniya-qatar/ | 203 | critical_thin,template_boilerplate,no_h1_in_body | محتوى هزيل جداً (203 كلمة) ؛ نفس الهيكل العناوين في 9 صفحة (hash cf87e50bf32a) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| خدمات ركن التطور في الشمال | https://www.rukn-eltatawer.com/qa/services-in-al-shamal-qatar/ | 205 | critical_thin,template_boilerplate,no_h1_in_body | محتوى هزيل جداً (205 كلمة) ؛ نفس الهيكل العناوين في 9 صفحة (hash cf87e50bf32a) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| خدمات ركن التطور في الظعاين | https://www.rukn-eltatawer.com/qa/services-in-al-daayen-qatar/ | 208 | critical_thin,template_boilerplate,no_h1_in_body | محتوى هزيل جداً (208 كلمة) ؛ نفس الهيكل العناوين في 9 صفحة (hash cf87e50bf32a) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| خدمات ركن التطور في أم صلال والخيسة | https://www.rukn-eltatawer.com/qa/services-in-umm-salal-qatar/ | 210 | critical_thin,template_boilerplate,no_h1_in_body | محتوى هزيل جداً (210 كلمة) ؛ نفس الهيكل العناوين في 9 صفحة (hash cf87e50bf32a) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| خدمات ركن التطور في الخور | https://www.rukn-eltatawer.com/qa/services-in-al-khor-qatar/ | 212 | critical_thin,template_boilerplate,no_h1_in_body | محتوى هزيل جداً (212 كلمة) ؛ نفس الهيكل العناوين في 9 صفحة (hash cf87e50bf32a) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| خدمات ركن التطور في الريان | https://www.rukn-eltatawer.com/qa/services-in-al-rayyan-qatar/ | 213 | critical_thin,template_boilerplate,no_h1_in_body | محتوى هزيل جداً (213 كلمة) ؛ نفس الهيكل العناوين في 9 صفحة (hash cf87e50bf32a) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| خدمات ركن التطور في الوكرة | https://www.rukn-eltatawer.com/qa/services-in-al-wakrah-qatar/ | 217 | critical_thin,template_boilerplate,no_h1_in_body | محتوى هزيل جداً (217 كلمة) ؛ نفس الهيكل العناوين في 9 صفحة (hash cf87e50bf32a) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| خدمات ركن التطور في لوسيل | https://www.rukn-eltatawer.com/qa/services-in-lusail-qatar/ | 227 | critical_thin,template_boilerplate,no_h1_in_body | محتوى هزيل جداً (227 كلمة) ؛ نفس الهيكل العناوين في 9 صفحة (hash cf87e50bf32a) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| خدمات ركن التطور في الدوحة | https://www.rukn-eltatawer.com/qa/services-in-doha-qatar/ | 244 | critical_thin,template_boilerplate,no_h1_in_body | محتوى هزيل جداً (244 كلمة) ؛ نفس الهيكل العناوين في 9 صفحة (hash cf87e50bf32a) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| شركة تخزين بضائع في قطر | https://www.rukn-eltatawer.com/qa/shrkh-tkhzyn-bdaya-fy-qtr/ | 411 | thin_content,no_h1_in_body,noindex | أقل من 1000 كلمة (411) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شراء أجهزة كهربائية مستعملة في قطر | https://www.rukn-eltatawer.com/qa/shra-ajhzh-khrbayyh-mstamlh-fy-qtr/ | 423 | thin_content,no_h1_in_body,noindex | أقل من 1000 كلمة (423) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شركة تخزين أثاث في قطر | https://www.rukn-eltatawer.com/qa/shrkh-tkhzyn-athath-fy-qtr/ | 426 | thin_content,no_h1_in_body,noindex | أقل من 1000 كلمة (426) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| تنظيف وتعقيم | https://www.rukn-eltatawer.com/qa/services/cleaning-and-sterilization/ | 438 | thin_content,similar_content,no_h1_in_body | أقل من 1000 كلمة (438) ؛ محتوى مشابه (hamming 5) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شراء سكراب في قطر | https://www.rukn-eltatawer.com/qa/shra-skrab-fy-qtr/ | 452 | thin_content,no_h1_in_body,noindex | أقل من 1000 كلمة (452) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شراء مكيفات مستعملة في قطر | https://www.rukn-eltatawer.com/qa/shra-mkyfat-mstamlh-fy-qtr/ | 461 | thin_content,no_h1_in_body,noindex | أقل من 1000 كلمة (461) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شراء معدات مطاعم مستعملة في قطر | https://www.rukn-eltatawer.com/qa/shra-madat-mtaam-mstamlh-fy-qtr/ | 464 | thin_content,no_h1_in_body,noindex | أقل من 1000 كلمة (464) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شراء أثاث مستعمل في قطر | https://www.rukn-eltatawer.com/qa/shra-athath-mstaml-fy-qtr/ | 471 | thin_content,no_h1_in_body,noindex | أقل من 1000 كلمة (471) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| تركيب الباركيه | https://www.rukn-eltatawer.com/qa/services/parquet-installation/ | 494 | thin_content,no_h1_in_body,noindex | أقل من 1000 كلمة (494) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| إنشاء وصيانة المباني | https://www.rukn-eltatawer.com/qa/services/construction-and-maintenance-of-buildings/ | 501 | thin_content,near_duplicate,no_h1_in_body | أقل من 1000 كلمة (501) ؛ تشابه SimHash مسافة 3 مع https://www.rukn-eltatawer.com/qa/shrkh-dhanat-kharjyh-fy-qtr/ ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان الق |
| تنسيق الحدائق | https://www.rukn-eltatawer.com/qa/services/landscaping/ | 501 | thin_content,keyword_cannibalization,no_h1_in_body | أقل من 1000 كلمة (501) ؛ نفس جذع الخدمة `landscaping` على 10 URL ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| تركيب جبس بورد | https://www.rukn-eltatawer.com/qa/services/gypsum-board-installation/ | 505 | thin_content,similar_content,no_h1_in_body | أقل من 1000 كلمة (505) ؛ محتوى مشابه (hamming 6) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| مكافحة الحشرات | https://www.rukn-eltatawer.com/qa/services/pest-control/ | 511 | thin_content,no_h1_in_body,noindex | أقل من 1000 كلمة (511) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| إنشاء وصيانة المسابح | https://www.rukn-eltatawer.com/qa/services/construction-and-maintenance-of-swimming-pools/ | 513 | thin_content,no_h1_in_body,noindex | أقل من 1000 كلمة (513) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| تسليك المجاري | https://www.rukn-eltatawer.com/qa/services/sewer-wiring/ | 516 | thin_content,no_h1_in_body,noindex | أقل من 1000 كلمة (516) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شركة تركيب ألومنيوم في قطر | https://www.rukn-eltatawer.com/qa/shrkh-trkyb-alwmnywm-fy-qtr/ | 533 | thin_content,no_h1_in_body | أقل من 1000 كلمة (533) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| صيانة وتركيب المكيفات | https://www.rukn-eltatawer.com/qa/services/air-conditioner-maintenance-and-installation/ | 536 | thin_content,similar_content,no_h1_in_body | أقل من 1000 كلمة (536) ؛ محتوى مشابه (hamming 6) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |

شبكة المدن: 1774 صفحة، وسيط الكلمات ≈ 229. كلها تحت العتبة ما لم يُذكر خلاف ذلك في CSV.

## 2) الإفراط في القوالب

| hash الهيكل | عدد الصفحات | عيّنة عنوان |
| --- | ---: | --- |
| `cb24e6f8b3f9` | 905 | شركة تسليك مجاري في الشحانية |
| `a6b89d30b159` | 868 | شركة تسليك مجاري في أم صلال والخيسة |
| `cf87e50bf32a` | 9 | خدمات ركن التطور في الشحانية |
| `no-headings` | 5 | الخدمات |
| `6ee8e73964db` | 1 | شراء معدات مطاعم مستعملة في قطر |
| `19479aaa4d12` | 1 | شراء سكراب في قطر |
| `d7f00a72c2ea` | 1 | شراء أجهزة كهربائية مستعملة في قطر |
| `e8aa0d7b3d20` | 1 | شراء مكيفات مستعملة في قطر |

الهيكل الأكثر تكراراً (بعد استبدال اسم المدينة بـ `{CITY}`):

`h2:متى تطلب الخدمة {CITY} / h2:طريقة العمل / h2:التغطية المحلية / h2:هل تعملون {CITY} فقط؟ / h2:هل يوجد رقم للاتصال؟ / h2:هل السعر ثابت؟ / h2:هل الزيارة في نفس اليوم؟`

## 3) التكرار والتشابه / cannibalization

جذوع الخدمات المكررة عبر المدن (أعلى 25):

| جذع السلَج | عدد الـ URL | مثال |
| --- | ---: | --- |
| `home-plumber` | 10 | https://www.rukn-eltatawer.com/qa/home-plumber-lusail/ |
| `bed-bug-control` | 10 | https://www.rukn-eltatawer.com/qa/bed-bug-control-lusail/ |
| `cockroach-control` | 10 | https://www.rukn-eltatawer.com/qa/cockroach-control-lusail/ |
| `termite-control` | 10 | https://www.rukn-eltatawer.com/qa/termite-control-lusail/ |
| `landscaping` | 10 | https://www.rukn-eltatawer.com/qa/landscaping-lusail/ |
| `water-leak-detection` | 10 | https://www.rukn-eltatawer.com/qa/water-leak-detection-lusail/ |
| `split-ac-maintenance` | 10 | https://www.rukn-eltatawer.com/qa/split-ac-maintenance-lusail/ |
| `plumbing-maintenance` | 10 | https://www.rukn-eltatawer.com/qa/plumbing-maintenance-lusail/ |
| `water-tank-cleaning` | 10 | https://www.rukn-eltatawer.com/qa/water-tank-cleaning-lusail/ |
| `villa-cleaning` | 10 | https://www.rukn-eltatawer.com/qa/villa-cleaning-lusail/ |
| `apartment-cleaning` | 10 | https://www.rukn-eltatawer.com/qa/apartment-cleaning-lusail/ |
| `sewerage-company-in` | 9 | https://www.rukn-eltatawer.com/qa/sewerage-company-in-al-shahaniya/ |
| `ac-periodic-maintenance-contracts` | 9 | https://www.rukn-eltatawer.com/qa/ac-periodic-maintenance-contracts-lusail/ |
| `commercial-refrigeration-maintenance` | 9 | https://www.rukn-eltatawer.com/qa/commercial-refrigeration-maintenance-lusail/ |
| `cooling-fault-detection` | 9 | https://www.rukn-eltatawer.com/qa/cooling-fault-detection-lusail/ |
| `new-central-ac-installation` | 9 | https://www.rukn-eltatawer.com/qa/new-central-ac-installation-lusail/ |
| `ac-duct-maintenance` | 9 | https://www.rukn-eltatawer.com/qa/ac-duct-maintenance-lusail/ |
| `ac-relocation-installation` | 9 | https://www.rukn-eltatawer.com/qa/ac-relocation-installation-lusail/ |
| `ac-cleaning-washing` | 9 | https://www.rukn-eltatawer.com/qa/ac-cleaning-washing-lusail/ |
| `ac-freon-refill` | 9 | https://www.rukn-eltatawer.com/qa/ac-freon-refill-lusail/ |
| `window-ac-installation` | 9 | https://www.rukn-eltatawer.com/qa/window-ac-installation-lusail/ |
| `split-ac-installation` | 9 | https://www.rukn-eltatawer.com/qa/split-ac-installation-lusail/ |
| `plumbing-fault-repair` | 9 | https://www.rukn-eltatawer.com/qa/plumbing-fault-repair-lusail/ |
| `central-heater-installation-maintenance` | 9 | https://www.rukn-eltatawer.com/qa/central-heater-installation-maintenance-lusail/ |
| `water-pump-maintenance` | 9 | https://www.rukn-eltatawer.com/qa/water-pump-maintenance-lusail/ |

صفحات **غير** الشبكة ومتشابهة (hamming ≤ 6):

| العنوان | الكلمات | مشابه لـ | المسافة |
| --- | ---: | --- | ---: |
| شركة تنظيف منازل في قطر | 607 | https://www.rukn-eltatawer.com/qa/shrkh-trkyb-wrq-jdran-fy-qtr/ | 6 |
| شركة مكافحة الصراصير في قطر | 618 | https://www.rukn-eltatawer.com/qa/shrkh-hdm-mbany-fy-qtr/ | 5 |
| شركة صيانة مسابح في قطر | 609 | https://www.rukn-eltatawer.com/qa/shrkh-ansha-msabh-fy-qtr/ | 5 |
| شركة إنشاء مسابح في قطر | 609 | https://www.rukn-eltatawer.com/qa/shrkh-syanh-msabh-fy-qtr/ | 5 |
| شركة تكريب نخيل في قطر | 606 | https://www.rukn-eltatawer.com/qa/shrkh-hdm-mbany-fy-qtr/ ; https://www.rukn-eltatawer.com/qa/shrkh-bna-mjals-fy-qtr/ | 5 |
| شركة تصميم حدائق في قطر | 606 | https://www.rukn-eltatawer.com/qa/shrkh-tnsyq-hdayq-fy-qtr/ | 3 |
| شركة تنسيق حدائق في قطر | 606 | https://www.rukn-eltatawer.com/qa/shrkh-tsmym-hdayq-fy-qtr/ | 3 |
| شركة تركيب بديل خشب في قطر | 552 | https://www.rukn-eltatawer.com/qa/shrkh-trkyb-barkyh-fy-qtr/ | 6 |
| شركة تركيب باركيه في قطر | 602 | https://www.rukn-eltatawer.com/qa/shrkh-trkyb-syramyk-wbwrslyn-fy-qtr/ ; https://www.rukn-eltatawer.com/qa/shrkh-trkyb-b | 5 |
| شركة تركيب انترلوك في قطر | 602 | https://www.rukn-eltatawer.com/qa/shrkh-trkyb-rkham-wjranyt-fy-qtr/ | 5 |
| شركة تركيب رخام وجرانيت في قطر | 617 | https://www.rukn-eltatawer.com/qa/shrkh-trkyb-antrlwk-fy-qtr/ | 5 |
| شركة تركيب سيراميك وبورسلين في قطر | 617 | https://www.rukn-eltatawer.com/qa/shrkh-trkyb-barkyh-fy-qtr/ | 5 |
| شركة تركيب جبس بورد في قطر | 615 | https://www.rukn-eltatawer.com/qa/services/gypsum-board-installation/ | 6 |
| شركة تركيب ورق جدران في قطر | 615 | https://www.rukn-eltatawer.com/qa/house-cleaning-in-qatar/ | 6 |
| شركة ديكورات داخلية في قطر | 600 | https://www.rukn-eltatawer.com/qa/shrkh-dhanat-dakhlyh-fy-qtr/ | 6 |
| شركة دهانات خارجية في قطر | 600 | https://www.rukn-eltatawer.com/qa/services/construction-and-maintenance-of-buildings/ | 3 |
| شركة دهانات داخلية في قطر | 600 | https://www.rukn-eltatawer.com/qa/shrkh-dykwrat-dakhlyh-fy-qtr/ | 6 |
| شركة هدم مباني في قطر | 595 | https://www.rukn-eltatawer.com/qa/shrkh-bna-astrahat-fy-qtr/ ; https://www.rukn-eltatawer.com/qa/cockroach-control-in-qa | 4 |
| شركة تشطيب شقق في قطر | 595 | https://www.rukn-eltatawer.com/qa/shrkh-tshtyb-fll-fy-qtr/ | 5 |
| شركة تشطيب فلل في قطر | 595 | https://www.rukn-eltatawer.com/qa/shrkh-tshtyb-shqq-fy-qtr/ | 5 |
| شركة بناء استراحات في قطر | 595 | https://www.rukn-eltatawer.com/qa/shrkh-bna-mjals-fy-qtr/ ; https://www.rukn-eltatawer.com/qa/shrkh-hdm-mbany-fy-qtr/ | 3 |
| شركة بناء مجالس في قطر | 595 | https://www.rukn-eltatawer.com/qa/shrkh-bna-astrahat-fy-qtr/ ; https://www.rukn-eltatawer.com/qa/shrkh-hdm-mbany-fy-qtr/ | 3 |
| شركة صيانة مباني في قطر | 595 | https://www.rukn-eltatawer.com/qa/shrkh-syanh-aamh-fy-qtr/ | 5 |
| شركة صيانة عامة في قطر | 595 | https://www.rukn-eltatawer.com/qa/shrkh-syanh-mbany-fy-qtr/ | 5 |
| شركة صيانة ميكروويف في قطر | 575 | https://www.rukn-eltatawer.com/qa/shrkh-syanh-thlajat-fy-qtr/ | 4 |
| شركة صيانة طباخات في قطر | 575 | https://www.rukn-eltatawer.com/qa/shrkh-syanh-ghsalat-fy-qtr/ | 4 |
| شركة صيانة غسالات في قطر | 575 | https://www.rukn-eltatawer.com/qa/shrkh-syanh-tbakhat-fy-qtr/ | 4 |
| شركة صيانة ثلاجات في قطر | 575 | https://www.rukn-eltatawer.com/qa/shrkh-syanh-mykrwwyf-fy-qtr/ | 4 |
| شركة تعبئة غاز مكيفات في قطر | 644 | https://www.rukn-eltatawer.com/qa/shrkh-ghsyl-mkyfat-fy-qtr/ | 6 |
| شركة غسيل مكيفات في قطر | 629 | https://www.rukn-eltatawer.com/qa/shrkh-tabyh-ghaz-mkyfat-fy-qtr/ | 6 |

## 4) عدم تطابق النية

| العنوان | الرابط | الكلمات | ملاحظة |
| --- | --- | ---: | --- |
| مكتب استقدام في قطر | https://www.rukn-eltatawer.com/qa/recruitment-in-qatar/ | 2117 | المقال ما زال منشوراً في REST لكن الحي يعيد **301** إلى الرئيسية؛ الموضوع استقدام لا خدمات منزلية |

## 5) أخطاء وعناصر مفقودة

| العنوان | الرابط | الكلمات | الفئة | ملاحظات |
| --- | --- | ---: | --- | --- |
| كشف تسربات المياه | https://www.rukn-eltatawer.com/qa/services/water-leak-detection/ | 42 | noindex | محتوى هزيل جداً (42 كلمة) ؛ نفس جذع الخدمة `water-leak-detection` على 10 URL ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الح |
| اتصل بنا | https://www.rukn-eltatawer.com/qa/contact-us/ | 92 | missing_h2_h3 | محتوى هزيل جداً (92 كلمة) ؛ لا توجد عناوين H2/H3 داخل المحتوى ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| Contact | https://www.rukn-eltatawer.com/qa/contact-us-2/ | 98 | missing_h2_h3 | محتوى هزيل جداً (98 كلمة) ؛ لا توجد عناوين H2/H3 داخل المحتوى ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) |
| شركة تخزين بضائع في قطر | https://www.rukn-eltatawer.com/qa/shrkh-tkhzyn-bdaya-fy-qtr/ | 411 | noindex | أقل من 1000 كلمة (411) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شراء أجهزة كهربائية مستعملة في قطر | https://www.rukn-eltatawer.com/qa/shra-ajhzh-khrbayyh-mstamlh-fy-qtr/ | 423 | noindex | أقل من 1000 كلمة (423) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شركة تخزين أثاث في قطر | https://www.rukn-eltatawer.com/qa/shrkh-tkhzyn-athath-fy-qtr/ | 426 | noindex | أقل من 1000 كلمة (426) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| تنظيف وتعقيم | https://www.rukn-eltatawer.com/qa/services/cleaning-and-sterilization/ | 438 | noindex | أقل من 1000 كلمة (438) ؛ محتوى مشابه (hamming 5) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شراء سكراب في قطر | https://www.rukn-eltatawer.com/qa/shra-skrab-fy-qtr/ | 452 | noindex | أقل من 1000 كلمة (452) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شراء مكيفات مستعملة في قطر | https://www.rukn-eltatawer.com/qa/shra-mkyfat-mstamlh-fy-qtr/ | 461 | noindex | أقل من 1000 كلمة (461) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شراء معدات مطاعم مستعملة في قطر | https://www.rukn-eltatawer.com/qa/shra-madat-mtaam-mstamlh-fy-qtr/ | 464 | noindex | أقل من 1000 كلمة (464) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| شراء أثاث مستعمل في قطر | https://www.rukn-eltatawer.com/qa/shra-athath-mstaml-fy-qtr/ | 471 | noindex | أقل من 1000 كلمة (471) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| تركيب الباركيه | https://www.rukn-eltatawer.com/qa/services/parquet-installation/ | 494 | noindex | أقل من 1000 كلمة (494) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| إنشاء وصيانة المباني | https://www.rukn-eltatawer.com/qa/services/construction-and-maintenance-of-buildings/ | 501 | noindex | أقل من 1000 كلمة (501) ؛ تشابه SimHash مسافة 3 مع https://www.rukn-eltatawer.com/qa/shrkh-dhanat-kharjyh-fy-qtr/ ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان الق |
| تنسيق الحدائق | https://www.rukn-eltatawer.com/qa/services/landscaping/ | 501 | noindex | أقل من 1000 كلمة (501) ؛ نفس جذع الخدمة `landscaping` على 10 URL ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| تركيب جبس بورد | https://www.rukn-eltatawer.com/qa/services/gypsum-board-installation/ | 505 | noindex | أقل من 1000 كلمة (505) ؛ محتوى مشابه (hamming 6) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| مكافحة الحشرات | https://www.rukn-eltatawer.com/qa/services/pest-control/ | 511 | noindex | أقل من 1000 كلمة (511) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| إنشاء وصيانة المسابح | https://www.rukn-eltatawer.com/qa/services/construction-and-maintenance-of-swimming-pools/ | 513 | noindex | أقل من 1000 كلمة (513) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| تسليك المجاري | https://www.rukn-eltatawer.com/qa/services/sewer-wiring/ | 516 | noindex | أقل من 1000 كلمة (516) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| صيانة وتركيب المكيفات | https://www.rukn-eltatawer.com/qa/services/air-conditioner-maintenance-and-installation/ | 536 | noindex | أقل من 1000 كلمة (536) ؛ محتوى مشابه (hamming 6) ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ robots noindex على الصفحة الحية |
| عزل الأسطح والخزانات | https://www.rukn-eltatawer.com/qa/services/insulation-of-roofs-and-cabinets/ | 588 | noindex | أقل من 1000 كلمة (588) ؛ تشابه SimHash مسافة 2 مع https://www.rukn-eltatawer.com/qa/shrkh-azl-mayy-fy-qtr/ ؛ لا H1 داخل جسم المقال (قد يعتمد على عنوان القالب) ؛ |

صفحات وCPT الخدمات (كلّها، لأنها واجهة الموقع وليست شبكة المدن):

| النوع | العنوان | الرابط | الكلمات | المشاكل |
| --- | --- | --- | ---: | --- |
| page | خدمات ركن التطور في الشحانية | https://www.rukn-eltatawer.com/qa/services-in-al-shahaniya-qatar/ | 203 | critical_thin,template_boilerplate,no_h1_in_body |
| page | خدمات ركن التطور في الشمال | https://www.rukn-eltatawer.com/qa/services-in-al-shamal-qatar/ | 205 | critical_thin,template_boilerplate,no_h1_in_body |
| page | خدمات ركن التطور في الظعاين | https://www.rukn-eltatawer.com/qa/services-in-al-daayen-qatar/ | 208 | critical_thin,template_boilerplate,no_h1_in_body |
| page | خدمات ركن التطور في أم صلال والخيسة | https://www.rukn-eltatawer.com/qa/services-in-umm-salal-qatar/ | 210 | critical_thin,template_boilerplate,no_h1_in_body |
| page | خدمات ركن التطور في الخور | https://www.rukn-eltatawer.com/qa/services-in-al-khor-qatar/ | 212 | critical_thin,template_boilerplate,no_h1_in_body |
| page | خدمات ركن التطور في الوكرة | https://www.rukn-eltatawer.com/qa/services-in-al-wakrah-qatar/ | 217 | critical_thin,template_boilerplate,no_h1_in_body |
| page | خدمات ركن التطور في الريان | https://www.rukn-eltatawer.com/qa/services-in-al-rayyan-qatar/ | 213 | critical_thin,template_boilerplate,no_h1_in_body |
| page | خدمات ركن التطور في الدوحة | https://www.rukn-eltatawer.com/qa/services-in-doha-qatar/ | 244 | critical_thin,template_boilerplate,no_h1_in_body |
| page | خدمات ركن التطور في لوسيل | https://www.rukn-eltatawer.com/qa/services-in-lusail-qatar/ | 227 | critical_thin,template_boilerplate,no_h1_in_body |
| page | خريطة الموقع | https://www.rukn-eltatawer.com/qa/sitemap/ | 114 | critical_thin,multiple_h1 |
| page | الأسئلة الشائعة | https://www.rukn-eltatawer.com/qa/faq/ | 138 | critical_thin,no_h1_in_body |
| page | المدن | https://www.rukn-eltatawer.com/qa/cities/ | 55 | critical_thin,no_h1_in_body |
| page | الأسعار | https://www.rukn-eltatawer.com/qa/as3ar/ | 94 | critical_thin,no_h1_in_body |
| page | الخدمات | https://www.rukn-eltatawer.com/qa/services/ | 62 | critical_thin,no_h1_in_body |
| page | سياسة الخصوصية | https://www.rukn-eltatawer.com/qa/privacy-policy/ | 88 | critical_thin,no_h1_in_body,no_internal_links_in_body |
| page | Contact | https://www.rukn-eltatawer.com/qa/contact-us-2/ | 98 | critical_thin,missing_h2_h3,no_h1_in_body |
| page | اتصل بنا | https://www.rukn-eltatawer.com/qa/contact-us/ | 92 | critical_thin,missing_h2_h3,no_h1_in_body |
| page | من نحن | https://www.rukn-eltatawer.com/qa/about/ | 141 | critical_thin,no_h1_in_body |
| page | المدونة | https://www.rukn-eltatawer.com/qa/blog/ | 32 | critical_thin,no_h1_in_body |
| services | إنشاء وصيانة المباني | https://www.rukn-eltatawer.com/qa/services/construction-and-maintenance-of-buildings/ | 501 | thin_content,near_duplicate,no_h1_in_body,noindex,missing_canonical |
| services | إنشاء وصيانة المسابح | https://www.rukn-eltatawer.com/qa/services/construction-and-maintenance-of-swimming-pools/ | 513 | thin_content,no_h1_in_body,noindex,missing_canonical |
| services | تنسيق الحدائق | https://www.rukn-eltatawer.com/qa/services/landscaping/ | 501 | thin_content,keyword_cannibalization,no_h1_in_body,noindex,missing_canonical |
| services | تركيب الباركيه | https://www.rukn-eltatawer.com/qa/services/parquet-installation/ | 494 | thin_content,no_h1_in_body,noindex,missing_canonical |
| services | تركيب جبس بورد | https://www.rukn-eltatawer.com/qa/services/gypsum-board-installation/ | 505 | thin_content,similar_content,no_h1_in_body,noindex,missing_canonical |
| services | عازل الصوت | https://www.rukn-eltatawer.com/qa/services/sound-insulation-installation/ | 139 | critical_thin,local_doorway_variant,no_h1_in_body |
| services | كشف تسربات المياه | https://www.rukn-eltatawer.com/qa/services/water-leak-detection/ | 42 | critical_thin,keyword_cannibalization,no_h1_in_body,noindex,missing_canonical |
| services | عزل الأسطح والخزانات | https://www.rukn-eltatawer.com/qa/services/insulation-of-roofs-and-cabinets/ | 588 | thin_content,near_duplicate,no_h1_in_body,noindex,missing_canonical |
| services | تسليك المجاري | https://www.rukn-eltatawer.com/qa/services/sewer-wiring/ | 516 | thin_content,no_h1_in_body,noindex,missing_canonical |
| services | صيانة وتركيب المكيفات | https://www.rukn-eltatawer.com/qa/services/air-conditioner-maintenance-and-installation/ | 536 | thin_content,similar_content,no_h1_in_body,noindex,missing_canonical |
| services | تنظيف وتعقيم | https://www.rukn-eltatawer.com/qa/services/cleaning-and-sterilization/ | 438 | thin_content,similar_content,no_h1_in_body,noindex,missing_canonical |
| services | مكافحة الحشرات | https://www.rukn-eltatawer.com/qa/services/pest-control/ | 511 | thin_content,no_h1_in_body,noindex,missing_canonical |

## توصيات تقنية (أولوية)

1. **لا توسّع الشبكة أكثر.** 9 نسخ لكل خدمة كافية للتجربة المحلية؛ أي خدمة جديدة تُكتب كركيزة قطر أولاً.
2. **ارفع 12–20 ركيزة** فوق 1200 كلمة أصلية (تسرب، عزل، تكييف، مجاري، حشرات، تنظيف، سباكة، كهرباء) ثم اربط الشبكة إليها.
3. **Cannibalization:** اجعل الصفحة الوطنية هي الهدف للبحث العام، وصفحات المدن لـ `[خدمة] في [مدينة]` فقط، مع canonical أو ربط عنقودي واضح.
4. **أوراق يتيمة:** Rank Math يُظهر أغلب الشبكة بدون روابط داخلة. أضف وحدات «خدمات في هذه المدينة» و«نفس الخدمة في مدن أخرى» في القالب.
5. **العنصر النائب/الشورت كود** على أي ركيزة متبقية يُحذف فوراً — Google يرى النص الحرفي.
7. **CPT noindex:** إمّا اكتب صفحات الخدمات كركائز قابلة للفهرسة (canonical ذاتي + محتوى فريد) أو اترك noindex واربط المقال الوطني فقط من القائمة.
8. **H1 مزدوج** على ركيزة التسربات: أوقف H1 القالب أو H1 داخل المقال — واحد فقط.
9. **روابط tel:** ما زالت في ثلاث ركائز طويلة؛ القصاصة تخفي الزر في الواجهة لكن النص/الـHTML الخام ما زال فيه `tel:` إن وُجد في المحتوى.

## إعادة التشغيل

```bash
export WP_USER=... WP_APP_PASSWORD=...
python3 content-audit/seo_content_audit.py --live-html priority --thin 1000
```

