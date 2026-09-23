/**
 * Rukn Qatar UI repair v10
 * Keep UAE WhatsApp 971586634710. Hide all call buttons. Strip Qatar phone numbers.
 * v9: stop hiding Qatar flag/alt images; hide GCC country switcher leftovers; no Oman false-positive.
 * v10: inject header/mobile nav from design; footer copy/logo/social; 404 err-wrap;
 *      hub href=#; strip dead forms/ratings; fill DNI; Qatar about/contact/faq chrome.
 */
if (!defined('ABSPATH')) {
    return;
}

const RUKN_QA_WA_KEEP = '971586634710';

function rukn_qa_is_en_html($html) {
    if (!is_string($html) || $html === '') {
        return false;
    }
    if (strpos($html, 'kayan-lang-en') !== false) {
        return true;
    }
    if (preg_match('/<html[^>]*\blang="en"/i', $html)) {
        return true;
    }
    return false;
}

function rukn_qa_preg_replace($pattern, $replacement, $html, $limit = -1) {
    if (!is_string($html) || $html === '') {
        return $html;
    }
    $out = preg_replace($pattern, $replacement, $html, $limit);
    return is_string($out) ? $out : $html;
}

function rukn_qa_nav_links($en = false) {
    if ($en) {
        $items = [
            ['Home', home_url('/en/')],
            ['Leak detection', home_url('/en/water-leak-detection-qatar-en/')],
            ['Roof insulation', home_url('/en/roof-insulation-qatar-en/')],
            ['AC maintenance', home_url('/en/ac-maintenance-qatar-en/')],
            ['Contact', home_url('/contact-us-2/')],
        ];
    } else {
        $items = [
            ['الرئيسية', home_url('/')],
            ['الخدمات', home_url('/services/')],
            ['المدن', home_url('/cities/')],
            ['الأسعار', home_url('/as3ar/')],
            ['من نحن', home_url('/about/')],
            ['المدونة', home_url('/blog/')],
            ['اتصل بنا', home_url('/contact-us/')],
        ];
    }
    $out = '';
    foreach ($items as $it) {
        $out .= '<a href="' . esc_url($it[1]) . '">' . esc_html($it[0]) . '</a>';
    }
    return $out;
}

function rukn_qa_mob_links($en = false) {
    if ($en) {
        $items = [
            ['Home', home_url('/en/')],
            ['Leak detection', home_url('/en/water-leak-detection-qatar-en/')],
            ['Roof insulation', home_url('/en/roof-insulation-qatar-en/')],
            ['AC maintenance', home_url('/en/ac-maintenance-qatar-en/')],
            ['About', home_url('/about/')],
            ['Contact', home_url('/contact-us-2/')],
        ];
    } else {
        $items = [
            ['الرئيسية', home_url('/')],
            ['الخدمات', home_url('/services/')],
            ['المدن', home_url('/cities/')],
            ['الأسعار', home_url('/as3ar/')],
            ['من نحن', home_url('/about/')],
            ['المدونة', home_url('/blog/')],
            ['الأسئلة الشائعة', home_url('/faq/')],
            ['اتصل بنا', home_url('/contact-us/')],
        ];
    }
    $out = '';
    foreach ($items as $it) {
        $out .= '<a href="' . esc_url($it[1]) . '" onclick="ruknToggleMob(false)">' . esc_html($it[0]) . '</a>';
    }
    return $out;
}

