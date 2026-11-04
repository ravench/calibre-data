"""python3 -m unittest discover -s tests"""
import os, re, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import outline  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
