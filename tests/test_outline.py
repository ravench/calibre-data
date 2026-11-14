"""python3 -m unittest discover -s tests"""
import math, os, re, statistics, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import outline  # noqa: E402
import cartridges  # noqa: E402
from cartridges import SPITZER, ROUND, FLAT, PATCHED, CRIMPED, BALL_NOSE, RIMLESS, SEMI_RIMMED, BELTED, RIMMED, RIMFIRE, LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP, HOLLOW_POINT, STEEL, BRASS, HYBRID, PAPER, SHOT, CASES, BALL, MINIE, PELLET, bullet, jacket, case_material, current_case_materials, loose_material  # noqa: E402

PATH = re.compile(r"^M[\d.]+ [\d.]+( L[\d.]+ [\d.]+)* Z$")


def points(d):
    return [tuple(map(float, p.split())) for p in d[1:-2].split(" L")]


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
        o = outline.outline(by_name["7.5x53.5 mm Swiss (GP 1890)"])
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
            [".38 Super", ".38 ACP"],  # one SAAMI drawing (.38 Super Automatic +P / .38 Automatic)
            [".223 Remington", "5.56x45 mm NATO", "5.6 mm GP 90"],
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
            if cartridges.SHOULDER_ANGLES.get(name, (0, ""))[1].startswith("https://bobp.cip-bobp.org/uploads/tdcc/"):  # a C.I.P. sheet
                continue
            with self.subTest(name):
                s = specs[name]
                top = s["neck"] / 2
                neck_start = next(h for r, h in outline.case_profile(s) if abs(r - top) < 1e-9 and h > s["sh_at"])
                self.assertLess(abs(neck_start - (case_length - neck_length)), 1.5)
                self.assertGreater(s["sh_at"], shoulder_start - 0.6)

    # Bottleneck calibres still drawn with DEFAULT_SHOULDER_ANGLE: no C.I.P. sheet, SAAMI drawing
    # or article giving the angle was found yet. Remove a name here when its angle is added.
    SHOULDER_UNSOURCED = {
        # Measured only from a dimension table in Cartridges of the World, which gives no angle (their
        # shoulder_at is estimated, as the note in [mm] says).
        ".275 No. 2 Magnum", ".276 Pedersen",
        ".32-30 Remington", ".32-40 Remington",
        ".338 Canadian Magnum",
        ".38-70 Winchester", ".38-90 Winchester Express",
        ".40-70 Peabody What Cheer",
        ".400/360 Nitro Express",
        ".400/375 Belted Nitro Express", ".416 Rimmed",
        ".45-100 Remington Necked",
        ".45-125 Winchester Express",
        ".50-115 Bullard",
        ".500/450 Magnum Express", ".500/450 Nitro Express", ".500/450 No. 1 Express",
        ".56-52 Spencer Necked", ".577/500 Nitro Express",
        ".577/500 No. 2 Express", "10.25x69 mm R Hunting-Express", "10.4x47 mm R Italian Vetterli",
        "10.75x57 mm Mannlicher", "10.75x58 mm R Russian Berdan",
        "10.8x47 mm R Martini Target",
        "11.4x50 mm R Brazilian Comblain", "11x53 mm R Comblain",
        "11x52 mm R Beaumont M71/78", "6.5x53.5 mm SR Daudeteau",
        "6x57 mm Mauser", "6x58 mm Forster", "7 mm Canadian Magnum",
        "8.5 mm Mars",
        "9.3x75 mm R Nimrod",
        "9x70 mm R Mauser",
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
        drawings = {".22 Nosler": (29.9, 35.29), ".38-56 WCF": (6.5, 30.64), "6.5x58 mm Vergueiro": (10.8, 41.0),
                    ".458 SOCOM": (35.2, 30.0), "10.4x38 mm R Vetterli": (10.6, 26.11),
                    ".280 British": (19.4, 30.97), "6 mm Lee Navy": (18.3, 43.75),
                    ".246 Purdey Flanged": (16.0, 46.3), ".400 A-Square DPM": (26.9, 59.1)}
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
                 ".450/400 Nitro Express 2⅜ inch": (5.2, 46.1, "tabiical-en-page52"),
                 ".40-70 Winchester": (13.26, 44.45, "winchestercollector")}
        specs = self.bottlenecks()
        for name, (angle, start, source) in found.items():
            with self.subTest(name):
                self.assertEqual(cartridges.shoulder_angle(name), angle)
                self.assertIn(source, cartridges.SHOULDER_ANGLES[name][1])
                self.assertEqual(specs[name]["sh_at"], start)

    def test_unsourced_shoulders_keep_the_default(self):
        self.assertEqual(cartridges.shoulder_angle("New calibre"), cartridges.DEFAULT_SHOULDER_ANGLE)

    # Rimless, semi-rimmed and belted cases without an extractor groove from a C.I.P. sheet (or a parent case that has
    # one); they get the generic groove, behind their own rim thickness where a source gives one. A new
    # rimless, semi-rimmed or belted calibre needs a head in CASE_HEADS or a place here.
    HEAD_UNSOURCED = {
        ".22 Nosler", ".22 TCM", ".25 Weatherby RPM", ".27 Nosler",
        ".277 SIG Fury", ".30 Remington AR",
        ".32 Winchester Self-Loading", ".33 Nosler",
        ".338 Weatherby RPM", ".35 S&W Auto", ".35 Winchester Self-Loading",
        ".351 Winchester Self-Loading", ".375 CheyTac",
        ".401 Winchester Self-Loading", ".408 CheyTac",
        ".458 SOCOM", ".50 Beowulf",
        ".55 Boys", "12.7x108 mm", "5.8x42 mm", "6 mm GT",
        "6.5x58 mm Vergueiro", "7.5 FK",
        "7.5x53.5 mm Swiss (GP 1890)", "7.5x54.5 mm Swiss (GP 90/23)", "7.5 mm Kadettenpatrone",
        "7.7x58 mm Arisaka", "7.92x107 mm DS", "8 mm Nambu",
        "9 mm P.A.K.", "9x23 mm Largo", "9x23 mm Winchester",
        ".315 Knall", "8 mm Knall",  # alarm blanks: head not read from C.I.P. Tab. VIII yet
        # Measured only from a dimension table in Cartridges of the World, which gives no groove.
        ".242 Rimless Nitro Express", ".256 Gibbs Magnum", ".26 BSA", ".275 H&H Magnum",
        ".276 Enfield", ".276 Pedersen", ".280 British", ".280 Jeffery", ".280 Ross", ".30 Borchardt",
        ".30 Newton", ".30 USA Rimless", ".300 Dakota", ".303 Magnum", ".33 BSA", ".330 Dakota",
        ".333 Jeffery Rimless", ".338 Canadian Magnum", ".338 Lehigh", ".35 Newton", ".360 Mars",
        ".375 Dakota", ".400/375 Belted Nitro Express", ".416 Dakota", ".425 Westley Richards Magnum",
        ".44 Auto Mag", ".45 Blaser", ".45 Mars Long", ".45 Mars Short", ".45 Remington Thompson",
        ".45-70 Auto", ".450 Dakota", ".455 Webley Automatic",
        ".458 Canadian Magnum", ".475 Bishop Short Magnum", ".50 GI", ".50-115 Bullard", ".500 Phantom",
        ".577 Tyrannosaur", "10.57 Lazzeroni Maverick", "10.57 Lazzeroni Meteor",
        "10.75x57 mm Mannlicher", "10.75x63 mm Mauser", "10.75x68 mm Mauser", "11.2x60 mm Schüler",
        "11.2x72 mm Schüler", "12.04 Bibamufu", "2.7 mm Kolibri", "3 mm Kolibri", "4.25 mm Liliput",
        "4.85x49 mm British", "5 mm Bergmann", "5 mm Clement", "5.2x68 mm Mondragón", "5.8x21 mm DAP92",
        "5x58 mm Sturtevant", "6 mm Lee Navy", "6 mm SAW", "6.17 Lazzeroni Flash", "6.17 Lazzeroni Spitfire",
        "6.5 mm Bergmann", "6.53 Lazzeroni Scramjet", "6.5x53.5 mm SR Daudeteau", "6.5x61 mm Mauser",
        "6.71 Lazzeroni Blackbird", "6.71 Lazzeroni Phantom", "6x58 mm Forster", "7 mm Canadian Magnum",
        "7 mm Dakota", "7 mm Nambu", "7.21 Lazzeroni Firebird", "7.21 Lazzeroni Firehawk",
        "7.21 Lazzeroni Tomahawk", "7.63 mm Mannlicher", "7.65 mm Roth-Sauer", "7.82 Lazzeroni Patriot",
        "7.82 Lazzeroni Warbird", "7.92x24 mm", "7x73 mm Vom Hofe Belted", "8.5 mm Mars",
        "8.59 Lazzeroni Galaxy", "8.59 Lazzeroni Titan", "8x59 mm Breda", "8x63 mm Swedish",
        "8x71 mm Peterlongo", "9 mm Winchester Magnum", "9.09 Lazzeroni Eagle", "9.3x53 mm Swiss",
        "9.53 Lazzeroni Hellcat", "9.53 Lazzeroni Saturn", "9.8 mm Auto Colt", "9x63 mm", "9x71 mm Peterlongo",
    }

    def rimless(self):
        return {s["name"]: s for _, s in outline.specs() if s["kind"] in (RIMLESS, SEMI_RIMMED, BELTED)}

    def test_every_rimless_head_is_sourced_or_listed(self):
        self.assertEqual(set(self.rimless()) - set(cartridges.CASE_HEADS), self.HEAD_UNSOURCED)
        self.assertEqual(set(cartridges.CASE_HEADS) - set(self.rimless()), set())
        for name, (thick, top_at, groove, angle, url) in cartridges.CASE_HEADS.items():
            with self.subTest(name):
                s = self.rimless()[name]
                self.assertTrue(url.startswith("https://") or url.startswith("book:"), url)
                self.assertTrue(0.7 < thick < 2.5 and 2.0 < top_at < 7.0 and 10 <= angle <= 75)
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
        self.assertLess(prof[6][0], 7.4)  # the body in front of it
        self.assertEqual(outline.outline(s)["width"], 15.33)  # the belt is the widest part
        for _, s in outline.specs():  # every belt stands out from the body
            if s["kind"] == BELTED:
                with self.subTest(s["name"]):
                    self.assertGreaterEqual(outline.case_profile(s)[5][0], s["base"] / 2)

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
            "5.6 mm GP 90": (1.14, 3.15, 8.43, 25.0),  # .223 case, via the .300 BLK sheet
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
                self.assertTrue(0.5 <= t <= 2.54, t)
                self.assertEqual(outline.case_profile(s)[1], (s["rim"] / 2, t))
                drawn += 1
        self.assertGreater(drawn, 330)

    def test_rim_thicknesses_follow_their_sources(self):
        values = {".30-30 Winchester": 1.6, "11x60 mm R Mauser": 2.4, ".470 Nitro Express": 1.02,  # C.I.P. R
                  ".22 LR": 1.02, ".38 Special": 1.5,  # .040 in, COTW 18; .059 in, SAAMI
                  "7.62x38 mm R Nagant": 1.22}  # .048 in, Donnelly
        for name, t in values.items():
            self.assertEqual(cartridges.rim_thickness(name), t, name)

    def test_rims_without_a_source_keep_the_old_drawing(self):
        # A rim no source gives a thickness is drawn as before rim thicknesses came in (2026-11-11).
        by_name = {s["name"]: s for _, s in outline.specs()}

        def head(name, n):
            self.assertIsNone(cartridges.rim_thickness(name), name)
            return [(round(r, 4), round(h, 4)) for r, h in outline.case_profile(by_name[name])[:n]]
        self.assertEqual(head(".32 Short Rimfire", 3), [(4.735, 0), (4.735, 1.1), (4.01, 1.1)])
        self.assertEqual(head(".44 Colt", 3), [(6.53, 0), (6.53, 1.5), (5.79, 1.5)])
        self.assertEqual(head(".276 Pedersen", 2), [(5.73, 0), (5.73, 1.3)])
        self.assertEqual(head(".55 Boys", 2), [(10.15, 0), (10.15, 1.3)])

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
        self.assertEqual(head(".276 Pedersen", 5), [(5.73, 0), (5.73, 1.3), (4.9851, 1.3), (4.9851, 2.3), (5.7, 3.152)])
        # Rebated (rim 12.01 mm on a 14.94 mm body): the groove is below the rim, the ramp climbs on to the body.
        self.assertEqual(head(".475 Bishop Short Magnum", 5),
                         [(6.005, 0), (6.005, 1.37), (5.2244, 1.37), (5.2244, 2.37), (7.47, 5.0463)])
        # Semi-rimmed (rim 9.91 mm on a 8.93 mm body): the groove is 90 % of the body, not level with it.
        self.assertEqual(head(".32 Winchester Self-Loading", 5),
                         [(4.955, 0), (4.955, 1.27), (4.0185, 1.27), (4.0185, 2.27), (4.465, 2.8021)])
        # Belted: the ramp ends on the belt, which ends 4.3 mm in front of the rim (the .55 Boys' own belt, 21.59 mm,
        # stands over its 20.3 mm rim); behind a rim of .062 in (COTW 18) groove and belt move up with it.
        self.assertEqual(head(".55 Boys", 7), [(10.15, 0), (10.15, 1.3), (8.8305, 1.3), (8.8305, 2.3), (10.795, 4.6412),
                                               (10.795, 5.6), (9.919, 5.6)])
        self.assertEqual(head(".400/375 Belted Nitro Express", 7),
                         [(5.92, 0), (5.92, 1.57), (5.121, 1.57), (5.121, 2.57), (5.92, 3.5222), (5.92, 5.87), (5.6047, 5.87)])
        for name in self.HEAD_UNSOURCED:
            with self.subTest(name):
                s, prof = specs[name], outline.case_profile(specs[name])
                self.assertLess(prof[2][0], min(s["rim"], s["base"]) / 2)  # a groove, below the rim and the body
                heights = [h for _, h in prof]
                self.assertEqual(heights, sorted(heights))

if __name__ == "__main__":
    unittest.main()
