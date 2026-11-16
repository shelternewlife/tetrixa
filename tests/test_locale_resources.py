import json
import pathlib
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT=pathlib.Path(__file__).resolve().parents[1]; DIST=ROOT/"dist"
APP=json.loads((ROOT/"content/app.json").read_text(encoding="utf-8"))
STRATEGY=json.loads((ROOT/"content/market-strategy.json").read_text(encoding="utf-8"))
LOCALES=tuple(STRATEGY["published_locales"]); BASE=APP["website_url"].rstrip("/")
HUBS=("tips","blog","guide","comparison")
NS="{http://www.sitemaps.org/schemas/sitemap/0.9}"; XHTML="{http://www.w3.org/1999/xhtml}"

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.canonical=None; self.alternates={}; self.title=""; self.h1=0; self.in_title=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="a" and a.get("href"): self.links.append(a["href"])
        if tag=="link" and a.get("rel")=="canonical": self.canonical=a.get("href")
        if tag=="link" and a.get("rel")=="alternate": self.alternates[a.get("hreflang")]=a.get("href")
        if tag=="title": self.in_title=True
        if tag=="h1": self.h1+=1
    def handle_endtag(self,tag):
        if tag=="title": self.in_title=False
    def handle_data(self,data):
        if self.in_title: self.title+=data

class ResourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable,str(ROOT/"scripts/build.py")],check=True)
        subprocess.run([sys.executable,str(ROOT/"scripts/validate.py")],check=True)

    def test_four_gameplay_hubs_exist_for_each_locale(self):
        for locale in LOCALES:
            for tail in HUBS:
                path=DIST/locale.lower()/tail/"index.html"
                self.assertTrue(path.is_file())
                source=path.read_text(encoding="utf-8"); page=Page(); page.feed(source)
                self.assertEqual(page.canonical,f"{BASE}/{locale.lower()}/{tail}/")
                self.assertEqual(page.h1,1)
                self.assertIn(f'<html lang="{locale}"',source)
                self.assertIn("TETRIXA",source)
                self.assertNotIn("Job Connect",source)
                self.assertEqual(page.alternates,{**{c:f"{BASE}/{c.lower()}/{tail}/" for c in LOCALES},"x-default":f"{BASE}/en-us/{tail}/"})

    def test_internal_links_resolve_to_generated_pages(self):
        for locale in LOCALES:
            for tail in HUBS:
                page=Page(); page.feed((DIST/locale.lower()/tail/"index.html").read_text(encoding="utf-8"))
                for href in page.links:
                    if href.startswith(("mailto:","tel:","#")) or (href.startswith("https://") and not href.startswith(BASE+"/")): continue
                    self.assertTrue(href.startswith(BASE+"/"),href)
                    relative=href[len(BASE)+1:]; target=DIST/relative
                    if relative.endswith("/") or not target.suffix: target=target/"index.html"
                    self.assertTrue(target.is_file(),f"Broken link: {href}")

    def test_resource_navigation_flags_and_social_links_are_retained(self):
        import re
        for locale in LOCALES:
            for tail in HUBS:
                source=(DIST/locale.lower()/tail/"index.html").read_text(encoding="utf-8")
                groups=re.findall(r'<details class="nav-menu" data-nav-group="([^"]+)">(.*?)</details>',source,re.DOTALL)
                self.assertEqual([x[0] for x in groups],["primary","resources"])
                for _,markup in groups: self.assertEqual(len(re.findall(r'<a data-nav-item="[^"]+"',markup)),4)
                flags=re.findall(r'<a class="locale-flag" lang="([^"]+)"[^>]*>(.*?)</a>',source,re.DOTALL)
                self.assertEqual({x[0] for x in flags},set(LOCALES))
                self.assertEqual(len(flags),8)
                self.assertEqual(source.count('<div class="social-links" aria-label="Social media">'),1)
                self.assertIn("https://www.facebook.com/",source)
                self.assertIn("https://x.com/",source)
                self.assertIn("https://www.tiktok.com/",source)
                self.assertIn("https://www.instagram.com/",source)

    def test_resource_hubs_are_in_both_sitemaps(self):
        expected={f"{BASE}/{locale.lower()}/{tail}/" for locale in LOCALES for tail in HUBS}
        root=ET.parse(DIST/"sitemap.xml").getroot()
        xml_urls={n.findtext(f"{NS}loc") for n in root.findall(f"{NS}url")}
        txt_urls=set((DIST/"sitemap.txt").read_text(encoding="utf-8").splitlines())
        self.assertTrue(expected.issubset(xml_urls)); self.assertTrue(expected.issubset(txt_urls))
        self.assertEqual(len(xml_urls),len(root.findall(f"{NS}url")))
        for node in root.findall(f"{NS}url"):
            loc=node.findtext(f"{NS}loc")
            if loc in expected:
                tail=loc.rsplit("/",2)[-2]
                alternates={n.get("hreflang"):n.get("href") for n in node.findall(f"{XHTML}link")}
                self.assertEqual(alternates,{**{c:f"{BASE}/{c.lower()}/{tail}/" for c in LOCALES},"x-default":f"{BASE}/en-us/{tail}/"})

if __name__=="__main__": unittest.main()
