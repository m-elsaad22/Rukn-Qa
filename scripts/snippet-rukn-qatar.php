
/**
 * Rukn Qatar SEO + contact localization
 */
if (!defined('ABSPATH')) {
    return;
}

const RUKN_QA_PHONE = '';
const RUKN_QA_WA = '971586634710';
const RUKN_QA_WA_PLUS = '+971586634710';
const RUKN_QA_GEO = '25.2854, 51.5310';
const RUKN_QA_LEAK = '/water-leak-detection-company-in-qatar/';
const RUKN_QA_HIDE_CALL = true;

function rukn_qa_is_english() {
    if (function_exists('kayan_i18n_is_english') && kayan_i18n_is_english()) {
        return true;
    }
    if (function_exists('pll_current_language') && pll_current_language() === 'en') {
        return true;
    }
    $uri = (string) ($_SERVER['REQUEST_URI'] ?? '');
    if (strpos($uri, '/qa/en') !== false) {
        return true;
    }
    return (bool) preg_match('#(^|/)en(/|$)#', $uri);
}

function rukn_qa_home_title() {
    return rukn_qa_is_english()
        ? 'Rukn El-Tatawer Qatar | Water leak detection, roof insulation and home maintenance in Doha'
        : 'ركن التطور قطر | كشف تسربات وعزل أسطح وصيانة في الدوحة';
}

