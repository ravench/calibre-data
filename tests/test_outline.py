"""python3 -m unittest discover -s tests"""
import os, re, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import outline  # noqa: E402
from cartridges import PATCHED, CRIMPED, LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP, BRASS, HYBRID, CASES, bullet, case_material  # noqa: E402

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
                paths = [o[k] for k in ("case", "head", "bullet", "patch", "tip") if k in o]
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

    def test_only_paper_patched_bullets_have_a_patch(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            has_bullet = s["oal"] > s["case"] + 0.1 and "case" in o
            patched = s["profile"] == PATCHED or bullet(s["name"]) == PAPER_PATCHED
            self.assertEqual("patch" in o, patched and has_bullet, s["name"])
            self.assertEqual(o.get("bulletMaterial") == "steel", s["profile"] == PATCHED and has_bullet, s["name"])

    def test_lead_bullets_are_drawn_in_lead(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            if "case" in o and "bullet" in o and s["profile"] != PATCHED:
                lead = bullet(s["name"]) in (LEAD, PAPER_PATCHED)
                self.assertEqual(o.get("bulletMaterial") == "lead", lead, s["name"])

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

    def test_hybrid_case_has_a_steel_head(self):
        for _, s in outline.specs():
            o = outline.outline(s)
            self.assertEqual(o.get("headMaterial") == "steel", case_material(s["name"]) == HYBRID, s["name"])
        fury = outline.outline(next(s for _, s in outline.specs() if s["name"] == ".277 SIG Fury"))
        ys = [y for _, y in points(fury["head"])]
        # y grows from the tip: the head runs from the base up to HYBRID_HEAD.
        self.assertAlmostEqual(max(ys), fury["height"], places=2)
        self.assertAlmostEqual(min(ys), fury["height"] - outline.HYBRID_HEAD, places=2)

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

    def test_rimmed_alarm_blank_draws_a_rim_and_a_crimp(self):
        s = next(s for _, s in outline.specs() if s["name"] == "9 mm R Knall")
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
            [".45 ACP", ".45 Super"],
            [".223 Remington", "5.56x45 mm NATO", "5.6 mm GP 90"],
            ["7.62x51 mm NATO", ".308 Winchester"],
        ])

    def test_outline_is_deterministic(self):
        _, s = outline.specs()[0]
        self.assertEqual(outline.outline(s), outline.outline(dict(s)))


    def test_necks_start_where_the_municion_drawings_show(self):
        # AECC specimen drawings on municion.org: (shoulder start SL, neck length NL, case length CL), mm.
        # The outline draws a 32-degree shoulder, so sh_at sits where the drawn neck begins
        # (CL - NL) minus that shoulder, and never well before the drawn shoulder start.
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
            with self.subTest(name):
                s = specs[name]
                top = s["neck"] / 2
                neck_start = next(h for r, h in outline.case_profile(s) if abs(r - top) < 1e-9)
                self.assertLess(abs(neck_start - (case_length - neck_length)), 1.5)
                self.assertGreater(s["sh_at"], shoulder_start - 0.6)

if __name__ == "__main__":
    unittest.main()
