/**
 * Rukn Qatar city×service grid publisher
 * Unique copy per city+service. Keep UAE WhatsApp. Hide calls. No Qatar numbers.
 * Skip shipping / piano / hospital / school pages.
 * Fast path: $wpdb->update (bypass wp_update_post hooks).
 */
if (!defined('ABSPATH')) {
    return;
}

const RUKN_GRID_WA = '971586634710';

function rukn_grid_skip_slug($slug) {
    $slug = (string) $slug;
    $needles = [
        'air-freight', 'car-shipping', 'cargo-shipping', 'domestic-shipping',
        'express-parcel-shipping', 'furniture-shipping', 'land-freight', 'sea-freight',
        'shipping-offices', 'piano-moving', 'hospital-clinic-cleaning', 'school-nursery-cleaning',
    ];
    foreach ($needles as $n) {
        if ($slug === $n || strpos($slug, $n . '-') === 0) {
            return true;
        }
    }
    return strpos($slug, 'shipping') !== false;
}

function rukn_grid_cities() {
    return [
        'doha' => [
            'ar' => 'الدوحة', 'in' => 'في الدوحة', 'prep' => 'بالدوحة',
            'areas' => 'الخليج الغربي واللؤلؤة والثمامة ومشيرب والسد وبن محمود',
            'stock' => 'أبراج سكنية وفلل قديمة ومبانٍ بعد تشطيب',
            'note' => 'الكثافة والحرارة تجعل العطل يظهر أسرع في فاتورة كهرماء والرطوبة',
            'access' => 'أبراج الخليج الغربي تحتاج تنسيقاً مع الأمن قبل دخول الفني',
            'hub' => '/services-in-doha-qatar/',
        ],
        'lusail' => [
            'ar' => 'لوسيل', 'in' => 'في لوسيل', 'prep' => 'بلوسيل',
            'areas' => 'المارينا وفوكس هيلز وقطيفان ولوسيل وسترن',
            'stock' => 'أبراج جديدة وتشطيبات حديثة ومواقف تحت الأرض',
            'note' => 'غبار التشطيب وملوحة الهواء قرب البحر يظهران في العزل والتكييف والدكت',
            'access' => 'المداخل والمواقف الجديدة تُحدد في رسالة واتساب قبل الزيارة',
            'hub' => '/services-in-lusail-qatar/',
        ],
        'al-rayyan' => [
            'ar' => 'الريان', 'in' => 'في الريان', 'prep' => 'بالريان',
            'areas' => 'العزيزية والوعب والغرافة والتعليم ومدينة خليفة',
            'stock' => 'فلل بمساحات كبيرة وأحواش وأسقف واسعة',
            'note' => 'الميل في الأسطح الكبيرة والخزانات الأرضية يختلف عن برج الدوحة',
            'access' => 'الفلل المنفصلة أوضح للوصول من المجمعات المغلقة',
            'hub' => '/services-in-al-rayyan-qatar/',
        ],
        'al-wakrah' => [
            'ar' => 'الوكرة', 'in' => 'في الوكرة', 'prep' => 'بالوكرة',
            'areas' => 'الوكرة القديمة والوكير ومسيعيد وأحواش الساحل',
            'stock' => 'بيوت شعبيّة وفلل ساحلية ومستودعات خفيفة',
            'note' => 'رطوبة البحر والملح يسرّعان تآكل العزل والمكيف الخارجي',
            'access' => 'المسافة من الدوحة تُذكر في موعد المعاينة بعد العنوان',
            'hub' => '/services-in-al-wakrah-qatar/',
        ],
        'al-khor' => [
            'ar' => 'الخور', 'in' => 'في الخور', 'prep' => 'بالخور',
            'areas' => 'الخور والذخيرة وروضة راشد',
            'stock' => 'فلل ومبانٍ منخفضة ومزارع صغيرة',
            'note' => 'الرحلة من الدوحة جزء من الجدولة؛ العطل الليلي يُذكر في الرسالة',
            'access' => 'نؤكد إمكانية الوصول في نفس اليوم أو اليوم التالي حسب الجدول',
            'hub' => '/services-in-al-khor-qatar/',
        ],
        'umm-salal' => [
            'ar' => 'أم صلال', 'in' => 'في أم صلال والخيسة', 'prep' => 'بأم صلال',
            'areas' => 'أم صلال محمد وأم صلال علي والخيسة',
            'stock' => 'فلل ومساحات مفتوحة وخزانات أرضية',
            'note' => 'الخيسة تُغطى مع أم صلال في نفس الجدولة',
            'access' => 'العنوان يوضّح الخيسة أو أم صلال حتى لا يتأخر الفني',
            'hub' => '/services-in-umm-salal-qatar/',
        ],
        'al-daayen' => [
            'ar' => 'الظعاين', 'in' => 'في الظعاين', 'prep' => 'بالظعاين',
            'areas' => 'لوسيل الشرقية وروضة الحمامة وأم العمد',
            'stock' => 'فلل جديدة وتوسعات سكنية',
            'note' => 'أعمال البناء المجاورة ترفع الغبار على الوحدات الخارجية والدكت',
            'access' => 'نؤكد الشارع والمركب قبل التحرك من الدوحة',
            'hub' => '/services-in-al-daayen-qatar/',
        ],
        'al-shamal' => [
            'ar' => 'الشمال', 'in' => 'في الشمال', 'prep' => 'بالشمال',
            'areas' => 'الرويس والشحانية الشمالية ومدن الساحل الشمالي',
            'stock' => 'بيوت ومبانٍ منخفضة وتعرّض رياح أقوى',
            'note' => 'المسافة أطول؛ الموعد يُكتب بعد العنوان لا كوعد فوري من الرسالة',
            'access' => 'الزيارة تُجدول ضمن يوم التغطية الشمالية',
            'hub' => '/services-in-al-shamal-qatar/',
        ],
        'al-shahaniya' => [
            'ar' => 'الشحانية', 'in' => 'في الشحانية', 'prep' => 'بالشحانية',
            'areas' => 'الشحانية والوجبة وغرب الريان',
            'stock' => 'فلل ومساحات مفتوحة وأحواش',
            'note' => 'الغبار والحرارة على الأسطح المكشوفة أوضح من وسط الدوحة',
            'access' => 'نحدد نقطة اللقاء إن كان البيت خارج الشارع الرئيسي',
            'hub' => '/services-in-al-shahaniya-qatar/',
        ],
    ];
}

