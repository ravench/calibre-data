"""python3 -m unittest discover -s tests"""
import os, sys, unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cartridges import (WORLDWIDE, CATALOGUE, ALL_CATALOGUE, DISPLAY_ALIASES, PRIMERS, PRIMER_DIAMETERS, PRIMER_MM, MINIATURE,  # noqa: E402
                        PRIMER_SOURCES, PRIMER_UNVERIFIED, BERDAN_NITRO,
                        SMALL_PISTOL, SMALL_RIFLE, LARGE_RIFLE,
                        INTRODUCED, INTRODUCED_UNKNOWN, OBSOLETE, is_obsolete, SPITZER,
                        RARE, is_rare, tags,
                        ORIGIN, ORIGIN_UNDECIDED, COUNTRIES, origin, origin_candidates, is_worldwide,
                        RIMFIRE, RIMLESS, RIMMED, BALL, MINIE, PELLET, SHOT,
                        BULLETS, BULLET_INFERRED, JACKETED, LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP, HOLLOW_POINT,
                        bullet,
                        CASES, BRASS, COPPER, STEEL, NICKEL, ALUMINIUM, PAPER, HYBRID, case_material,
                        CURRENT_CASES, current_case_materials, PLASTIC, loose_material, CARTRIDGE_BULLETS, LOOSE_BULLETS, is_blank,
                        PROFILE_TODAY, LOOKALIKES, LOOKALIKE_NAMES, RIM, BORE, LENGTH, SEATING, LOAD, IGNITION, lookalikes,
                        BOOK_SOURCE, SOURCES)

ALL = [s for _, items in CATALOGUE for s in items]  # the calibres in the apps
APP_NAMES = {s["name"] for s in ALL}
NAMES = {s["name"] for _, items in ALL_CATALOGUE for s in items}  # also the catalogue-only ones
CATEGORIES = {"Randfeuer", "Kurzwaffe", "Langwaffe", "Schwarzpulver", "Flinte", "Luftdruck"}


def is_source(s):
    """A web address or a page of a book in books.toml."""
    return s.startswith("https://") or bool(BOOK_SOURCE.fullmatch(s))


