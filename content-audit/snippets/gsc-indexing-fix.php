/**
 * Rukn Qatar GSC indexing fix
 * Do not edit snippet 5. Do not change post #2973 content.
 * Keep WhatsApp 971586634710. Hide calls.
 *
 * Fixes Search Console "not indexed" reasons for qa/sitemap_index.xml:
 * - drop redirecting and 404 URLs from the sitemap
 * - 301 dead category URLs to real pillars
 * - collapse duplicate /qa/qa/ URLs
 * - stop advertising English hreflang that 301s back to Arabic
 */
if (!defined('ABSPATH')) {
    return;
}

const RUKN_QA_GSC_WA = '971586634710';

function rukn_qa_gsc_skip_sitemap_urls() {
    $home = untrailingslashit(home_url('/'));
    return [
        $home . '/water-leak-detection',
        $home . '/roof-insulation',
        $home . '/service',
        $home . '/sewerage-company-in-doha',
        $home . '/gas-leak-detection-doha',
        $home . '/water-leak-detection-lusail',
        $home . '/water-pipe-leak-detection-lusail',
        $home . '/shrkh-tnzyf-mnazl-fy-qtr-2',
        $home . '/shrkh-mkafhh-srasyr-fy-qtr',
    ];
}

function rukn_qa_gsc_en_allow() {
    $home = untrailingslashit(home_url('/'));
    return [
        $home . '/en',
        $home . '/en/water-leak-detection-qatar-en',
        $home . '/en/roof-insulation-qatar-en',
        $home . '/en/ac-maintenance-qatar-en',
        $home . '/contact-us-2',
    ];
}

function rukn_qa_gsc_norm($url) {
    $url = strtok((string) $url, '?');
    return untrailingslashit($url);
}

function rukn_qa_gsc_redirect_map() {
    $h = trailingslashit(home_url('/'));
    return [
        '/qa/water-leak-detection/' => $h . 'water-leak-detection-company-in-qatar/',
        '/qa/roof-insulation/' => $h . 'shrkh-azl-asth-fy-qtr/',
        '/qa/service/' => $h . 'services/',
        '/qa/sewerage-company-in-doha/' => $h . 'shrkh-tslyk-mjary-fy-qtr/',
        '/qa/gas-leak-detection-doha/' => $h . 'shrkh-kshf-tsrbat-alghaz-fy-qtr/',
        '/qa/water-leak-detection-lusail/' => $h . 'water-leak-detection-company-in-qatar/',
        '/qa/water-pipe-leak-detection-lusail/' => $h . 'water-leak-detection-company-in-qatar/',
        '/qa/shrkh-tnzyf-mnazl-fy-qtr-2/' => $h . 'house-cleaning-in-qatar/',
        '/qa/shrkh-mkafhh-srasyr-fy-qtr/' => $h . 'cockroach-control-in-qatar/',
    ];
}

add_action('template_redirect', function () {
    $path = (string) parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    if ($path === '') {
        return;
    }
    if (substr($path, -1) !== '/') {
        $path .= '/';
    }
    $map = rukn_qa_gsc_redirect_map();
    if (isset($map[$path])) {
        wp_redirect($map[$path], 301);
        exit;
    }
    if (preg_match('#^/qa/qa(/.*)?$#', $path, $m)) {
        $rest = isset($m[1]) && $m[1] !== '' ? $m[1] : '/';
        wp_redirect(home_url($rest), 301);
        exit;
    }
}, -1);

add_action('wp_head', function () {
    if (function_exists('is_author') && (is_author() || is_date() || is_search() || is_attachment())) {
        echo '<meta name="robots" content="noindex,follow" />' . "\n";
    }
}, 1);

add_filter('rank_math/frontend/canonical', function ($canonical) {
    $canonical = str_replace('https://www.rukn-eltatawer.com/qa/qa/', 'https://www.rukn-eltatawer.com/qa/', (string) $canonical);
    return $canonical;
}, 99);