function rukn_qa_en_pairs() {
    $map = [
        'ركن التطور قطر | كشف تسربات وعزل أسطح وصيانة في الدوحة' => 'Rukn El-Tatawer Qatar | Water leak detection, roof insulation and home maintenance in Doha',
        'ركن التطور الرائدة في تقديم كل الخدمات المنزلية، كشف تسربات المياه💧🕵️‍♂️عزل الأسطح🏠المسابح🏊‍♂️ التشطيبات🧱الديكورات🎨صيانة عامة🛠️السباكة🚿الكهرباء💡الأجهزة الكهربائية🔌تنسيق الحدائق🌴التنظيف🧼مكافحة الحشرات🐜وكل ما تحتاجه لراحة منزلك أو منشأتك.' => 'Rukn El-Tatawer leads home services in Qatar: water leak detection, roof insulation, pools, finishing, interiors, general maintenance, plumbing, electrical, appliances, landscaping, cleaning, pest control — everything your home or facility needs.',
        'من أشهر العلامات: ارتفاع مفاجئ في فاتورة المياه، بقع رطوبة أو تقشير في الجدران والأسقف، رائحة عفن، أو صوت مياه مع إغلاق كل المحابس.' => 'Common signs: a sudden rise in the water bill, damp patches or peeling on walls and ceilings, a musty smell, or the sound of water after every tap is closed.',
        'نغطي كشف التسربات والعزل والصيانة العامة والسباكة والتكييف والكهرباء والتنظيف ومكافحة الحشرات وتنسيق الحدائق والمسابح والطاقة الشمسية والصبغ والديكورات.' => 'We cover leak detection, insulation, general maintenance, plumbing, AC, electrical, cleaning, pest control, landscaping, pools, solar, painting and interiors.',
        'من كشف تسربات المياه بدون تكسير وعزل الأسطح، إلى الصيانة العامة والتكييف والتنظيف ومكافحة الحشرات وتنسيق الحدائق والطاقة الشمسية — فريق مقيم في الدوحة يغطي قطر، بتشخيص قبل الإصلاح وعرض سعر مكتوب.' => 'From non-destructive water leak detection and roof insulation to general maintenance, AC, cleaning, pest control, landscaping and solar — a Doha-based team covering Qatar, with diagnosis before repair and a written quote.',
        'نعم. نستخدم كاميرا حرارية وأجهزة كشف لتحديد مصدر التسرب بدقة قبل أي تكسير، وتستلم تقريراً مصوّراً يوضح الموقع والسبب.' => 'Yes. We use a thermal camera and detection devices to locate the leak before any breaking, and you receive a photo report showing the location and cause.',
        'حقوق النشر 2026 © جميع الحقوق محفوظة لصالح "شركة ركن التطور - قطر"' => 'Copyright 2026 © All rights reserved to Rukn El-Tatawer Company - Qatar',
        'نعم، ويختلف حسب نوع الخدمة والخامة المستخدمة — ويُوضَّح لك مكتوباً في عرض السعر قبل البدء.' => 'Yes. It depends on the service and materials, and it is written in the quote before work starts.',
        'نعم — لا نسعّر عبر الهاتف. الفني يعاين الموقع ويشخّص المشكلة، ثم تستلم عرض سعر واضح.' => 'Yes — we do not quote by phone. A technician inspects the site, diagnoses the issue, then you receive a clear quote.',
        'مقرنا الدوحة، ونغطي الريان ولوسيل وأم صلال والوكرة والخور والخيسة والشحانية.' => 'We are based in Doha and cover Al Rayyan, Lusail, Umm Salal, Al Wakrah, Al Khor, Al Kheesa and Al Shahaniya.',
        'اختر الخدمة ومدينتك في قطر، ونتواصل معك لتحديد موعد المعاينة.' => 'Choose the service and your city in Qatar, and we will contact you to book an inspection.',
        'حلول شاملة لكل احتياجات منزلك أو منشأتك — بفريق واحد في كل مدن قطر.' => 'Complete solutions for your home or facility — one team across all cities in Qatar.',
        'خدمة واحدة تغطي كل احتياجات المكان — بفريق مقيم في قطر ومسؤولية واحدة.' => 'One service covering every need on site — a Qatar-based team and one point of contact.',
        'فريق ركن التطور يغطي {city} — معاينة وتشخيص قبل بدء العمل.' => 'The Rukn El-Tatawer team covers {city} — inspection and diagnosis before work starts.',
        'مرحباً، أرغب في طلب خدمة:' => 'Hello, I would like to request this service:',
        'مرحباً، أريد الاستفسار عن خدمات ركن التطور في قطر' => 'Hello, I would like to enquire about Rukn El-Tatawer services in Qatar',
        'تُحدَّد بعد المعاينة حسب حجم العمل، وتكون مكتوبة في عرض السعر.' => 'It is set after inspection according to the scope of work, and it is written in the quote.',
        'من تسرب مياه إلى صيانة شاملة — تواصل معنا ونصلك للمعاينة والتشخيص.' => 'From a water leak to full maintenance — contact us and we will come for inspection and diagnosis.',
        'إجابات واضحة لأكثر ما يسأل عنه عملاؤنا في قطر.' => 'Clear answers to what our clients in Qatar ask most.',
        'اتصل أو أرسل واتساب على 974+ ونرد عليك لتحديد الموعد.' => 'Send WhatsApp and we will reply to book the visit.',
        'اتصل أو أرسل واتساب على  ونرد عليك لتحديد الموعد.' => 'Send WhatsApp and we will reply to book the visit.',
        'معلومات تساعدك تفهم المشكلة قبل ما تتصل.' => 'Information that helps you understand the issue before you contact us.',
        'خبرتنا مكتوبة — نصائح عملية لمنزلك في قطر.' => 'Practical written advice for your home in Qatar.',
        'تسربات وعزل وسباكة وتكييف وتنظيف ومكافحة حشرات — من نفس الشركة.' => 'Leaks, insulation, plumbing, AC, cleaning and pest control — from the same company.',
        'كشف التسربات بالكاميرا الحرارية بدون تكسير — نحدد المصدر أولاً.' => 'Thermal leak detection without breaking — we locate the source first.',
        'تعرف المشكلة والتكلفة والمدة قبل أن يبدأ أي فني.' => 'Know the issue, cost and duration before any technician starts.',
        'الدوحة والريان ولوسيل وأم صلال والوكرة والخور وغيرها.' => 'Doha, Al Rayyan, Lusail, Umm Salal, Al Wakrah, Al Khor and more.',
        'فريق ثابت يعرف طبيعة المباني والمناخ في قطر.' => 'A standing team that knows Qatar buildings and climate.',
        'اتصال أو واتساب على مدار الأسبوع — بلا وسطاء.' => 'Call or WhatsApp all week — no middlemen.',
        'مقارنة صريحة بين طريقتنا وما هو شائع في السوق.' => 'A clear comparison between our method and what is common in the market.',
        'مقرنا الدوحة، وفريقنا يصل إليك في أي مدينة.' => 'Based in Doha, and our team reaches you in any city.',
        'تواصل معنا ونوضح لك إمكانية الوصول لموقعك.' => 'Contact us and we will confirm whether we can reach your location.',
        'أرقام تعكس نطاق عملنا داخل الدولة.' => 'Figures that reflect the scale of our work in Qatar.',
        'من أول اتصال حتى إغلاق المشكلة.' => 'From the first contact until the issue is closed.',
        'اتصال أو واتساب، ونحدد موعد زيارة الموقع.' => 'Call or WhatsApp, and we book a site visit.',
        'تشخيص بالأجهزة وتقرير مصوّر يوضح المشكلة ومصدرها.' => 'Instrument diagnosis and a photo report showing the issue and its source.',
        'تكلفة ومدة مكتوبة قبل بدء أي عمل.' => 'Cost and duration in writing before any work starts.',
        'ننفّذ ونسلّم بعد معاينتك — مع متابعة بعد التسليم.' => 'We carry out the work and hand over after your inspection — with follow-up after handover.',
        'تحديد دقيق لمصدر التسرب بدون تكسير.' => 'Precise leak location without breaking.',
        'حماية من الحرارة وتسرب المياه.' => 'Protection from heat and water leaks.',
        'صيانة شاملة للمباني والمنشآت.' => 'Full maintenance for buildings and facilities.',
        'تركيب وصيانة وإصلاح الأعطال.' => 'Installation, servicing and fault repair.',
        'إصلاح وتركيب احترافي يدوم.' => 'Professional repair and installation that lasts.',
        'حل الانسدادات من جذورها.' => 'Clearing blockages at the source.',
        'نظافة عميقة لكل المساحات.' => 'Deep cleaning for every space.',
        'إبادة آمنة ومرخّصة.' => 'Safe, licensed pest control.',
        'مساحات خارجية بتصميم وتنفيذ متكامل.' => 'Outdoor spaces designed and built as one project.',
        'تنفيذ ومعالجة وصيانة دورية.' => 'Build, treat and maintain on a schedule.',
        'تشطيب داخلي بلمسة نظيفة.' => 'Interior finishing with a clean result.',
        'توريد وتركيب أنظمة الطاقة الشمسية.' => 'Supply and installation of solar systems.',
        'تعرف المشكلة ومصدرها قبل ما تدفع' => 'Know the issue and its source before you pay',
        'تقرير مصوّر قبل أي إصلاح' => 'Photo report before any repair',
        'تشخيص بالأجهزة قبل التكسير' => 'Instrument diagnosis before breaking',
        'عرض سعر مكتوب قبل البدء' => 'Written quote before work starts',
        'الصيانة العامة وصيانة المباني' => 'General and building maintenance',
        'التكييف والأجهزة الكهربائية' => 'AC and electrical appliances',
        'الصبغ والجبس بورد والديكورات' => 'Painting, gypsum board and interiors',
        'تصميم وتنفيذ الديكورات' => 'Interior design and fit-out',
        'تركيب وصيانة التكييف' => 'AC installation and maintenance',
        'صيانة الأجهزة الكهربائية' => 'Electrical appliance maintenance',
        'إنشاء وصيانة المسابح' => 'Pool construction and maintenance',
        'خدمات الطاقة الشمسية' => 'Solar energy services',
        'العزل المائي والحراري' => 'Waterproofing and thermal insulation',
        'التنظيف والتعقيم' => 'Cleaning and disinfection',
        'مكافحة الحشرات' => 'Pest control',
        'تنسيق الحدائق' => 'Landscaping',
        'النوافير والشلالات' => 'Fountains and waterfalls',
        'الصبغ والدهانات' => 'Painting and coatings',
        'تركيب الجبس بورد' => 'Gypsum board installation',
        'التشطيبات الداخلية' => 'Interior finishing',
        'كشف تسربات المياه' => 'Water leak detection',
        'عزل الأسطح' => 'Roof insulation',
        'الصيانة العامة' => 'General maintenance',
        'صيانة المباني' => 'Building maintenance',
        'أعمال السباكة' => 'Plumbing works',
        'تسليك المجاري' => 'Drain clearing',
        'أعمال الكهرباء' => 'Electrical works',
        'لوحة خدمات ركن التطور — قطر' => 'Rukn El-Tatawer services board — Qatar',
        'ركن التطور قطر —' => 'Rukn El-Tatawer Qatar —',
        'الخدمات المنزلية المتكاملة' => 'integrated home services',
        'خدماتنا المنزلية' => 'Our home services',
        'المتكاملة في قطر' => 'complete in Qatar',
        'في كل مدن الدولة' => 'across every city in the country',
        'شركة ركن التطور قطر' => 'Rukn El-Tatawer Company Qatar',
        'شركة ركن التطور - قطر' => 'Rukn El-Tatawer Company - Qatar',
        'من نحن — ركن التطور في قطر' => 'About us — Rukn El-Tatawer in Qatar',
        'اتصل بنا — ركن التطور قطر' => 'Contact us — Rukn El-Tatawer Qatar',
        'الصيانة المنزلية والأجهزة' => 'Home and appliance maintenance',
        'لماذا يختار عملاء قطر' => 'Why Qatar clients choose',
        'ركن التطور في قطر' => 'Rukn El-Tatawer in Qatar',
        'ركن التطور؟' => 'Rukn El-Tatawer?',
        'ركن التطور' => 'Rukn El-Tatawer',
        'أكمل الطلب عبر واتساب' => 'Complete the request on WhatsApp',
        'تواصل عبر واتساب' => 'Chat on WhatsApp',
        'اطلب الخدمة الآن' => 'Request the service now',
        'اطلب الخدمة' => 'Request service',
        'اختر الخدمة' => 'Choose service',
        'اختر المدينة' => 'Choose city',
        'اختر الإمارة' => 'Choose city',
        'ما الخدمة التي' => 'What service do you',
        'تحتاجها؟' => 'need?',
        'ابدأ الآن' => 'Start now',
        'كشف بدون تكسير' => 'Detection without breaking',
        'نغطي كل مدن قطر' => 'We cover every city in Qatar',
        '20 خدمة منزلية' => '20 home services',
        'عرض سعر مكتوب' => 'Written quote',
        'كشف تسربات' => 'Leak detection',
        'عزل أسطح' => 'Roof insulation',
        'صيانة تكييف' => 'AC maintenance',
        'تنظيف وتعقيم' => 'Cleaning and disinfection',
        'مكافحة حشرات' => 'Pest control',
        'سباكة وتسليك' => 'Plumbing and drains',
        'مدن تغطية' => 'cities covered',
        'فريق مقيم في قطر' => 'Qatar-based team',
        'متابعة بعد التسليم' => 'Follow-up after handover',
        'وقت الاستجابة' => 'Response time',
        'حالة الخدمة' => 'Service status',
        'دعم الطوارئ' => 'Emergency support',
        'يُحدَّد عند التواصل' => 'Confirmed when you contact us',
        'كاميرا حرارية متطورة' => 'Advanced thermal camera',
        'بدون تكسير' => 'No breaking',
        'تقرير مصوّر مفصّل' => 'Detailed photo report',
        'إصلاح بعد التشخيص' => 'Repair after diagnosis',
        'عزل فوم بولي يوريثان' => 'Spray polyurethane foam',
        'أغشية بيتومينية معدّلة' => 'Modified bitumen membranes',
        'طلاء عازل للحرارة' => 'Heat-reflective coating',
        'عزل خزانات وحمامات' => 'Tank and bathroom waterproofing',
        'معالجة الشروخ' => 'Crack repair',
        'ترميم وتجديد' => 'Restoration and renovation',
        'عقود صيانة دورية' => 'Scheduled maintenance contracts',
        'تنظيف الفلاتر والكويل' => 'Filter and coil cleaning',
        'شحن الفريون' => 'Refrigerant recharge',
        'إصلاح الأجهزة الكهربائية' => 'Electrical appliance repair',
        'تمديدات وإنارة' => 'Wiring and lighting',
        'إصلاح تسربات الأنابيب' => 'Pipe leak repair',
        'تركيب الأدوات الصحية' => 'Sanitary ware installation',
        'فحص شبكات المياه' => 'Water network inspection',
        'توصيل السخانات' => 'Water heater connection',
        'تسليك بالضغط' => 'High-pressure clearing',
        'تسليك بالسوستة' => 'Cable drain clearing',
        'كاميرا فحص المواسير' => 'Pipe inspection camera',
        'تنظيف بيارات' => 'Septic tank cleaning',
        'تنظيف عميق شامل' => 'Full deep clean',
        'تعقيم بالبخار' => 'Steam disinfection',
        'تنظيف الخزانات' => 'Tank cleaning',
        'مواد صديقة للبيئة' => 'Eco-friendly materials',
        'مواد آمنة ومرخصة' => 'Safe licensed materials',
        'إبادة كاملة' => 'Full treatment',
        'متابعة بعد التنفيذ' => 'Follow-up after the job',
        'آمن للأطفال' => 'Child-safe',
        'تصميم الحدائق' => 'Garden design',
        'عشب طبيعي وصناعي' => 'Natural and artificial turf',
        'شبكات ري' => 'Irrigation networks',
        'إنارة خارجية' => 'Outdoor lighting',
        'إنشاء مسابح' => 'Pool construction',
        'معالجة المياه' => 'Water treatment',
        'صيانة دورية' => 'Scheduled maintenance',
        'نوافير وشلالات' => 'Fountains and waterfalls',
        'صبغ داخلي وخارجي' => 'Indoor and outdoor painting',
        'تركيب جبس بورد' => 'Gypsum board installation',
        'تصميم وتنفيذ ديكورات' => 'Interior design and fit-out',
        'تشطيبات داخلية' => 'Interior finishing',
        'دراسة الاستهلاك' => 'Consumption study',
        'توريد وتركيب الألواح' => 'Panel supply and installation',
        'سخانات شمسية' => 'Solar water heaters',
        'لماذا نحن' => 'Why us',
        'كيف نعمل؟' => 'How we work',
        'تواصل وتشخيص' => 'Contact and diagnosis',
        'معاينة وتقرير' => 'Inspection and report',
        'عرض سعر واضح' => 'Clear quote',
        'التنفيذ والمتابعة' => 'Delivery and follow-up',
        'تشخيص قبل الإصلاح' => 'Diagnosis before repair',
        'كل الخدمات في مكان' => 'All services in one place',
        'تقرير وعرض مكتوب' => 'Written report and quote',
        'تغطية مدن قطر' => 'Qatar city coverage',
        'فنيون مدرّبون' => 'Trained technicians',
        'تواصل مباشر' => 'Direct contact',
        'أرقامنا' => 'Our figures',
        'مشروع منفّذ' => 'completed projects',
        'في قطر منذ' => 'in Qatar since',
        'عدد المشاريع' => 'projects',
        'سنة التأسيس' => 'founded',
        'ما الذي يميّز' => 'What sets us apart',
        'الشائع في السوق' => 'Typical in the market',
        'كشف التسرب بدون تكسير' => 'Leak detection without breaking',
        'تقرير مصوّر قبل الإصلاح' => 'Photo report before repair',
        'كل الخدمات من جهة واحدة' => 'All services from one company',
        'تخصص واحد غالباً' => 'Usually one specialism',
        'نطاق التغطية' => 'Coverage',
        'عدد الخدمات' => 'Number of services',
        'مناطق الخدمة' => 'Service areas',
        'تغطية 8 مدن' => '8 cities covered',
        'المقر الرئيسي: الدوحة — قطر.' => 'Head office: Doha — Qatar.',
        'المقر: الدوحة' => 'Office: Doha',
        '20 خدمة متوفرة' => '20 services available',
        'كشف التسربات' => 'Leak detection',
        'السباكة والتسليك' => 'Plumbing and drains',
        'التكييف والكهرباء' => 'AC and electrical',
        'الحدائق والمسابح' => 'Gardens and pools',
        'الطاقة الشمسية' => 'Solar energy',
        'الصبغ والديكورات' => 'Painting and interiors',
        'مدينتك غير مذكورة؟' => 'Is your city not listed?',
        'مركز المعرفة' => 'Knowledge hub',
        'دليل كشف التسربات' => 'Leak detection guide',
        'علامات تسرب المياه' => 'Signs of a water leak',
        'الكشف بدون تكسير' => 'Detection without breaking',
        'تسرب الخزانات' => 'Tank leaks',
        'أنواع العزل المائي' => 'Types of waterproofing',
        'العزل الحراري' => 'Thermal insulation',
        'عزل الأسطح والخزانات' => 'Roof and tank insulation',
        'دليل الصيانة العامة' => 'General maintenance guide',
        'الصيانة الدورية' => 'Scheduled maintenance',
        'صيانة الأجهزة' => 'Appliance servicing',
        'التنظيف ومكافحة الحشرات' => 'Cleaning and pest control',
        'دليل التنظيف' => 'Cleaning guide',
        'التنظيف العميق' => 'Deep cleaning',
        'دليل الطاقة الشمسية' => 'Solar energy guide',
        'كيف تعمل الألواح' => 'How the panels work',
        'السخانات الشمسية' => 'Solar water heaters',
        'دليل العزل' => 'Insulation guide',
        'الخدمات المنزلية' => 'home services',
        'اقرأ المزيد' => 'Read more',
        'كل المقالات' => 'All articles',
        'عندك مشكلة' => 'Have a problem',
        'في منزلك؟' => 'at home?',
        'تغطية كل قطر' => 'Coverage across Qatar',
        'الأسئلة الشائعة' => 'FAQ',
        'هل تكشفون التسرب بدون تكسير؟' => 'Do you detect leaks without breaking?',
        'ما المدن التي تغطونها في قطر؟' => 'Which cities do you cover in Qatar?',
        'كيف أعرف أن عندي تسرب؟' => 'How do I know I have a leak?',
        'هل تقدمون كل الخدمات أم تخصص واحد؟' => 'Do you offer every service or only one specialism?',
        'هل يوجد ضمان على العمل؟' => 'Is the work guaranteed?',
        'كم تستغرق مدة التنفيذ؟' => 'How long does the work take?',
        'هل المعاينة قبل التسعير؟' => 'Is there an inspection before the quote?',
        'كيف أطلب الخدمة؟' => 'How do I request the service?',
        'روابط هامة' => 'Important links',
        'سياسة الخصوصية' => 'Privacy policy',
        'خريطة الموقع' => 'Sitemap',
        'أهم خدماتنا' => 'Top services',
        'روابط سريعة' => 'Quick links',
        'تحدث مع خبير' => 'Talk to an expert',
        'مقرنا الرئيسي' => 'Head office',
        'ابحث في الموقع' => 'Search the site',
        'المعيار' => 'Criteria',
        'مقارنة' => 'Compare',
        'خدماتنا' => 'Our services',
        'المدونة' => 'Blog',
        'العزل' => 'Insulation',
        'الصيانة' => 'Maintenance',
        'التنظيف' => 'Cleaning',
        'المسابح' => 'Pools',
        'الخزانات' => 'Tanks',
        'الدليل' => 'Guide',
        'دليل' => 'Guide',
        'الشائعة' => 'asked',
        'الأسئلة' => 'Questions',
        'الرئيسية' => 'Home',
        'اتصل بنا' => 'Contact us',
        'من نحن' => 'About us',
        'القائمة' => 'Menu',
        'إغلاق' => 'Close',
        'بحث' => 'Search',
        'واتساب' => 'WhatsApp',
        'متاحة' => 'Available',
        'مباشر' => 'Live',
        'محدودة' => 'Limited',
        'نغطي' => 'We cover',
        'المدن' => 'Cities',
        'مدن قطر' => 'Qatar cities',
        'كل مدن قطر' => 'every city in Qatar',
        'مدن' => 'cities',
        'المقر' => 'Office',
        'تغطية' => 'Coverage',
        'فنيون' => 'Technicians',
        'تواصل' => 'Contact',
        'مشاريع' => 'Projects',
        'تأسيس' => 'Founded',
        'عرض سعر' => 'Quote',
        'تقرير مصوّر' => 'Photo report',
        'التكييف والأجهزة' => 'AC and appliances',
        'كل الخدمات' => 'All services',
        'عرض مكتوب' => 'Written quote',
        'تشخيص' => 'Diagnosis',
        'سباكة' => 'Plumbing',
        'الدوحة غالباً' => 'Mostly Doha',
        '8 مدن' => '8 cities',
        '20 خدمة' => '20 services',
        'أم صلال' => 'Umm Salal',
        'الشحانية' => 'Al Shahaniya',
        'الخيسة' => 'Al Kheesa',
        'الوكرة' => 'Al Wakrah',
        'الريان' => 'Al Rayyan',
        'لوسيل' => 'Lusail',
        'الخور' => 'Al Khor',
        'الدوحة' => 'Doha',
        'في قطر' => 'in Qatar',
        'قطر' => 'Qatar',
        'المدينة' => 'city',
        'الإمارة' => 'city',
    ];
    uksort($map, static function ($a, $b) {
        return strlen($b) <=> strlen($a);
    });
    return $map;
}