function rukn_grid_city_key($slug) {
    foreach (array_keys(rukn_grid_cities()) as $k) {
        if ($slug === $k || substr($slug, -strlen($k) - 1) === '-' . $k) {
            return $k;
        }
    }
    return '';
}

function rukn_grid_kind($slug) {
    $s = (string) $slug;
    if (strpos($s, 'soundproof') !== false) {
        return 'sound';
    }
    if (preg_match('/leak|humidity|waterproof|pipe-leak/', $s)) {
        return 'leak';
    }
    if (preg_match('/insulat|lining|thermal|tank-insul/', $s)) {
        return 'insulate';
    }
    if (preg_match('/(^|-)(ac|freon|cooling|split-ac|window-ac|central-ac)/', $s) || strpos($s, 'ac-') !== false) {
        return 'ac';
    }
    if (preg_match('/pest|cockroach|termite|ant-|bed-bug|rodent|snake|scorpion|flea|lizard|mosquito|bird|pigeon|disinfect/', $s)) {
        return 'pest';
    }
    if (preg_match('/clean|polishing|chimney/', $s)) {
        return 'clean';
    }
    if (preg_match('/plumb|drain|septic|sanitary|heater|pump|pipe/', $s)) {
        return 'plumb';
    }
    if (preg_match('/electric|lighting|cctv|satellite|sat-dish|audio/', $s)) {
        return 'electric';
    }
    if (preg_match('/garden|grass|irrigation|palm|landscap|pergola|arbor|fountain|waterfall|pathway|seating/', $s)) {
        return 'garden';
    }
    if (preg_match('/paint|wallpaper|gypsum|decor|spray/', $s)) {
        return 'paint';
    }
    if (strpos($s, 'solar') !== false) {
        return 'solar';
    }
    if (preg_match('/inspect|renovation|crack/', $s)) {
        return 'renovate';
    }
    if (preg_match('/moving|storage|furniture|assembly|packaging/', $s)) {
        return 'move';
    }
    return 'general';
}