function rukn_qa_render_404_page() {
    $home = esc_url(home_url('/'));
    $logo = esc_url(home_url('/wp-content/uploads/2025/11/qa-logo.webp'));
    $theme = esc_url(get_template_directory_uri());
    $nav = rukn_qa_nav_links(false);
    $mob = rukn_qa_mob_links(false);
    $services = esc_url(home_url('/services/'));
    $cities = esc_url(home_url('/cities/'));
    $blog = esc_url(home_url('/blog/'));
    $contact = esc_url(home_url('/contact-us/'));
    $faq = esc_url(home_url('/faq/'));
    $wa_e = esc_url('https://wa.me/' . RUKN_QA_WA_KEEP);
    header('Content-Type: text/html; charset=UTF-8');
    echo '<!DOCTYPE html><html lang="ar" dir="rtl"><head>';
    echo '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">';
    echo '<title>الصفحة غير موجودة (404) | ركن التطور قطر</title>';
    echo '<link rel="preconnect" href="https://fonts.googleapis.com">';
    echo '<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&amp;family=Tajawal:wght@400;500;700;800;900&amp;display=swap" rel="stylesheet">';
    echo '<link rel="stylesheet" href="' . $theme . '/components/styles/FontAwesome/css/all.min.css">';
    echo '<link rel="stylesheet" href="' . $theme . '/style.css">';
    echo '<style id="rukn-404-v10">:root{--navy:#0A1F4E;--aqua:#5BB4EA;--turq:#1A8CDE;--grad:linear-gradient(135deg,#00205B 0%,#004B93 38%,#0066B8 68%,#5BB4EA 100%)}';
    echo 'body{margin:0;font-family:Tajawal,sans-serif;background:#f4f7fb}';
    echo 'header#hdr{position:sticky;top:0;z-index:50;background:#fff;box-shadow:0 8px 24px rgba(10,31,78,.08)}';
    echo 'header#hdr .nav{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:12px 20px;max-width:1200px;margin:0 auto}';
    echo 'header#hdr .logo img{height:42px;width:auto}';
    echo 'header#hdr nav.menu{display:flex;flex-wrap:wrap;gap:8px 16px}';
    echo 'header#hdr nav.menu a{color:#0A1F4E;text-decoration:none;font-weight:700;font-family:Cairo,sans-serif}';
    echo '.nav-cta{display:flex;align-items:center;gap:10px}';
    echo '.btn-wa{display:inline-flex;align-items:center;gap:8px;background:#18c96a;color:#fff!important;text-decoration:none;padding:10px 16px;border-radius:12px;font-weight:700}';
    echo '.err-wrap{min-height:70vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:120px 20px 80px;background:var(--grad);position:relative}';
    echo '.err-num{font-family:Cairo,sans-serif;font-weight:900;font-size:clamp(90px,16vw,180px);line-height:1;background:linear-gradient(120deg,#fff,var(--aqua));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}';
    echo '.err-wrap h2{color:#fff;margin:10px 0 14px;font-family:Cairo,sans-serif}';
    echo '.err-wrap p{color:rgba(255,255,255,.82);max-width:520px;margin:0 auto 30px}';
    echo '.err-actions{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-bottom:22px}';
    echo '.btn-quote{display:inline-flex;align-items:center;gap:8px;background:#fff;color:#0A1F4E;text-decoration:none;padding:12px 18px;border-radius:12px;font-weight:800}';
    echo '.err-links{display:flex;flex-wrap:wrap;gap:14px;justify-content:center}';
    echo '.err-links a{color:#fff;text-decoration:none;opacity:.9}';
    echo 'footer{background:#00205B;color:#d7e6f7;padding:36px 20px}';
    echo 'footer .wrap{max-width:1200px;margin:0 auto}';
    echo 'footer a{color:#fff}';
    echo '.fab-call,a[href^="tel:"],.btn-call{display:none!important}';
    echo '@media(max-width:900px){header#hdr nav.menu{display:none}.ham{display:inline-flex}}';
    echo '.ham{display:none;flex-direction:column;gap:4px;background:transparent;border:0;cursor:pointer}';
    echo '.ham span{display:block;width:20px;height:2px;background:#0A1F4E}';
    echo '.mob{display:none;position:fixed;inset:0;background:#fff;z-index:80;padding:24px;flex-direction:column;gap:14px}';
    echo '.mob.open{display:flex}.mob a{color:#0A1F4E;text-decoration:none;font-weight:700;padding:8px 0}';
    echo '</style></head><body class="kayan-lang-ar">';
    echo '<header id="hdr"><div class="wrap nav">';
    echo '<a href="' . $home . '" class="logo has-logo-image"><img src="' . $logo . '" alt="ركن التطور" height="42"></a>';
    echo '<nav class="menu">' . $nav . '</nav>';
    echo '<div class="nav-cta"><a class="btn-wa" href="' . $wa_e . '" rel="nofollow noopener" target="_blank"><i class="fab fa-whatsapp"></i> واتساب</a>';
    echo '<button type="button" class="ham icon-btn" onclick="ruknToggleMob(true)" aria-label="القائمة"><span></span><span></span><span></span></button></div></div></header>';
    echo '<div class="mob" id="ruknMob"><button type="button" class="mob-close" onclick="ruknToggleMob(false)" aria-label="إغلاق">×</button>' . $mob;
    echo '<a class="btn-wa" href="' . $wa_e . '" rel="nofollow noopener" target="_blank">تواصل عبر واتساب</a></div>';
    echo '<section class="err-wrap"><div class="wrap"><div class="err-num">404</div>';
    echo '<h2>عذراً، هذه الصفحة غير موجودة</h2>';
    echo '<p>هذا الرابط غير موجود على موقع ركن التطور في قطر. يمكنك العودة للرئيسية أو مراسلتنا على واتساب.</p>';
    echo '<div class="err-actions"><a class="btn-quote" href="' . $home . '"><i class="fas fa-house"></i> العودة للرئيسية</a>';
    echo '<a class="btn-wa" href="' . $wa_e . '" rel="nofollow noopener" target="_blank"><i class="fab fa-whatsapp"></i> تحدث معنا</a></div>';
    echo '<div class="err-links"><a href="' . $services . '">جميع الخدمات</a><a href="' . $cities . '">المدن</a><a href="' . $blog . '">المدونة</a><a href="' . $contact . '">اتصل بنا</a><a href="' . $faq . '">الأسئلة الشائعة</a></div>';
    echo '</div></section>';
    echo '<footer><div class="wrap"><p>ركن التطور — خدمات منزلية من الدوحة. التشخيص قبل الإصلاح وعرض سعر مكتوب.</p>';
    echo '<p><a href="' . $wa_e . '" rel="nofollow noopener" target="_blank">واتساب</a> · الدوحة، قطر</p></div></footer>';
    echo '<script>window.ruknToggleMob=function(open){var m=document.getElementById("ruknMob");if(!m)return;if(typeof open==="undefined"){m.classList.toggle("open")}else{m.classList.toggle("open",!!open);};};</script>';
    echo '</body></html>';
}


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
    update_option('wa_number', RUKN_QA_WA_KEEP);
    update_option('dni_wa_number', RUKN_QA_WA_KEEP);
    update_option('dni_phone', '');
    update_option('kayan_dni_wa', RUKN_QA_WA_KEEP);
    update_option('kayan_dni_phone', '');
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
    update_option('rukn_qa_repair_v10', '1');
    update_option('rukn_qa_repair_v8', '1');
    return ['ok' => true, 'general_keys' => $gen_keys, 'pll_browser' => is_array($pll) ? $pll['browser'] : null];
}

