import json
import re
import pathlib
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlparse
from build_resources import routes as resource_routes

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
APP = json.loads((ROOT / "content/app.json").read_text(encoding="utf-8"))
STRATEGY = json.loads((ROOT / "content/market-strategy.json").read_text(encoding="utf-8"))
GA_MEASUREMENT_ID = APP["ga4_measurement_id"]
SCREENSHOTS = json.loads((ROOT / "content/screenshots.json").read_text(encoding="utf-8"))
FEATURES = json.loads((ROOT / "content/features.json").read_text(encoding="utf-8"))
BASE = APP["website_url"].rstrip("/")
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
ERRORS = []

class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.all_images = []
        self.canonical = None
        self.hreflang = {}
        self.title = []
        self.h1 = []
        self.in_title = False
        self.in_h1 = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "img":
            self.all_images.append(attrs)
            image_src = attrs.get("src", "")
            if image_src.startswith("https://play-lh.googleusercontent.com/") or "/assets/screens/" in image_src:
                self.images.append(attrs)
        if tag == "link":
            if attrs.get("rel") == "canonical":
                self.canonical = attrs.get("href")
            if attrs.get("rel") == "alternate" and attrs.get("hreflang"):
                self.hreflang[attrs["hreflang"]] = attrs.get("href")
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.in_h1 = True
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "h1":
            self.in_h1 = False
    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self.in_h1:
            self.h1.append(data)

def expected_url(lang, section="home"):
    return f"{BASE}/{lang}/" + ("" if section == "home" else f"{section}/")

def page_path(lang, section="home"):
    return DIST / lang / ("" if section == "home" else section) / "index.html"

def fail(message):
    ERRORS.append(message)

required_files = [
    DIST / "index.html", DIST / "robots.txt", DIST / "sitemap.xml",
    DIST / "sitemap.txt", DIST / "llms.txt", DIST / "assets/style.css",
]
if not (ROOT / "content/screenshots.json").is_file():
    fail("Missing source screenshot manifest: content/screenshots.json")
for path in required_files:
    if not path.is_file():
        fail(f"Missing generated file: {path.relative_to(DIST)}")