class CatalogueTests(unittest.TestCase):
    def test_tables_the_apps_read_whole_name_only_app_calibres(self):
        # The generators assert these against CATALOGUE, so a catalogue-only calibre breaks them.
        for table in (DISPLAY_ALIASES, PRIMERS, PRIMER_SOURCES, PRIMER_UNVERIFIED):
            self.assertLessEqual(set(table), APP_NAMES)
        for _, names in LOOKALIKES:
            self.assertLessEqual(set(names), APP_NAMES, names)

    def test_names_are_unique(self):
        self.assertEqual(len(NAMES), sum(len(items) for _, items in ALL_CATALOGUE))

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
                if s["kind"] == SHOT:  # the hull opened by firing is longer than the loaded shell
                    self.assertGreaterEqual(s["case"], s["oal"])
                else:
                    self.assertGreaterEqual(s["oal"] + 0.01, s["case"])
                self.assertGreater(s["rim"], 0)
                self.assertGreater(s["bullet"], 0)
                if s["shoulder"]:
                    self.assertLessEqual(s["neck"], s["shoulder"])
                    self.assertLess(s["sh_at"], s["case"])

    def test_display_aliases_name_known_calibres(self):
        self.assertLessEqual(set(DISPLAY_ALIASES), APP_NAMES)
        for name, aliases in DISPLAY_ALIASES.items():
            self.assertLessEqual(len(aliases), 2, name)

    def test_every_centrefire_calibre_has_a_primer(self):
        centrefire = {s["name"] for s in ALL if s["kind"] not in (RIMFIRE, BALL, MINIE, PELLET)}
        self.assertEqual(set(PRIMERS), centrefire)
        self.assertLessEqual(set(PRIMERS.values()), set(PRIMER_DIAMETERS) | {MINIATURE})
        self.assertEqual(set(PRIMER_MM), centrefire)
        for name, size in PRIMERS.items():
            if size != MINIATURE:  # a measured diameter stays near its size
                self.assertAlmostEqual(PRIMER_MM[name], PRIMER_DIAMETERS[size], delta=0.5, msg=name)

    def test_miniature_primers_measured_on_headstamps(self):
        # Kolibri and Liliput primers are smaller than any reloading size (municion.org photos).
        self.assertEqual({n for n, s in PRIMERS.items() if s == MINIATURE},
                         {"2.7 mm Kolibri", "3 mm Kolibri", "4.25 mm Liliput"})
        self.assertEqual(PRIMER_MM["4.25 mm Liliput"], 3.0)
        for name in ("2.7 mm Kolibri", "3 mm Kolibri"):
            self.assertLess(PRIMER_MM[name], 2.5, name)

    def test_original_primers_from_headstamp_photos(self):
        for name in ("10.3x60 mm R", "11x59 mm R Gras", ".500/465 Nitro Express",
                     ".475 No. 2 Nitro Express", ".375 Flanged Nitro Express", "9.3x72 mm R"):
            self.assertEqual(PRIMERS[name], BERDAN_NITRO, name)
        self.assertEqual(PRIMER_DIAMETERS[BERDAN_NITRO], 6.45)
        for name in (".450 Adams", ".476 Enfield", ".360 No. 5 Rook"):
            self.assertEqual(PRIMERS[name], SMALL_PISTOL, name)

    def test_every_primer_is_sourced_or_marked_unverified(self):
        self.assertEqual(set(PRIMER_SOURCES) & PRIMER_UNVERIFIED, set())
        self.assertEqual(set(PRIMER_SOURCES) | PRIMER_UNVERIFIED, set(PRIMERS))
        for name, url in PRIMER_SOURCES.items():
            self.assertTrue(is_source(url), name)

    def test_checked_primer_corrections(self):
        # Primer sizes that were guessed wrong, checked against reloading data and brass makers:
        # 7.62x39, 6.8 SPC: Hodgdon (Winchester/Remington cases) and Vihtavuori (Lapua 7.62x39 cases) use large rifle.
        # .450 Bushmaster, .30 RAR: Hodgdon loads Hornady/Starline/Remington cases with small rifle primers.
        # .277 SIG Fury: Vihtavuori loads the SIG hybrid case with large rifle primers.
        # .400 Cor-Bon: Starline changed the pocket to small pistol in 12/2000; Cor-Bon recommends small pistol.
        # .22 TCM: Hodgdon loads Armscor cases with CCI 500 small pistol primers.
        expected = {"7.62x39 mm": LARGE_RIFLE, "6.8 mm Remington SPC": LARGE_RIFLE,
                    ".450 Bushmaster": SMALL_RIFLE, ".30 Remington AR": SMALL_RIFLE,
                    ".277 SIG Fury": LARGE_RIFLE, ".400 Cor-Bon": SMALL_PISTOL, ".22 TCM": SMALL_PISTOL}
        for name, primer in expected.items():
            self.assertEqual(PRIMERS[name], primer, name)

    def test_swiss_service_rounds(self):
        by_name = {s["name"]: s for s in ALL}
        self.assertIn("gp11", by_name["7.5x55 mm Swiss (GP 11)"]["aliases"])
        self.assertIn("gp1890", by_name["7.5x53.5 mm Swiss (GP 1890)"]["aliases"])
        self.assertIn("gp90", by_name["5.6 mm GP 90"]["aliases"], "GP 90 means the 5.6 mm Stgw 90 round")
        self.assertEqual(by_name["12/70"]["kind"], SHOT)

    def test_kadettenpatrone_is_its_own_round(self):
        # Raven 2026-11-08: a variant of GP 1890, but technically its own cartridge; measured on one round.
        by_name = {s["name"]: s for s in ALL}
        kp, gp = by_name["7.5 mm Kadettenpatrone"], by_name["7.5x54.5 mm Swiss (GP 90/23)"]
        measured = {"rim": 12.7, "base": 12.6, "shoulder": 11.5, "neck": 8.6, "sh_at": 45.0, "oal": 77.5, "bullet": 7.8}
        self.assertEqual({k: kp[k] for k in measured}, measured)
        self.assertEqual(kp["case"], 54.6, "measured 54.8 on a 1964 round, drawn on the GP 90/23's case")
        # A late round on the longer case of 1923: Schiesstagebuch offers the two as one chamber.
        chamber = ("kind", "rim", "base", "shoulder", "neck", "case", "sh_at", "bullet")
        self.assertEqual([kp[k] for k in chamber], [gp[k] for k in chamber])
        self.assertNotEqual(kp["profile"], by_name["7.5x53.5 mm Swiss (GP 1890)"]["profile"],
                            "a jacketed round nose, not the paper-patched bullet")
        self.assertEqual(kp["kind"], RIMLESS)
        self.assertEqual(kp["profile"], "round")
        self.assertIn("kadettenpatrone", kp["aliases"])
        self.assertEqual(DISPLAY_ALIASES["7.5 mm Kadettenpatrone"], ["Cart. 7,5 mm cadets", "Cart. 7,5 mm cadetti"])
        self.assertEqual(INTRODUCED["7.5 mm Kadettenpatrone"][0], 1897)
        self.assertEqual(ORIGIN["7.5 mm Kadettenpatrone"], "CH")
        self.assertEqual(tags("7.5 mm Kadettenpatrone"), ["obsolete", "rare"])
        self.assertEqual(bullet("7.5 mm Kadettenpatrone"), JACKETED)

    def test_gp1890_and_gp90_23_are_two_cases(self):
        # Raven 2026-11-11: his 1906 GP round measures 53.5; Poyer p. 50/54 and swissrifles.com give 53.5 for
        # the GP 90 and 90/03 and the longer case only from the GP 90/23 of 1923, a calibre of its own.
        by_name = {s["name"]: s for s in ALL}
        gp, gp23 = by_name["7.5x53.5 mm Swiss (GP 1890)"], by_name["7.5x54.5 mm Swiss (GP 90/23)"]
        self.assertEqual((gp["case"], gp["rim"], gp["base"]), (53.5, 12.5, 12.4))
        self.assertEqual((gp23["case"], gp23["rim"], gp23["base"]), (54.6, 12.7, 12.6))
        self.assertEqual(by_name["7.5x55 mm Swiss (GP 11)"]["case"], 55.6)
        self.assertIn("gp90/03", gp["aliases"], "the 90/03 only changed the primer")
        self.assertIn("gp90/23", gp23["aliases"])
        self.assertNotIn("gp90/23", gp["aliases"])
        self.assertEqual(INTRODUCED["7.5x54.5 mm Swiss (GP 90/23)"][0], 1923)

    def test_gp1890_follows_the_1892_drawing(self):
        # «Patrone, Modell 1890», Eidg. Munitionsfabrik Thun, 1 Feb 1892 (Federal Archives E27#1000/721#18612*).
        gp = next(s for s in ALL if s["name"] == "7.5x53.5 mm Swiss (GP 1890)")
        self.assertEqual((gp["case"], gp["shoulder"], gp["sh_at"], gp["neck"], gp["oal"], gp["bullet"]),
                         (53.5, 11.5, 44.5, 8.5, 77.2, 8.15))
        self.assertIn("patrone modell 1890", gp["aliases"])
        # Federal Council decisions of 1 July 1890 and 6 March 1903 (Federal Archives minutes).
        self.assertEqual(INTRODUCED["7.5x53.5 mm Swiss (GP 1890)"][0], 1890)
        self.assertIn("gewehrpatrone 1890/1903", gp["aliases"])
        self.assertEqual(bullet("7.5x54.5 mm Swiss (GP 90/23)"), JACKETED)
        self.assertEqual(lookalikes("7.5 mm Kadettenpatrone"),
                         ["7.5x53.5 mm Swiss (GP 1890)", "7.5x54.5 mm Swiss (GP 90/23)"])

    def test_swiss_army_pistol_round_names(self):
        # Raven 2026-11-08: 9 mm Para is «Pistolenpatrone 41» (Pist Pat 41) in the Swiss Army; the
        # 7.65 mm Parabellum boxes say «Pistolen-Patronen Cal. 7,65 mm».
        by_name = {s["name"]: s for s in ALL}
        self.assertIn("pist pat 41", by_name["9x19 mm"]["aliases"])
        self.assertIn("pistolenpatrone 41", by_name["9x19 mm"]["aliases"])
        self.assertIn("9 mm pist pat 41", by_name["9x19 mm"]["aliases"])
        self.assertIn("pistolenpatrone 7.65", by_name["7.65 mm Parabellum"]["aliases"])
        # Search names only: the printed names stay as they were.
        self.assertEqual(DISPLAY_ALIASES["7.65 mm Parabellum"], [".30 Luger"])
        self.assertEqual(DISPLAY_ALIASES["9x19 mm"], ["9 mm Luger", "9 mm Para"])

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

    def test_third_cip_batch_keeps_the_sheet_values(self):
        by_name = {s["name"]: s for s in ALL}
        keys = ("rim", "base", "shoulder", "neck", "case", "sh_at", "oal", "bullet")
        sheet = {  # C.I.P. TDCC maximum cartridge
            ".450 No. 2 Nitro Express": (16.76, 14.35, 13.97, 12.24, 88.9, 72.39, 109.98, 11.63),
            "10.3x60 mm R": (15.7, 13.85, 12.5, 11.26, 60.8, 40.8, 78.9, 10.54),
            "7x61 mm Sharpe & Hart": (13.5, 13.05, 11.91, 8.06, 61.0, 50.8, 83.0, 7.2),
        }
        for name, values in sheet.items():
            self.assertEqual(tuple(by_name[name][k] for k in keys), values, name)
        self.assertEqual(ORIGIN["10.3x60 mm R"], "CH")

    def test_fury_and_dbp87_keep_the_published_values(self):
        by_name = {s["name"]: s for s in ALL}
        keys = ("rim", "base", "neck", "case", "oal", "bullet")
        published = {  # Wikipedia infoboxes (.277 Fury after the SAAMI drawing)
            ".277 SIG Fury": (11.99, 11.95, 7.87, 51.18, 71.76, 7.06),
            "5.8x42 mm": (10.42, 10.4, 6.65, 42.2, 58.0, 6.0),  # bullet from the AECC drawing
        }
        for name, values in published.items():
            self.assertEqual(tuple(by_name[name][k] for k in keys), values, name)
        self.assertEqual(ORIGIN["5.8x42 mm"], "CN")
        self.assertEqual(ORIGIN[".277 SIG Fury"], "US")

    def test_rpm_family_and_hamr_keep_the_saami_values(self):
        by_name = {s["name"]: s for s in ALL}
        keys = ("rim", "base", "shoulder", "neck", "case", "sh_at", "oal", "bullet")
        self.assertEqual(tuple(by_name[".25 Weatherby RPM"][k] for k in keys),
                         (12.01, 12.7, 12.14, 7.37, 60.96, 50.48, 84.84, 6.53))
        self.assertEqual(tuple(by_name[".300 HAM'R"][k] for k in ("rim", "case", "oal")), (9.6, 41.02, 57.4))
        for name in (".25 Weatherby RPM", "6.5 Weatherby RPM", ".338 Weatherby RPM"):
            s = by_name[name]  # one case family: rebated rim under a 0.500 in head
            self.assertEqual((s["rim"], s["base"]), (12.01, 12.7), name)
        self.assertEqual(ORIGIN[".300 HAM'R"], "US")

    def test_blaser_family_keeps_the_cip_values(self):
        by_name = {s["name"]: s for s in ALL}
        keys = ("rim", "base", "shoulder", "neck", "case", "sh_at", "oal", "bullet")
        sheet = {  # C.I.P. TDCC maximum cartridge
            "7 mm Blaser Magnum": (13.59, 13.84, 13.09, 8.0, 59.7, 47.24, 80.0, 7.22),
            ".338 Blaser Magnum": (13.59, 13.84, 13.02, 9.36, 63.7, 51.51, 84.84, 8.59),
            "8.5x55 mm Blaser": (13.59, 13.84, 13.17, 9.36, 54.7, 42.38, 75.84, 8.59),
        }
        for name, values in sheet.items():
            self.assertEqual(tuple(by_name[name][k] for k in keys), values, name)
        self.assertFalse(is_rare("8.5x55 mm Blaser"))  # sold widely in German-speaking countries

    def test_swiss_rimfires_keep_the_drawing_values(self):
        s = {c["name"]: c for c in ALL}["18 mm Milbank-Amsler"]
        keys = ("rim", "base", "neck", "case", "oal", "bullet")
        self.assertEqual(tuple(s[k] for k in keys), (20.72, 18.58, 18.27, 25.54, 39.92, 18.15))
        self.assertEqual(s["kind"], RIMFIRE)
        self.assertEqual(ORIGIN["18 mm Milbank-Amsler"], "CH")
        self.assertTrue(is_obsolete("18 mm Milbank-Amsler"))
        rf72 = {c["name"]: c for c in ALL}["10.4 mm Swiss Ordnance 1872 Rimfire"]
        self.assertEqual(tuple(rf72[k] for k in keys), (12.7, 10.95, 10.85, 18.23, 30.52, 10.85))
        self.assertEqual(rf72["kind"], RIMFIRE)

    def test_9mm_pak_keeps_the_cip_blank_values(self):
        pak = {s["name"]: s for s in ALL}["9 mm P.A.K."]
        self.assertEqual((pak["rim"], pak["base"], pak["case"], pak["oal"]), (9.5, 9.5, 22.5, 22.5))
        self.assertNotEqual(pak["profile"], "crimped")  # closed inside the case, no star crimp
        self.assertEqual(pak["neck"], pak["base"])
        self.assertFalse(is_rare("9 mm P.A.K."))

    def test_32_wadcutter_is_its_own_cip_cartridge(self):
        # C.I.P. "32 S&W Long Wad Cut." (Tab. IV page 46): maximum cartridge R1, P1, H2, L3, G1; seated flush.
        by_name = {s["name"]: s for s in ALL}
        wc, swl = by_name[".32 S&W Long Wadcutter"], by_name[".32 S&W Long"]
        keys = ("kind", "rim", "base", "neck", "case", "oal", "bullet")
        self.assertEqual(tuple(wc[k] for k in keys), (RIMMED, 9.53, 8.56, 8.56, 23.27, 23.27, 8.0))
        self.assertNotEqual(wc["case"], swl["case"], "a different chamber, so not grouped with the .32 S&W Long")
        self.assertIn("32 s&w long wc", wc["aliases"])
        self.assertEqual(DISPLAY_ALIASES[".32 S&W Long Wadcutter"], [".32 S&W Long WC"])
        self.assertEqual(PRIMERS[".32 S&W Long Wadcutter"], SMALL_PISTOL)
        self.assertEqual(bullet(".32 S&W Long Wadcutter"), LEAD)
        self.assertEqual(origin_candidates(".32 S&W Long Wadcutter")[0][0], "DE")
        self.assertEqual(tags(".32 S&W Long Wadcutter"), [])

    def test_municion_specimens_keep_the_drawing_values(self):
        by_name = {s["name"]: s for s in ALL}
        keys = ("rim", "base", "neck", "case", "oal", "bullet")
        drawn = {  # AECC drawings on municion.org, mm
            "5.75 mm Velo-Dog": (7.78, 6.37, 6.25, 29.41, 35.24, 5.65),
            ".32 Long Rimfire": (9.51, 8.09, 8.09, 20.0, 30.85, 7.92),
            ".22 Extra Long": (6.95, 5.74, 5.72, 19.83, 29.89, 5.63),
            ".55 Boys": (20.3, 20.14, 15.51, 99.11, 133.64, 14.36),
            ".45-90 WCF": (15.44, 12.82, 12.22, 60.96, 82.0, 11.63),  # C.I.P. maximum
        }
        for name, values in drawn.items():
            self.assertEqual(tuple(by_name[name][k] for k in keys), values, name)
        self.assertEqual(by_name[".32 Short Rimfire"]["kind"], RIMFIRE)
        self.assertTrue(is_obsolete(".55 Boys"))
        self.assertEqual(ORIGIN["5.75 mm Velo-Dog"], "FR")

    def test_second_cip_batch_keeps_the_sheet_values(self):
        by_name = {s["name"]: s for s in ALL}
        keys = ("rim", "base", "shoulder", "neck", "case", "sh_at", "oal", "bullet")
        sheet = {  # C.I.P. TDCC maximum cartridge
            "8x75 mm RS": (13.35, 11.9, 10.4, 9.08, 74.6, 66.2, 96.0, 8.22),
            ".450/400 Nitro Express 3 inch": (15.87, 13.92, 13.21, 11.18, 76.2, 55.26, 95.25, 10.41),
            ".338 Marlin Express": (14.05, 12.89, 12.52, 9.35, 48.01, 37.03, 62.23, 8.6),
            ".17 Remington Fireball": (9.6, 9.57, 9.28, 5.18, 35.81, 27.05, 46.48, 4.38),
        }
        for name, values in sheet.items():
            self.assertEqual(tuple(by_name[name][k] for k in keys), values, name)
        # Values the earlier sources got wrong:
        self.assertAlmostEqual(by_name["6.5-300 Weatherby Magnum"]["neck"], 7.49)  # Wikipedia: 13.68
        self.assertGreater(by_name[".38-56 WCF"]["case"], 50)                     # Wikipedia mm: 2.10
        self.assertLess(by_name[".22 Nosler"]["rim"], by_name[".22 Nosler"]["base"])  # rebated rim
        self.assertIsNone(by_name["9.3x72 mm R"]["shoulder"])

    def test_45_colt_is_drawn_with_a_round_nose(self):
        # Factory lead loads are round nose with a small flat (Raven's W-W round, 2026-11-08).
        by_name = {s["name"]: s for s in ALL}
        self.assertEqual(by_name[".45 Colt"]["profile"], "round")

    def test_crimped_blank(self):
        by_name = {s["name"]: s for s in ALL}
        b = by_name[".22 Blank (6.8/11)"]
        self.assertEqual(b["kind"], RIMFIRE)
        self.assertEqual((b["rim"], b["case"], b["oal"]), (6.8, 11.0, 11.0))
        self.assertEqual(b["base"], by_name[".22 Short"]["base"], "same .22 case body")
        self.assertIn("platzpatrone", b["aliases"])
        self.assertFalse(is_obsolete(b["name"]))

    def test_alarm_blanks_keep_the_cip_values(self):
        by_name = {s["name"]: s for s in ALL}
        keys = ("kind", "rim", "base", "case", "oal", "profile")
        sheet = {  # C.I.P. Tab. VIII maximum cartridge, mm
            "8 mm Knall": (RIMLESS, 8.0, 8.0, 20.3, 20.3, "flat"),
            ".315 Knall": (RIMLESS, 8.0, 8.0, 17.65, 17.65, "flat"),
            "9 mm R Knall": (RIMMED, 11.0, 9.58, 17.5, 17.5, "crimped"),
            ".320 Knall": (RIMMED, 9.55, 8.09, 16.0, 16.0, "crimped"),
            ".45 Knall": (RIMMED, 13.0, 12.1, 16.6, 16.6, "crimped"),
            ".22 Long Knall": (RIMFIRE, 7.06, 5.74, 15.0, 15.0, "crimped"),
            "6 mm Flobert Knall": (RIMFIRE, 7.15, 5.75, 6.6, 6.6, "crimped"),
        }
        for name, values in sheet.items():
            with self.subTest(name):
                s = by_name[name]
                self.assertEqual(tuple(s[k] for k in keys), values)
                self.assertLess(s["neck"], s["base"] + 0.01)
                self.assertFalse(is_obsolete(name))
                self.assertFalse(is_rare(name))
                self.assertEqual(INTRODUCED[name][0], 1991)
                self.assertEqual(name in PRIMERS, s["kind"] != RIMFIRE)
        self.assertIsNone(origin("6 mm Flobert Knall"))  # blanks have no country (2026-11-07)
        self.assertIn("9mmrk", by_name["9 mm R Knall"]["aliases"])

    def test_rounds_from_ravens_bag_keep_their_sources(self):
        # 2026-11-08: .320 Revolver from the C.I.P. «320 Short» sheet, 9 mm Flobert from Wikipedia's infobox.
        by_name = {s["name"]: s for s in ALL}
        keys = ("kind", "rim", "base", "neck", "case", "oal", "bullet", "profile")
        self.assertEqual(tuple(by_name[".320 Revolver"][k] for k in keys),
                         (RIMMED, 9.55, 8.12, 8.12, 16.6, 26.7, 8.0, "round"))
        self.assertEqual(tuple(by_name["9 mm Flobert Bosquette"][k] for k in keys),
                         (RIMFIRE, 10.16, 8.85, 8.85, 10.18, 14.98, 8.84, "round"))
        self.assertEqual(INTRODUCED[".320 Revolver"][0], 1868)
        self.assertEqual(origin(".320 Revolver")[0], "GB")
        self.assertEqual(origin("9 mm Flobert Bosquette")[0], "FR")
        self.assertEqual(tags(".320 Revolver"), ["obsolete", "rare"])
        self.assertEqual(tags("9 mm Flobert Bosquette"), ["rare"])
        self.assertEqual(bullet(".320 Revolver"), LEAD)
        self.assertNotIn("9 mm Flobert Bosquette", PRIMERS)  # rimfire

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
                self.assertTrue(is_source(source), source)

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
        rifles = {s["name"] for cat, items in CATALOGUE if cat == "Langwaffe" for s in items}
        for name in (".338 Norma Magnum", "12.7x108 mm", "7.65x53 mm Argentine"):
            self.assertIn(name, rifles)

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
        self.assertFalse(is_rare(".450 Marlin"))  # 1.5 per mille of the guns on TownPost
        self.assertFalse(is_rare("10.3x60 mm R"))  # 2.4 per mille on swisswaffen.com
        self.assertTrue(is_rare(".405 Winchester"))  # not among GunBroker's 250 calibres

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
        candidates = {c for cs in ORIGIN_UNDECIDED.values() for c in cs}
        self.assertLessEqual(candidates, set(COUNTRIES))
        self.assertEqual(set(ORIGIN.values()) | candidates, set(COUNTRIES))  # no unused country
        for code, (name, flag) in COUNTRIES.items():
            self.assertTrue(name)
            self.assertTrue(flag is None or len(flag) == 2, code)

    def test_known_origins(self):
        for name in ("5.6 mm GP 90", "7.5x55 mm Swiss (GP 11)", "7.5x53.5 mm Swiss (GP 1890)",
                     "7.5 mm Swiss Ordnance 1882"):
            self.assertEqual(ORIGIN[name], "CH")
        # Raven 2026-11-08: the tag tilts to the main adopter, user or producer where only the developer differs
        self.assertEqual(origin("7.65 mm Parabellum"), ("CH", "Switzerland", "🇨🇭"))  # Swiss service pistol round 1900-49; DWM design
        self.assertEqual(origin("7.62x39 mm"), ("SU", "Soviet Union", None))
        self.assertEqual(origin("7.62x54 mm R"), ("RUE", "Russian Empire", None))
        self.assertNotIn("RU", COUNTRIES)  # RU is today's Russia, not the Russian Empire
        self.assertEqual(origin("5.6 mm GP 90"), ("CH", "Switzerland", "🇨🇭"))
        # Raven 2026-11-07: worldwide rounds keep the state that introduced them; WORLDWIDE is a separate set
        for worldwide in ("9x19 mm", ".22 LR", ".308 Winchester", "5.56x45 mm NATO", ".45 ACP", "12/70"):
            self.assertIn(worldwide, WORLDWIDE)
        self.assertEqual(origin("9x19 mm"), ("DE", "Germany", "🇩🇪"))
        self.assertEqual(ORIGIN[".22 LR"], "US")
        # unions of states are origins too (Raven 2026-11-08): the NATO rounds carry NATO, which has no flag emoji
        self.assertEqual(origin("5.56x45 mm NATO"), ("NATO", "NATO", None))
        self.assertEqual(origin("7.62x51 mm NATO"), ("NATO", "NATO", None))
        self.assertEqual(ORIGIN[".223 Remington"], "US")
        self.assertIsNone(origin("12/70"))  # a gauge, not a cartridge
        self.assertNotIn("7.62x39 mm", WORLDWIDE)
        self.assertLessEqual(WORLDWIDE, NAMES)
        self.assertNotIn("WW", COUNTRIES)
        self.assertEqual(origin("9x23 mm Largo"), ("ES", "Spain", "🇪🇸"))  # Spanish service round 1905-1980s; Bergmann design
        self.assertEqual(origin(".30 Nosler"), ("US", "United States", "🇺🇸"))  # sporting rounds are tagged too
        self.assertIsNone(origin(".36 Rundkugel (.375)"))  # not a single cartridge
        self.assertEqual(origin("9x18 mm Ultra"), ("DE", "Germany", "🇩🇪"))  # Genschow 1936, not Hirtenberger 1972
        self.assertEqual(ORIGIN[".300 HAM'R"], "US")
        self.assertNotIn(".300 HAM'R", WORLDWIDE)

    def test_worldwide_and_candidate_helpers(self):
        self.assertTrue(is_worldwide("9x19 mm"))
        self.assertTrue(is_worldwide("12/70"))
        self.assertFalse(is_worldwide("7.62x39 mm"))
        self.assertFalse(is_worldwide("no such calibre"))
        # every two-state case was decided 2026-11-07/08; #52 then added the C.I.P. "DE/FI" wadcutter and
        # the cannon rounds the GAU-8/KCA 30 mm round
        self.assertEqual(set(ORIGIN_UNDECIDED), {".32 S&W Long Wadcutter", "30x173 mm"})
        self.assertEqual(origin_candidates("9x19 mm"), ())  # decided
        self.assertEqual(origin_candidates("12/70"), ())  # a gauge, nothing to decide
        with patch.dict(ORIGIN_UNDECIDED, {"5.56x45 mm NATO": ("US", "BE")}):
            self.assertEqual(origin_candidates("5.56x45 mm NATO"),
                             (("US", "United States", "🇺🇸"), ("BE", "Belgium", "🇧🇪")))
        for name in ORIGIN_UNDECIDED:
            self.assertIsNone(origin(name), name)
            self.assertEqual(len(origin_candidates(name)), len(ORIGIN_UNDECIDED[name]))

    def test_every_cartridge_has_an_origin_or_is_undecided(self):
        # Raven 2026-11-06: every calibre gets the state that introduced it, where the sources agree.
        # Shot shell gauges, loose balls and air gun pellets are not one cartridge, and blanks (no bullet, so
        # the case is the whole round and the width kept for drawings is the case's: the crimped ones from
        # blank() and the plain-cylinder alarm rounds from straight()) are trade sizes made everywhere:
        # none of them has a country.
        sizes = {s["name"] for s in ALL if s["kind"] in (SHOT, BALL, MINIE, PELLET)}
        blanks = {s["name"] for s in ALL if s["oal"] == s["case"] and s["bullet"] == s["base"]} - sizes
        self.assertEqual(len(blanks), 9)  # 9 mm P.A.K., .22 Blank (6.8/11) and the seven Knall rounds
        self.assertLessEqual(sizes | {".22 Blank (6.8/11)"}, set(INTRODUCED_UNKNOWN))  # no single launch year
        self.assertIn("9 mm P.A.K.", blanks)
        for name in sizes | blanks:
            self.assertIsNone(origin(name), name)
            self.assertNotIn(name, ORIGIN_UNDECIDED)
        for name in NAMES - sizes - blanks:
            self.assertTrue(name in ORIGIN or name in ORIGIN_UNDECIDED, name)
        self.assertLessEqual(set(ORIGIN_UNDECIDED), NAMES)
        self.assertFalse(set(ORIGIN_UNDECIDED) & set(ORIGIN))
        for name, candidates in ORIGIN_UNDECIDED.items():
            self.assertGreaterEqual(len(candidates), 2, name)  # two states can claim it
            self.assertEqual(len(set(candidates)), len(candidates), name)
        self.assertEqual(ORIGIN[".22 BB Cap"], "FR")  # Flobert 1845
        self.assertEqual(ORIGIN["6.5x53 mm R Mannlicher"], "AH")  # Steyr 1892, Romanian and Dutch service round
        self.assertEqual(origin(".338 Lapua Magnum"), ("FI", "Finland", "🇫🇮"))
        self.assertIn(".338 Lapua Magnum", WORLDWIDE)
        self.assertEqual(origin(".300 Lapua Magnum"), ("FI", "Finland", "🇫🇮"))
        # the two-state cases decided 2026-11-07/08
        self.assertEqual(origin(".22 TCM"), ("PH", "Philippines", "🇵🇭"))
        self.assertEqual(origin("7.65x53 mm Argentine"), ("AR", "Argentina", "🇦🇷"))  # the largest adopter; Mauser design
        self.assertEqual(ORIGIN["9x21 mm IMI"], "IT")  # Jager of Loano designed it; IMI only commercialised it
        self.assertEqual(ORIGIN[".500 Jeffery"], "GB")
        self.assertEqual(ORIGIN["6 mm BR Norma"], "SE")
        self.assertEqual(ORIGIN["6.35 mm Browning (.25 ACP)"], "BE")
        self.assertEqual(ORIGIN["10 mm Auto"], "US")

    def test_swiss_service_revolver_rounds_are_obsolete(self):
        for name in ("7.5 mm Swiss Ordnance 1882", "10.4 mm Swiss Ordnance 1878"):
            self.assertIn(name, NAMES)
            self.assertTrue(is_obsolete(name), name)
        self.assertEqual(INTRODUCED["10.4 mm Swiss Ordnance 1878"][0], 1878)

    def test_municion_check_fixes_wrong_dimensions(self):
        # Values that disagreed with both the municion.org drawing and the published standard.
        by_name = {s["name"]: s for s in ALL}
        expected = {
            ".22 WMR": {"oal": 34.3},
            ".41 Magnum": {"rim": 12.5},
            ".22-250 Remington": {"shoulder": 10.5},
            ".338 Lapua Magnum": {"shoulder": 13.82},
            ".300 PRC": {"case": 65.5, "sh_at": 54.6},
            # sh_at is the C.I.P. sheet's L1 (see SHOULDER_ANGLES), not the municion.org specimen.
            "6.5x54 mm Mannlicher-Schönauer": {"case": 53.6, "sh_at": 41.82},
            "10.4x38 mm R Vetterli": {"rim": 15.7, "base": 13.62, "shoulder": 13.1, "neck": 11.43,
                                      "case": 38.21, "sh_at": 26.11, "oal": 56.22, "bullet": 10.92},
        }
        for name, fields in expected.items():
            for key, value in fields.items():
                self.assertEqual(by_name[name][key], value, f"{name} {key}")

    def test_cip_case_heads_flagged_by_cartridges_of_the_world(self):
        # Cartridges of the World (14th ed., ch. 12) gave bigger rims; the values are the C.I.P.
        # sheets' (R1 rim, P1 body, P2 shoulder, H2 neck, L3 case, L6 length, G1 bullet).
        by_name = {s["name"]: s for s in ALL}
        expected = {
            ".300 Winchester Magnum": {"rim": 13.51},
            ".375 H&H Magnum": {"rim": 13.51, "shoulder": 11.37, "neck": 10.21, "bullet": 9.55},
            "7 mm STW": {"rim": 13.51, "base": 13.03, "shoulder": 12.37, "neck": 8.05, "oal": 92.71},
            "6.5 mm Remington Magnum": {"rim": 13.51, "base": 13.03},
            ".350 Remington Magnum": {"rim": 13.51, "base": 13.03},
            ".416 Weatherby Magnum": {"rim": 14.71},
            "7x57 mm R": {"rim": 13.5, "oal": 78.0},
            "7x65 mm R": {"rim": 13.32, "oal": 83.6},
            "6.5x57 mm R": {"rim": 13.32, "base": 11.92},
            "8x57 mm IRS": {"rim": 13.32, "base": 11.92, "shoulder": 10.95, "neck": 9.08, "oal": 82.0},
            "9.3x74 mm R": {"rim": 13.35, "shoulder": 10.4, "neck": 9.92, "case": 74.7},
            "11x60 mm R Mauser": {"rim": 15.0, "neck": 11.85, "case": 60.35, "oal": 78.0, "bullet": 11.4},
        }
        for name, fields in expected.items():
            for key, value in fields.items():
                self.assertEqual(by_name[name][key], value, f"{name} {key}")
        for s in ALL:
            if s["kind"] == "belted" and s["base"] < 13.1:
                # Only the .378 Weatherby family has a body wider than its rim.
                self.assertGreater(s["rim"], s["base"], s["name"])

    def test_other_names_of_the_same_cartridge_are_search_aliases(self):
        # Names that Cartridges of the World (14th ed.) gives for the same cartridge: renames, maker or
        # national names, loads in the same case and +P loads.
        by_name = {s["name"]: s for s in ALL}
        expected = {
            "38coltnewpolice": ".38 S&W", "7mmmauser": "7x57 mm Mauser", "6.5x52r": ".25-35 Winchester",
            "7.7x56r": ".303 British", "400jeffery": ".450/400 Nitro Express 3 inch", "12.7x107": "12.7x108 mm",
            "38special+p": ".38 Special", "45-85": ".45-90 WCF", "50-105": ".50-110 Winchester",
            "7.5swedishnagant": "7.5 mm Swedish Nagant", "6.5-08": ".260 Remington",
            "7mmexpress": ".280 Remington", "8.58x71": ".338 Lapua Magnum", "8.58x70": ".338 Lapua Magnum",
            "301savage": ".303 Savage", "45-90hv": ".45-90 WCF", "44remmag": ".44 Magnum",
        }
        for alias, name in expected.items():
            self.assertIn(alias, by_name[name]["aliases"], name)
        # Same case, but a hotter load the older guns must not fire: their own calibres.
        for name in (".38 ACP", ".38 Super", "9 mm Glisenti", "9x19 mm"):
            self.assertIn(name, NAMES)

    def test_municion_years_fill_unknown_introductions(self):
        years = {".17 Hornet": 2012, ".35 Winchester Self-Loading": 1905, ".401 Winchester Self-Loading": 1910,
                 ".375 Flanged Magnum Nitro Express": 1912, "9.3x72 mm R": 1892, "9x57 mm Mauser": 1890,
                 "10.3x60 mm R": 1919, "9x39 mm": 1980}
        for name, year in years.items():
            self.assertEqual(INTRODUCED[name][0], year, name)
            self.assertTrue(INTRODUCED[name][1].startswith("https://municion.org/producto/"), name)
            self.assertNotIn(name, INTRODUCED_UNKNOWN)

    def test_every_calibre_with_a_bullet_names_it(self):
        # Raven 2026-11-11: written out in every file, a jacket and lead too; sources = [] is not checked.
        apps = {s["name"] for _, items in CATALOGUE for s in items}
        for _, items in ALL_CATALOGUE:
            for s in items:
                loose = s["kind"] in (BALL, MINIE, PELLET)
                blank = not loose and is_blank(s["profile"], s["rim"], s["base"], s["neck"], s["bullet"], s["case"], s["oal"])
                has_bullet = s["name"] in apps and s["kind"] != SHOT and not blank
                self.assertEqual(s["name"] in BULLETS, has_bullet, s["name"])
                if has_bullet:
                    usual = LEAD if s["kind"] in (BALL, MINIE, PELLET) else JACKETED
                    allowed = LOOSE_BULLETS if s["kind"] in (BALL, MINIE, PELLET) else CARTRIDGE_BULLETS
                    self.assertIn(bullet(s["name"]), allowed, s["name"])
                    unchecked = BULLETS[s["name"]][1] is None
                    self.assertEqual(s["name"] in BULLET_INFERRED, unchecked and bullet(s["name"]) != usual, s["name"])
                else:
                    self.assertIsNone(bullet(s["name"]), s["name"])
        for name in ("12/70", ".22 Blank (6.8/11)", "9 mm P.A.K.", "8 mm Knall", ".315 Knall"):
            self.assertIsNone(bullet(name), name)
        self.assertEqual(bullet("7.62x38 mm R Nagant"), JACKETED)  # seated inside the case, not a blank
        self.assertEqual(bullet("5.66x39 mm MPS"), STEEL)

    def test_bullets_name_known_calibres_and_are_sourced(self):
        names = {s["name"] for _, items in CATALOGUE for s in items}
        for name, (kind, url) in BULLETS.items():
            self.assertIn(name, names)
            self.assertIn(kind, CARTRIDGE_BULLETS + LOOSE_BULLETS, name)
            self.assertTrue(url is None or is_source(url), name)
        self.assertEqual(BULLET_INFERRED, {"7 mm Blaser Magnum", ".300 Blaser Magnum", "8.5x55 mm Blaser",
                                           ".338 Blaser Magnum", ".375 Blaser Magnum", "9.3x66 mm Sako (.370 Sako Magnum)",
                                           "8x60 mm RS", "8x57 mm IR", ".275 Rigby",
                                           # The page gives no factory load, or a later one than the original.
                                           "6.5x40 mm R", "7x75 mm R Vom Hofe Super Express", "8x48 mm R Sauer",
                                           "8x57 mm R 360", "8x58 mm R Sauer",
                                           # COTW 18 gives only the weight or handloads.
                                           "9.3x72 mm R Sauer", "9.3x75 mm R Nimrod", "10.75x63 mm Mauser",
                                           "9.5x47 mm R", "10.5x47 mm R",
                                           "10.25x69 mm R Hunting-Express", "12.17x44 mm R",
                                           # Brass-coated bullets drawn as lead.
                                           "10.4x47 mm R Italian Vetterli", "11.5x57 mm R Spanish Reformado",
                                           # COTW 18 gives a ball without its material.
                                           "8x60 mm R Guedes",
                                           # No factory load on the page, or a later one than the original.
                                           ".242 Rimless Nitro Express", ".280 Jeffery", ".297/250 Rook",
                                           ".500 Express 3 inch", ".500/450 Magnum Express",
                                           ".32 Protector", "7.7 mm Bittner", ".380 Long Revolver",
                                           "9.4 mm Dutch", ".44 Merwin & Hulbert", ".45 Cowboy Special",
                                           ".25-20 Single-Shot", ".25-21 Stevens", ".338-06 A-Square",
                                           ".40-65 Ballard Everlasting", ".44-40 Extra Long", ".44 Long Centrefire",
                                           ".44-75 Ballard Everlasting", ".45-100 Remington Necked",
                                           # Rimfire rounds whose page does not name the bullet.
                                           ".22 CB Cap", ".22 Winchester Automatic", ".25 Short Rimfire",
                                           ".25 Stevens Short", ".30 Long Rimfire", ".38 Long Rimfire",
                                           ".38 Extra Long Rimfire", ".41 Long Rimfire", ".44 Short Rimfire",
                                           ".44 Long Rimfire", ".44 Extra Long Rimfire", ".46 Short Rimfire",
                                           ".46 Long Rimfire", ".46 Extra Long Rimfire", ".56-46 Spencer",
                                           ".50 Remington Navy Rimfire", ".56-50 Spencer", ".56-52 Spencer",
                                           ".56-52 Spencer Necked", ".58 Miller",
                                           # Proprietary hunting rounds whose page gives bullet weights only.
                                           "7.82 Lazzeroni Patriot", "8.59 Lazzeroni Galaxy",
                                           "9.09 Lazzeroni Eagle", "7 mm Dakota", ".300 Dakota", ".330 Dakota",
                                           ".375 Dakota", ".416 Dakota", ".450 Dakota", "7 mm Canadian Magnum",
                                           ".338 Canadian Magnum", ".458 Canadian Magnum",
                                           # A-Square's and Hoffman's: handloads or bullet weights only.
                                           ".338 Excaliber", ".375 A-Square", ".416 Hoffman",
                                           ".460 A-Square Short", ".500 A-Square", ".416 Rimmed",
                                           ".450 Assegai", ".400 A-Square DPM"})
        self.assertEqual(bullet("9x19 mm"), JACKETED)

    def test_rounds_older_than_jacketed_bullets_are_not_jacketed(self):
        # Jacketed bullets came with smokeless powder (Rubin 1882, Lebel 1886); the Swiss 1882 revolver
        # round was one of the first.
        for _, items in CATALOGUE:
            for s in items:
                year = INTRODUCED.get(s["name"], (None,))[0]
                if year and year < 1886 and s["oal"] > s["case"] and s["case"] and s["name"] != "7.5 mm Swiss Ordnance 1882":
                    self.assertNotEqual(bullet(s["name"]), JACKETED, s["name"])

    def test_todays_noses_are_kept_beside_the_first_ones(self):
        # Raven 2026-11-11: draw the nose first sold, and keep today's usual one in the data.
        early = {".303 British", "7.65x53 mm Argentine", "7x57 mm Mauser", "6.5x57 mm Mauser", "7x57 mm R",
                 "6.5x55 mm Swedish", "6.5x50 mm SR Arisaka", "7.62x54 mm R", "8x50 mm R Lebel", ".275 Rigby",
                 ".405 Winchester"}
        for name in early:
            self.assertEqual(PROFILE_TODAY.get(name), SPITZER, name)
        # The 6x57 mm Mauser is no longer loaded, so it has no nose of today.
        self.assertNotIn("6x57 mm Mauser", PROFILE_TODAY)

    def test_rounds_older_than_pointed_bullets_are_not_drawn_pointed(self):
        # The profile is the nose of the bullet first sold, and the first pointed service bullet was the
        # French Balle D of 1898 (COTW 18 p. 553).
        for _, items in ALL_CATALOGUE:
            for s in items:
                year = INTRODUCED.get(s["name"], (None,))[0]
                if year and year < 1898:
                    self.assertNotEqual(s["profile"], SPITZER, s["name"])

    def test_known_original_bullets(self):
        self.assertEqual(bullet(".22 LR"), LEAD)
        self.assertEqual(bullet(".38 Special"), LEAD)
        self.assertEqual(bullet(".357 Magnum"), LEAD)
        self.assertEqual(bullet("11x59 mm R Gras"), PAPER_PATCHED)
        self.assertEqual(bullet("10.4x38 mm R Vetterli"), PAPER_PATCHED)
        self.assertEqual(bullet(".30-30 Winchester"), SOFT_POINT)
        self.assertEqual(bullet("9.3x62 mm"), SOFT_POINT)
        self.assertEqual(bullet(".308 Winchester"), SOFT_POINT)
        self.assertEqual(bullet("7.62x51 mm NATO"), JACKETED)
        self.assertEqual(bullet("7.5x55 mm Swiss (GP 11)"), JACKETED)
        self.assertEqual(bullet(".17 HMR"), POLYMER_TIP)
        self.assertEqual(bullet("6.5 mm Creedmoor"), POLYMER_TIP)
        self.assertEqual(bullet(".22 TCM"), HOLLOW_POINT)
        self.assertEqual(bullet("5 mm Remington Rimfire Magnum"), HOLLOW_POINT)
        self.assertEqual(bullet(".25 NAA"), HOLLOW_POINT)
        self.assertEqual(bullet(".32 NAA"), JACKETED)  # also sold with full metal jackets

    def test_case_materials(self):
        names = {s["name"] for _, items in ALL_CATALOGUE for s in items}
        for name, (material, url) in CASES.items():
            self.assertIn(name, names)
            self.assertIn(material, (BRASS, COPPER, STEEL, NICKEL, ALUMINIUM, PAPER, HYBRID), name)
            if material != BRASS:
                self.assertTrue(is_source(url), name)
        # Every calibre with a case names its material, brass too; shot shells and loose projectiles have none.
        self.assertEqual(set(CASES), {s["name"] for _, items in ALL_CATALOGUE for s in items
                                      if s["kind"] not in (SHOT, BALL, MINIE, PELLET)})
        self.assertEqual(case_material(".44 Henry"), COPPER)
        self.assertEqual(case_material("5.45x39 mm"), STEEL)
        self.assertEqual(case_material(".577 Snider"), PAPER)
        self.assertEqual(case_material("9x19 mm"), BRASS)
        self.assertEqual(case_material(".277 SIG Fury"), HYBRID)

    def test_current_case_materials_differ_from_the_original(self):
        for name, (materials, url) in CURRENT_CASES.items():
            self.assertIn(name, NAMES)
            self.assertTrue(materials, name)
            self.assertNotIn(case_material(name), materials, name)
            self.assertTrue(set(materials) <= {BRASS, COPPER, STEEL, NICKEL, ALUMINIUM}, name)
            self.assertTrue(is_source(url), name)
        self.assertEqual(current_case_materials(".45-70 Government"), (BRASS,))
        self.assertEqual(current_case_materials("9x19 mm"), (STEEL, ALUMINIUM))
        self.assertEqual(current_case_materials("7.5x55 mm Swiss (GP 11)"), ())
        # The ZU-23's steel case followed the VYa-23's brass one (Jane's 2002 p. 91).
        self.assertEqual(current_case_materials("23x152 mm B"), (STEEL,))
        # Raven 2026-11-11: aluminium too. CCI's Blazer Aluminum line; the Apache's LW30 rounds (Jane's p. 112).
        for name in ("6.35 mm Browning (.25 ACP)", "7.65 mm Browning (.32 ACP)", "9 mm Browning kurz (.380 ACP)",
                     ".38 Special", ".357 Magnum", ".40 S&W", "10 mm Auto", ".44 Special", ".44 Magnum",
                     "30x113 mm B"):
            self.assertEqual(current_case_materials(name), (ALUMINIUM,), name)
        # Copper first (Frankford Arsenal's 1873/74 rounds), brass and aluminium today.
        self.assertEqual(current_case_materials(".45 Colt"), (BRASS, ALUMINIUM))
        self.assertEqual(current_case_materials(".44 Colt"), (BRASS,))
        self.assertEqual(current_case_materials(".45 ACP"), (STEEL, ALUMINIUM))
        # The GAU-8's aluminium case first, the KCA's steel too (Jane's 2002 pp. 105, 112-113).
        self.assertEqual(current_case_materials("30x173 mm"), (STEEL,))
        # Copper and wartime steel first, brass today.
        self.assertEqual(current_case_materials(".22 Short"), (BRASS,))
        self.assertEqual(current_case_materials("7.92x33 mm Kurz"), (BRASS,))

    def test_case_materials_checked_2026_11_11(self):
        # Raven 2026-11-11: check every calibre's case material. COTW 18, Jane's 2002 and Gun Digest name
        # these. Rounds whose sources give brass or steel alike (9x18 mm Makarov, 12.7x108 mm, 7.62x45 mm
        # vz. 52, 20x102 mm, 20x139 mm, 30x113 mm B) stay brass.
        expected = {"7.92x33 mm Kurz": STEEL, "5.45x18 mm": STEEL, "5.8x42 mm": STEEL, "9x39 mm": STEEL,
                    "6 mm SAW": STEEL, ".22 Short": COPPER, "27x145 mm B": STEEL, "30x165 mm": STEEL,
                    "30x173 mm": ALUMINIUM, "35x228 mm": STEEL, "23x152 mm B": BRASS, "40x311 mm R": BRASS,
                    "40x365 mm R": BRASS}
        for name, material in expected.items():
            self.assertEqual(case_material(name), material, name)
            self.assertTrue(CASES[name][1], name)

    def test_copper_cases_seen_on_wikimedia_commons_photos(self):
        # Raven 2026-11-11: look at the Wikipedia photos of the old rounds whose case was an unchecked brass.
        for name in (".22 BB Cap", ".22 Extra Long", ".32 Short Rimfire", ".38 Long Rimfire", ".41 Short",
                     ".44 Colt", ".45 Colt"):
            self.assertEqual(case_material(name), COPPER, name)
            self.assertTrue(any(url.startswith("https://commons.wikimedia.org/wiki/File:")
                                for url in SOURCES[(name, "case")]), name)

    def test_copper_cases_seen_on_municion_photos(self):
        # Raven 2026-11-11: municion.org's photos of the early makers' rounds show copper cases.
        for name in (".25 Short Rimfire", ".30 Short Rimfire", ".30 Long Rimfire", ".32 Extra Short Rimfire",
                     ".32 Long Rimfire", ".32 Extra Long Rimfire", ".38 Short Rimfire", ".38 Extra Long Rimfire",
                     ".41 Long Rimfire", ".44 Short Rimfire", ".44 Long Rimfire", ".46 Short Rimfire",
                     ".46 Long Rimfire", ".46 Extra Long Rimfire", ".50 Remington Navy Rimfire", ".58 Miller",
                     ".56-50 Spencer", ".56-46 Spencer", ".56-52 Spencer Necked", ".50 Remington Army",
                     ".45 Colt Government"):
            self.assertEqual(case_material(name), COPPER, name)
            self.assertTrue(any(url.startswith("https://municion.org/producto/")
                                for url in SOURCES[(name, "case")]), name)
        # municion.org's text: the .22 WRF's case was copper at first. Its BB and CB cap page shows copper.
        for name in (".22 Winchester Rimfire", ".22 CB Cap"):
            self.assertEqual(case_material(name), COPPER, name)
            self.assertTrue(any(url.startswith("https://municion.org/producto/")
                                for url in SOURCES[(name, "case")]), name)
        self.assertEqual(current_case_materials(".22 Winchester Rimfire"), (BRASS,))
        # Brass, each with a photo, a drawing or a page's text as its source.
        for name in (".45-70 Van Choate", "12.17x44 mm R", ".577/450 Martini-Henry", "10.4 mm Swiss Ordnance 1878",
                     "7.62x54 mm R", ".38 Long Colt", "6.5x52 mm Carcano", "8x50 mm R Mannlicher", "9.3x74 mm R",
                     "8x59 mm Breda", ".380 Short Revolver", ".40-50 Sharps Necked",
                     ".44-60 Sharps & Remington Necked", ".44-77 Sharps & Remington", ".58 Berdan Musket",
                     "11.43x50 mm R Egyptian Remington", ".32-40 Remington", ".40-70 Sharps Necked",
                     "11.3x50 mm R Beaumont M71", ".50-90 Sharps", ".32 Long Colt", ".40-90 Sharps Necked",
                     ".44 Henry Centrefire", ".44-90 Remington Special", ".45-50 Peabody Sporting",
                     "10.15x61 mm R Jarmann", "10.15x63 mm R Serbian Mauser", "11.15x58 mm R Werndl M77",
                     "11x59 mm R Gras", "11x60 mm R Japanese Murata", ".25-20 Single-Shot", ".30-30 Wesson",
                     ".32-30 Remington", ".32-40 Ballard", ".32-40 Bullard", ".35-40 Maynard 1882",
                     ".38-40 Remington-Hepburn", ".38-50 Ballard Everlasting", ".38-50 Maynard 1882",
                     ".38-50 Remington-Hepburn", ".40-50 Sharps Straight", ".40-60 Winchester", ".40-70 Ballard",
                     ".40-70 Peabody What Cheer", ".40-70 Sharps Straight", ".40-90 Peabody What Cheer",
                     ".40-90 Sharps Straight", ".44-100 Ballard", ".44-95 Peabody What Cheer",
                     ".44 Extra Long Centrefire", ".45-110 Sharps", ".45-75 Winchester",
                     ".450/400 Nitro Express 2⅜ inch", ".50-140 Sharps", "8x60 mm R Guedes", ".41 Long Colt",
                     ".44 Bull Dog", ".476 Enfield", "7.5 mm Swedish Nagant", ".303 British",
                     ".32-35 Stevens & Maynard", ".38-55 Winchester", ".38-90 Winchester Express",
                     ".40-110 Winchester Express", ".40-65 Winchester", ".40-75 Bullard", ".40-90 Bullard",
                     ".45-125 Winchester Express", ".45-90 WCF", ".50-110 Winchester", ".50-115 Bullard",
                     ".50-95 WCF", "7.65x53 mm Argentine", "8x42 mm R M88", "8x50 mm R Lebel", "8x51 mm Mauser",
                     "8x51 mm R Mauser"):
            self.assertEqual(case_material(name), BRASS, name)
            self.assertTrue(SOURCES[(name, "case")], name)

    def test_bbs_are_loose_steel_or_plastic_balls(self):
        by_name = {s["name"]: s for _, items in CATALOGUE for s in items}
        for name, (material, url) in BULLETS.items():
            if material in (STEEL, PLASTIC):
                self.assertTrue(is_source(url), name)
                if name != "5.66x39 mm MPS":  # the steel underwater dart
                    self.assertIn(by_name[name]["kind"], (BALL, MINIE, PELLET), name)
        steel = by_name["4.4 mm Stahl-BB (.177 BB)"]
        self.assertEqual(steel["kind"], BALL)
        self.assertTrue(4.3 <= steel["bullet"] <= 4.4)  # 0.171-0.173 in, smaller than a 4.5 mm pellet
        self.assertEqual(loose_material("4.4 mm Stahl-BB (.177 BB)"), STEEL)
        self.assertEqual(loose_material("6 mm Airsoft-BB"), PLASTIC)
        self.assertEqual(loose_material(".50 Rundkugel (.490)"), LEAD)
        self.assertEqual(by_name["6 mm Airsoft-BB"]["bullet"], 6.0)
        self.assertEqual(by_name["8 mm Airsoft-BB"]["bullet"], 8.0)
        air_guns = [s["name"] for cat, items in CATALOGUE if cat == "Luftdruck" for s in items]
        self.assertIn("6 mm Airsoft-BB", air_guns)

    def test_lookalike_groups(self):
        by_name = {s["name"]: s for s in ALL}
        seen = set()
        for differs, names in LOOKALIKES:
            self.assertGreaterEqual(len(names), 2, names)
            self.assertTrue(differs, names)
            self.assertLessEqual(set(differs), {RIM, BORE, LENGTH, SEATING, LOAD, IGNITION}, names)
            for name in names:
                self.assertIn(name, NAMES)
                self.assertNotIn(name, seen, f"{name} is in two lookalike groups")
                seen.add(name)
            specs = [by_name[n] for n in names]

            def spread(key):
                return round(max(s[key] for s in specs) - min(s[key] for s in specs), 2)
            # What the group names as the difference is what the dimensions show (LOAD is not in them).
            kinds = {s["kind"] for s in specs}
            self.assertEqual(len(kinds - {RIMFIRE}) > 1, RIM in differs, names)
            self.assertEqual(RIMFIRE in kinds and len(kinds) > 1, IGNITION in differs, names)
            # 8x57 I .318" against IS .323"; Finnish 7.62x53 R against 7.62x54 R. A wadcutter group is left
            # out: the parent's bullet is a rounded figure, the wadcutter's from its sheet.
            # A wadcutter sits flush or nearly so with the case mouth.
            self.assertEqual(min(s["oal"] - s["case"] for s in specs) < 1.5, SEATING in differs, names)
            if IGNITION in differs:
                # Rimfire and centrefire versions come from other makers and sources, so only bigger
                # differences count. The .44 Henry rimfire's heeled bullet is wider than the centrefire's
                # seated one, fired in the same guns.
                bore = spread("bullet") > 0.3 and names[0] != ".44 Henry"
                length = spread("case") > 1.5
            else:
                # The .30 Borchardt's bullet is the COTW table's .307 in., the Mauser's from its C.I.P. sheet;
                # COTW 18 p. 467 measures the three alike, and p. 466 has Tokarev pistols fire Mauser loads.
                bore = spread("bullet") >= 0.05 and SEATING not in differs and names[0] != ".30 Borchardt"
                length = spread("case") > 0.5
            if SEATING not in differs:
                self.assertEqual(bore, BORE in differs, names)
            self.assertEqual(length, LENGTH in differs, names)
        self.assertEqual(lookalikes("5.6 mm GP 90"), [".223 Remington", "5.56x45 mm NATO"])
        self.assertEqual(lookalikes("7x65 mm R"), ["7x64 mm"])
        self.assertEqual(lookalikes("8x57 mm I"), ["8x57 mm IS", "8x57 mm IRS", "8x57 mm IR"])
        self.assertEqual(lookalikes(".275 Rigby"), ["7x57 mm Mauser", "7x57 mm R"])
        self.assertEqual(lookalikes(".30-06 Springfield"), [".30-03 Springfield"])
        self.assertEqual(lookalikes("7.62x25 mm Tokarev"), [".30 Borchardt", "7.63x25 mm Mauser"])

    def test_lookalike_groups_have_names(self):
        # Raven 2026-11-11: a group's name is one of its calibres' or the family's own.
        self.assertEqual(len(LOOKALIKE_NAMES), len(LOOKALIKES))
        self.assertEqual(len(set(LOOKALIKE_NAMES)), len(LOOKALIKE_NAMES))
        groups = dict(zip(LOOKALIKE_NAMES, (names for _, names in LOOKALIKES)))
        self.assertEqual(groups[".308 Winchester"], [".308 Winchester", "7.62x51 mm NATO"])
        self.assertEqual(groups["7.63x25 mm"], [".30 Borchardt", "7.63x25 mm Mauser", "7.62x25 mm Tokarev"])
        for title, names in groups.items():
            self.assertTrue(title not in NAMES or title in names, title)

    def test_rimfire_and_centrefire_versions_are_calibres_of_their_own(self):
        # Raven 2026-11-09: a cartridge made in numbers both as rimfire and centrefire gets a file for each
        # ignition, grouped as lookalikes; the original keeps the plain name.
        kinds = {s["name"]: s["kind"] for s in ALL}
        for rimfire, centrefire in [("10.4x38 mm R Vetterli", "10.4x38 mm R Vetterli Centrefire"),
                                    (".44 Henry", ".44 Henry Centrefire"),
                                    (".32 Long Rimfire", ".32 Long Centrefire"),
                                    ("10.4 mm Swiss Ordnance 1872 Rimfire", "10.4 mm Swiss Ordnance 1878")]:
            with self.subTest(rimfire):
                self.assertEqual(kinds[rimfire], RIMFIRE)
                self.assertNotIn(rimfire, PRIMERS)
                self.assertEqual(kinds[centrefire], RIMMED)
                self.assertIn(centrefire, PRIMERS)
                self.assertIn(centrefire, lookalikes(rimfire))
        # The Swiss service Vetterli was rimfire; the centrefire one is the same case with a primer.
        by_name = {s["name"]: s for s in ALL}
        for key in ("rim", "base", "shoulder", "neck", "case", "sh_at", "oal", "bullet"):
            self.assertEqual(by_name["10.4x38 mm R Vetterli"][key], by_name["10.4x38 mm R Vetterli Centrefire"][key])
        self.assertEqual(case_material("10.4x38 mm R Vetterli"), COPPER)
        self.assertEqual(case_material("10.4x38 mm R Vetterli Centrefire"), BRASS)

    def test_lookalike_variants_from_their_cip_sheets(self):
        # Raven 2026-11-08: the cartridges C.I.P. lists apart from a calibre already in the catalogue are
        # calibres of their own. Values are the sheets' maximum cartridge (rim R1, body P1, neck H2, case L3,
        # length L6, bullet G1).
        by_name = {s["name"]: s for s in ALL}
        expected = {
            "5.6x50 mm R Magnum": (10.9, 9.59, 6.48, 50.0, 61.0, 5.7),
            "5.6x57 mm R": (13.32, 11.94, 7.1, 56.7, 69.0, 5.7),
            "6.5x65 mm R RWS": (13.5, 12.08, 7.57, 65.0, 85.0, 6.7),
            "6.5x68 mm R": (15.0, 13.34, 7.6, 67.5, 87.5, 6.7),
            "8x60 mm RS": (13.4, 12.03, 9.08, 60.0, 83.6, 8.22),
            "8x65 mm RS": (13.32, 11.99, 8.96, 65.0, 87.5, 8.22),
            "9x57 mm R": (13.4, 11.96, 9.83, 56.8, 81.0, 9.08),
            "8x57 mm I": (11.95, 11.94, 8.99, 57.0, 82.0, 8.09),
            "8x57 mm IR": (13.32, 11.92, 8.99, 57.0, 82.0, 8.09),
            "7.62x53 mm R": (14.4, 12.42, 8.5, 53.5, 77.0, 7.85),
            ".450/400 Nitro Express 3¼ inch": (15.85, 13.84, 11.05, 82.55, 100.33, 10.41),
            ".275 Rigby": (12.06, 12.04, 8.23, 56.9, 77.98, 7.21),
            ".38 Special Wadcutter": (11.18, 9.63, 9.63, 29.34, 30.35, 9.14),
        }
        for name, values in expected.items():
            s = by_name[name]
            self.assertEqual((s["rim"], s["base"], s["neck"], s["case"], s["oal"], s["bullet"]), values, name)
            self.assertTrue(lookalikes(name), name)
        # .275 Rigby is its own calibre now (C.I.P. gives it 3200 bar against the 7x57's 3900), so its names
        # moved from the 7x57 to it.
        self.assertLessEqual({"275rigby", "275hvrigby"}, set(by_name[".275 Rigby"]["aliases"]))
        self.assertFalse({"275rigby", "275hvrigby"} & set(by_name["7x57 mm Mauser"]["aliases"]))
        # municion.org gives the rimmed 6.5x65 its own 1988 launch, like the rimless one.
        self.assertEqual(INTRODUCED["6.5x65 mm R RWS"][0], 1988)

    def test_years_checked_against_cartridges_of_the_world(self):
        # 2026-11-08: years compared with Cartridges of the World (14th ed.) and a second source. A wildcat
        # counts from its first factory ammunition, a military round from its adoption.
        years = {".22 Remington Automatic": 1914, "7.5 mm Swiss Ordnance 1882": 1882, "9x23 mm Winchester": 1996,
                 ".50-110 Winchester": 1887, ".338 Remington Ultra Magnum": 2002, "7 mm Remington Ultra Magnum": 2001,
                 ".30-378 Weatherby Magnum": 1996, ".338-378 Weatherby Magnum": 1998, "7 mm STW": 1994,
                 ".450/400 Nitro Express 3 inch": 1902}
        for name, year in years.items():
            self.assertEqual(INTRODUCED[name][0], year, name)
            self.assertNotIn(name, INTRODUCED_UNKNOWN)
        # The 3 inch case is Jeffery's shortened 3 1/4 inch one, so it cannot be older.
        self.assertGreater(INTRODUCED[".450/400 Nitro Express 3 inch"][0],
                           INTRODUCED[".450/400 Nitro Express 3¼ inch"][0])

    def test_45_super_is_an_alias_of_45_acp(self):
        # Raven 2026-11-08: no board lists the .45 Super and it measures like the .45 ACP.
        self.assertNotIn(".45 Super", NAMES)
        self.assertIn("45super", next(s for s in ALL if s["name"] == ".45 ACP")["aliases"])


if __name__ == "__main__":
    unittest.main()
