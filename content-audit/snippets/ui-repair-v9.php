/**
 * Rukn Qatar UI repair v9
 * Keep UAE WhatsApp 971586634710. Hide all call buttons. Strip Qatar phone numbers.
 * v9: stop hiding Qatar flag/alt images; hide GCC country switcher leftovers; no Oman false-positive.
 */
if (!defined('ABSPATH')) {
    return;
}

const RUKN_QA_WA_KEEP = '971586634710';

add_filter('register_post_type_args', function ($args, $post_type) {
    if ($post_type === 'services') {
        $args['has_archive'] = false;
    }
    if (in_array($post_type, ['reviews', 'faqs', 'pricing', 'portfolio', 'before_after'], true)) {
        $args['has_archive'] = false;
    }
    return $args;
}, 100, 2);

function rukn_qa_repair_v8_patch_options() {
    $pll = get_option('polylang');
    if (is_array($pll)) {
        $pll['browser'] = 0;
        $pll['redirect_lang'] = 0;
        update_option('polylang', $pll);
    }
    $gen = get_option('rank-math-options-general');
    $gen_keys = [];
    if (is_array($gen)) {
        $gen_keys = array_keys($gen);
        $gen['redirections_fallback'] = 'default';
        $gen['redirect_404'] = '';
        $gen['404_redirection'] = '';
        if (isset($gen['fallback'])) {
            $gen['fallback'] = 'default';
        }
        if (isset($gen['redirections_post_redirect'])) {
            $gen['redirections_post_redirect'] = 'off';
        }
        update_option('rank-math-options-general', $gen);
    }
    $titles = get_option('rank-math-options-titles');
    if (is_array($titles)) {
        $titles['phone_numbers'] = [];
        $titles['twitter_author'] = '';
        $titles['facebook_author'] = '';
        $titles['social_url_twitter'] = '';
        $titles['twitter_use_author'] = 'off';
        if (isset($titles['social_url_facebook']) && strpos((string) $titles['social_url_facebook'], 'melsaadgroup') !== false) {
            $titles['social_url_facebook'] = '';
        }
        $titles['local_address'] = [
            'streetAddress' => 'الدوحة',
            'addressLocality' => 'الدوحة',
            'addressRegion' => 'الدوحة',
            'addressCountry' => 'QA',
            'postalCode' => '',
        ];
        $titles['opening_hours'] = [
            ['day' => 'Saturday', 'time' => '08:00-20:00'],
            ['day' => 'Sunday', 'time' => '08:00-20:00'],
            ['day' => 'Monday', 'time' => '08:00-20:00'],
            ['day' => 'Tuesday', 'time' => '08:00-20:00'],
            ['day' => 'Wednesday', 'time' => '08:00-20:00'],
            ['day' => 'Thursday', 'time' => '08:00-20:00'],
        ];
        update_option('rank-math-options-titles', $titles);
    }
    update_option('rukn_hide_call_global', '1');
    update_option('phonenumber', '');
    update_option('whatsapp_number', RUKN_QA_WA_KEEP);
    delete_option('rukn_hide_wa_global');
    if (function_exists('pll_set_post_language')) {
        $svc = get_posts(['post_type' => 'services', 'posts_per_page' => 50, 'post_status' => 'any', 'lang' => '']);
        foreach ($svc as $p) {
            $cur = function_exists('pll_get_post_language') ? pll_get_post_language($p->ID) : '';
            if (!$cur) {
                pll_set_post_language($p->ID, 'ar');
            }
        }
    }
    flush_rewrite_rules(true);
    if (function_exists('do_action')) {
        do_action('litespeed_purge_all');
    }
    update_option('rukn_qa_repair_v8', '1');
    return ['ok' => true, 'general_keys' => $gen_keys, 'pll_browser' => is_array($pll) ? $pll['browser'] : null];
}

add_action('init', function () {
    if (get_option('rukn_qa_repair_v8') === '1') {
        return;
    }
    rukn_qa_repair_v8_patch_options();
}, 30);

add_filter('pre_get_document_title', function ($title) {
    if (function_exists('is_singular') && is_singular('services')) {
        $t = get_the_title();
        return $t ? $t . ' | ركن التطور قطر' : $title;
    }
    return $title;
}, 99);
add_filter('rank_math/frontend/title', function ($title) {
    if (function_exists('is_singular') && is_singular('services')) {
        $t = get_the_title();
        return $t ? $t . ' | ركن التطور قطر' : $title;
    }
    return $title;
}, 99);

