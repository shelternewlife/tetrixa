#!/usr/bin/env python3
"""Generate only fully translated, explicitly published market locales."""
import html
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
APP = json.loads((ROOT / "content/app.json").read_text(encoding="utf-8"))
STRATEGY = json.loads((ROOT / "content/market-strategy.json").read_text(encoding="utf-8"))
LOCALES = json.loads((ROOT / "content/locales.json").read_text(encoding="utf-8"))
BASE = APP["website_url"].rstrip("/")
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML = "http://www.w3.org/1999/xhtml"
SECTIONS = ("home", "about", "features", "download", "faq")

def slug(locale):
    return locale.lower()

def locale_parts(locale):
    language, region = locale.split("-", 1)
    return language, region

def replace_text(source, old, new):
    if old and old != new:
        source = source.replace(html.escape(old, quote=False), html.escape(new, quote=True))
    return source

FLAG_DATA = {
    "en-US": ("us", "United States", "United States · English"),
    "en-CA": ("ca", "Canada", "Canada · English"),
    "fr-CA": ("ca", "Canada", "Canada · Français"),
    "es-ES": ("es", "Spain", "España · Español"),
    "pt-PT": ("pt", "Portugal", "Portugal · Português"),
    "fr-FR": ("fr", "France", "France · Français"),
    "de-DE": ("de", "Germany", "Deutschland · Deutsch"),
    "it-IT": ("it", "Italy", "Italia · Italiano"),
}

def render_locale_flags(published, tail="", current=None):
    links = []
    for code in published:
        country, country_name, label = FLAG_DATA[code]
        current_attr = ' aria-current="page"' if code == current else ""
        flag_url = f"https://flagcdn.com/w80/{country}.png"
        links.append(
            f'<a class="locale-flag" lang="{code}" href="{BASE}/{slug(code)}/{tail}" '
            f'title="{html.escape(label, quote=True)}" aria-label="{html.escape(label, quote=True)}"{current_attr}>'
            f'<img src="{flag_url}" alt="{html.escape(country_name, quote=True)} flag" width="40" height="30" loading="eager" decoding="async"></a>'
        )
    return "".join(links)

def ensure_social_links(source):
    if 'class="social-links"' in source:
        return source
    import build
    return re.sub(
        r'(<div class="locale-switch"[^>]*>.*?)(</div>)',
        lambda match: match.group(1) + build.render_social_links() + match.group(2),
        source,
        count=1,
        flags=re.DOTALL,
    )

