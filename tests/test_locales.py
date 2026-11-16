import json
import pathlib
import subprocess
import sys
import unittest
from html.parser import HTMLParser

ROOT=pathlib.Path(__file__).resolve().parents[1]; DIST=ROOT/"dist"
APP=json.loads((ROOT/"content/app.json").read_text(encoding="utf-8"))
STRATEGY=json.loads((ROOT/"content/market-strategy.json").read_text(encoding="utf-8"))
LOCALES=json.loads((ROOT/"content/locales.json").read_text(encoding="utf-8"))
BASE=APP["website_url"].rstrip("/")

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.canonical=None; self.alternates={}; self.title=""; self.description=None; self.in_title=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="title": self.in_title=True
        if tag=="meta" and a.get("name")=="description": self.description=a.get("content")
        if tag=="link" and a.get("rel")=="canonical": self.canonical=a.get("href")
        if tag=="link" and a.get("rel")=="alternate": self.alternates[a.get("hreflang")]=a.get("href")
    def handle_endtag(self,tag):
        if tag=="title": self.in_title=False
    def handle_data(self,data):
        if self.in_title: self.title+=data

class LocaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable,str(ROOT/"scripts/build.py")],check=True)
        subprocess.run([sys.executable,str(ROOT/"scripts/validate.py")],check=True)

    def test_only_complete_published_locales_are_generated(self):
        self.assertEqual(set(LOCALES),set(STRATEGY["published_locales"]))
        for locale in STRATEGY["published_locales"]:
            self.assertTrue((DIST/locale.lower()/"index.html").is_file())
        for locale in ("nl-nl","pl-pl","en-gb"):
            self.assertFalse((DIST/locale).exists())

    def test_titles_descriptions_canonical_and_hreflang_are_valid(self):
        for locale in STRATEGY["published_locales"]:
            slug=locale.lower()
            for section in ("","about","features","download","faq"):
                path=DIST/slug/(section or "")/"index.html"
                parser=Page(); parser.feed(path.read_text(encoding="utf-8"))
                key=section or "home"; bundle=LOCALES[locale]
                self.assertEqual(parser.title,bundle["titles"][key])
                self.assertEqual(parser.description,bundle["descriptions"][key])
                self.assertLessEqual(len(parser.title),60)
                self.assertLessEqual(len(parser.description),160)
                suffix="" if not section else section+"/"
                self.assertEqual(parser.canonical,f"{BASE}/{slug}/{suffix}")
                self.assertEqual(parser.alternates,{**{c:f"{BASE}/{c.lower()}/{suffix}" for c in STRATEGY["published_locales"]},"x-default":f"{BASE}/en-us/{suffix}"})

    def test_market_keywords_describe_block_puzzle_game(self):
        clusters=STRATEGY["initial_keyword_clusters"]
        self.assertEqual(set(clusters),set(STRATEGY["published_locales"]))
        self.assertIn("block puzzle game",clusters["en-US"]["primary"])
        self.assertIn("block puzzle game Canada",clusters["en-CA"]["primary"])
        self.assertIn("jeu de puzzle de blocs",clusters["fr-CA"]["primary"])
        for locale,config in clusters.items():
            self.assertTrue(config["primary"] and config["secondary"] and config["clusters"])
            metadata=" ".join(LOCALES[locale]["titles"].values())+" "+" ".join(LOCALES[locale]["descriptions"].values())
            for term in config["excluded_terms"]:
                self.assertNotIn(term.casefold(),metadata.casefold())

    def test_french_pages_use_french_game_copy(self):
        for locale in ("fr-CA","fr-FR"):
            source=(DIST/locale.lower()/"index.html").read_text(encoding="utf-8")
            self.assertIn(f'<html lang="{locale}"',source)
            self.assertIn("Tetrixa",source)
            self.assertIn("Jeu",source)
            self.assertIn("Questions fréquentes",(DIST/locale.lower()/"faq"/"index.html").read_text(encoding="utf-8"))
            self.assertNotIn("Job Connect",source)

    def test_all_locales_reference_tetrixa_and_not_the_previous_app(self):
        for locale in STRATEGY["published_locales"]:
            source=(DIST/locale.lower()/"index.html").read_text(encoding="utf-8")
            self.assertIn("Tetrixa",source)
            self.assertNotIn("Job Connect",source)
            self.assertNotIn("job search",source.casefold())

if __name__=="__main__": unittest.main()