add_action('init', function () {
    add_rewrite_rule('^services/([^/]+)/?$', 'index.php?services=$matches[1]', 'top');
}, 21);

add_action('parse_request', function ($wp) {
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    $path = trim(preg_replace('#^/qa/#', '/', $path), '/');
    if (preg_match('#^services/([^/]+)$#', $path, $m)) {
        $wp->query_vars = [
            'post_type' => 'services',
            'name' => $m[1],
            'services' => $m[1],
            'lang' => 'ar',
        ];
    }
}, 99);

add_filter('request', function ($vars) {
    $name = '';
    if (!empty($vars['pagename']) && is_string($vars['pagename']) && strpos($vars['pagename'], 'services/') === 0) {
        $name = substr($vars['pagename'], strlen('services/'));
    } elseif (!empty($vars['name']) && !empty($vars['pagename']) && $vars['pagename'] === 'services') {
        $name = (string) $vars['name'];
    }
    $name = trim((string) $name, '/');
    if ($name !== '' && strpos($name, '/') === false) {
        $found = get_posts([
            'name' => $name,
            'post_type' => 'services',
            'post_status' => 'publish',
            'posts_per_page' => 1,
            'suppress_filters' => true,
        ]);
        if ($found) {
            return [
                'post_type' => 'services',
                'name' => $name,
                'services' => $name,
            ];
        }
    }
    return $vars;
}, 1);

add_action('template_redirect', function () {
    if (!is_404()) {
        return;
    }
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    $path = trim(preg_replace('#^/qa/#', '/', $path), '/');
    if (preg_match('#^services/([^/]+)$#', $path, $m)) {
        $found = get_posts([
            'name' => $m[1],
            'post_type' => 'services',
            'post_status' => 'publish',
            'posts_per_page' => 1,
            'suppress_filters' => true,
        ]);
        if ($found) {
            global $wp_query, $post;
            $post = $found[0];
            setup_postdata($post);
            $wp_query->queried_object = $post;
            $wp_query->queried_object_id = (int) $post->ID;
            $wp_query->posts = [$post];
            $wp_query->post = $post;
            $wp_query->post_count = 1;
            $wp_query->found_posts = 1;
            $wp_query->max_num_pages = 1;
            $wp_query->is_404 = false;
            $wp_query->is_single = true;
            $wp_query->is_singular = true;
            $wp_query->is_page = false;
            $wp_query->is_home = false;
            $wp_query->is_archive = false;
            $GLOBALS['wp_the_query'] = $wp_query;
            status_header(200);
            return;
        }
    }
    status_header(404);
    nocache_headers();
    $wa = 'https://wa.me/' . RUKN_QA_WA_KEEP;
    get_header();
    echo '<main id="content" class="rukn-404" style="max-width:720px;margin:40px auto;padding:24px;text-align:center">';
    echo '<h1>الصفحة غير موجودة</h1>';
    echo '<p>هذا الرابط غير موجود على موقع ركن التطور في قطر. يمكنك العودة للرئيسية أو مراسلتنا على واتساب.</p>';
    echo '<p><a href="' . esc_url(home_url('/')) . '">الرئيسية</a> · <a href="' . esc_url($wa) . '" rel="nofollow noopener" target="_blank">واتساب</a></p>';
    echo '</main>';
    get_footer();
    exit;
}, 0);

add_action('wp_body_open', function () {
    echo '<a class="rukn-skip-link" href="#content" style="position:absolute;left:-999px;top:0">تخطي إلى المحتوى</a>';
}, 1);

add_action('wp_head', function () {
    echo '<link rel="alternate" href="https://www.rukn-eltatawer.com/qa/" hreflang="x-default" />' . "\n";
    echo '<style id="rukn-repair-v9">'
        . '.fab-call,a.fab-btn.fab-call,a[href^="tel:"],.--button-call-link-phone,.-callbutton--post-card,.post-card-buttons.-callbutton--post-card,[data-call="Phone"],.btn-call,.kayan-call-btn,#ruknFab .fab-call{display:none!important;visibility:hidden!important;pointer-events:none!important}'
        . '.--rating--widgets--stars-averageList,.ratingServise--stars-value,.-Js-Rate-AverageItems,.-rating-value,.stars-averageList{display:none!important}'
        . '.-YC-WidgetType-contact__form,form.contact__form,form[action="#"]:not(.search-form):not([role="search"]){display:none!important}'
        . '.gcc-flags,.country-flags,img[alt*="UAE"],img[alt*="United Arab Emirates"]{display:none!important}'
        . '.ksw-country-btn[data-country="ae"],.ksw-country-btn[data-country="sa"],.ksw-country-btn[data-country="kw"],.ksw-country-btn[data-country="om"],.ksw-country-btn[data-country="bh"],.ksw-country-btn[data-country="eg"]{display:none!important}'
        . '.kayan-switcher-wrap .ksw-countries,.kayan-switcher-wrap .ksw-divider,.kayan-switcher-wrap .ksw-section:first-child{display:none!important}'
        . '</style>';
}, 99);