def localize(source, locale, section, route_tail=None):
    import build
    language, region = locale_parts(locale)
    data = LOCALES.get(locale, {})
    replacements = []
    for key, value in build.TEXT["en"].items():
        if key in data.get("text", {}):
            replacements.append((value, data["text"][key]))
    for key, value in build.PAGE_TITLES["en"].items():
        if key in data.get("titles", {}):
            replacements.append((value, data["titles"][key]))
    for key, value in build.PAGE_DESCRIPTIONS["en"].items():
        if key in data.get("descriptions", {}):
            replacements.append((value, data["descriptions"][key]))
    if data.get("app_description"):
        replacements.append((APP["description"]["en"], data["app_description"]))
    if data.get("tagline"):
        replacements.append((APP["tagline"]["en"], data["tagline"]))
    replacements.extend([
        ("Explore this feature", "Explorer cette fonctionnalité")
        for _ in [0] if language == "fr"
    ])
    if data.get("features"):
        for feature, translated in zip(build.FEATURES, data["features"]):
            replacements.extend([(feature["title"]["en"], translated[0]),
                                 (feature["description"]["en"], translated[1])])
    if data.get("faq"):
        for item, translated in zip(build.FAQ, data["faq"]):
            replacements.extend([(item["q"]["en"], translated[0]),
                                 (item["a"]["en"], translated[1])])
    if data.get("screenshots"):
        for screenshot, translated in zip(build.SCREENSHOTS, data["screenshots"]):
            replacements.extend([(screenshot["alt"]["en"], translated[0]),
                                 (screenshot["caption"]["en"], translated[1])])
    for old, new in sorted(replacements, key=lambda pair: len(pair[0]), reverse=True):
        source = replace_text(source, old, new)
    if locale == "fr-CA":
        source = source.replace('og:locale" content="en_US"', 'og:locale" content="fr_CA"')
    elif locale == "en-CA":
        source = source.replace('og:locale" content="en_US"', 'og:locale" content="en_CA"')
    # Localize the two navigation group labels and the resource links.
    nav_groups = {
        "en-US": ("Explore", "Resources"), "en-CA": ("Explore", "Resources"),
        "fr-CA": ("Explorer", "Ressources"), "es-ES": ("Explorar", "Recursos"),
        "pt-PT": ("Explorar", "Recursos"), "fr-FR": ("Explorer", "Ressources"),
        "de-DE": ("Entdecken", "Ressourcen"), "it-IT": ("Esplora", "Risorse"),
    }
    primary_label, resource_label = nav_groups[locale]
    source = source.replace("<summary>Explore</summary>", f"<summary>{primary_label}</summary>")
    source = source.replace("<summary>Resources</summary>", f"<summary>{resource_label}</summary>")
    from build_locale_resources import CONTENT as RESOURCE_CONTENT
    for item, label in RESOURCE_CONTENT[locale]["nav"].items():
        source = re.sub(
            rf'(<a[^>]*data-nav-item="{re.escape(item)}"[^>]*>).*?(</a>)',
            lambda match, value=html.escape(label, quote=False): match.group(1) + value + match.group(2),
            source,
        )
    # Convert every internal English route, including navigation and feature anchors.
    source = source.replace(f"{BASE}/en/", f"{BASE}/{slug(locale)}/")
    source = source.replace('<html lang="en"', f'<html lang="{locale}"')
    tail = route_tail if route_tail is not None else ("" if section == "home" else f"{section}/")
    source = ensure_social_links(source)
    selector = render_locale_flags(STRATEGY["published_locales"], tail, locale)
    source = re.sub(
        r'(<div class="locale-switch"[^>]*>).*?(<div class="social-links"[^>]*>)',
        lambda match: match.group(1) + selector + match.group(2),
        source,
        count=1,
        flags=re.DOTALL,
    )
    if section != "home":
        switch_match = re.search(r'<div class="locale-switch"[^>]*>.*?</div>', source, re.DOTALL)
        if switch_match:
            switch_markup = switch_match.group(0)
            source = source.replace(switch_markup, "", 1)
            source = source.replace('<div class="header-main">', '<div class="header-main">' + switch_markup, 1)
        source = source.replace('<header class="home-header">', '<header class="standard-header">', 1)

    source = re.sub(
        r'<link rel="alternate" hreflang="(?:en|ar|x-default)" href="[^"]+">\n?',
        "",
        source,
    )
    canonical = f"{BASE}/{slug(locale)}/{tail}"
    alternates = ''.join(
        f'<link rel="alternate" hreflang="{code}" href="{BASE}/{slug(code)}/{tail}">\n'
        for code in STRATEGY["published_locales"]
    )
    alternates += f'<link rel="alternate" hreflang="x-default" href="{BASE}/en-us/{tail}">'
    source = source.replace(f'<link rel="canonical" href="{canonical}">',
                            f'<link rel="canonical" href="{canonical}">\n{alternates}')
    source = source.replace('content="en_US"', f'content="{locale.replace("-", "_")}"')
    source = source.replace('"inLanguage": "en"', f'"inLanguage": "{locale}"')
    return source

def build_localized_pages():
    published = STRATEGY.get("published_locales", [])
    if not published:
        raise ValueError("market-strategy.json must explicitly list published_locales")
    market_locales = {
        locale
        for market in STRATEGY["markets"]
        if market.get("status") == "initial"
        for locale in market.get("locales", [])
    }
    if not set(published).issubset(market_locales):
        raise ValueError("A published locale must belong to an initial market")
    if set(published) != set(LOCALES.keys()) | {"en-US", "en-CA"}:
        raise ValueError("Every published locale must have complete locale content")
    for locale in published:
        if locale not in ("en-US", "en-CA") and locale not in LOCALES:
            raise ValueError(f"Missing translation bundle for {locale}")
        for section in SECTIONS:
            source_path = DIST / "en" / ("" if section == "home" else section) / "index.html"
            source = source_path.read_text(encoding="utf-8")
            write_path = DIST / slug(locale) / ("" if section == "home" else section) / "index.html"
            write_path.parent.mkdir(parents=True, exist_ok=True)
            write_path.write_text(localize(source, locale, section), encoding="utf-8")
    import build
    for locale in published:
        for feature in build.FEATURES:
            tail = f"features/{feature['id']}/"
            source_path = DIST / "en" / "features" / feature["id"] / "index.html"
            source = source_path.read_text(encoding="utf-8")
            target = DIST / slug(locale) / tail / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(localize(source, locale, "features", tail), encoding="utf-8")
    update_legacy_pages(published)
    update_root_page(published)
    update_sitemaps(published)
    llms = DIST / "llms.txt"
    existing = llms.read_text(encoding="utf-8")
    existing += "\n## Published market locales\n"
    for locale in published:
        existing += f"- {locale}: {BASE}/{slug(locale)}/\n"
    llms.write_text(existing, encoding="utf-8")