route_urls = set()
for lang in ("en", "ar"):
    for section in ("home", "about", "features", "download", "faq"):
        route_urls.add(expected_url(lang, section))
        path = page_path(lang, section)
        if not path.is_file():
            fail(f"Missing route: {path.relative_to(DIST)}")
            continue
        parser = DocumentParser()
        parser.feed(path.read_text(encoding="utf-8"))
        expected_canonical = expected_url(lang, section)
        if parser.canonical != expected_canonical:
            fail(f"Wrong canonical for {path.relative_to(DIST)}: {parser.canonical}")
        if parser.hreflang.get("en") != expected_url("en", section):
            fail(f"Wrong English hreflang for {path.relative_to(DIST)}")
        if parser.hreflang.get("ar") != expected_url("ar", section):
            fail(f"Wrong Arabic hreflang for {path.relative_to(DIST)}")
        if parser.hreflang.get("x-default") != expected_url("en", section):
            fail(f"Wrong x-default hreflang for {path.relative_to(DIST)}")
        page_html = path.read_text(encoding="utf-8")
        if '"@type": "Organization"' not in page_html or '"@type": "SoftwareApplication"' not in page_html:
            fail(f"Missing Organization or SoftwareApplication JSON-LD on {path.relative_to(DIST)}")
        if section == "faq" and ('"@type": "FAQPage"' not in page_html or page_html.count('"@type": "Question"') != 12):
            fail(f"FAQPage JSON-LD must describe all 12 visible FAQ entries: {path.relative_to(DIST)}")
        if section != "faq" and '"@type": "FAQPage"' in page_html:
            fail(f"FAQPage JSON-LD must only appear on the FAQ page: {path.relative_to(DIST)}")
        if f"https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}" not in page_html:
            fail(f"Missing GA4 library on {path.relative_to(DIST)}")
        if f"gtag('config', '{GA_MEASUREMENT_ID}')" not in page_html:
            fail(f"Missing GA4 configuration on {path.relative_to(DIST)}")
        if "gtag('event', 'google_play_click'" not in page_html:
            fail(f"Missing Google Play click event handler on {path.relative_to(DIST)}")
        for required_meta in ('name="description"', 'name="robots" content="index,follow', 'property="og:title"', 'property="og:image"', 'name="twitter:card"'):
            if required_meta not in page_html:
                fail(f"Missing SEO metadata {required_meta} in {path.relative_to(DIST)}")
        if not parser.title or not "".join(parser.title).strip():
            fail(f"Missing title for {path.relative_to(DIST)}")
        if not parser.h1 or not "".join(parser.h1).strip():
            fail(f"Missing H1 for {path.relative_to(DIST)}")
        if page_html.count("<h1") != 1:
            fail(f"Page must contain exactly one H1: {path.relative_to(DIST)}")
        if '<a class="skip-link" href="#main-content">' not in page_html or '<main id="main-content">' not in page_html:
            fail(f"Missing accessible skip link or main landmark: {path.relative_to(DIST)}")
        for image in parser.all_images:
            if not image.get("alt", "").strip():
                fail(f"Image without alternative text: {path.relative_to(DIST)}")
            if not image.get("width") or not image.get("height"):
                fail(f"Image without intrinsic dimensions: {path.relative_to(DIST)}")
        import re
        tracked_locations = {
            "home": ["home_hero"],
            "about": ["about_intro"],
            "features": ["features_end"],
            "download": ["download_hero", "download_end"],
            "faq": ["faq_end"],
        }
        found_locations = re.findall(r'data-analytics-event="google_play_click" data-cta-location="([^"]+)"', page_html)
        if found_locations != tracked_locations[section]:
            fail(f"Incorrect Google Play click tracking locations on {path.relative_to(DIST)}")
        if section == "download":
            page_html = path.read_text(encoding="utf-8")
            if APP["google_play_url"] not in parser.links:
                fail(f"Download page is missing its official Google Play CTA: {path.relative_to(DIST)}")
            if 'name="description"' not in page_html or 'name="robots" content="index,follow' not in page_html:
                fail(f"Download page is missing SEO description or index directive: {path.relative_to(DIST)}")
            if '"@type": "SoftwareApplication"' not in page_html or '"installUrl":' not in page_html:
                fail(f"Download page is missing SoftwareApplication install structured data: {path.relative_to(DIST)}")
                fail(f"Download page is missing MobileApplication install structured data: {path.relative_to(DIST)}")
        if section == "faq" and APP["google_play_url"] not in parser.links:
            fail(f"FAQ page is missing its official Google Play CTA: {path.relative_to(DIST)}")
        if section == "features":
            page_html = path.read_text(encoding="utf-8")
            if APP["google_play_url"] not in parser.links:
                fail(f"Features page is missing its Google Play CTA: {path.relative_to(DIST)}")
            if len(parser.images) != len(FEATURES):
                fail(f"Features page should illustrate every feature with a screenshot: {path.relative_to(DIST)}")
        if section == "home":
            if len(parser.images) != 1 + (len(SCREENSHOTS) * 2):
                fail(f"Homepage should contain a hero image, {len(SCREENSHOTS)} gallery images and {len(SCREENSHOTS)} feature images: {path.relative_to(DIST)}")
            gallery_images = parser.images[1:1 + len(SCREENSHOTS)]
            if len({image.get("src") for image in gallery_images}) != len(SCREENSHOTS):
                fail(f"Homepage gallery contains duplicate screenshot sources: {path.relative_to(DIST)}")
            if any(not image.get("alt", "").strip() for image in gallery_images):
                fail(f"Homepage gallery contains an image without alt text: {path.relative_to(DIST)}")
        for href in parser.links:
            if href.startswith(("mailto:", "tel:", "#")):
                continue
            parsed = urlparse(href)
            base_parts = urlparse(BASE)
            if parsed.scheme in ("http", "https"):
                if parsed.netloc != base_parts.netloc:
                    continue
                base_path = base_parts.path.rstrip("/")
                if parsed.path != base_path and not parsed.path.startswith(base_path + "/"):
                    fail(f"Internal link escapes project base path: {href} in {path.relative_to(DIST)}")
                    continue
                relative = parsed.path[len(base_path):].lstrip("/")
            else:
                if parsed.scheme or parsed.netloc:
                    fail(f"Unsupported internal link {href} in {path.relative_to(DIST)}")
                    continue
                if not href.startswith(BASE + "/"):
                    fail(f"Internal link escapes project base path: {href} in {path.relative_to(DIST)}")
                    continue
                relative = href[len(BASE) + 1:]
            target = DIST / relative
            if relative.endswith("/"):
                target = target / "index.html"
            elif not target.suffix:
                target = target / "index.html"
            if not target.is_file():
                fail(f"Broken internal link {href} in {path.relative_to(DIST)}")