function rukn_grid_service_label($title, $city) {
    $t = (string) $title;
    foreach ([$city['prep'], $city['in'], $city['ar'], 'قطر'] as $w) {
        $t = str_replace($w, '', $t);
    }
    $t = trim(preg_replace('/\s+/u', ' ', $t), " —-|");
    return $t !== '' ? $t : $title;
}

function rukn_grid_kind_copy($kind, $label, $city, $v) {
    $in = $city['in'];
    $stock = $city['stock'];
    $map = [
        'leak' => [
            'do' => "نحدد مصدر الرطوبة أو التسرب {$in} بالأجهزة قبل أي تكسير. {$stock} تختلف فيها المسارات؛ برج غير فلة.",
            'when' => ['ارتفاع فاتورة كهرماء والمياه مقفلة', 'بقعة أو تقشير يعود بعد الدهان', 'صوت ماء في السقف أو الجدار', 'خزان يفقد منسوبه'],
            'avoid' => 'لا ندهن فوق البقعة ولا نفتح بلاطاً عشوائياً قبل التقرير.',
        ],
        'sound' => [
            'do' => "نعزل مسار الصوت لا اسم الخامة فقط. {$in} الجار أو الدكت أو الشارع يحدد الطبقة.",
            'when' => ['صوت وحدة مجاورة في برج', 'غرفة على شارع', 'صوت دكت في المجلس', 'مكتب منزلي يحتاج هدوءاً'],
            'avoid' => 'ألواح على جدار واحد دون فحص الباب والدكت لا تكفي.',
        ],
        'insulate' => [
            'do' => "نفحص الميل والصرف والخامة الحالية ثم نكتب طبقة العزل. الأسطح {$in} تتعرض لحرارة صيف عالية.",
            'when' => ['أول صيف على سطح جديد', 'تزهير أو بقع في السقف', 'غرف علوية حارة', 'خزان يغيّر لون الماء'],
            'avoid' => 'لا نعد بضمان عشر سنوات كشعار؛ المدة تُكتب في العرض.',
        ],
        'ac' => [
            'do' => "نفحص التبريد والصرف والوحدة الخارجية والدكت. الغبار {$in} يغيّر جدول الغسيل.",
            'when' => ['ضعف تبريد بعد الظهر', 'رائحة من الدكت', 'ماء تحت الوحدة', 'فاتورة كهرباء قفزت بعد صيف'],
            'avoid' => 'تعبئة فريون دون معرفة سبب النقص ليست حلاً.',
        ],
        'pest' => [
            'do' => "نحدد النوع والمسار ثم المادة المناسبة للسكن. {$stock} تغيّر نقاط الدخول.",
            'when' => ['أثر ليلي متكرر', 'وجود في المطبخ أو المجاري', 'بعد تخزين أو انتقال', 'شكوى جيران في نفس المبنى'],
            'avoid' => 'لا رش أعمى فوق طعام أطفال دون تحديد المادة.',
        ],
        'clean' => [
            'do' => "نحدد المساحة ونوع التشطيب وأولوية الغرف. {$in} الغبار أو الملح أو التشطيب الجديد يغيّر الأسلوب.",
            'when' => ['بعد انتقال أو تشطيب', 'قبل استقبال', 'رائحة أو عفن في المكيف', 'تراكم غبار على الزجاج'],
            'avoid' => 'لا نخلط مواداً على رخام أو خشب دون اختبار.',
        ],
        'plumb' => [
            'do' => "نفحص الضغط والصرف والسخان والمضخة قبل فك التشطيب. {$in} الخزان الأرضي شائع في الفلل.",
            'when' => ['ضعف ضغط', 'راجع صرف', 'سخان لا يسخن', 'تسرب ظاهر تحت حوض'],
            'avoid' => 'تغيير قطعة دون معرفة سبب الضغط المرتفع يعيد العطل.',
        ],
        'electric' => [
            'do' => "نفحص اللوحة والأحمال والقواطع قبل أي تمديد. حرارة {$in} ترفع الحمل على المكيف واللوحة.",
            'when' => ['قافلات تفصل', 'إنارة تضعف', 'سخونة في المفتاح', 'دائرة جديدة لمطبخ أو ملحق'],
            'avoid' => 'لا نعد بـ24 ساعة كشعار إن كان الوصول يحتاج جدولة.',
        ],
        'garden' => [
            'do' => "نعاين التربة والري والشمس والملوحة. {$in} العشب الصناعي والري يختلفان عن حديقة ظل.",
            'when' => ['عشب يحترق صيفاً', 'ري غير منتظم', 'ملحق خارجي جديد', 'غبار يغطي الأوراق'],
            'avoid' => 'عشب جداري بلا تصريف يفسد الواجهة.',
        ],
        'paint' => [
            'do' => "نفحص الرطوبة قبل الدهان. إن كانت البقعة من تسرب، نعالج المصدر أولاً.",
            'when' => ['تقشير بعد صيف', 'بعد كشف تسرب', 'واجهة باهتة', 'تشطيب فيلا جديدة'],
            'avoid' => 'دهان فوق رطوبة نشطة يعيد التقشير.',
        ],
        'solar' => [
            'do' => "نراجع الاستهلاك والتظليل وزاوية السطح {$in} قبل التوصية بالألواح أو السخان.",
            'when' => ['فاتورة كهرماء مرتفعة', 'سخان تقليدي ضعيف', 'سطح مكشوف مناسب', 'عقد صيانة بعد تركيب قديم'],
            'avoid' => 'لا نركّب على سطح بميل أو صرف غير محلول.',
        ],
        'renovate' => [
            'do' => "نفحص الشقوق والرطوبة والتمديدات قبل الترميم. فحص ما قبل الشراء {$in} يربط التسرب والعزل والتكييف.",
            'when' => ['قبل شراء فيلا', 'شقوق بعد صيف', 'حمام أو مطبخ تالف', 'منزل قديم يحتاج أولوية'],
            'avoid' => 'ترميم تجميلي فوق تسرب يخفي التكلفة الحقيقية.',
        ],
        'move' => [
            'do' => "نحدد الحجم والممرات والمصعد. {$in} الأبراج تختلف عن الفلل في التغليف والوقت.",
            'when' => ['انتقال بين شقتين', 'تخزين مؤقت', 'فك غرف كاملة', 'ضيق مصعد أو موقف'],
            'avoid' => 'لا ننقل بيانو أو شحناً دولياً ضمن هذه الصفحة.',
        ],
        'general' => [
            'do' => "المعاينة {$in} تحدد نطاق «{$label}» على {$stock} لا وصفاً عاماً من الرسالة.",
            'when' => ['عطل ظاهر', 'صيانة قبل الصيف', 'بعد تشطيب', 'توسعة أو ملحق جديد'],
            'avoid' => 'لا سعر نهائي عبر واتساب دون فهم الحالة.',
        ],
    ];
    $row = $map[$kind] ?? $map['general'];
    $when = $row['when'];
    $rot = $v % max(1, count($when));
    if ($rot) {
        $when = array_merge(array_slice($when, $rot), array_slice($when, 0, $rot));
    }
    $when[] = $city['access'];
    return [$row['do'], $when, $row['avoid']];
}