add_action('template_redirect', function () {
    if (is_admin() || (function_exists('wp_doing_ajax') && wp_doing_ajax()) || (function_exists('wp_is_json_request') && wp_is_json_request())) {
        return;
    }
    ob_start('rukn_qa_repair_v8_html');
}, 9);

function rukn_qa_repair_v8_html($html) {
    if (!is_string($html) || $html === '') {
        return $html;
    }

    $html = str_replace(
        ['31553076', '31110184', '3111 0184', '3155 3076', '+974 3111 0184', '+97431110184', '97431110184', '+97431553076', '97431553076'],
        '',
        $html
    );
    $html = str_replace(
        [
            'اتصل أو أرسل واتساب على  974+ ونرد عليك لتحديد الموعد.',
            'اتصل أو أرسل واتساب على 974+ ونرد عليك لتحديد الموعد.',
            'اتصل أو أرسل WhatsApp على 974+ ونرد عليك لتحديد الموعد.',
        ],
        'أرسل واتساب ونرد عليك لتحديد الموعد.',
        $html
    );
    $html = preg_replace('/(?<!\d)(?:\+974|974\+)(?!\d)/', '', $html);

    $html = preg_replace('#href="tel:[^"]*"#i', 'href="javascript:void(0)" class="kayan-call-btn"', $html);
    $html = str_replace('"call_show":true', '"call_show":false', $html);
    $html = str_replace('"call_number":"+97431110184"', '"call_number":""', $html);
    $html = str_replace('a[href="#"],a[href="#"]', 'a[href^="tel:"]', $html);

    $html = str_replace(
        ['[[عدد المشاريع]]', '[[سنة التأسيس]]', '[[projects]]', '[[founded]]', '[[عدد Projects]]', '[[سنة Founded]]'],
        ['9', 'الدوحة', '9', 'Doha', '9', 'Doha'],
        $html
    );
    $html = str_replace('<div class="num" data-count="20">0</div>', '<div class="num" data-count="20">20</div>', $html);
    $html = str_replace('<div class="num" data-count="8">0</div>', '<div class="num" data-count="9">9</div>', $html);
    $html = str_replace('<b data-count="20">0</b>', '<b data-count="20">20</b>', $html);
    $html = str_replace('<b data-count="8">0</b>', '<b data-count="9">9</b>', $html);
    $html = str_replace('<small>مدن تغطية</small>', '<small>مدن نغطيها</small>', $html);
    $html = str_replace('<div class="lbl">مشروع منفّذ</div>', '<div class="lbl">مدن نغطيها</div>', $html);
    $html = str_replace('<div class="lbl">في قطر منذ</div>', '<div class="lbl">المقر</div>', $html);
    $html = str_replace('>completed projects<', '>cities covered<', $html);
    $html = str_replace('>in Qatar since<', '>based in<', $html);

    $html = str_replace(
        '<option value="الشحانية">الشحانية</option></select>',
        '<option value="الشحانية">الشحانية</option><option value="الشمال">الشمال</option><option value="الظعاين">الظعاين</option></select>',
        $html
    );
    $html = str_replace(
        '"الشحانية":"يُحدَّد عند التواصل"}',
        '"الشحانية":"يُحدَّد عند التواصل","الشمال":"يُحدَّد عند التواصل","الظعاين":"يُحدَّد عند التواصل"}',
        $html
    );
    $html = str_replace(
        '"الشحانية":"يُحدَّد عند التواصل"}',
        '"الشحانية":"يُحدَّد عند التواصل","الشمال":"يُحدَّد عند التواصل","الظعاين":"يُحدَّد عند التواصل"}',
        $html
    );

    $html = preg_replace('#<a[^>]*>\s*KAYAN WEB\s*</a>#i', '', $html);
    $html = str_replace('شركة كيان ويب للتسويق الإلكتروني', 'ركن التطور قطر', $html);
    $html = str_replace('السلام عليكم - شركة كيان ويب للتسويق الإلكتروني', 'مرحباً، أريد الاستفسار عن خدمات ركن التطور في قطر', $html);
    $html = str_replace('KAYAN WEB WhatsApp', 'WhatsApp', $html);
    $html = str_replace('🇦🇪', '🇶🇦', $html);
    $html = str_replace(['🇸🇦', '🇧🇭', '🇰🇼', '🇴🇲', '🇪🇬'], '', $html);
    $html = str_replace('إمارات قطر', 'مدن قطر', $html);
    $html = str_replace('مختلف إمارات قطر', 'مدن قطر', $html);
    $html = str_replace(' — عجمان', ' — أم صلال', $html);
    $html = str_replace('عجمان —', 'أم صلال —', $html);
    $html = str_replace(' في عجمان', ' في أم صلال', $html);
    $html = str_replace('img[alt*="UAE"],img[alt*="قطر"]', 'img[alt*="UAE"]', $html);
    $html = str_replace('img[alt*="UAE"],img[alt*="Qatar"]', 'img[alt*="UAE"]', $html);
    $html = str_replace('var country="ae";', 'var country="qa";', $html);
    $html = str_replace('aria-label="تبديل الدولة واللغة"', 'aria-label="تبديل اللغة"', $html);
    $html = str_replace('title="تبديل الدولة واللغة"', 'title="تبديل اللغة"', $html);
    $html = str_replace('class="uae-svg"', 'class="qa-map-svg uae-svg"', $html);
    $html = str_replace('>تغطية 8 مدن<', '>تغطية 9 مدن<', $html);
    $html = str_replace('<div class="cc val rk">8 مدن</div>', '<div class="cc val rk">9 مدن</div>', $html);
    $html = str_replace('> 8 مدن<', '> 9 مدن<', $html);
    $html = str_replace(
        'مقرنا الدوحة، ونغطي الريان ولوسيل وأم صلال والوكرة والخور والخيسة والشحانية.',
        'مقرنا الدوحة، ونغطي الريان ولوسيل وأم صلال والوكرة والخور والخيسة والشحانية والشمال والظعاين.',
        $html
    );
    $html = str_replace(
        'href="https://www.rukn-eltatawer.com/qa/contact-us/" title="صيانة تكييف"',
        'href="https://www.rukn-eltatawer.com/qa/central-air-conditioning-maintenance-in-qatar/" title="صيانة تكييف"',
        $html
    );
    $html = str_replace(
        'href="https://www.rukn-eltatawer.com/qa/contact-us/" title="سباكة وتسليك"',
        'href="https://www.rukn-eltatawer.com/qa/plumbing-maintenance-in-qatar/" title="سباكة وتسليك"',
        $html
    );
    $html = preg_replace('#<li>✅\s*<strong>رقم الهاتف:\s*974</strong>\s*\|\s*<strong>واتساب:\s*974</strong></li>#u', '', $html);
    $html = preg_replace('#📞\s*اتصل:\s+\|\s*💬\s*واتساب:#u', '💬 واتساب:', $html);

    $html = str_replace('خبرة أكثر من 15 عام', 'فريق يعرف مباني ومناخ قطر', $html);
    $html = str_replace('معتمدون من الجهات المختصة', 'تشخيص قبل التنفيذ', $html);
    $html = str_replace('ضمان مكتوب يصل إلى 10 سنوات', 'الضمان يُكتب في عرض السعر', $html);
    $html = str_replace('ضمان مكتوب حتى 10 سنوات', 'الضمان يُكتب في عرض السعر', $html);
    $html = str_replace('ضمان 10 سنوات مكتوب', 'ضمان مكتوب حسب الخدمة', $html);
    $html = str_replace('ضمان 10 سنوات', 'ضمان مكتوب حسب الخدمة', $html);
    $html = str_replace('4.9/5 (1,247+ تقييم Google)', 'تقييم بعد التسليم', $html);
    $html = str_replace('15,000+ عميل راضٍ', 'فريق مقيم في الدوحة', $html);
    $html = str_replace('12+ سنة خبرة', 'خبرة في مباني قطر', $html);
    $html = str_replace('معاينة مجانية', 'معاينة قبل العرض المكتوب', $html);
    $html = str_replace('Call buttons are hidden for now.', 'Send the area and the fault on WhatsApp.', $html);
    $html = str_replace('زر الاتصال الهاتفي مخفي مؤقتاً.', 'التواصل حالياً عبر واتساب.', $html);
    $html = str_replace('Questions asked', 'FAQ', $html);
    $html = str_replace('Guide home services', 'Home services guide', $html);
    $html = str_replace('in Qatar in Qatar', 'in Qatar', $html);

    $html = str_replace('"streetAddress": "Rayan"', '"streetAddress": "Doha"', $html);
    $html = str_replace('"openingHours": "24"', '"openingHours": "Sa-Th 08:00-20:00"', $html);
    $html = str_replace('https://www.facebook.com/melsaadgroup/', 'https://www.rukn-eltatawer.com/qa/', $html);
    $html = str_replace('https://www.facebook.com/melsaadgroup', 'https://www.rukn-eltatawer.com/qa/', $html);
    $html = str_replace('https://twitter.com/RuknEltatwer', 'https://www.rukn-eltatawer.com/qa/', $html);
    $html = str_replace('content="@RuknEltatwer"', 'content=""', $html);
    $html = preg_replace('#<a[^>]*class="[^"]*fab-call[^"]*"[^>]*>.*?</a>#is', '', $html);
    $html = str_replace('"query-input": "required name=s"', '"query-input": "required name=search_term_string"', $html);
    $html = str_replace('?s={s}', '?s={search_term_string}', $html);

    $html = preg_replace_callback('#<title>(.*?)</title>#is', function ($m) {
        $t = html_entity_decode($m[1], ENT_QUOTES | ENT_HTML5, 'UTF-8');
        $t = str_replace(['31553076', '31110184', '🔍', '💧', '🗺️'], '', $t);
        $t = preg_replace('/\s+/u', ' ', $t);
        $t = trim($t, " |-\t\n\r");
        return '<title>' . esc_html($t) . '</title>';
    }, $html, 1);

    $html = str_replace('الخدمات Archive', 'خدمات ركن التطور', $html);
    $html = preg_replace('#<h1>\s*services\s*</h1>#i', '<h1>خدمات ركن التطور في قطر</h1>', $html);

    $wa = RUKN_QA_WA_KEEP;
    $html = preg_replace('#https://(?:wa\.me|api\.whatsapp\.com/send\?phone=)/?\+?(?:97431110184|97431553076|' . $wa . ')#', 'https://wa.me/' . $wa, $html);

    return $html;
}