for locale in STRATEGY.get("published_locales", []):
    slug = locale.lower()
    for section in ("home", "about", "features", "download", "faq"):
        route = f"{BASE}/{slug}/" + ("" if section == "home" else f"{section}/")
        route_urls.add(route)
        path = DIST / slug / ("" if section == "home" else section) / "index.html"
        if not path.is_file():
            fail(f"Missing published locale route: {path.relative_to(DIST)}")
            continue
        source = path.read_text(encoding="utf-8")
        parser = DocumentParser()
        parser.feed(source)
        if parser.canonical != route:
            fail(f"Wrong locale canonical for {path.relative_to(DIST)}")
        expected = {code: f"{BASE}/{code.lower()}/" + ("" if section == "home" else f"{section}/") for code in STRATEGY["published_locales"]}
        expected["x-default"] = f"{BASE}/en-us/" + ("" if section == "home" else f"{section}/")
        if parser.hreflang != expected:
            fail(f"Incorrect or non-reciprocal locale hreflang for {path.relative_to(DIST)}")
        if f'<html lang="{locale}"' not in source:
            fail(f"Incorrect HTML language for {path.relative_to(DIST)}")
        if '<meta name="robots" content="index,follow' not in source or not parser.title:
            fail(f"Locale page lacks indexable metadata: {path.relative_to(DIST)}")

import build as site_build
for locale in STRATEGY.get("published_locales", []):
    slug = locale.lower()
    for feature in site_build.FEATURES:
        tail = f"features/{feature['id']}/"
        route = f"{BASE}/{slug}/{tail}"
        route_urls.add(route)
        path = DIST / slug / tail / "index.html"
        if not path.is_file():
            fail(f"Missing published localized feature route: {path.relative_to(DIST)}")
            continue
        parser = DocumentParser()
        parser.feed(path.read_text(encoding="utf-8"))
        expected = {code: f"{BASE}/{code.lower()}/{tail}" for code in STRATEGY["published_locales"]}
        expected["x-default"] = f"{BASE}/en-us/{tail}"
        if parser.canonical != route or parser.hreflang != expected:
            fail(f"Incorrect canonical or reciprocal hreflang for {path.relative_to(DIST)}")

for lang, tail in resource_routes():
    resource_url = f"{BASE}/{lang}/" + (f"{tail}/" if tail else "")
    route_urls.add(resource_url)
    if tail in ("", "about", "features", "download", "faq"):
        continue
    resource_path = DIST / lang / tail / "index.html"
    if not resource_path.is_file():
        fail(f"Missing resource route: {resource_path.relative_to(DIST)}")
        continue
    source = resource_path.read_text(encoding="utf-8")
    parser = DocumentParser()
    parser.feed(source)
    if parser.canonical != resource_url:
        fail(f"Wrong canonical for {resource_path.relative_to(DIST)}")
    if parser.hreflang.get("en") != f"{BASE}/en/{tail}/" or parser.hreflang.get("ar") != f"{BASE}/ar/{tail}/":
        fail(f"Wrong bilingual alternates for {resource_path.relative_to(DIST)}")
    if parser.hreflang.get("x-default") != f"{BASE}/en/{tail}/":
        fail(f"Wrong x-default alternate for {resource_path.relative_to(DIST)}")
    if source.count("<h1") != 1 or not parser.h1:
        fail(f"Resource page must contain exactly one H1: {resource_path.relative_to(DIST)}")
    if '<a class="skip-link" href="#main-content">' not in source or '<main id="main-content">' not in source:
        fail(f"Resource page is missing accessibility landmarks: {resource_path.relative_to(DIST)}")
    for image in parser.all_images:
        if not image.get("alt", "").strip() or not image.get("width") or not image.get("height"):
            fail(f"Resource image missing alt text or dimensions: {resource_path.relative_to(DIST)}")
    if '"@type": "Organization"' not in source:
        fail(f"Resource page missing Organization JSON-LD: {resource_path.relative_to(DIST)}")
    if 'name="description"' not in source or 'name="robots" content="index,follow' not in source:
        fail(f"Resource page missing SEO metadata: {resource_path.relative_to(DIST)}")



# Every page that exposes the market-language selector must use the same eight real flag images.
expected_flag_codes = set(STRATEGY.get("published_locales", []))
for html_path in DIST.rglob("*.html"):
    source = html_path.read_text(encoding="utf-8")
    if 'class="locale-switch"' not in source:
        continue
    flag_links = re.findall(
        r'<a class="locale-flag" lang="([^"]+)"[^>]*>(.*?)</a>',
        source,
        re.DOTALL,
    )
    observed_codes = {code for code, _ in flag_links}
    if len(flag_links) != len(expected_flag_codes) or observed_codes != expected_flag_codes:
        fail(f"Language selector must contain exactly the eight published locale flags: {html_path.relative_to(DIST)}")
        continue
    for code, markup in flag_links:
        if not re.search(
            r'<img src="https://flagcdn\.com/w80/[a-z]{2}\.png" alt="[^"]+ flag" width="40" height="30"',
            markup,
        ):
            fail(f"Language selector uses a non-image or inaccessible flag for {code}: {html_path.relative_to(DIST)}")