add_filter('rank_math/opengraph/url', function ($url) {
    return str_replace('https://www.rukn-eltatawer.com/qa/qa/', 'https://www.rukn-eltatawer.com/qa/', (string) $url);
}, 99);

add_filter('pll_rel_hreflang_attributes', function ($hreflangs) {
    if (!is_array($hreflangs)) {
        return $hreflangs;
    }
    $allow = array_map('rukn_qa_gsc_norm', rukn_qa_gsc_en_allow());
    foreach ($hreflangs as $lang => $url) {
        if ($lang !== 'en' && strpos((string) $lang, 'en') !== 0) {
            continue;
        }
        if (!in_array(rukn_qa_gsc_norm($url), $allow, true)) {
            unset($hreflangs[$lang]);
        }
    }
    return $hreflangs;
}, 99);

add_filter('rank_math/sitemap/entry', function ($url, $type = '', $object = null) {
    if (!is_array($url) || empty($url['loc'])) {
        return $url;
    }
    $loc = rukn_qa_gsc_norm($url['loc']);
    if (strpos($loc, '/qa/qa/') !== false) {
        return false;
    }
    foreach (rukn_qa_gsc_skip_sitemap_urls() as $skip) {
        if ($loc === rukn_qa_gsc_norm($skip)) {
            return false;
        }
    }
    return $url;
}, 20, 3);

add_filter('rank_math/sitemap/exclude_taxonomy', function ($exclude, $taxonomy) {
    if ($taxonomy === 'category') {
        return true;
    }
    return $exclude;
}, 20, 2);

add_action('init', function () {
    if (get_option('rukn_qa_gsc_fix_v1') === '1') {
        return;
    }
    if (function_exists('do_action')) {
        do_action('rank_math/sitemap/invalidate_cache');
        do_action('litespeed_purge_all');
    }
    update_option('rukn_qa_gsc_fix_v1', '1');
}, 40);

add_action('template_redirect', function () {
    if (is_admin() || (function_exists('wp_doing_ajax') && wp_doing_ajax()) || (function_exists('wp_is_json_request') && wp_is_json_request())) {
        return;
    }
    ob_start('rukn_qa_gsc_html');
}, 8);

function rukn_qa_gsc_html($html) {
    if (!is_string($html) || $html === '') {
        return $html;
    }
    $html = str_replace('https://www.rukn-eltatawer.com/qa/qa/', 'https://www.rukn-eltatawer.com/qa/', $html);
    $allow = array_map('rukn_qa_gsc_norm', rukn_qa_gsc_en_allow());
    $next = preg_replace_callback('#<link[^>]+rel=["\']alternate["\'][^>]*>#i', function ($m) use ($allow) {
        $tag = $m[0];
        if (stripos($tag, 'hreflang="en"') === false && stripos($tag, "hreflang='en'") === false) {
            return $tag;
        }
        if (!preg_match('#href=["\']([^"\']+)#i', $tag, $hm)) {
            return $tag;
        }
        $href = rukn_qa_gsc_norm($hm[1]);
        return in_array($href, $allow, true) ? $tag : '';
    }, $html);
    if (is_string($next)) {
        $html = $next;
    }
    return $html;
}

add_action('rest_api_init', function () {
    register_rest_route('rukn-qa/v1', '/gsc-fix', [
        'methods' => 'POST',
        'permission_callback' => function () {
            return current_user_can('manage_options');
        },
        'callback' => function () {
            delete_option('rukn_qa_gsc_fix_v1');
            if (function_exists('do_action')) {
                do_action('rank_math/sitemap/invalidate_cache');
                do_action('litespeed_purge_all');
            }
            if (class_exists('LiteSpeed\\Purge')) {
                \LiteSpeed\Purge::purge_all();
            }
            update_option('rukn_qa_gsc_fix_v1', '1');
            return ['ok' => true];
        },
    ]);
});