add_action('rest_api_init', function () {
    register_rest_route('rukn-qa/v1', '/repair-run', [
        'methods' => 'POST',
        'permission_callback' => function () {
            return current_user_can('manage_options');
        },
        'callback' => function () {
            delete_option('rukn_qa_repair_v8');
            $out = rukn_qa_repair_v8_patch_options();
            if (function_exists('do_action')) {
                do_action('litespeed_purge_all');
                foreach ([
                    home_url('/'),
                    home_url('/services/'),
                    home_url('/services/landscaping/'),
                    home_url('/services/sound-insulation-installation/'),
                    home_url('/about/'),
                    home_url('/contact-us/'),
                    home_url('/faq/'),
                    home_url('/en/'),
                ] as $u) {
                    do_action('litespeed_purge_url', $u);
                }
            }
            if (class_exists('LiteSpeed\\Purge')) {
                \LiteSpeed\Purge::purge_all();
            }
            return $out;
        },
    ]);
    register_rest_route('rukn-qa/v1', '/url-resolve', [
        'methods' => 'GET',
        'permission_callback' => function () {
            return current_user_can('manage_options');
        },
        'callback' => function ($req) {
            $slug = (string) $req->get_param('slug');
            if ($slug === '') {
                $slug = 'landscaping';
            }
            $rules = [];
            global $wp_rewrite;
            if (isset($wp_rewrite->wp_rewrite_rules) || method_exists($wp_rewrite, 'wp_rewrite_rules')) {
                foreach ((array) $wp_rewrite->wp_rewrite_rules() as $pat => $dest) {
                    if (strpos($pat, 'service') !== false || strpos($dest, 'service') !== false) {
                        $rules[$pat] = $dest;
                    }
                }
            }
            $found = get_posts([
                'name' => $slug,
                'post_type' => 'services',
                'post_status' => 'publish',
                'posts_per_page' => 1,
                'lang' => '',
            ]);
            $lang = function_exists('pll_get_post_language') && $found ? pll_get_post_language($found[0]->ID) : null;
            return [
                'url_to_postid' => url_to_postid(home_url('/services/' . $slug . '/')),
                'found_id' => $found ? $found[0]->ID : 0,
                'found_title' => $found ? $found[0]->post_title : '',
                'pll_lang' => $lang,
                'rules' => $rules,
                'post_types' => get_post_types(['public' => true]),
            ];
        },
    ]);
});