function rukn_grid_html($slug, $title, $city_key) {
    $cities = rukn_grid_cities();
    $city = $cities[$city_key];
    $label = rukn_grid_service_label($title, $city);
    $kind = rukn_grid_kind($slug);
    $v = abs(crc32($slug)) % 6;
    [$do, $when, $avoid] = rukn_grid_kind_copy($kind, $label, $city, $v);
    $wa = 'https://wa.me/' . RUKN_GRID_WA . '?text=' . rawurlencode('مرحباً، أريد الاستفسار عن: ' . $title);
    $intros = [
        "{$label} {$city['in']} تُنفَّذ بعد معاينة المكان لا بعد وصف جاهز. {$city['stock']} — لذلك نطاق العمل في {$city['areas']} يختلف من عنوان لآخر.",
        "في {$city['ar']} نتعامل مع {$label} انطلاقاً من {$city['note']}. الأحياء المعنية تشمل {$city['areas']}.",
        "طلب {$label} {$city['prep']} يبدأ برسالة واتساب فيها المنطقة والعطل. {$city['access']}",
    ];
    $intro = $intros[$v % 3];
    $methods = [
        'معاينة وتشخيص مكتوب، ثم عرض سعر قبل التنفيذ، ثم تسليم بعد مراجعتك.',
        'نحدد المصدر أو النطاق أولاً، نكتب ما سيُعمل وما لن يُعمل، ثم نبدأ.',
        'لا نخلط المعاينة بالتنفيذ: التقرير أولاً حتى لا يتغير السعر في منتصف العمل.',
    ];
    $lis = '';
    foreach ($when as $item) {
        $lis .= '<li>' . esc_html($item) . '</li>';
    }
    $faq = [
        ['هل تعملون ' . $city['in'] . ' فقط؟', 'المقر الدوحة والتغطية تشمل ' . $city['ar'] . ' وبقية المدن بالتنسيق. ' . $city['access']],
        ['هل يوجد رقم للاتصال؟', 'حالياً التواصل واتساب فقط. أزرار الاتصال مخفية حتى يتوفر رقم قطري جديد.'],
        ['هل السعر ثابت؟', 'لا. يُكتب بعد المعاينة أو وصف دقيق. الضمان إن وُجد يُذكر في العرض لا كشعار عام.'],
    ];
    if ($v % 2) {
        $faq[] = ['كم يستغرق الوصول؟', $city['note']];
    } else {
        $faq[] = ['هل الزيارة في نفس اليوم؟', 'بعد العنوان ونوع العطل نؤكد اليوم. ' . $city['access']];
    }
    $faq_html = '';
    foreach ($faq as $q) {
        $faq_html .= '<h2>' . esc_html($q[0]) . '</h2><p>' . esc_html($q[1]) . '</p>';
    }
    $pillar = '';
    if ($kind === 'leak') {
        $pillar = '<p>دليل الدولة لكشف التسربات: <a href="https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/">شركة كشف تسربات المياه في قطر</a>.</p>';
    } elseif ($kind === 'insulate') {
        $pillar = '<p>عزل الأسطح على مستوى قطر: <a href="https://www.rukn-eltatawer.com/qa/shrkh-azl-asth-fy-qtr/">عزل الأسطح</a>.</p>';
    } elseif ($kind === 'ac') {
        $pillar = '<p>صيانة التكييف: <a href="https://www.rukn-eltatawer.com/qa/central-air-conditioning-maintenance-in-qatar/">صيانة التكييف</a>.</p>';
    }
    $html = '<div class="rukn-article">';
    $html .= '<p>' . esc_html($intro) . '</p>';
    $html .= '<p>' . esc_html($do) . '</p>';
    $html .= '<p><a class="btn btn-wa" href="' . esc_url($wa) . '" rel="nofollow noopener" target="_blank">تواصل عبر واتساب</a></p>';
    $html .= '<h2>متى تطلب الخدمة ' . esc_html($city['in']) . '</h2><ul>' . $lis . '</ul>';
    $html .= '<h2>طريقة العمل</h2><p>' . esc_html($methods[$v % 3]) . ' ' . esc_html($avoid) . '</p>';
    $html .= '<h2>التغطية المحلية</h2><p>' . esc_html($city['areas']) . '. ' . esc_html($city['note']) . '</p>';
    $html .= '<p>صفحة المدينة: <a href="https://www.rukn-eltatawer.com/qa' . esc_attr($city['hub']) . '">خدمات ركن التطور ' . esc_html($city['in']) . '</a>.</p>';
    $html .= $pillar;
    $html .= $faq_html;
    $html .= '<p>التواصل واتساب. لا رقم قطري منشور حالياً.</p>';
    $html .= '</div>';
    return $html;
}

