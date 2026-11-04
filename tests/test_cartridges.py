"""python3 -m unittest discover -s tests"""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cartridges import (WORLDWIDE, CATALOGUE, DISPLAY_ALIASES, PRIMERS, PRIMER_DIAMETERS,  # noqa: E402
                        INTRODUCED, INTRODUCED_UNKNOWN, OBSOLETE, is_obsolete,
                        RARE, is_rare, tags,
                        ORIGIN, COUNTRIES, origin,
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
        self.assertIn("gp90", by_name["5.6 mm GP 90"]["aliases"], "GP 90 means the 5.6 mm Stgw 90 round")
        self.assertEqual(by_name["12/70"]["kind"], SHOT)

    def test_gp90_uses_the_short_swiss_army_name(self):
        # Swiss Army: «5,6 mm Gewehrpatrone 90», short «5,6 mm GP 90».
        by_name = {s["name"]: s for s in ALL}
        self.assertNotIn("5.6 mm GP 90 (Swiss)", by_name)
        self.assertIn("gewehrpatrone 90", by_name["5.6 mm GP 90"]["aliases"])

    def test_cip_sourced_rounds_keep_the_sheet_values(self):
        # C.I.P. TDCC maximum cartridge: shoulder is P2 (not H1), shoulder starts at L1.
        by_name = {s["name"]: s for s in ALL}
        sheet = {".450 Rigby": (14.99, 14.96, 14.5, 12.38, 73.5, 59.5, 95.25, 11.66),
                 ".375 CheyTac": (16.25, 16.18, 15.22, 10.31, 76.91, 62.28, 113.4, 9.52)}
        keys = ("rim", "base", "shoulder", "neck", "case", "sh_at", "oal", "bullet")
        for name, values in sheet.items():
            self.assertEqual(tuple(by_name[name][k] for k in keys), values, name)
            self.assertGreater(by_name[name]["shoulder"], by_name[name]["neck"], name)
            self.assertTrue(is_rare(name), name)

    def test_crimped_blank(self):
        by_name = {s["name"]: s for s in ALL}
        b = by_name[".22 Blank (6.8/11)"]
        self.assertEqual(b["kind"], RIMFIRE)
        self.assertEqual((b["rim"], b["case"], b["oal"]), (6.8, 11.0, 11.0))
        self.assertEqual(b["base"], by_name[".22 Short"]["base"], "same .22 case body")
        self.assertIn("platzpatrone", b["aliases"])
        self.assertFalse(is_obsolete(b["name"]))

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

    def test_black_powder_category_holds_only_black_powder_era_rounds(self):
        # Smokeless powder arrived with the 8 mm Lebel in 1886.
        for cat, items in CATALOGUE:
            if cat != "Schwarzpulver":
                continue
            for s in items:
                year = INTRODUCED.get(s["name"], (None,))[0]
                if year is not None:
                    self.assertLessEqual(year, 1886, s["name"])
        langwaffe = {s["name"] for cat, items in CATALOGUE if cat == "Langwaffe" for s in items}
        for name in (".338 Norma Magnum", "12.7x108 mm", "7.65x53 mm Argentine"):
            self.assertIn(name, langwaffe)

    def test_obsolete_calibres_are_known(self):
        self.assertLessEqual(OBSOLETE, NAMES)
        self.assertTrue(is_obsolete("7.5x53.5 mm Swiss (GP 1890)"))
        self.assertFalse(is_obsolete("7.5x55 mm Swiss (GP 11)"))
        self.assertFalse(is_obsolete("9x19 mm"))

    def test_rare_calibres_are_known(self):
        self.assertTrue(RARE)
        self.assertLessEqual(RARE, NAMES)
        self.assertTrue(is_rare("11x59 mm R Gras"))
        self.assertFalse(is_rare("7.5 mm Swiss Ordnance 1882"))
        self.assertFalse(is_rare("7.5x55 mm Swiss (GP 11)"))

    def test_rare_does_not_require_obsolete(self):
        self.assertTrue(RARE & OBSOLETE)
        self.assertTrue(RARE - OBSOLETE)
        self.assertTrue(OBSOLETE - RARE)

    def test_tags(self):
        self.assertEqual(tags("7.5x55 mm Swiss (GP 11)"), [])
        self.assertEqual(tags("7.5 mm Swiss Ordnance 1882"), ["obsolete"])
        self.assertEqual(tags(".505 Gibbs"), ["rare"])
        self.assertEqual(tags("11x59 mm R Gras"), ["obsolete", "rare"])
    def test_origins_name_known_calibres_and_countries(self):
        self.assertLessEqual(set(ORIGIN), NAMES)
        self.assertLessEqual(set(ORIGIN.values()), set(COUNTRIES))
        self.assertEqual(set(ORIGIN.values()), set(COUNTRIES))  # no unused country
        for code, (name, flag) in COUNTRIES.items():
            self.assertTrue(name)
            self.assertTrue(flag is None or len(flag) == 2 or code == WORLDWIDE, code)

    def test_known_origins(self):
        for name in ("5.6 mm GP 90", "7.5x55 mm Swiss (GP 11)", "7.5x53.5 mm Swiss (GP 1890)",
                     "7.5 mm Swiss Ordnance 1882", "7.65 mm Parabellum"):
            self.assertEqual(ORIGIN[name], "CH")
        self.assertEqual(origin("7.62x39 mm"), ("SU", "Soviet Union", None))
        self.assertEqual(origin("7.62x54 mm R"), ("RUE", "Russian Empire", None))
        self.assertNotIn("RU", COUNTRIES)  # RU is today's Russia, not the Russian Empire
        self.assertEqual(origin("5.6 mm GP 90"), ("CH", "Switzerland", "🇨🇭"))
        for worldwide in ("9x19 mm", ".22 LR", ".308 Winchester", "5.56x45 mm NATO", ".45 ACP", "12/70"):
            self.assertEqual(origin(worldwide), ("WW", "Worldwide", "🌐"), worldwide)
        self.assertEqual(ORIGIN["7.62x39 mm"], "SU")  # a clear country wins over worldwide use
        self.assertIsNone(origin(".30 Nosler"))  # neither a clear country nor universal

    def test_swiss_service_revolver_rounds_are_obsolete(self):
        for name in ("7.5 mm Swiss Ordnance 1882", "10.4 mm Swiss Ordnance 1878"):
            self.assertIn(name, NAMES)
            self.assertTrue(is_obsolete(name), name)
        self.assertEqual(INTRODUCED["10.4 mm Swiss Ordnance 1878"][0], 1878)


if __name__ == "__main__":
    unittest.main()