function rukn_allowed_city_slugs() {
    return [
        'sewerage-company-in-doha',
        'gas-leak-detection-doha',
        'ac-leak-detection-doha',
    ];
}

function rukn_city_hub_path($suffix) {
    $map = [
        'doha' => '/services-in-doha-qatar/',
        'al-rayyan' => '/services-in-al-rayyan-qatar/',
        'al-wakrah' => '/services-in-al-wakrah-qatar/',
        'al-khor' => '/services-in-al-khor-qatar/',
        'umm-salal' => '/services-in-umm-salal-qatar/',
        'al-daayen' => '/services-in-al-daayen-qatar/',
        'al-shamal' => '/services-in-al-shamal-qatar/',
        'al-shahaniya' => '/services-in-al-shahaniya-qatar/',
        'lusail' => '/services-in-lusail-qatar/',
    ];
    return $map[$suffix] ?? null;
}

function rukn_city_suffix($slug) {
    foreach (array_keys([
        'al-shahaniya' => 1, 'al-daayen' => 1, 'umm-salal' => 1, 'al-wakrah' => 1,
        'al-rayyan' => 1, 'al-shamal' => 1, 'al-khor' => 1, 'lusail' => 1, 'doha' => 1,
    ]) as $s) {
        if ($slug === $s || substr($slug, -strlen($s) - 1) === '-' . $s) {
            return $s;
        }
    }
    return null;
}

