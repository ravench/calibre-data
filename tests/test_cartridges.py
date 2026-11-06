"""python3 -m unittest discover -s tests"""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cartridges import (WORLDWIDE, CATALOGUE, DISPLAY_ALIASES, PRIMERS, PRIMER_DIAMETERS,  # noqa: E402
                        PRIMER_SOURCES, PRIMER_UNVERIFIED, BERDAN_NITRO,
                        SMALL_PISTOL, SMALL_RIFLE, LARGE_RIFLE,
                        INTRODUCED, INTRODUCED_UNKNOWN, OBSOLETE, is_obsolete,
                        RARE, is_rare, tags,
                        ORIGIN, ORIGIN_UNDECIDED, COUNTRIES, origin,
                        RIMFIRE, RIMLESS, RIMMED, BALL, MINIE, PELLET, SHOT,
                        BULLETS, BULLET_INFERRED, JACKETED, LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP, bullet,
                        CASES, BRASS, COPPER, STEEL, NICKEL, PAPER, HYBRID, case_material,
                        CURRENT_CASES, current_case_materials, LOOSE_MATERIALS, PLASTIC, loose_material)

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
            self.assertTrue(url.startswith("https://"), name)

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
        self.assertEqual(ORIGIN["6 mm Flobert Knall"], "FR")
        self.assertIn("9mmrk", by_name["9 mm R Knall"]["aliases"])

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
        self.assertEqual(origin(".30 Nosler"), ("US", "United States", "🇺🇸"))  # sporting rounds are tagged too
        self.assertIsNone(origin(".36 Rundkugel (.375)"))  # not a single cartridge

    def test_every_cartridge_has_an_origin_or_is_undecided(self):
        # Raven 2026-11-06: every calibre gets the state that introduced it, where the sources agree.
        generic = {n for n, why in INTRODUCED_UNKNOWN.items()
                   if "not a single cartridge" in why or "family of blanks" in why}
        self.assertEqual(len(generic), 21)
        for name in NAMES - generic:
            self.assertTrue(name in ORIGIN or name in ORIGIN_UNDECIDED, name)
        self.assertLessEqual(set(ORIGIN_UNDECIDED), NAMES)
        self.assertFalse(set(ORIGIN_UNDECIDED) & set(ORIGIN))
        for name, candidates in ORIGIN_UNDECIDED.items():
            self.assertGreaterEqual(len(candidates), 2, name)  # two states can claim it
            self.assertEqual(len(set(candidates)), len(candidates), name)
        self.assertEqual(ORIGIN[".22 BB Cap"], "FR")  # Flobert 1845
        self.assertEqual(ORIGIN["6.5x53 mm R Mannlicher"], "AH")  # Steyr 1892, Romanian and Dutch service round
        self.assertEqual(origin(".338 Lapua Magnum"), ("WW", "Worldwide", "🌐"))
        self.assertEqual(origin(".300 Lapua Magnum"), ("FI", "Finland", "🇫🇮"))

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

    def test_municion_years_fill_unknown_introductions(self):
        years = {".17 Hornet": 2012, ".35 Winchester Self-Loading": 1905, ".401 Winchester Self-Loading": 1910,
                 ".375 Flanged Magnum Nitro Express": 1912, "9.3x72 mm R": 1892, "9x57 mm Mauser": 1890,
                 "10.3x60 mm R": 1919, "9x39 mm": 1980}
        for name, year in years.items():
            self.assertEqual(INTRODUCED[name][0], year, name)
            self.assertTrue(INTRODUCED[name][1].startswith("https://municion.org/producto/"), name)
            self.assertNotIn(name, INTRODUCED_UNKNOWN)

    def test_bullets_name_known_calibres_and_are_sourced(self):
        names = {s["name"] for _, items in CATALOGUE for s in items}
        for name, (kind, url) in BULLETS.items():
            self.assertIn(name, names)
            self.assertIn(kind, (LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP), name)
            self.assertTrue(url is None or url.startswith("https://"), name)
        self.assertEqual(BULLET_INFERRED, {"7 mm Blaser Magnum", ".300 Blaser Magnum", "8.5x55 mm Blaser",
                                           ".338 Blaser Magnum", ".375 Blaser Magnum", "9.3x66 mm Sako (.370 Sako Magnum)"})
        self.assertEqual(bullet("9x19 mm"), JACKETED)

    def test_rounds_older_than_jacketed_bullets_are_not_jacketed(self):
        # Jacketed bullets came with smokeless powder (Rubin 1882, Lebel 1886); the Swiss 1882 revolver
        # round was one of the first.
        for _, items in CATALOGUE:
            for s in items:
                year = INTRODUCED.get(s["name"], (None,))[0]
                if year and year < 1886 and s["oal"] > s["case"] and s["case"] and s["name"] != "7.5 mm Swiss Ordnance 1882":
                    self.assertNotEqual(bullet(s["name"]), JACKETED, s["name"])

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

    def test_case_materials(self):
        names = {s["name"] for _, items in CATALOGUE for s in items}
        for name, (material, url) in CASES.items():
            self.assertIn(name, names)
            self.assertIn(material, (COPPER, STEEL, NICKEL, PAPER, HYBRID), name)
            self.assertTrue(url.startswith("https://"), name)
        self.assertEqual(case_material(".44 Henry"), COPPER)
        self.assertEqual(case_material("5.45x39 mm"), STEEL)
        self.assertEqual(case_material(".577 Snider"), PAPER)
        self.assertEqual(case_material("9x19 mm"), BRASS)
        self.assertEqual(case_material(".277 SIG Fury"), HYBRID)

    def test_current_case_materials_differ_from_the_original(self):
        names = {s["name"] for _, items in CATALOGUE for s in items}
        for name, (materials, url) in CURRENT_CASES.items():
            self.assertIn(name, names)
            self.assertTrue(materials, name)
            self.assertNotIn(case_material(name), materials, name)
            self.assertTrue(set(materials) <= {BRASS, COPPER, STEEL, NICKEL, PAPER, HYBRID}, name)
            self.assertTrue(url.startswith("https://"), name)
        self.assertEqual(current_case_materials(".45-70 Government"), (BRASS,))
        self.assertEqual(current_case_materials("9x19 mm"), (STEEL,))
        self.assertEqual(current_case_materials("7.5x55 mm Swiss (GP 11)"), ())


    def test_bbs_are_loose_steel_or_plastic_balls(self):
        by_name = {s["name"]: s for _, items in CATALOGUE for s in items}
        for name, (material, url) in LOOSE_MATERIALS.items():
            self.assertIn(by_name[name]["kind"], (BALL, MINIE, PELLET), name)
            self.assertIn(material, (STEEL, PLASTIC), name)
            self.assertTrue(url.startswith("https://"), name)
        steel = by_name["4.4 mm Stahl-BB (.177 BB)"]
        self.assertEqual(steel["kind"], BALL)
        self.assertTrue(4.3 <= steel["bullet"] <= 4.4)  # 0.171-0.173 in, smaller than a 4.5 mm pellet
        self.assertEqual(loose_material("4.4 mm Stahl-BB (.177 BB)"), STEEL)
        self.assertEqual(loose_material("6 mm Airsoft-BB"), PLASTIC)
        self.assertEqual(loose_material(".50 Rundkugel (.490)"), LEAD)
        self.assertEqual(by_name["6 mm Airsoft-BB"]["bullet"], 6.0)
        self.assertEqual(by_name["8 mm Airsoft-BB"]["bullet"], 8.0)
        luftdruck = [s["name"] for cat, items in CATALOGUE if cat == "Luftdruck" for s in items]
        self.assertIn("6 mm Airsoft-BB", luftdruck)


if __name__ == "__main__":
    unittest.main()
