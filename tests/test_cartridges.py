"""python3 -m unittest discover -s tests"""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cartridges import (CATALOGUE, DISPLAY_ALIASES, PRIMERS, PRIMER_DIAMETERS,  # noqa: E402
                        INTRODUCED, INTRODUCED_UNKNOWN,
                        RIMFIRE, BALL, MINIE, PELLET, SHOT)

ALL = [s for _, items in CATALOGUE for s in items]
NAMES = {s["name"] for s in ALL}
CATEGORIES = {"Randfeuer", "Kurzwaffe", "Langwaffe", "Schwarzpulver", "Flinte", "Luftdruck"}


class CatalogueTests(unittest.TestCase):
    def test_names_are_unique(self):
        self.assertEqual(len(NAMES), len(ALL))

    def test_categories_are_the_ones_the_apps_know(self):
        self.assertEqual({c for c, _ in CATALOGUE}, CATEGORIES)

    def test_search_aliases_are_unique_across_calibres(self):
        seen = {}
        for s in ALL:
            for a in s["aliases"]:
                self.assertNotIn(a, seen, f"{a!r} used by {seen.get(a)} and {s['name']}")
                seen[a] = s["name"]

    def test_dimensions_are_plausible(self):
        for s in ALL:
            with self.subTest(s["name"]):
                self.assertGreater(s["oal"], 0)
                self.assertGreaterEqual(s["oal"] + 0.01, s["case"])
                self.assertGreater(s["rim"], 0)
                self.assertGreater(s["bullet"], 0)
                if s["shoulder"]:
                    self.assertLessEqual(s["neck"], s["shoulder"])
                    self.assertLess(s["sh_at"], s["case"])

    def test_display_aliases_name_known_calibres(self):
        self.assertLessEqual(set(DISPLAY_ALIASES), NAMES)
        for name, aliases in DISPLAY_ALIASES.items():
            self.assertLessEqual(len(aliases), 2, name)

    def test_every_centrefire_calibre_has_a_primer(self):
        centrefire = {s["name"] for s in ALL if s["kind"] not in (RIMFIRE, BALL, MINIE, PELLET)}
        self.assertEqual(set(PRIMERS), centrefire)
        self.assertLessEqual(set(PRIMERS.values()), set(PRIMER_DIAMETERS))

    def test_swiss_service_rounds(self):
        by_name = {s["name"]: s for s in ALL}
        self.assertIn("gp11", by_name["7.5x55 mm Swiss (GP 11)"]["aliases"])
        self.assertIn("gp1890", by_name["7.5x53.5 mm Swiss (GP 1890)"]["aliases"])
        self.assertIn("gp90", by_name["5.6 mm GP 90 (Swiss)"]["aliases"], "GP 90 means the 5.6 mm Stgw 90 round")
        self.assertEqual(by_name["12/70"]["kind"], SHOT)

    def test_every_calibre_has_an_introduction_year_or_a_reason(self):
        self.assertEqual(set(INTRODUCED) | set(INTRODUCED_UNKNOWN), NAMES)
        self.assertFalse(set(INTRODUCED) & set(INTRODUCED_UNKNOWN))
        for name, reason in INTRODUCED_UNKNOWN.items():
            self.assertTrue(reason.strip(), name)

    def test_introduction_years_are_plausible_and_sourced(self):
        for name, (year, source) in INTRODUCED.items():
            with self.subTest(name):
                self.assertIsInstance(year, int)
                self.assertGreaterEqual(year, 1800)
                self.assertLessEqual(year, 2026)
                self.assertTrue(source.startswith("https://"), source)

    def test_known_introduction_years(self):
        self.assertEqual(INTRODUCED["7.5x55 mm Swiss (GP 11)"][0], 1911)
        self.assertEqual(INTRODUCED["9x19 mm"][0], 1902)
        self.assertEqual(INTRODUCED[".308 Winchester"][0], 1952)
        self.assertLess(INTRODUCED[".308 Winchester"][0], INTRODUCED["7.62x51 mm NATO"][0])


if __name__ == "__main__":
    unittest.main()