function rukn_is_city_template($title, $slug) {
    $slug = (string) $slug;
    $title = (string) $title;
    if (in_array($slug, rukn_allowed_city_slugs(), true)) {
        return false;
    }
    if ($slug === 'water-leak-detection-company-in-qatar' || $slug === 'water-leak-detection-qatar-en') {
        return false;
    }
    if (rukn_city_suffix($slug)) {
        return true;
    }
    foreach (['في الدوحة', 'في الريان', 'في الوكرة', 'في الخور', 'في أم صلال', 'في الظعاين', 'في الشمال', 'في الشحانية', 'في لوسيل'] as $city) {
        if (strpos($title, $city) !== false) {
            return true;
        }
    }
    return false;
}

add_action('init', function () {
    if (get_option('rukn_qa_options_patched_v3') === '1') {
        return;
    }

    $titles = get_option('rank-math-options-titles');
    if (is_array($titles)) {
        $titles['geo'] = RUKN_QA_GEO;
        $titles['pt_post_title'] = '%title% %sep% ركن التطور قطر';
        $titles['pt_page_title'] = '%title% %sep% ركن التطور قطر';
        $titles['pt_post_description'] = '%excerpt%';
        $titles['pt_page_description'] = '%excerpt%';
        $titles['pt_post_default_snippet_name'] = '%title% %sep% ركن التطور قطر';
        $titles['pt_page_default_snippet_name'] = '%title% %sep% ركن التطور قطر';
        $titles['tax_category_title'] = '%title% %sep% ركن التطور قطر';
        $titles['tax_post_tag_title'] = '%term% %sep% ركن التطور قطر';
        $titles['tax_city_title'] = '%term% %sep% ركن التطور قطر';
        $titles['pt_faq_title'] = '%title% %sep% ركن التطور قطر';
        $titles['pt_price_title'] = '%title% %sep% ركن التطور قطر';
        $titles['pt_works_title'] = '%title% %sep% ركن التطور قطر';
        $titles['404_title'] = 'الصفحة غير موجودة %sep% ركن التطور قطر';
        $titles['phone_numbers'] = [];
        $titles['local_address'] = [
            'streetAddress' => 'الدوحة',
            'addressLocality' => 'الدوحة',
            'addressRegion' => 'الدوحة',
            'addressCountry' => 'QA',
            'postalCode' => '',
        ];
        update_option('rank-math-options-titles', $titles);
    }

    $theme_mod = get_option('theme_mods_kayan-theme');
    $changed = false;
    if (is_array($theme_mod)) {
        $encoded = wp_json_encode($theme_mod);
        $new = str_replace(
            ['201151481000', '20 1151481000', 'الخيثة', 'المشحمية'],
            [RUKN_QA_WA, RUKN_QA_WA, 'الخيسة', 'الشحانية'],
            $encoded
        );
        if ($new !== $encoded) {
            $decoded = json_decode($new, true);
            if (is_array($decoded)) {
                update_option('theme_mods_kayan-theme', $decoded);
                $changed = true;
            }
        }
    }

    global $wpdb;
    $like_patterns = ['%971586634710%', '%201151481000%', '%الخيثة%', '%المشحمية%', '%RuknCS%', '%wa_number%'];
    $hits = [];
    foreach ($like_patterns as $like) {
        $rows = $wpdb->get_results($wpdb->prepare(
            "SELECT option_name FROM {$wpdb->options} WHERE option_name NOT LIKE %s AND option_value LIKE %s LIMIT 40",
            '_transient%',
            $like
        ));
        foreach ($rows as $row) {
            $hits[] = $row->option_name;
        }
    }
    $hits = array_values(array_unique($hits));
    foreach ($hits as $name) {
        if (in_array($name, ['rank-math-options-titles', 'theme_mods_kayan-theme'], true)) {
            continue;
        }
        $val = get_option($name);
        if (is_string($val)) {
            $nv = str_replace(
                ['201151481000', 'الخيثة', 'المشحمية'],
                [RUKN_QA_WA, 'الخيسة', 'الشحانية'],
                $val
            );
            if ($nv !== $val) {
                update_option($name, $nv);
            }
        } elseif (is_array($val)) {
            $encoded = wp_json_encode($val);
            $new = str_replace(
                ['201151481000', 'الخيثة', 'المشحمية'],
                [RUKN_QA_WA, 'الخيسة', 'الشحانية'],
                $encoded
            );
            if ($new !== $encoded) {
                $decoded = json_decode($new, true);
                if (is_array($decoded)) {
                    update_option($name, $decoded);
                }
            }
        }
    }

    update_option('rukn_qa_debug_option_hits', $hits);
    update_option('rukn_qa_options_patched_v3', '1');
}, 5);

add_filter('rank_math/json_ld', function ($data, $jsonld) {
    if (!is_array($data)) {
        return $data;
    }
    $walk = function (&$node) use (&$walk) {
        if (!is_array($node)) {
            return;
        }
        if (isset($node['geo']['latitude']) && isset($node['geo']['longitude'])) {
            $node['geo']['latitude'] = '25.2854';
            $node['geo']['longitude'] = '51.5310';
        }
        if (isset($node['hasMap']) && is_string($node['hasMap']) && strpos($node['hasMap'], '24.4539') !== false) {
            $node['hasMap'] = 'https://www.google.com/maps/search/?api=1&query=25.2854,51.5310';
        }
        if (isset($node['telephone'])) {
            unset($node['telephone']);
        }
        if (isset($node['address']['addressCountry'])) {
            $node['address']['addressCountry'] = 'QA';
        }
        foreach ($node as &$v) {
            if (is_array($v)) {
                $walk($v);
            }
        }
    };
    $walk($data);
    return $data;
}, 99, 2);

add_filter('rank_math/frontend/canonical', function ($canonical) {
    if (!is_string($canonical)) {
        return $canonical;
    }
    $canonical = str_replace('https://www.rukn-eltatawer.com/qa/qa/', 'https://www.rukn-eltatawer.com/qa/', $canonical);
    if (is_front_page()) {
        return rukn_qa_is_english() ? 'https://www.rukn-eltatawer.com/qa/en/' : 'https://www.rukn-eltatawer.com/qa/';
    }
    return $canonical;
}, 99);

add_filter('robots_txt', function ($output, $public) {
    $output = preg_replace(
        '/^Sitemap:\s*https?:\/\/www\.rukn-eltatawer\.com\/sitemap_index\.xml\s*$/mi',
        '',
        (string) $output
    );
    if (strpos($output, 'rukn-eltatawer.com/qa/sitemap_index.xml') === false) {
        $output .= "\nSitemap: https://www.rukn-eltatawer.com/qa/sitemap_index.xml\n";
    }
    return $output;
}, 99, 2);

add_filter('rank_math/sitemap/robots', function ($robots) {
    return ['Sitemap: https://www.rukn-eltatawer.com/qa/sitemap_index.xml'];
});