function rukn_grid_excerpt($title, $city) {
    return wp_strip_all_tags($title . ' ' . $city['in'] . ': معاينة ثم عرض مكتوب. التواصل واتساب.');
}

function rukn_grid_fast_publish($id, $content, $excerpt, $status = 'publish') {
    global $wpdb;
    $now = current_time('mysql');
    $now_gmt = current_time('mysql', 1);
    $wpdb->update(
        $wpdb->posts,
        [
            'post_content' => $content,
            'post_excerpt' => $excerpt,
            'post_status' => $status,
            'post_modified' => $now,
            'post_modified_gmt' => $now_gmt,
        ],
        ['ID' => (int) $id],
        ['%s', '%s', '%s', '%s', '%s'],
        ['%d']
    );
    clean_post_cache((int) $id);
}

function rukn_grid_fast_status($id, $status) {
    global $wpdb;
    $wpdb->update(
        $wpdb->posts,
        ['post_status' => $status],
        ['ID' => (int) $id],
        ['%s'],
        ['%d']
    );
    clean_post_cache((int) $id);
}

function rukn_grid_maybe_terms($id, $city_ar) {
    static $done = [];
    $id = (int) $id;
    if (isset($done[$id])) {
        return;
    }
    $done[$id] = true;
    if (function_exists('pll_set_post_language')) {
        $cur = function_exists('pll_get_post_language') ? pll_get_post_language($id) : '';
        if ($cur !== 'ar') {
            pll_set_post_language($id, 'ar');
        }
    }
    if (taxonomy_exists('cities')) {
        $existing = wp_get_object_terms($id, 'cities', ['fields' => 'names']);
        if (is_wp_error($existing) || !in_array($city_ar, (array) $existing, true)) {
            wp_set_object_terms($id, $city_ar, 'cities', false);
        }
    }
}

