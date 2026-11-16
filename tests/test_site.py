import json
import pathlib
import subprocess
import sys
import unittest
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
APP = json.loads((ROOT / "content/app.json").read_text(encoding="utf-8"))
BASE = APP["website_url"].rstrip("/")
STRATEGY = json.loads((ROOT / "content/market-strategy.json").read_text(encoding="utf-8"))
FEATURES = json.loads((ROOT / "content/features.json").read_text(encoding="utf-8"))
FAQ = json.loads((ROOT / "content/faq.json").read_text(encoding="utf-8"))
SHOTS = json.loads((ROOT / "content/screenshots.json").read_text(encoding="utf-8"))

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.h1 = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "img":
            self.images.append(attrs)
        if tag == "h1":
            self.h1 += 1

class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "scripts/build.py")], check=True)
        subprocess.run([sys.executable, str(ROOT / "scripts/validate.py")], check=True)

    def test_tetrixa_identity_and_official_store_link(self):
        self.assertEqual(APP["name"], "Tetrixa")
        self.assertEqual(APP["package_id"], "com.game.tetrixa.devimpact")
        self.assertIn(APP["package_id"], APP["google_play_url"])
        self.assertEqual(APP["website_url"], BASE + "/")
        self.assertEqual(APP["category"], "GameApplication")

    def test_core_pages_exist_for_english_and_arabic(self):
        for lang in ("en", "ar"):
            for section in ("", "about", "features", "download", "faq"):
                path = DIST / lang / (section or "") / "index.html"
                self.assertTrue(path.is_file(), f"Missing {lang}/{section}")
                source = path.read_text(encoding="utf-8")
                self.assertEqual(source.count("<h1"), 1)
                self.assertIn(APP["google_play_url"], source)

    def test_root_redirects_to_us_english_about_page(self):
        source = (DIST / "index.html").read_text(encoding="utf-8")
        target = f"{BASE}/en-us/about/"
        self.assertIn(f'<link rel="canonical" href="{target}">', source)
        self.assertIn(f'<meta http-equiv="refresh" content="0; url={target}">', source)
        self.assertIn(f'window.location.replace("{target}")', source)
        self.assertIn('name="google-site-verification"', source)

    def test_all_five_real_store_screenshots_are_used(self):
        self.assertEqual(len(SHOTS), 5)
        self.assertTrue(all(x["src"].startswith("https://play-lh.googleusercontent.com/") for x in SHOTS))
        for lang in ("en", "ar"):
            source = (DIST / lang / "index.html").read_text(encoding="utf-8")
            for shot in SHOTS:
                self.assertIn(shot["src"], source)
            self.assertIn('id="screenshots"', source)

    def test_features_and_faq_match_the_game(self):
        self.assertEqual(len(FEATURES), 5)
        self.assertEqual(len(FAQ), 8)
        text = " ".join(x["title"]["en"] + " " + x["description"]["en"] for x in FEATURES)
        self.assertIn("block", text.lower())
        self.assertIn("offline", text.lower())
        for lang in ("en", "ar"):
            source = (DIST / lang / "features" / "index.html").read_text(encoding="utf-8")
            for feature in FEATURES:
                self.assertIn(feature["title"][lang], source)
            faq = (DIST / lang / "faq" / "index.html").read_text(encoding="utf-8")
            for item in FAQ:
                self.assertIn(item["q"][lang], faq)
                self.assertIn(item["a"][lang], faq)

    def test_feature_detail_pages_exist(self):
        for lang in ("en", "ar"):
            for feature in FEATURES:
                path = DIST / lang / "features" / feature["id"] / "index.html"
                self.assertTrue(path.is_file())
                source = path.read_text(encoding="utf-8")
                self.assertIn(feature["title"][lang], source)
                self.assertIn('"@type": "Organization"', source)

    def test_gameplay_resource_pages_are_not_career_content(self):
        for lang in ("en", "ar"):
            for tail in ("blog", "guide", "tips", "comparison"):
                path = DIST / lang / tail / "index.html"
                self.assertTrue(path.is_file())
                source = path.read_text(encoding="utf-8")
                self.assertIn("TETRIXA", source)
                self.assertNotRegex(source.lower(), r"job connect|job search|career resources|employment opportunities")

    def test_all_images_have_alt_text_and_dimensions(self):
        for path in DIST.rglob("*.html"):
            parser = Page()
            parser.feed(path.read_text(encoding="utf-8"))
            for image in parser.images:
                self.assertTrue(image.get("alt", "").strip(), str(path))
                self.assertTrue(image.get("width", "").isdigit(), str(path))
                self.assertTrue(image.get("height", "").isdigit(), str(path))

    def test_all_google_play_ctas_use_the_tetrixa_listing(self):
        for path in DIST.rglob("*.html"):
            source = path.read_text(encoding="utf-8")
            if "google_play_click" in source:
                self.assertIn(APP["google_play_url"], source)
                self.assertNotIn("com.jobsearch.jobconnect", source)

    def test_no_legacy_product_identity_remains_in_generated_site(self):
        forbidden = ("Job Connect", "jobsearch.jobconnect", "tobemotif-app-discovery", "job search app", "career resources")
        for path in DIST.rglob("*"):
            if path.is_file() and path.suffix in (".html", ".txt", ".xml", ".json", ".css"):
                data = path.read_text(encoding="utf-8", errors="ignore").casefold()
                for phrase in forbidden:
                    self.assertNotIn(phrase.casefold(), data, f"{phrase} remains in {path}")

if __name__ == "__main__":
    unittest.main()