def update_legacy_pages(published):
    for language in ("en", "ar"):
        root = DIST / language
        for path in root.rglob("index.html"):
            relative = path.parent.relative_to(root)
            tail = "" if str(relative) == "." else relative.as_posix() + "/"
            source = path.read_text(encoding="utf-8")
            source = ensure_social_links(source)
            selector = render_locale_flags(published, tail)
            source = re.sub(
                r'(<div class="locale-switch"[^>]*>).*?(<div class="social-links"[^>]*>)',
                lambda match: match.group(1) + selector + match.group(2),
                source,
                count=1,
                flags=re.DOTALL,
            )
            if tail:
                switch_match = re.search(r'<div class="locale-switch"[^>]*>.*?</div>', source, re.DOTALL)
                if switch_match:
                    switch_markup = switch_match.group(0)
                    source = source.replace(switch_markup, "", 1)
                    source = source.replace('<div class="header-main">', '<div class="header-main">' + switch_markup, 1)
                source = source.replace('<header class="home-header">', '<header class="standard-header">', 1)
            path.write_text(source, encoding="utf-8")


def update_root_page(published):
    import build
    build.write(pathlib.Path("index.html"), build.render_language_root())

def update_sitemaps(published):
    xml_path = DIST / "sitemap.xml"
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ET.register_namespace("", NS)
    ET.register_namespace("xhtml", XHTML)
    for node in list(root.findall(f"{{{NS}}}url")):
        if node.findtext(f"{{{NS}}}loc") == f"{BASE}/":
            root.remove(node)
    for section in SECTIONS:
        path_tail = "" if section == "home" else f"{section}/"
        alternates = [(locale, f"{BASE}/{slug(locale)}/{path_tail}") for locale in published]
        for locale, url in alternates:
            node = ET.SubElement(root, f"{{{NS}}}url")
            ET.SubElement(node, f"{{{NS}}}loc").text = url
            for alt_locale, alt_url in alternates:
                ET.SubElement(node, f"{{{XHTML}}}link", {
                    "rel": "alternate", "hreflang": alt_locale, "href": alt_url
                })
            ET.SubElement(node, f"{{{XHTML}}}link", {
                "rel": "alternate", "hreflang": "x-default", "href": alternates[0][1]
            })
    import build
    for feature in build.FEATURES:
        tail = f"features/{feature['id']}/"
        alternates = [(locale, f"{BASE}/{slug(locale)}/{tail}") for locale in published]
        for locale, url in alternates:
            node = ET.SubElement(root, f"{{{NS}}}url")
            ET.SubElement(node, f"{{{NS}}}loc").text = url
            for alt_locale, alt_url in alternates:
                ET.SubElement(node, f"{{{XHTML}}}link", {
                    "rel": "alternate", "hreflang": alt_locale, "href": alt_url
                })
            ET.SubElement(node, f"{{{XHTML}}}link", {
                "rel": "alternate", "hreflang": "x-default", "href": alternates[0][1]
            })
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    urls = [line.strip() for line in (DIST / "sitemap.txt").read_text(encoding="utf-8").splitlines() if line.strip() and line.strip() != f"{BASE}/"]
    for section in SECTIONS:
        tail = "" if section == "home" else f"{section}/"
        urls.extend(f"{BASE}/{slug(locale)}/{tail}" for locale in published)
    for feature in build.FEATURES:
        tail = f"features/{feature['id']}/"
        urls.extend(f"{BASE}/{slug(locale)}/{tail}" for locale in published)
    (DIST / "sitemap.txt").write_text("\n".join(urls) + "\n", encoding="utf-8")

def main():
    build_localized_pages()

if __name__ == "__main__":
    main()