add_action('wp_head', function () {
    echo '<style id="rukn-hide-call">.fab-call,a.fab-btn.fab-call,a[href^="tel:"],a[href="tel:"],a[href="tel: "],.--button-call-link-phone,.-callbutton--post-card,.post-card-buttons.-callbutton--post-card,[data-call="Phone"],.btn-call,.kayan-call-btn{display:none!important;visibility:hidden!important;pointer-events:none!important}</style>';
    echo '<style id="rukn-article-ui">
.rukn-article{color:#151c28;line-height:1.85;font-size:17px;max-width:100%}
.rukn-article .article-hero{background:linear-gradient(145deg,#0A1F4E 0%,#041c36 70%);color:#fff;border-radius:18px;padding:22px 20px;margin:16px 0 22px}
.rukn-article .hero-label{display:inline-block;background:#f0c33c;color:#041c36;font-weight:700;font-size:12px;padding:4px 10px;border-radius:999px;margin-bottom:10px}
.rukn-article .article-hero h2{color:#fff;margin:8px 0 10px;font-size:1.35rem;line-height:1.45}
.rukn-article .article-hero p{color:#e3e9f2;margin:0 0 14px}
.rukn-article .hero-buttons,.rukn-article .cta-section{display:flex;flex-wrap:wrap;gap:10px}
.rukn-article .cta-button{display:inline-flex;align-items:center;gap:8px;background:#0e8a47;color:#fff!important;text-decoration:none!important;padding:12px 18px;border-radius:12px;font-weight:700;min-height:44px}
.rukn-article .features-grid,.rukn-article .steps-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:16px 0}
.rukn-article .feature-card,.rukn-article .step-card{background:#fff;border:1px solid #e3e9f2;border-radius:14px;padding:16px;box-shadow:0 6px 18px rgba(10,31,78,.06)}
.rukn-article .feature-card i,.rukn-article .step-card i{color:#1269eb;font-size:22px;margin-bottom:8px}
.rukn-article .step-number{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:50%;background:#0A1F4E;color:#f0c33c;font-weight:800;margin-bottom:8px}
.rukn-article .warning-box{background:#fff5f5;border-right:4px solid #c0392b;border-radius:12px;padding:14px 16px;margin:16px 0}
.rukn-article .expert-tip{background:#edf8ff;border-right:4px solid #2E9DF7;border-radius:12px;padding:14px 16px;margin:16px 0}
.rukn-article .cta-section{background:linear-gradient(145deg,#0A1F4E,#14335e);color:#fff;border-radius:16px;padding:20px;margin:22px 0;flex-direction:column}
.rukn-article .cta-section h2,.rukn-article .cta-section p{color:#fff}
.rukn-article .responsive-table{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:16px 0;border-radius:12px;border:1px solid #e3e9f2}
.rukn-article table{width:100%;border-collapse:collapse;min-width:480px}
.rukn-article th{background:#0A1F4E;color:#fff;padding:10px 12px;text-align:right;font-weight:700}
.rukn-article td{padding:10px 12px;border-bottom:1px solid #eef2f6;background:#fff}
.rukn-article tr:nth-child(even) td{background:#f7fafc}
.rukn-article .faq-item{background:#fff;border:1px solid #e3e9f2;border-radius:12px;padding:14px 16px;margin:10px 0}
.rukn-article .faq-item h3{margin:0 0 8px;font-size:1.05rem;color:#0A1F4E}
.rukn-article img{max-width:100%;height:auto;border-radius:12px}
@media(max-width:640px){.rukn-article{font-size:16px}.rukn-article .features-grid,.rukn-article .steps-grid{grid-template-columns:1fr}.rukn-article .article-hero h2{font-size:1.2rem}.rukn-article table{min-width:100%;font-size:14px}}
</style>';
    echo '<style id="rukn-fa-wa">
.yc-shortcode-features--icon>i,.yc-shortcode-features--icon .fa-solid,.yc-shortcode-features--icon .fas,.rukn-article .fas,.rukn-article .fa-solid{font-family:"Font Awesome 6 Free"!important;font-weight:900!important;font-style:normal!important;display:inline-block!important;line-height:1!important;-webkit-font-smoothing:antialiased}
.yc-shortcode-features--icon .fa-brands,.fa-brands,.fab,i.fa-whatsapp,.--button-call-link-whatsapp i{font-family:"Font Awesome 6 Brands"!important;font-weight:400!important;font-style:normal!important}
.yc-shortcode--section--contactus .--contact--post-call--buttons{display:flex!important;flex-direction:row!important;align-items:center!important;gap:12px}
.yc-shortcode--section--contactus a.--button-call-link-whatsapp,.yc-shortcode--section--contactus a.rukn-wa-3d{display:inline-flex!important;visibility:visible!important;pointer-events:auto!important;align-items:center;justify-content:center;gap:10px;min-height:56px;padding:14px 28px!important;border:0!important;border-radius:18px!important;color:#fff!important;text-decoration:none!important;font-weight:800!important;font-size:18px!important;background:linear-gradient(180deg,#40e57a 0%,#25d366 42%,#128c7e 100%)!important;box-shadow:0 10px 0 #0b6b4f,0 16px 28px rgba(18,140,126,.4)!important;transform:translateY(-4px);text-shadow:0 1px 0 rgba(0,0,0,.15)}
.yc-shortcode--section--contactus a.--button-call-link-whatsapp:hover{transform:translateY(0);box-shadow:0 6px 0 #0b6b4f,0 10px 18px rgba(18,140,126,.35)!important}
.yc-shortcode--section--contactus a.--button-call-link-whatsapp i{font-size:28px!important;margin:0!important}
@media(max-width:640px){.yc-shortcode--section--contactus{flex-direction:column}.yc-shortcode--section--contactus a.--button-call-link-whatsapp{width:100%;box-sizing:border-box}}
</style>';
}, 1);

add_action('wp_footer', function () {
    $wa = RUKN_QA_WA;
    $is_en = rukn_qa_is_english();
    $wa_msg = $is_en
        ? 'Hello, I would like to enquire about Rukn El-Tatawer services in Qatar'
        : 'مرحباً، أريد الاستفسار عن خدمات ركن التطور في قطر';
    $msg = rawurlencode($wa_msg);
    echo '<script id="rukn-qa-contact-fix">';
    echo 'window.RuknCS=Object.assign(window.RuknCS||{},{call_show:false,wa_show:true,call_number:"",wa_number:"' . esc_js($wa) . '",wa_message:"' . esc_js($wa_msg) . '"});';
    echo '(function(){var w="' . esc_js($wa) . '",m="' . $msg . '";';
    echo 'function hideCall(root){root=root||document;root.querySelectorAll(\'a[href^="tel:"],.fab-call,.--button-call-link-phone,.-callbutton--post-card,[data-call="Phone"],.btn-call,.kayan-call-btn\').forEach(function(a){if(a.classList&&(a.classList.contains("fa-whatsapp")||(a.getAttribute("href")||"").indexOf("wa.me")!==-1||a.classList.contains("--button-call-link-whatsapp")))return;a.style.setProperty("display","none","important");a.setAttribute("hidden","hidden");if((a.getAttribute("href")||"").indexOf("tel:")===0)a.removeAttribute("href");});}';
    echo 'function apply(){hideCall();document.querySelectorAll("a[href*=\'wa.me\'],a[href*=\'api.whatsapp\'],a[data-fn-wa],a.btn-wa,a.fab-wa").forEach(function(a){var u="https://wa.me/"+w+"?text="+m;a.setAttribute("href",u);if(a.hasAttribute("data-wa-number")){a.setAttribute("data-wa-number","+"+w);}});}';
    echo 'apply();document.addEventListener("DOMContentLoaded",apply);setTimeout(apply,300);setTimeout(apply,1200);setTimeout(apply,3000);';
    echo 'if(window.MutationObserver){new MutationObserver(function(){apply();}).observe(document.documentElement,{childList:true,subtree:true});}';
    echo '})();';
    echo 'document.addEventListener("DOMContentLoaded",function(){document.querySelectorAll("[data-count]").forEach(function(el){if((el.textContent||"").trim()==="0"){el.textContent=el.getAttribute("data-count")||"0";}});});';
    echo '</script>';
    if (is_front_page()) {
        $is_en = rukn_qa_is_english();
        $url = $is_en
            ? 'https://www.rukn-eltatawer.com/qa/en/water-leak-detection-qatar-en/'
            : 'https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/';
        $label = $is_en ? 'Water leak detection in Qatar' : 'شركة كشف تسربات المياه في قطر';
        echo '<p class="rukn-home-leak-link" style="text-align:center;padding:14px 16px;margin:0;background:#0E2455;"><a style="color:#fff;font-weight:700;text-decoration:none;" href="' . esc_url($url) . '">' . esc_html($label) . '</a></p>';
    }
}, 9999);

add_filter('pre_get_document_title', function ($title) {
    if (is_front_page() && !is_singular()) {
        return rukn_qa_home_title();
    }
    return $title;
}, 99);
add_filter('rank_math/frontend/title', function ($title) {
    if (is_front_page() && !is_singular()) {
        return rukn_qa_home_title();
    }
    return $title;
}, 99);

add_filter('language_attributes', function ($out) {
    if (rukn_qa_is_english()) {
        return 'lang="en-GB" dir="ltr"';
    }
    return $out;
}, 99);

add_action('template_redirect', function () {
    if (is_admin() || wp_doing_ajax() || wp_is_json_request()) {
        return;
    }
    $slug = '';
    $id = 0;
    if (is_singular('post')) {
        $id = (int) get_queried_object_id();
        $slug = (string) get_post_field('post_name', $id);
    } elseif (is_404()) {
        $path = trim((string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH), '/');
        $path = preg_replace('#^qa/#', '', $path);
        $slug = basename($path);
    }
    if ($id !== 2973 && $slug && $slug !== 'water-leak-detection-company-in-qatar' && $slug !== 'water-leak-detection-qatar-en') {
        if (preg_match('/^(water-leak-detection|water-pipe-leak-detection)-/', $slug)) {
            wp_safe_redirect(home_url(RUKN_QA_LEAK), 301);
            exit;
        }
        if (!in_array($slug, rukn_allowed_city_slugs(), true)) {
            $suf = rukn_city_suffix($slug);
            $hub = $suf ? rukn_city_hub_path($suf) : null;
            if ($hub) {
                wp_safe_redirect(home_url($hub), 301);
                exit;
            }
        }
    }
    if (is_post_type_archive('pricing')) {
        wp_safe_redirect(home_url('/as3ar/'), 301);
        exit;
    }
    if (is_page('pricing') || is_page(7464)) {
        add_filter('ez_toc_maybe_apply_the_content_filter', '__return_false', 99);
        add_filter('ez_toc_should_auto_insert', '__return_false', 99);
        add_filter('ez_toc_apply_filter', '__return_false', 99);
    }
    if (is_admin() || wp_doing_ajax() || wp_is_json_request()) {
        return;
    }
    ob_start(function ($html) {
        if (!is_string($html)) {
            return $html;
        }
        $is_locked = is_singular() && (int) get_queried_object_id() === 2973;
        $html = preg_replace('#https://(?:wa\.me|api\.whatsapp\.com/send\?phone=)/?\+?(?:97431110184|97431553076|971586634710)#', 'https://wa.me/971586634710', $html);
        $html = preg_replace('#href="tel:[^"]*"#', 'href="#"', $html);
        $html = str_replace('"wa_number":"97431110184"', '"wa_number":"971586634710"', $html);
        $html = str_replace('"call_number":"+97431110184"', '"call_number":""', $html);
        $html = str_replace('"call_show":true', '"call_show":false', $html);
        $html = preg_replace('/,"aggregateRating"\s*:\s*\{[^{}]*\}/', '', $html);
        if ($is_locked) {
            return $html;
        }
        $html = str_replace(
            [
                'https://www.rukn-eltatawer.com/qa/water-leak-detection/',
                'https://www.rukn-eltatawer.com/qa/services/water-leak-detection/',
            ],
            [
                'https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/',
                'https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/',
            ],
            $html
        );
        $html = str_replace(
            'href="https://www.rukn-eltatawer.com/qa/contact-us/" title="التكييف والأجهزة الكهربائية"',
            'href="https://www.rukn-eltatawer.com/qa/central-air-conditioning-maintenance-in-qatar/" title="التكييف والأجهزة الكهربائية"',
            $html
        );
        $html = str_replace(
            'href="https://www.rukn-eltatawer.com/qa/contact-us/" title="أعمال السباكة"',
            'href="https://www.rukn-eltatawer.com/qa/plumbing-maintenance-in-qatar/" title="أعمال السباكة"',
            $html
        );
        $html = str_replace(
            'href="https://www.rukn-eltatawer.com/qa/contact-us/" title="تسليك المجاري"',
            'href="https://www.rukn-eltatawer.com/qa/shrkh-tslyk-mjary-fy-qtr/" title="تسليك المجاري"',
            $html
        );
        $html = str_replace(
            'href="https://www.rukn-eltatawer.com/qa/contact-us/" title="الصبغ والجبس بورد والديكورات"',
            'href="https://www.rukn-eltatawer.com/qa/shrkh-dhanat-dakhlyh-fy-qtr/" title="الصبغ والجبس بورد والديكورات"',
            $html
        );
        $html = str_replace('اختر الإمارة', 'اختر المدينة', $html);
        $html = str_replace('والإمارة', 'والمدينة', $html);
        $html = str_replace('الإمارة', 'المدينة', $html);
        $html = str_replace('الخيثة', 'الخيسة', $html);
        $html = str_replace('المشحمية', 'الشحانية', $html);
        $html = str_replace('+974 3111 0184', '', $html);
        $html = str_replace('+97431110184', '', $html);
        $html = str_replace('97431110184', '', $html);
        $html = str_replace('3111 0184', '', $html);
        $html = preg_replace('/<iframe[^>]+Mazid\+Mall[^>]*>/i', '', $html);
        $html = str_replace('Mazid+Mall', 'Doha+Qatar', $html);
        $html = str_replace('Office 306, Tower A, Mazid Mall, Mohamed Bin Zayed City, Abu Dhabi, UAE', 'الدوحة، قطر', $html);
        $html = str_replace('اتصال وواتساب', 'واتساب', $html);
        $html = str_replace('شركة إماراتية متخصصة', 'شركة قطرية متخصصة', $html);
        $html = str_replace('داخل أبوظبي وبقية قطر', 'في الدوحة وبقية مدن قطر', $html);
        $html = str_replace('أبوظبي', 'الدوحة', $html);
        $html = str_replace('تغطية جميع الإمارات', 'تغطية مدن قطر', $html);
        $html = str_replace('جميع إمارات الدولة', 'كل مدن قطر', $html);
        $html = str_replace('إمارات الدولة', 'مدن قطر', $html);
        $html = str_replace('جميع الإمارات', 'مدن قطر', $html);
        $html = str_replace('كل الإمارات', 'مدن قطر', $html);
        $html = str_replace('السوق الإماراتي', 'السوق القطري', $html);
        $html = str_replace('دولة الإمارات', 'دولة قطر', $html);
        $html = str_replace('في الإمارات', 'في قطر', $html);
        $html = str_replace('الإمارات', 'قطر', $html);
        $html = str_replace('المجموعه المتحده للخدمات المتكاملة', 'شركة ركن التطور', $html);
        $html = str_replace('https://www.rukn-eltatawer.com/qa/qa/', 'https://www.rukn-eltatawer.com/qa/', $html);
        $is_en = rukn_qa_is_english();
        if ($is_en) {
            $pairs = rukn_qa_en_pairs();
            $html = str_replace(array_keys($pairs), array_values($pairs), $html);
            $html = preg_replace('/<html[^>]*>/', '<html lang="en-GB" dir="ltr">', $html, 1);
        }
        if (is_front_page()) {
            $home_title = rukn_qa_home_title();
            $html = preg_replace(
                '/<title>.*?<\/title>/is',
                '<title>' . esc_html($home_title) . '</title>',
                $html,
                1
            );
        }
        return $html;
    });
});


add_action('rest_api_init', function () {
    register_rest_route('rukn-qa/v1', '/redirect', [
        'methods' => 'POST',
        'permission_callback' => function () { return current_user_can('manage_options'); },
        'callback' => function ($req) {
            $from = ltrim((string) $req->get_param('from'), '/');
            $to = (string) $req->get_param('to');
            if (!$from || !$to) {
                return new WP_Error('bad', 'from/to required', ['status' => 400]);
            }
            if (class_exists('\RankMath\Redirections\DB')) {
                $id = \RankMath\Redirections\DB::add([
                    'sources' => [['pattern' => $from, 'comparison' => 'exact']],
                    'url_to' => $to,
                    'header_code' => 301,
                    'status' => 'active',
                ]);
                return ['ok' => true, 'id' => $id, 'engine' => 'rankmath'];
            }
            return new WP_Error('no_rm', 'Rank Math redirections unavailable', ['status' => 500]);
        },
    ]);
});



/** Freeze ranking leak article (#2973) — do not change title/slug/content/status. */
add_filter('wp_insert_post_data', function ($data, $postarr) {
    $id = isset($postarr['ID']) ? (int) $postarr['ID'] : 0;
    if ($id === 2973 && empty($GLOBALS['rukn_unlock_2973'])) {
        $orig = get_post(2973);
        if ($orig) {
            $data['post_title'] = $orig->post_title;
            $data['post_name'] = $orig->post_name;
            $data['post_content'] = $orig->post_content;
            $data['post_excerpt'] = $orig->post_excerpt;
            $data['post_status'] = 'publish';
        }
        return $data;
    }
    $blob = ($data['post_title'] ?? '') . ' ' . ($data['post_name'] ?? '');
    $status = $data['post_status'] ?? '';
    $type = $data['post_type'] ?? 'post';
    if (
        $type === 'post'
        && in_array($status, ['publish', 'future'], true)
        && $id !== 12866
        && strpos($blob, 'qatar-en') === false
        && strpos($blob, 'الغاز') === false
        && strpos($blob, 'التكييف') === false
        && strpos($blob, 'المسبح') === false
        && strpos($blob, 'gas-leak') === false
        && strpos($blob, 'ac-leak') === false
        && strpos($blob, 'pool') === false
        && (
            strpos($blob, 'كشف تسربات المياه في') !== false
            || strpos($blob, 'كشف تسريبات مواسير') !== false
            || strpos($blob, 'water-leak-detection-') !== false
            || strpos($blob, 'water-pipe-leak-detection-') !== false
        )
    ) {
        $data['post_status'] = 'draft';
    }
    if (
        $type === 'post'
        && in_array($status, ['publish', 'future'], true)
        && rukn_is_city_template($data['post_title'] ?? '', $data['post_name'] ?? '')
    ) {
        $data['post_status'] = 'draft';
    }
    return $data;
}, 99, 2);

add_filter('update_post_metadata', function ($check, $object_id, $meta_key) {
    if ((int) $object_id !== 2973 || !empty($GLOBALS['rukn_unlock_2973'])) {
        return $check;
    }
    if (is_string($meta_key) && strpos($meta_key, 'rank_math') === 0) {
        return true;
    }
    return $check;
}, 10, 3);

add_action('rest_api_init', function () {
    register_rest_route('rukn-qa/v1', '/kayan-home', [
        'methods' => 'GET',
        'permission_callback' => function () { return current_user_can('manage_options'); },
        'callback' => function () {
            global $wpdb;
            $names = $wpdb->get_col("SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE '%kayan%' OR option_name LIKE '%rukn%' OR option_name LIKE '%homepage%' LIMIT 120");
            $out = ['names' => $names];
            foreach ([
                'kayan_homepage_sections_order',
                'kayan_home_seeded_v1',
                'kayan_seed_home_done_v141',
                'theme_mods_kayan-theme',
            ] as $k) {
                $v = get_option($k);
                if (is_array($v) || is_object($v)) {
                    $json = wp_json_encode($v);
                    $out[$k] = ['type' => 'array', 'len' => strlen($json), 'preview' => substr($json, 0, 2500)];
                } else {
                    $out[$k] = $v;
                }
            }
            return $out;
        },
    ]);
});


add_action('rest_api_init', function () {
    register_rest_route('rukn-qa/v1', '/seed-widget', [
        'methods' => ['GET', 'POST'],
        'permission_callback' => function () { return current_user_can('manage_options'); },
        'callback' => function ($req) {
            $id = (int) $req->get_param('id');
            if ($id <= 0) {
                return get_option('kayan_homepage_sections_order');
            }
            $p = get_post($id);
            if (!$p) {
                return new WP_Error('missing', 'no post', ['status' => 404]);
            }
            if ($req->get_method() === 'POST') {
                $wpm = $req->get_param('widget_post_meta');
                if (is_array($wpm)) {
                    update_post_meta($id, 'widget_post_meta', $wpm);
                }
                $p = get_post($id);
            }
            $meta = get_post_meta($id);
            $meta_out = [];
            foreach ($meta as $k => $vals) {
                $meta_out[$k] = maybe_unserialize($vals[0]);
            }
            return [
                'id' => $p->ID,
                'type' => $p->post_type,
                'title' => $p->post_title,
                'content' => $p->post_content,
                'meta' => $meta_out,
            ];
        },
    ]);
});

add_filter('register_post_type_args', function ($args, $post_type) {
    if ($post_type === 'pricing') {
        $args['has_archive'] = false;
    }
    return $args;
}, 99, 2);

add_action('init', function () {
    if (get_option('rukn_qa_options_patched_v5') === '1') {
        return;
    }
    $gen = get_option('rank-math-options-general');
    if (is_array($gen) && !empty($gen['robots_txt']) && is_string($gen['robots_txt'])) {
        $gen['robots_txt'] = preg_replace(
            '/Sitemap:\s*https?:\/\/www\.rukn-eltatawer\.com\/sitemap_index\.xml/',
            'Sitemap: https://www.rukn-eltatawer.com/qa/sitemap_index.xml',
            $gen['robots_txt']
        );
        update_option('rank-math-options-general', $gen);
    }
    flush_rewrite_rules(false);
    if (function_exists('do_action')) {
        do_action('litespeed_purge_all');
    }
    update_option('rukn_qa_options_patched_v5', '1');
}, 20);

add_action('init', function () {
    if (get_option('rukn_qa_options_patched_v6') === '1') {
        return;
    }
    update_option('rukn_hide_call_global', '1');
    $titles = get_option('rank-math-options-titles');
    if (is_array($titles)) {
        $titles['phone_numbers'] = [];
        $titles['pt_price_title'] = '%title% %sep% ركن التطور قطر';
        $titles['pt_pricing_title'] = '%title% %sep% ركن التطور قطر';
        $titles['breadcrumbs_archive_format'] = 'الأرشيف: %s';
        $titles['breadcrumbs_search_format'] = 'نتائج البحث: %s';
        $titles['breadcrumbs_404_title'] = 'الصفحة غير موجودة';
        unset($titles['facebook_admin_id']);
        update_option('rank-math-options-titles', $titles);
    }
    $gen = get_option('rank-math-options-general');
    if (is_array($gen)) {
        $gen['add_img_alt'] = 'on';
        $gen['add_img_title'] = 'on';
        if (isset($gen['content_ai_language'])) {
            $gen['content_ai_language'] = 'ar';
        }
        if (isset($gen['content_ai_country'])) {
            $gen['content_ai_country'] = 'QA';
        }
        update_option('rank-math-options-general', $gen);
    }
    update_option('page_for_posts', 2453);
    $mods = get_option('theme_mods_kayan-theme');
    if (is_array($mods)) {
        if (!isset($mods['nav_menu_locations']) || !is_array($mods['nav_menu_locations'])) {
            $mods['nav_menu_locations'] = [];
        }
        $mods['nav_menu_locations']['main-menu'] = 2372;
        update_option('theme_mods_kayan-theme', $mods);
    }
    if (function_exists('do_action')) {
        do_action('litespeed_purge_all');
    }
    update_option('rukn_qa_options_patched_v6', '1');
}, 25);

add_action('rest_api_init', function () {
    register_rest_route('rukn-qa/v1', '/draft-city-templates', [
        'methods' => 'POST',
        'permission_callback' => function () { return current_user_can('manage_options'); },
        'callback' => function () {
            global $wpdb;
            $keep = [
                'water-leak-detection-company-in-qatar',
                'water-leak-detection-qatar-en',
                'roof-insulation-qatar-en',
                'ac-maintenance-qatar-en',
                'gas-leak-detection-doha',
                'ac-leak-detection-doha',
                'sewerage-company-in-doha',
            ];
            $in = implode(',', array_fill(0, count($keep), '%s'));
            $like = "
                post_name LIKE %s OR post_name LIKE %s OR post_name LIKE %s OR post_name LIKE %s
                OR post_name LIKE %s OR post_name LIKE %s OR post_name LIKE %s OR post_name LIKE %s
                OR post_name LIKE %s
            ";
            $sql = $wpdb->prepare(
                "UPDATE {$wpdb->posts} SET post_status = 'draft'
                 WHERE post_type = 'post' AND ID <> 2973
                 AND post_status IN ('publish','future')
                 AND post_name NOT IN ($in)
                 AND ($like)",
                array_merge($keep, [
                    '%-doha', '%-al-rayyan', '%-al-wakrah', '%-al-khor', '%-umm-salal',
                    '%-al-daayen', '%-al-shamal', '%-al-shahaniya', '%-lusail',
                ])
            );
            $n = $wpdb->query($sql);
            if (function_exists('wp_cache_flush')) {
                wp_cache_flush();
            }
            return ['updated' => $n];
        },
    ]);
    register_rest_route('rukn-qa/v1', '/robots-file', [
        'methods' => ['GET', 'POST'],
        'permission_callback' => function () { return current_user_can('manage_options'); },
        'callback' => function ($req) {
            $path = rtrim(ABSPATH, '/\\') . '/robots.txt';
            $desired = "User-Agent: *\nAllow: /\nAllow: /wp-admin/admin-ajax.php\nAllow: /wp-content/uploads/\nDisallow: /wp-admin/\nDisallow: /wp-includes/\nDisallow: /wp-content/plugins/\nDisallow: /trackback\nDisallow: /*.php$\nDisallow: /*.inc$\nDisallow: /*.gz$\n\n# We de-index the login page (unnecessary content)\nDisallow: /wp-login.php\n\nSitemap: https://www.rukn-eltatawer.com/qa/sitemap_index.xml\n";
            $parent = dirname(rtrim(ABSPATH, '/\\')) . '/robots.txt';
            $out = [
                'abspath' => ABSPATH,
                'path' => $path,
                'exists' => file_exists($path),
                'writable' => is_writable($path) || (!file_exists($path) && is_writable(dirname($path))),
                'current' => file_exists($path) ? file_get_contents($path) : null,
                'parent_path' => $parent,
                'parent_writable' => is_writable($parent),
                'parent_current' => file_exists($parent) ? file_get_contents($parent) : null,
            ];
            if ($req->get_method() === 'POST') {
                $ok = @file_put_contents($path, $desired);
                $out['wrote'] = $ok !== false;
                $out['bytes'] = $ok;
                $out['current'] = file_exists($path) ? file_get_contents($path) : null;
                $qa_line = 'Sitemap: https://www.rukn-eltatawer.com/qa/sitemap_index.xml';
                if (file_exists($parent) && is_writable($parent)) {
                    $pc = (string) file_get_contents($parent);
                    if (strpos($pc, 'rukn-eltatawer.com/qa/sitemap_index.xml') === false) {
                        $out['parent_appended'] = (bool) @file_put_contents($parent, rtrim($pc) . "\n" . $qa_line . "\n");
                    } else {
                        $out['parent_appended'] = 'already';
                    }
                    $out['parent_current'] = file_get_contents($parent);
                }
                if (function_exists('do_action')) {
                    do_action('litespeed_purge_url', home_url('/robots.txt'));
                    do_action('litespeed_purge_all');
                }
            }
            return $out;
        },
    ]);
    register_rest_route('rukn-qa/v1', '/theme-inspect', [
        'methods' => 'GET',
        'permission_callback' => function () { return current_user_can('manage_options'); },
        'callback' => function ($req) {
            $theme = get_template_directory();
            $q = (string) $req->get_param('q');
            if ($q === '') {
                $q = 'post__features__data';
            }
            $file = (string) $req->get_param('file');
            $out = [
                'theme' => $theme,
                'query' => $q,
                'file' => $file,
                'matches' => [],
                'shortcodes' => [],
                'content' => null,
            ];
            if ($file !== '') {
                $full = $theme . '/' . ltrim(str_replace(['..', "\0"], '', $file), '/');
                $real_theme = realpath($theme);
                $real_file = realpath($full);
                if ($real_theme && $real_file && strpos($real_file, $real_theme) === 0 && is_file($real_file)) {
                    $out['content'] = file_get_contents($real_file);
                }
                return $out;
            }
            global $shortcode_tags;
            if (is_array($shortcode_tags)) {
                foreach (array_keys($shortcode_tags) as $tag) {
                    if ($q === '*' || stripos($tag, $q) !== false || preg_match('/post_|feature|step|service|price|gallery|faq|schema/i', $tag)) {
                        $out['shortcodes'][] = $tag;
                    }
                }
            }
            if (!is_dir($theme)) {
                return $out;
            }
            $limit = 40;
            $rii = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($theme, FilesystemIterator::SKIP_DOTS));
            foreach ($rii as $file) {
                if (count($out['matches']) >= $limit) {
                    break;
                }
                if (!$file->isFile()) {
                    continue;
                }
                $ext = strtolower($file->getExtension());
                if (!in_array($ext, ['php', 'js', 'json'], true)) {
                    continue;
                }
                $path = $file->getPathname();
                $c = @file_get_contents($path);
                if (!is_string($c) || $c === '' || stripos($c, $q) === false) {
                    continue;
                }
                $hits = [];
                $offset = 0;
                $qlower = strtolower($q);
                $clower = strtolower($c);
                while (count($hits) < 4 && ($pos = strpos($clower, $qlower, $offset)) !== false) {
                    $start = max(0, $pos - 180);
                    $hits[] = substr($c, $start, 900);
                    $offset = $pos + max(1, strlen($q));
                }
                $out['matches'][] = [
                    'file' => str_replace($theme . '/', '', $path),
                    'hits' => $hits,
                ];
            }
            return $out;
        },
    ]);
    register_rest_route('rukn-qa/v1', '/post-blocks', [
        'methods' => ['GET', 'POST'],
        'permission_callback' => function () { return current_user_can('manage_options'); },
        'callback' => function ($req) {
            $id = (int) $req->get_param('id');
            if ($id <= 0) {
                return new WP_Error('missing', 'id required', ['status' => 400]);
            }
            if ($id === 2973 && empty($GLOBALS['rukn_unlock_2973'])) {
                return new WP_Error('locked', 'post 2973 is locked', ['status' => 403]);
            }
            $p = get_post($id);
            if (!$p) {
                return new WP_Error('missing', 'no post', ['status' => 404]);
            }
            if ($req->get_method() === 'POST') {
                $json = $req->get_json_params();
                if (!is_array($json)) {
                    $json = [];
                }
                $meta = $json['meta'] ?? $req->get_param('meta');
                $updated = [];
                if (is_array($meta)) {
                    foreach ($meta as $k => $v) {
                        if (!is_string($k) || $k === '' || strpos($k, 'rank_math') === 0) {
                            continue;
                        }
                        update_post_meta($id, $k, $v);
                        $updated[] = $k;
                    }
                }
                $excerpt = $json['excerpt'] ?? $req->get_param('excerpt');
                $content = $json['content'] ?? $req->get_param('content');
                $post_update = ['ID' => $id];
                if (is_string($excerpt) && $excerpt !== '') {
                    $post_update['post_excerpt'] = wp_strip_all_tags($excerpt);
                    $updated[] = 'excerpt';
                }
                if (is_string($content) && $content !== '') {
                    $post_update['post_content'] = $content;
                    $updated[] = 'content';
                }
                if (count($post_update) > 1) {
                    wp_update_post($post_update);
                }
                $tags = $json['tags'] ?? $req->get_param('tags');
                if (is_array($tags) && $p->post_type === 'post') {
                    $tag_ids = [];
                    foreach ($tags as $t) {
                        $name = is_string($t) ? trim($t) : '';
                        if ($name === '') {
                            continue;
                        }
                        $term = term_exists($name, 'post_tag');
                        if (!$term) {
                            $term = wp_insert_term($name, 'post_tag');
                        }
                        if (is_array($term) && !empty($term['term_id'])) {
                            $tag_ids[] = (int) $term['term_id'];
                        }
                    }
                    if ($tag_ids) {
                        wp_set_post_terms($id, $tag_ids, 'post_tag', false);
                        $updated[] = 'tags';
                    }
                }
                $cities = $json['cities'] ?? $req->get_param('cities');
                if (is_array($cities) && taxonomy_exists('cities')) {
                    $city_ids = [];
                    foreach ($cities as $c) {
                        $name = is_string($c) ? trim($c) : '';
                        if ($name === '') {
                            continue;
                        }
                        $term = term_exists($name, 'cities');
                        if (!$term) {
                            $term = wp_insert_term($name, 'cities');
                        }
                        if (is_array($term) && !empty($term['term_id'])) {
                            $city_ids[] = (int) $term['term_id'];
                        }
                    }
                    if ($city_ids) {
                        wp_set_object_terms($id, $city_ids, 'cities', false);
                        $updated[] = 'cities';
                    }
                }
                if (function_exists('do_action')) {
                    do_action('litespeed_purge_post', $id);
                }
                $p = get_post($id);
                return [
                    'id' => $id,
                    'updated' => $updated,
                    'excerpt' => $p ? $p->post_excerpt : '',
                    'tags' => wp_get_post_terms($id, 'post_tag', ['fields' => 'names']),
                ];
            }
            $meta = get_post_meta($id);
            $meta_out = [];
            foreach ($meta as $k => $vals) {
                $meta_out[$k] = maybe_unserialize($vals[0]);
            }
            return [
                'id' => $p->ID,
                'type' => $p->post_type,
                'title' => $p->post_title,
                'excerpt' => $p->post_excerpt,
                'meta' => $meta_out,
                'tags' => wp_get_post_terms($id, 'post_tag', ['fields' => 'names']),
            ];
        },
    ]);
});