# Published market resource hubs: these four routes must exist in every live locale.
RESOURCE_HUBS = ("tips", "blog", "guide", "comparison")
for locale in STRATEGY.get("published_locales", []):
    slug = locale.lower()
    expected_hreflang = {
        code: f"{BASE}/{code.lower()}/" + "{tail}/"
        for code in STRATEGY["published_locales"]
    }
    for tail in RESOURCE_HUBS:
        route = f"{BASE}/{slug}/{tail}/"
        route_urls.add(route)
        path = DIST / slug / tail / "index.html"
        if not path.is_file():
            fail(f"Missing localized resource hub: {path.relative_to(DIST)}")
            continue
        source = path.read_text(encoding="utf-8")
        parser = DocumentParser()
        parser.feed(source)
        expected = {code: f"{BASE}/{code.lower()}/{tail}/" for code in STRATEGY["published_locales"]}
        expected["x-default"] = f"{BASE}/en-us/{tail}/"
        if parser.canonical != route or parser.hreflang != expected:
            fail(f"Incorrect canonical or reciprocal hreflang for {path.relative_to(DIST)}")
        if f'<html lang="{locale}"' not in source:
            fail(f"Incorrect HTML language for {path.relative_to(DIST)}")
        if source.count("<h1") != 1 or not parser.h1:
            fail(f"Localized resource hub must contain exactly one H1: {path.relative_to(DIST)}")
        if 'name="description"' not in source or 'name="robots" content="index,follow' not in source:
            fail(f"Localized resource hub is missing SEO metadata: {path.relative_to(DIST)}")
        if '<a class="skip-link" href="#main-content">' not in source or '<main id="main-content">' not in source:
            fail(f"Localized resource hub is missing accessibility landmarks: {path.relative_to(DIST)}")
        for href in parser.links:
            if href.startswith(("mailto:", "tel:", "#")):
                continue
            parsed = urlparse(href)
            if parsed.scheme in ("http", "https"):
                if parsed.netloc != urlparse(BASE).netloc:
                    continue
                base_path = urlparse(BASE).path.rstrip("/")
                if parsed.path != base_path and not parsed.path.startswith(base_path + "/"):
                    fail(f"Localized resource link escapes project base path: {href}")
                    continue
                relative = parsed.path[len(base_path):].lstrip("/")
            else:
                fail(f"Unsupported localized resource link: {href}")
                continue
            target = DIST / relative
            if relative.endswith("/") or not target.suffix:
                target = target / "index.html"
            if not target.is_file():
                fail(f"Broken localized resource link {href} in {path.relative_to(DIST)}")

root_parser = DocumentParser()
if (DIST / "index.html").is_file():
    root_html = (DIST / "index.html").read_text(encoding="utf-8")
    root_parser.feed(root_html)
    target = f"{BASE}/en-us/about/"
    if root_parser.canonical != target:
        fail("Root redirect canonical must point to the selected English About homepage")
    if 'name="google-site-verification"' not in root_html:
        fail("Google Search Console verification meta tag missing from root redirect")
    if f'<meta http-equiv="refresh" content="0; url={target}">' not in root_html:
        fail("Root page must immediately redirect to the selected About homepage")
    if f'window.location.replace("{target}")' not in root_html:
        fail("Root redirect JavaScript fallback is missing")
    if 'name="robots" content="noindex,follow"' not in root_html:
        fail("Root redirect must not be indexed as a duplicate page")
    if "Choose your language" in root_html or "اختر لغتك" in root_html:
        fail("Obsolete language gateway content remains on the root page")

