#!/usr/bin/env python3
"""Generated national articles stay >=1000 words and keep WhatsApp."""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kayan_article_builder import build_article
from post_policy import should_rewrite_post, should_unpublish


def word_count(s: str) -> int:
    text = re.sub(r"<[^>]+>", " ", s)
    text = html.unescape(text)
    return len(re.findall(r"\w+", text, flags=re.UNICODE))


SAMPLES = [
    ("شركة تنظيف فلل في قطر", "villa-cleaning-in-qatar", "ar"),
    ("شركة تنظيف شقق في قطر", "apartment-cleaning-in-qatar", "ar"),
    ("شركة عزل أسطح في قطر", "roof-insulation-in-qatar", "ar"),
    ("شركة عزل صوتي في قطر", "shrkh-azl-swty-fy-qtr", "ar"),
    ("شركة تسليك مجاري في الدوحة", "sewerage-company-in-doha", "ar"),
    ("Water leak detection in Qatar without breaking", "water-leak-detection-qatar-en", "en"),
    ("AC maintenance in Doha and Qatar", "ac-maintenance-qatar-en", "en"),
    ("Roof insulation in Qatar", "roof-insulation-qatar-en", "en"),
]


def main():
    failed = []
    for title, slug, lang in SAMPLES:
        html_out, desc, kw = build_article(title, slug, lang)
        n = word_count(html_out)
        print(f"{n:5} {lang} {title}")
        if n < 1000:
            failed.append((title, n))
        if "971586634710" not in html_out:
            failed.append((title, "missing-whatsapp"))
        if "معاينة مجانية" in html_out:
            failed.append((title, "free-inspection-claim"))
    assert should_rewrite_post(10264, "شركة تنظيف فلل في قطر", "villa-cleaning-in-qatar")
    assert not should_rewrite_post(2973, "شركة كشف تسربات المياه في قطر", "water-leak-detection-company-in-qatar")
    assert not should_rewrite_post(17411, "شركة تسليك مجاري في الشحانية", "sewerage-company-in-al-shahaniya")
    assert should_unpublish(17411, "شركة تسليك مجاري في الشحانية", "sewerage-company-in-al-shahaniya")
    assert not should_unpublish(3182, "شركة تسليك مجاري في الدوحة", "sewerage-company-in-doha")
    if failed:
        raise SystemExit(f"failed: {failed}")
    print("PASS")


if __name__ == "__main__":
    main()
