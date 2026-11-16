"""python3 -m unittest discover -s tests"""
import math, os, re, statistics, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import outline  # noqa: E402
import cartridges  # noqa: E402
from cartridges import SPITZER, ROUND, FLAT, PATCHED, CRIMPED, BALL_NOSE, RIMLESS, SEMI_RIMMED, BELTED, RIMMED, RIMFIRE, LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP, HOLLOW_POINT, STEEL, BRASS, HYBRID, PAPER, SHOT, CASES, BALL, MINIE, PELLET, bullet, jacket, case_material, current_case_materials, loose_material  # noqa: E402

PATH = re.compile(r"^M[\d.]+ [\d.]+( L[\d.]+ [\d.]+)* Z$")


def points(d):
    return [tuple(map(float, p.split())) for p in d[1:-2].split(" L")]


class GapTests(unittest.TestCase):
    def spec(self, name):
        return next(s for _, items in cartridges.ALL_CATALOGUE for s in items if s["name"] == name)

    def test_gaps_name_what_the_drawing_has_no_source_for(self):
        for name, gaps in [
                (".308 Winchester", ()),
                ("12/70", ()),  # its loaded length is SAAMI's
                (".56-52 Spencer Necked", ("measurements", "shoulder_angle")),  # shoulder_at estimated, 32 degrees
                (".69 Minié", ()),  # the Altered Musket drawing: 1.1 in long
                (".58 Minié", ()),  # the Harpers Ferry drawing: 1.05 in long
                ("4.5 mm Diabolo (.177)", ()),  # its length from RWS
                ("5.5 mm Diabolo (.22)", ()),
                ("7.5 mm Kadettenpatrone", ()),  # its length: Raven measured it (measured:raven)
                (".25 Stevens", ("rim_thickness",)),
                ("20x138 mm B", ()),  # its AECC drawing (2026-11-15)
                ("24x138 mm", ()),
                ("27x145 mm B", ("measurements", "groove", "rim_thickness")),  # no base: Jane's neck and the drawing's differ
                ("57x441 mm R", ("measurements", "rim_thickness"))]:  # no neck from any source
            with self.subTest(name):
                self.assertEqual(outline.gaps(self.spec(name)), gaps)
        for _, items in cartridges.ALL_CATALOGUE:
            for s in items:
                self.assertLessEqual(set(outline.gaps(s)), set(outline.GAPS), s["name"])

    def test_cannon_rounds_with_a_specimen_drawing_are_well_sourced(self):
        # 2026-11-15: eleven AECC drawings (municion.org) and naboje.org's 34x239 gave these their shoulders and
        # heads (each loading of the 23x152 B, 30x165 and 30x173 from its own drawing). The others lack a
        # drawing that shows the shoulder (or, the 27x145 mm B, one that fits Jane's neck).
        drawn = {"20x102 mm", "20x110 mm Hispano", "20x138 mm B", "20x139 mm", "23x152 mm B VYa", "23x152 mm B ZU-23",
                 "24x138 mm", "25x137 mm", "30x113 mm B", "30x165 mm GSh-30", "30x165 mm 2A42", "30x173 mm GAU-8",
                 "30x173 mm KCA", "34x239 mm", "35x228 mm"}
        cannon = dict(cartridges.ALL_CATALOGUE)["Kanone"]
        self.assertEqual({s["name"] for s in cannon if outline.well_sourced(s)}, drawn)

    def test_a_crimped_blanks_mouth_is_a_sketch(self):
        # Raven 2026-11-14: "treat the crimp as a sketch". No sheet gives a star crimp's size: the mouth stays
        # listed as unsourced, but it keeps no blank from being well sourced.
        for name in (".22 Long Blanc", "6 mm Flobert Blanc", "9 mm R Blanc", ".320 Court Blanc", ".45 K Blanc"):
            with self.subTest(name):
                self.assertEqual(cartridges.unsourced(name), ("mouth",))
                self.assertEqual(outline.gaps(self.spec(name)), ())
        s = dict(self.spec(".45 K Blanc"), profile=FLAT)  # on any other profile it would still be a gap
        self.assertEqual(outline.gaps(s)[:1], ("measurements",))

    def test_gaps_follow_the_tables(self):
        for _, s in outline.specs():
            gaps, name = outline.gaps(s), s["name"]
            cartridge = s["kind"] not in (SHOT, BALL, MINIE, PELLET)
            crimp = {"mouth"} if s["profile"] == CRIMPED else set()  # a sketch (Raven 2026-11-14)
            self.assertEqual("measurements" in gaps, bool(set(cartridges.unsourced(name)) - crimp), name)
            self.assertEqual("rim_thickness" in gaps, cartridge and name not in cartridges.RIM_THICKNESS, name)
            self.assertEqual("groove" in gaps, s["kind"] in (RIMLESS, SEMI_RIMMED, BELTED)
                             and name not in cartridges.CASE_HEADS, name)
            self.assertEqual("shoulder_angle" in gaps, cartridge and bool(s["shoulder"]) and s["profile"] != CRIMPED
                             and name not in cartridges.SHOULDER_ANGLES, name)

    def test_a_shoulder_the_drawing_moves_back_is_a_gap(self):
        s = dict(self.spec(".308 Winchester"))
        self.assertEqual(outline.gaps(s), ())
        s["sh_at"] = s["case"] - outline.shoulder_run(s) - 1.0  # 1 mm of neck: under MIN_NECK
        self.assertEqual(outline.gaps(s), ("shoulder_moved",))
        s["name"] = ".56-52 Spencer Necked"  # also beside a measurement without a source (at that calibre's angle)
        s["sh_at"] = s["case"] - outline.shoulder_run(s) - 1.0
        self.assertEqual(outline.gaps(s)[0], "measurements")
        self.assertIn("shoulder_moved", outline.gaps(s))
        self.assertLess(max(h for r, h in outline.case_profile(s) if r == s["shoulder"] / 2), s["sh_at"])

    def test_cip_sheets_source_popular_calibres(self):
        # Popular calibres that failed the well-sourced rule on 2026-11-14 and have a C.I.P. sheet.
        for name, groove in [(".408 CheyTac", 13.8), (".375 CheyTac", 13.8), (".458 SOCOM", 10.34), ("7.5 FK", 8.6),
                             (".32 Remington", 9.09), (".351 Winchester Self-Loading", 9.02), (".50-70 Government", None)]:
            with self.subTest(name):
                self.assertTrue(outline.well_sourced(self.spec(name)))
                self.assertEqual(outline.gaps(self.spec(name)), ())
                if groove:
                    self.assertEqual(cartridges.case_head(name)[2], groove)  # E1

    def test_aecc_drawings_source_popular_calibres(self):
        # Popular calibres that failed the well-sourced rule on 2026-11-14, now with a head from an AECC drawing
        # (municion.org) or, for the .338 Weatherby RPM, from the SAAMI drawing of the 6.5 Weatherby RPM, its case.
        for name, groove in [("7.7x58 mm Arisaka", 10.32), ("8 mm Nambu", 9.22), ("9x23 mm Largo", 7.73),
                             (".22 TCM", 8.2), (".50 Beowulf", 9.23), (".55 Boys", 17.18), (".338 Weatherby RPM", 10.39)]:
            with self.subTest(name):
                self.assertEqual(outline.gaps(self.spec(name)), ())
                self.assertEqual(cartridges.case_head(name)[2], groove)
        self.assertEqual(cartridges.case_head(".338 Weatherby RPM"), cartridges.case_head("6.5 Weatherby RPM"))
        # The Boys' belt (21.59 mm) stands over its 20.3 mm rim; the drawing's belt ends 9 mm up.
        boys = [(round(r, 4), round(h, 4)) for r, h in outline.case_profile(self.spec(".55 Boys"))[:7]]
        self.assertEqual(boys, [(10.15, 0), (10.15, 2.08), (8.59, 2.08), (8.59, 3.08), (10.795, 4.9302), (10.795, 9.0),
                                (10.07, 9.0)])

    def test_aecc_drawings_source_pistol_heads(self):
        # Twelve pistol rounds with no C.I.P. or SAAMI sheet: rim thickness, ramp top, groove and ramp angle from
        # the AECC drawing (municion.org). A book's rim thickness stays where it is within 0.3 mm of the drawing's.
        heads = {".35 S&W Auto": (1.09, 3.34, 7.56, 24.0), ".30 Borchardt": (1.1, 2.5, 8.55, 42.0),
                 "2.7 mm Kolibri": (0.41, 1.31, 3.09, 32.0), "3 mm Kolibri": (0.85, 1.48, 3.38, 44.0),
                 "4.25 mm Liliput": (0.54, 1.35, 4.37, 34.0), "7 mm Nambu": (0.98, 2.53, 7.81, 36.0),
                 # The book's rim was .025 and .030 in., over 0.3 mm thinner than the drawing's: the drawing's.
                 "6.5 mm Bergmann": (1.0, 1.9, 8.63, 35.0), "7.63 mm Mannlicher": (1.09, 2.4, 7.81, 50.0),
                 # The book's rim: .040, .040, .025 and .044 in. (the drawings: 1.07, 1.00, 0.53 and 1.13).
                 ".45 Mars Long": (1.02, 3.55, 10.25, 38.0), ".45 Mars Short": (1.02, 3.1, 10.3, 40.0),
                 "5 mm Clement": (0.64, 1.75, 5.61, 56.0), "5.8x21 mm DAP92": (1.12, 2.94, 6.79, 31.0)}
        for name, head in heads.items():
            with self.subTest(name):
                self.assertEqual(outline.gaps(self.spec(name)), ())
                self.assertEqual(cartridges.case_head(name), head)
                self.assertIn("municion.org", cartridges.sources(name, "case_head")[-1])
        for name in ("6.5 mm Bergmann", "7.63 mm Mannlicher"):
            self.assertEqual(len(cartridges.sources(name, "case_head")), 1)  # the book no longer backs a value
        # The smallest head: the 2.7 mm Kolibri's rim is 0.41 mm thick and its groove ends 1.31 mm up.
        kolibri = [(round(r, 3), round(h, 3)) for r, h in outline.case_profile(self.spec("2.7 mm Kolibri"))[:5]]
        self.assertEqual(kolibri, [(1.78, 0), (1.78, 0.41), (1.545, 0.41), (1.545, 0.934), (1.78, 1.31)])
        # The other two Mars rounds stay on the generic head: their drawings do not fit the book's rim and base.
        for name in (".360 Mars", "8.5 mm Mars"):
            self.assertIn("groove", outline.gaps(self.spec(name)))

    def test_aecc_drawings_source_more_pistol_heads(self):
        # Seven more pistol rounds measured from Cartridges of the World, which gives no groove: the head from the
        # AECC drawing (municion.org), behind the book's rim thickness where the table has one.
        heads = {".455 Webley Automatic": (1.18, 4.0, 11.06, 24.0), ".50 GI": (1.22, 5.3, 9.83, 30.0),
                 "5 mm Bergmann": (0.51, 1.35, 6.4, 47.0), "7.65 mm Roth-Sauer": (1.1, 2.95, 6.93, 43.0),
                 "9 mm Winchester Magnum": (1.17, 3.1, 8.71, 28.0), "9.8 mm Auto Colt": (1.21, 3.65, 8.7, 28.0),
                 ".45 Remington Thompson": (1.12, 4.33, 9.99, 23.0)}
        for name, head in heads.items():
            with self.subTest(name):
                self.assertEqual(outline.gaps(self.spec(name)), ())
                self.assertEqual(cartridges.case_head(name), head)
                self.assertIn("municion.org", cartridges.sources(name, "case_head")[-1])
        for name in (".50 GI", "5 mm Bergmann", "9 mm Winchester Magnum", ".45 Remington Thompson"):  # the book's rim
            self.assertTrue(cartridges.sources(name, "case_head")[0].startswith("book:cotw-18 p. "), name)
        # The .50 GI's rebated rim (12.19 mm on a 13.36 mm body): the groove's ramp climbs past the rim on to the body.
        s = self.spec(".50 GI")
        self.assertEqual([(round(r, 4), round(h, 4)) for r, h in outline.case_profile(s)[:5]],
                         [(6.095, 0), (6.095, 1.22), (4.915, 1.22), (4.915, 2.2429), (6.68, 5.3)])

    def test_aecc_drawings_source_sporting_rifle_heads(self):
        # Sporting rifle rounds of about 1900 to 1940 with no C.I.P. sheet: the head from the AECC drawing
        # (municion.org). Donnelly's rim thickness stays on the two BSA rounds (within 0.3 mm of the drawing's); on
        # the .400/375 it is .062 in. against the drawing's 1.00, so that head is the drawing's throughout.
        heads = {".242 Rimless Nitro Express": (1.19, 3.56, 10.41, 26.0), ".303 Magnum": (1.18, 2.65, 12.2, 52.0),
                 ".425 Westley Richards Magnum": (1.12, 3.52, 10.39, 50.0),
                 "11.2x60 mm Schüler": (1.26, 3.9, 10.25, 49.0), "11.2x72 mm Schüler": (1.2, 4.05, 10.27, 44.0),
                 "6.5x61 mm Mauser": (1.45, 3.6, 10.43, 36.0), "8x71 mm Peterlongo": (1.23, 3.0, 10.32, 37.0),
                 "9x63 mm": (1.2, 3.1, 10.2, 46.0), "9x71 mm Peterlongo": (1.2, 3.25, 10.22, 46.0),
                 # Belted: the ramp's top is the front of the belt (HL + LW on the drawing).
                 ".26 BSA": (1.24, 5.3, 11.92, 37.0), ".33 BSA": (1.3, 5.05, 11.69, 40.0),
                 ".400/375 Belted Nitro Express": (1.0, 5.42, 10.3, 39.0),
                 "7x73 mm Vom Hofe Belted": (1.12, 4.55, 11.98, 47.0)}
        for name, head in heads.items():
            with self.subTest(name):
                self.assertEqual(outline.gaps(self.spec(name)), ())
                self.assertEqual(cartridges.case_head(name), head)
                self.assertIn("municion.org", cartridges.sources(name, "case_head")[-1])
        # A head from the drawing does not close the other gaps: the 10.75x57's drawing shows no shoulder.
        self.assertEqual(cartridges.case_head("10.75x57 mm Mannlicher"), (1.2, 3.2, 10.0, 29.0))
        self.assertEqual(outline.gaps(self.spec("10.75x57 mm Mannlicher")), ("measurements", "shoulder_angle"))
        # The .280 Jeffery is the .333 Jeffery case necked down: the head of the .333's C.I.P. sheet.
        self.assertEqual(outline.gaps(self.spec(".280 Jeffery")), ())
        self.assertEqual(cartridges.case_head(".280 Jeffery"), cartridges.case_head(".333 Jeffery Rimless"))
        self.assertEqual(cartridges.sources(".280 Jeffery", "case_head"),
                         ["https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page129.pdf", "book:cotw-18 p. 582"])
        # Two drawings show a belt wider than the rim: 12.06 over 11.84 mm and 13.88 over 13.54 mm.
        for name, belt, front in [(".400/375 Belted Nitro Express", 12.06, 5.42), ("7x73 mm Vom Hofe Belted", 13.88, 4.55)]:
            s = self.spec(name)
            self.assertEqual(s["belt"], belt)
            self.assertEqual(outline.case_profile(s)[5], (belt / 2, front))

    def test_aecc_drawings_and_parent_cases_source_american_magnums(self):
        # American magnums and wildcats of 1913 to 2012 without a C.I.P. or SAAMI sheet. Twelve have the groove of their
        # own AECC drawing (municion.org), behind the book's rim thickness where one gives it. The drawings of the 7 mm
        # and .338 Canadian Magnum carry the range's earlier name, Imperial Magnum.
        heads = {".30 Newton": (1.28, 3.23, 11.57, 41.0), ".35 Newton": (1.17, 3.1, 11.65, 42.0),
                 "7 mm Dakota": (1.07, 3.25, 12.11, 33.0), ".300 Dakota": (1.17, 3.3, 12.12, 35.0),
                 ".330 Dakota": (1.14, 3.28, 12.13, 43.0), ".375 Dakota": (1.17, 3.2, 12.08, 42.0),
                 "7 mm Canadian Magnum": (1.17, 3.3, 11.65, 46.0), ".338 Canadian Magnum": (1.17, 3.55, 11.8, 38.0),
                 ".458 Canadian Magnum": (1.17, 3.5, 11.85, 34.0), ".475 Bishop Short Magnum": (1.37, 4.7, 10.4, 46.0),
                 ".500 Phantom": (1.31, 3.9, 11.75, 57.0), ".577 Tyrannosaur": (1.52, 3.5, 16.1, 38.0)}
        for name, head in heads.items():
            with self.subTest(name):
                self.assertEqual(outline.gaps(self.spec(name)), ())
                self.assertEqual(cartridges.case_head(name), head)
                self.assertIn("municion.org", cartridges.sources(name, "case_head")[-1])
        # Two are a parent case with a C.I.P. sheet: the whole head is the parent's.
        for name, parent, page in [(".450 Dakota", ".416 Rigby", "book:cotw-18 p. 435"),
                                   (".338 Lehigh", "6.5 mm Grendel", "book:cotw-18 p. 402")]:
            with self.subTest(name):
                self.assertEqual(outline.gaps(self.spec(name)), ())
                self.assertEqual(cartridges.case_head(name), cartridges.case_head(parent))
                self.assertEqual(cartridges.sources(name, "case_head"), cartridges.sources(parent, "case_head") + [page])
        # The .416 Dakota has no drawing of its own: the groove of the .375 Dakota's drawing (the same altered .404
        # Jeffery head on a shorter case) behind its own rim thickness.
        self.assertEqual(cartridges.case_head(".416 Dakota"), (1.07,) + cartridges.case_head(".375 Dakota")[1:])
        self.assertEqual(cartridges.sources(".416 Dakota", "case_head"),
                         ["book:cotw-18 p. 453", "https://municion.org/producto/375-dakota/", "book:cotw-18 p. 424"])
        self.assertEqual(outline.gaps(self.spec(".416 Dakota")), ())
        # The .50-115 Bullard's drawing gives its rim only.
        self.assertEqual(cartridges.rim_thickness(".50-115 Bullard"), 1.5)
        self.assertIn("groove", outline.gaps(self.spec(".50-115 Bullard")))
        # 7 mm Long Range Magnum: the shoulder starts where its drawing shows it.
        self.assertEqual(self.spec("7 mm Long Range Magnum")["sh_at"], 49.92)
        self.assertEqual(outline.gaps(self.spec("7 mm Long Range Magnum")), ())

    def test_aecc_drawings_source_military_rifle_rounds(self):
        # Service and trial rifle rounds of 1893 to 1987 without a C.I.P. sheet: the head from the AECC drawing
        # (municion.org), behind the book's rim thickness on the 4.85 mm British, the Sturtevant and the Daudeteau.
        heads = {".276 Enfield": (1.2, 3.36, 11.16, 43.0), ".280 British": (1.21, 3.46, 10.04, 33.0),
                 "7.92x107 mm DS": (1.54, 3.8, 14.38, 40.0), "4.85x49 mm British": (1.04, 3.1, 8.35, 29.0),
                 "5x58 mm Sturtevant": (1.15, 3.2, 10.2, 38.0), "6 mm Lee Navy": (1.4, 3.0, 9.65, 49.0),
                 "6 mm SAW": (1.18, 3.54, 8.8, 27.0), "8x59 mm Breda": (1.4, 3.5, 10.36, 48.0),
                 "8x63 mm Swedish": (1.42, 3.25, 10.34, 52.0), "5.8x42 mm": (1.42, 3.45, 8.64, 45.0),
                 ".276 Pedersen": (1.2, 3.79, 9.6, 37.0)}
        for name, head in heads.items():
            with self.subTest(name):
                self.assertEqual(outline.gaps(self.spec(name)), ())
                self.assertEqual(cartridges.case_head(name), head)
                self.assertIn("municion.org", cartridges.sources(name, "case_head")[-1])
        # The Daudeteau's drawing does not fit the book's shoulder, so only its head is taken. The book's rim
        # thickness (.065 in. in the military table) is within 0.3 mm of the drawing's 1.80 and stays.
        self.assertEqual(cartridges.case_head("6.5x53.5 mm SR Daudeteau"), (1.65, 3.25, 11.31, 39.0))
        self.assertEqual(cartridges.sources("6.5x53.5 mm SR Daudeteau", "case_head"),
                         ["book:cotw-18 p. 573", "https://municion.org/producto/65-x-53-sr-daudeteau-n12/"])
        self.assertEqual(outline.gaps(self.spec("6.5x53.5 mm SR Daudeteau")), ("measurements", "shoulder_angle"))
        # The .276 Pedersen (the PD-42 case) is drawn with its own shoulder now, 10.8 degrees from 40.95 mm.
        self.assertEqual(cartridges.shoulder_angle(".276 Pedersen"), 10.8)
        # Shoulder starts that were estimates, now case_length - (CL - SL) of the drawing; the 5.8x42's bullet.
        for name, start in [("6.5x53 mm R Mannlicher", 41.15), ("8x58 mm R Danish Krag", 41.3), (".276 Pedersen", 40.95)]:
            with self.subTest(name):
                self.assertEqual(self.spec(name)["sh_at"], start)
                self.assertEqual(cartridges.unsourced(name), ())
                self.assertEqual(outline.gaps(self.spec(name)), ())
        self.assertEqual(cartridges.unsourced("5.8x42 mm"), ())
        self.assertIn("municion.org", cartridges.sources("5.8x42 mm", "mm")[-1])

    def test_aecc_drawings_source_lazzeroni_rounds(self):
        # Lazzeroni's rounds without a C.I.P. sheet (the Firebird and the Warbird have one). Twelve take the groove
        # and the shoulder's start from their AECC drawing (municion.org): the groove behind the rim thickness of
        # Cartridges of the World, the start (case_length - (CL - SL)) under the book's 30-degree shoulder.
        drawn = {"10.57 Lazzeroni Maverick": ((1.52, 3.8, 12.7, 46.0), 39.67),
                 "10.57 Lazzeroni Meteor": ((1.52, 3.5, 12.66, 45.0), 59.21),
                 "12.04 Bibamufu": ((1.52, 3.56, 13.25, 42.0), 59.0),
                 "7.21 Lazzeroni Firehawk": ((1.4, 3.5, 12.25, 42.0), 59.09),
                 "7.21 Lazzeroni Tomahawk": ((1.52, 3.85, 12.72, 42.0), 39.69),
                 "7.82 Lazzeroni Patriot": ((1.52, 3.9, 12.67, 36.0), 39.71),
                 "8.59 Lazzeroni Galaxy": ((1.52, 3.7, 12.72, 44.0), 39.57),
                 "8.59 Lazzeroni Titan": ((1.52, 3.5, 13.0, 43.0), 59.04),
                 "9.53 Lazzeroni Hellcat": ((1.52, 3.8, 12.7, 46.0), 39.95),
                 "9.53 Lazzeroni Saturn": ((1.52, 4.0, 12.55, 38.0), 58.91),
                 "6.17 Lazzeroni Spitfire": ((1.27, 3.12, 11.88, 48.0), 40.66),
                 "6.71 Lazzeroni Phantom": ((1.4, 3.2, 12.03, 53.0), 40.19)}
        for name, (head, start) in drawn.items():
            with self.subTest(name):
                self.assertEqual(outline.gaps(self.spec(name)), ())
                self.assertEqual(cartridges.unsourced(name), ())
                self.assertEqual(cartridges.case_head(name), head)
                self.assertEqual(self.spec(name)["sh_at"], start)
                self.assertEqual(cartridges.shoulder_angle(name), 30)
                self.assertTrue(cartridges.sources(name, "case_head")[0].startswith("book:cotw-18 p. "))
                self.assertIn("municion.org", cartridges.sources(name, "case_head")[1])
                self.assertIn("municion.org", cartridges.sources(name, "mm")[-1])
        # The Scramjet's drawing has a 21-degree cone that starts 2.5 mm before the book's 30-degree shoulder would:
        # only its head is taken. The Eagle is the Patriot's case necked up and has that head; no drawing of its own.
        self.assertEqual(cartridges.case_head("6.53 Lazzeroni Scramjet"), (1.4, 3.22, 11.83, 52.0))
        self.assertEqual(cartridges.case_head("9.09 Lazzeroni Eagle"), cartridges.case_head("7.82 Lazzeroni Patriot"))
        self.assertEqual(cartridges.sources("9.09 Lazzeroni Eagle", "case_head")[1:],
                         ["https://municion.org/producto/782-mm-lazzeroni-patriot/", "book:cotw-18 p. 410"])
        for name in ("6.53 Lazzeroni Scramjet", "9.09 Lazzeroni Eagle"):
            self.assertEqual(outline.gaps(self.spec(name)), ("measurements",))
            self.assertEqual(cartridges.unsourced(name), ("shoulder_at",))
        # The Flash and the Blackbird have no drawing.
        for name in ("6.17 Lazzeroni Flash", "6.71 Lazzeroni Blackbird"):
            self.assertEqual(outline.gaps(self.spec(name)), ("measurements", "groove"))

    def test_aecc_drawings_source_old_rimmed_rounds(self):
        # Blackpowder and early nitro rounds measured from Cartridges of the World, which gives no shoulder start and,
        # for most of these, no rim thickness. The .500/450 No. 1 Express takes the shoulder (start and half angle)
        # and the rim thickness from its AECC drawing (municion.org).
        name = ".500/450 No. 1 Express"
        self.assertEqual(outline.gaps(self.spec(name)), ())
        self.assertEqual(cartridges.unsourced(name), ())
        self.assertEqual((self.spec(name)["sh_at"], cartridges.shoulder_angle(name)), (47.3, 9.9))
        self.assertEqual(cartridges.rim_thickness(name), 1.45)
        for part in ("mm", "case_head"):
            self.assertIn("municion.org", cartridges.sources(name, part)[-1])
        # The Italian Vetterli takes the shoulder from its drawing and keeps the book's rim thickness.
        name = "10.4x47 mm R Italian Vetterli"
        self.assertEqual(outline.gaps(self.spec(name)), ())
        self.assertEqual((self.spec(name)["sh_at"], cartridges.shoulder_angle(name)), (34.75, 13.9))
        self.assertEqual(cartridges.rim_thickness(name), 1.47)
        self.assertEqual(cartridges.sources(name, "mm")[-1],
                         "https://municion.org/producto/1035-x-47-r-italian-vetterli-m-1870-71-m-1890/")
        self.assertEqual(cartridges.SHOULDER_ANGLES[name][1], cartridges.sources(name, "mm")[-1])
        # The .25-45 Sharps keeps the book's 23 degrees and takes the drawing's shoulder start.
        self.assertEqual(self.spec(".25-45 Sharps")["sh_at"], 36.53)
        self.assertEqual(cartridges.shoulder_angle(".25-45 Sharps"), 23)
        self.assertEqual(outline.gaps(self.spec(".25-45 Sharps")), ())
        # The .32-30 Remington takes the shoulder and the rim thickness from its drawing.
        name = ".32-30 Remington"
        self.assertEqual(outline.gaps(self.spec(name)), ())
        self.assertEqual((self.spec(name)["sh_at"], cartridges.shoulder_angle(name)), (31.18, 4.0))
        self.assertEqual(cartridges.rim_thickness(name), 1.39)
        # The Russian Berdan takes the shoulder from its drawing; the book's rim thickness stays, and the drawing's
        # head (13.09 mm against the book's 14.40) is not used.
        name = "10.75x58 mm R Russian Berdan"
        self.assertEqual(outline.gaps(self.spec(name)), ())
        self.assertEqual((self.spec(name)["sh_at"], cartridges.shoulder_angle(name)), (38.45, 7.9))
        self.assertEqual(cartridges.rim_thickness(name), 2.03)
        self.assertEqual(cartridges.sources(name, "case_head"), ["book:cotw-18 p. 574"])
        self.assertIn("municion.org", cartridges.sources(name, "mm")[-1])
        # The two Comblain rounds keep their estimates. The drawing with the sizes of the 11x53 is the Brazilian
        # Model 1889, whose page says it differs from the Belgian round in its shorter neck; three drawings of other
        # rounds fit the 11.4x50 and start the shoulder up to 6.4 mm apart. No drawing is cited for either.
        for name, start, gaps in [
                ("11.4x50 mm R Brazilian Comblain", 39.1, ("measurements", "shoulder_angle", "rim_thickness")),
                ("11x53 mm R Comblain", 40.8, ("measurements", "shoulder_angle"))]:
            with self.subTest(name):
                s = self.spec(name)
                self.assertEqual(outline.gaps(s), gaps)
                self.assertFalse(outline.well_sourced(s))
                self.assertEqual(s["sh_at"], start)
                self.assertEqual(cartridges.unsourced(name), ("shoulder_at",))
                self.assertEqual(cartridges.shoulder_angle(name), cartridges.DEFAULT_SHOULDER_ANGLE)
                self.assertEqual(cartridges.sources(name, "mm"), ["book:cotw-18 p. 574"])
        self.assertIsNone(cartridges.rim_thickness("11.4x50 mm R Brazilian Comblain"))
        self.assertEqual(cartridges.rim_thickness("11x53 mm R Comblain"), 2.08)
        self.assertEqual(cartridges.sources("11x53 mm R Comblain", "case_head"), ["book:cotw-18 p. 574"])
        # Two drawings fit the book's rim and base but not its shoulder or case length: the rim thickness only.
        # (Four more give their shoulder in the next two tests.)
        for name, rim in [(".32-40 Remington", 1.6), (".38-70 Winchester", 1.72)]:
            with self.subTest(name):
                self.assertEqual(cartridges.rim_thickness(name), rim)
                self.assertIn("municion.org", cartridges.sources(name, "case_head")[0])
                self.assertEqual(outline.gaps(self.spec(name)), ("measurements", "shoulder_angle"))
                self.assertEqual(cartridges.unsourced(name), ("shoulder_at",))
        for name, rim in [(".38-90 Winchester Express", 1.68), (".40-70 Peabody What Cheer", 1.87),
                          (".500/450 Magnum Express", 1.04), (".500/450 Nitro Express", 1.04)]:
            self.assertEqual(cartridges.rim_thickness(name), rim)
            self.assertIn("municion.org", cartridges.sources(name, "case_head")[0])
        # The two 3¼ in. .500/450 loads share one case and one drawing.
        self.assertEqual(outline.case_profile(self.spec(".500/450 Magnum Express")),
                         outline.case_profile(self.spec(".500/450 Nitro Express")))

    def test_shallow_shoulders_run_over_the_drawings_shoulder_length(self):
        # These AECC drawings fit the file (case within 1.5 mm, shoulder and neck within 0.5 mm), but the specimen's
        # own cone, drawn between the file's diameters, would leave a neck more than 1.5 mm longer or shorter than the
        # specimen's: on a shallow cone a small difference in diameter is a long one in length. The half angle runs
        # between the file's diameters over the drawing's shoulder length (CL - NL - SL) instead, so the shoulder
        # starts and ends where the drawing shows. The first two share one case and one drawing; the other seven had
        # the specimen's cone until the walk in test_every_recorded_municion_reading_keeps_its_neck found them.
        # name: (shoulder_at, half angle, the specimen's own cone, the drawing's SØ, NØ, SL, NL, CL)
        shallow = {
            ".500/450 Magnum Express": (61.08, 2.5, 4.4, 13.19, 12.25, 61.0, 15.4, 82.47),
            ".500/450 Nitro Express": (61.08, 2.5, 4.4, 13.19, 12.25, 61.0, 15.4, 82.47),
            "11.2x60 mm Schüler": (34.44, 5.5, 3.8, 12.76, 11.95, 35.0, 19.1, 60.25),
            "11.43x50 mm R Egyptian Remington": (34.19, 14.3, 9.5, 13.56, 12.51, 33.44, 11.96, 48.53),
            ".32-40 Bullard": (23.86, 6.4, 5.1, 10.22, 8.6, 23.6, 14.0, 46.73),
            ".40-110 Winchester Express": (60.45, 7.9, 6.1, 12.2, 11.09, 60.5, 16.9, 82.6),
            ".40-70 Sharps Necked": (35.68, 7.8, 5.9, 12.42, 11.01, 35.7, 14.6, 57.17),
            ".577 Tyrannosaur": (59.55, 10.3, 7.4, 16.71, 15.64, 59.3, 12.3, 75.7),
            "9.3x65 mm R Collath": (55.16, 16.4, 5.9, 10.22, 9.9, 55.1, 8.3, 64.96),
        }
        for name, (start, angle, own, so, no, sl, nl, cl) in shallow.items():
            with self.subTest(name):
                s = self.spec(name)
                # Nothing is left open but, on these four, a rim thickness that no source gives.
                no_rim = {".32-40 Bullard", ".40-110 Winchester Express", ".40-70 Sharps Necked", "9.3x65 mm R Collath"}
                self.assertEqual(outline.gaps(s), ("rim_thickness",) if name in no_rim else ())
                self.assertEqual((s["sh_at"], cartridges.shoulder_angle(name)), (start, angle))
                self.assertLess(abs(cl - s["case"]), 1.5)
                self.assertLess(max(abs(so - s["shoulder"]), abs(no - s["neck"])), 0.5)
                self.assertAlmostEqual(s["sh_at"], s["case"] - (cl - sl), delta=0.005)
                run = cl - nl - sl
                step = (s["shoulder"] - s["neck"]) / 2
                self.assertAlmostEqual(math.degrees(math.atan((so - no) / 2 / run)), own, delta=0.05)
                self.assertAlmostEqual(math.degrees(math.atan(step / run)), angle, delta=0.05)
                # What test_necks_start_where_the_municion_drawings_show would find with the specimen's own cone.
                own_neck = s["sh_at"] + step / math.tan(math.radians(own))
                self.assertGreater(abs((s["case"] - own_neck) - nl), 1.5)
                self.assertEqual(cartridges.sources(name, "mm")[-1], cartridges.SHOULDER_ANGLES[name][1])
                self.assertIn("municion.org", cartridges.SHOULDER_ANGLES[name][1])

    def test_shoulders_that_donnelly_and_an_aecc_drawing_agree_on(self):
        # An AECC drawing that misses a size limit (shoulder diameter, case length) gives the shoulder all the same
        # where Donnelly's Handloader's Manual prints the same shoulder: its start (his J) and its end (J + K) within
        # 0.5 mm of the drawing's, both taken from the mouth. shoulder_at is the drawing's SL carried from the mouth
        # and the half angle runs between the file's diameters over the drawing's shoulder length (CL - NL - SL).
        # His printed angles are not used.
        # His J runs from the head and is set beside shoulder_at as it is, so his case (A) must be the file's.
        # name: (shoulder_at, half angle, Donnelly's A, J and K in inches, his page, the drawing's SL, NL, CL)
        agreed = {
            ".38-90 Winchester Express": (59.95, 9.7, 3.25, 2.36, 0.24, 489, 60.0, 17.0, 82.6),
            ".40-70 Peabody What Cheer": (25.15, 8.9, 1.76, 0.988, 0.392, 500, 22.9, 9.6, 42.45),
            "11x52 mm R Beaumont M71/78": (34.67, 7.1, 2.04, 1.36, 0.18, 554, 33.9, 12.65, 51.05),
        }
        for name, (start, angle, a, j, k, page, sl, nl, cl) in agreed.items():
            with self.subTest(name):
                s = self.spec(name)
                self.assertEqual(outline.gaps(s), ())
                self.assertEqual(cartridges.unsourced(name), ())
                self.assertEqual((s["sh_at"], cartridges.shoulder_angle(name)), (start, angle))
                self.assertAlmostEqual(a * 25.4, s["case"], delta=0.13)  # two decimals of an inch
                self.assertAlmostEqual(s["sh_at"], s["case"] - (cl - sl), delta=0.005)
                self.assertLess(abs(s["sh_at"] - j * 25.4), 0.5)
                self.assertLess(abs((s["case"] - nl) - (j + k) * 25.4), 0.5)
                run = cl - nl - sl
                cone = math.degrees(math.atan((s["shoulder"] - s["neck"]) / 2 / run))
                self.assertAlmostEqual(cone, angle, delta=0.05)
                top = s["neck"] / 2  # the drawn neck is the specimen's, measured from the mouth
                neck_start = next(h for r, h in outline.case_profile(s) if abs(r - top) < 1e-9 and h > s["sh_at"])
                self.assertLess(abs((s["case"] - neck_start) - nl), 0.1)
                found = cartridges.sources(name, "mm")
                self.assertIn("municion.org", found[1])
                self.assertEqual(found[2], "book:donnelly p. %d" % page)
                self.assertIn("municion.org", cartridges.SHOULDER_ANGLES[name][1])
        # Donnelly alone is no source for a shoulder: these have an entry of his and no drawing that shows theirs. The
        # Daudeteau's drawing starts the shoulder where he does (0.14 mm apart) but ends it 0.95 mm later. The drawings
        # that fit the two Comblain rounds are of other rounds (test_aecc_drawings_source_old_rimmed_rounds).
        for name in (".45-100 Remington Necked", "10.25x69 mm R Hunting-Express", "6x57 mm Mauser",
                     "10.75x57 mm Mannlicher", ".50-115 Bullard", "6.5x53.5 mm SR Daudeteau",
                     "11x53 mm R Comblain", "11.4x50 mm R Brazilian Comblain"):
            self.assertIn(name, OutlineTests.SHOULDER_UNSOURCED)
            self.assertEqual(cartridges.unsourced(name), ("shoulder_at",))

    def test_aecc_drawings_filed_under_other_names(self):
        # AECC drawings that municion.org files under a name the file does not carry, found through the pages' other
        # names, the list of all pages and the catalogue codes: the .577/500 Nitro Express as «.577/.500 Express
        # 3 1/8″», the 6x58 mm Forster as «6,2 x 58 Förster», the .416 Rimmed as «.416 Chapuis» (the page gives
        # «.416 Rimmed» as its other name). The limits are the AECC rule's: case within 1.5 mm, rim, base, shoulder
        # and neck within 0.5 mm. shoulder_at is SL carried from the mouth and the half angle the specimen's cone.
        # name: (shoulder_at, half angle, page, the drawing's RØ, HØ, SØ, NØ, SL, NL, CL)
        drawings = {
            ".577/500 Nitro Express": (59.96, 8.9, "577-500-express-3-1-8",
                                       18.42, 16.36, 14.83, 13.56, 59.85, 15.5, 79.39),
            "6x58 mm Forster": (41.27, 13.4, "62-x-58-forster", 11.8, 11.87, 10.93, 7.07, 41.8, 8.05, 57.93),
            ".416 Rimmed": (69.12, 16.1, "416-chapuis", 16.57, 14.64, 13.9, 11.18, 69.0, 10.0, 83.7),
        }
        for name, (start, angle, page, rim, base, so, no, sl, nl, cl) in drawings.items():
            with self.subTest(name):
                s = self.spec(name)
                self.assertEqual(outline.gaps(s), ())
                self.assertEqual(cartridges.unsourced(name), ())
                self.assertEqual((s["sh_at"], cartridges.shoulder_angle(name)), (start, angle))
                self.assertLess(abs(cl - s["case"]), 1.5)
                sizes = [(rim, "rim"), (base, "base"), (so, "shoulder"), (no, "neck")]
                self.assertLess(max(abs(size - s[key]) for size, key in sizes), 0.5)
                self.assertAlmostEqual(s["sh_at"], s["case"] - (cl - sl), delta=0.005)
                self.assertAlmostEqual(math.degrees(math.atan((so - no) / 2 / (cl - nl - sl))), angle, delta=0.05)
                url = "https://municion.org/producto/%s/" % page
                self.assertEqual(cartridges.sources(name, "mm")[-1], url)
                self.assertEqual(cartridges.SHOULDER_ANGLES[name][1], url)
        # Two heads, as the README takes a head from an AECC drawing: rim and head within 0.5 mm of the file's, the
        # book's rim thickness stays within 0.3 mm of the drawing's RT, the ramp angle from HL = RT + GW +
        # ((HØ - GØ)/2)/tan(angle). The .30 USA Rimless is filed as «.30 Blake» (other name «.30 Krag Rimless»; UMC
        # loaded it for the Blake rifle, COTW 18 p. 197).
        # name: (the head, page, the book's page, the drawing's RØ, HØ, RT, HL, GØ, GW)
        heads = {
            "6x58 mm Forster": ((1.14, 3.7, 10.04, 36.0), "62-x-58-forster", 651, 11.8, 11.87, 1.43, 3.7, 10.04, 1.0),
            ".30 USA Rimless": ((1.37, 3.9, 10.0, 28.0), "30-blake", 250, 11.59, 11.57, 1.55, 3.9, 10.0, 0.85),
        }
        for name, (head, page, book, rim, base, rt, hl, groove, gw) in heads.items():
            with self.subTest(name):
                s = self.spec(name)
                self.assertEqual(outline.gaps(s), ())
                self.assertEqual(cartridges.case_head(name), head)
                self.assertLess(max(abs(rim - s["rim"]), abs(base - s["base"])), 0.5)
                self.assertLess(abs(rt - head[0]), 0.3)
                self.assertEqual((head[1], head[2]), (hl, groove))
                self.assertAlmostEqual(math.degrees(math.atan((base - groove) / 2 / (hl - rt - gw))), head[3], delta=0.5)
                self.assertEqual(cartridges.sources(name, "case_head"),
                                 ["book:cotw-18 p. %d" % book, "https://municion.org/producto/%s/" % page])
        # The .30 Blake drawing's shoulder is not taken: it is labelled 11.59 mm, wider than the head and 1.00 mm
        # more than the book's. The shoulder stays the rimmed twin's (the C.I.P. sheet of the .30-40 Krag).
        usa = self.spec(".30 USA Rimless")
        self.assertGreater(abs(11.59 - usa["shoulder"]), 0.5)
        self.assertIn("cip-bobp.org", cartridges.SHOULDER_ANGLES[".30 USA Rimless"][1])
        self.assertEqual(cartridges.sources(".30 USA Rimless", "mm")[-1], cartridges.SHOULDER_ANGLES[".30 USA Rimless"][1])
        # The .56-52 Spencer Necked keeps its estimate: municion.org has two necked drawings near the book's case,
        # from the mouth they start the shoulder 0.25 mm apart, but their necks are 7.0 and 5.0 mm long, more than
        # the 1.5 mm that the rule allows a drawn neck to differ. (SL, NL, CL of the longest and the shortest case.)
        spencer = self.spec(".56-52 Spencer Necked")
        (sl1, nl1, cl1), (sl2, nl2, cl2) = (16.0, 7.0, 26.75), (13.3, 5.0, 24.3)
        self.assertLess(abs(cl1 - spencer["case"]), 1.5)
        self.assertGreater(abs(cl2 - spencer["case"]), 1.5)
        starts = [round(spencer["case"] - (cl - sl), 2) for sl, cl in ((sl1, cl1), (sl2, cl2))]
        self.assertEqual(starts, [15.16, 14.91])  # carried from the mouth; the file keeps its estimate
        self.assertEqual(spencer["sh_at"], 12.4)
        self.assertGreater(abs(nl1 - nl2), 1.5)
        self.assertEqual(cartridges.unsourced(".56-52 Spencer Necked"), ("shoulder_at",))
        self.assertEqual(cartridges.sources(".56-52 Spencer Necked", "mm"), ["book:cotw-18 p. 670"])
        self.assertEqual(cartridges.shoulder_angle(".56-52 Spencer Necked"), cartridges.DEFAULT_SHOULDER_ANGLE)
        self.assertIn(".56-52 Spencer Necked", OutlineTests.SHOULDER_UNSOURCED)
        # naboje.org shows the drawings of the .577/500 and the Forster again (nodes 1356 and 13746): one measurement,
        # not two, so the files cite the AECC drawing for the shoulder and the head.
        for name in (".577/500 Nitro Express", "6x58 mm Forster"):
            cited = cartridges.sources(name, "mm") + [cartridges.SHOULDER_ANGLES[name][1]]
            self.assertFalse([url for url in cited if "naboje.org" in url], name)

    def test_specimens_measured_apart_outweigh_a_books_table(self):
        # The literature gives the 10.75x63 mm Mauser a rebated head: the table of Cartridges of the World has a rim
        # of .467 in. under a head of .493 in. in the five editions in the library, and Donnelly (p. 958) repeats it.
        # None of the three specimens found has one. Two drawings have a rim as wide as the head (the AECC's, on a
        # page with two DWM cartridges: 12.60 on 12.54; naboje.org's, of an RWS one: 12.50 on 12.52): within 0.5 mm
        # of each other and more than 0.5 mm from the table. The book's own text stands with them (practically the
        # dimensions of the 10.75x68 mm but for the length), and so does the C.I.P. sheet of the 10.75x68. The file
        # takes the AECC drawing's rim and, with it, the drawing's head.
        name, table, naboje_rim = "10.75x63 mm Mauser", 0.467 * 25.4, 12.5
        s, sister = self.spec(name), self.spec("10.75x68 mm Mauser")
        head = cartridges.case_head(name)
        self.assertEqual(s["rim"], 12.6)  # the AECC drawing's RØ
        self.assertLess(abs(s["rim"] - naboje_rim), 0.5)
        self.assertGreater(min(s["rim"], naboje_rim) - table, 0.5)
        self.assertLess(abs(s["rim"] - s["base"]), 0.1)  # the file's rim on its head: not rebated
        self.assertGreater(s["base"] - table, 0.5)  # the table's rim under the same head: rebated
        self.assertLess(max(abs(sister["rim"] - s["rim"]), abs(sister["rim"] - naboje_rim)), 0.5)
        self.assertLess(abs(sister["base"] - s["base"]), 0.5)
        # naboje.org often shows an AECC drawing again, which would be one measurement. These two were measured
        # apart: of the labels they share only the bullet's diameter is the same (AECC: mouth 11.32, neck 11.38,
        # shoulder 12.10 at 52.50, head 12.54, groove 11.00, case 62.98, rim thickness 1.15, overall 82.10;
        # naboje.org: 11.29, 11.32, 12.00 at 51.80, 12.52, 11.10, 62.72, 1.09, 79.50). The file's rim, rim thickness
        # and groove are the AECC drawing's and none of them is naboje.org's.
        self.assertEqual((head[0], head[2]), (1.15, 11.0))
        self.assertTrue(all(ours != theirs for ours, theirs in zip((s["rim"], head[0], head[2]), (12.5, 1.09, 11.1))))
        # Only the AECC drawing gives a value, so only its page is a source of the measurements.
        self.assertEqual(cartridges.sources(name, "mm"),
                         ["book:cotw-18 p. 652", "https://municion.org/producto/1075-x-63-g-mauser/"])
        # The head: HL = RT + GW + ((HØ - GØ)/2)/tan(angle) on the AECC drawing (HØ 12.54, GW 1.20), whose head
        # diameter is the file's. Donnelly's rim thickness (.06 in.) is more than 0.3 mm from the drawing's, so the
        # whole head is the drawing's.
        self.assertEqual(head, (1.15, 3.7, 11.0, 30.0))
        self.assertAlmostEqual(math.degrees(math.atan((12.54 - head[2]) / 2 / (head[1] - head[0] - 1.2))), head[3],
                               delta=0.5)
        self.assertLess(abs(12.54 - s["base"]), 0.5)
        self.assertGreater(0.06 * 25.4 - head[0], 0.3)
        self.assertEqual(cartridges.sources(name, "case_head"), ["https://municion.org/producto/1075-x-63-g-mauser/"])
        self.assertEqual(outline.gaps(s), ())

    def test_cip_sheets_found_under_another_title_source_their_calibres(self):
        # Calibres that failed the rule on 2026-11-14 and now take every measurement and the head from their C.I.P.
        # sheet, some found under another title (the Vergueiro as «6,5 x 58 Mauser», the .256 Gibbs as «256 Mag.
        # Gibbs», the .275 H&H Magnum as «275 Belt. N.E.»). Rim R1, case L3, half the cone angle alpha, groove E1
        # (None: straight case, rimmed case).
        sheets = {
            "6.5x58 mm Vergueiro": (11.8, 58.0, 15.0, 10.2), ".275 H&H Magnum": (13.51, 63.5, 32.0, 11.94),
            ".280 Ross": (14.22, 66.32, 26.6, 12.45), ".333 Jeffery Rimless": (13.79, 62.86, 19.9, 12.37),
            "10.75x68 mm Mauser": (12.57, 68.0, 28.0, 10.6), ".256 Gibbs Magnum": (12.09, 55.25, 20.1, 10.41),
            ".45 Blaser": (12.01, 55.0, 10.0, 10.39), "12.7x108 mm": (21.8, 108.0, 17.8, 18.0),
            "7.21 Lazzeroni Firebird": (14.76, 71.37, 30.0, 12.95),
            "7.82 Lazzeroni Warbird": (14.76, 71.37, 30.0, 12.95), "7.92x24 mm VBR": (9.14, 24.0, None, 7.87),
            ".32 Winchester Self-Loading": (9.91, 32.77, None, 8.64),
            ".35 Winchester Self-Loading": (10.29, 29.31, None, 9.02),
            ".401 Winchester Self-Loading": (11.68, 38.1, None, 10.31),
            ".475 No. 2 Nitro Express": (17.14, 88.9, 6.1, None), ".577/450 Martini-Henry": (19.3, 59.08, 15.8, None),
            "9x57 mm Mauser": (11.95, 56.8, 19.1, 10.5),
        }
        for name, (rim, case, angle, groove) in sheets.items():
            with self.subTest(name):
                s = self.spec(name)
                self.assertEqual(outline.gaps(s), ())
                self.assertEqual((s["rim"], s["case"]), (rim, case))
                self.assertEqual(cartridges.SHOULDER_ANGLES.get(name, (None,))[0], angle)
                self.assertEqual((cartridges.case_head(name) or (None,) * 3)[2], groove)
                self.assertIn("bobp.cip-bobp.org/uploads/tdcc/", cartridges.sources(name, "mm")[0])
        # The .32 Winchester Self-Loading has no groove floor: a 3.7 degree cone runs from the rim's front (1.27 mm)
        # up to the body 3.49 mm from the base.
        cone = [(round(r, 4), round(h, 4)) for r, h in outline.case_profile(self.spec(".32 Winchester Self-Loading"))[:5]]
        self.assertEqual(cone, [(4.955, 0), (4.955, 1.27), (4.32, 1.27), (4.32, 1.27), (4.465, 3.49)])

    def test_well_sourced_allows_a_default_rim_only(self):
        self.assertTrue(outline.well_sourced(self.spec(".308 Winchester")))
        self.assertTrue(outline.well_sourced(self.spec(".25 Stevens")))  # rim thickness only
        self.assertFalse(outline.well_sourced(self.spec(".45-70 Auto")))  # generic groove
        self.assertFalse(outline.well_sourced(self.spec(".56-52 Spencer Necked")))
        passing = sum(outline.well_sourced(s) for _, s in outline.specs())  # 606 of 759 before these sheets
        self.assertTrue(0 < passing < len(outline.specs()))

    def test_popular_calibres_are_well_sourced(self):
        # Raven's list of popular calibres that failed the rule on 2026-11-14, as they get sourced.
        # SAAMI's groove diameter; the ramp's top from rim thickness + groove width (the "+ .010" dimension) + ramp.
        for name, top, groove in [("6 mm GT", 3.84, 10.39), (".22 Nosler", 4.12, 8.43), (".277 SIG Fury", 3.86, 10.36),
                                  (".33 Nosler", 3.73, 12.07)]:
            with self.subTest(name):
                self.assertTrue(outline.well_sourced(self.spec(name)))
                self.assertEqual(cartridges.case_head(name)[1:3], (top, groove))

    def test_more_heads_from_saami_drawings_and_a_related_case(self):
        # SAAMI drawings (Z299.4, Z299.3 and the .25 Weatherby RPM's public introduction): ramp top and groove
        # diameter, worked out as above. The .25 Weatherby RPM has the head of the 6.5 and the .338.
        for name, top, groove in [(".27 Nosler", 3.73, 12.07), (".30 Remington AR", 4.03, 10.87),
                                  ("9x23 mm Winchester", 3.36, 8.81), (".25 Weatherby RPM", 3.76, 10.39)]:
            with self.subTest(name):
                self.assertEqual(outline.gaps(self.spec(name)), ())
                self.assertEqual(cartridges.case_head(name)[1:3], (top, groove))
                self.assertIn("saami.org", cartridges.sources(name, "case_head")[0])
        self.assertEqual(cartridges.case_head(".25 Weatherby RPM"), cartridges.case_head("6.5 Weatherby RPM"))
        # The .44 Auto Mag has no sheet; the .357 Auto Mag, the same case necked down, has one (C.I.P. Tab. IV).
        self.assertEqual(outline.gaps(self.spec(".44 Auto Mag")), ())
        self.assertEqual(cartridges.case_head(".44 Auto Mag"), (1.37, 3.56, 10.4, 45.0))
        self.assertEqual(cartridges.sources(".44 Auto Mag", "case_head"),
                         ["https://bobp.cip-bobp.org/uploads/tdcc/tab-iv/tabivcal-en-page49.pdf", "book:cotw-18 p. 320"])


