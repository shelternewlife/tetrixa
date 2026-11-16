import json
import pathlib
import re
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
STRATEGY=json.loads((ROOT/"content/market-strategy.json").read_text(encoding="utf-8"))
class MarketStrategyTests(unittest.TestCase):
    def test_north_america_is_first_priority(self):
        markets={x["country_code"]:x for x in STRATEGY["markets"]}
        self.assertEqual(markets["US"]["priority"],1); self.assertEqual(markets["CA"]["priority"],1)
        self.assertEqual(markets["US"]["locales"],["en-US"])
        self.assertEqual(set(markets["CA"]["locales"]),{"en-CA","fr-CA"})
    def test_european_markets_are_secondary(self):
        markets=[x for x in STRATEGY["markets"] if x["priority"]==2]
        self.assertGreaterEqual(len(markets),45)
        self.assertEqual(len({x["country_code"] for x in markets}),len(markets))
        self.assertTrue(all(x["status"] in ("planned","initial") for x in markets))
        self.assertTrue(all(x["locales"] for x in markets))
    def test_locale_tags_and_url_policy_are_explicit(self):
        tags=[loc for market in STRATEGY["markets"] for loc in market["locales"]]
        self.assertEqual(len(tags),len(set(tags)))
        self.assertTrue(all(re.fullmatch(r"[a-z]{2,3}-[A-Z]{2}",x) for x in tags))
        self.assertEqual(STRATEGY["url_policy"]["pattern"],"/{locale}/")
        self.assertIn("reciprocal hreflang",STRATEGY["url_policy"]["hreflang"])
    def test_keyword_clusters_match_published_locales(self):
        clusters=STRATEGY["initial_keyword_clusters"]
        self.assertEqual(set(clusters),set(STRATEGY["published_locales"]))
        for locale,data in clusters.items():
            self.assertTrue(data["primary"] and data["secondary"] and data["clusters"])
            self.assertTrue(all(x["primary"] for x in data["clusters"]))
        self.assertIn("block puzzle game",clusters["en-US"]["primary"])
        self.assertIn("Not supplied or verified",STRATEGY["measurement"]["search_volume"])
    def test_european_keyword_research_is_localized_and_unmeasured(self):
        examples=STRATEGY["europe_keyword_research"]["examples"]
        self.assertTrue({"fr-FR","de-DE","es-ES","it-IT","nl-NL","pl-PL","en-GB"}.issubset(examples))
        self.assertEqual(STRATEGY["europe_keyword_research"]["status"],"research-seeds-only")
if __name__=="__main__": unittest.main()
