"""Which posts may be rewritten, published, or returned to draft."""
from __future__ import annotations

LOCKED_POST_IDS = {2973}
SKIP_SERVICES = {1877}
ALLOWED_CITY_SLUGS = {
    "sewerage-company-in-doha",
    "gas-leak-detection-doha",
    "ac-leak-detection-doha",
}
PILLAR_LEAK = {
    "water-leak-detection-company-in-qatar",
    "water-leak-detection-qatar-en",
}
CITY_SUFFIXES = (
    "al-shahaniya",
    "al-daayen",
    "umm-salal",
    "al-wakrah",
    "al-rayyan",
    "al-shamal",
    "al-khor",
    "lusail",
    "doha",
)
CITY_IN_TITLE = (
    "في الدوحة",
    "في الريان",
    "في الوكرة",
    "في الخور",
    "في أم صلال",
    "في الظعاين",
    "في الشمال",
    "في الشحانية",
    "في لوسيل",
)
LEAK_MARKS = ("كشف تسربات المياه", "كشف تسربات المواسير", "water leak", "water-leak")


def city_suffix(slug: str) -> str | None:
    slug = slug or ""
    for s in CITY_SUFFIXES:
        if slug == s or slug.endswith("-" + s):
            return s
    return None


def is_city_template(title: str, slug: str) -> bool:
    if slug in ALLOWED_CITY_SLUGS or slug in PILLAR_LEAK:
        return False
    if city_suffix(slug):
        return True
    return any(c in (title or "") for c in CITY_IN_TITLE)


def is_leak_clone(title: str, slug: str) -> bool:
    if slug in PILLAR_LEAK:
        return False
    blob = f"{title} {slug}".lower()
    if not any(m.lower() in blob for m in LEAK_MARKS):
        return False
    return bool(city_suffix(slug) or any(c in (title or "") for c in CITY_IN_TITLE))


def should_rewrite_post(pid: int, title: str, slug: str) -> bool:
    if int(pid) in LOCKED_POST_IDS:
        return False
    if is_leak_clone(title, slug) or is_city_template(title, slug):
        return False
    return True


def should_unpublish(pid: int, title: str, slug: str) -> bool:
    if int(pid) in LOCKED_POST_IDS or slug in ALLOWED_CITY_SLUGS or slug in PILLAR_LEAK:
        return False
    return is_leak_clone(title, slug) or is_city_template(title, slug)