class OutlineTests(unittest.TestCase):
    def test_every_calibre_has_a_valid_outline_inside_its_box(self):
        for _, s in outline.specs():
            with self.subTest(s["name"]):
                o = outline.outline(s)
                self.assertAlmostEqual(o["height"], s["oal"], places=2)
                self.assertAlmostEqual(o["width"], max(s["rim"], s["base"], s["bullet"], s["belt"] or 0), places=2)
                paths = [o[k] for k in ("case", "head", "bullet", "patch", "tip") if k in o]
                self.assertTrue(paths)
                xs = [x for d in paths for x, _ in points(d)]
                self.assertAlmostEqual(max(xs) - min(xs), o["width"], delta=0.02)  # and the drawing fills the box
                for d in paths:
                    self.assertRegex(d, PATH)
                    for x, y in points(d):
                        self.assertGreaterEqual(x, -0.01)
                        self.assertLessEqual(x, o["width"] + 0.01)
                        self.assertGreaterEqual(y, -0.01)
                        self.assertLessEqual(y, o["height"] + 0.01)

    def test_outlines_are_symmetric(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            xs = [x for x, _ in points(o.get("case") or o["bullet"])]
            self.assertAlmostEqual(min(xs) + max(xs), o["width"], places=1, msg=s["name"])

    def test_only_paper_patched_bullets_have_a_patch(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            has_bullet = s["oal"] > s["case"] + 0.1 and "case" in o
            patched = s["profile"] == PATCHED or bullet(s["name"]) == PAPER_PATCHED
            self.assertEqual("patch" in o, patched and has_bullet, s["name"])
            if "case" in o:
                # GP 1890's cap, the MPS dart, a steel jacket
                steel = s["profile"] == PATCHED or bullet(s["name"]) == STEEL or jacket(s["name"]) == STEEL
                self.assertEqual(o.get("bulletMaterial") == "steel", steel and has_bullet, s["name"])

    def test_a_patch_length_sets_the_paper_band(self):
        # Paper over half the exposed bullet unless [bullet] patch_length gives the paper above the mouth.
        name = "10.4x38 mm R Vetterli"
        s = {x["name"]: x for _, x in outline.specs()}[name]
        def band():
            ys = [float(v) for v in re.findall(r"[ML][\d.]+ ([\d.]+)", outline.outline(s)["patch"])]
            return round(max(ys) - min(ys), 2)
        self.assertIsNone(cartridges.patch_length(name))
        self.assertAlmostEqual(band(), (s["oal"] - s["case"]) / 2, places=1)
        cartridges.PATCH_LENGTHS[name] = (6.0, None)
        try:
            self.assertEqual(cartridges.patch_length(name), 6.0)
            self.assertAlmostEqual(band(), 6.0, places=1)
        finally:
            del cartridges.PATCH_LENGTHS[name]

    def test_gp_1890_bullet_follows_the_1892_drawing(self):
        # «Patrone, Modell 1890» (Thun, 1 Feb 1892): 23.7 mm out of the case, paper over the first
        # 12.7, the capped nose the last 11; 8.15 where the paper ends, 7.95 on the cap; an R 22 ogive
        # with a 2.3 mm round tip.
        pts = outline.bullet_profile(8.15 / 2, 53.5, 77.2, PATCHED)
        self.assertEqual([(round(x, 3), round(y, 3)) for x, y in pts[:3]], [(4.075, 53.5), (4.075, 66.2), (3.975, 66.2)])
        self.assertEqual(pts[-1], (0, 77.2))
        nose = pts[2:]
        self.assertTrue(all(a[0] > b[0] and a[1] < b[1] for a, b in zip(nose, nose[1:])))  # narrows to the tip
        # The round tip: about 0.3 mm below it the nose is still about 1 mm from the axis, not a point.
        x = next(x for x, y in nose if y >= 77.2 - 0.5)
        self.assertGreater(x, 1.0)
        # The R 22 ogive: halfway up the nose it is still about 3.36 mm from the axis.
        mid = 66.2 + 11 / 2
        (x0, y0), (x1, y1) = next((a, b) for a, b in zip(nose, nose[1:]) if a[1] <= mid <= b[1])
        self.assertAlmostEqual(x0 + (x1 - x0) * (mid - y0) / (y1 - y0), 3.36, delta=0.05)
        by_name = {s["name"]: s for _, s in outline.specs()}
        o = outline.outline(by_name["7.5x53.5 mm Swiss (Patrone Modell 1890)"])
        ys = [y for _, y in points(o["patch"])]
        self.assertAlmostEqual(max(ys) - min(ys), 12.7, places=1)

    def test_jackets_that_are_not_copper_are_named(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            material = jacket(s["name"])  # None without a jacket
            if "bullet" in o and material:
                self.assertEqual(o.get("bulletMaterial"), None if material == "copper" else material, s["name"])
        by_name = {s["name"]: s for _, s in outline.specs()}
        self.assertEqual(outline.outline(by_name[".303 British"])["bulletMaterial"], "cupronickel")
        self.assertNotIn("bulletMaterial", outline.outline(by_name["9x19 mm"]))

    def test_a_ball_nose_is_the_sphere_out_of_the_mouth(self):
        # The Flobert Bosquette: an 8.84 ball, 4.8 mm of it out of a 10.18 case.
        pts = outline.bullet_profile(4.42, 10.18, 14.98, BALL_NOSE)
        self.assertEqual(pts[-1], (0, 14.98))
        centre = 14.98 - 4.42
        for x, y in pts[:-1]:
            self.assertAlmostEqual(x * x + (y - centre) ** 2, 4.42 ** 2, places=6)
        self.assertAlmostEqual(max(x for x, _ in pts), 4.42, places=2)  # the equator shows
        flobert = next(s for _, s in outline.specs() if s["name"] == "9 mm Flobert Bosquette")
        self.assertEqual(outline.outline(flobert)["bulletMaterial"], "lead")

    def test_loose_projectiles_name_only_non_lead_materials(self):
        for _, s in outline.specs():
            if s["kind"] in (BALL, MINIE, PELLET):
                material = loose_material(s["name"])
                self.assertEqual(outline.outline(s).get("bulletMaterial"), None if material == LEAD else material, s["name"])
        by_name = {s["name"]: s for _, s in outline.specs()}
        self.assertEqual(outline.outline(by_name["4.4 mm Stahl-BB (.177 BB)"])["bulletMaterial"], "steel")
        self.assertEqual(outline.outline(by_name["6 mm Airsoft-BB"])["bulletMaterial"], "plastic")
        self.assertNotIn("bulletMaterial", outline.outline(by_name[".44 Rundkugel (.454)"]))

    def test_lead_bullets_are_drawn_in_lead(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            if "case" in o and "bullet" in o and s["profile"] != PATCHED:
                lead = bullet(s["name"]) in (LEAD, PAPER_PATCHED)
                self.assertEqual(o.get("bulletMaterial") == "lead", lead, s["name"])

    def test_hollow_points_have_a_cavity_in_the_nose(self):
        names = [s["name"] for _, s in outline.specs() if bullet(s["name"]) == HOLLOW_POINT]
        self.assertIn(".22 TCM", names)
        for _, s in outline.specs():
            o = outline.outline(s)
            if "bullet" not in o:
                continue
            centre = [y for x, y in points(o["bullet"]) if abs(x - o["width"] / 2) < 0.01]
            # The nose is the highest point (y 0) unless a cavity is cut into it.
            self.assertEqual(min(centre) > 0.1, s["name"] in names, s["name"])

    def test_a_hollow_point_keeps_the_round_s_nose_up_to_its_cavity(self):
        for profile in (SPITZER, ROUND, FLAT):
            nose, hollow = outline.bullet_profile(3, 10, 20, profile), outline.hollow_profile(3, 10, 20, profile)
            (mx, my), (ax, ay) = hollow[-2:]
            self.assertEqual(hollow[:-2], nose[:len(hollow) - 2], profile)
            self.assertAlmostEqual(mx, outline.HOLLOW_MOUTH * 3)
            self.assertEqual(ax, 0)
            self.assertLess(ay, my)
            self.assertLessEqual(my, 20)
        self.assertEqual(outline.hollow_profile(3, 10, 20, FLAT)[-2][1], 20)  # the cavity opens in the flat
        self.assertLess(outline.hollow_profile(3, 10, 20, SPITZER)[-2][1], 20)  # a pointed nose is cut short

    def test_soft_points_show_a_lead_tip_at_the_front_of_the_bullet(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            self.assertEqual("tip" in o, bullet(s["name"]) in (SOFT_POINT, POLYMER_TIP) and "bullet" in o, s["name"])
            self.assertEqual(o.get("tipMaterial") == "polymer", bullet(s["name"]) == POLYMER_TIP and "bullet" in o, s["name"])
            if "tip" in o:
                tip, whole = points(o["tip"]), points(o["bullet"])
                self.assertAlmostEqual(min(y for _, y in tip), 0, places=2, msg=s["name"])
                exposed = s["oal"] - s["case"]
                self.assertAlmostEqual(max(y for _, y in tip), outline.TIP_SHARE * exposed, places=1, msg=s["name"])
                # The tip lies inside the bullet's width.
                self.assertLessEqual(max(x for x, _ in tip), max(x for x, _ in whole) + 0.01, s["name"])

    def test_tip_profile_cuts_the_front_of_a_profile(self):
        right = [(2.0, 10.0), (2.0, 12.0), (1.0, 14.0), (0.0, 16.0)]
        self.assertEqual(outline.tip_profile(right, 16.0, share=1 / 3), [(1.0, 14.0), (0.0, 16.0)])
        self.assertEqual(outline.tip_profile(right, 16.0, share=0.25), [(0.75, 14.5), (0.0, 16.0)])

    def test_case_material_only_where_not_brass(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            self.assertEqual(o.get("caseMaterial"), None if case_material(s["name"]) == BRASS else case_material(s["name"]), s["name"])
        self.assertEqual(outline.outline(next(s for _, s in outline.specs() if s["name"] == ".45-70 Government"))["caseMaterial"], "copper")
        self.assertTrue(CASES)

    def test_current_case_materials_are_listed_but_not_drawn(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            self.assertEqual(o.get("currentCaseMaterials"), list(current_case_materials(s["name"])) or None, s["name"])
        o = outline.outline(next(s for _, s in outline.specs() if s["name"] == ".45-70 Government"))
        self.assertEqual((o["caseMaterial"], o["currentCaseMaterials"]), ("copper", ["brass"]))

    def test_hybrid_case_has_a_steel_head(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            self.assertEqual(o.get("headMaterial") == "steel", case_material(s["name"]) == HYBRID, s["name"])
        fury = outline.outline(next(s for _, s in outline.specs() if s["name"] == ".277 SIG Fury"))
        ys = [y for _, y in points(fury["head"])]
        # y grows from the tip: the head runs from the base up to where the body starts, the top of the extractor
        # groove's ramp, wherever the calibre's head puts it (a fixed 3.3 mm cut through the ramp once the Fury
        # had its own rim thickness).
        s = next(s for _, s in outline.specs() if s["name"] == ".277 SIG Fury")
        (body, ramp_top), (_, body_end) = outline.case_profile(s)[4:6]
        self.assertEqual(body, s["base"] / 2)
        self.assertLess(ramp_top, body_end)
        self.assertAlmostEqual(max(ys), fury["height"], places=2)
        self.assertAlmostEqual(min(ys), fury["height"] - ramp_top, places=2)

    def test_paper_case_stands_on_a_brass_head(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            # Only shot shells, hybrid and paper cases have a head part apart from the case.
            self.assertEqual("head" in o, s["kind"] == SHOT or case_material(s["name"]) in (HYBRID, PAPER), s["name"])
        s = next(s for _, s in outline.specs() if s["name"] == ".577 Snider")
        o = outline.outline(s)
        self.assertEqual(o["caseMaterial"], "paper")
        self.assertNotIn("headMaterial", o, "no headMaterial: the head is brass")
        head = points(o["head"])
        self.assertAlmostEqual(max(y for _, y in head), o["height"], places=2)
        top = min(y for _, y in head)
        self.assertAlmostEqual(top, o["height"] - outline.PAPER_HEAD, places=2)
        # The head ends on the case's tapering wall: narrower than the base, wider than the mouth.
        xs = [x for x, y in head if y == top]
        self.assertTrue(s["neck"] < max(xs) - min(xs) < s["base"], xs)

    def test_crimped_blank_is_a_case_narrowing_to_the_mouth(self):
        s = next(s for _, s in outline.specs() if s["name"] == ".22 SH (5.6/11)")
        self.assertEqual(s["profile"], CRIMPED)
        o = outline.outline(s)
        self.assertNotIn("bullet", o, "a blank has no bullet")
        pts = points(o["case"])
        # Tip at y = 0: the mouth is the crimp's width, the body further back the full base.
        mouth = [x for x, y in pts if y < 0.01]
        self.assertAlmostEqual(max(mouth) - min(mouth), s["neck"], places=1)
        body = [x for x, y in pts if abs(y - s["case"] * outline.CRIMP_LENGTH) < 0.01]
        self.assertAlmostEqual(max(body) - min(body), s["base"], places=1)
        self.assertLess(s["neck"], s["base"])

    def test_rimmed_alarm_blank_draws_a_rim_and_a_crimp(self):
        s = next(s for _, s in outline.specs() if s["name"] == "9 mm R Blanc")
        o = outline.outline(s)
        self.assertNotIn("bullet", o)
        pts = points(o["case"])
        self.assertAlmostEqual(max(x for x, _ in pts) - min(x for x, _ in pts), s["rim"], places=1)
        mouth = [x for x, y in pts if y < 0.01]
        self.assertAlmostEqual(max(mouth) - min(mouth), s["neck"], places=1)

    def test_only_blanks_are_crimped(self):
        for _, s in outline.specs():
            if s["profile"] == CRIMPED:
                self.assertEqual(s["oal"], s["case"], s["name"])

    def test_identical_groups(self):
        self.assertEqual(outline.identical_groups(), [
            [".38 Super", ".38 ACP"],  # one SAAMI drawing (.38 Super Automatic +P / .38 Automatic)
            [".223 Remington", "5.56x45 mm NATO", "5.56 Commercial", "5.6 mm GP 90"],
            ["7.62x51 mm NATO", ".308 Winchester"],
            [".500/450 Nitro Express", ".500/450 Magnum Express"],
        ])

    def test_identical_calibres_are_lookalikes(self):
        # Calibres that look exactly the same from the side must be in one lookalike group.
        for names in outline.identical_groups():
            self.assertEqual(set(cartridges.lookalikes(names[0])), set(names[1:]), names)

    def test_flush_wadcutter_shows_only_its_case(self):
        # The .32 S&W Long wadcutter sits flush with the case mouth: a plain rimmed cylinder.
        by_name = {s["name"]: s for _, s in outline.specs()}
        o = outline.outline(by_name[".32 S&W Long Wadcutter"])
        self.assertNotIn("bullet", o)
        self.assertNotIn("bulletMaterial", o)
        self.assertEqual(o["height"], 23.27)
        self.assertNotIn(".32 S&W Long Wadcutter", [n for g in outline.identical_groups() for n in g])

    def test_outline_is_deterministic(self):
        _, s = outline.specs()[0]
        self.assertEqual(outline.outline(s), outline.outline(dict(s)))


    def test_necks_start_where_the_municion_drawings_show(self):
        # AECC specimen drawings on municion.org: (shoulder start SL, neck length NL, case length CL), mm.
        # The neck the outline draws is as long as the specimen's (NL) within 1.5 mm, and sh_at is never
        # well before the drawn shoulder start. Both are taken from the mouth, as the README's rule carries
        # the start, so a case a little longer or shorter than the specimen's does not count twice (the
        # size limit on the case length is its own check). Calibres with a C.I.P. sheet follow the sheet
        # instead (test_cip_shoulders_follow_the_sheets), which wins over a measured specimen.
        drawn = {
            "4.6x30 mm": (18.77, 8.98, 30.58), ".32-20 Winchester": (19.0, 11.0, 33.18),
            ".25 NAA": (13.8, 3.83, 18.91), ".32 NAA": (13.55, 2.1, 17.16), ".400 Cor-Bon": (17.25, 3.45, 22.84),
            "6 mm BR Norma": (26.9, 7.9, 39.38), "6 mm PPC": (27.2, 7.4, 38.65), "9x39 mm": (31.1, 5.85, 38.97),
            "6.5x47 mm Lapua": (36.18, 7.7, 46.78), "6.5 PRC": (40.08, 8.55, 51.41),
            ".300 AAC Blackout": (26.6, 6.6, 34.6), ".300 Norma Magnum": (48.08, 7.31, 63.04),
            ".300 Lapua Magnum": (54.9, 8.89, 69.2), ".303 British": (45.3, 8.65, 56.08),
            ".400/350 Nitro Express": (53.0, 13.3, 69.82), ".400 H&H Magnum": (49.6, 15.35, 72.0),
            ".257 Roberts": (43.5, 7.8, 56.6), ".375 Ruger": (55.3, 7.0, 65.32),
            ".25-35 Winchester": (34.2, 13.2, 52.0), ".300 Weatherby Magnum": (59.0, 9.3, 71.5),
            ".416 Remington Magnum": (60.9, 10.3, 72.27), ".470 Nitro Express": (61.2, 18.9, 82.34),
            ".500/465 Nitro Express": (56.0, 16.5, 82.37), ".240 Weatherby Magnum": (50.96, 8.78, 63.3),
            ".220 Swift": (43.7, 6.9, 55.78), ".25-20 Winchester": (20.4, 9.6, 33.25),
            ".257 Weatherby Magnum": (52.18, 9.45, 64.6), ".270 Weatherby Magnum": (52.0, 8.7, 64.58),
            "7 mm Weatherby Magnum": (51.85, 9.4, 64.45), ".300 Savage": (39.35, 4.9, 47.2),
            ".32 Remington": (37.7, 11.95, 52.0), ".303 Savage": (34.0, 13.0, 51.09),
            ".219 Zipper": (34.4, 7.75, 49.15), "6 mm Remington": (43.65, 8.5, 56.64),
            ".22 Savage Hi-Power": (34.0, 10.7, 52.07), ".223 WSSM": (29.05, 6.04, 42.05),
            ".243 WSSM": (29.1, 6.4, 42.3), ".25 WSSM": (29.2, 7.4, 42.57),
            ".338-378 Weatherby Magnum": (60.4, 9.78, 73.7), "7 mm Remington SAUM": (38.95, 7.5, 51.52),
            ".458 SOCOM": (30.0, 9.15, 40.0), "8x58 mm R Danish Krag": (41.0, 11.2, 57.7),
            ".416 Barrett": (63.5, 12.17, 82.95), ".400/375 Belted Nitro Express": (43.7, 18.5, 63.38),
            "7 mm Long Range Magnum": (49.91, 9.7, 63.85), ".276 Pedersen": (41.05, 6.05, 51.41),
            "6.5x53 mm R Mannlicher": (41.2, 7.5, 53.55),
            "10.57 Lazzeroni Maverick": (39.2, 9.55, 51.6), "10.57 Lazzeroni Meteor": (59.0, 9.0, 70.91),
            "12.04 Bibamufu": (59.0, 9.8, 71.12), "7.21 Lazzeroni Firehawk": (59.0, 7.0, 71.03),
            "7.21 Lazzeroni Tomahawk": (39.5, 6.6, 51.88), "7.82 Lazzeroni Patriot": (39.2, 6.85, 51.56),
            "8.59 Lazzeroni Galaxy": (39.0, 8.0, 51.5), "8.59 Lazzeroni Titan": (59.0, 8.0, 71.08),
            "9.53 Lazzeroni Hellcat": (39.38, 8.6, 51.5), "9.53 Lazzeroni Saturn": (58.6, 8.83, 70.81),
            "6.17 Lazzeroni Spitfire": (40.5, 5.85, 51.91), "6.71 Lazzeroni Phantom": (40.0, 6.0, 51.88),
            ".500/450 No. 1 Express": (47.33, 19.35, 69.88), ".25-45 Sharps": (36.05, 5.4, 44.22),
            "10.4x47 mm R Italian Vetterli": (34.7, 9.0, 47.45),
            # Confirmed by Donnelly (test_shoulders_that_donnelly_and_an_aecc_drawing_agree_on).
            ".38-90 Winchester Express": (60.0, 17.0, 82.6), "11x52 mm R Beaumont M71/78": (33.9, 12.65, 51.05),
            ".40-70 Peabody What Cheer": (22.9, 9.6, 42.45),
            # The angle over the drawing's shoulder length
            # (test_shallow_shoulders_run_over_the_drawings_shoulder_length).
            ".500/450 Magnum Express": (61.0, 15.4, 82.47), ".500/450 Nitro Express": (61.0, 15.4, 82.47),
            "11.2x60 mm Schüler": (35.0, 19.1, 60.25), "11.43x50 mm R Egyptian Remington": (33.44, 11.96, 48.53),
            ".32-40 Bullard": (23.6, 14.0, 46.73), ".40-110 Winchester Express": (60.5, 16.9, 82.6),
            ".40-70 Sharps Necked": (35.7, 14.6, 57.17), ".577 Tyrannosaur": (59.3, 12.3, 75.7),
            "9.3x65 mm R Collath": (55.1, 8.3, 64.96),
            ".450/400 Nitro Express 2⅜ inch": (40.48, 16.7, 60.63),
            "7 mm Canadian Magnum": (58.75, 6.7, 71.63), ".338 Canadian Magnum": (59.82, 8.15, 71.72),
            ".32-30 Remington": (31.0, 7.3, 41.48), "10.75x58 mm R Russian Berdan": (39.0, 12.2, 57.45),
            # Filed under other names (test_aecc_drawings_filed_under_other_names).
            ".577/500 Nitro Express": (59.85, 15.5, 79.39), "6x58 mm Forster": (41.8, 8.05, 57.93),
            ".416 Rimmed": (69.0, 10.0, 83.7),
        }
        specs = {s["name"]: s for _, items in cartridges.ALL_CATALOGUE for s in items}
        for name, (shoulder_start, neck_length, case_length) in drawn.items():
            if cartridges.SHOULDER_ANGLES.get(name, (0, ""))[1].startswith("https://bobp.cip-bobp.org/uploads/tdcc/"):  # a C.I.P. sheet
                continue
            with self.subTest(name):
                s = specs[name]
                top = s["neck"] / 2
                neck_start = next(h for r, h in outline.case_profile(s) if abs(r - top) < 1e-9 and h > s["sh_at"])
                self.assertLess(abs((s["case"] - neck_start) - neck_length), 1.5)
                self.assertLess((s["case"] - s["sh_at"]) - (case_length - shoulder_start), 0.6)

    def test_every_recorded_municion_reading_keeps_its_neck(self):
        # The same two checks without a list: every calibre whose shoulder angle cites municion.org and whose file
        # records the drawing's reading in the note under [shoulder_angle] ("SØ .., NØ .., SL .., NL .., CL .."), so
        # that a drawing added later is held to the rule as well. The two Vetterli rounds are left out: their [mm]
        # are older than the rule and start the shoulder 1.0 mm before the drawing they cite, which is for a change
        # of its own to settle.
        older = {"10.4x38 mm R Vetterli", "10.4x38 mm R Vetterli Centrefire"}
        # Angles that cite municion.org without a reading in that format: notes that name only the drawing or spell
        # it out another way. Nine of them are in the list of test_necks_start_where_the_municion_drawings_show.
        # A new angle from a drawing records its reading, so no name is added here.
        no_reading = {
            ".17 Winchester Super Magnum", ".22 Nosler", ".22 TCM", ".25 NAA",
            ".256 Winchester Magnum", ".308 Norma Magnum", ".32 NAA", ".38-56 WCF", ".38-90 Winchester Express",
            ".40-70 Peabody What Cheer", ".400 A-Square DPM", ".400 Cor-Bon", ".416 Barrett",
            ".500/450 Magnum Express", ".500/450 Nitro Express", ".55 Boys", "11x52 mm R Beaumont M71/78",
            "11x59 mm R Gras", "7.35x51 mm Carcano", "7.5 mm Kadettenpatrone", "7.7x58 mm Arisaka",
            "7.92x107 mm DS", "8 mm Nambu", "8x50 mm R Lebel", "9x25 mm Dillon",
        }
        reading = re.compile(r"SØ (\d+\.\d+), NØ \d+\.\d+, SL (\d+\.\d+), NL (\d+\.\d+), CL (\d+\.\d+)")
        folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "calibres")
        specs = {s["name"]: s for _, items in cartridges.ALL_CATALOGUE for s in items}
        walked, unread = set(), set()
        for name, (_, url) in cartridges.SHOULDER_ANGLES.items():
            if "municion.org" not in url:
                continue
            with open(os.path.join(folder, cartridges.slug(name) + ".toml"), encoding="utf-8") as f:
                found = reading.search(f.read().split("[shoulder_angle]")[1])
            if not found:
                unread.add(name)
                continue
            walked.add(name)
            if name in older:
                continue
            _, shoulder_start, neck_length, case_length = map(float, found.groups())
            with self.subTest(name):
                s = specs[name]
                top = s["neck"] / 2
                neck_start = next(h for r, h in outline.case_profile(s) if abs(r - top) < 1e-9 and h > s["sh_at"])
                self.assertLess(abs((s["case"] - neck_start) - neck_length), 1.5)
                self.assertLess(abs((s["case"] - s["sh_at"]) - (case_length - shoulder_start)), 0.6)
        self.assertEqual(unread, no_reading)  # every other note keeps the format the walk reads
        self.assertGreaterEqual(len(walked), 116)
        self.assertLessEqual(older, walked)

    # Bottleneck calibres still drawn with DEFAULT_SHOULDER_ANGLE: no C.I.P. sheet, SAAMI drawing
    # or article giving the angle was found yet. Remove a name here when its angle is added.
    SHOULDER_UNSOURCED = {
        # Measured only from a dimension table in Cartridges of the World, which gives no angle (their
        # shoulder_at is estimated, as the note in [mm] says).
        ".275 No. 2 Magnum", ".32-40 Remington", ".38-70 Winchester",
        ".400/360 Nitro Express", ".45-100 Remington Necked", ".45-125 Winchester Express",
        ".50-115 Bullard", ".56-52 Spencer Necked", ".577/500 No. 2 Express",
        "10.25x69 mm R Hunting-Express", "10.75x57 mm Mannlicher", "10.8x47 mm R Martini Target",
        "11.4x50 mm R Brazilian Comblain", "11x53 mm R Comblain",
        "6.5x53.5 mm SR Daudeteau", "6x57 mm Mauser", "8.5 mm Mars", "9.3x75 mm R Nimrod", "9x70 mm R Mauser",
    }

    def bottlenecks(self):
        # The cannon rounds too (catalogue only), since the AECC drawings gave them their shoulders (2026-11-15).
        return {s["name"]: s for _, items in cartridges.ALL_CATALOGUE for s in items
                if s["shoulder"] and s["profile"] != CRIMPED}

    def test_every_bottleneck_has_a_sourced_angle_or_is_listed(self):
        sourced = set(cartridges.SHOULDER_ANGLES)
        self.assertEqual(sourced - set(self.bottlenecks()), set(), "angles for calibres without a shoulder")
        self.assertEqual(set(self.bottlenecks()) - sourced, self.SHOULDER_UNSOURCED)
        for name, (angle, url) in cartridges.SHOULDER_ANGLES.items():
            with self.subTest(name):
                self.assertTrue(2 <= angle <= 55, angle)
                self.assertTrue(url.startswith("https://") or url.startswith("book:"), url)

    def test_angles_read_from_cip_sheets_found_by_name(self):
        # Half the junction cone angle alpha on each sheet.
        for name, angle, page in [("10.75x68 mm Mauser", 28.0, "tab-i/tabical-en-page74.pdf"),
                                  (".460 Steyr", 28.3, "tab-i/tabical-en-page151.pdf"),
                                  (".333 Jeffery Rimless", 19.9, "tab-i/tabical-en-page129.pdf"),
                                  (".280 Ross", 26.6, "tab-i/tabical-en-page104.pdf"),
                                  (".275 H&H Magnum", 32.0, "tab-iii/tabiiical-en-page15.pdf")]:
            with self.subTest(name):
                self.assertEqual(cartridges.SHOULDER_ANGLES[name][0], angle)
                self.assertTrue(cartridges.SHOULDER_ANGLES[name][1].endswith(page))

    def test_shoulders_are_drawn_at_their_own_angle(self):
        # Regression: every shoulder used to be drawn at one shared 32-degree slope.
        for name, s in self.bottlenecks().items():
            with self.subTest(name):
                prof = outline.case_profile(s)
                top = s["neck"] / 2
                i = next(i for i, (r, h) in enumerate(prof) if abs(r - top) < 1e-9 and h > s["sh_at"])
                (r0, h0), (r1, h1) = prof[i - 1], prof[i]
                self.assertAlmostEqual(r0, s["shoulder"] / 2)
                drawn = math.degrees(math.atan2(r0 - r1, h1 - h0))
                self.assertAlmostEqual(drawn, cartridges.shoulder_angle(name), places=6)
                self.assertEqual(h0, s["sh_at"], "shoulder moved to fit a neck")
        self.assertGreater(len({a for a, _ in cartridges.SHOULDER_ANGLES.values()}), 40)

    def test_cip_shoulders_follow_the_sheets(self):
        # (half angle, L1 body/shoulder junction, L2 shoulder/neck junction) from the C.I.P. sheets.
        sheets = {
            ".308 Winchester": (20.0, 39.62, 43.48), "7.5x55 mm Swiss (GP 11)": (30.5, 44.58, 47.085),
            ".300 H&H Magnum": (8.5, 53.46, 62.96), "6.5 mm Creedmoor": (30.0, 37.84, 41.52),
            ".350 Rigby Magnum": (45.0, 57.15, 57.99), ".22 Hornet": (5.6, 21.64, 25.80),
            "7.62x54 mm R": (18.5, 39.70, 44.30), ".300 AAC Blackout": (23.0, 27.20, 28.00),
            "6.5 PRC": (30.0, 39.84, 44.65), "7 mm PRC": (30.0, 46.21, 50.63),
            "6 mm ARC": (30.0, 28.47, 31.90), "9x39 mm": (17.0, 31.40, 33.00),
            ".223 Remington": (23, 36.52, 39.55),
        }
        specs = self.bottlenecks()
        for name, (angle, l1, l2) in sheets.items():
            with self.subTest(name):
                s = specs[name]
                self.assertEqual(cartridges.shoulder_angle(name), angle)
                self.assertEqual(s["sh_at"], l1)
                top = s["neck"] / 2
                neck_start = next(h for r, h in outline.case_profile(s) if abs(r - top) < 1e-9 and h > s["sh_at"])
                self.assertLess(abs(neck_start - l2), 0.6)

    def test_municion_shoulders_follow_the_aecc_drawings(self):
        # (half angle, shoulder start) from AECC drawings on municion.org: atan(((SØ-NØ)/2)/(CL-NL-SL)).
        # The .22 Nosler's start is SAAMI's 35.29 (the drawing: 35.28).
        drawings = {".22 Nosler": (29.9, 35.29), ".38-56 WCF": (6.5, 30.64), "10.4x38 mm R Vetterli": (10.6, 26.11),
                    ".280 British": (19.4, 30.97), "6 mm Lee Navy": (18.3, 43.75),
                    ".246 Purdey Flanged": (16.0, 46.3), ".400 A-Square DPM": (26.9, 59.1),
                    ".400/375 Belted Nitro Express": (20.4, 43.82), ".276 Pedersen": (10.8, 40.95),
                    ".500/450 No. 1 Express": (9.9, 47.3), "10.4x47 mm R Italian Vetterli": (13.9, 34.75),
                    ".450/400 Nitro Express 2⅜ inch": (11.5, 40.3),
                    "7 mm Canadian Magnum": (23.6, 59.0), ".338 Canadian Magnum": (28.1, 59.98),
                    ".32-30 Remington": (4.0, 31.18), "10.75x58 mm R Russian Berdan": (7.9, 38.45),
                    ".577/500 Nitro Express": (8.9, 59.96), "6x58 mm Forster": (13.4, 41.27),
                    ".416 Rimmed": (16.1, 69.12)}
        specs = self.bottlenecks()
        for name, (angle, start) in drawings.items():
            with self.subTest(name):
                self.assertEqual(cartridges.shoulder_angle(name), angle)
                self.assertIn("municion.org", cartridges.SHOULDER_ANGLES[name][1])
                self.assertEqual(specs[name]["sh_at"], start)

    def test_shoulders_from_other_drawings_and_photos(self):
        # (half angle, shoulder start, a word of the source) for angles from drawings, prints and photos.
        found = {"11x50 mm R Albini": (18.6, 42.5, "naboje.org"),
                 "6.8x45 mm UCC": (45, 36.1, "pacifictoolandgauge"),
                 ".44-77 Sharps & Remington": (4.5, 33.0, "ammo-one1"),
                 ".40-70 Winchester": (13.26, 44.45, "winchestercollector")}
        specs = self.bottlenecks()
        for name, (angle, start, source) in found.items():
            with self.subTest(name):
                self.assertEqual(cartridges.shoulder_angle(name), angle)
                self.assertIn(source, cartridges.SHOULDER_ANGLES[name][1])
                self.assertEqual(specs[name]["sh_at"], start)

    def test_unsourced_shoulders_keep_the_default(self):
        self.assertEqual(cartridges.shoulder_angle("New calibre"), cartridges.DEFAULT_SHOULDER_ANGLE)

    # Rimless, semi-rimmed and belted cases without an extractor groove from a drawing (C.I.P., SAAMI, AECC) of
    # their own or of a related case (its parent, or a case made from it); they get the generic groove, behind
    # their own rim thickness where a source gives one. A new rimless, semi-rimmed or belted calibre needs a head
    # in CASE_HEADS or a place here.
    HEAD_UNSOURCED = {
        # Measured only from a dimension table in Cartridges of the World, which gives no groove.
        ".360 Mars", ".45-70 Auto", ".50-115 Bullard", "6.17 Lazzeroni Flash",
        "6.71 Lazzeroni Blackbird", "8.5 mm Mars",
        # Cannon rounds without a specimen drawing that shows the head (catalogue only).
        "20x139 mm FMK", "27x145 mm B", "45x386 mm SR", "50x346 mm B", "57x348 mm SR",
    }

    SHALLOW_CONES = {".32 Winchester Self-Loading": 3.7, ".35 Winchester Self-Loading": 8.0,
                     ".401 Winchester Self-Loading": 7.0}
    # Small pistol heads: a rim under 0.7 mm thick or a groove that ends less than 2 mm up, on their AECC drawings
    # (the 5 mm Clement's rim is the book's).
    SMALL_HEADS = {"2.7 mm Kolibri", "3 mm Kolibri", "4.25 mm Liliput", "5 mm Bergmann", "5 mm Clement", "6.5 mm Bergmann"}

    def rimless(self):
        return {s["name"]: s for _, items in cartridges.ALL_CATALOGUE for s in items
                if s["kind"] in (RIMLESS, SEMI_RIMMED, BELTED)}

    def test_every_rimless_head_is_sourced_or_listed(self):
        self.assertEqual(set(self.rimless()) - set(cartridges.CASE_HEADS), self.HEAD_UNSOURCED)
        self.assertEqual(set(cartridges.CASE_HEADS) - set(self.rimless()), set())
        for name, (thick, top_at, groove, angle, url) in cartridges.CASE_HEADS.items():
            with self.subTest(name):
                s = self.rimless()[name]
                self.assertTrue(url.startswith("https://") or url.startswith("book:"), url)
                # The .55 Boys: 9.0.
                low = (0.4, 1.3) if name in self.SMALL_HEADS else (0.7, 2.0)
                high = (2.5, 9.5)
                if cartridges.categories(name)[0] == "Kanone":  # a cannon round: the 35x228 mm's rim is 5.08 mm thick, the 20x138 mm B's belt ends at 15.34
                    low, high = (1.5, 5.0), (6.0, 16.0)
                self.assertTrue(low[0] < thick < high[0] and low[1] < top_at < high[1])
                # A groove's front ramp is 10 degrees or more. Three Winchester self-loading cases have a shallow
                # cone in its place on their C.I.P. sheets: from the rim's front on the .32 and .401, after a
                # 0.64 mm groove floor on the .35.
                self.assertTrue(10 <= angle <= 75 or self.SHALLOW_CONES.get(name) == angle, angle)
                self.assertLess(groove, min(s["rim"], s["base"]))

    def test_heads_are_drawn_from_their_own_groove(self):
        # Regression: every rimless head used to get one generic groove (82 % of the base, 1.3 mm rim).
        for name, s in self.rimless().items():
            head = cartridges.case_head(name)
            if not head:
                continue
            thick, top_at, groove, angle = head
            with self.subTest(name):
                prof = outline.case_profile(s)
                self.assertEqual(prof[1], (s["rim"] / 2, thick))
                self.assertEqual(prof[2], (groove / 2, thick))
                (r0, h0), (r1, h1) = prof[3], prof[4]
                self.assertEqual(r0, groove / 2)
                self.assertGreaterEqual(h0, thick)
                if s["kind"] in (RIMLESS, SEMI_RIMMED):
                    self.assertEqual(h1, top_at)
                    if h0 > thick:  # the ramp keeps its angle unless it would cut into the rim
                        self.assertAlmostEqual(math.degrees(math.atan2(r1 - r0, h1 - h0)), angle, places=6)
                else:
                    self.assertAlmostEqual(math.degrees(math.atan2(r1 - r0, h1 - h0)), angle, places=6)
                    belt = s["belt"] or s["rim"]  # as wide as the rim unless the file gives it
                    self.assertEqual(prof[5], (belt / 2, top_at))  # front of the belt
                heights = [h for _, h in prof]
                self.assertEqual(heights, sorted(heights))
        self.assertGreater(len({h[:4] for h in cartridges.CASE_HEADS.values()}), 40)

    def test_a_belt_wider_than_the_rim_is_drawn_at_its_own_diameter(self):
        # C.I.P. 378 Weath. Mag.: rim R1 14.71, belt R3 15.33 up to E 6.40, body P1 14.78. The belt used to be
        # drawn at the rim's diameter, below the body: the ten cases on this head showed no belt at all (2026-11-14).
        s = self.rimless()[".378 Weatherby Magnum"]
        prof = [(round(r, 4), round(h, 4)) for r, h in outline.case_profile(s)[:7]]
        self.assertEqual(prof[:4], [(7.35, 0), (7.35, 1.6), (6.285, 1.6), (6.285, 2.6)])  # rim and groove
        self.assertEqual(prof[4:6], [(7.665, 3.98), (7.665, 6.4)])  # the belt, after a 45 degree ramp
        self.assertEqual(prof[6], (7.4, 6.4))  # the body in front of it, at the base diameter
        self.assertEqual(outline.outline(s)["width"], 15.33)  # the belt is the widest part

    def test_the_body_in_front_of_a_belt_starts_at_the_base_diameter(self):
        # The base diameter of a belted case is the body's in front of the belt (P1 on the C.I.P. sheets). The body
        # used to be drawn 1.5 % narrower than that, 0.2 mm on most of these cases and 0.3 mm on the .55 Boys
        # (2026-11-14).
        belted = [s for _, s in outline.specs() if s["kind"] == BELTED]
        self.assertTrue(belted)
        for s in belted:
            with self.subTest(s["name"]):
                (belt, belt_front), (body, body_from) = outline.case_profile(s)[5:7]
                self.assertEqual((body, body_from), (s["base"] / 2, belt_front))
                self.assertGreater(belt, body, "a belt no wider than the body does not show: [mm] belt gives its diameter")

    def test_a_long_ramp_stops_at_the_front_of_the_belt(self):
        # A cannon-sized belted case on the generic head (the 50x346 mm B's rim and body): at 40 degrees the ramp
        # would end 2 mm beyond the belt's front, and the outline would turn back on itself.
        s = cartridges.c("a 50 mm belted case", BELTED, 68.0, 68.0, None, 52.0, 346.0, None, 500.0, 50.0, SPITZER)
        prof = outline.case_profile(s)
        self.assertEqual(prof[4], (34.0, 5.6))  # the ramp ends where the belt does
        heights = [h for _, h in prof]
        self.assertEqual(heights, sorted(heights))

    def test_heads_follow_the_sheets(self):
        # (R rim thickness, E, E1 groove diameter, ramp angle) on the C.I.P. sheets.
        sheets = {
            ".308 Winchester": (1.37, 3.85, 10.39, 36.0), "9x19 mm": (1.27, 2.98, 8.79, 35.0),
            ".45 ACP": (1.24, 4.11, 10.16, 26.0), ".300 Winchester Magnum": (1.27, 5.59, 12.07, 35.0),
            "7.5x55 mm Swiss (GP 11)": (1.65, 3.46, 10.3, 51.8), ".50 BMG": (2.26, 6.23, 17.27, 36.0),
            "5.6 mm GP 90": (1.14, 3.13, 8.43, 25.0),  # .223 case, via the 223 Rem. sheet
        }
        for name, values in sheets.items():
            self.assertEqual(cartridges.case_head(name), values, name)

    def test_rims_are_drawn_at_their_own_thickness(self):
        # Regression: rimmed cases were all drawn with a 1.5 mm rim, rimfire ones with 1.1 mm and
        # rimless ones without a C.I.P. head with 1.3 mm (2026-11-11).
        drawn = 0
        for _, s in outline.specs():
            t = cartridges.rim_thickness(s["name"])
            if t is None or s["kind"] not in (RIMMED, RIMFIRE, RIMLESS, SEMI_RIMMED, BELTED):
                continue
            with self.subTest(s["name"]):
                # The thinnest: .020 in., the 5 mm Bergmann pistol round; the thickest: .100 in., the Werndl M77.
                # Under that only the 2.7 mm Kolibri, 0.41 mm on its AECC drawing.
                self.assertTrue(0.5 <= t <= 2.54 or (s["name"], t) == ("2.7 mm Kolibri", 0.41), t)
                self.assertEqual(outline.case_profile(s)[1], (s["rim"] / 2, t))
                drawn += 1
        self.assertGreater(drawn, 330)

    def test_rim_thicknesses_follow_their_sources(self):
        values = {".30-30 Winchester": 1.6, "11x60 mm R Mauser": 2.4, ".470 Nitro Express": 1.02,  # C.I.P. R
                  ".22 LR": 1.02, ".38 Special": 1.5,  # .040 in, COTW 18; .059 in, SAAMI
                  "7.62x38 mm R Nagant": 1.22}  # .048 in, Donnelly
        for name, t in values.items():
            self.assertEqual(cartridges.rim_thickness(name), t, name)

    def test_shot_shells_draw_their_rim_at_its_cip_thickness(self):
        # t on the C.I.P. Tab. VII sheets, maximum cartridge (2026-11-16); before, every shell's rim was 1.5 mm.
        thickness = {"12/70": 1.85, "12/76": 1.85, "12/89": 1.85, "16/70": 1.65, "20/70": 1.55, "20/76": 1.55,
                     "28/70": 1.55, ".410/76": 1.55}
        shells = {s["name"]: s for _, s in outline.specs() if s["kind"] == SHOT}
        self.assertEqual(set(shells), set(thickness))
        for name, t in thickness.items():
            with self.subTest(name):
                self.assertEqual(cartridges.rim_thickness(name), t)
                self.assertIn("tab-vii", cartridges.sources(name, "case_head")[0])
                s = shells[name]
                head = points(outline.outline(s)["head"])
                # The head's outline runs out to the rim and up to t before it steps in to the hull.
                self.assertIn(round(s["oal"] - t, 2), {round(y, 2) for _, y in head})
                self.assertEqual(outline.gaps(s), ())

    def test_rims_without_a_source_keep_the_old_drawing(self):
        # A rim no source gives a thickness is drawn as before rim thicknesses came in (2026-11-11).
        by_name = {s["name"]: s for _, s in outline.specs()}

        def head(name, n):
            self.assertIsNone(cartridges.rim_thickness(name), name)
            return [(round(r, 4), round(h, 4)) for r, h in outline.case_profile(by_name[name])[:n]]
        self.assertEqual(head(".32 Short Rimfire", 3), [(4.735, 0), (4.735, 1.1), (4.01, 1.1)])
        self.assertEqual(head(".44 Colt", 3), [(6.53, 0), (6.53, 1.5), (5.79, 1.5)])
        # Every rimless and every belted case in the catalogue has a rim thickness now: two made up for the test.
        made_up = [(RIMLESS, 11.86, 12.52, 12.17, 11.35, 62.74, 52.26, 81.79, 10.77, [(5.93, 0), (5.93, 1.3)]),
                   (BELTED, 13.54, 13.39, 12.27, 8.0, 72.9, 52.04, 98.55, 7.21, [(6.77, 0), (6.77, 1.3)])]
        for kind, *sizes, rim in made_up:
            case = cartridges.c("A case", kind, *sizes, SPITZER)
            self.assertEqual([(round(r, 4), round(h, 4)) for r, h in outline.case_profile(case)[:2]], rim)

    def test_generic_heads_are_fitted_to_the_sourced_ones(self):
        # Review 2026-11-13: the old generic groove, 82 % of the base, was deeper than 224 of the 233 sourced
        # ones (half of them by 0.6 mm and more) and wider than the rim under a rebated one. The generic head,
        # worked out for the cases that have a sourced one, stays close to it: half of them are within 0.2 mm
        # in the groove's diameter and within 0.25 mm in the ramp's top or the belt's front.
        specs = self.rimless()
        grooves, tops = [], []
        for name, (thick, top_at, groove, _, _) in cartridges.CASE_HEADS.items():
            head = outline.generic_head(specs[name])
            self.assertEqual(head[0], thick, name)
            tops.append(abs(head[1] - top_at))
            grooves.append(abs(head[2] - groove))
        self.assertLess(statistics.median(grooves), 0.2)
        self.assertLess(statistics.median(tops), 0.25)

    def test_generic_heads_are_drawn_for_every_kind_of_rim(self):
        specs = self.rimless()

        def head(name, n):
            self.assertIn(name, self.HEAD_UNSOURCED)
            return [(round(r, 4), round(h, 4)) for r, h in outline.case_profile(specs[name])[:n]]
        # Rimless: the groove is 87 % of the rim, 1 mm long, and a 40 degree ramp leads up to the body.
        self.assertEqual(head("6.17 Lazzeroni Flash", 5),
                         [(6.73, 0), (6.73, 1.27), (5.8551, 1.27), (5.8551, 2.27), (6.73, 3.3127)])
        # Rebated (rim 12.01 mm on a 14.94 mm body): the groove is below the rim, the ramp climbs on to the body.
        # The rebated cases of the catalogue have their own heads now, so this one is made up.
        rebated = cartridges.c("A rebated case", RIMLESS, 12.01, 14.94, 14.66, 12.8, 55.78, 40.88, 72.39, 12.06, SPITZER)
        self.assertEqual([(round(r, 4), round(h, 4)) for r, h in outline.case_profile(rebated)[:5]],
                         [(6.005, 0), (6.005, 1.3), (5.2244, 1.3), (5.2244, 2.3), (7.47, 4.9763)])
        # Semi-rimmed (rim 15.72 mm on a 14.86 mm body): the groove is 90 % of the body, not level with it.
        self.assertEqual(head(".50-115 Bullard", 5),
                         [(7.86, 0), (7.86, 1.5), (6.687, 1.5), (6.687, 2.5), (7.43, 3.3855)])
        # Belted: the ramp ends on the belt, which ends 4.3 mm in front of the default 1.3 mm rim. Every belted
        # case in the catalogue has its own head now, so this one is made up (a rim of 13.54 mm, a body of 13.39).
        belted = cartridges.c("A belted case", BELTED, 13.54, 13.39, 12.27, 8.0, 72.9, 52.04, 98.55, 7.21, SPITZER)
        self.assertEqual([(round(r, 4), round(h, 4)) for r, h in outline.case_profile(belted)[:7]],
                         [(6.77, 0), (6.77, 1.3), (5.8899, 1.3), (5.8899, 2.3), (6.77, 3.3489), (6.77, 5.6), (6.695, 5.6)])
        for name in self.HEAD_UNSOURCED:
            if None in (specs[name]["base"], specs[name]["neck"]):  # a cannon round without the sizes to draw it
                continue
            with self.subTest(name):
                s, prof = specs[name], outline.case_profile(specs[name])
                self.assertLess(prof[2][0], min(s["rim"], s["base"]) / 2)  # a groove, below the rim and the body
                heights = [h for _, h in prof]
                self.assertEqual(heights, sorted(heights))

if __name__ == "__main__":
    unittest.main()