try:
    sitemap_root = ET.parse(DIST / "sitemap.xml").getroot()
    if sitemap_root.tag != f"{NS}urlset":
        fail("Sitemap root must be the standard XML urlset element")
    sitemap_nodes = sitemap_root.findall(f"{NS}url")
    sitemap_urls = []
    xhtml_ns = "{http://www.w3.org/1999/xhtml}"
    for node in sitemap_nodes:
        loc = node.find(f"{NS}loc")
        if loc is None or not loc.text:
            fail("Sitemap contains a URL entry without a loc value")
            continue
        sitemap_urls.append(loc.text.strip())
        alternates = {
            item.get("hreflang"): item.get("href")
            for item in node.findall(f"{xhtml_ns}link")
            if item.get("rel") == "alternate"
        }
        if loc.text.strip() == f"{BASE}/":
            expected_alternates = {
                **{code: f"{BASE}/{code.lower()}/" for code in STRATEGY["published_locales"]},
                "x-default": f"{BASE}/",
            }
        else:
            parsed_loc = urlparse(loc.text.strip())
            relative_path = parsed_loc.path[len(urlparse(BASE).path.rstrip("/")):].strip("/")
            relative_parts = relative_path.split("/")
            published_slugs = {code.lower() for code in STRATEGY["published_locales"]}
            if relative_parts[0] in published_slugs:
                tail = "/".join(relative_parts[1:])
                suffix = f"{tail}/" if tail else ""
                expected_alternates = {
                    code: f"{BASE}/{code.lower()}/{suffix}"
                    for code in STRATEGY["published_locales"]
                }
                expected_alternates["x-default"] = f"{BASE}/en-us/{suffix}"
            else:
                tail = "/".join(relative_parts[1:])
                expected_alternates = {
                    "en": f"{BASE}/en/" + (f"{tail}/" if tail else ""),
                    "ar": f"{BASE}/ar/" + (f"{tail}/" if tail else ""),
                    "x-default": f"{BASE}/en/" + (f"{tail}/" if tail else ""),
                }
        if alternates != expected_alternates:
            fail(f"Incorrect hreflang sitemap alternates for {loc.text.strip()}")
    if len(sitemap_urls) != len(route_urls):
        fail(f"Sitemap should contain {len(route_urls)} routes, found {len(sitemap_urls)}")
    if len(set(sitemap_urls)) != len(sitemap_urls):
        fail("Sitemap contains duplicate URLs")
    if set(sitemap_urls) != route_urls:
        fail("Sitemap URLs do not match the generated site routes")
    for sitemap_url in sitemap_urls:
        parsed_url = urlparse(sitemap_url)
        if parsed_url.scheme != "https" or parsed_url.netloc != urlparse(BASE).netloc:
            fail(f"Sitemap contains a non-canonical host or non-HTTPS URL: {sitemap_url}")
        if parsed_url.query or parsed_url.fragment:
            fail(f"Sitemap contains a URL with query or fragment: {sitemap_url}")
except Exception as exc:
    fail(f"Invalid sitemap XML: {exc}")

try:
    text_sitemap = (DIST / "sitemap.txt").read_text(encoding="utf-8")
    text_urls = [line.strip() for line in text_sitemap.splitlines() if line.strip()]
    if len(text_urls) != len(route_urls):
        fail(f"Text sitemap should contain {len(route_urls)} routes, found {len(text_urls)}")
    if len(set(text_urls)) != len(text_urls):
        fail("Text sitemap contains duplicate URLs")
    if set(text_urls) != route_urls:
        fail("Text sitemap URLs do not match the generated site routes")
    for sitemap_url in text_urls:
        parsed_url = urlparse(sitemap_url)
        if parsed_url.scheme != "https" or parsed_url.netloc != urlparse(BASE).netloc:
            fail(f"Text sitemap contains a non-canonical host or non-HTTPS URL: {sitemap_url}")
        if parsed_url.query or parsed_url.fragment:
            fail(f"Text sitemap contains a URL with query or fragment: {sitemap_url}")
except Exception as exc:
    fail(f"Invalid text sitemap: {exc}")

robots = (DIST / "robots.txt").read_text(encoding="utf-8") if (DIST / "robots.txt").is_file() else ""
robots_lines = [line.strip() for line in robots.splitlines() if line.strip()]
if "User-agent: *" not in robots_lines or "Allow: /" not in robots_lines:
    fail("robots.txt must allow crawling for all user agents")
sitemap_directives = [line for line in robots_lines if line.lower().startswith("sitemap:")]
if sitemap_directives != [f"Sitemap: {BASE}/sitemap.xml", f"Sitemap: {BASE}/sitemap.txt"]:
    fail("robots.txt must reference both canonical XML and text sitemaps in order")

if APP["package_id"] not in APP["google_play_url"]:
    fail("Package ID mismatch in Google Play URL")
if len(SCREENSHOTS) != 5 or any(urlparse(item.get("src", "")).hostname != "play-lh.googleusercontent.com" for item in SCREENSHOTS):
    fail("Gallery must use the five official Google Play screenshot assets")

if ERRORS:
    print("\n".join(ERRORS))
    sys.exit(1)
print(f"Validated {len(route_urls)} routes, bilingual resources, navigation targets, canonical/hreflang pairs, root verification and sitemap.")