add_action('init', function () {
    if (get_option('rukn_qa_repair_v10') === '1') {
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
    rukn_qa_render_404_page();
    exit;
}, 0);

add_action('wp_body_open', function () {
    echo '<a class="rukn-skip-link" href="#content" style="position:absolute;left:-999px;top:0">تخطي إلى المحتوى</a>';
}, 1);

add_action('wp_head', function () {
    echo '<link rel="alternate" href="https://www.rukn-eltatawer.com/qa/" hreflang="x-default" />' . "\n";
    echo '<style id="rukn-repair-v10">'
        . '.fab-call,a.fab-btn.fab-call,a[href^="tel:"],.--button-call-link-phone,.-callbutton--post-card,.post-card-buttons.-callbutton--post-card,[data-call="Phone"],.btn-call,.kayan-call-btn,#ruknFab .fab-call{display:none!important;visibility:hidden!important;pointer-events:none!important}'
        . '.--rating--widgets--stars-averageList,.ratingServise--stars-value,.-Js-Rate-AverageItems,.-rating-value,.stars-averageList{display:none!important}'
        . 'form[action="#"]:not(.search-form):not([role="search"]){display:none!important}'
        . '.gcc-flags,.country-flags,img[alt*="UAE"],img[alt*="United Arab Emirates"]{display:none!important}'
        . '.ksw-country-btn[data-country="ae"],.ksw-country-btn[data-country="sa"],.ksw-country-btn[data-country="kw"],.ksw-country-btn[data-country="om"],.ksw-country-btn[data-country="bh"],.ksw-country-btn[data-country="eg"]{display:none!important}'
        . '.kayan-switcher-wrap .ksw-countries,.kayan-switcher-wrap .ksw-divider,.kayan-switcher-wrap .ksw-section:first-child{display:none!important}'
        . 'header#hdr nav.menu{display:flex;align-items:center;flex-wrap:wrap;gap:6px 18px}'
        . 'header#hdr nav.menu a{color:inherit;text-decoration:none;font-weight:700;font-family:Cairo,sans-serif;white-space:nowrap}'
        . '.qa-map-svg{width:100%;max-width:340px}'
        . '.article-body .about-grid{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin:12px 0 28px}'
        . '.article-body .abcard{background:#fff;border:1px solid var(--border,#e6edf5);border-radius:28px;padding:28px}'
        . '.article-body .timeline-h{max-width:760px;margin:0 auto;display:grid}'
        . '.article-body .faq-item{background:#fff;border:1px solid var(--border,#e6edf5);border-radius:20px;margin-bottom:14px;overflow:hidden}'
        . '.article-body .faq-q{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:18px 22px;cursor:pointer;font-weight:700}'
        . '.article-body .faq-a{display:none;padding:0 22px 18px;color:#4a5b73}'
        . '.article-body .faq-item.faq-open .faq-a{display:block}'
        . '</style>';
    echo '<script>document.addEventListener("click",function(e){var q=e.target.closest&&e.target.closest(".faq-q");if(!q)return;var i=q.closest(".faq-item");if(i)i.classList.toggle("faq-open");});</script>';
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

    $html = rukn_qa_repair_v10_html($html);

    return $html;
}

function rukn_qa_repair_v10_html($html) {
    if (!is_string($html) || $html === '') {
        return $html;
    }
    $en = rukn_qa_is_en_html($html);
    $nav = rukn_qa_nav_links($en);
    $html = rukn_qa_preg_replace('#<nav class="menu">\s*</nav>#', '<nav class="menu">' . $nav . '</nav>', $html, 1);

    if (strpos($html, 'id="ruknMob"') !== false && strpos($html, 'rukn-v10-nav') === false) {
        $mob = '<nav class="rukn-v10-nav">' . rukn_qa_mob_links($en) . '</nav>';
        $html = rukn_qa_preg_replace(
            '#(<div class="mob" id="ruknMob">)(.*?)(<a href="https://wa\.me/' . RUKN_QA_WA_KEEP . '")#s',
            '$1$2' . $mob . '$3',
            $html,
            1
        );
    }

    $html = str_replace('qa-logo-foter.webp', 'qa-logo.webp', $html);
    $html = str_replace('class="uae-svg"', 'class="qa-map-svg"', $html);
    $html = str_replace('.uae-svg{', '.qa-map-svg{', $html);
    $html = str_replace('.uae-svg path{', '.qa-map-svg path{', $html);

    $html = str_replace(
        'ركن التطور الرائدة في تقديم كل الخدمات المنزلية، كشف تسربات المياه💧🕵️‍♂️عزل الأسطح🏠المسابح🏊‍♂️ التشطيبات🧱الديكورات🎨صيانة عامة🛠️السباكة🚿الكهرباء💡الأجهزة الكهربائية🔌تنسيق الحدائق🌴التنظيف🧼مكافحة الحشرات🐜وكل ما تحتاجه لراحة منزلك أو منشأتك.',
        'ركن التطور — خدمات منزلية من الدوحة: كشف تسربات المياه، عزل الأسطح، التكييف، السباكة، التنظيف ومكافحة الحشرات. تشخيص قبل الإصلاح وعرض سعر مكتوب.',
        $html
    );
    $html = str_replace(
        'Rukn Eltatawer a leader in providing all Services المنزلية، Water leak detection💧🕵️‍♂️Roof insulation🏠Pools🏊‍♂️ التشطيبات🧱الديكورات🎨General maintenance🛠️الPlumbing🚿الElectrical💡الأجهزة الكهربائية🔌Landscaping🌴الCleaning🧼Pest control🐜and everything you need for a comfortable home or facility.',
        'Rukn Eltatawer — home services from Doha: leak detection, insulation, AC, plumbing, cleaning and pest control. Diagnose first, then a written quote.',
        $html
    );

    $html = rukn_qa_preg_replace('#<a class="twitter"[^>]*>.*?</a>#is', '', $html);
    $html = rukn_qa_preg_replace('#<a class="linkedin"[^>]*>.*?</a>#is', '', $html);
    $html = rukn_qa_preg_replace('#<a class="instagram"[^>]*>.*?</a>#is', '', $html);

    $contact = home_url('/contact-us/');
    $html = str_replace(
        '<a href="#"><i class="fas fa-location-dot"></i> Doha, Qa 🇶🇦</a>',
        '<a href="' . esc_url($contact) . '"><i class="fas fa-location-dot"></i> الدوحة، قطر</a>',
        $html
    );
    $html = str_replace('<small>Doha, Qa 🇶🇦</small>', '<small>الدوحة، قطر</small>', $html);
    $html = str_replace('<small>e-mail</small>', '<small>info@rukn-eltatawer.com</small>', $html);

    $html = rukn_qa_preg_replace(
        '#<h1>من نحن</h1>\s*<p class="psub">.*?</p>#s',
        '<h1>نحن <em>ركن التطور</em> — شريكك في راحة المنزل</h1><p class="psub">فريق خدمات منزلية يعمل من الدوحة: تشخيص قبل الإصلاح، تقرير واضح، وعرض سعر مكتوب. نغطي الدوحة ولوسيل والريان والوكرة وباقي مدن قطر.</p>',
        $html,
        1
    );
    $html = rukn_qa_preg_replace(
        '#<h1>اتصل بنا</h1>\s*<p class="psub">.*?</p>#s',
        '<h1>تواصل <em>معنا</em> — عبر واتساب</h1><p class="psub">أرسل المدينة ونوع الخدمة ووصف العطل. نحدد موعد المعاينة ثم نكتب العرض قبل التنفيذ. أزرار الاتصال مخفية حتى يتوفر رقم قطري جديد.</p>',
        $html,
        1
    );
    $html = rukn_qa_preg_replace(
        '#<h1>الأسئلة الشائعة</h1>\s*<p class="psub">.*?</p>#s',
        '<h1>الأسئلة <em>الشائعة</em></h1><p class="psub">إجابات مباشرة عن التغطية، المعاينة، الضمان، والتواصل عبر واتساب في قطر.</p>',
        $html,
        1
    );

    $guides = [
        'علامات تسرب المياه' => 'https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/',
        'الكشف بدون تكسير' => 'https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/',
        'تسرب الخزانات' => 'https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/',
        'أنواع العزل المائي' => 'https://www.rukn-eltatawer.com/qa/roof-insulation/',
        'العزل الحراري' => 'https://www.rukn-eltatawer.com/qa/roof-insulation/',
        'عزل الأسطح والخزانات' => 'https://www.rukn-eltatawer.com/qa/roof-insulation/',
        'الصيانة الدورية' => 'https://www.rukn-eltatawer.com/qa/maintenance/',
        'صيانة المباني' => 'https://www.rukn-eltatawer.com/qa/maintenance/',
        'صيانة الأجهزة' => 'https://www.rukn-eltatawer.com/qa/maintenance/',
        'التنظيف العميق' => 'https://www.rukn-eltatawer.com/qa/house-cleaning-in-qatar/',
        'تنظيف الخزانات' => 'https://www.rukn-eltatawer.com/qa/%d8%b9%d8%a7%d9%85%d9%84%d8%a7%d8%aa-%d8%aa%d9%86%d8%b8%d9%8a%d9%81/',
        'مكافحة الحشرات' => 'https://www.rukn-eltatawer.com/qa/house-cleaning-in-qatar/',
        'كيف تعمل الألواح' => 'https://www.rukn-eltatawer.com/qa/solar-energy/',
        'السخانات الشمسية' => 'https://www.rukn-eltatawer.com/qa/solar-energy/',
        'Signs of a water leak' => 'https://www.rukn-eltatawer.com/qa/en/water-leak-detection-qatar-en/',
        'Detection without breaking' => 'https://www.rukn-eltatawer.com/qa/en/water-leak-detection-qatar-en/',
        'Tank leaks' => 'https://www.rukn-eltatawer.com/qa/en/water-leak-detection-qatar-en/',
        'Tank cleaning' => 'https://www.rukn-eltatawer.com/qa/house-cleaning-in-qatar/',
        'Pest control' => 'https://www.rukn-eltatawer.com/qa/house-cleaning-in-qatar/',
        'How the panels work' => 'https://www.rukn-eltatawer.com/qa/solar-energy/',
        'Solar water heaters' => 'https://www.rukn-eltatawer.com/qa/solar-energy/',
        'أنواع الInsulation المائي' => 'https://www.rukn-eltatawer.com/qa/en/roof-insulation-qatar-en/',
        'الInsulation الحراري' => 'https://www.rukn-eltatawer.com/qa/en/roof-insulation-qatar-en/',
        'Roof insulation وTanks' => 'https://www.rukn-eltatawer.com/qa/en/roof-insulation-qatar-en/',
        'الMaintenance الدورية' => 'https://www.rukn-eltatawer.com/qa/maintenance/',
        'Maintenance المباني' => 'https://www.rukn-eltatawer.com/qa/maintenance/',
        'Maintenance الأجهزة' => 'https://www.rukn-eltatawer.com/qa/maintenance/',
        'الCleaning العميق' => 'https://www.rukn-eltatawer.com/qa/house-cleaning-in-qatar/',
    ];
    foreach ($guides as $label => $url) {
        $html = str_replace(
            '<a href="#"><i class="fas fa-chevron-left"></i> ' . $label . '</a>',
            '<a href="' . esc_url($url) . '"><i class="fas fa-chevron-left"></i> ' . $label . '</a>',
            $html
        );
    }

    $html = rukn_qa_preg_replace('~<form[^>]*action="#"[\\s\\S]*?</form>~i', '', $html);
    $html = str_replace('"wa_number":""', '"wa_number":"' . RUKN_QA_WA_KEEP . '"', $html);

    $html = str_replace(
        '<div class="faq-q">كيف أحجز خدمة؟ <i class="fas fa-chevron-down"></i></div><div class="faq-a" style="max-height:400px"><p>يمكن الحجز عبر الموقع مباشرة أو الاتصال بنا</p></div>',
        '<div class="faq-q">كيف أحجز خدمة؟ <i class="fas fa-chevron-down"></i></div><div class="faq-a" style="max-height:400px"><p>أرسل المدينة ونوع الخدمة ووصف العطل على واتساب. نحدد موعد المعاينة ثم نكتب العرض قبل التنفيذ. لا يوجد زر اتصال حتى يتوفر رقم قطري جديد.</p></div>',
        $html
    );
    $html = str_replace(
        '<div class="faq-q">ما هي طرق الدفع المتاحة؟ <i class="fas fa-chevron-down"></i></div><div class="faq-a"><p>نقدي، تحويل بنكي، أو دفع إلكتروني حسب الخدمة المتاحة.</p></div>',
        '<div class="faq-q">هل تعملون خارج الدوحة؟ <i class="fas fa-chevron-down"></i></div><div class="faq-a"><p>نعم بالتنسيق: لوسيل والريان والوكرة والخور وأم صلال والظعاين والشمال والشحانية. زمن الوصول يُذكر بعد العنوان.</p></div>',
        $html
    );
    $html = str_replace(
        '<div class="faq-q">هل يمكن إلغاء أو تعديل الحجز؟ <i class="fas fa-chevron-down"></i></div><div class="faq-a"><p>نعم، يمكن تعديل أو إلغاء الحجز قبل وصول الفريق حسب السياسات الموضحة في الموقع.</p></div>',
        '<div class="faq-q">هل الضمان عشر سنوات دائماً؟ <i class="fas fa-chevron-down"></i></div><div class="faq-a"><p>لا. مدة الضمان تُكتب في عرض السعر حسب الخدمة والخامة، وليست وعداً عاماً لكل عمل.</p></div>',
        $html
    );

    return $html;
}

add_filter('rest_request_after_callbacks', function ($response, $handler, $request) {
    if (!is_object($request) || !is_object($response) || !method_exists($response, 'get_data')) {
        return $response;
    }
    $route = method_exists($request, 'get_route') ? (string) $request->get_route() : '';
    if ($route === '/kayan/v1/dni' || substr($route, -12) === 'kayan/v1/dni') {
        $data = $response->get_data();
        if (is_array($data)) {
            $data['phone'] = '';
            $data['wa_number'] = RUKN_QA_WA_KEEP;
            $response->set_data($data);
        }
    }
    return $response;
}, 20, 3);

add_action('rest_api_init', function () {
    register_rest_route('rukn-qa/v1', '/repair-run', [
        'methods' => 'POST',
        'permission_callback' => function () {
            return current_user_can('manage_options');
        },
        'callback' => function () {
            delete_option('rukn_qa_repair_v10');
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
