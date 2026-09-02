
/**
 * Rukn Qatar SEO + contact localization
 */
if (!defined('ABSPATH')) {
    return;
}

const RUKN_QA_PHONE = '+97431110184';
const RUKN_QA_WA = '97431110184';
const RUKN_QA_GEO = '25.2854, 51.5310';

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
        $titles['phone_numbers'] = [
            ['type' => 'customer support', 'number' => RUKN_QA_PHONE],
        ];
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
            ['971586634710', '201151481000', '20 1151481000', 'الخيثة', 'المشحمية'],
            [RUKN_QA_WA, RUKN_QA_WA, RUKN_QA_PHONE, 'الخيسة', 'الشحانية'],
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
                ['971586634710', '201151481000', 'الخيثة', 'المشحمية'],
                [RUKN_QA_WA, RUKN_QA_WA, 'الخيسة', 'الشحانية'],
                $val
            );
            if ($nv !== $val) {
                update_option($name, $nv);
            }
        } elseif (is_array($val)) {
            $encoded = wp_json_encode($val);
            $new = str_replace(
                ['971586634710', '201151481000', 'الخيثة', 'المشحمية'],
                [RUKN_QA_WA, RUKN_QA_WA, 'الخيسة', 'الشحانية'],
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
            $node['telephone'] = RUKN_QA_PHONE;
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
    $is_en = (function_exists('pll_current_language') && pll_current_language() === 'en')
        || (isset($_SERVER['REQUEST_URI']) && strpos($_SERVER['REQUEST_URI'], '/qa/en') !== false);
    if (is_front_page()) {
        return $is_en ? 'https://www.rukn-eltatawer.com/qa/en/' : 'https://www.rukn-eltatawer.com/qa/';
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

add_action('wp_footer', function () {
    $phone = RUKN_QA_PHONE;
    $wa = RUKN_QA_WA;
    $msg = rawurlencode('مرحباً، أريد الاستفسار عن خدمات ركن التطور في قطر');
    echo '<script id="rukn-qa-contact-fix">';
    echo 'window.RuknCS=Object.assign(window.RuknCS||{},{call_show:true,wa_show:true,call_number:"' . esc_js($phone) . '",wa_number:"' . esc_js($wa) . '",wa_message:"مرحباً، أريد الاستفسار عن خدمات ركن التطور في قطر"});';
    echo '(function(){var p="' . esc_js($phone) . '",w="' . esc_js($wa) . '",m="' . $msg . '";';
    echo 'function apply(){document.querySelectorAll("a[href^=\'tel:\']").forEach(function(a){if(a.getAttribute("href")!=="tel:"+p){a.setAttribute("href","tel:"+p)}});';
    echo 'document.querySelectorAll("a[href*=\'wa.me\'],a[href*=\'api.whatsapp\']").forEach(function(a){var u="https://wa.me/"+w+"?text="+m;if(a.getAttribute("href")!==u){a.setAttribute("href",u);}});}';
    echo 'apply();document.addEventListener("DOMContentLoaded",apply);setTimeout(apply,500);setTimeout(apply,1500);})();';
    echo 'document.addEventListener("DOMContentLoaded",function(){document.querySelectorAll("[data-count]").forEach(function(el){if((el.textContent||"").trim()==="0"){el.textContent=el.getAttribute("data-count")||"0";}});});';
    echo '</script>';
    if (is_front_page()) {
        $is_en = (function_exists('pll_current_language') && pll_current_language() === 'en')
            || (isset($_SERVER['REQUEST_URI']) && strpos($_SERVER['REQUEST_URI'], '/qa/en') !== false);
        $url = $is_en
            ? 'https://www.rukn-eltatawer.com/qa/en/water-leak-detection-qatar-en/'
            : 'https://www.rukn-eltatawer.com/qa/water-leak-detection-company-in-qatar/';
        $label = $is_en ? 'Water leak detection in Qatar' : 'شركة كشف تسربات المياه في قطر';
        echo '<p class="rukn-home-leak-link" style="text-align:center;padding:14px 16px;margin:0;background:#0E2455;"><a style="color:#fff;font-weight:700;text-decoration:none;" href="' . esc_url($url) . '">' . esc_html($label) . '</a></p>';
    }
}, 9999);

add_filter('language_attributes', function ($out) {
    if (function_exists('pll_current_language') && pll_current_language() === 'en') {
        return 'lang="en-GB" dir="ltr"';
    }
    return $out;
}, 99);

add_action('template_redirect', function () {
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
        // Never alter the ranking leak article HTML.
        if (is_singular() && (int) get_queried_object_id() === 2973) {
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
        $html = str_replace('الخيثة', 'الخيسة', $html);
        $html = str_replace('المشحمية', 'الشحانية', $html);
        $html = str_replace('971586634710', '97431110184', $html);
        $html = str_replace('201151481000', '97431110184', $html);
        $html = str_replace('+971586634710', '+97431110184', $html);
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
        $is_en = (function_exists('pll_current_language') && pll_current_language() === 'en')
            || (isset($_SERVER['REQUEST_URI']) && strpos($_SERVER['REQUEST_URI'], '/qa/en') !== false);
        if ($is_en) {
            $html = preg_replace('/<html[^>]*>/', '<html lang="en-GB" dir="ltr">', $html, 1);
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
