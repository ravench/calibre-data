"""python3 -m unittest discover -s tests"""
import math, os, re, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import outline  # noqa: E402
import cartridges  # noqa: E402
from cartridges import PATCHED, CRIMPED  # noqa: E402

PATH = re.compile(r"^M[\d.]+ [\d.]+( L[\d.]+ [\d.]+)* Z$")


def points(d):
    return [tuple(map(float, p.split())) for p in d[1:-2].split(" L")]


class OutlineTests(unittest.TestCase):
    def test_every_calibre_has_a_valid_outline_inside_its_box(self):
        for _, s in outline.specs():
            with self.subTest(s["name"]):
                o = outline.outline(s)
                self.assertAlmostEqual(o["height"], s["oal"], places=2)
                self.assertAlmostEqual(o["width"], max(s["rim"], s["base"], s["bullet"]), places=2)
                paths = [o[k] for k in ("case", "head", "bullet", "patch") if k in o]
                self.assertTrue(paths)
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

    def test_only_the_paper_patched_bullet_has_a_patch(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            self.assertEqual("patch" in o, s["profile"] == PATCHED and s["oal"] > s["case"] + 0.1, s["name"])
            self.assertEqual(o.get("bulletMaterial") == "steel", "patch" in o, s["name"])

    def test_crimped_blank_is_a_case_narrowing_to_the_mouth(self):
        s = next(s for _, s in outline.specs() if s["name"] == ".22 Blank (6.8/11)")
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

    def test_only_blanks_are_crimped(self):
        for _, s in outline.specs():
            if s["profile"] == CRIMPED:
                self.assertEqual(s["oal"], s["case"], s["name"])

    def test_identical_groups(self):
        self.assertEqual(outline.identical_groups(), [
            [".45 ACP", ".45 Super"],
            [".223 Remington", "5.56x45 mm NATO", "5.6 mm GP 90"],
            ["7.62x51 mm NATO", ".308 Winchester"],
        ])

    def test_outline_is_deterministic(self):
        _, s = outline.specs()[0]
        self.assertEqual(outline.outline(s), outline.outline(dict(s)))


    def test_necks_start_where_the_municion_drawings_show(self):
        # AECC specimen drawings on municion.org: (shoulder start SL, neck length NL, case length CL), mm.
        # sh_at sits where the drawn neck begins (CL - NL) minus the calibre's shoulder, and never
        # well before the drawn shoulder start. Calibres with a C.I.P. sheet follow the sheet
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
            ".416 Barrett": (63.5, 12.17, 82.95),
        }
        specs = {s["name"]: s for _, s in outline.specs()}
        for name, (shoulder_start, neck_length, case_length) in drawn.items():
            if cartridges.SHOULDER_ANGLES.get(name, (0, ""))[1].startswith(cartridges._CIP):
                continue
            with self.subTest(name):
                s = specs[name]
                top = s["neck"] / 2
                neck_start = next(h for r, h in outline.case_profile(s) if abs(r - top) < 1e-9)
                self.assertLess(abs(neck_start - (case_length - neck_length)), 1.5)
                self.assertGreater(s["sh_at"], shoulder_start - 0.6)

    # Bottleneck calibres still drawn with DEFAULT_SHOULDER_ANGLE: no C.I.P. sheet, SAAMI drawing
    # or article giving the angle was found yet. Remove a name here when its angle is added.
    SHOULDER_UNSOURCED = {
        ".17 Winchester Super Magnum", ".400 Cor-Bon", ".256 Winchester Magnum", "9x25 mm Dillon", ".22 TCM",
        "8 mm Nambu", ".25 NAA", ".32 NAA", ".338 ARC", "9x39 mm", "6 mm GT", ".22 Creedmoor",
        "7 mm Backcountry", "8.6 Blackout", ".22 ARC", ".338 Ruger Compact Magnum",
        "7.5x53.5 mm Swiss (GP 1890)", ".300 HAM'R", "6.5x58 mm Vergueiro", ".375 CheyTac",
        "7.7x58 mm Arisaka", "8x50 mm R Lebel", "7.35x51 mm Carcano", ".277 SIG Fury", "5.8x42 mm",
        ".25-35 Winchester", ".32 Winchester Special", ".264 Winchester Magnum", ".55 Boys",
        "8.5x55 mm Blaser", ".38-56 WCF", ".22 Nosler", "6.5-300 Weatherby Magnum", ".17 Hornet",
        "6.8 Western", ".26 Nosler", ".27 Nosler", ".30 Nosler", ".33 Nosler", ".300 Ruger Compact Magnum",
        ".224 Valkyrie", ".458 SOCOM", ".222 Remington Magnum", ".25 Weatherby RPM", "6.5 Weatherby RPM",
        ".338 Weatherby RPM", "7.92x107 mm DS", ".308 Norma Magnum", ".404 Jeffery", ".416 Barrett",
        "10.4x38 mm R Vetterli", "11x59 mm R Gras", "11x60 mm R Mauser",
    }

    def bottlenecks(self):
        return {s["name"]: s for _, s in outline.specs() if s["shoulder"] and s["profile"] != CRIMPED}

    def test_every_bottleneck_has_a_sourced_angle_or_is_listed(self):
        sourced = set(cartridges.SHOULDER_ANGLES)
        self.assertEqual(sourced - set(self.bottlenecks()), set(), "angles for calibres without a shoulder")
        self.assertEqual(set(self.bottlenecks()) - sourced, self.SHOULDER_UNSOURCED)
        for name, (angle, url) in cartridges.SHOULDER_ANGLES.items():
            with self.subTest(name):
                self.assertTrue(2 <= angle <= 55, angle)
                self.assertTrue(url.startswith("https://"), url)

    def test_shoulders_are_drawn_at_their_own_angle(self):
        # Regression: every shoulder used to be drawn at one shared 32-degree slope.
        for name, s in self.bottlenecks().items():
            with self.subTest(name):
                prof = outline.case_profile(s)
                top = s["neck"] / 2
                i = next(i for i, (r, _) in enumerate(prof) if abs(r - top) < 1e-9)
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
        }
        specs = self.bottlenecks()
        for name, (angle, l1, l2) in sheets.items():
            with self.subTest(name):
                s = specs[name]
                self.assertEqual(cartridges.shoulder_angle(name), angle)
                self.assertEqual(s["sh_at"], l1)
                top = s["neck"] / 2
                neck_start = next(h for r, h in outline.case_profile(s) if abs(r - top) < 1e-9)
                self.assertLess(abs(neck_start - l2), 0.6)

    def test_unsourced_shoulders_keep_the_default(self):
        self.assertEqual(cartridges.shoulder_angle(".22 Nosler"), cartridges.DEFAULT_SHOULDER_ANGLE)

if __name__ == "__main__":
    unittest.main()