add_action('rest_api_init', function () {
    register_rest_route('rukn-qa/v1', '/city-grid', [
        'methods' => 'POST',
        'permission_callback' => function () {
            return current_user_can('manage_options');
        },
        'callback' => function ($req) {
            $offset = max(0, (int) $req->get_param('offset'));
            $limit = min(80, max(1, (int) $req->get_param('limit')));
            $after_id = max(0, (int) $req->get_param('after_id'));
            $mode = (string) $req->get_param('mode');
            $cities = rukn_grid_cities();
            $out = ['updated' => [], 'skipped' => [], 'created' => [], 'errors' => []];
            $GLOBALS['rukn_unlock_2973'] = true;
            wp_defer_term_counting(true);
            wp_defer_comment_counting(true);

            if ($mode === 'fill-missing') {
                global $wpdb;
                $rows = $wpdb->get_results($wpdb->prepare(
                    "SELECT ID, post_name, post_title FROM {$wpdb->posts} WHERE post_type='post' AND post_status='publish' AND post_name LIKE %s AND ID > %d ORDER BY ID ASC LIMIT %d",
                    '%-doha',
                    $after_id,
                    $limit
                ));
                $city_keys = array_keys($cities);
                foreach ($rows as $row) {
                    if (rukn_grid_skip_slug($row->post_name)) {
                        $out['skipped'][] = $row->post_name;
                        continue;
                    }
                    $base = preg_replace('/-doha$/', '', $row->post_name);
                    foreach ($city_keys as $ck) {
                        if ($ck === 'doha') {
                            continue;
                        }
                        $slug = $base . '-' . $ck;
                        $exists = $wpdb->get_var($wpdb->prepare(
                            "SELECT ID FROM {$wpdb->posts} WHERE post_name=%s AND post_type='post' LIMIT 1",
                            $slug
                        ));
                        if ($exists) {
                            continue;
                        }
                        $title = str_replace(
                            ['بالدوحة', 'في الدوحة', 'الدوحة'],
                            [$cities[$ck]['prep'], $cities[$ck]['in'], $cities[$ck]['ar']],
                            $row->post_title
                        );
                        $html = rukn_grid_html($slug, $title, $ck);
                        $excerpt = rukn_grid_excerpt($title, $cities[$ck]);
                        $id = wp_insert_post([
                            'post_title' => $title,
                            'post_name' => $slug,
                            'post_content' => $html,
                            'post_excerpt' => $excerpt,
                            'post_status' => 'publish',
                            'post_type' => 'post',
                        ], true);
                        if (is_wp_error($id)) {
                            $out['errors'][] = $slug . ' ' . $id->get_error_message();
                            continue;
                        }
                        rukn_grid_maybe_terms((int) $id, $cities[$ck]['ar']);
                        $out['created'][] = $slug;
                    }
                }
                wp_defer_term_counting(false);
                wp_defer_comment_counting(false);
                $out['last_id'] = $rows ? (int) $rows[count($rows) - 1]->ID : $after_id;
                $out['count'] = count($rows);
                return $out;
            }

            if ($mode === 'lusail') {
                global $wpdb;
                $rows = $wpdb->get_results($wpdb->prepare(
                    "SELECT ID, post_name, post_title, post_status FROM {$wpdb->posts} WHERE post_type='post' AND post_status IN ('draft','publish') AND post_name LIKE %s AND ID > %d ORDER BY ID ASC LIMIT %d",
                    '%-doha',
                    $after_id,
                    $limit
                ));
                foreach ($rows as $row) {
                    if (rukn_grid_skip_slug($row->post_name)) {
                        $out['skipped'][] = $row->post_name;
                        continue;
                    }
                    $lusail_slug = preg_replace('/-doha$/', '-lusail', $row->post_name);
                    $exists = $wpdb->get_var($wpdb->prepare(
                        "SELECT ID FROM {$wpdb->posts} WHERE post_name=%s AND post_type='post' LIMIT 1",
                        $lusail_slug
                    ));
                    $title = str_replace(['بالدوحة', 'في الدوحة', 'الدوحة'], ['بلوسيل', 'في لوسيل', 'لوسيل'], $row->post_title);
                    $html = rukn_grid_html($lusail_slug, $title, 'lusail');
                    $excerpt = rukn_grid_excerpt($title, $cities['lusail']);
                    if ($exists) {
                        rukn_grid_fast_publish((int) $exists, $html, $excerpt, 'publish');
                        $id = (int) $exists;
                        $out['updated'][] = $lusail_slug;
                    } else {
                        $id = wp_insert_post([
                            'post_title' => $title,
                            'post_name' => $lusail_slug,
                            'post_content' => $html,
                            'post_excerpt' => $excerpt,
                            'post_status' => 'publish',
                            'post_type' => 'post',
                        ], true);
                        if (is_wp_error($id)) {
                            $out['errors'][] = $lusail_slug . ' ' . $id->get_error_message();
                            continue;
                        }
                        $out['created'][] = $lusail_slug;
                    }
                    rukn_grid_maybe_terms((int) $id, 'لوسيل');
                }
                wp_defer_term_counting(false);
                wp_defer_comment_counting(false);
                $out['last_id'] = $rows ? (int) $rows[count($rows) - 1]->ID : $after_id;
                $out['count'] = count($rows);
                return $out;
            }

            global $wpdb;
            $id_clause = $after_id > 0 ? $wpdb->prepare(' AND ID > %d ', $after_id) : '';
            $rows = $wpdb->get_results($wpdb->prepare(
                "SELECT ID, post_name, post_title, post_status FROM {$wpdb->posts}
                 WHERE post_type='post' AND post_status IN ('draft','publish')
                 AND ID <> 2973
                 {$id_clause}
                 AND (
                    post_name LIKE %s OR post_name LIKE %s OR post_name LIKE %s OR post_name LIKE %s
                    OR post_name LIKE %s OR post_name LIKE %s OR post_name LIKE %s OR post_name LIKE %s
                    OR post_name LIKE %s
                 )
                 ORDER BY ID ASC LIMIT %d",
                '%-doha', '%-al-rayyan', '%-al-wakrah', '%-al-khor', '%-umm-salal',
                '%-al-daayen', '%-al-shamal', '%-al-shahaniya', '%-lusail',
                $limit
            ));
            foreach ($rows as $row) {
                $key = rukn_grid_city_key($row->post_name);
                if ($key === '' || empty($cities[$key])) {
                    $out['skipped'][] = $row->post_name;
                    continue;
                }
                if (rukn_grid_skip_slug($row->post_name)) {
                    if ($row->post_status === 'publish') {
                        rukn_grid_fast_status((int) $row->ID, 'draft');
                    }
                    $out['skipped'][] = $row->post_name;
                    continue;
                }
                $html = rukn_grid_html($row->post_name, $row->post_title, $key);
                $excerpt = rukn_grid_excerpt($row->post_title, $cities[$key]);
                rukn_grid_fast_publish((int) $row->ID, $html, $excerpt, 'publish');
                rukn_grid_maybe_terms((int) $row->ID, $cities[$key]['ar']);
                $out['updated'][] = $row->post_name;
            }
            wp_defer_term_counting(false);
            wp_defer_comment_counting(false);
            $out['offset'] = $offset;
            $out['count'] = count($rows);
            $out['last_id'] = $rows ? (int) $rows[count($rows) - 1]->ID : $after_id;
            return $out;
        },
    ]);
});
